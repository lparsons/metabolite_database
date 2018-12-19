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
    def import_csv(csvfile, method, date, operator):
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
            print("Created new Standard Run: {}".format(sr))
        else:
            exit("Error: Standard Run with same operator and date already "
                 "exists for this chromatography method.")
        db.session.add_all([m, sr])
        with open(csvfile) as csvfh:
            csvreader = csv.DictReader(csvfh)
            c_created = 0
            rt_created = 0
            failed_rows = []
            for row in csvreader:
                # print("Name: {}".format(row["Name"]))
                try:
                    c, created = get_one_or_create(
                        session=db.session, model=Compound, name=row['Name'],
                        molecular_formula=row['Formula'])
                    if created:
                        c_created += 1
                    else:
                        if c.molecular_formula != row['Formula']:
                            sys.stderr.write(
                                "Error: Compound {} already exists with "
                                "different formula.\n"
                                "   Existing: {} - {}\n"
                                "   New: {} - {}\n"
                                .format(c, c.name, c.molecular_formula,
                                        row['Name'], row['Formula']))
                except AssertionError as e:
                    sys.stderr.write("Unable to create compound '{}': {}\n"
                                     .format(row['Name'], e))
                    failed_rows.append(row)
                try:
                    rt_value = float(row['RT'])
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
                            "Retention time for this compound and standard "
                            "run already exists")
                        failed_rows.append(row)
                except ValueError:
                        sys.stderr.write("Unable to parse retention "
                                         "time '{}' for {}\n"
                                         .format(row['RT'], c))
                        failed_rows.append(row)
                except AssertionError as e:
                    sys.stderr.write("Unable to record retetion time '{}': "
                                     "{}\n".format(row['RT'], e))

            print("Created {} new Compounds".format(c_created))
            print("Recorded {} new Retention Times".format(rt_created))
            print("Invalid rows:")
            writer = csv.DictWriter(sys.stderr, fieldnames=row.keys())
            for row in failed_rows:
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
