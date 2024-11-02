from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from db_config import get_db_connection
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/')
def index():
    return render_template('login.html')


@bp.route('/login', methods=['POST'])
def login():
    ID_CLIENTE_DEFAULT = 4
    ID_CLIENTE = ID_CLIENTE_DEFAULT
    id_usuario = request.form.get('id_usuario', '').strip().lower()
    pwd = request.form.get('pwd', '').strip()

    if not id_usuario or not pwd:
        flash("Por favor, completa ambos campos para continuar ;).", "error")
        return render_template('login.html')

    validacion = valida_acceso(ID_CLIENTE, id_usuario, pwd)

    if validacion.startswith('OK'):
        session['ID_CLIENTE'] = ID_CLIENTE
        session['id_usuario'] = id_usuario
        return redirect(url_for('menu.menu'))  # Redirige al menú principal
    else:
        error = validacion.split(
            ';')[1] if ';' in validacion else "Credenciales incorrectas"
        flash(error, "error")
        return render_template('login.html')


def valida_acceso(ID_CLIENTE, id_usuario, pwd):
    id_usuario = id_usuario.lower()
    if len(id_usuario) < 3:
        return "ERROR;ID Usuario debe tener al menos 3 caracteres"

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT public.valida_acceso(%s, %s, %s)",
                            (ID_CLIENTE, id_usuario, pwd))
                result = cur.fetchone()
        return result[0] if result else "ERROR;Credenciales incorrectas"
    except Exception as e:
        logging.error("Error al validar acceso: %s", e)
        return "ERROR;Error interno. Intenta de nuevo más tarde."


@bp.route('/logout')
def logout():
    session.clear()  # Limpiar todas las cookies y la sesión
    return redirect(url_for('auth.index'))  # Redirigir al login
