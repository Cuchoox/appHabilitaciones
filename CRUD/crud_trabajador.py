import zipfile
from flask import Blueprint, jsonify, request, make_response, send_file
from models import Empresa, db, Trabajador, HistorialAsignacion, Documento
import logging
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
import os
import shutil
import tempfile


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



@trabajador_bp.route("/trabajadores/<int:trabajador_id>/documentos", methods=["POST"])
@jwt_required()
def subir_documento(trabajador_id):
    if "archivo" not in request.files:
        return jsonify({"error": "No se ha enviado un archivo"}), 400

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return jsonify({"error": "No se ha seleccionado ningún archivo"}), 400

    data = request.form
    categoria = data.get("categoria")
    fecha_vencimiento = data.get("fecha_vencimiento")
    tipo_documento = data.get("tipo")

    # Obtener el nombre del trabajador
    trabajador = Trabajador.query.get(trabajador_id)
    if not trabajador:
        return jsonify({"error": "Trabajador no encontrado"}), 404

    # Generar el nombre del archivo: "Tipo - Nombre Apellido.extensión"
    extension = archivo.filename.rsplit(".", 1)[-1]
    nuevo_nombre = f"{tipo_documento} - {trabajador.nombre} {trabajador.apellido}.{extension}"
    
    # Generar ruta del archivo
    ruta_archivo = os.path.join(UPLOAD_FOLDER, secure_filename(nuevo_nombre))
    
    # 🔹 Agregar print para depuración
    print(f"📂 Guardando archivo en: {ruta_archivo}")

    # Guardar el archivo en el servidor
    archivo.save(ruta_archivo)

    # Crear el objeto Documento y asignar ruta_archivo
    nuevo_documento = Documento(
        trabajador_id=trabajador_id,
        nombre_archivo=nuevo_nombre,
        categoria=categoria,
        fecha_vencimiento=fecha_vencimiento,
        tipo=tipo_documento,
        ruta_archivo=ruta_archivo  # ✅ Asegurarse de que no sea None
    )

    # Agregar a la BD y confirmar
    db.session.add(nuevo_documento)
    db.session.commit()

    return jsonify({"mensaje": "Documento subido exitosamente", "documento": nuevo_nombre}), 201

@trabajador_bp.route("/trabajadores/<int:trabajador_id>/generar-rar", methods=["POST"])
@jwt_required()
def generar_rar(trabajador_id):
    data = request.get_json()
    empresa_id = data.get("empresa_id")

    # Validar que la empresa existe
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        return jsonify({"error": "Empresa no encontrada"}), 404

    # Obtener los requisitos de la empresa
    documentos_requeridos = [req.nombre_requisito for req in empresa.requisitos]

    # Obtener los documentos del trabajador
    documentos_trabajador = Documento.query.filter_by(trabajador_id=trabajador_id).all()
    documentos_subidos = {doc.tipo for doc in documentos_trabajador}

    # Verificar si faltan documentos
    documentos_faltantes = [doc for doc in documentos_requeridos if doc not in documentos_subidos]
    if documentos_faltantes:
        return jsonify({
            "error": "No se puede habilitar al trabajador.",
            "faltantes": documentos_faltantes
        }), 400

    # Crear una carpeta temporal para los archivos
    ruta_temp = f"temp/habilitacion_trabajador_{trabajador_id}"
    os.makedirs(ruta_temp, exist_ok=True)

    archivos_a_comprimir = []
    for documento in documentos_trabajador:
        ruta_archivo = os.path.join(UPLOAD_FOLDER, documento.nombre_archivo).replace("\\", "/")

        if not os.path.exists(ruta_archivo):
            print(f"⚠️ Archivo no encontrado: {ruta_archivo}, se omitirá.")
            continue

        destino = os.path.join(ruta_temp, f"{documento.nombre_archivo}-{documento.tipo}")
        shutil.copy(ruta_archivo, destino)
        archivos_a_comprimir.append(destino)

    if not archivos_a_comprimir:
        return jsonify({"error": "No hay archivos para comprimir."}), 400

    # Crear el archivo .rar
    ruta_rar = f"{ruta_temp}.zip"
    with zipfile.ZipFile(ruta_rar, "w", zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos_a_comprimir:
            zipf.write(archivo, os.path.basename(archivo))

    return send_file(ruta_rar, as_attachment=True, download_name=f"trabajador_{trabajador_id}.zip")