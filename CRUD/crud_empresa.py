from flask import Blueprint, jsonify, request
from models import db, Empresa, HistorialAsignacion
from flask_jwt_extended import jwt_required

# Crear un Blueprint para Empresa
empresa_bp = Blueprint('empresa_bp', __name__)


@empresa_bp.route('/empresas/count', methods=['GET'])
@jwt_required()
def count_empresas():
    try:
        count = Empresa.query.count()
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@empresa_bp.route('/empresas', methods=['GET'])
@jwt_required()
def obtener_empresas():
    empresas = Empresa.query.all()

    resultado = []
    for empresa in empresas:
        trabajadores_activos = HistorialAsignacion.query.filter_by(empresa_id=empresa.id).count()

        resultado.append({
            "id": empresa.id,
            "nombre": empresa.nombre,
            "trabajadores_activos": trabajadores_activos
        })

    return jsonify(resultado), 200

# Crear una nueva empresa
@empresa_bp.route('/empresas', methods=['POST'])
@jwt_required()
def create_empresa():
    data = request.json
    nueva_empresa = Empresa(
        nombre=data['nombre'],
        localidad=data['localidad']
    )
    db.session.add(nueva_empresa)
    db.session.commit()
    return jsonify({'message': 'Empresa creada correctamente', 'id': nueva_empresa.id})

# Actualizar una empresa
@empresa_bp.route('/empresas/<int:id>', methods=['PUT'])
@jwt_required()
def update_empresa(id):
    data = request.json
    empresa = Empresa.query.get(id)
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404
    
    empresa.nombre = data.get('nombre', empresa.nombre)
    empresa.localidad = data.get('localidad', empresa.localidad)
    db.session.commit()
    return jsonify({'message': 'Empresa actualizada correctamente'})

# Eliminar una empresa
@empresa_bp.route('/empresas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_empresa(id):
    empresa = Empresa.query.get(id)
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404
    
    db.session.delete(empresa)
    db.session.commit()
    return jsonify({'message': 'Empresa eliminada correctamente'})


# Obtener trabajadores asignados a una empresa
@empresa_bp.route('/empresas/<int:empresa_id>/trabajadores', methods=['GET'])
@jwt_required()
def get_trabajadores_de_empresa(empresa_id):
    # Verificar si la empresa existe
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404

    # Obtener asignaciones de trabajadores a esta empresa
    asignaciones = HistorialAsignacion.query.filter_by(empresa_id=empresa_id).all()
    trabajadores = [
        {
            'id': a.trabajador.id,
            'nombre': a.trabajador.nombre,
            'rut': a.trabajador.rut,
            'cargo': a.trabajador.cargo,
            'localidad': a.trabajador.localidad
        }
        for a in asignaciones
    ]

    return jsonify(trabajadores)

@empresa_bp.route('/empresas/busqueda', methods=['GET'])
@jwt_required()
def buscar_empresas():
    nombre = request.args.get('nombre')
    localidad = request.args.get('localidad')

    # Construir la consulta dinámica
    query = Empresa.query
    if nombre:
        query = query.filter(Empresa.nombre.like(f"%{nombre}%"))
    if localidad:
        query = query.filter(Empresa.localidad.like(f"%{localidad}%"))

    # Ejecutar la consulta
    empresas = query.all()
    return jsonify([{
        'id': e.id,
        'nombre': e.nombre,
        'localidad': e.localidad
    } for e in empresas])

@empresa_bp.route('/empresas/<int:empresa_id>/trabajadores_asignados', methods=['GET'])
@jwt_required()
def trabajadores_asignados_a_empresa(empresa_id):
    # Verificar si la empresa existe
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        return jsonify({'message': f'Empresa con ID {empresa_id} no encontrada'}), 404

    # Obtener las asignaciones activas de esta empresa
    asignaciones = HistorialAsignacion.query.filter_by(empresa_id=empresa_id).all()

    # Extraer los trabajadores asociados
    trabajadores = [
        {
            'id': a.trabajador.id,
            'nombre': a.trabajador.nombre,
            'rut': a.trabajador.rut,
            'cargo': a.trabajador.cargo,
            'localidad': a.trabajador.localidad
        }
        for a in asignaciones
    ]

    return jsonify(trabajadores)
