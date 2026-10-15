from flask import Flask, render_template, request, redirect, url_for, flash
from database import create_connection

app = Flask(__name__)
app.secret_key = "bank_management_secret_key"


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = create_connection()

        if connection:

            cursor = connection.cursor()

            query = """
            SELECT admin_id, username
            FROM admins
            WHERE username = %s AND password = %s
            """

            cursor.execute(query, (username, password))

            admin = cursor.fetchone()

            cursor.close()
            connection.close()

            if admin:
                return redirect(url_for("admin_dashboard"))

            else:
                flash("Invalid username or password!")

        else:
            flash("Database connection failed!")

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        # =========================
        # TOTAL CUSTOMERS
        # =========================

        cursor.execute(
            "SELECT COUNT(*) FROM customers"
        )

        total_customers = cursor.fetchone()[0]


        # =========================
        # TOTAL ACCOUNTS
        # =========================

        cursor.execute(
            "SELECT COUNT(*) FROM accounts"
        )

        total_accounts = cursor.fetchone()[0]


        # =========================
        # TOTAL TRANSACTIONS
        # =========================

        cursor.execute(
            "SELECT COUNT(*) FROM transactions"
        )

        total_transactions = cursor.fetchone()[0]


        # =========================
        # TOTAL BALANCE
        # =========================

        cursor.execute(
            "SELECT COALESCE(SUM(balance), 0) FROM accounts"
        )

        total_balance = cursor.fetchone()[0]


        # =========================
        # RECENT TRANSACTIONS
        # =========================

        cursor.execute("""
            SELECT
                t.transaction_id,
                a.account_number,
                c.full_name,
                t.transaction_type,
                t.amount,
                t.transaction_date
            FROM transactions t
            JOIN accounts a
                ON t.account_id = a.account_id
            JOIN customers c
                ON a.customer_id = c.customer_id
            ORDER BY t.transaction_id DESC
            LIMIT 5
        """)

        recent_transactions = cursor.fetchall()


        # =========================
        # CLOSE DATABASE
        # =========================

        cursor.close()
        connection.close()


        # =========================
        # SEND DATA TO DASHBOARD
        # =========================

        return render_template(
            "admin_dashboard.html",

            total_customers=total_customers,

            total_accounts=total_accounts,

            total_transactions=total_transactions,

            total_balance=total_balance,

            recent_transactions=recent_transactions
        )


    return "Database connection failed!"
@app.route("/analytics")
def analytics():

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        # Total Customers
        cursor.execute(
            "SELECT COUNT(*) FROM customers"
        )
        total_customers = cursor.fetchone()[0]

        # Total Accounts
        cursor.execute(
            "SELECT COUNT(*) FROM accounts"
        )
        total_accounts = cursor.fetchone()[0]

        # Total Transactions
        cursor.execute(
            "SELECT COUNT(*) FROM transactions"
        )
        total_transactions = cursor.fetchone()[0]

        # Total Balance
        cursor.execute(
            "SELECT COALESCE(SUM(balance), 0) FROM accounts"
        )
        total_balance = cursor.fetchone()[0]

        # Deposit Total
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Deposit'
        """)
        total_deposit = cursor.fetchone()[0]

        # Withdrawal Total
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Withdrawal'
        """)
        total_withdrawal = cursor.fetchone()[0]

        # Transaction Type Count
        cursor.execute("""
            SELECT transaction_type, COUNT(*)
            FROM transactions
            GROUP BY transaction_type
        """)

        transaction_data = cursor.fetchall()

        transaction_labels = []
        transaction_counts = []

        for row in transaction_data:
            transaction_labels.append(row[0])
            transaction_counts.append(row[1])

        cursor.close()
        connection.close()

        return render_template(
            "analytics.html",

            total_customers=total_customers,
            total_accounts=total_accounts,
            total_transactions=total_transactions,
            total_balance=total_balance,

            total_deposit=total_deposit,
            total_withdrawal=total_withdrawal,

            transaction_labels=transaction_labels,
            transaction_counts=transaction_counts
        )

    return "Database connection failed!"
# =========================================================
# CUSTOMER MANAGEMENT
# VIEW + SEARCH
# =========================================================

@app.route("/customers")
def customers():

    search = request.args.get("search", "")

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if search:

            query = """
            SELECT
                customer_id,
                full_name,
                email,
                phone,
                address,
                created_at
            FROM customers
            WHERE full_name LIKE %s
               OR email LIKE %s
               OR phone LIKE %s
            ORDER BY customer_id DESC
            """

            search_value = "%" + search + "%"

            cursor.execute(
                query,
                (
                    search_value,
                    search_value,
                    search_value
                )
            )

        else:

            query = """
            SELECT
                customer_id,
                full_name,
                email,
                phone,
                address,
                created_at
            FROM customers
            ORDER BY customer_id DESC
            """

            cursor.execute(query)

        customers_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "customers.html",
            customers=customers_data,
            search=search
        )

    return "Database connection failed!"


