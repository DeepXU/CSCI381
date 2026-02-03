import psycopg
from psycopg.rows import dict_row

def get_db():
    return psycopg.connect(
        "dbname=scoring user=scoring_user password=scoring_pass host=127.0.0.1",
        row_factory=dict_row
    )

