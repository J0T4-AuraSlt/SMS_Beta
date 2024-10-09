from flask import Blueprint, render_template, session, redirect, url_for
from db_config import get_db_connection
import json

modules_bp = Blueprint('modules', __name__, url_prefix='/mod')


@modules_bp.route('/mAdmcreusr')
def mAdmcreusr():
    return render_template('mod/mAdmcreusr.html')

# Define las demás rutas de módulos aquí
