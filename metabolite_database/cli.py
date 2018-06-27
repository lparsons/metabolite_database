import click
import csv
from dateutil.parser import parse
from metabolite_database import db
from metabolite_database.models import get_one_or_create
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import StandardRun
from metabolite_database.models import RetentionTime


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
            date=datep, operator=operator)
        if created:
            sr.chromatography_method = m
            print("Created new Standard Run: {}".format(sr))
        else:
            if sr.chromatography_method != m:
                exit("Error: Stanard Run already exists for different method: "
                     "{}".format(sr.chromatography_method))
        db.session.add_all([m, sr])
        with open(csvfile) as csvfh:
            csvreader = csv.DictReader(csvfh)
            c_created = 0
            rt_created = 0
            for row in csvreader:
                # print("Name: {}".format(row["Name"]))
                c, created = get_one_or_create(
                    session=db.session, model=Compound, name=row['Name'])
                if created:
                    c.molecular_formula = row['Formula']
                    c.molecular_weight = 0
                    c_created += 1
                else:
                    if c.molecular_formula != row['Formula']:
                        exit("Error: Compound {} already exists with "
                             "different formula.\n"
                             "   Existing: {} - {}\n"
                             "   New: {} - {}"
                             .format(c, c.name, c.molecular_formula,
                                     row['Name'], row['Formula']))
                rt, created = get_one_or_create(
                    session=db.session, model=RetentionTime,
                    compound_id=c.id, standard_run_id=sr.id)
                if created:
                    if row['RT'] != '':
                        try:
                            rt_value = float(row['RT'])
                            rt.retention_time = rt_value
                            c.retention_times.append(rt)
                            rt_created += 1
                        except ValueError:
                            print("Unable to parse retention time: {}"
                                  .format(row['RT']))
                db.session.add_all([c, rt])

            print("Created {} new Compounds".format(c_created))
            print("Recorded {} new Retention Times".format(rt_created))
            db.session.commit()
