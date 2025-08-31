from flask import Blueprint, render_template
from src.database import get_ip_history, get_current_ip

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    current_ip = get_current_ip()
    return render_template('index.html', current_ip=current_ip)

@bp.route('/history')
def history():
    ip_history = get_ip_history()
    return render_template('history.html', ip_history=ip_history)