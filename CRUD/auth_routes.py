from flask import Blueprint, request, jsonify
from flask_mail import Message
from models import db, Usuario
from werkzeug.security import generate_password_hash
import random, string

auth_bp = Blueprint('auth_bp', __name__)

# 📧 Configuración de Flask-Mail (Asegúrate de configurarlo en tu app)
from flask_mail import Mail

def configure_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'auth.mci@gmail.com'
    app.config['MAIL_PASSWORD'] = 'authMCI20062025'
    mail.init_app(app)

mail = Mail()

def generar_contraseña_segura(longitud=8):
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()?"
    return ''.join(random.choices(caracteres, k=longitud))

@auth_bp.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "El correo es obligatorio"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "No se encontró un usuario con este correo"}), 404

    # Generar una nueva contraseña segura
    nueva_contraseña = generar_contraseña_segura()
    usuario.password_hash = generate_password_hash(nueva_contraseña)
    db.session.commit()

    # Enviar el correo con la nueva contraseña
    msg = Message("Recuperación de contraseña", sender="rbeltran1107@gmail.com", recipients=[email])
    msg.body = f"Tu nueva contraseña es: {nueva_contraseña}\n\nPor seguridad, te recomendamos anotarla en un lugar solo donde tú tengas acceso."

    try:
        mail.send(msg)
        return jsonify({"message": "Correo de recuperación enviado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
