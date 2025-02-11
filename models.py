from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Trabajador(db.Model):
    __tablename__ = 'trabajadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(50))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)  # ✅ Relación directa
    localidad = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    creado_en = db.Column(db.DateTime, default=db.func.now())

    # ✅ Relación directa con Empresa (un trabajador puede estar en una empresa principal)
    empresa = db.relationship("Empresa", back_populates="trabajadores")

    # ✅ Relación de historial de asignaciones
    historial_asignaciones = db.relationship('HistorialAsignacion', back_populates='trabajador', lazy=True, cascade="all, delete-orphan")

    # ✅ Relación con Documentos
    documentos = db.relationship('Documento', back_populates='trabajador', lazy=True, cascade="all, delete-orphan")

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    localidad = db.Column(db.String(50))
    creado_en = db.Column(db.DateTime, default=db.func.now())

    # ✅ Relación con Trabajadores (sin usar `secondary`, porque `HistorialAsignacion` ya maneja la relación Many-to-Many)
    trabajadores = db.relationship("Trabajador", back_populates="empresa", lazy=True)

    # ✅ Relación con Historial de asignaciones
    historial_asignaciones = db.relationship("HistorialAsignacion", back_populates="empresa", lazy=True, cascade="all, delete-orphan")

    # ✅ Relación con Requisitos
    requisitos = db.relationship("RequisitoEmpresa", back_populates="empresa", lazy=True, cascade="all, delete-orphan")

class HistorialAsignacion(db.Model):
    __tablename__ = 'historial_asignaciones'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=db.func.now())

    # ✅ Referencias correctas para evitar loops
    trabajador = db.relationship("Trabajador", back_populates="historial_asignaciones")
    empresa = db.relationship("Empresa", back_populates="historial_asignaciones")

class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(10))
    ruta_archivo = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime, default=db.func.now())
    fecha_vencimiento = db.Column(db.Date)
    tipo = db.Column(db.String(100), nullable=False)  # ✅ Manteniendo el tipo

    trabajador = db.relationship("Trabajador", back_populates="documentos")

    def __repr__(self):
        return f"<Documento {self.nombre_archivo} ({self.tipo})>"

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # Ejemplo: 'admin', 'colaborador'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RequisitoEmpresa(db.Model):
    __tablename__ = 'requisitos_empresa'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    nombre_requisito = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

    empresa = db.relationship("Empresa", back_populates="requisitos")
