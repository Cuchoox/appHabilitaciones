from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Trabajador(db.Model):
    __tablename__ = 'trabajadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(50))
    localidad = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    creado_en = db.Column(db.DateTime, default=db.func.now())
    asignaciones = db.relationship('HistorialAsignacion', backref='trabajador', lazy=True)

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    localidad = db.Column(db.String(50))
    creado_en = db.Column(db.DateTime, default=db.func.now())
    asignaciones = db.relationship('HistorialAsignacion', backref='empresa', lazy=True)

class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(10))
    ruta_archivo = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime, default=db.func.now())

class HistorialAsignacion(db.Model):
    __tablename__ = 'historial_asignaciones'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=db.func.now())

from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # Ejemplo: 'admin', 'colaborador'

    # Método para establecer contraseña encriptada
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
