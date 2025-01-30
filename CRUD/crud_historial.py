from flask import Blueprint, jsonify, request
from models import db, HistorialAsignacion, Trabajador, Empresa
from flask_jwt_extended import jwt_required

# Crear un Blueprint para HistorialAsignacion
historial_bp = Blueprint('historial_bp', __name__)

# Obtener todas las asignaciones
@historial_bp.route('/asignaciones', methods=['GET'])
@jwt_required()
def get_asignaciones():
    asignaciones = HistorialAsignacion.query.all()
    return jsonify([{
        'id': a.id,
        'trabajador_id': a.trabajador_id,
        'empresa_id': a.empresa_id,
        'fecha_asignacion': a.fecha_asignacion
    } for a in asignaciones])

# Crear una nueva asignación
@historial_bp.route('/asignaciones', methods=['POST'])
@jwt_required()
def create_asignacion():
    data = request.json
    nueva_asignacion = HistorialAsignacion(
        trabajador_id=data['trabajador_id'],
        empresa_id=data['empresa_id']
    )
    db.session.add(nueva_asignacion)
    db.session.commit()
    return jsonify({'message': 'Asignación creada correctamente', 'id': nueva_asignacion.id})

# Actualizar una asignación
@historial_bp.route('/asignaciones/<int:id>', methods=['PUT'])
@jwt_required()
def update_asignacion(id):
    data = request.json
    asignacion = HistorialAsignacion.query.get(id)
    if not asignacion:
        return jsonify({'message': 'Asignación no encontrada'}), 404
    
    asignacion.trabajador_id = data.get('trabajador_id', asignacion.trabajador_id)
    asignacion.empresa_id = data.get('empresa_id', asignacion.empresa_id)
    db.session.commit()
    return jsonify({'message': 'Asignación actualizada correctamente'})

# Eliminar una asignación
@historial_bp.route('/asignaciones/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asignacion(id):
    asignacion = HistorialAsignacion.query.get(id)
    if not asignacion:
        return jsonify({'message': 'Asignación no encontrada'}), 404
    
    db.session.delete(asignacion)
    db.session.commit()
    return jsonify({'message': 'Asignación eliminada correctamente'})

# Asignar un trabajador a una empresa
@historial_bp.route('/asignaciones', methods=['POST'])
@jwt_required()
def asignar_trabajador_a_empresa():
    data = request.json
    trabajador_id = data.get('trabajador_id')
    empresa_id = data.get('empresa_id')

    # Verificar que el trabajador y la empresa existan
    trabajador = db.session.query(Trabajador).get(trabajador_id)
    empresa = db.session.query(Empresa).get(empresa_id)

    if not trabajador or not empresa:
        return jsonify({'message': 'Trabajador o empresa no encontrados'}), 404

    # Registrar la asignación
    nueva_asignacion = HistorialAsignacion(trabajador_id=trabajador_id, empresa_id=empresa_id)
    db.session.add(nueva_asignacion)
    db.session.commit()

    return jsonify({'message': 'Asignación registrada correctamente', 'id': nueva_asignacion.id})
