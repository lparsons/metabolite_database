import click
import csv
import sys
from dateutil.parser import parse
from metabolite_database import db
from metabolite_database.models import get_one_or_create
from metabolite_database.models import Compound
from metabolite_database.models import CompoundList
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import StandardRun
from metabolite_database.models import RetentionTime
from sqlalchemy.orm.exc import NoResultFound


def register(app):
    @app.cli.command()
    @click.argument('csvfile')
    @click.argument('method')
    @click.argument('date')
    @click.argument('operator')
    @click.option('-d', '--method-description', default=None)
    def import_csv(csvfile, method, date, operator, method_description=None):
        """Import retention times from CSV file"""
        print("Importing records from '{}'".format(csvfile))
        datep = parse(date)
        m, created = get_one_or_create(
            session=db.session, model=ChromatographyMethod, name=method)
        if created:
            print("Created new method: {}".format(m))
        sr, created = get_one_or_create(
            session=db.session, model=StandardRun,
            date=datep, operator=operator, chromatography_method=m)
        if created:
            sr.chromatography_method = m
            if method_description:
                m.description = method_description
            print("Created new Standard Run: {}".format(sr))
        else:
            exit("Error: Standard Run with same operator and date already "
                 "exists for this chromatography method.")
        db.session.add_all([m, sr])
        with open(csvfile) as csvfh:
            csvreader = csv.DictReader(csvfh)
            c_created = 0
            rt_created = 0
            bad_compounds = []
            bad_retention_times = []
            for row in csvreader:
                name = row["Name"].strip()
                formula = row["Formula"].strip()
                rt_string = row["RT"].strip()
                try:
                    c = Compound.query.filter_by(name=name).one()
                    assert (c.molecular_formula == formula)
                except NoResultFound:
                    try:
                        c, created = get_one_or_create(
                            session=db.session, model=Compound,
                            name=name,
                            molecular_formula=formula)
                        if created:
                            c_created += 1
                            db.session.add(c)
                    except AssertionError as e:
                        sys.stderr.write(
                            "Error: Unable to record compound {} {}: {}\n"
                            .format(name, formula, e))
                        bad_compounds.append(row)
                        next
                except AssertionError as e:
                    sys.stderr.write(
                        "Error: Compound {} already exists with different "
                        "formula.\n"
                        "   Existing: {} - {}\n"
                        "   New: {} - {}\n"
                        .format(c, c.name, c.molecular_formula, name,
                                formula))
                    bad_compounds.append(row)
                try:
                    rt_value = float(rt_string)
                    rt, created = get_one_or_create(
                        session=db.session, model=RetentionTime,
                        compound_id=c.id, standard_run_id=sr.id)
                    if created:
                        rt.retention_time = rt_value
                        c.retention_times.append(rt)
                        db.session.add_all([c, rt])
                        rt_created += 1
                    else:
                        sys.stderr.write(
                            "Retention time for this compound {} and standard "
                            "run already exists\n".format(c))
                        bad_retention_times.append(row)
                except ValueError:
                        sys.stderr.write("Unable to parse retention "
                                         "time '{}' for {}\n"
                                         .format(rt_string, c))
                        bad_retention_times.append(row)
                except AssertionError as e:
                    sys.stderr.write("Unable to record retetion time '{}': "
                                     "{}\n".format(rt_string, e))
                    bad_retention_times.append(row)

            print("Created {} new Compounds".format(c_created))
            print("Recorded {} new Retention Times".format(rt_created))
            print("\nRows with invalid compounds:")
            writer = csv.DictWriter(sys.stdout, fieldnames=row.keys())
            for row in bad_compounds:
                writer.writerow(row)
            print("\nRows with invalid retention times:")
            for row in bad_retention_times:
                writer.writerow(row)
            db.session.commit()

    @app.cli.command()
    @click.argument('csvfile')
    @click.argument('name')
    @click.option('-d', '--description', default=None)
    def add_compound_list(csvfile, name, description):
        """Create new compound list from CSV file"""
        list, created = get_one_or_create(
            session=db.session, model=CompoundList, name=name,
            description=description)
        if created:
            print("Created new compound list: {}".format(list))
        else:
            exit("Error: compound list already exists with name: {}"
                 .format(list.name))
        db.session.add(list)
        print("Importing list of compounds from '{}'".format(csvfile))
        with open(csvfile) as csvfh:
            csvreader = csv.reader(csvfh)
            compounds_added = 0
            compounds_not_found = []
            for row in csvreader:
                value = row[0]
                id = None
                compound = None
                try:
                    id = int(value)
                    compound = Compound.query.get(id)
                except ValueError:
                    pass
                if not compound:
                    try:
                        compound = Compound.query.filter_by(name=value).one()
                    except NoResultFound:
                        pass
                if not compound:
                    try:
                        compound = Compound.query.filter_by(
                            molecular_formula=value).one()
                    except NoResultFound:
                        pass
                if not compound:
                    compounds_not_found.append(value)
                    sys.stderr.write("Unable to find compound: {}\n"
                                     .format(value))
                else:
                    print(compound)
                    list.compounds.append(compound)
                    compounds_added += 1
        db.session.add(list)
        print("Added {} new compounds to compound list {}"
              .format(compounds_added, list.name))
        print("Unable to find {} compounds in file".format(
            len(compounds_not_found)))
        db.session.commit()
