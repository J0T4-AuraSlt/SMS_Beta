from flask import Flask, request, render_template, url_for, flash, g, session, redirect
from db_config import get_db_connection
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesaria para usar sesiones
ID_CLIENTE = 4  # El ID del cliente será basada en la URL, relacionando URL=CLT
FECHA_HORA = datetime.now().strftime("%Y-%m-%d %H:%M")
# actualizacion login


@app.context_processor
def inject_user_data():
    ID_CLIENTE = session.get('ID_CLIENTE')
    id_usuario = session.get('id_usuario')
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
    return dict(ID_CLIENTE=ID_CLIENTE, id_usuario=id_usuario, fecha_hora=fecha_hora)


@app.route('/login', methods=['POST'])
def login():
    id_usuario = request.form['id_usuario']
    pwd = request.form['pwd']

    # Validar las credenciales de acceso
    validacion = valida_acceso(ID_CLIENTE, id_usuario, pwd)

    if validacion.startswith('OK'):
        # Almacenar en la sesión
        session['ID_CLIENTE'] = ID_CLIENTE
        session['id_usuario'] = id_usuario
        # Verifica que se almacenen correctamente
        print("ID_CLIENTE:", session['ID_CLIENTE'],
              "id_usuario:", session['id_usuario'])

        # Obtener el menú si la validación es exitosa
        menu_json = get_menu(ID_CLIENTE, id_usuario)

        # Estructurar el menú
        menu = []
        for item in menu_json:
            if item['tpo_nodo'] == 'PADRE':
                menu.append({
                    'path': item['path'],
                    'descripcion': item['descripcion'],
                    'hijos': []  # Inicializa la lista de hijos
                })
            elif item['tpo_nodo'] == 'HIJO':
                if menu:  # Asegúrate de que haya al menos un padre
                    menu[-1]['hijos'].append({
                        'path': item['path'],
                        'descripcion': item['descripcion']
                    })

        try:
            # Renderizar la plantilla 'menu.html' con el menú estructurado
            return render_template('menu.html', menu=menu, id_usuario=id_usuario, ID_CLIENTE=ID_CLIENTE, fecha_hora=FECHA_HORA)
        except BuildError as e:
            # Manejar el error y mostrar un mensaje amigable
            flash(f"Error al construir la URL: {str(e)}", "error")
            return render_template('menu.html', menu=menu, id_usuario=id_usuario, ID_CLIENTE=ID_CLIENTE, fecha_hora=FECHA_HORA)
    else:
        error = validacion.split(
            ';')[1] if ';' in validacion else "Credenciales incorrectas"
        return render_template('login.html', error=error)


def valida_acceso(ID_CLIENTE, id_usuario, pwd):
    id_usuario = id_usuario.lower()

    if len(id_usuario) < 5:
        return "ID Usuario debe tener al menos 5 caracteres"

    # Conectar a la base de datos
    conn = get_db_connection()
    cur = conn.cursor()

    # Ejecutar la función de validación en la base de datos
    cur.execute("SELECT public.valida_acceso(%s, %s, %s)",
                (ID_CLIENTE, id_usuario, pwd))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else "Credenciales incorrectas"

# Función para obtener el menú del usuario


def get_menu(ID_CLIENTE, id_usuario):
    conn = get_db_connection()
    cur = conn.cursor()

    # Ejecutar la consulta que llama a la función almacenada
    cur.execute("SELECT public.get_menu(%s, %s)", (ID_CLIENTE, id_usuario))

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result and result[0]:
        if isinstance(result[0], list):
            menu_json = result[0]
        else:
            try:
                menu_json = json.loads(result[0])
            except json.JSONDecodeError:
                return {"message": "Error al decodificar el menú desde el servidor."}

        if not menu_json:
            return {"message": "El menú no tiene información disponible."}

        return menu_json
    else:
        return {"message": "No se ha encontrado información para este usuario."}


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/menu')
def menu():
    ID_CLIENTE = session.get('ID_CLIENTE')
    id_usuario = session.get('id_usuario')

    # Verificar si hay sesión válida
    if not ID_CLIENTE or not id_usuario:
        print("Redireccionando a dev: falta ID_CLIENTE o id_usuario")
        return redirect(url_for('dev'))

    menu_json = get_menu(ID_CLIENTE, id_usuario)

    menu = []
    for item in menu_json:
        if item['tpo_nodo'] == 'PADRE':
            menu.append({
                'path': item['path'],
                'descripcion': item['descripcion'],
                'hijos': []
            })
        elif item['tpo_nodo'] == 'HIJO':
            if menu:
                menu[-1]['hijos'].append({
                    'path': item['path'],
                    'descripcion': item['descripcion']
                })

    valid_paths = [item['path'] for item in menu_json if item['tpo_nodo'] == 'PADRE'] + \
                  [item['path']
                      for item in menu_json if item['tpo_nodo'] == 'HIJO']

    # Verificar que el menú no esté vacío
    if not menu:
        print("Redireccionando a dev: menú vacío")
        return redirect(url_for('dev'))

    # Verificar que todos los paths sean válidos
    for item in menu:
        for hijo in item['hijos']:
            if hijo['path'] not in valid_paths:
                print("Redireccionando a dev: path inválido")
                return redirect(url_for('dev'))

    # Renderizar la plantilla del menú
    return render_template('menu.html', menu=menu, id_usuario=id_usuario, ID_CLIENTE=ID_CLIENTE,
                           fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           valid_paths=valid_paths)


# Nueva ruta para manejar las solicitudes AJAX
@app.route('/load_module/<path:modulo>')
def load_module(modulo):
    # Aquí puedes cargar el contenido del módulo solicitado
    # Para este ejemplo, simplemente se devolverá una plantilla con el nombre del módulo
    try:
        return render_template(f'{modulo}.html')
    except Exception as e:
        return f"Error al cargar el módulo: {str(e)}"

# Menu


# @app.route('/mPadminist')
# def mPadminist():
#    return render_template('mPadminist.html')

# modulos


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
    return render_template('dev.html')


if __name__ == '__main__':
    app.run(debug=True)
