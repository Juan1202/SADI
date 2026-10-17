from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('ACCESO DENEGADO: Su cuenta ha sido desactivada.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            return redirect(url_for('dashboard.home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('auth.login'))
