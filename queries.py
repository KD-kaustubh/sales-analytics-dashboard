from sqlalchemy import create_engine, text
import pandas as pd

# ── Connection ─────────────────────────────────────────────────────
DB_URL = "postgresql://postgres:kdsql@localhost:5432/olist_db"
engine = create_engine(DB_URL)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


# ── Query 1: Monthly Revenue Trend ────────────────────────────────
# Powers: Line chart — revenue over time
def get_monthly_revenue():
    sql = """
        SELECT 
            DATE_TRUNC('month', o.order_purchase_timestamp::timestamp) AS month,
            ROUND(SUM(p.payment_value)::numeric, 2) AS revenue
        FROM orders o
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY month
        ORDER BY month
    """
    return run_query(sql)


# ── Query 2: Top 10 Product Categories by Revenue ─────────────────
# Powers: Horizontal bar chart
def get_top_categories():
    sql = """
        SELECT 
            pr.product_category_name AS category,
            ROUND(SUM(i.price)::numeric, 2) AS revenue,
            COUNT(DISTINCT i.order_id) AS total_orders
        FROM items i
        JOIN products pr ON i.product_id = pr.product_id
        WHERE pr.product_category_name IS NOT NULL
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 10
    """
    return run_query(sql)


# ── Query 3: Order Status Breakdown ───────────────────────────────
# Powers: Pie/donut chart
def get_order_status():
    sql = """
        SELECT 
            order_status,
            COUNT(*) AS total_orders,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
        FROM orders
        GROUP BY order_status
        ORDER BY total_orders DESC
    """
    return run_query(sql)


# ── Query 4: Revenue by Payment Method ────────────────────────────
# Powers: Bar chart
def get_payment_methods():
    sql = """
        SELECT 
            payment_type,
            COUNT(*) AS total_transactions,
            ROUND(SUM(payment_value)::numeric, 2) AS total_revenue
        FROM payments
        GROUP BY payment_type
        ORDER BY total_revenue DESC
    """
    return run_query(sql)


# ── Query 5: Top 10 States by Number of Orders ────────────────────
# Powers: Choropleth or bar chart
def get_orders_by_state():
    sql = """
        SELECT 
            c.customer_state AS state,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(p.payment_value)::numeric, 2) AS revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY state
        ORDER BY total_orders DESC
        LIMIT 10
    """
    return run_query(sql)


# ── Query 6: Average Delivery Time by State ───────────────────────
# Powers: Bar chart — operational insight
def get_avg_delivery_time():
    sql = """
        SELECT 
            c.customer_state AS state,
            ROUND(AVG(
                EXTRACT(EPOCH FROM (
                    o.order_delivered_customer_date::timestamp - 
                    o.order_purchase_timestamp::timestamp
                )) / 86400
            )::numeric, 1) AS avg_delivery_days
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_delivered_customer_date IS NOT NULL
          AND o.order_status = 'delivered'
        GROUP BY state
        ORDER BY avg_delivery_days ASC
        LIMIT 10
    """
    return run_query(sql)


# ── Query 7: Daily Orders Count (last 6 months of data) ───────────
# Powers: Area chart
def get_daily_orders():
    sql = """
        SELECT 
            DATE_TRUNC('day', order_purchase_timestamp::timestamp) AS day,
            COUNT(*) AS total_orders
        FROM orders
        WHERE order_purchase_timestamp::timestamp >= (
            SELECT MAX(order_purchase_timestamp::timestamp) - INTERVAL '180 days'
            FROM orders
        )
        GROUP BY day
        ORDER BY day
    """
    return run_query(sql)


# ── Query 8: Revenue vs Freight Cost by Category ──────────────────
# Powers: Scatter plot
def get_revenue_vs_freight():
    sql = """
        SELECT 
            pr.product_category_name AS category,
            ROUND(AVG(i.price)::numeric, 2) AS avg_price,
            ROUND(AVG(i.freight_value)::numeric, 2) AS avg_freight,
            COUNT(*) AS total_items
        FROM items i
        JOIN products pr ON i.product_id = pr.product_id
        WHERE pr.product_category_name IS NOT NULL
        GROUP BY category
        HAVING COUNT(*) > 100
        ORDER BY avg_price DESC
        LIMIT 20
    """
    return run_query(sql)


# ── Query 9: Monthly New Customers ────────────────────────────────
# Powers: Bar chart — growth metric
def get_new_customers_monthly():
    sql = """
        SELECT 
            DATE_TRUNC('month', first_order::timestamp) AS month,
            COUNT(*) AS new_customers
        FROM (
            SELECT 
                customer_unique_id,
                MIN(o.order_purchase_timestamp) AS first_order
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY customer_unique_id
        ) first_orders
        GROUP BY month
        ORDER BY month
    """
    return run_query(sql)


# ── Query 10: KPI Summary Card ─────────────────────────────────────
# Powers: 4 KPI cards at top of dashboard
def get_kpi_summary():
    sql = """
        SELECT
            COUNT(DISTINCT o.order_id)                        AS total_orders,
            ROUND(SUM(p.payment_value)::numeric, 2)           AS total_revenue,
            ROUND(AVG(p.payment_value)::numeric, 2)           AS avg_order_value,
            COUNT(DISTINCT c.customer_unique_id)              AS unique_customers
        FROM orders o
        JOIN payments p  ON o.order_id  = p.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
    """
    return run_query(sql)


# ── Test all queries ───────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("Monthly Revenue",       get_monthly_revenue),
        ("Top Categories",        get_top_categories),
        ("Order Status",          get_order_status),
        ("Payment Methods",       get_payment_methods),
        ("Orders by State",       get_orders_by_state),
        ("Avg Delivery Time",     get_avg_delivery_time),
        ("Daily Orders",          get_daily_orders),
        ("Revenue vs Freight",    get_revenue_vs_freight),
        ("New Customers Monthly", get_new_customers_monthly),
        ("KPI Summary",           get_kpi_summary),
    ]

    for name, func in tests:
        df = func()
        print(f"✅ {name:25s} → {df.shape[0]} rows, {df.shape[1]} cols")
        print(df.head(2))
        print()