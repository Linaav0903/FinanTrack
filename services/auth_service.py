import re
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]+$")


def register_user(name, email, password, confirm=None):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    if not name:
        raise ValueError("El nombre es obligatorio.")
    if not _NOMBRE.match(name):
        raise ValueError("El nombre solo puede contener letras y espacios.")
    if not _EMAIL.match(email):
        raise ValueError("El correo no es válido.")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if confirm is not None and password != confirm:
        raise ValueError("Las contraseñas no coinciden.")
    if User.query.filter_by(email=email).first():
        raise ValueError("Ya existe una cuenta con ese correo.")
    user = User(name=name, email=email,
                password_hash=generate_password_hash(password, method="pbkdf2:sha256"))
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email, password):
    user = User.query.filter_by(email=(email or "").strip().lower()).first()
    if user and check_password_hash(user.password_hash, password or ""):
        return user
    return None
