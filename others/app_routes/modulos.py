from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

bp = Blueprint('modulos', __name__)


@bp.route('/mod/<module_name>')
def load_module(module_name):
    try:
        return render_template(f'mod/{module_name}.html')
    except TemplateNotFound:
        return render_template('404.html'), 404
