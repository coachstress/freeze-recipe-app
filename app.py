from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

DB_NAME = "recipes.db"

# ==== DATABASE SETUP ====
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Buat tabel vaksin
    c.execute('''
        CREATE TABLE IF NOT EXISTS vaccine_recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    # Buat tabel step
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipe_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vaccine_id INTEGER NOT NULL,
            step TEXT NOT NULL,
            FOREIGN KEY (vaccine_id) REFERENCES vaccine_recipe(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ==== FLASK APP ====
app = Flask(__name__)

# Inisialisasi DB setiap kali app start
init_db()

# ==== ROUTES ====
@app.route("/")
def index():
    conn = get_db_connection()
    vaccines = conn.execute("SELECT * FROM vaccine_recipe").fetchall()
    conn.close()
    return render_template("index.html", vaccines=vaccines)

@app.route("/add_vaccine", methods=("GET", "POST"))
def add_vaccine():
    if request.method == "POST":
        name = request.form["name"]
        conn = get_db_connection()
        conn.execute("INSERT INTO vaccine_recipe (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_vaccine.html")

@app.route("/edit_vaccine/<int:vaccine_id>", methods=("GET", "POST"))
def edit_vaccine(vaccine_id):
    conn = get_db_connection()
    vaccine = conn.execute("SELECT * FROM vaccine_recipe WHERE id = ?", (vaccine_id,)).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        conn.execute("UPDATE vaccine_recipe SET name = ? WHERE id = ?", (name, vaccine_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("edit_vaccine.html", vaccine=vaccine)

@app.route("/delete_vaccine/<int:vaccine_id>")
def delete_vaccine(vaccine_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM recipe_steps WHERE vaccine_id = ?", (vaccine_id,))
    conn.execute("DELETE FROM vaccine_recipe WHERE id = ?", (vaccine_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/vaccine/<int:vaccine_id>")
def view_vaccine(vaccine_id):
    conn = get_db_connection()
    vaccine = conn.execute("SELECT * FROM vaccine_recipe WHERE id = ?", (vaccine_id,)).fetchone()
    steps = conn.execute("SELECT * FROM recipe_steps WHERE vaccine_id = ?", (vaccine_id,)).fetchall()
    conn.close()
    return render_template("view_vaccine.html", vaccine=vaccine, steps=steps)

@app.route("/add_step/<int:vaccine_id>", methods=("GET", "POST"))
def add_step(vaccine_id):
    if request.method == "POST":
        step = request.form["step"]
        conn = get_db_connection()
        conn.execute("INSERT INTO recipe_steps (vaccine_id, step) VALUES (?, ?)", (vaccine_id, step))
        conn.commit()
        conn.close()
        return redirect(url_for("view_vaccine", vaccine_id=vaccine_id))
    return render_template("add_step.html", vaccine_id=vaccine_id)

@app.route("/edit_step/<int:step_id>", methods=("GET", "POST"))
def edit_step(step_id):
    conn = get_db_connection()
    step = conn.execute("SELECT * FROM recipe_steps WHERE id = ?", (step_id,)).fetchone()
    if request.method == "POST":
        new_step = request.form["step"]
        conn.execute("UPDATE recipe_steps SET step = ? WHERE id = ?", (new_step, step_id))
        conn.commit()
        conn.close()
        return redirect(url_for("view_vaccine", vaccine_id=step["vaccine_id"]))
    conn.close()
    return render_template("edit_step.html", step=step)

@app.route("/delete_step/<int:step_id>/<int:vaccine_id>")
def delete_step(step_id, vaccine_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM recipe_steps WHERE id = ?", (step_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("view_vaccine", vaccine_id=vaccine_id))

# ==== RUN SERVER ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
