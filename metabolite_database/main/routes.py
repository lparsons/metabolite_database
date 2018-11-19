from flask import (render_template, make_response, current_app, redirect,
                   url_for)
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
    return redirect(url_for('main.methods'))


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
    compound_lists = [("All", "All ({} compounds)".format(
        Compound.query.count()))]
    standard_runs = [
        (r.id, "Run on {:%Y-%m-%d} by {} ({} retention times)".format(
            r.date, r.operator, len(r.retention_times)))
        for r in method.standard_runs]
    form = RetentionTimesForm(
        compoundlist="All",
        standardruns=[r.id for r in method.standard_runs])
    form.compoundlist.choices = compound_lists
    form.standardruns.choices = standard_runs
    retention_times = None
    if form.validate_on_submit():
        retention_times = method.retention_time_means(
            standard_run_ids=form.standardruns.data)
        if form.export.data:
            current_app.logger.debug("Export form submitted")
            current_app.logger.debug("compound list data: {}".format(
                form.compoundlist.data))
            current_app.logger.debug("standard run list data: {}".format(
                form.standardruns.data))
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
        elif form.submit.data:
            current_app.logger.debug("Select form submitted")
    if not form.standardruns.data:
        form.standardruns.process_data([r.id for r in method.standard_runs])
    return render_template(
        'main/method.html',
        title="{} method".format(method.name),
        method=method,
        form=form,
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
