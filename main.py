from metabolite_database import app
from metabolite_database import db
from metabolite_database.models import Compound
from metabolite_database.models import DbXref
from metabolite_database.models import ExternalDatabase
from metabolite_database.models import RetentionTime
from metabolite_database.models import ChromatographyMethod


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Compound': Compound, 'DbXref': DbXref,
            'ExternalDatabase': ExternalDatabase,
            'RetentionTime': RetentionTime,
            'ChromatographyMethod': ChromatographyMethod}