# =========================================================
# ADD CUSTOMER
# =========================================================

@app.route("/add-customer", methods=["GET", "POST"])
def add_customer():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = request.form["password"]

        connection = create_connection()

        if connection:

            cursor = connection.cursor()

            query = """
            INSERT INTO customers
            (
                full_name,
                email,
                phone,
                address,
                password
            )
            VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                full_name,
                email,
                phone,
                address,
                password
            )

            cursor.execute(query, values)

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("customers"))

        return "Database connection failed!"

    return render_template("add_customer.html")


# =========================================================
# EDIT CUSTOMER
# =========================================================

@app.route("/edit-customer/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if request.method == "POST":

            full_name = request.form["full_name"]
            email = request.form["email"]
            phone = request.form["phone"]
            address = request.form["address"]

            query = """
            UPDATE customers
            SET
                full_name = %s,
                email = %s,
                phone = %s,
                address = %s
            WHERE customer_id = %s
            """

            cursor.execute(
                query,
                (
                    full_name,
                    email,
                    phone,
                    address,
                    customer_id
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("customers"))

        query = """
        SELECT
            customer_id,
            full_name,
            email,
            phone,
            address
        FROM customers
        WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        if customer:

            return render_template(
                "edit_customer.html",
                customer=customer
            )

        return "Customer not found!"

    return "Database connection failed!"


# =========================================================
# DELETE CUSTOMER
# =========================================================

@app.route("/delete-customer/<int:customer_id>")
def delete_customer(customer_id):

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        query = """
        DELETE FROM customers
        WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("customers"))

    return "Database connection failed!"


# =========================================================
# ACCOUNT MANAGEMENT
# VIEW + SEARCH
# =========================================================

@app.route("/accounts")
def accounts():

    search = request.args.get("search", "")

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if search:

            query = """
            SELECT
                a.account_id,
                c.full_name,
                a.account_number,
                a.account_type,
                a.balance,
                a.status,
                a.created_at
            FROM accounts a
            JOIN customers c
                ON a.customer_id = c.customer_id
            WHERE c.full_name LIKE %s
               OR a.account_number LIKE %s
               OR a.account_type LIKE %s
            ORDER BY a.account_id DESC
            """

            search_value = "%" + search + "%"

            cursor.execute(
                query,
                (
                    search_value,
                    search_value,
                    search_value
                )
            )

        else:

            query = """
            SELECT
                a.account_id,
                c.full_name,
                a.account_number,
                a.account_type,
                a.balance,
                a.status,
                a.created_at
            FROM accounts a
            JOIN customers c
                ON a.customer_id = c.customer_id
            ORDER BY a.account_id DESC
            """

            cursor.execute(query)

        accounts_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "accounts.html",
            accounts=accounts_data,
            search=search
        )

    return "Database connection failed!"


# =========================================================
# ADD ACCOUNT
# =========================================================

@app.route("/add-account", methods=["GET", "POST"])
def add_account():

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if request.method == "POST":

            customer_id = request.form["customer_id"]
            account_number = request.form["account_number"]
            account_type = request.form["account_type"]
            balance = request.form["balance"]

            query = """
            INSERT INTO accounts
            (
                customer_id,
                account_number,
                account_type,
                balance
            )
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    customer_id,
                    account_number,
                    account_type,
                    balance
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("accounts"))

        cursor.execute("""
            SELECT
                customer_id,
                full_name
            FROM customers
            ORDER BY full_name
        """)

        customers_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "add_account.html",
            customers=customers_data
        )

    return "Database connection failed!"


# =========================================================
# EDIT ACCOUNT
# =========================================================

