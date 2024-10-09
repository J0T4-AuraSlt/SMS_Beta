from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db_config import get_db_connection
import json

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    # Tu lógica de login aquí
    pass


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))
