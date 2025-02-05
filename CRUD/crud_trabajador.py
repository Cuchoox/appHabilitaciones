from flask import Blueprint, jsonify, request, make_response, send_file
from models import db, Trabajador, HistorialAsignacion, Documento
import logging
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
import os

# 📂 Configuración de almacenamiento de archivos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear carpeta si no existe

# 🔹 Crear un Blueprint para las rutas de Trabajador
trabajador_bp = Blueprint('trabajador_bp', __name__)

# 📌 CONTAR TRABAJADORES
@trabajador_bp.route('/trabajadores/count', methods=['GET'])
@jwt_required()
def count_trabajadores():
    try:
        count = Trabajador.query.count()
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📌 OBTENER TODOS LOS TRABAJADORES
@trabajador_bp.route('/trabajadores', methods=['GET'])
@jwt_required()
def obtener_trabajadores():
    try:
        trabajadores = Trabajador.query.all()
        return jsonify([{
            "id": t.id,
            "nombre": t.nombre,
            "apellido": t.apellido,
            "rut": t.rut,
            "cargo": t.cargo,
            "localidad": t.localidad,
            "tipo": t.tipo if t.tipo else "N/A"
        } for t in trabajadores]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # 📌 OBTENER UN TRABAJADOR ESPECÍFICO
@trabajador_bp.route('/trabajadores/<int:id>', methods=['GET'])
@jwt_required()
def obtener_trabajador(id):
        try:
            trabajador = Trabajador.query.get(id)
            if not trabajador:
                return jsonify({'error': 'Trabajador no encontrado'}), 404

            return jsonify({
                "id": trabajador.id,
                "nombre": trabajador.nombre,
                "apellido": trabajador.apellido,
                "rut": trabajador.rut,
                "cargo": trabajador.cargo,
                "localidad": trabajador.localidad,
                "tipo": trabajador.tipo if trabajador.tipo else "N/A"
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# 📌 CREAR UN NUEVO TRABAJADOR
@trabajador_bp.route('/trabajadores', methods=['POST'])
@jwt_required()
def create_trabajador():
    data = request.get_json()
    required_fields = ["nombre", "apellido", "rut", "cargo", "localidad"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo '{field}'"}), 400

    nuevo_trabajador = Trabajador(
        nombre=data['nombre'],
        apellido=data['apellido'],
        rut=data['rut'],
        cargo=data['cargo'],
        localidad=data['localidad'],
        tipo=data.get('tipo', "Desconocido")
    )

    db.session.add(nuevo_trabajador)
    db.session.commit()
    return jsonify({'message': 'Trabajador creado correctamente', 'id': nuevo_trabajador.id}), 201

# 📌 ACTUALIZAR UN TRABAJADOR
@trabajador_bp.route('/trabajadores/<int:id>', methods=['PUT'])
@jwt_required()
def update_trabajador(id):
    data = request.json
    trabajador = Trabajador.query.get(id)
    if not trabajador:
        return jsonify({'message': 'Trabajador no encontrado'}), 404

    trabajador.nombre = data.get('nombre', trabajador.nombre)
    trabajador.apellido = data.get('apellido', trabajador.apellido)
    trabajador.rut = data.get('rut', trabajador.rut)
    trabajador.cargo = data.get('cargo', trabajador.cargo)
    trabajador.localidad = data.get('localidad', trabajador.localidad)
    db.session.commit()
    return jsonify({'message': 'Trabajador actualizado correctamente'}), 200

# 📌 ELIMINAR UN TRABAJADOR
@trabajador_bp.route('/trabajadores/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_trabajador(id):
    trabajador = Trabajador.query.get(id)
    if not trabajador:
        return jsonify({'message': 'Trabajador no encontrado'}), 404

    db.session.delete(trabajador)
    db.session.commit()
    return jsonify({'message': 'Trabajador eliminado correctamente'}), 200

# 📌 OBTENER DOCUMENTOS DE UN TRABAJADOR
@trabajador_bp.route('/documentos', methods=['GET'])
@jwt_required()
def obtener_documentos_trabajador():
    trabajador_id = request.args.get("trabajador_id")  # 🔹 Obtener desde la URL
    
    if not trabajador_id:
        return jsonify({"error": "Falta el trabajador_id"}), 400  # ✅ Mensaje de error claro

    trabajador = Trabajador.query.get(trabajador_id)
    if not trabajador:
        return jsonify({"error": "Trabajador no encontrado"}), 404

    documentos = Documento.query.filter_by(trabajador_id=trabajador_id).all()
    
    return jsonify([
        {
            "id": doc.id,
            "nombre_archivo": doc.nombre_archivo,
            "categoria": doc.categoria,
            "fecha_vencimiento": doc.fecha_vencimiento,
            "ruta_archivo": doc.ruta_archivo
        }
        for doc in documentos
    ]), 200


# 📌 SUBIR DOCUMENTO
@trabajador_bp.route('/trabajadores/<int:trabajador_id>/documentos', methods=['POST'])
@jwt_required()
def subir_documento(trabajador_id):
    if 'archivo' not in request.files:
        return jsonify({"error": "No se proporcionó ningún archivo"}), 400

    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return jsonify({"error": "El archivo no tiene nombre válido"}), 400

    # 🔹 Obtener nombre del archivo de forma segura
    nombre_archivo = secure_filename(archivo.filename)

    # 🔹 Verificar si ya existe un documento con el mismo nombre
    documento_existente = Documento.query.filter_by(
        trabajador_id=trabajador_id, 
        nombre_archivo=nombre_archivo
    ).first()

    if documento_existente:
        return jsonify({"error": "Ya existe un documento con este nombre"}), 400

    # 🔹 Guardar el archivo en la carpeta local
    ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_archivo).replace("\\", "/")
    archivo.save(ruta_archivo)

    # 🔹 Guardar el documento en la base de datos
    nuevo_documento = Documento(
        trabajador_id=trabajador_id,
        nombre_archivo=nombre_archivo,
        categoria=request.form.get("categoria"),
        ruta_archivo=ruta_archivo,
        fecha_vencimiento=request.form.get("fecha_vencimiento")
    )

    db.session.add(nuevo_documento)
    db.session.commit()

    return jsonify({
        "message": "✅ Documento subido exitosamente",
        "nombre_archivo": nuevo_documento.nombre_archivo
    }), 201

# 📌 ELIMINAR DOCUMENTO
@trabajador_bp.route('/documentos/<int:documento_id>', methods=['DELETE'])
@jwt_required()
def eliminar_documento(documento_id):
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"error": "Documento no encontrado"}), 404

    # 🔹 Eliminar archivo del servidor si existe
    if documento.ruta_archivo and os.path.exists(documento.ruta_archivo):
        os.remove(documento.ruta_archivo)

    db.session.delete(documento)
    db.session.commit()

    return jsonify({"message": "✅ Documento eliminado correctamente"}), 200

# 📌 DESCARGAR DOCUMENTO
@trabajador_bp.route('/documentos/<int:documento_id>/descargar', methods=['GET'])
@jwt_required()
def descargar_documento(documento_id):
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"error": "Documento no encontrado"}), 404

    if not documento.ruta_archivo or not os.path.exists(documento.ruta_archivo):
        return jsonify({"error": "Archivo no encontrado en el servidor"}), 404

    return send_file(documento.ruta_archivo, as_attachment=True)

