from flask import render_template
from metabolite_database import db
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import RetentionTime
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
    compound = Compound.query.filter(Compound.id == id).first_or_404()
    return render_template('main/compound.html', compound=compound)


@bp.route('/methods')
def methods():
    methods = ChromatographyMethod.query.all()
    return render_template('main/methods.html', methods=methods)


@bp.route('/retention_times/<method>')
@bp.route('/retention-times/<method>')
@bp.route('/retentiontimes/<method>')
def retention_times(method):
    method = ChromatographyMethod.query.filter(
        ChromatographyMethod.name == method).first_or_404()
    results = db.session.query(Compound, RetentionTime).\
        join(RetentionTime).\
        filter(RetentionTime.chromatography_method.has(name=method.name))
    return render_template('main/retention_times.html', method=method,
                           results=results)
