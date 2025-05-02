CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    legacy_name VARCHAR(100)  
);

CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    person_id INT NOT NULL REFERENCES person(id),  
    street VARCHAR(200),
    city VARCHAR(100),
    zipcode VARCHAR(20)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    person_id INT NOT NULL REFERENCES person(id),  
    order_date DATE,
    amount NUMERIC(10,2)
);
