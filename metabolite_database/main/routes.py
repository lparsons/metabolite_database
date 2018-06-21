from flask import render_template
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    user = {'username': 'Lance'}
    return render_template('main/index.html', title='Home', user=user)


@bp.route('/compounds')
def compounds():
    compounds = Compound.query.all()
    return render_template('main/compounds.html', compounds=compounds)


@bp.route('/compound/<id>')
def compound(id):
    compound = Compound.query.filter(id == id).first_or_404()
    return render_template('main/compound.html', compound=compound)


@bp.route('/methods')
def methods():
    methods = ChromatographyMethod.query.all()
    return render_template('main/methods.html', methods=methods)


@bp.route('/retention_times/method/<id>')
@bp.route('/retentiontimes/method/<id>')
@bp.route('/retention-times/method/<id>')
def retention_times_for_method(id):
    method = ChromatographyMethod.query.filter(id == id).first_or_404()
    results = method.compounds_with_retention_times()
    return render_template('main/retention_times_for_method.html',
                           method=method, results=results)
