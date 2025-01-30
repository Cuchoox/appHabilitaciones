from flask import Blueprint, jsonify, request
from models import db, Trabajador, HistorialAsignacion
import logging
from flask_jwt_extended import get_jwt_identity, jwt_required

# Crear un Blueprint para las rutas de Trabajador
trabajador_bp = Blueprint('trabajador_bp', __name__)

@trabajador_bp.route('/trabajadores', methods=['GET'])
@jwt_required()
def obtener_trabajadores():
    current_user = get_jwt_identity()  # Aquí extrae el usuario del token
    print(f"Usuario autenticado: {current_user}")  # Para depuración
    trabajadores = Trabajador.query.all()
    return jsonify([{
        "id": t.id,
        "nombre": t.nombre,
        "rut": t.rut,
        "cargo": t.cargo,
        "localidad": t.localidad,
        "tipo": t.tipo
    } for t in trabajadores])
    
@trabajador_bp.route('/trabajadores', methods=['POST'])
@jwt_required()
def create_trabajador():
    data = request.json
    nuevo_trabajador = Trabajador(
        nombre=data['nombre'],
        rut=data['rut'],
        cargo=data['cargo'],
        localidad=data['localidad']
    )
    db.session.add(nuevo_trabajador)
    db.session.commit()
    return jsonify({'message': 'Trabajador creado correctamente', 'id': nuevo_trabajador.id})

@trabajador_bp.route('/trabajadores/<int:id>', methods=['PUT'])
@jwt_required()
def update_trabajador(id):
    data = request.json
    trabajador = Trabajador.query.get(id)
    if not trabajador:
        return jsonify({'message': 'Trabajador no encontrado'}), 404
    
    trabajador.nombre = data.get('nombre', trabajador.nombre)
    trabajador.rut = data.get('rut', trabajador.rut)
    trabajador.cargo = data.get('cargo', trabajador.cargo)
    trabajador.localidad = data.get('localidad', trabajador.localidad)
    db.session.commit()
    return jsonify({'message': 'Trabajador actualizado correctamente'})

@trabajador_bp.route('/trabajadores/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_trabajador(id):
    trabajador = Trabajador.query.get(id)
    if not trabajador:
        return jsonify({'message': 'Trabajador no encontrado'}), 404
    
    db.session.delete(trabajador)
    db.session.commit()
    return jsonify({'message': 'Trabajador eliminado correctamente'})

# Obtener empresas a las que un trabajador ha sido asignado
@trabajador_bp.route('/trabajadores/<int:trabajador_id>/empresas', methods=['GET'])
@jwt_required()
def get_empresas_de_trabajador(trabajador_id):
    # Verificar si el trabajador existe
    trabajador = Trabajador.query.get(trabajador_id)
    if not trabajador:
        return jsonify({'message': 'Trabajador no encontrado'}), 404

    # Obtener asignaciones de este trabajador
    asignaciones = HistorialAsignacion.query.filter_by(trabajador_id=trabajador_id).all()
    empresas = [
        {
            'id': a.empresa.id,
            'nombre': a.empresa.nombre,
            'localidad': a.empresa.localidad
        }
        for a in asignaciones
    ]

    return jsonify(empresas)


@trabajador_bp.route('/trabajadores/busqueda', methods=['GET'])
@jwt_required()
def buscar_trabajadores():
    try:
        nombre = request.args.get('nombre')
        rut = request.args.get('rut')
        cargo = request.args.get('cargo')
        localidad = request.args.get('localidad')
        
        logging.info(f" Búsqueda realizada con filtros: nombre={nombre}, rut={rut}, cargo={cargo}, localidad={localidad}")

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if per_page > 100:
            return jsonify({'error': 'El número máximo de resultados por página es 100'}), 400

        query = Trabajador.query
        if nombre:
            query = query.filter(Trabajador.nombre.like(f"%{nombre}%"))
        if rut:
            query = query.filter(Trabajador.rut == rut)
        if cargo:
            query = query.filter(Trabajador.cargo.like(f"%{cargo}%"))
        if localidad:
            query = query.filter(Trabajador.localidad.like(f"%{localidad}%"))

        paginacion = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'total': paginacion.total,
            'pages': paginacion.pages,
            'page': paginacion.page,
            'per_page': paginacion.per_page,
            'results': [{
                'id': t.id,
                'nombre': t.nombre,
                'rut': t.rut,
                'cargo': t.cargo,
                'localidad': t.localidad
            } for t in paginacion.items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
