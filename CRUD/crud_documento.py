from flask import Blueprint, jsonify, request, send_file
from models import RequisitoEmpresa, db, Documento, Trabajador, Empresa
from flask_jwt_extended import jwt_required
import os


# Crear un Blueprint para Documento
documento_bp = Blueprint('documento_bp', __name__)


@documento_bp.route('/documentos/count', methods=['GET'])
@jwt_required()
def count_documentos():
    try:
        count = Documento.query.count()
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documento_bp.route('/documentos-general', methods=['GET'])
@jwt_required()
def get_documentos():
    documentos = db.session.query(Documento, Trabajador.nombre).join(
        Trabajador, Documento.trabajador_id == Trabajador.id
    ).all()

    return jsonify([
        {
            'id': d.id,
            'trabajador_id': d.trabajador_id,
            'nombre_trabajador': nombre,  # 🔹 Se obtiene desde el JOIN
            'nombre_archivo': d.nombre_archivo,
            'categoria': d.categoria,
            'fecha_vencimiento': d.fecha_vencimiento,
            'ruta_archivo': d.ruta_archivo
        }
        for d, nombre in documentos
    ])
    

# Crear un nuevo documento
@documento_bp.route('/documentos', methods=['POST'])
@jwt_required()
def create_documento():
    data = request.json
    nuevo_documento = Documento(
        trabajador_id=data['trabajador_id'],
        nombre_archivo=data['nombre_archivo'],
        tipo=data['tipo'],
        ruta_archivo=data['ruta_archivo']
    )
    db.session.add(nuevo_documento)
    db.session.commit()
    return jsonify({'message': 'Documento creado correctamente', 'id': nuevo_documento.id})

# Actualizar un documento
@documento_bp.route('/documentos/<int:id>', methods=['PUT'])
@jwt_required()
def update_documento(id):
    data = request.json
    documento = Documento.query.get(id)
    if not documento:
        return jsonify({'message': 'Documento no encontrado'}), 404
    
    documento.trabajador_id = data.get('trabajador_id', documento.trabajador_id)
    documento.nombre_archivo = data.get('nombre_archivo', documento.nombre_archivo)
    documento.tipo = data.get('tipo', documento.tipo)
    documento.ruta_archivo = data.get('ruta_archivo', documento.ruta_archivo)
    db.session.commit()
    return jsonify({'message': 'Documento actualizado correctamente'})

# Eliminar un documento
@documento_bp.route('/documentos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_documento(id):
    documento = Documento.query.get(id)
    if not documento:
        return jsonify({'message': 'Documento no encontrado'}), 404
    
    db.session.delete(documento)
    db.session.commit()
    return jsonify({'message': 'Documento eliminado correctamente'})


# 📌 ELIMINAR DOCUMENTO
@documento_bp.route('/documentos/<int:documento_id>', methods=['DELETE'])
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
@documento_bp.route('/documentos/<int:documento_id>/descargar', methods=['GET'])
@jwt_required()
def descargar_documento(documento_id):
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"error": "Documento no encontrado"}), 404

    if not documento.ruta_archivo or not os.path.exists(documento.ruta_archivo):
        return jsonify({"error": "Archivo no encontrado en el servidor"}), 404

    return send_file(documento.ruta_archivo, as_attachment=True)


@documento_bp.route("/documentos/tipos", methods=["GET"])
@jwt_required()
def obtener_tipos_documentos():
    # 🔹 Obtener todos los requisitos únicos de todas las empresas
    tipos_documentos = db.session.query(RequisitoEmpresa.nombre_requisito).distinct().all()

    # Convertir a lista simple
    tipos_documentos = [tipo[0] for tipo in tipos_documentos]

    return jsonify(tipos_documentos)
