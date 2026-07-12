from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.extensions import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.email.data) | (User.phone == form.email.data)
        ).first()

        if user and user.check_password(form.password.data):
            if user.status != 'Active':
                flash('Your account is inactive. Please contact administrator.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'Administrator':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'Staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('customer.search_bus'))
        else:
            flash('Invalid email/phone or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check existing
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(phone=form.phone.data).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            role='Customer',
            address=form.address.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Password reset link has been sent to your email (simulated).', 'info')
        else:
            flash('If the email exists, a reset link will be sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)
