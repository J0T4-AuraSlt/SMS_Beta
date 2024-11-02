from flask import Flask, request, jsonify
import os
import json
import logging
import re
from datetime import datetime
from flask import Flask, request, render_template, url_for, flash, session, redirect, abort, jsonify
from db_config import get_db_connection
from jinja2 import TemplateNotFound
import smtplib
from email.mime.text import MIMEText

# Configuración de logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Desactivar temporalmente la protección CSRF si estás usando Flask-WTF
app.config['WTF_CSRF_ENABLED'] = False

# Configuraciones de seguridad
app.secret_key = os.environ.get('SECRET_KEY', 'clave_por_defecto_segura')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_SAMESITE='Lax'
)

ID_CLIENTE_DEFAULT = 4


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
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return dict(ID_CLIENTE=ID_CLIENTE, id_usuario=id_usuario, fecha_hora=fecha_hora)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # Puedes ajustar esta lógica para obtener el ID_CLIENTE desde la URL u otra fuente
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
        logger.info("ID_CLIENTE: %s, id_usuario: %s", ID_CLIENTE, id_usuario)

        return redirect(url_for('menu'))
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


def obtener_user_menu(ID_CLIENTE, id_usuario):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT public.get_user_menu(%s, %s)",
                            (ID_CLIENTE, id_usuario))
                result = cur.fetchone()

        if result and result[0]:
            user_menu_json = result[0]
            return json.loads(user_menu_json) if isinstance(user_menu_json, str) else user_menu_json
        else:
            return None
    except Exception as e:
        logger.error("Error al obtener la información del usuario: %s", e)
        return None


@app.route('/menu')
def menu():
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    id_usuario = session.get('id_usuario', '').strip().lower()

    logger.info(f"ID_CLIENTE: {ID_CLIENTE}, id_usuario: {id_usuario}")

    if not id_usuario:
        logger.info("Redireccionando a dev: falta id_usuario")
        return redirect(url_for('dev'))

    menu_json = get_menu(ID_CLIENTE, id_usuario)
    if isinstance(menu_json, dict) and "message" in menu_json:
        flash(menu_json["message"], "error")
        return redirect(url_for('dev'))
    menu = construir_menu(menu_json)

    user_data = obtener_user_menu(ID_CLIENTE, id_usuario)

    if not user_data:
        logger.error("Error al obtener la información del usuario.")
        flash("Error al obtener la información del usuario.", "error")
        return redirect(url_for('dev'))

    load_module = [mod['desc_modulo'] for mod in user_data.get('modulos', [])]

    return render_template('menu.html',
                           nom_usr=user_data['nom_usr'],
                           raz_social=user_data['raz_social'],
                           dsc=user_data['dsc'],
                           load_module=load_module,
                           id_usuario=id_usuario,
                           menu=menu)


@app.route('/get_user_menu', methods=['POST'])
def get_user_menu_route():
    if request.method == 'POST':
        try:
            id_cliente = request.json.get('id_cliente')
            id_usuario = request.json.get('id_usuario', '').strip().lower()
            if not id_cliente or not id_usuario:
                return jsonify({"message": "Faltan parámetros: id_cliente o id_usuario"}), 400

            user_data = obtener_user_menu(id_cliente, id_usuario)

            if user_data:
                return jsonify({"message": "Información del usuario obtenida correctamente."}), 200
            else:
                return jsonify({"message": "No se ha encontrado información para este usuario."}), 404

        except Exception as e:
            return jsonify({"message": "Error interno al procesar la solicitud."}), 500

    return jsonify({"message": "Método no permitido"}), 405


# @ app.route('/mod/<module_name>')
# def load_module(module_name):
#     if not re.match("^[a-zA-Z0-9_]+$", module_name):
#         abort(404)

