import re
from metabolite_database import db
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import label, func
from flask import current_app

valid_atoms = {
    'e': 0.00054857990943,
    'C': 12.00000000,
    'H': 1.00782503224,
    'I': 126.904457,
    'N': 14.0030740052,
    'O': 15.9949146221,
    'P': 30.97376151,
    'S': 31.972072}


compoundlists = db.Table(
    'compoundlists',
    db.Column('compound_id', db.Integer,
              db.ForeignKey('compound.id'), primary_key=True),
    db.Column('compound_list_id', db.Integer,
              db.ForeignKey('compound_list.id'), primary_key=True))


def standardize_compound_name(name):
    '''Return a standardized version of a compound name'''
    return name.lower()


def standardized_compound_name_default(context):
    return standardize_compound_name(context.get_current_parameters()['name'])


class CompoundList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    description = db.Column(db.Text)
    compounds = db.relationship('Compound', secondary=compoundlists,
                                back_populates="compound_lists")


class Compound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    standardized_name = db.Column(db.String(256), index=True, unique=True,
                                  default=standardized_compound_name_default,
                                  onupdate=standardized_compound_name_default)
    name = db.Column(db.String(256), index=True, unique=True, nullable=False)
    molecular_formula = db.Column(db.String(128), index=True, nullable=False)
    notes = db.Column(db.Text)
    external_databases = db.relationship('DbXref', back_populates="compound")
    retention_times = db.relationship('RetentionTime', backref="compound")
    compound_lists = db.relationship('CompoundList', secondary=compoundlists,
                                     back_populates="compounds")

    @validates('molecular_formula')
    def is_formula_valid(self, key, formula):
        if formula == '' or formula is None:
            raise AssertionError("Molecular formula must not be blank")
        check_formula = formula
        for atom in valid_atoms.keys():
            check_formula = re.sub(r'{}[\d]*'.format(atom), '', check_formula)
        if check_formula != '':
            raise AssertionError("Invalid formula specified: '{}' not "
                                 "recognized".format(check_formula))
        return formula

    @hybrid_property
    def monoisotopic_mass(self):
        mass = None
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
    name = db.Column(db.String(256), unique=True, nullable=False)
    url = db.Column(db.String(256))
    compound_url = db.Column(db.String(256))
    compounds = db.relationship('DbXref', back_populates="external_database")

    def __repr__(self):
        return '<ExternalDatabase {}>'.format(self.name)


class ChromatographyMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    standard_runs = db.relationship('StandardRun',
                                    backref='chromatography_method')

    def retention_time_means(self, standard_run_ids=None,
                             compound_list_id=None):
        '''
        Return list of compounds and retention time means for specified runs
        '''
        subq = (db.session.query(RetentionTime).join(StandardRun)
                .filter(StandardRun.chromatography_method_id == self.id))
        if standard_run_ids:
            subq = subq.filter(StandardRun.id.in_(standard_run_ids))
        subq = subq.subquery()
        query = (db.session.query(
            Compound, label('mean_rt', func.avg(subq.c.retention_time)))
            .outerjoin(subq)
            .group_by(Compound.id))
        if compound_list_id:
            query = query.join(CompoundList, Compound.compound_lists)\
                .filter(CompoundList.id == compound_list_id)
        current_app.logger.debug(query)
        return query.all()

    def compounds_with_retention_times(self, standard_run_ids=None):
        query = db.session.query(Compound.id).\
            join(RetentionTime).\
            join(StandardRun).\
            filter(StandardRun.chromatography_method_id == self.id).\
            filter(RetentionTime.retention_time.isnot(None))
        if standard_run_ids:
            query = query.filter(StandardRun.id.in_(standard_run_ids))
        return query

    def unique_compounds_with_retention_times(self, standard_run_ids=None):
        query = self.compounds_with_retention_times(standard_run_ids)
        query = query.distinct(Compound.id)
        current_app.logger.debug(query)
        return query

    def __repr__(self):
        return '<ChromatographyMethod {}>'.format(self.name)


class RetentionTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(
        db.Integer,
        db.ForeignKey('compound.id'),
        nullable=False)
    standard_run_id = db.Column(db.Integer, db.ForeignKey('standard_run.id'))
    retention_time = db.Column(db.Float)

    def __repr__(self):
        return '<RetentionTime {}>'.format(self.retention_time)


class StandardRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, index=True, nullable=False)
    operator = db.Column(db.String(256), index=True, nullable=False)
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
    if (model == Compound and 'standardized_name' not in kwargs):
        name = kwargs.pop('name', None)
        kwargs['standardized_name'] = standardize_compound_name(name)
        if create_method_kwargs:
            create_method_kwargs['name'] = name
        else:
            create_method_kwargs = {'name': name}
        return get_one_or_create(session, model, create_method,
                                 create_method_kwargs, **kwargs)
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
