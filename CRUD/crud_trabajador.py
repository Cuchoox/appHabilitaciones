import zipfile
from flask import Blueprint, jsonify, request, make_response, send_file
from models import Empresa, RequisitoEmpresa, db, Trabajador, HistorialAsignacion, Documento
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
        return jsonify({"error": "No se ha enviado un archivo"}), 422

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return jsonify({"error": "No se ha seleccionado ningún archivo"}), 422

    data = request.form
    print("📥 Datos recibidos en el backend:", data)  # 🔹 Ver qué llega desde el frontend

    categoria = data.get("categoria")
    fecha_vencimiento = data.get("fecha_vencimiento")
    tipo_documento = data.get("tipo")

    print(f"📂 Archivo recibido: {archivo.filename}")  # Debugging
    print(f"📅 Fecha de vencimiento recibida: {fecha_vencimiento}")  # Debugging
    print(f"📄 Tipo de documento recibido: {tipo_documento}")  # Debugging

    if not fecha_vencimiento or not tipo_documento:
        return jsonify({"error": "Todos los campos son obligatorios (fecha de vencimiento, tipo)."}), 422

    # 🔹 Buscar el trabajador
    trabajador = Trabajador.query.get(trabajador_id)
    if not trabajador:
        return jsonify({"error": "El trabajador no existe"}), 404

    # 🔹 Renombrar archivo correctamente
    extension = archivo.filename.split('.')[-1]
    nuevo_nombre_archivo = f"{tipo_documento} - {trabajador.nombre} {trabajador.apellido}.{extension}"

    # 🔹 Guardar el archivo
    ruta_archivo = os.path.join(UPLOAD_FOLDER, nuevo_nombre_archivo)
    archivo.save(ruta_archivo)

    # 🔹 Guardar en la base de datos
    nuevo_documento = Documento(
        trabajador_id=trabajador_id,
        nombre_archivo=nuevo_nombre_archivo,
        categoria=categoria,
        ruta_archivo=ruta_archivo,
        fecha_vencimiento=fecha_vencimiento,
        tipo=tipo_documento
    )

    db.session.add(nuevo_documento)
    db.session.commit()

    return jsonify({"mensaje": "Documento subido correctamente"}), 201



# 🔹 Función para obtener la categoría automáticamente
def obtener_categoria_por_tipo(tipo_documento):
    categorias_por_tipo = {
        "carnet": "Administrativos",
        "licencia": "Salud y Seguridad",
        "certificado": "Capacitación y Certificaciones",
        "contrato": "Administrativos",
        "seguro": "Salud y Seguridad"
    }
    return categorias_por_tipo.get(tipo_documento)



