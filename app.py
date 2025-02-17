from flask import Flask, jsonify, request
from flask_migrate import Migrate  # Importar Flask-Migrate
from models import db, Trabajador, Empresa, Documento, HistorialAsignacion, Usuario  # Importar modelos necesarios
from config import Config
from CRUD.crud_trabajador import trabajador_bp
from CRUD.crud_empresa import empresa_bp
from CRUD.crud_documento import documento_bp
from CRUD.crud_historial import historial_bp
from CRUD.crud_usuario import usuario_bp
from CRUD.auth_routes import auth_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from flask_mail import Mail




app = Flask(__name__)
app.config.from_object(Config)  # Configuración desde config.py
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

db.init_app(app)  # Inicializar SQLAlchemy con la app
migrate = Migrate(app, db)  # Inicializar Flask-Migrate

app.register_blueprint(trabajador_bp)  # Registrar Blueprint de Trabajador
app.register_blueprint(empresa_bp)  # Registrar Blueprint de Empresa
app.register_blueprint(documento_bp)  # Registrar Blueprint de Documento    
app.register_blueprint(historial_bp)  # Registrar Blueprint de HistorialAsignacion  
app.register_blueprint(usuario_bp)
app.register_blueprint(auth_bp)  # Registrar Blueprint de Usuario


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Error interno del servidor'}), 500

# Configurar Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP (Usar el de tu proveedor)
app.config['MAIL_PORT'] = 587  # Puerto SMTP (587 para TLS, 465 para SSL)
app.config['MAIL_USE_TLS'] = True  # Habilitar TLS
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'auth.mci@gmail.com'  # Tu dirección de correo
app.config['MAIL_PASSWORD'] = 'dmfhxkhfkdqgaqeg'
app.config['MAIL_DEFAULT_SENDER'] = 'tuemail@gmail.com'  # Email desde donde se enviarán los correos
app.config['MAIL_MAX_EMAILS'] = 10

mail = Mail(app)  # Inicializar Flask-Mail


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

