from flask import Flask, redirect, url_for
from app_routes import auth, menu, modulos  # Importamos Blueprints
import logging
from others.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Registro de Blueprints
app.register_blueprint(auth.bp, url_prefix='/auth')
app.register_blueprint(menu.bp, url_prefix='/menu')
app.register_blueprint(modulos.bp, url_prefix='/mod')

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Redirigir la ruta raíz ("/") a la página de inicio de sesión en 'auth.index'


@app.route('/')
def home():
    return redirect(url_for('auth.index'))


if __name__ == '__main__':
    app.run(debug=True)