@trabajador_bp.route("/trabajadores/<int:trabajador_id>/generar-rar", methods=["POST"])
@jwt_required()
def generar_rar(trabajador_id):
    data = request.get_json()
    empresa_id = data.get("empresa_id")  # 🔹 Cambiar nombre de variable para claridad

    print(f"📥 Empresa ID recibido: {empresa_id}")  # 📌 Depuración

    if not empresa_id:
        return jsonify({"error": "Falta el campo 'empresa_id'"}), 400

    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        print("❌ Empresa no encontrada")
        return jsonify({"error": "Empresa no encontrada"}), 404
    # Obtener los requisitos de la empresa
    documentos_requeridos = [req.nombre_requisito for req in empresa.requisitos] if empresa.requisitos else []
    print(f"📋 Documentos requeridos por {empresa.nombre}: {documentos_requeridos}")

    # Obtener los documentos del trabajador
    documentos_trabajador = Documento.query.filter_by(trabajador_id=trabajador_id).all()
    documentos_subidos = {doc.tipo for doc in documentos_trabajador} if documentos_trabajador else set()
    print(f"📂 Documentos subidos por el trabajador: {documentos_subidos}")

    # Verificar si faltan documentos
    documentos_faltantes = [doc for doc in documentos_requeridos if doc not in documentos_subidos]
    print(f"⚠️ Documentos faltantes: {documentos_faltantes}")

    if documentos_faltantes:
        return jsonify({
            "error": "No se puede habilitar al trabajador por falta de documentos.",
            "faltantes": documentos_faltantes
        }), 400

    # Verificar que haya documentos antes de continuar
    if not documentos_trabajador:
        print("❌ No hay documentos asociados al trabajador")
        return jsonify({"error": "No hay documentos asociados al trabajador"}), 400

    # Verificar si el trabajador ya está asignado a esta empresa
    asignacion_existente = HistorialAsignacion.query.filter_by(trabajador_id=trabajador_id, empresa_id=empresa.id).first()
    
    if asignacion_existente:
        print("ℹ️ El trabajador ya está asignado a esta empresa. Solo se generará el archivo ZIP sin modificar la base de datos.")
        trabajador = Trabajador.query.get(trabajador_id)
        ruta_zip = f"temp/Documentos_{trabajador.nombre}_{trabajador.apellido}.zip"
        
        if os.path.exists(ruta_zip):
            return send_file(ruta_zip, as_attachment=True, download_name=f"Documentos_{trabajador.nombre}_{trabajador.apellido}.zip")
        else:
            print("❌ Archivo ZIP no encontrado, se volverá a generar.")

    # Crear una carpeta temporal para los archivos
    ruta_temp = f"temp/habilitacion_trabajador_{trabajador_id}"
    os.makedirs(ruta_temp, exist_ok=True)
    print(f"📁 Carpeta temporal creada: {ruta_temp}")

    archivos_a_comprimir = []
    trabajador = Trabajador.query.get(trabajador_id)
    if not trabajador:
        return jsonify({"error": "Trabajador no encontrado"}), 404

    for documento in documentos_trabajador:
        ruta_archivo = os.path.join(UPLOAD_FOLDER, documento.nombre_archivo).replace("\\", "/")

        if not os.path.exists(ruta_archivo):
            print(f"⚠️ Archivo no encontrado: {ruta_archivo}, se omitirá.")
            continue

        # Obtener la extensión original del archivo
        nombre_original, extension = os.path.splitext(documento.nombre_archivo)

        # Crear el nuevo nombre con la extensión original
        nuevo_nombre = f"{documento.tipo} - {trabajador.nombre} {trabajador.apellido}{extension}"

        # Copiar el archivo con el nuevo nombre, pero manteniendo la extensión
        destino = os.path.join(ruta_temp, nuevo_nombre)
        shutil.copy(ruta_archivo, destino)
        archivos_a_comprimir.append(destino)

        print(f"📄 Archivo copiado: {destino}")

    if not archivos_a_comprimir:
        print("❌ No hay archivos para comprimir.")
        return jsonify({"error": "No hay archivos para comprimir."}), 400

    # Crear el nombre correcto del archivo .zip
    ruta_zip = f"temp/Documentos_{trabajador.nombre}_{trabajador.apellido}.zip"

    # Crear el archivo zip
    with zipfile.ZipFile(ruta_zip, 'w') as zipf:
        for archivo in archivos_a_comprimir:
            zipf.write(archivo, os.path.basename(archivo))

    # Si el trabajador no estaba asignado, se asigna
    if not asignacion_existente:
        nueva_asignacion = HistorialAsignacion(trabajador_id=trabajador_id, empresa_id=empresa.id)
        db.session.add(nueva_asignacion)
        db.session.commit()
        print("✅ Trabajador asignado correctamente a la empresa.")

    trabajador_nombre = f"{trabajador.nombre}_{trabajador.apellido}"
    return send_file(ruta_zip, as_attachment=True, download_name=f"Documentos_{trabajador_nombre}.zip")


@trabajador_bp.route('/trabajadores/<int:trabajador_id>/documentos-faltantes', methods=['GET'])
@jwt_required()
def obtener_documentos_faltantes(trabajador_id):
    empresa_id = request.args.get("empresa_id")
    if not empresa_id:
        return jsonify({"error": "Falta el ID de la empresa"}), 400

    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        return jsonify({"error": "Empresa no encontrada"}), 404

    # Obtener los requisitos de la empresa
    requisitos_empresa = RequisitoEmpresa.query.filter_by(empresa_id=empresa_id).all()
    if not requisitos_empresa:
        return jsonify({"error": "Esta empresa no tiene requisitos configurados"}), 404

    # Obtener los documentos del trabajador
    documentos_trabajador = Documento.query.filter_by(trabajador_id=trabajador_id).all()
    documentos_subidos = {doc.tipo: doc for doc in documentos_trabajador}

    # Verificar qué requisitos faltan
    documentos_faltantes = []
    for requisito in requisitos_empresa:
        if requisito.tipo in documentos_subidos:
            doc = documentos_subidos[requisito.tipo]
            documentos_faltantes.append({
                "nombre_archivo": doc.nombre_archivo,
                "tipo": doc.tipo,
                "fecha_vencimiento": doc.fecha_vencimiento.strftime("%Y-%m-%d") if doc.fecha_vencimiento else None,
                "subido": True  # ✅ Documento subido correctamente
            })
        else:
            documentos_faltantes.append({
                "nombre_archivo": None,
                "tipo": requisito.tipo,  
                "fecha_vencimiento": None,
                "subido": False  # ✅ Documento aún no subido
            })

    return jsonify({"documentos": documentos_faltantes})

