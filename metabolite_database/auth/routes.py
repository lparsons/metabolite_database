from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from metabolite_database.auth.forms import LoginForm
from metabolite_database.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)
