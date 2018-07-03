#!/usr/bin/env python
from datetime import datetime
import unittest
from config import Config
from metabolite_database import create_app
from metabolite_database import db
from metabolite_database.models import Compound
from metabolite_database.models import ChromatographyMethod
from metabolite_database.models import RetentionTime
from metabolite_database.models import StandardRun


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class CompoundModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_compound(self):
        c = Compound(name="aconitate",
                     molecular_formula="C6H6O6")
        self.assertEqual(c.name, "aconitate")
        self.assertEqual(c.molecular_formula, "C6H6O6")
        self.assertEqual(c.monoisotopic_mass, 174.01643792604)
        self.assertEqual(c.m_z(-1), 173.00916147370944)
        self.assertEqual(c.m_z(1), 175.02371437837056)

    def test_invalid_formula(self):
        with self.assertRaises(AssertionError):
            Compound(name="Invalid compound", molecular_formula="C6Z6O6")

    def test_retention_time(self):
        c = Compound(name="aconitate",
                     molecular_formula="C6H6O6")
        cm = ChromatographyMethod(name="Test Method")
        rt = RetentionTime(retention_time=5.25)
        sr = StandardRun(date=datetime.utcnow(), operator="Lance")
        c.retention_times.append(rt)
        rt.standard_run = sr
        sr.chromatography_method = cm
        db.session.add_all([c, cm, rt, sr])
        db.session.commit()
        res = cm.compounds_with_retention_times()
        res_list = list(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0], (c, rt))


if __name__ == '__main__':
    unittest.main(verbosity=2)
