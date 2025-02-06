from flask import Blueprint, jsonify, request, send_file
from models import db, Documento, Trabajador, Empresa
from flask_jwt_extended import jwt_required
import os
import shutil
import rarfile

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


@documento_bp.route('/generar-rar/<int:trabajador_id>/<int:empresa_id>', methods=['GET'])
@jwt_required()
def generar_rar(trabajador_id, empresa_id):
    # Obtener datos del trabajador y empresa
    trabajador = Trabajador.query.get_or_404(trabajador_id)
    empresa = Empresa.query.get_or_404(empresa_id)

    # Obtener los requisitos de la empresa
    requisitos_empresa = {req.nombre_requisito for req in empresa.requisitos}

    # Obtener los documentos del trabajador
    documentos_trabajador = {doc.tipo: doc for doc in trabajador.documentos}

    # Verificar si el trabajador tiene todos los documentos requeridos
    documentos_faltantes = requisitos_empresa - documentos_trabajador.keys()

    if documentos_faltantes:
        return jsonify({"error": "Faltan documentos", "documentos_faltantes": list(documentos_faltantes)}), 400

    # Crear carpeta temporal para el .rar
    temp_folder = f"temp_rar_{trabajador.id}"
    os.makedirs(temp_folder, exist_ok=True)

    # Copiar y renombrar archivos
    for tipo_doc, documento in documentos_trabajador.items():
        origen = os.path.join("uploads", documento.ruta_archivo)  # Ruta de subida
        destino = os.path.join(temp_folder, f"{documento.nombre_archivo}-{tipo_doc}{os.path.splitext(documento.ruta_archivo)[1]}")
        shutil.copy(origen, destino)

    # Nombre del archivo .rar
    rar_filename = f"{trabajador.nombre}.rar"
    rar_path = os.path.join("uploads", rar_filename)

    # Crear el .rar
    with rarfile.RarFile(rar_path, "w") as rar:
        rar.add(temp_folder, arcname=os.path.basename(temp_folder))

    # Limpiar archivos temporales
    shutil.rmtree(temp_folder)

    return send_file(rar_path, as_attachment=True)