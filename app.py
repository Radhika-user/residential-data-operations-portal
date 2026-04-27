from flask import Flask, render_template, redirect, url_for, session, jsonify
import getpass

from db import get_csdb_connection, get_taxroll_connection

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


# -----------------------------
# HOME PAGE (Auto Windows User Display)
# -----------------------------
@app.route("/")
def home():
    user = getpass.getuser()
    return render_template("login.html", user=user)


# -----------------------------
# LOGIN (Session setup only - Windows based)
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    session["user"] = getpass.getuser()
    return redirect(url_for("dashboard"))


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    return render_template("dashboard.html", user=session["user"])


# -----------------------------
# CSDB TEST CONNECTION
# -----------------------------
@app.route("/test_csdb")
def test_csdb():
    try:
        conn = get_csdb_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SYSTEM_USER")
        result = cursor.fetchone()

        return jsonify({
            "status": "success",
            "sql_user": str(result[0])
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# -----------------------------
# TAXROLL TEST CONNECTION
# -----------------------------
@app.route("/test_taxroll")
def test_taxroll():
    try:
        conn = get_taxroll_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SYSTEM_USER")
        result = cursor.fetchone()

        return jsonify({
            "status": "success",
            "sql_user": str(result[0])
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# -----------------------------
# RUN APP (IMPORTANT FIX FOR PYCHARM)
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
