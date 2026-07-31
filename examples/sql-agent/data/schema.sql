CREATE TABLE IF NOT EXISTS sales_orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL CHECK (region IN ('east', 'south', 'north')),
    customer_name TEXT NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    net_revenue REAL NOT NULL CHECK (net_revenue >= 0)
);

CREATE INDEX IF NOT EXISTS idx_sales_orders_date_region
    ON sales_orders(order_date, region);
