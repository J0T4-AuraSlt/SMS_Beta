# Asegúrate de que 'app' sea el nombre de tu objeto Flask o Django
from app import app as application
import sys
import os

# Agregar la ruta al directorio donde está tu app.py
sys.path.insert(0, '/var/www/html')

# Importar la aplicación de tu archivo app.py

if __name__ == "__main__":
    application.run()
