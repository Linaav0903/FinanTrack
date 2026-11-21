import pytest
from services import auth_service as au


def test_registro_guarda_hash_y_autentica(app):
    u = au.register_user("Ana López", "Ana@Correo.com", "clave1234", "clave1234")
    assert u.id and u.email == "ana@correo.com"
    assert u.password_hash != "clave1234"
    assert au.authenticate("ANA@correo.com", "clave1234").id == u.id


def test_login_con_clave_incorrecta(app):
    au.register_user("Ana López", "ana@correo.com", "clave1234")
    assert au.authenticate("ana@correo.com", "otra-clave") is None
    assert au.authenticate("nadie@correo.com", "clave1234") is None


@pytest.mark.parametrize("nombre,correo,clave,conf,mensaje", [
    ("", "a@b.com", "clave1234", None, "nombre"),
    ("Ana 123", "a@b.com", "clave1234", None, "letras"),
    ("Ana", "correo-malo", "clave1234", None, "correo"),
    ("Ana", "a@b.com", "corta", None, "8 caracteres"),
    ("Ana", "a@b.com", "clave1234", "distinta", "no coinciden"),
])
def test_registro_rechaza_datos_invalidos(app, nombre, correo, clave, conf, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        au.register_user(nombre, correo, clave, conf)


def test_correo_duplicado(app):
    au.register_user("Ana", "ana@correo.com", "clave1234")
    with pytest.raises(ValueError, match="Ya existe"):
        au.register_user("Otra Ana", "ANA@correo.com", "clave5678")
