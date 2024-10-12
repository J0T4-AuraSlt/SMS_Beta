import os
import json
import logging
import re
from datetime import datetime
from flask import Flask, request, render_template, url_for, flash, session, redirect, abort
from db_config import get_db_connection
from jinja2 import TemplateNotFound

# Configuración de logging
# control para DEBUG, INFO, WARNING, ERROR o CRITICAL
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuraciones de seguridad
# Utiliza una variable de entorno para la clave secreta
app.secret_key = os.environ.get('SECRET_KEY', 'clave_por_defecto_segura')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # Asegúrate de usar HTTPS en producción
    SESSION_COOKIE_SAMESITE='Lax'
)

# Valor por defecto, se puede ajustar según la lógica de la aplicación
ID_CLIENTE_DEFAULT = 4
# El cliente se define por la URL que este consultando, base a esto hereda el ID para todo lo demás


def construir_menu(menu_json):
    """Construye la estructura del menú a partir de la respuesta JSON."""
    menu = []
    for item in menu_json:
        if item['tpo_nodo'] == 'PADRE':
            menu.append({
                'path': item['path'],
                'descripcion': item['descripcion'],
                'hijos': []
            })
        elif item['tpo_nodo'] == 'HIJO' and menu:
            menu[-1]['hijos'].append({
                'path': item['path'],
                'descripcion': item['descripcion']
            })
    return menu


@app.context_processor
def inject_user_data():
    """Inyecta datos del usuario en el contexto de las plantillas."""
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    id_usuario = session.get('id_usuario')
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return dict(ID_CLIENTE=ID_CLIENTE, id_usuario=id_usuario, fecha_hora=fecha_hora)


@app.route('/')
def index():
    """Ruta principal que renderiza la página de login."""
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """Maneja el proceso de login del usuario."""
    ID_CLIENTE = ID_CLIENTE_DEFAULT  # Puedes ajustar esta lógica para obtener el ID_CLIENTE desde la URL u otra fuente
    id_usuario = request.form.get('id_usuario', '').strip().lower()
    pwd = request.form.get('pwd', '').strip()

    if not id_usuario or not pwd:
        flash("Por favor, completa ambos campos.", "error")
        return render_template('login.html')

    # Validar las credenciales de acceso
    validacion = valida_acceso(ID_CLIENTE, id_usuario, pwd)

    if validacion.startswith('OK'):
        # Almacenar en la sesión
        session['ID_CLIENTE'] = ID_CLIENTE
        session['id_usuario'] = id_usuario
        logger.info("ID_CLIENTE: %s, id_usuario: %s", ID_CLIENTE, id_usuario)

        # Obtener el menú si la validación es exitosa
        menu_json = get_menu(ID_CLIENTE, id_usuario)

        if isinstance(menu_json, dict) and "message" in menu_json:
            flash(menu_json["message"], "error")
            return render_template('login.html')

        menu = construir_menu(menu_json)

        return render_template('menu.html', menu=menu, id_usuario=id_usuario, ID_CLIENTE=ID_CLIENTE)
    else:
        error = validacion.split(
            ';')[1] if ';' in validacion else "Credenciales incorrectas"
        flash(error, "error")
        return render_template('login.html')


def valida_acceso(ID_CLIENTE, id_usuario, pwd):
    """Valida las credenciales del usuario."""
    id_usuario = id_usuario.lower()

    if len(id_usuario) < 3:
        return "ERROR;ID Usuario debe tener al menos 5 caracteres"

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT public.valida_acceso(%s, %s, %s)",
                            (ID_CLIENTE, id_usuario, pwd))
                result = cur.fetchone()
        return result[0] if result else "ERROR;Credenciales incorrectas"
    except Exception as e:
        logger.error("Error al validar acceso: %s", e)
        return "ERROR;Error interno. Intenta de nuevo más tarde."


