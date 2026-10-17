from flask import Blueprint, render_template
from flask_login import login_required
from models import db, Control, Evaluacion, ResultadoControl
from utils import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/reset-db')
@admin_required
def reset_db():
    try:
        db.session.query(ResultadoControl).delete()
        db.session.query(Evaluacion).delete()
        db.session.query(Control).delete()
        db.session.commit()
        return "Base de datos reseteada."
    except Exception as e:
        db.session.rollback()
        return f"Error al resetear: {e}"


@admin_bp.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403
