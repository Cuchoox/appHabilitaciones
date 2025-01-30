from flask import Blueprint, jsonify, request
from models import db, Documento
from flask_jwt_extended import jwt_required

# Crear un Blueprint para Documento
documento_bp = Blueprint('documento_bp', __name__)

# Obtener todos los documentos
@documento_bp.route('/documentos', methods=['GET'])
@jwt_required()
def get_documentos():
    documentos = Documento.query.all()
    return jsonify([{
        'id': d.id,
        'trabajador_id': d.trabajador_id,
        'nombre_archivo': d.nombre_archivo,
        'tipo': d.tipo,
        'ruta_archivo': d.ruta_archivo
    } for d in documentos])

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