@app.route("/edit-account/<int:account_id>", methods=["GET", "POST"])
def edit_account(account_id):

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if request.method == "POST":

            account_number = request.form["account_number"]
            account_type = request.form["account_type"]
            status = request.form["status"]

            query = """
            UPDATE accounts
            SET
                account_number = %s,
                account_type = %s,
                status = %s
            WHERE account_id = %s
            """

            cursor.execute(
                query,
                (
                    account_number,
                    account_type,
                    status,
                    account_id
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("accounts"))

        query = """
        SELECT
            a.account_id,
            c.full_name,
            a.account_number,
            a.account_type,
            a.balance,
            a.status,
            a.created_at
        FROM accounts a
        JOIN customers c
            ON a.customer_id = c.customer_id
        WHERE a.account_id = %s
        """

        cursor.execute(query, (account_id,))

        account = cursor.fetchone()

        cursor.close()
        connection.close()

        if account:

            return render_template(
                "edit_account.html",
                account=account
            )

        return "Account not found!"

    return "Database connection failed!"


# =========================================================
# DELETE ACCOUNT
# =========================================================

@app.route("/delete-account/<int:account_id>")
def delete_account(account_id):

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        query = """
        DELETE FROM accounts
        WHERE account_id = %s
        """

        cursor.execute(query, (account_id,))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("accounts"))

    return "Database connection failed!"



# =========================
# TRANSACTION MANAGEMENT
# VIEW + SEARCH TRANSACTIONS
# =========================

@app.route("/transactions")
def transactions():

    search = request.args.get("search", "")

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        if search:

            query = """
            SELECT
                t.transaction_id,
                a.account_number,
                c.full_name,
                t.transaction_type,
                t.amount,
                t.transaction_date
            FROM transactions t
            JOIN accounts a
                ON t.account_id = a.account_id
            JOIN customers c
                ON a.customer_id = c.customer_id
            WHERE c.full_name LIKE %s
               OR a.account_number LIKE %s
               OR t.transaction_type LIKE %s
            ORDER BY t.transaction_id DESC
            """

            search_value = "%" + search + "%"

            cursor.execute(
                query,
                (search_value, search_value, search_value)
            )

        else:

            query = """
            SELECT
                t.transaction_id,
                a.account_number,
                c.full_name,
                t.transaction_type,
                t.amount,
                t.transaction_date
            FROM transactions t
            JOIN accounts a
                ON t.account_id = a.account_id
            JOIN customers c
                ON a.customer_id = c.customer_id
            ORDER BY t.transaction_id DESC
            """

            cursor.execute(query)

        transactions_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "transactions.html",
            transactions=transactions_data,
            search=search
        )

    return "Database connection failed!"


# 

# =========================================================
# ADD TRANSACTION
# =========================================================

@app.route("/add-transaction", methods=["GET", "POST"])
def add_transaction():

    connection = create_connection()

    if connection:

        cursor = connection.cursor()

        # -----------------------------------------
        # SAVE TRANSACTION
        # -----------------------------------------

        if request.method == "POST":

            account_id = request.form["account_id"]

            transaction_type = request.form[
                "transaction_type"
            ]

            amount = float(
                request.form["amount"]
            )

            # Check account balance
            cursor.execute(
                """
                SELECT balance
                FROM accounts
                WHERE account_id = %s
                """,
                (account_id,)
            )

            account = cursor.fetchone()

            if not account:

                cursor.close()
                connection.close()

                return "Account not found!"

            current_balance = float(
                account[0]
            )

            # -----------------------------------------
            # DEPOSIT
            # -----------------------------------------

            if transaction_type == "Deposit":

                new_balance = (
                    current_balance + amount
                )

            # -----------------------------------------
            # WITHDRAWAL
            # -----------------------------------------

            elif transaction_type == "Withdrawal":

                if amount > current_balance:

                    cursor.close()
                    connection.close()

                    return "Insufficient balance!"

                new_balance = (
                    current_balance - amount
                )

            else:

                cursor.close()
                connection.close()

                return "Invalid transaction type!"

            # -----------------------------------------
            # INSERT TRANSACTION
            # -----------------------------------------
            # NOW() automatically saves current date/time

            query = """
            INSERT INTO transactions
            (
                account_id,
                transaction_type,
                amount,
                transaction_date
            )
            VALUES (%s, %s, %s, NOW())
            """

            cursor.execute(
                query,
                (
                    account_id,
                    transaction_type,
                    amount
                )
            )

            # -----------------------------------------
            # UPDATE ACCOUNT BALANCE
            # -----------------------------------------

            update_query = """
            UPDATE accounts
            SET balance = %s
            WHERE account_id = %s
            """

            cursor.execute(
                update_query,
                (
                    new_balance,
                    account_id
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(
                url_for("transactions")
            )

        # -----------------------------------------
        # ACCOUNT DROPDOWN
        # -----------------------------------------

        query = """
        SELECT
            a.account_id,
            a.account_number,
            c.full_name,
            a.balance
        FROM accounts a
        JOIN customers c
            ON a.customer_id = c.customer_id
        ORDER BY a.account_id DESC
        """

        cursor.execute(query)

        accounts_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "add_transaction.html",
            accounts=accounts_data
        )

    return "Database connection failed!"


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)