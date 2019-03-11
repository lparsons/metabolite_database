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
        c = Compound(name="Aconitate", molecular_formula="C6H6O6")
        cm = ChromatographyMethod(name="Test Method")
        rt = RetentionTime(retention_time=5.00)
        sr = StandardRun(date=datetime.utcnow(), operator="Lance")
        rt.standard_run = sr
        c.retention_times.append(rt)
        sr.chromatography_method = cm

        sr2 = StandardRun(date=datetime.utcnow(), operator="Lance 2")
        rt2 = RetentionTime(retention_time=7.00)
        rt2.standard_run = sr2
        c.retention_times.append(rt2)
        sr2.chromatography_method = cm

        db.session.add_all([c, cm, rt, sr, rt2, sr2])
        db.session.add(c)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_compound(self):
        c = Compound.query.get(1)
        self.assertEqual(c.name, "Aconitate")
        self.assertEqual(c.molecular_formula, "C6H6O6")
        self.assertEqual(c.monoisotopic_mass, 174.01643792604)
        self.assertEqual(c.m_z(-1), 173.00916147370944)
        self.assertEqual(c.m_z(1), 175.02371437837056)

    def test_name_standardization_caps(self):
        c = Compound.query.get(1)
        self.assertEqual(c.name, 'Aconitate')
        self.assertEqual(c.standardized_name, 'aconitate')

    def test_name_standardization_spaces(self):
        name = "AconiTate -5"
        standardized_name = "aconitate-5"
        c = Compound(name=name,
                     molecular_formula="C6H6O6")
        db.session.add(c)
        db.session.commit()
        self.assertEqual(c.name, name)
        self.assertEqual(c.standardized_name, standardized_name)

    def test_invalid_formula(self):
        with self.assertRaises(AssertionError):
            Compound(name="Invalid compound", molecular_formula="C6Z6O6")

    def test_retention_time_single(self):
        c = Compound.query.get(1)
        cm = ChromatographyMethod.query.get(1)
        res = cm.retention_time_means(standard_run_ids=[1])
        res_list = list(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0], (c, 5.00))

    def test_retention_time_mean(self):
        c = Compound.query.get(1)
        cm = ChromatographyMethod.query.get(1)
        res = cm.retention_time_means()
        res_list = list(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0], (c, 6.00))


if __name__ == '__main__':
    unittest.main(verbosity=2)
