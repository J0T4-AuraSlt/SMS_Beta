from flask import Flask, request, jsonify
import os
import json
import logging
import re
from datetime import datetime
from flask import Flask, request, render_template, url_for, flash, session, redirect, abort, jsonify
from db_config import get_db_connection, release_db_connection
from jinja2 import TemplateNotFound
import smtplib
from email.mime.text import MIMEText

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
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

# Diccionario de iconos para el menú
ICONOS_MENU = {
    "Administracion": "fas fa-cogs",
    "Creación de usuarios": "fas fa-user-plus",
    "Gestión de Roles y Permisos": "fas fa-user-shield",
    "Gestión de Perfiles de Acceso": "fas fa-id-badge",
    "Monitoreo de Actividad de Usuarios": "fas fa-chart-line",
    "Restablecer Contraseñas": "fas fa-unlock-alt",
    "Configuración de Notificaciones": "fas fa-bell",
    "Mantenimiento de Datos del Usuario": "fas fa-user-edit",
    "Gestión de Maestros": "fas fa-server",
    "Carga de artículos": "fas fa-upload",
    "Carga de tiendas": "fas fa-upload",
    "Carga de Clientes": "fas fa-upload",
    "Carga de Proveedores": "fas fa-upload",
    "Carga de Categorías y Subcategorías": "fas fa-upload",
    "Carga de Precios y Descuentos": "fas fa-tags",
    "Carga de Impuestos y Tarifas": "fas fa-percent",
    "Carga de Promociones o Campañas": "fas fa-bullhorn",
    "Inventario": "fas fa-boxes",
    "Carga de Inv. Inicial por tienda": "fas fa-box",
    "Stock por tienda": "fas fa-box",
    "Stock por clientes": "fas fa-box",
    "Stock por jerarquía": "fas fa-box",
    "Ajustes de Inventario": "fas fa-boxes",
    "Gestión de Devoluciones": "fas fa-undo-alt",
    "Control de Caducidad": "fas fa-hourglass-end",
    "Gestión de Lotes y Series": "fas fa-boxes",
    "Historial de Movimientos": "fas fa-history",
    "Gestion de Ventas": "fas fa-shopping-cart",
    "Análisis de Ventas": "fas fa-chart-line",
    "Ventas diarias": "fas fa-calendar-day",
    "Ventas retail": "fas fa-cart-arrow-down",
    "Devoluciones y Reembolsos": "fas fa-exchange-alt",
    "Clientes Frecuentes": "fas fa-user-friends",
    "Promociones y Descuentos": "fas fa-tags",
    "Facturación": "fas fa-file-invoice-dollar",
    "Pagos y Cobros": "fas fa-money-bill-wave",
    "Seguimiento de Ventas por Vendedor": "fas fa-chart-line",
    "Reportes": "fas fa-file-alt",
    "Informes de Ventas": "fas fa-chart-bar",
    "Informes de Stock por tiendas": "fas fa-box",
    "Ventas por tiendas": "fas fa-store",
    "Sugerido de compras": "fas fa-shopping-bag",
    "Top 10 productos por tienda": "fas fa-star",
    "Detalle de promociones": "fas fa-tags",
    "Cumplimiento de metas por tienda": "fas fa-clipboard-check",
    "Informes de Clientes": "fas fa-user-tie",
    "Informes de Proveedores": "fas fa-truck",
    "Informes de Devoluciones": "fas fa-undo-alt",
    "Informes de Finanzas": "fas fa-chart-pie",
    "Informes de Empleados": "fas fa-users",
    "Informes de Inventario": "fas fa-boxes",
    "Informes de Marketing": "fas fa-bullhorn",
    "Informes de Cumplimiento": "fas fa-check-circle",
    "Informes de Tendencias": "fas fa-chart-line",
    "Informes de Satisfacción del Cliente": "fas fa-smile",
    "Gestión de Asistencia": "fas fa-user-clock",
    "Reporte de Asistencia General": "fas fa-clipboard",
    "Reporte de Asistencia por Cliente": "fas fa-clipboard-list",
    "Reporte de Asistencia por Turno": "fas fa-business-time",
    "Reporte de Retrasos": "fas fa-clock",
    "Reporte de Ausencias": "fas fa-user-slash",
    "Reporte de Horas Extras": "fas fa-user-clock",
    "Reporte de Salidas Anticipadas": "fas fa-sign-out-alt",
    "Reporte de Marcajes Duplicados o Incorrectos": "fas fa-user-times",
    "Reporte de Incidencias": "fas fa-exclamation-triangle",
    "Reporte de Cumplimiento de Horarios": "fas fa-clipboard-check",
    "Reporte de Resumen Mensual por Empleado": "fas fa-calendar-alt",
    "Reporte de Vacaciones y Permisos": "fas fa-plane-departure",
    "Gestión de Alertas": "fas fa-bell",
    "Alerta de quiebre de inventario": "fas fa-exclamation-triangle",
    "Alertas dirigidas a tiendas": "fas fa-store-alt",
    "Alerta de sobreventa": "fas fa-exclamation",
    "Alerta 4": "fas fa-info-circle",
    "Alerta 5": "fas fa-info-circle",
    "AI Hub": "fas fa-brain",
    "Análisis de Ventas": "fas fa-chart-line",
    "Gestión de Ventas": "fas fa-shopping-cart",
    "Productos para Ofertas": "fas fa-gift",
    "Notificaciones Inteligentes": "fas fa-robot"
}


