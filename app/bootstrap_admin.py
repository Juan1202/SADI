"""
Crea el usuario administrador inicial a partir de ADMIN_USERNAME y ADMIN_PASSWORD.

Cubre el hallazgo S10 de CONTEXTO_SADI.md: ambas variables se declaran en .env y
se inyectan en el contenedor web, pero ningun archivo del codigo las leia, de
modo que 'admin_sadi' habia que crearlo a mano aunque los seeds lo exigen.

Uso:
    docker compose exec web python bootstrap_admin.py

Es idempotente: si el usuario ya existe no lo toca, salvo que se pase
--reset-password, en cuyo caso reestablece la clave desde ADMIN_PASSWORD.
"""
import argparse
import os
import sys

from main import app, db
from models import Usuario
from utils import ROL_ADMINISTRADOR, validar_seguridad_password


def crear_administrador(reset_password=False):
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')

    if not username or not password:
        print("ERROR: faltan ADMIN_USERNAME o ADMIN_PASSWORD en el entorno.")
        return 1

    es_valida, mensaje = validar_seguridad_password(password)
    if not es_valida:
        print(f"ERROR: ADMIN_PASSWORD no es valida. {mensaje}")
        return 1

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario:
        cambios = []
        if usuario.role != ROL_ADMINISTRADOR:
            usuario.role = ROL_ADMINISTRADOR
            cambios.append('rol corregido a administrador')
        if not usuario.activo:
            usuario.activo = True
            cambios.append('cuenta reactivada')
        if reset_password:
            usuario.set_password(password)
            cambios.append('contrasena reestablecida desde ADMIN_PASSWORD')
        if cambios:
            db.session.commit()
            print(f"Usuario '{username}' ya existia. {'; '.join(cambios)}.")
        else:
            print(f"Usuario '{username}' ya existe y esta correcto. Sin cambios.")
        return 0

    usuario = Usuario(
        username=username,
        role=ROL_ADMINISTRADOR,
        email=os.environ.get('ADMIN_EMAIL', f'{username}@sadi.local'),
        cargo='Administrador del SGSI',
        is_active=True,
    )
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()
    print(f"Usuario administrador '{username}' creado correctamente.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset-password', action='store_true',
                        help='Reestablece la contrasena si el usuario ya existe.')
    args = parser.parse_args()
    with app.app_context():
        return crear_administrador(reset_password=args.reset_password)


if __name__ == '__main__':
    sys.exit(main())
