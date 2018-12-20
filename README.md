# Rabinowitz Lab Metabolite Database

Metabolite database used by the Rabinowitz Lab


## Setup

1.  Install [Miniconda](https://conda.io/miniconda.html).
2.  Create environment from the `environment.yml` file.
3.  Activate the environment.


## Configuration

1.  Copy `env.sample` to `.env` and edit as needed
2.  `export FLASK_APP=main.py`
3.  `export FLASK_ENV=development`
4.  Create the database: `flask db upgrade`
4.  Start the application: `flask run`


## Load Data

1.  Import knowns file(s) to create compounds and methods.
        ```
        flask import-csv CSVFILE METHOD DATE OPERATOR
        ```

2.  Import compound lists.
        ```
        flask add-compound-list CSVFILE LISTNAME
        ```


### Example of data loading

     ```
     flask import-csv data/Knowns-new-E-30min.csv "E-30min" "2018-05-02" "Lin Wang"
     flask import-csv data/Knowns-new-E-waters-25min.csv "E-waters-25min" "2018-05-02" "Lin Wang"
     flask import-csv data/Knowns-new-Hilic20min-QE.csv "Hilic-20min-QE" "2018-05-02" "Lin Wang"
     flask import-csv data/Knowns-new-Hilic25min-QE.csv "Hilic-25min-QE" "2018-05-02" "Lin Wang"
     flask import-csv data/Knowns-new-QTOF-Hilic30min.csv "Hilic-30min-QTOF" "2018-05-02" "Lin Wang"
     # flask import-csv data/Knowns-new-E-waters-25min-lparsons.csv "E-waters-25min" "2018-12-20" "Lance Parsons"
     # flask add-compound-list data/compound_list_lparsons.csv "Lance's Selected Compounds"
     flask import-csv data/rutgers_qe_plus_hilic_2018-05.csv "Rutgers QE PLUS HILIC" "2018-04-18" "Xiaoyang Su" --method-description "22min HILIC runs on Rutgers Q Exactive PLUS"
     ```
