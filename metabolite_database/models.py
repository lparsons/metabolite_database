from metabolite_database import db


class Compound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    molecular_formula = db.Column(db.String(128), index=True)
    molecular_weight = db.Column(db.Float, index=True)
    external_databases = db.relationship('DbXref', back_populates="compound")
    retention_times = db.relationship('RetentionTime',
                                      back_populates="compound")

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
    retention_times = db.relationship('RetentionTime',
                                      back_populates="chromatography_method")

    def __repr__(self):
        return '<ChromatographyMethod {}>'.format(self.name)


class RetentionTime(db.Model):
    chromatography_method_id = db.Column(
        db.Integer,
        db.ForeignKey('chromatography_method.id'),
        primary_key=True)
    compound_id = db.Column(
        db.Integer,
        db.ForeignKey('compound.id'),
        primary_key=True)
    retention_time = db.Column(db.Float)
    compound = db.relationship(
        "Compound", back_populates="retention_times", viewonly=True)
    chromatography_method = db.relationship(
        "ChromatographyMethod", back_populates="retention_times",
        viewonly=True)

    def __repr__(self):
        return '<RetentionTime {}>'.format(self.retention_time)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), index=True, unique=True)
#     email = db.Column(db.String(120), index=True, unique=True)
#     password_hash = db.Column(db.String(128))
#
#     def __repr__(self):
#         return '<User {}>'.format(self.username)
