from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

@app.route('/')
def dashboard():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siri4106@",
        database="superstore_db"
    )

    cursor = conn.cursor()

    # Total Sales
    cursor.execute("""
        SELECT ROUND(SUM(Sales), 2)
        FROM superstore_sales
    """)
    total_sales = cursor.fetchone()[0]

    # Total Orders
    cursor.execute("""
        SELECT COUNT(*)
        FROM superstore_sales
    """)
    total_orders = cursor.fetchone()[0]

    # Highest Demand Region
    cursor.execute("""
        SELECT Region, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY Region
        ORDER BY SUM(Sales) DESC
        LIMIT 1
    """)
    top_region = cursor.fetchone()

    # Top State
    cursor.execute("""
        SELECT State, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY State
        ORDER BY SUM(Sales) DESC
        LIMIT 1
    """)
    top_state = cursor.fetchone()

    # Top Product
    cursor.execute("""
        SELECT `Product Name`, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY `Product Name`
        ORDER BY SUM(Sales) DESC
        LIMIT 1
    """)
    top_product = cursor.fetchone()

    # Region-wise Sales Data for Bar Chart
    cursor.execute("""
        SELECT Region, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY Region
    """)
    region_data = cursor.fetchall()

    regions = [row[0] for row in region_data]
    sales_values = [float(row[1]) for row in region_data]

    # State-wise Sales Data for Pie Chart
    cursor.execute("""
        SELECT State, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY State
        ORDER BY SUM(Sales) DESC
    """)
    state_data = cursor.fetchall()

    states = [row[0] for row in state_data]
    state_sales = [float(row[1]) for row in state_data]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_sales=total_sales,
        total_orders=total_orders,
        top_region=top_region,
        top_state=top_state,
        top_product=top_product,
        regions=regions,
        sales_values=sales_values,
        states=states,
        state_sales=state_sales
    )

@app.route('/sales', methods=['GET', 'POST'])
def sales():

    if request.method == 'POST':

        order_id = request.form['order_id']
        order_date = request.form['order_date']
        customer_name = request.form['customer_name']
        state = request.form['state']
        region = request.form['region']
        product_name = request.form['product_name']
        sales_amount = request.form['sales']
        quantity = request.form['quantity']
        profit = request.form['profit']

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Siri4106@",
            database="superstore_db"
        )

        cursor = conn.cursor()

        query = """
        INSERT INTO superstore_sales
        (`Order ID`, `Order Date`, `Customer Name`,
         `State`, `Region`, `Product Name`,
         `Sales`, `Quantity`, `Profit`)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            order_id,
            order_date,
            customer_name,
            state,
            region,
            product_name,
            sales_amount,
            quantity,
            profit
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return "Record Added Successfully!"

    return render_template('sales.html')

@app.route('/reports')
def reports():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siri4106@",
        database="superstore_db"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT Region, ROUND(SUM(Sales), 2)
        FROM superstore_sales
        GROUP BY Region
    """)

    report_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'reports.html',
        report_data=report_data
    )
@app.route('/heatmap')
def heatmap():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siri4106@",
        database="superstore_db"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT State, ROUND(SUM(Sales),2)
        FROM superstore_sales
        GROUP BY State
        ORDER BY SUM(Sales) DESC
    """)

    state_sales = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'heatmap.html',
        state_sales=state_sales
    )
@app.route('/view_sales')
def view_sales():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siri4106@",
        database="superstore_db"
    )

    cursor = conn.cursor()

    search = request.args.get('search', '')

    query = """
    SELECT `Order ID`, `Customer Name`,
           `State`, `Region`,
           `Product Name`, `Sales`
    FROM superstore_sales
    WHERE `Customer Name` LIKE %s
       OR `State` LIKE %s
       OR `Product Name` LIKE %s
    ORDER BY Sales DESC
    LIMIT 100
    """

    search_term = f"%{search}%"

    cursor.execute(
        query,
        (search_term, search_term, search_term)
    )

    sales_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_sales.html',
        sales_data=sales_data
    )
# ADD THIS NEW FUNCTION HERE
@app.route('/edit/<order_id>', methods=['GET', 'POST'])
def edit_record(order_id):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siri4106@",
        database="superstore_db"
    )

    cursor = conn.cursor()

    # Update record when form is submitted
    if request.method == 'POST':
        print("post recieved")

        customer_name = request.form['customer_name']
        state = request.form['state']
        region = request.form['region']
        product_name = request.form['product_name']
        sales = request.form['sales']

        cursor.execute("""
            UPDATE superstore_sales
            SET `Customer Name`=%s,
                `State`=%s,
                `Region`=%s,
                `Product Name`=%s,
                `Sales`=%s
            WHERE `Order ID`=%s
        """, (
            customer_name,
            state,
            region,
            product_name,
            sales,
            order_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/view_sales')

    # Load record for editing
    cursor.execute("""
        SELECT `Order ID`,
               `Customer Name`,
               `State`,
               `Region`,
               `Product Name`,
               `Sales`
        FROM superstore_sales
        WHERE `Order ID` = %s
    """, (order_id,))

    record = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'edit_sales.html',
        record=record
    )
if __name__ == '__main__':
    app.run(debug=True)