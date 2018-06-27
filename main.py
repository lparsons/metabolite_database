from metabolite_database import create_app
from metabolite_database import db
from metabolite_database import cli
from metabolite_database.models import Compound
from metabolite_database.models import DbXref
from metabolite_database.models import ExternalDatabase
from metabolite_database.models import RetentionTime
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import StandardRun


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Compound': Compound, 'DbXref': DbXref,
            'ExternalDatabase': ExternalDatabase,
            'RetentionTime': RetentionTime,
            'ChromatographyMethod': ChromatographyMethod,
            'StandardRun': StandardRun}
