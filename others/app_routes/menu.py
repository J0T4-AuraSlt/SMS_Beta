from flask import Blueprint, render_template, session, redirect, url_for, flash
from db_config import get_db_connection
import json
import logging

bp = Blueprint('menu', __name__, url_prefix='/menu')


@bp.route('/')
def menu():
    ID_CLIENTE_DEFAULT = 4
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    id_usuario = session.get('id_usuario', '').strip().lower()

    if not id_usuario:
        return redirect(url_for('auth.index'))

    menu_json = get_menu(ID_CLIENTE, id_usuario)
    if isinstance(menu_json, dict) and "message" in menu_json:
        flash(menu_json["message"], "error")
        return redirect(url_for('auth.index'))

    return render_template('menu.html', menu=menu_json)


def get_menu(ID_CLIENTE, id_usuario):
    """Obtiene el menú desde la base de datos."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT public.get_menu(%s, %s)",
                            (ID_CLIENTE, id_usuario))
                result = cur.fetchone()

        if result and result[0]:
            menu_json = json.loads(result[0]) if isinstance(
                result[0], str) else result[0]
            if not menu_json:
                return {"message": "El menú no tiene información disponible."}
            return menu_json
        else:
            return {"message": "No se ha encontrado información para este usuario."}
    except Exception as e:
        logging.error("Error al obtener el menú: %s", e)
        return {"message": "Error al obtener el menú. Intenta de nuevo más tarde."}