def construir_menu(menu_json):
    """Construye la estructura del menú a partir de la respuesta JSON."""
    menu = []
    for item in menu_json:
        if item['tpo_nodo'] == 'PADRE':
            # Asignar el icono al menú según la descripción
            item_icono = ICONOS_MENU.get(
                item['descripcion'], "fas fa-cogs")
            menu.append({
                'path': item['path'],
                'descripcion': item['descripcion'],
                'icono': item_icono,
                'hijos': []
            })
        elif item['tpo_nodo'] == 'HIJO' and menu:
            # Asignar el icono a los hijos también
            item_icono = ICONOS_MENU.get(
                item['descripcion'], "fas fa-cogs")
            menu[-1]['hijos'].append({
                'path': item['path'],
                'descripcion': item['descripcion'],
                'icono': item_icono
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

    # if validacion.startswith('OK'):
    #     session['ID_CLIENTE'] = ID_CLIENTE
    #     session['id_usuario'] = id_usuario
    #     logger.info("ID_CLIENTE: %s, id_usuario: %s", ID_CLIENTE, id_usuario)

    #     return redirect(url_for('menu'))
    # #
    if validacion.startswith('OK'):
        session['ID_CLIENTE'] = ID_CLIENTE
        session['id_usuario'] = id_usuario
        logger.info("ID_CLIENTE: %s, id_usuario: %s", ID_CLIENTE, id_usuario)

        # Registrar el evento de inicio de sesión
        registrar_evento(
            id_cliente=ID_CLIENTE,
            id_usuario=id_usuario,
            modulo_accedido="login",
            accion="Inicio de sesión exitoso"
        )

        return redirect(url_for('menu'))
    else:
        error = validacion.split(
            ';')[1] if ';' in validacion else "Credenciales incorrectas"
        flash(error, "error")
        return render_template('login.html')

# Función para registrar eventos de usuario en la base de datos


def registrar_evento(id_cliente, id_usuario, modulo_accedido, accion, detalles=None):
    conn = get_db_connection()
    if conn is None:
        logger.error("No se pudo obtener una conexión de base de datos")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO registro_eventos (id_cliente, id_usuario, fecha, modulo_accedido, accion, detalles)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                id_cliente,
                id_usuario,
                datetime.now(),
                modulo_accedido,
                accion,
                json.dumps(detalles) if detalles else None
            ))
        conn.commit()
    except Exception as e:
        logger.error("Error al registrar el evento: %s", e)
    finally:
        release_db_connection(conn)


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
    """Obtiene el menú para el usuario desde la base de datos y agrega íconos."""
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

            # Agregar íconos al menú
            for item in menu_json:
                descripcion = item.get('descripcion', '')
                item['icono'] = ICONOS_MENU.get(
                    descripcion, "fas fa-question-circle")  # Ícono por defecto

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
        return redirect(url_for('login'))

    # Obtiene el menú del usuario desde la base de datos
    menu_json = get_menu(ID_CLIENTE, id_usuario)

    # Registrar el acceso al menú en la tabla de eventos
    registrar_evento(
        id_cliente=ID_CLIENTE,
        id_usuario=id_usuario,
        modulo_accedido="menu",
        accion="Acceso al menú principal"
    )

    # Verifica si el menú tiene mensajes de error
    if isinstance(menu_json, dict) and "message" in menu_json:
        flash(menu_json["message"], "error")
        return redirect(url_for('dev'))

    # Construye el menú usando la estructura JSON
    menu = construir_menu(menu_json)

    # Obtiene la información del usuario desde la base de datos
    user_data = obtener_user_menu(ID_CLIENTE, id_usuario)

    if not user_data:
        logger.error("Error al obtener la información del usuario.")
        flash("Error al obtener la información del usuario.", "error")
        return redirect(url_for('dev'))

    # Crea una lista de módulos para cargar en la interfaz
    load_module = [mod['desc_modulo'] for mod in user_data.get('modulos', [])]

    # Renderiza la plantilla del menú con la información del usuario y el menú
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
@ app.route('/mod/<module_name>')
def load_module(module_name):
    # Validación del nombre del módulo para evitar rutas inseguras
    if not re.match("^[a-zA-Z0-9_]+$", module_name):
        abort(404)

    # Obtener datos del usuario y cliente desde la sesión
    ID_CLIENTE = session.get('ID_CLIENTE', ID_CLIENTE_DEFAULT)
    id_usuario = session.get('id_usuario')

    # Registrar el evento de acceso al módulo en la base de datos
    registrar_evento(
        id_cliente=ID_CLIENTE,
        id_usuario=id_usuario,
        modulo_accedido=module_name,
        accion="Acceso al módulo"
    )

    try:
        # Renderizar la plantilla correspondiente al módulo
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
        # Obtener valores del formulario
        id_clt = request.form.get('id_clt', '').strip()
        rut_completo = request.form.get('rut', '').strip()
        nombre_usuario = request.form.get('nomb_usr', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        ema_usr = request.form.get('ema_usr', '').strip().lower()
        cel_usr = request.form.get('cel_usr', '').strip()
        id_tda = request.form.get('id_tda', '').strip()
        id_prf = request.form.get('id_prf', '').strip()
        pwd = request.form.get('pwd', '').strip()

        # Separar el RUT y el DV
        if '-' in rut_completo:
            rut_usr, dv_usr = rut_completo.split('-')
        else:
            rut_usr, dv_usr = rut_completo, ''  # Asignar DV vacío si no existe

        # Separar apellidos en paterno y materno
        apellido_paterno = apellido_materno = ''
        if apellidos:
            apellidos_split = apellidos.split(' ')
            apellido_paterno = apellidos_split[0] if len(
                apellidos_split) > 0 else ''
            apellido_materno = apellidos_split[1] if len(
                apellidos_split) > 1 else ''

        # Datos procesados listos para la inserción
        form_data = {
            'id_clt': id_clt,
            'rut_usr': rut_usr,
            'dv_usr': dv_usr,
            'nomb_usr': nombre_usuario,
            'ape_pat_usr': apellido_paterno,
            'ape_mat_usr': apellido_materno,
            'ema_usr': ema_usr,
            'cel_usr': cel_usr,
            'id_tda': id_tda,
            'id_prf': id_prf,
            'pwd': pwd,
        }

        # Imprimir los datos procesados para verificación
        print("Datos procesados para la creación de usuario:", form_data)

        # Verificar que todos los campos requeridos están completos
        if not all(form_data.values()):
            return jsonify({'status': 'error', 'message': 'Por favor, complete todos los campos requeridos.'}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Llamar a la función crea_usuario en la base de datos
                    cur.execute("""
                        SELECT crea_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        form_data['id_clt'], form_data['rut_usr'], form_data['dv_usr'], form_data['nomb_usr'],
                        form_data['ape_pat_usr'], form_data['ape_mat_usr'], form_data['ema_usr'],
                        form_data['cel_usr'], form_data['id_tda'], form_data['id_prf'], form_data['pwd'],
                        id_usuario
                    ))
                    respuesta = cur.fetchone()[0]

    #         if respuesta.startswith('OK'):
    #             return jsonify({"status": "success", "message": "USUARIO CREADO CON EXITO"})
    #         else:
    #             return jsonify({'status': 'error', 'message': respuesta.split(';')[1]}), 400

    #     except Exception as e:
    #         print(f"Error al crear el usuario: {str(e)}")
    #         return jsonify({"status": "error", "message": "Error al crear el usuario."}), 500

    # return render_template('mod/mAdmcreusr.html')

            # Simulación de éxito en la creación del usuario
            return jsonify({"status": "success", "message": "USUARIO CREADO CON EXITO"})
        except Exception as e:
            print(f"Error al crear el usuario: {str(e)}")
            return jsonify({"status": "error", "message": "Error al crear el usuario."}), 500

    return render_template('mod/mAdmcreusr.html')

# opcion 2
# @app.route('/mod/mAdmcreusr', methods=['GET', 'POST'])
# def crear_usuario():
#     id_usuario = session.get('id_usuario', '').strip().lower()

#     if request.method == 'POST':
#         # Obtener los valores del formulario y verificarlos
#         form_data = {key: request.form.get(key, '').strip() for key in
#                      ['id_clt', 'rut_usr', 'dv_usr', 'nomb_usr', 'ape_pat_usr', 'ape_mat_usr',
#                       'ema_usr', 'cel_usr', 'id_tda', 'id_prf', 'pwd']}

#         # Muestra los datos recibidos en la consola
#         print("Datos recibidos del formulario:", form_data)

#         # Verifica que todos los campos necesarios estén completos
#         if not all(form_data.values()):
#             # En caso de error, recarga la página con un mensaje flash
#             flash('Por favor, complete todos los campos requeridos.', 'error')
#             return render_template('mod/mAdmcreusr.html'), 400

#         try:
#             with get_db_connection() as conn:
#                 with conn.cursor() as cur:
#                     # Llamar a la función crea_usuario en la base de datos
#                     cur.execute("""
#                         SELECT crea_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#                     """, (
#                         form_data['id_clt'], form_data['rut_usr'], form_data['dv_usr'], form_data['nomb_usr'],
#                         form_data['ape_pat_usr'], form_data['ape_mat_usr'], form_data['ema_usr'],
#                         form_data['cel_usr'], form_data['id_tda'], form_data['id_prf'], form_data['pwd'],
#                         id_usuario
#                     ))
#                     respuesta = cur.fetchone()[0]

#             # Manejo de respuesta desde la base de datos
#             if respuesta.startswith('OK'):
#                 flash(respuesta.split(';')[1], 'success')
#                 return redirect(url_for('mAdmcreusr'))
#             else:
#                 flash(respuesta.split(';')[1], 'error')
#                 return render_template('mod/mAdmcreusr.html'), 400

#         except Exception as e:
#             print(f"Error al crear el usuario: {str(e)}")
#             flash('Error al crear el usuario.', 'error')
#             return render_template('mod/mAdmcreusr.html'), 500

#     return render_template('mod/mAdmcreusr.html')
# opcion 1
# @app.route('/mod/mAdmcreusr', methods=['GET', 'POST'])
# def crear_usuario():
#     id_usuario = session.get('id_usuario', '').strip().lower()

#     if request.method == 'POST':
#         # Obtener los valores del formulario
#         id_clt = request.form.get('id_clt')
#         rut_usr = request.form.get('rut_usr')
#         dv_usr = request.form.get('dv_usr')
#         nomb_usr = request.form.get('nomb_usr')
#         ape_pat_usr = request.form.get('ape_pat_usr')
#         ape_mat_usr = request.form.get('ape_mat_usr')
#         ema_usr = request.form.get('ema_usr').lower()
#         cel_usr = request.form.get('cel_usr')
#         id_tda = request.form.get('id_tda')
#         id_prf = request.form.get('id_prf')
#         pwd = request.form.get('pwd')

#         # Verificar que los campos requeridos estén completos
#         if not (rut_usr and dv_usr and nomb_usr and ape_pat_usr and ape_mat_usr and ema_usr and cel_usr and pwd and id_clt and id_tda and id_prf):
#             flash('Por favor, complete todos los campos requeridos.', 'error')
#             return render_template('mod/mAdmcreusr.html')

#         print(
#             f"Parámetros enviados: {id_clt}, {rut_usr}, {dv_usr}, {nomb_usr}, {ape_pat_usr}, {ape_mat_usr}, {ema_usr}, {cel_usr}, {id_tda}, {id_prf}, {pwd}, {id_usuario}")

#         try:
#             with get_db_connection() as conn:
#                 with conn.cursor() as cur:
#                     # Llamar a la función crea_usuario en la base de datos
#                     cur.execute("""
#                         SELECT crea_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#                     """, (
#                         id_clt,
#                         rut_usr,
#                         dv_usr,
#                         nomb_usr,
#                         ape_pat_usr,
#                         ape_mat_usr,
#                         ema_usr,
#                         cel_usr,
#                         id_tda,
#                         id_prf,
#                         pwd,
#                         id_usuario  # usr_cre será el usuario que está creando el nuevo usuario
#                     ))

#                     respuesta = cur.fetchone()[0]
#                     print(f"Respuesta de la función SQL: {respuesta}")

#             # Validar la respuesta de la función SQL
#             if respuesta.startswith('OK'):
#                 flash(respuesta.split(';')[1], 'success')
#                 return redirect(url_for('mAdmcreusr'))
#             else:
#                 flash(respuesta.split(';')[1], 'error')
#                 return render_template('mod/mAdmcreusr.html')

#         except Exception as e:
#             print(f"Error al crear el usuario: {str(e)}")
#             flash(f"Error al crear el usuario: {str(e)}", 'error')
#             return render_template('mod/mAdmcreusr.html')

#     return render_template('mod/mAdmcreusr.html')


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


@app.route('/logout')
def logout():
    id_cliente = session.get('ID_CLIENTE')
    id_usuario = session.get('id_usuario')

    # Registrar el evento de cierre de sesión
    registrar_evento(
        id_cliente=ID_CLIENTE,
        id_usuario=id_usuario,
        modulo_accedido="logout",
        accion="Cierre de sesión"
    )

    session.clear()
    return redirect(url_for('login'))

# Rutas


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


@ app.route('/mod/dashboard2')
def dashboard2():
    return render_template('mod/dashboard2.html')


@app.route('/dev')
def dev():
    id_usuario = session.get(
        'id_usuario', 'Usuario no definido')  # Valor por defecto
    return render_template('dev.html', id_usuario=id_usuario)


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
