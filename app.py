from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
init_db()
DB_NAME = "recipes.db"

# ================= TEMPLATE HTML =================
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Freeze Drying Recipes</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        select, input, textarea, button { padding: 5px; margin: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background: #2c3e50; color: white; }
        .form-box { border: 1px solid #ccc; padding: 15px; margin: 20px 0; background: #f9f9f9; }
        .action-btn { padding: 5px 10px; margin: 2px; border: none; cursor: pointer; }
        .edit { background: #3498db; color: white; }
        .delete { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <h1>Freeze Drying Recipes</h1>

    <form method="get">
        <label for="vaccine">Pilih Vaksin:</label>
        <select name="id" onchange="this.form.submit()">
            <option value="">-- pilih vaksin --</option>
            {% for v in vaccines %}
            <option value="{{ v[0] }}" {% if v[0] == selected_id %}selected{% endif %}>
                {{ v[1] }}
            </option>
            {% endfor %}
        </select>
    </form>

    {% if recipe %}
    <h2>Resep: {{ recipe[1] }} (Batch: {{ recipe[2] }})</h2>
    <p>Tanggal: {{ recipe[3] }} | Volume: {{ recipe[4] }} | Note: {{ recipe[5] }} | Total Hours: {{ recipe[6] }}</p>

    <form method="get" action="{{ url_for('edit_recipe', recipe_id=recipe[0]) }}">
        <button type="submit" class="action-btn edit">Edit Vaksin</button>
    </form>
    <form method="post" action="{{ url_for('delete_recipe', recipe_id=recipe[0]) }}" onsubmit="return confirm('Yakin hapus vaksin ini beserta semua stepnya?')">
        <button type="submit" class="action-btn delete">Hapus Vaksin</button>
    </form>

    <table>
        <tr>
            <th>Stage</th><th>Suhu</th><th>Ramp</th><th>Soak</th><th>Vacuum</th><th>Hours</th><th>Aksi</th>
        </tr>
        {% for step in steps %}
        <tr>
            <td>{{ step[2] }}</td>
            <td>{{ step[3] }}</td>
            <td>{{ step[4] }}</td>
            <td>{{ step[5] }}</td>
            <td>{{ step[6] if step[6] else "-" }}</td>
            <td>{{ step[7] if step[7] else "-" }}</td>
            <td>
                <form method="get" action="{{ url_for('edit_step', step_id=step[0]) }}" style="display:inline;">
                    <button type="submit" class="action-btn edit">Edit</button>
                </form>
                <form method="post" action="{{ url_for('delete_step', step_id=step[0]) }}" style="display:inline;" onsubmit="return confirm('Yakin hapus step ini?')">
                    <button type="submit" class="action-btn delete">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h3>Tambah Step Baru</h3>
    <div class="form-box">
        <form method="post" action="{{ url_for('add_step', recipe_id=recipe[0]) }}">
            <label>Stage:</label><br>
            <input type="text" name="stage" required><br>
            <label>Suhu:</label><br>
            <input type="number" step="0.1" name="suhu" required><br>
            <label>Ramp:</label><br>
            <input type="number" name="ramp"><br>
            <label>Soak:</label><br>
            <input type="number" name="soak"><br>
            <label>Vacuum:</label><br>
            <input type="number" step="0.001" name="vacuum"><br>
            <label>Hours:</label><br>
            <input type="number" name="hours"><br><br>
            <button type="submit">Tambah Step</button>
        </form>
    </div>
    {% endif %}

    <hr>
    <h2>Tambah Vaksin Baru</h2>
    <div class="form-box">
        <form method="post" action="{{ url_for('add_recipe') }}">
            <label>Nama Vaksin:</label><br>
            <input type="text" name="vaccine_name" required><br>
            <label>Batch Code:</label><br>
            <input type="text" name="batch_code"><br>
            <label>Tanggal:</label><br>
            <input type="date" name="date"><br>
            <label>Volume:</label><br>
            <input type="text" name="volume"><br>
            <label>Note:</label><br>
            <textarea name="note"></textarea><br>
            <label>Total Hours:</label><br>
            <input type="number" name="total_hours"><br><br>
            <button type="submit">Tambah Vaksin</button>
        </form>
    </div>
</body>
</html>
"""

# ================ DB INIT =================
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE vaccine_recipe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vaccine_name TEXT,
                batch_code TEXT,
                date TEXT,
                volume TEXT,
                note TEXT,
                total_hours INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE recipe_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                stage TEXT,
                suhu REAL,
                ramp INTEGER,
                soak INTEGER,
                vacuum REAL,
                hours INTEGER,
                FOREIGN KEY(recipe_id) REFERENCES vaccine_recipe(id)
            )
        """)
        # Data contoh
        c.execute("""
            INSERT INTO vaccine_recipe (vaccine_name, batch_code, date, volume, note, total_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("IB NV-1", "A23AN25OOT", "2025-08-29", "2.8 ml", "SM + BP + Lactose", 35))
        recipe_id = c.lastrowid
        steps = [
            (recipe_id, "Cooling", -40, 30, 15, None, 5),
            (recipe_id, "Cooling", -50, 30, 240, None, None),
            (recipe_id, "Primary Drying", -30, 60, 60, 0.250, 22),
            (recipe_id, "Primary Drying", -20, 120, 300, 0.175, None),
            (recipe_id, "Primary Drying", -10, 240, 120, 0.150, None),
            (recipe_id, "Primary Drying", 0, 240, 180, 0.125, None),
            (recipe_id, "Secondary Drying", 10, 180, 120, 0.100, 8),
            (recipe_id, "Secondary Drying", 35, 120, 60, 0.050, None),
        ]
        c.executemany("""
            INSERT INTO recipe_steps (recipe_id, stage, suhu, ramp, soak, vacuum, hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, steps)
        conn.commit()
        conn.close()

# ================ ROUTES =================
@app.route("/", methods=["GET"])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM vaccine_recipe")
    vaccines = c.fetchall()
    selected_id = request.args.get("id")
    recipe, steps = None, []
    if selected_id:
        c.execute("SELECT * FROM vaccine_recipe WHERE id=?", (selected_id,))
        recipe = c.fetchone()
        c.execute("SELECT * FROM recipe_steps WHERE recipe_id=?", (selected_id,))
        steps = c.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, vaccines=vaccines, recipe=recipe, steps=steps, selected_id=int(selected_id) if selected_id else None)

@app.route("/add", methods=["POST"])
def add_recipe():
    data = (
        request.form["vaccine_name"],
        request.form["batch_code"],
        request.form["date"],
        request.form["volume"],
        request.form["note"],
        request.form["total_hours"] if request.form["total_hours"] else None
    )
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO vaccine_recipe (vaccine_name, batch_code, date, volume, note, total_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/add_step/<int:recipe_id>", methods=["POST"])
def add_step(recipe_id):
    data = (
        recipe_id,
        request.form["stage"],
        request.form["suhu"],
        request.form["ramp"] if request.form["ramp"] else None,
        request.form["soak"] if request.form["soak"] else None,
        request.form["vacuum"] if request.form["vacuum"] else None,
        request.form["hours"] if request.form["hours"] else None,
    )
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO recipe_steps (recipe_id, stage, suhu, ramp, soak, vacuum, hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
    return redirect(url_for("index", id=recipe_id))

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == "POST":
        data = (
            request.form["vaccine_name"],
            request.form["batch_code"],
            request.form["date"],
            request.form["volume"],
            request.form["note"],
            request.form["total_hours"] if request.form["total_hours"] else None,
            recipe_id
        )
        c.execute("""
            UPDATE vaccine_recipe
            SET vaccine_name=?, batch_code=?, date=?, volume=?, note=?, total_hours=?
            WHERE id=?
        """, data)
        conn.commit()
        conn.close()
        return redirect(url_for("index", id=recipe_id))
    else:
        c.execute("SELECT * FROM vaccine_recipe WHERE id=?", (recipe_id,))
        recipe = c.fetchone()
        conn.close()
        return f"""
        <h2>Edit Vaksin</h2>
        <form method="post">
            Nama: <input type="text" name="vaccine_name" value="{recipe[1]}"><br>
            Batch: <input type="text" name="batch_code" value="{recipe[2]}"><br>
            Tanggal: <input type="date" name="date" value="{recipe[3]}"><br>
            Volume: <input type="text" name="volume" value="{recipe[4]}"><br>
            Note: <textarea name="note">{recipe[5]}</textarea><br>
            Total Hours: <input type="number" name="total_hours" value="{recipe[6]}"><br>
            <button type="submit">Simpan</button>
        </form>
        """

@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM recipe_steps WHERE recipe_id=?", (recipe_id,))
    c.execute("DELETE FROM vaccine_recipe WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit_step/<int:step_id>", methods=["GET", "POST"])
def edit_step(step_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == "POST":
        data = (
            request.form["stage"],
            request.form["suhu"],
            request.form["ramp"] if request.form["ramp"] else None,
            request.form["soak"] if request.form["soak"] else None,
            request.form["vacuum"] if request.form["vacuum"] else None,
            request.form["hours"] if request.form["hours"] else None,
            step_id
        )
        c.execute("""
            UPDATE recipe_steps
            SET stage=?, suhu=?, ramp=?, soak=?, vacuum=?, hours=?
            WHERE id=?
        """, data)
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    else:
        c.execute("SELECT * FROM recipe_steps WHERE id=?", (step_id,))
        step = c.fetchone()
        conn.close()
        return f"""
        <h2>Edit Step</h2>
        <form method="post">
            Stage: <input type="text" name="stage" value="{step[2]}"><br>
            Suhu: <input type="number" step="0.1" name="suhu" value="{step[3]}"><br>
            Ramp: <input type="number" name="ramp" value="{step[4] if step[4] else ''}"><br>
            Soak: <input type="number" name="soak" value="{step[5] if step[5] else ''}"><br>
            Vacuum: <input type="number" step="0.001" name="vacuum" value="{step[6] if step[6] else ''}"><br>
            Hours: <input type="number" name="hours" value="{step[7] if step[7] else ''}"><br>
            <button type="submit">Simpan</button>
        </form>
        """

@app.route("/delete_step/<int:step_id>", methods=["POST"])
def delete_step(step_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT recipe_id FROM recipe_steps WHERE id=?", (step_id,))
    recipe_id = c.fetchone()[0]
    c.execute("DELETE FROM recipe_steps WHERE id=?", (step_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index", id=recipe_id))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

