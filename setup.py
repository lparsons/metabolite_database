from setuptools import setup

setup(
    name='metabolite_database',
    packages=['metabolite_database'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_wtf',
    ],
)