def get_menu(ID_CLIENTE, id_usuario):
    """Obtiene el menú para el usuario desde la base de datos."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT public.get_menu(%s, %s)",
                            (ID_CLIENTE, id_usuario))
                result = cur.fetchone()

        if result and result[0]:
            if isinstance(result[0], list):
                menu_json = result[0]
            else:
                try:
                    menu_json = json.loads(result[0])
                except json.JSONDecodeError:
                    logger.error("Error al decodificar el menú JSON.")
                    return {"message": "Error al decodificar el menú desde el servidor."}

            if not menu_json:
                return {"message": "El menú no tiene información disponible."}

            return menu_json
        else:
            return {"message": "No se ha encontrado información para este usuario."}
    except Exception as e:
        logger.error("Error al obtener el menú: %s", e)
        return {"message": "Error al obtener el menú. Intenta de nuevo más tarde."}


@app.route('/menu')
def menu():
    """Ruta que muestra el menú al usuario autenticado."""
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    id_usuario = session.get('id_usuario')

    logger.info(f"ID_CLIENTE: {ID_CLIENTE}, id_usuario: {id_usuario}")

    # Verificar si hay sesión válida
    if not id_usuario:
        logger.info("Redireccionando a dev: falta id_usuario")
        return redirect(url_for('dev'))

    # Llamar a la función para obtener el menú
    menu_json = get_menu(ID_CLIENTE, id_usuario)
    logger.info(f"Menu JSON obtenido: {menu_json}")

    # Verificar si hay un mensaje de error en el JSON del menú
    if isinstance(menu_json, dict) and "message" in menu_json:
        flash(menu_json["message"], "error")
        return redirect(url_for('dev'))

    # Construir el menú para renderizarlo en la plantilla
    menu = construir_menu(menu_json)
    logger.info(f"Menú construido: {menu}")

    # Llamar a la función para obtener la información del usuario
    user_data = get_user_menu(ID_CLIENTE, id_usuario)
    logger.info(f"User Data obtenido: {user_data}")

    # Verificar si la información del usuario es válida
    if not user_data:
        logger.error("Error al obtener la información del usuario.")
        flash("Error al obtener la información del usuario.", "error")
        return redirect(url_for('dev'))

    # Obtener módulos del usuario desde la respuesta del JSON
    load_module = [mod['desc_modulo'] for mod in user_data['modulos']]
    logger.info(f"Módulos obtenidos: {load_module}")

    # Renderizar la plantilla del menú con los datos obtenidos
    return render_template('menu.html',
                           nom_usr=user_data['nom_usr'],
                           raz_social=user_data['raz_social'],
                           dsc=user_data['dsc'],
                           load_module=load_module,
                           id_usuario=id_usuario,
                           menu=menu)


@app.route('/mod/<module_name>')
def load_module(module_name):
    """Ruta dinámica para cargar módulos."""
    # Validar el nombre del módulo para evitar accesos no deseados
    if not re.match("^[a-zA-Z0-9_]+$", module_name):
        abort(404)

    try:
        return render_template(f'mod/{module_name}.html')
    except TemplateNotFound:
        flash("Módulo no encontrado.", "error")
        return redirect(url_for('menu'))
    except Exception as e:
        logger.error("Error al cargar el módulo %s: %s", module_name, e)
        flash("Error al cargar el módulo.", "error")
        return redirect(url_for('menu'))


@app.route('/mod/mAdmcreusr', methods=['GET', 'POST'])
def crear_usuario():
    # Suponiendo que tienes el id_usuario disponible en la sesión o en el contexto
    # Obtén el id del usuario que hizo login
    id_usuario = session.get('id_usuario')

    if request.method == 'POST':
        # Obtener datos del formulario
        id_clt = request.form.get('id_clt')
        rut_usr = request.form.get('rut_usr')
        dv_usr = request.form.get('dv_usr')
        nomb_usr = request.form.get('nomb_usr')
        ape_pat_usr = request.form.get('ape_pat_usr')
        ape_mat_usr = request.form.get('ape_mat_usr')
        ema_usr = request.form.get('ema_usr')
        cel_usr = request.form.get('cel_usr')
        id_tda = request.form.get('id_tda')
        id_prf = request.form.get('id_prf')
        pwd = request.form.get('pwd')
        # Obtener el nuevo campo de nombre de usuario
        # nombre_usuario = request.form.get('nombre_usuario')

        # Llamar a la función SQL crea_usuario
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Asegúrate de que la cantidad y el orden de los parámetros coincidan con la definición de la función SQL
                    cur.execute("SELECT public.crea_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s);",
                                (id_clt, rut_usr, dv_usr, nomb_usr, ape_pat_usr, ape_mat_usr,
                                 ema_usr, cel_usr, id_tda, id_prf, pwd, id_usuario))  # Cambiado el orden

                    # Recuperar la respuesta
                    respuesta = cur.fetchone()[0]

            # Manejar la respuesta de la función SQL
            if respuesta.startswith('OK'):
                flash(respuesta.split(';')[1], 'success')
                return redirect(url_for('menu'))
            else:
                flash(respuesta.split(';')[1], 'error')
                return redirect(url_for('crear_usuario'))

        except Exception as e:
            flash(f"Error al crear el usuario: {str(e)}", 'error')
            return redirect(url_for('crear_usuario'))

    return render_template('mod/mAdmcreusr.html')


@app.route('/get_user_menu', methods=['POST'])
def get_user_menu():
    if request.method == 'POST':
        try:
            # Obtener los datos enviados en la solicitud
            id_cliente = request.json.get('id_cliente')
            id_usuario = request.json.get('id_usuario')

            # Validar que se hayan enviado los parámetros
            if not id_cliente or not id_usuario:
                return jsonify({"message": "Faltan parámetros: id_cliente o id_usuario"}), 400

            # Llamar a la función get_user_menu de la base de datos
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT public.get_user_menu(%s, %s)",
                                (id_cliente, id_usuario))
                    result = cur.fetchone()

            # Verificar si la función retornó un resultado
            if result and result[0]:
                user_menu_json = result[0]

                # Aquí imprimes el JSON que devuelve la función SQL
                print(
                    f"Resultado de la función SQL (user_menu_json): {user_menu_json}")

                # Asegúrate de que user_menu_json tenga la estructura adecuada
                # Ejemplo de estructura esperada:
                # user_menu_json = {
                #     "raz_social": "Nombre de la Empresa",
                #     "nom_usr": "VENDEDOR",
                #     "dsc": "Descripción del Usuario",
                #     "modulos": ["Modulo1", "Modulo2", "Modulo3"]
                # }

                return jsonify(user_menu_json), 200
            else:
                return jsonify({"message": "No se ha encontrado información para este usuario."}), 404

        except Exception as e:
            logger.error("Error al obtener el menú del usuario: %s", e)
            return jsonify({"message": "Error interno al procesar la solicitud."}), 500

    # Si no es POST, devolver un error 405 (Método no permitido)
    return jsonify({"message": "Método no permitido"}), 405


@app.route('/mod/mAdmcreusr')
def mAdmcreusr():
    return render_template('mAdmcreusr.html')


@app.route('/mod/mAdmgstrol')
def mAdmgstrol():
    return render_template('mod/mAdmgstrol.html')


@app.route('/mod/mAdmgstper')
def mAdmgstper():
    return render_template('mod/mAdmgstper.html')


@app.route('/mod/mAdmmonact')
def mAdmmonact():
    return render_template('mod/mAdmmonact.html')


@app.route('/mod/mAdmrstpwd')
def mAdmrstpwd():
    return render_template('mod/mAdmrstpwd.html')


@app.route('/mod/mAdmcfgnot')
def mAdmcfgnot():
    return render_template('mod/mAdmcfgnot.html')


@app.route('/mod/mAdmmntdat')
def mAdmmntdat():
    return render_template('mod/mAdmmntdat.html')

# Menu


# @app.route('/mGesdmaest')
# def mGesdmaest():
#    return render_template('mGesdmaest.html')
# Modulos


@app.route('/mod/mGescrgart')
def mGescrgart():
    return render_template('mod/mGescrgart.html')


@app.route('/mod/mGescrgtnd')
def mGescrgtnd():
    return render_template('mod/mGescrgtnd.html')


@app.route('/mod/mGescrgcli')
def mGescrgcli():
    return render_template('mod/mGescrgcli.html')


@app.route('/mod/mGescrgprv')
def mGescrgprv():
    return render_template('mod/mGescrgprv.html')


@app.route('/mod/mGescrgcat')
def mGescrgcat():
    return render_template('mod/mGescrgcat.html')


@app.route('/mod/mGescrgprc')
def mGescrgprc():
    return render_template('mod/mGescrgprc.html')


@app.route('/mod/mGescrgimp')
def mGescrgimp():
    return render_template('mod/mGescrgimp.html')


@app.route('/mod/mGescrgpro')
def mGescrgpro():
    return render_template('mod/mGescrgpro.html')

# Menu


# @app.route('/mPInventar')
# def mPInventar():
#    return render_template('mPInventar.html')

# Modulos


@app.route('/mod/mInvcrginv')
def mInvcrginv():
    return render_template('mod/mInvcrginv.html')


@app.route('/mod/mInvstktnd')
def mInvstktnd():
    return render_template('mod/mInvstktnd.html')


@app.route('/mod/mInvstkcli')
def mInvstkcli():
    return render_template('mod/mInvstkcli.html')


@app.route('/mod/mInvstkjer')
def mInvstkjer():
    return render_template('mod/mInvstkjer.html')


@app.route('/mod/mInvajstin')
def mInvajstin():
    return render_template('mod/mInvajstin.html')


@app.route('/mod/mInvgstdev')
def mInvgstdev():
    return render_template('mod/mInvgstdev.html')


@app.route('/mod/mInvctlcad')
def mInvctlcad():
    return render_template('mod/mInvctlcad.html')


@app.route('/mod/mInvgstlot')
def mInvgstlot():
    return render_template('mod/mInvgstlot.html')


@app.route('/mod/mInvhismov')
def mInvhismov():
    return render_template('mod/mInvhismov.html')

# Menu


# @app.route('/mPgesanlve')
# def mPgesanlve():
#    return render_template('mPgesanlve.html')
# Modulo


@app.route('/mod/mGesanlven')
def mGesanlven():
    return render_template('mod/mGesanlven.html')


@app.route('/mod/mGesvendia')
def mGesvendia():
    return render_template('mod/mGesvendia.html')


@app.route('/mod/mGesvenret')
def mGesvenret():
    return render_template('mod/mGesvenret.html')


@app.route('/mod/mGesdevree')
def mGesdevree():
    return render_template('mod/mGesdevree.html')


@app.route('/mod/mGesclifre')
def mGesclifre():
    return render_template('mod/mGesclifre.html')


@app.route('/mod/mGespromde')
def mGespromde():
    return render_template('mod/mGespromde.html')


@app.route('/mod/mGesfactur')
def mGesfactur():
    return render_template('mod/mGesfactur.html')


@app.route('/mod/mGespagcob')
def mGespagcob():
    return render_template('mod/mGespagcob.html')


@app.route('/mod/mGessegven')
def mGessegven():
    return render_template('mod/mGessegven.html')
# Menu


# @app.route('/mPreportes')
# def mPreportes():
#    return render_template('mPreportes.html')
# Modulo


@app.route('/mod/mRepinfven')
def mRepinfven():
    return render_template('mod/mRepinfven.html')


@app.route('/mod/mRepinfstk')
def mRepinfstk():
    return render_template('mod/mRepinfstk.html')


@app.route('/mod/mRepventnd')
def mRepventnd():
    return render_template('mod/mRepventnd.html')


@app.route('/mod/mRepsugcom')
def mRepsugcom():
    return render_template('mod/mRepsugcom.html')


@app.route('/mod/mReptoppro')
def mReptoppro():
    return render_template('mod/mReptoppro.html')


@app.route('/mod/mRepdetpro')
def mRepdetpro():
    return render_template('mod/mRepdetpro.html')


@app.route('/mod/mRepcummet')
def mRepcummet():
    return render_template('mod/mRepcummet.html')


@app.route('/mod/mRepinfcli')
def mRepinfcli():
    return render_template('mod/mRepinfcli.html')


@app.route('/mod/mRepinfprv')
def mRepinfprv():
    return render_template('mod/mRepinfprv.html')


@app.route('/mod/mRepinfdev')
def mRepinfdev():
    return render_template('mod/mRepinfdev.html')


@app.route('/mod/mRepinffin')
def mRepinffin():
    return render_template('mod/mRepinffin.html')


@app.route('/mod/mRepinfemp')
def mRepinfemp():
    return render_template('mod/mRepinfemp.html')


@app.route('/mod/mRepinfinv')
def mRepinfinv():
    return render_template('mod/mRepinfinv.html')


@app.route('/mod/mRepinfmkt')
def mRepinfmkt():
    return render_template('mod/mRepinfmkt.html')


@app.route('/mod/mRepinfcum')
def mRepinfcum():
    return render_template('mod/mRepinfcum.html')


@app.route('/mod/mRepinften')
def mRepinften():
    return render_template('mod/mRepinften.html')


@app.route('/mod/mRepinfsat')
def mRepinfsat():
    return render_template('mod/mRepinfsat.html')
# Menu


# @app.route('/mPgesdasis')
# def mPgesdasis():
#    return render_template('mPgesdasis.html')
# Modulo


@app.route('/mod/mGesrptasg')
def mGesrptasg():
    return render_template('mod/mGesrptasg.html')


@app.route('/mod/mGesrptasc')
def mGesrptasc():
    return render_template('mod/mGesrptasc.html')


@app.route('/mod/mGesrptast')
def mGesrptast():
    return render_template('mod/mGesrptast.html')


@app.route('/mod/mGesrptret')
def mGesrptret():
    return render_template('mod/mGesrptret.html')


@app.route('/mod/mGesrptaus')
def mGesrptaus():
    return render_template('mod/mGesrptaus.html')


@app.route('/mod/mGesrpthex')
def mGesrpthex():
    return render_template('mod/mGesrpthex.html')


@app.route('/mod/mGesrptsal')
def mGesrptsal():
    return render_template('mod/mGesrptsal.html')


@app.route('/mod/mGesrptmar')
def mGesrptmar():
    return render_template('mod/mGesrptmar.html')


@app.route('/mod/mGesrptinc')
def mGesrptinc():
    return render_template('mod/mGesrptinc.html')


@app.route('/mod/mGesrptcum')
def mGesrptcum():
    return render_template('mod/mGesrptcum.html')


@app.route('/mod/mGesrptres')
def mGesrptres():
    return render_template('mod/mGesrptres.html')


@app.route('/mod/mGesrptvac')
def mGesrptvac():
    return render_template('mod/mGesrptvac.html')
# Menu


# @app.route('/mPgesdaler')
# def mPgesdaler():
#    return render_template('mPgesdaler.html')
# Modulo


@app.route('/mod/mGesaltqui')
def mGesaltqui():
    return render_template('mod/mGesaltqui.html')


@app.route('/mod/mGesaltnds')
def mGesaltnds():
    return render_template('mod/mGesaltnds.html')


@app.route('/mod/mGesaltsob')
def mGesaltsob():
    return render_template('mod/mGesaltsob.html')


@app.route('/dev')
def dev():
    """Ruta para desarrollo o manejo de errores."""
    return render_template('dev.html')

# Manejo de errores personalizados


@app.errorhandler(404)
def pagina_no_encontrada(e):
    """Manejador para errores 404."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    """Manejador para errores 500."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
