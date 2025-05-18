# python addData.py --count 5000
import psycopg2
from faker import Faker
import random
import argparse

parser = argparse.ArgumentParser(description="Generate fake data for the database.")
parser.add_argument('--count', type=int, default=100000, help='Number of people to generate (default: 100000)')
args = parser.parse_args()
record_count = args.count

conn = psycopg2.connect(
    dbname="mastersThesis", user="postgres", password="postgres",
    host="localhost", port="5432"
)
cur = conn.cursor()
fake = Faker()
print("Start...")

cur.execute("DROP TABLE IF EXISTS orders CASCADE")
cur.execute("DROP TABLE IF EXISTS address CASCADE")
cur.execute("DROP TABLE IF EXISTS person CASCADE")
cur.execute("DROP TABLE IF EXISTS databasechangelog CASCADE")
cur.execute("DROP TABLE IF EXISTS databasechangeloglock CASCADE")
cur.execute("DROP TABLE IF EXISTS flyway_schema_history CASCADE")
cur.execute("DROP TABLE IF EXISTS person_audit CASCADE")
cur.execute("DROP TABLE IF EXISTS big_table CASCADE")

cur.execute("""
    CREATE TABLE person (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        legacy_name VARCHAR(100)  
    )
""")

cur.execute("""
    CREATE TABLE address (
        id SERIAL PRIMARY KEY,
        person_id INT NOT NULL REFERENCES person(id),  
        street VARCHAR(200),
        city VARCHAR(100),
        zipcode VARCHAR(20)
    )
""")

cur.execute("""
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        person_id INT NOT NULL REFERENCES person(id),  
        order_date DATE,
        amount NUMERIC(10,2)
    )
""")

for _ in range(record_count):
    name = fake.name()
    email = fake.unique.email()
    legacy_name = name
    cur.execute(
        "INSERT INTO person (name, email, legacy_name) VALUES (%s, %s, %s)",
        (name, email, legacy_name)
    )

# Pobranie wszystkich ID osób do generowania danych powiązanych
cur.execute("SELECT id FROM person")
person_ids = [row[0] for row in cur.fetchall()]

# Generowanie adresów i zamówień
for pid in person_ids:
    # losujemy od 1 do 3 adresów na osobę
    for i in range(random.randint(1, 3)):
        street = fake.street_address()
        city = fake.city()
        zipcode = fake.postcode()
        cur.execute(
            "INSERT INTO address (person_id, street, city, zipcode) VALUES (%s, %s, %s, %s)",
            (pid, street, city, zipcode)
        )
    # losujemy od 0 do 5 zamówień na osobę
    for i in range(random.randint(0, 5)):
        order_date = fake.date_between(start_date='-1y', end_date='today')
        amount = round(random.uniform(10, 1000), 2)
        cur.execute(
            "INSERT INTO orders (person_id, order_date, amount) VALUES (%s, %s, %s)",
            (pid, order_date, amount)
        )

# (5) Zatwierdzenie zmian
conn.commit()
cur.close()
conn.close()
print("Finished!")