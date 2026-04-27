from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, send_file
)

from db import get_csdb_connection, get_taxroll_connection
import pandas as pd
import io
import os
import getpass
import platform
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# ================= ADMIN USERS =================
ADMIN_USERS = [
    "RADHIKAJ",
    "KARTHIK.PADMANABAN"
]

ALLOWED_SPS = {
    "EXEC dbo.sp_UpdateResidentialData_CAD;",
    "Exec Send_CommercialSales_Core_Report;",
    "Exec Send_CommercialSales_NonCore_Report;",
    "EXEC dbo.usp_Load_Clickhouse_Sales;"
}

run_history = []
last_preview_data = []

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        display_user = getpass.getuser()

        if request.method == "POST":

            # Render / Linux / Non-Windows
            if platform.system() != "Windows":
                session.clear()
                session["user"] = display_user.lower()
                session["windows_user"] = display_user
                session["is_admin"] = display_user.upper() in ADMIN_USERS

                return redirect(url_for("dashboard"))

            # Local Windows → SQL validation
            conn = get_csdb_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT SYSTEM_USER")
            windows_user = cursor.fetchone()[0]

            username = windows_user.split("\\")[-1].lower()

            session.clear()
            session["user"] = username
            session["windows_user"] = windows_user
            session["is_admin"] = username.upper() in ADMIN_USERS

            conn.close()

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            username=display_user
        )

    except Exception as e:
        return render_template(
            "login.html",
            error=str(e),
            username=getpass.getuser()
        )

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    try:
        if not session.get("user"):
            return redirect(url_for("login"))

        return render_template(
            "index.html",
            sps=list(ALLOWED_SPS),
            tables=["TaxRoll_2026"],
            history=run_history,
            username=session.get(
                "windows_user",
                session.get("user")
            ),
            is_admin=session.get("is_admin", False)
        )

    except Exception as e:
        return f"Dashboard Error: {str(e)}"

# ================= RUN SP =================
@app.route("/run_sp", methods=["POST"])
def run_sp():
    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    if not session.get("is_admin", False):
        return jsonify({
            "status": "error",
            "message": "Access Denied - Admins Only"
        }), 403

    sp_name = request.form.get("sp_name")

    if sp_name not in ALLOWED_SPS:
        return jsonify({
            "status": "error",
            "message": "Invalid SP"
        }), 400

    conn = None

    try:
        conn = get_csdb_connection()
        cursor = conn.cursor()

        cursor.execute(sp_name)
        conn.commit()

        run_history.append({
            "action": "Stored Procedure",
            "source": sp_name,
            "status": "Success",
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "user": session.get("user")
        })

        return jsonify({
            "status": "success",
            "message": "Stored Procedure executed successfully"
        })

    except Exception as e:
        run_history.append({
            "action": "Stored Procedure",
            "source": sp_name,
            "status": "Failed",
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "user": session.get("user")
        })

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn:
            conn.close()

# ================= PREVIEW TAXROLL =================
@app.route("/preview_taxroll", methods=["POST"])
def preview_taxroll():
    global last_preview_data

    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    cad_account = request.form.get("cad_account", "").strip()
    prop_address = request.form.get("prop_address", "").strip()
    parcel_id = request.form.get("parcel_id", "").strip()
    cad_id = request.form.get("cad_id", "").strip()

    conn = None

    try:
        conn = get_taxroll_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                txroll_CADAccountNumber,
                txroll_PropAddress,
                txroll_ParcelID,
                txroll_CadID
            FROM dbo.TaxRoll_2026 WITH (NOLOCK)
            WHERE 1=1
        """

        params = []

        if cad_account:
            accounts = [
                x.strip()
                for x in cad_account.replace("\n", ",").split(",")
                if x.strip()
            ]

            placeholders = ",".join(["?"] * len(accounts))
            query += f"""
                AND txroll_CADAccountNumber IN ({placeholders})
            """
            params.extend(accounts)

        if prop_address:
            addresses = [
                x.strip()
                for x in prop_address.replace("\n", ",").split(",")
                if x.strip()
            ]

            conditions = []
            for addr in addresses:
                conditions.append("txroll_PropAddress LIKE ?")
                params.append(f"%{addr}%")

            query += f"""
                AND ({' OR '.join(conditions)})
            """

        if parcel_id:
            parcels = [
                x.strip()
                for x in parcel_id.replace("\n", ",").split(",")
                if x.strip()
            ]

            placeholders = ",".join(["?"] * len(parcels))
            query += f"""
                AND txroll_ParcelID IN ({placeholders})
            """
            params.extend(parcels)

        if cad_id:
            cad_ids = [
                x.strip()
                for x in cad_id.replace("\n", ",").split(",")
                if x.strip()
            ]

            placeholders = ",".join(["?"] * len(cad_ids))
            query += f"""
                AND txroll_CadID IN ({placeholders})
            """
            params.extend(cad_ids)

        cursor.execute(query, params)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

        last_preview_data = data

        return jsonify({
            "status": "success",
            "columns": columns,
            "data": data
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn:
            conn.close()

# ================= EXCEL DOWNLOAD =================
@app.route("/download_excel")
def download_excel():
    global last_preview_data

    if not last_preview_data:
        return jsonify({
            "status": "error",
            "message": "No data available"
        })

    df = pd.DataFrame(last_preview_data)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="TaxRoll")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="TaxRoll_Output.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ================= CSV DOWNLOAD =================
@app.route("/download_csv")
def download_csv():
    global last_preview_data

    if not last_preview_data:
        return jsonify({
            "status": "error",
            "message": "No data available"
        })

    df = pd.DataFrame(last_preview_data)

    output = io.StringIO()
    df.to_csv(output, index=False)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        as_attachment=True,
        download_name="TaxRoll_Output.csv",
        mimetype="text/csv"
    )

# ================= HISTORY =================
@app.route("/history")
def history():
    return jsonify(run_history)

# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
