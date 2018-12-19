# Rabinowitz Lab Metabolite Database

Metabolite database used by the Rabinowitz Lab


# Setup

1.  Install [Miniconda](https://conda.io/miniconda.html).
2.  Create environment from the `environment.yml` file.
3.  Activate the environment.


# Configuration

1.  Copy `env.sample` to `.env` and edit as needed
2.  `export FLASK_APP=main.py`
3.  `export FLASK_ENV=development`
4.  Create the database: `flask db upgrade`
4.  Start the application: `flask run`


# Load Data

1.  Import knowns file(s) to create compounds and methods.
        ```
        flask import-csv CSVFILE METHOD DATE OPERATOR
        ```
