from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

# Testing, testing

app = Flask(__name__)

@app.template_filter('currency')
def currency(value):
    try:
        return "%.2f" % float(value)
    except (TypeError, ValueError):
        return value


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            budget REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            amount REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_month_report(conn, month):
    categories = conn.execute("SELECT * FROM categories").fetchall()
    items = []
    total_budget = 0
    total_spent = 0

    for cat in categories:
        spent = conn.execute("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE category_id = ? AND date LIKE ?
        """, (cat["id"], f"{month}%")).fetchone()["total"]

        item = {
            "id": cat["id"],
            "name": cat["name"],
            "budget": cat["budget"],
            "spent": spent,
            "remaining": cat["budget"] - spent
        }
        items.append(item)
        total_budget += cat["budget"]
        total_spent += spent

    return items, total_budget, total_spent


def split_by_budget(items):
    under_budget = []
    hit_budget = []
    over_budget = []

    for item in items:
        if item["remaining"] < 0:
            over_budget.append(item)
        elif item["remaining"] == 0:
            hit_budget.append(item)
        else:
            under_budget.append(item)

    return under_budget, hit_budget, over_budget

@app.route("/")
def index():
    conn = get_db()
    now = datetime.now()
    month = now.strftime("%Y-%m")
    month_label = now.strftime("%B, %Y")

    items, total_budget, total_spent = get_month_report(conn, month)
    under_budget, hit_budget, over_budget = split_by_budget(items)
    total_remaining = total_budget - total_spent
    total_progress_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0

    conn.close()
    return render_template(
        "index.html",
        under_budget=under_budget,
        hit_budget=hit_budget,
        over_budget=over_budget,
        month_label=month_label,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_remaining,
        total_progress_pct=total_progress_pct
    )

@app.route("/history")
def history():
    conn = get_db()
    search = request.args.get("search", "").strip()
    months = conn.execute(
        "SELECT DISTINCT SUBSTR(date, 1, 7) AS month FROM expenses ORDER BY month DESC"
    ).fetchall()

    history_data = []
    for row in months:
        month = row["month"]
        items, total_budget, total_spent = get_month_report(conn, month)
        label = datetime.strptime(month, "%Y-%m").strftime("%B, %Y")
        history_data.append({
            "month": month,
            "label": label,
            "items": items,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_budget - total_spent,
            "total_progress_pct": (total_spent / total_budget * 100) if total_budget > 0 else 0,
        })

    if search:
        search_lower = search.lower()
        history_data = [entry for entry in history_data if search_lower in entry["month"].lower() or search_lower in entry["label"].lower()]

    conn.close()
    return render_template("history.html", history=history_data)

@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        name = request.form["name"]
        budget = float(request.form["budget"])

        conn = get_db()
        conn.execute("INSERT INTO categories (name, budget) VALUES (?, ?)", (name, budget))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_category.html")

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    conn = get_db()

    if request.method == "POST":
        category_id = request.form["category_id"]
        amount = float(request.form["amount"])
        date = datetime.now().strftime("%Y-%m-%d")

        conn.execute(
            "INSERT INTO expenses (category_id, amount, date) VALUES (?, ?, ?)",
            (category_id, amount, date)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    categories = conn.execute("SELECT * FROM categories").fetchall()

    selected_category = request.args.get("category_id")

    conn.close()
    return render_template(
        "add_expense.html",
        categories=categories,
        selected_category=selected_category
    )

@app.route("/delete_category", methods=["POST"])
def delete_category():
    category_id = request.form.get("category_id")
    if category_id:
        conn = get_db()
        conn.execute("DELETE FROM expenses WHERE category_id = ?", (category_id,))
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)