#     try:
#         return render_template(f'mod/{module_name}.html')
#     except TemplateNotFound:
#         flash("Módulo no encontrado.", "error")
#         return redirect(url_for('menu'))
#     except Exception as e:
#         logger.error("Error al cargar el módulo %s: %s", module_name, e)
#         flash("Error al cargar el módulo.", "error")
#         return redirect(url_for('menu'))
@app.route('/mod/<module_name>')
def load_module(module_name):
    if not re.match("^[a-zA-Z0-9_]+$", module_name):
        abort(404)

    try:
        # Cargar el HTML del módulo dinámicamente
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
    id_usuario = session.get('id_usuario', '').strip().lower()

    if request.method == 'POST':
        # Obtener los valores del formulario
        id_clt = request.form.get('id_clt')
        rut_usr = request.form.get('rut_usr')
        dv_usr = request.form.get('dv_usr')
        nomb_usr = request.form.get('nomb_usr')
        ape_pat_usr = request.form.get('ape_pat_usr')
        ape_mat_usr = request.form.get('ape_mat_usr')
        ema_usr = request.form.get('ema_usr').lower()
        cel_usr = request.form.get('cel_usr')
        id_tda = request.form.get('id_tda')
        id_prf = request.form.get('id_prf')
        pwd = request.form.get('pwd')

        # Verificar que los campos requeridos estén completos
        if not (rut_usr and dv_usr and nomb_usr and ape_pat_usr and ape_mat_usr and ema_usr and cel_usr and pwd and id_clt and id_tda and id_prf):
            flash('Por favor, complete todos los campos requeridos.', 'error')
            return render_template('mod/mAdmcreusr.html')

        print(
            f"Parámetros enviados: {id_clt}, {rut_usr}, {dv_usr}, {nomb_usr}, {ape_pat_usr}, {ape_mat_usr}, {ema_usr}, {cel_usr}, {id_tda}, {id_prf}, {pwd}, {id_usuario}")

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Llamar a la función crea_usuario en la base de datos
                    cur.execute("""
                        SELECT crea_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        id_clt,
                        rut_usr,
                        dv_usr,
                        nomb_usr,
                        ape_pat_usr,
                        ape_mat_usr,
                        ema_usr,
                        cel_usr,
                        id_tda,
                        id_prf,
                        pwd,
                        id_usuario  # usr_cre será el usuario que está creando el nuevo usuario
                    ))

                    respuesta = cur.fetchone()[0]
                    print(f"Respuesta de la función SQL: {respuesta}")

            # Validar la respuesta de la función SQL
            if respuesta.startswith('OK'):
                flash(respuesta.split(';')[1], 'success')
                return redirect(url_for('mAdmcreusr'))
            else:
                flash(respuesta.split(';')[1], 'error')
                return render_template('mod/mAdmcreusr.html')

        except Exception as e:
            print(f"Error al crear el usuario: {str(e)}")
            flash(f"Error al crear el usuario: {str(e)}", 'error')
            return render_template('mod/mAdmcreusr.html')

    return render_template('mod/mAdmcreusr.html')


def enviar_correo(email, nueva_contrasena):
    mensaje = f"Tu nueva contraseña temporal es: {nueva_contrasena}"
    msg = MIMEText(mensaje)
    msg['Subject'] = 'Restablecimiento de Contraseña'
    msg['From'] = 'reset_pass@portal.sms-vivo.com'
    msg['To'] = email

    try:
        with smtplib.SMTP('mail.auraslt.com', 465) as server:
            server.starttls()
            server.login('info@auraslt.com', '23!')
            server.sendmail('reset_pass@portal.sms-vivo.com',
                            email, msg.as_string())
        print("Correo enviado con éxito")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


@app.route('/restpass', methods=['POST'])
def restpass():
    id_usuario = request.form.get('id_usuario', '').strip().lower()
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    email_usr = request.form['email_usr']

    print(id_usuario, ID_CLIENTE, email_usr)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT restablecer_contraseña(%s, %s, %s)",
                            (id_usuario, ID_CLIENTE, email_usr))
                nueva_contrasena = "Aquí puedes generar o recuperar la nueva contraseña"

        enviar_correo(email_usr, nueva_contrasena)
        flash("Se ha enviado un correo con la nueva contraseña.")
        return redirect(url_for('login'))
    except Exception as e:
        flash("Por favor, valide su correo y siga las instrucciones.")
        return redirect(url_for('login'))


@app.route('/get_users', methods=['GET'])
def get_users():
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT get_users(%s)", (ID_CLIENTE))
                users = cur.fetchall()
        user_list = [
            {
                'id_usr': user[0],
                'raz_social': user[1],
                'nom_usr': user[2],
                'dsc': user[3],
                'pwd': user[4]
            }
            for user in users
        ]
        return jsonify(user_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset_user_password', methods=['POST'])
def reset_user_password():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    new_password = data.get('new_password')

    return jsonify({"message": "Se procesó OK, por favor validar su correo electrónico."}), 200


@app.route('/mod/reset_password', methods=['GET', 'POST'])
def restpass_view():
    if request.method == 'POST':
        return jsonify({"message": "Formulario enviado correctamente"}), 200
    return render_template('mod/mAdmrstpwd.html')


@app.route('/mod/mAdmrstpwd', methods=['GET'])
def mostrar_reset_password():
    return render_template('mod/mAdmrstpwd.html')


@app.route('/')
def reset_password():
    return render_template('login.html')


@ app.route('/mod/mAdmcreusr')
def mAdmcreusr():
    return render_template('mod/mAdmcreusr.html')


@ app.route('/mod/mAdmgstrol')
def mAdmgstrol():
    return render_template('mod/mAdmgstrol.html')


@ app.route('/mod/mAdmgstper')
def mAdmgstper():
    return render_template('mod/mAdmgstper.html')


@ app.route('/mod/mAdmmonact')
def mAdmmonact():
    return render_template('mod/mAdmmonact.html')


@ app.route('/mod/mAdmcfgnot')
def mAdmcfgnot():
    return render_template('mod/mAdmcfgnot.html')


@ app.route('/mod/mAdmmntdat')
def mAdmmntdat():
    return render_template('mod/mAdmmntdat.html')


@ app.route('/mod/mGescrgart')
def mGescrgart():
    return render_template('mod/mGescrgart.html')


@ app.route('/mod/mGescrgtnd')
def mGescrgtnd():
    return render_template('mod/mGescrgtnd.html')


@ app.route('/mod/mGescrgcli')
def mGescrgcli():
    return render_template('mod/mGescrgcli.html')


@ app.route('/mod/mGescrgprv')
def mGescrgprv():
    return render_template('mod/mGescrgprv.html')


@ app.route('/mod/mGescrgcat')
def mGescrgcat():
    return render_template('mod/mGescrgcat.html')


@ app.route('/mod/mGescrgprc')
def mGescrgprc():
    return render_template('mod/mGescrgprc.html')


@ app.route('/mod/mGescrgimp')
def mGescrgimp():
    return render_template('mod/mGescrgimp.html')


@ app.route('/mod/mGescrgpro')
def mGescrgpro():
    return render_template('mod/mGescrgpro.html')


@ app.route('/mod/mInvcrginv')
def mInvcrginv():
    return render_template('mod/mInvcrginv.html')


@ app.route('/mod/mInvstktnd')
def mInvstktnd():
    return render_template('mod/mInvstktnd.html')


@ app.route('/mod/mInvstkcli')
def mInvstkcli():
    return render_template('mod/mInvstkcli.html')


@ app.route('/mod/mInvstkjer')
def mInvstkjer():
    return render_template('mod/mInvstkjer.html')


@ app.route('/mod/mInvajstin')
def mInvajstin():
    return render_template('mod/mInvajstin.html')


@ app.route('/mod/mInvgstdev')
def mInvgstdev():
    return render_template('mod/mInvgstdev.html')


@ app.route('/mod/mInvctlcad')
def mInvctlcad():
    return render_template('mod/mInvctlcad.html')


@ app.route('/mod/mInvgstlot')
def mInvgstlot():
    return render_template('mod/mInvgstlot.html')


@ app.route('/mod/mInvhismov')
def mInvhismov():
    return render_template('mod/mInvhismov.html')


@ app.route('/mod/mGesanlven')
def mGesanlven():
    return render_template('mod/mGesanlven.html')


@ app.route('/mod/mGesvendia')
def mGesvendia():
    return render_template('mod/mGesvendia.html')


@ app.route('/mod/mGesvenret')
def mGesvenret():
    return render_template('mod/mGesvenret.html')


@ app.route('/mod/mGesdevree')
def mGesdevree():
    return render_template('mod/mGesdevree.html')


@ app.route('/mod/mGesclifre')
def mGesclifre():
    return render_template('mod/mGesclifre.html')


@ app.route('/mod/mGespromde')
def mGespromde():
    return render_template('mod/mGespromde.html')


@ app.route('/mod/mGesfactur')
def mGesfactur():
    return render_template('mod/mGesfactur.html')


@ app.route('/mod/mGespagcob')
def mGespagcob():
    return render_template('mod/mGespagcob.html')


@ app.route('/mod/mGessegven')
def mGessegven():
    return render_template('mod/mGessegven.html')


@ app.route('/mod/mRepinfven')
def mRepinfven():
    return render_template('mod/mRepinfven.html')


@ app.route('/mod/mRepinfstk')
def mRepinfstk():
    return render_template('mod/mRepinfstk.html')


@ app.route('/mod/mRepventnd')
def mRepventnd():
    return render_template('mod/mRepventnd.html')


@ app.route('/mod/mRepsugcom')
def mRepsugcom():
    return render_template('mod/mRepsugcom.html')


@ app.route('/mod/mReptoppro')
def mReptoppro():
    return render_template('mod/mReptoppro.html')


@ app.route('/mod/mRepdetpro')
def mRepdetpro():
    return render_template('mod/mRepdetpro.html')


@ app.route('/mod/mRepcummet')
def mRepcummet():
    return render_template('mod/mRepcummet.html')


@ app.route('/mod/mRepinfcli')
def mRepinfcli():
    return render_template('mod/mRepinfcli.html')


@ app.route('/mod/mRepinfprv')
def mRepinfprv():
    return render_template('mod/mRepinfprv.html')


@ app.route('/mod/mRepinfdev')
def mRepinfdev():
    return render_template('mod/mRepinfdev.html')


@ app.route('/mod/mRepinffin')
def mRepinffin():
    return render_template('mod/mRepinffin.html')


@ app.route('/mod/mRepinfemp')
def mRepinfemp():
    return render_template('mod/mRepinfemp.html')


@ app.route('/mod/mRepinfinv')
def mRepinfinv():
    return render_template('mod/mRepinfinv.html')


@ app.route('/mod/mRepinfmkt')
def mRepinfmkt():
    return render_template('mod/mRepinfmkt.html')


@ app.route('/mod/mRepinfcum')
def mRepinfcum():
    return render_template('mod/mRepinfcum.html')


@ app.route('/mod/mRepinften')
def mRepinften():
    return render_template('mod/mRepinften.html')


@ app.route('/mod/mRepinfsat')
def mRepinfsat():
    return render_template('mod/mRepinfsat.html')


@ app.route('/mod/mGesrptasg')
def mGesrptasg():
    return render_template('mod/mGesrptasg.html')


@ app.route('/mod/mGesrptasc')
def mGesrptasc():
    return render_template('mod/mGesrptasc.html')


@ app.route('/mod/mGesrptast')
def mGesrptast():
    return render_template('mod/mGesrptast.html')


@ app.route('/mod/mGesrptret')
def mGesrptret():
    return render_template('mod/mGesrptret.html')


@ app.route('/mod/mGesrptaus')
def mGesrptaus():
    return render_template('mod/mGesrptaus.html')


@ app.route('/mod/mGesrpthex')
def mGesrpthex():
    return render_template('mod/mGesrpthex.html')


@ app.route('/mod/mGesrptsal')
def mGesrptsal():
    return render_template('mod/mGesrptsal.html')


@ app.route('/mod/mGesrptmar')
def mGesrptmar():
    return render_template('mod/mGesrptmar.html')


@ app.route('/mod/mGesrptinc')
def mGesrptinc():
    return render_template('mod/mGesrptinc.html')


@ app.route('/mod/mGesrptcum')
def mGesrptcum():
    return render_template('mod/mGesrptcum.html')


@ app.route('/mod/mGesrptres')
def mGesrptres():
    return render_template('mod/mGesrptres.html')


@ app.route('/mod/mGesrptvac')
def mGesrptvac():
    return render_template('mod/mGesrptvac.html')


@ app.route('/mod/mGesaltqui')
def mGesaltqui():
    return render_template('mod/mGesaltqui.html')


@ app.route('/mod/mGesaltnds')
def mGesaltnds():
    return render_template('mod/mGesaltnds.html')


@ app.route('/mod/mGesaltsob')
def mGesaltsob():
    return render_template('mod/mGesaltsob.html')


@app.route('/dev')
def dev():
    id_usuario = session.get(
        'id_usuario', 'Usuario no definido')  # Valor por defecto
    return render_template('dev.html', id_usuario=id_usuario)


@app.route('/logout')
def logout():
    session.clear()  # Limpiar todas las cookies y la sesión
    return redirect(url_for('login.htm'))  # Redirigir al login


# Manejo de errores personalizados
@ app.errorhandler(404)
def pagina_no_encontrada(e):
    """Manejador para errores 404."""
    return render_template('404.html'), 404


@ app.errorhandler(500)
def error_interno(e):
    """Manejador para errores 500."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
    # , port=5001)
