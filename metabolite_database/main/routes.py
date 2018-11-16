from flask import render_template
from flask import make_response
from flask import current_app
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import StandardRun
from metabolite_database.main import bp
from metabolite_database.main.forms import RetentionTimesForm
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
    return render_template('main/compounds.html',
                           title="Compound list", compounds=compounds)


@bp.route('/compound/<id>')
def compound(id):
    compound = Compound.query.filter_by(id=id).first_or_404()
    return render_template('main/compound.html',
                           title=compound.name, compound=compound)


@bp.route('/methods')
def methods():
    methods = ChromatographyMethod.query.all()
    return render_template('main/methods.html',
                           title="Chromatography Methods", methods=methods)


@bp.route('/method/<id>', methods=['GET', 'POST'])
def method(id):
    method = ChromatographyMethod.query.filter_by(id=id).first_or_404()
    total_compounds = Compound.query.count()
    selectform = RetentionTimesForm()
    selectform.standardruns.choices = [(r.id, "{} by {}"
                                        .format(r.date, r.operator))
                                       for r in method.standard_runs]
    retention_times = None
    if selectform.validate_on_submit():
        retention_times = method.retention_time_means(
            standard_run_ids=selectform.standardruns.data)
        if selectform.export.data:
            current_app.logger.debug("Export form submitted")
            current_app.logger.debug("compound list data: {}".format(
                selectform.compoundlist.data))
            current_app.logger.debug("standard run list data: {}".format(
                selectform.standardruns.data))
            si = io.StringIO()
            cw = csv.writer(si)
            for compound, mean_rt in retention_times:
                cw.writerow((compound.name, compound.molecular_formula,
                             mean_rt))
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = (
                "attachment; filename={}.csv".format(method.name))
            output.headers["Content-type"] = "text/csv"
            return output
        elif selectform.submit.data:
            current_app.logger.debug("Select form submitted")
    return render_template(
        'main/method.html',
        title="{} method".format(method.name),
        method=method,
        total_compounds=total_compounds,
        selectform=selectform,
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
    return render_template('main/standard_runs.html',
                           title="Standard runs", runs=runs)


@bp.route('/standard_run/<id>')
@bp.route('/standardrun/<id>')
@bp.route('/standard-run/<id>')
def standard_run(id):
    run = StandardRun.query.filter_by(id=id).first_or_404()
    # TODO Fix date represntation (how to use moment for format?)
    return render_template('main/standard_run.html',
                           title="Standard run: {}".format(run.date), run=run)
