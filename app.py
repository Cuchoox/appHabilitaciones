from flask import Flask, jsonify, request
from flask_migrate import Migrate  # Importar Flask-Migrate
from models import db, Trabajador, Empresa, Documento, HistorialAsignacion, Usuario  # Importar modelos necesarios
from config import Config
from CRUD.crud_trabajador import trabajador_bp
from CRUD.crud_empresa import empresa_bp
from CRUD.crud_documento import documento_bp
from CRUD.crud_historial import historial_bp
from CRUD.crud_usuario import usuario_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS


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


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    app.run(debug=True)
