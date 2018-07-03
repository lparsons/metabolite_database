import re
from metabolite_database import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property

valid_atoms = {
    'e': 0.00054857990943,
    'C': 12.00000000,
    'H': 1.00782503224,
    'N': 14.0030740052,
    'O': 15.9949146221,
    'P': 30.97376151}


class Compound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    molecular_formula = db.Column(db.String(128), index=True)
    external_databases = db.relationship('DbXref', back_populates="compound")
    retention_times = db.relationship('RetentionTime',
                                      backref="compound")

    def is_formula_valid(self):
        formula = self.molecular_formula
        if formula == '' or formula is None:
            return False, formula
        for atom in valid_atoms.keys():
            formula = re.sub(r'{}[\d]*'.format(atom), '', formula)
        if formula != '':
            return False, formula
        else:
            return True, ''

    @hybrid_property
    def monoisotopic_mass(self):
        mass = None
        # print(self.is_formula_valid())
        if self.is_formula_valid()[0]:
            # print(self.molecular_formula)
            mass = 0.0
            for atom in valid_atoms.keys():
                num_atom = 0
                m = re.match(r'.*{}(\d*).*'.format(atom),
                             self.molecular_formula)
                if m:
                    # print("Num {} atoms: {}".format(atom, m.group(1)))
                    try:
                        num_atom = int(m.group(1))
                    except ValueError:
                        num_atom = 1
                # print("weight = {} + ({} * {})".format(
                #       mass, valid_atoms[atom], num_atom))
                mass += num_atom * valid_atoms[atom]
        return mass

    def m_z(self, mode):
        m_z = None
        if (self.monoisotopic_mass):
            try:
                m_z = (self.monoisotopic_mass
                       + ((valid_atoms['H'] - valid_atoms['e']) * mode))
            except (AttributeError, TypeError):
                raise AssertionError("mode must be integer")
        return m_z

    def __repr__(self):
        return '<Compound {}>'.format(self.name)


class DbXref(db.Model):
    __tablename__ = 'dbxref'
    # id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'),
                            primary_key=True)
    external_database_id = db.Column(db.Integer,
                                     db.ForeignKey('external_database.id'),
                                     primary_key=True)
    external_compound_id = db.Column(db.String(128))
    compound = db.relationship("Compound", back_populates="external_databases")
    external_database = db.relationship("ExternalDatabase",
                                        back_populates="compounds")

    def __repr__(self):
        return '<DbXref {}>'.format(self.id)


class ExternalDatabase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    url = db.Column(db.String(256))
    compound_url = db.Column(db.String(256))
    compounds = db.relationship('DbXref', back_populates="external_database")

    def __repr__(self):
        return '<ExternalDatabase {}>'.format(self.name)


class ChromatographyMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.Text)
    standard_runs = db.relationship('StandardRun',
                                    backref='chromatography_method')

    def compounds_with_retention_times(self):
        return db.session.query(Compound, RetentionTime).join(
            RetentionTime).join(
                StandardRun).filter(
                    StandardRun.chromatography_method_id == self.id)

    def compounds_with_valid_retention_times(self):
        return db.session.query(Compound, RetentionTime).join(
            RetentionTime).join(
                StandardRun).filter(
                    StandardRun.chromatography_method_id == self.id).filter(
                        RetentionTime.retention_time.isnot(None))

    def __repr__(self):
        return '<ChromatographyMethod {}>'.format(self.name)


class RetentionTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(
        db.Integer,
        db.ForeignKey('compound.id'))
    standard_run_id = db.Column(db.Integer, db.ForeignKey('standard_run.id'))
    retention_time = db.Column(db.Float)

    def __repr__(self):
        return '<RetentionTime {}>'.format(self.retention_time)


class StandardRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    operator = db.Column(db.String(256), index=True)
    mzxml_file = db.Column(db.String(256), index=True)
    chromatography_method_id = db.Column(
        db.Integer, db.ForeignKey('chromatography_method.id'))
    retention_times = db.relationship('RetentionTime',
                                      backref='standard_run')

    def __repr__(self):
        return '<StandardRun for {} by {} at {}>'.format(
            self.chromatography_method, self.operator, self.date)


def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.flush()
            return created, True
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), False

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), index=True, unique=True)
#     email = db.Column(db.String(120), index=True, unique=True)
#     password_hash = db.Column(db.String(128))
#
#     def __repr__(self):
#         return '<User {}>'.format(self.username)
