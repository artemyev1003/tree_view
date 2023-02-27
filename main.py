import json
import re
import os
import psycopg2
import time
from psycopg2 import OperationalError
from functools import reduce


def create_connection(db_name, db_user, db_password, db_host, db_port):
    """Creates connection to the PostgreSQL database"""
    conn = None
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return conn


def execute_query(conn, query):
    """Executes SQL query for creating/populating a table """
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        print(f"Executing {query}")
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")


def execute_read_query(conn, query):
    """Executes SQL select read query"""
    cursor = conn.cursor()
    result = None
    try:
        print(f"Executing {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")


create_table = '''
CREATE TABLE IF NOT EXISTS employees (
id SERIAL PRIMARY KEY,
name VARCHAR(50),
position INT,
bossid INT);

INSERT INTO employees
VALUES (1, 'Дмитрий Иванов', 1, 0),
(2, 'Сергей Крылов', 2, 1),
(3, 'Иван Старшов', 2, 10),
(4, 'Руслан Ивлев', 3, 2),
(5, 'Ирина Кортнева', 3, 2),
(6, 'Елизавета Зайцева', 3, 8),
(7, 'Адрей Петров', 3, 9),
(8, 'Анна Миронова', 2, 10),
(9, 'Владимир Павлов', 2, 10),
(10, 'Константин Ли', 1, 0)
ON CONFLICT DO NOTHING;


CREATE TABLE IF NOT EXISTS positions (
id SERIAL PRIMARY KEY,
position VARCHAR(50));

INSERT INTO positions
VALUES (1, 'Региональный директор'),
(2, 'Территориальный менеджер'),
(3, 'Супервайзер')
ON CONFLICT DO NOTHING;


'''

get_employees_tree = """
WITH RECURSIVE tree_view AS (
    SELECT 
        id,
        name,
        position,
        bossid,
        0 AS level,
        CAST(id AS VARCHAR(50)) AS order_sequence
    FROM employees
    WHERE bossid = 0
    
    UNION ALL
    
    SELECT 
        boss.id,
        boss.name,
        boss.position, 
        boss.bossid,
        level + 1 AS level,
        CAST(order_sequence || '-' || CAST(boss.id AS VARCHAR(50)) AS VARCHAR(50)) AS order_sequence
        FROM employees boss
    JOIN tree_view tv
    ON boss.bossid = tv.id
)

SELECT tree_view.id, name, positions.position, level, order_sequence
FROM tree_view
JOIN positions
ON tree_view.position = positions.id
ORDER BY order_sequence;
"""


def employees_tree_to_cmd(query: list[tuple]):
    """Receives a list of tuples with company employees data and
    prints them to command line as a tree structure"""
    query = sorted(query, key=lambda l: l[4])
    for line in query:
        (_, name, position, level, order_sequence) = line
        print("\t" * level, f"{name}, {position.lower()}")
        time.sleep(1)


def employees_tree_to_html(query: list[tuple]):
    """Receives a list of tuples with company employees data and
    generates an HTML file showing them as a tree structure"""
    with open('data/tree.html', 'w') as f:
        print('<meta charset="UTF-8">', file=f)
        print('<ul>', file=f)
        for line in query:
            (_, name, position, level, _) = line
            print(f'<li style="margin-left:{2*level}em'
                  f'{";list-style-type:circle" if level > 0 else ""}">{name}, '
                  f'{position.lower()}</li>', file=f)
        print("</ul>", file=f)


def employees_tree_to_json(query: list[tuple]):
    """Receives a list of tuples with company employees data and
    generates an JSON file showing them as a tree structure"""
    result = {}
    for line in query:
        (employee_id, name, position, level, order_sequence) = line
        if level == 0:
            result[str(employee_id)] = {"name": name,
                                        "position": position.lower(),
                                        "subordinate": {}}
        else:
            order = re.split(r'(subordinate)', order_sequence.replace('-', 'subordinate'))
            reduce(dict.get, order[:-1], result)[order[-1]] = {"name": name,
                                                               "position": position.lower(),
                                                               "subordinate": {}}
    with open('data/tree.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    connection = create_connection(
        "EmployeeStructure", "postgres", "postgres", "db", "5432"
    )
    execute_query(connection, create_table)

    q = execute_read_query(connection, get_employees_tree)

    if not os.path.exists('data'):
        os.mkdir('data')

    employees_tree_to_cmd(q)
    employees_tree_to_html(q)
    employees_tree_to_json(q)
