-- step 1 change the datatypes into date datatype

ALTER TABLE superstore_sales
    ALTER COLUMN order_date TYPE DATE USING order_date::TEXT::DATE,
    ALTER COLUMN ship_date  TYPE DATE USING ship_date::TEXT::DATE;


-- step 2 change the integers datatype and remove the symbols

ALTER TABLE superstore_sales
    ALTER COLUMN sales TYPE NUMERIC(10, 4)
        USING REPLACE(TRIM(LEADING '$' FROM sales), ',', '')::NUMERIC,
    ALTER COLUMN postal_code TYPE INTEGER
        USING postal_code::NUMERIC::INTEGER;

-- step 3 set the row id to the primary key

ALTER TABLE superstore_sales
    ADD PRIMARY KEY (row_id);

-- step 4 trim the white spaces in all the colums
UPDATE superstore_sales
SET
    ship_mode     = TRIM(ship_mode),
    segment       = TRIM(segment),
    country       = TRIM(country),
    city          = TRIM(city),
    state         = TRIM(state),
    region        = TRIM(region),
    category      = TRIM(category),
    "sub-category"= TRIM("sub-category"),
    product_name  = TRIM(product_name);

-- step 5  Add and Calculate 'days_to_ship'

ALTER TABLE superstore_sales
    ADD COLUMN days_to_ship INTEGER;

UPDATE superstore_sales
SET days_to_ship = ship_date - order_date;