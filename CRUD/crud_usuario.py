from flask import Blueprint, jsonify, request
from models import db, Usuario

from flask_jwt_extended import create_access_token
usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol', 'colaborador')  # Rol por defecto: colaborador
    email = data.get('email')

    if Usuario.query.filter_by(username=username).first():
        return jsonify({'message': 'El usuario ya existe'}), 400

    nuevo_usuario = Usuario(username=username, rol=rol, email=email)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario registrado correctamente'})



@usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Generar el token JWT
    token = create_access_token(identity=f"{usuario.id}")
    return jsonify({'access_token': token})

@usuario_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
        usuarios = Usuario.query.all()
        usuarios_list = [{'id': usuario.id, 'username': usuario.username, 'rol': usuario.rol} for usuario in usuarios]
        return jsonify(usuarios_list)


@usuario_bp.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
        data = request.json
        usuario = Usuario.query.get_or_404(id)

        username = data.get('username', usuario.username)
        password = data.get('password')
        rol = data.get('rol', usuario.rol)

        usuario.username = username
        if password:
            usuario.set_password(password)
        usuario.rol = rol

        db.session.commit()
        return jsonify({'message': 'Usuario actualizado correctamente'})

@usuario_bp.route('/logout', methods=['POST'])
def logout():
        return jsonify({'message': 'Logout successful'})