from flask import render_template
from flask import make_response
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import StandardRun
from metabolite_database.main import bp
import io
import csv


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
    compound = Compound.query.filter_by(id=id).first_or_404()
    return render_template('main/compound.html', compound=compound)


@bp.route('/methods')
def methods():
    methods = ChromatographyMethod.query.all()
    return render_template('main/methods.html', methods=methods)


@bp.route('/method/<id>')
def method(id):
    method = ChromatographyMethod.query.filter_by(id=id).first_or_404()
    total_compounds = Compound.query.count()
    retention_times = method.retention_time_means()
    return render_template(
        'main/method.html',
        method=method,
        total_compounds=total_compounds,
        retention_times=retention_times)


@bp.route('/compound_database/method/<id>')
def compound_database(id):
    method = ChromatographyMethod.query.filter_by(id=id).first_or_404()
    results = method.compounds_with_retention_times()
    si = io.StringIO()
    cw = csv.writer(si)
    for compound, rt in results:
        cw.writerow((compound.name, compound.molecular_formula,
                     rt.retention_time))
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        "attachment; filename={}.csv".format(method.name))
    output.headers["Content-type"] = "text/csv"
    return output


@bp.route('/standard_runs')
@bp.route('/standardruns')
@bp.route('/standard-runs')
def standard_runs():
    runs = StandardRun.query.all()
    return render_template('main/standard_runs.html', runs=runs)


@bp.route('/standard_run/<id>')
@bp.route('/standardrun/<id>')
@bp.route('/standard-run/<id>')
def standard_run(id):
    run = StandardRun.query.filter_by(id=id).first_or_404()
    return render_template('main/standard_run.html', run=run)
