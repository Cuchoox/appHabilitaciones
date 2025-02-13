from flask import Blueprint, request, jsonify
from models import RequisitoEmpresa, db, Empresa  # ✅ Importar modelo de base de datos
from flask_jwt_extended import jwt_required

# Crear Blueprint para requisitos
requisitos_bp = Blueprint('requisitos_bp', __name__)

### 📌 Obtener todos los requisitos
@requisitos_bp.route('/requisitos', methods=['GET'])
@jwt_required()
def get_requisitos():
    requisitos = RequisitoEmpresa.query.all()
    return jsonify([{
        "id": req.id,
        "empresa_id": req.empresa_id,
        "tipo": req.tipo
    } for req in requisitos])

### 📌 Agregar un nuevo requisito


### 📌 Actualizar un requisito existente
@requisitos_bp.route('/requisitos/<int:id>', methods=['PUT'])
@jwt_required()
def update_requisito(id):
    requisito = RequisitoEmpresa.query.get(id)
    if not requisito:
        return jsonify({"error": "Requisito no encontrado"}), 404

    data = request.json
    requisito.empresa_id = data.get("empresa_id", requisito.empresa_id)
    requisito.tipo = data.get("tipo", requisito.tipo)

    db.session.commit()  # ✅ Guardar cambios en la BD

    return jsonify({
        "id": requisito.id,
        "empresa_id": requisito.empresa_id,
        "tipo": requisito.tipo
    })

### 📌 Eliminar un requisito
@requisitos_bp.route('/requisitos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_requisito(id):
    requisito = RequisitoEmpresa.query.get(id)
    if not requisito:
        return jsonify({"error": "Requisito no encontrado"}), 404

    db.session.delete(requisito)
    db.session.commit()  # ✅ Confirmar eliminación

    return jsonify({"message": "Requisito eliminado correctamente"}), 200


@requisitos_bp.route('/empresas/<int:empresa_id>/requisitos', methods=['GET'])
@jwt_required()
def obtener_requisitos_empresa(empresa_id):
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        return jsonify({"error": "Empresa no encontrada"}), 404

    requisitos = RequisitoEmpresa.query.filter_by(empresa_id=empresa_id).all()
    return jsonify([{
        "id": req.id,  # ✅ Asegurar que se devuelve el ID
        "nombre_requisito": req.nombre_requisito,
        "categoria": req.categoria
    } for req in requisitos])
