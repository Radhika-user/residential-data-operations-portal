from flask import Flask, render_template, request, redirect, url_for, session, send_file
from db import get_csdb_connection, get_taxroll_connection
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = "secret123"


# 🔐 Fixed user
USER = {
    "username": "karthik.padmanathan",
    "password": "Data@123"
}


# 🔑 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            request.form.get("username") == USER["username"]
            and request.form.get("password") == USER["password"]
        ):
            session["user"] = USER["username"]
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# 📊 DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    results = []
    columns = []

    # ▶ STORED PROCEDURE
    if request.method == "POST" and request.form.get("action") == "run_sp":
        try:
            sp_map = {
                "sp_UpdateResidentialData_CAD": "EXEC dbo.sp_UpdateResidentialData_CAD",
                "Send_CommercialSales_Core_Report": "EXEC Send_CommercialSales_Core_Report",
                "Send_CommercialSales_NonCore_Report": "EXEC Send_CommercialSales_NonCore_Report",
                "usp_Load_Clickhouse_Sales": "EXEC dbo.usp_Load_Clickhouse_Sales"
            }

            selected_sp = request.form.get("sp_name")

            if selected_sp not in sp_map:
                raise Exception("Invalid Stored Procedure")

            conn = get_csdb_connection()
            cursor = conn.cursor()

            cursor.execute(sp_map[selected_sp])
            conn.commit()

            cursor.close()
            conn.close()

            results = [["Stored Procedure Executed Successfully"]]

        except Exception as e:
            results = [[str(e)]]

    # 🔍 PREVIEW
    if request.method == "POST" and request.form.get("action") == "preview":
        try:
            conn = get_taxroll_connection()
            cursor = conn.cursor()

            cad = request.form.get("cad")
            address = request.form.get("address")
            parcel = request.form.get("parcel")
            cadid = request.form.get("cadid")

            query = "SELECT * FROM TaxRoll_2026 WHERE 1=1"
            params = []

            if cad:
                cad_list = [x.strip() for x in cad.replace("\n", ",").split(",") if x.strip()]
                if cad_list:
                    placeholders = ",".join(["?"] * len(cad_list))
                    query += f" AND AccountNumber IN ({placeholders})"
                    params.extend(cad_list)

            if address:
                query += " AND PropertyAddress LIKE ?"
                params.append(f"%{address}%")

            if parcel:
                query += " AND ParcelID LIKE ?"
                params.append(f"%{parcel}%")

            if cadid:
                query += " AND CADID LIKE ?"
                params.append(f"%{cadid}%")

            cursor.execute(query, params)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            results = [list(row) for row in rows]

            cursor.close()
            conn.close()

        except Exception as e:
            results = [[str(e)]]

    return render_template("index.html", results=results, columns=columns)


# 📥 DOWNLOAD EXCEL
@app.route("/download_excel", methods=["POST"])
def download_excel():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_taxroll_connection()
        cursor = conn.cursor()

        cad = request.form.get("cad")
        address = request.form.get("address")
        parcel = request.form.get("parcel")
        cadid = request.form.get("cadid")

        query = "SELECT * FROM TaxRoll_2026 WHERE 1=1"
        params = []

        if cad:
            cad_list = [x.strip() for x in cad.replace("\n", ",").split(",") if x.strip()]
            if cad_list:
                placeholders = ",".join(["?"] * len(cad_list))
                query += f" AND AccountNumber IN ({placeholders})"
                params.extend(cad_list)

        if address:
            query += " AND PropertyAddress LIKE ?"
            params.append(f"%{address}%")

        if parcel:
            query += " AND ParcelID LIKE ?"
            params.append(f"%{parcel}%")

        if cadid:
            query += " AND CADID LIKE ?"
            params.append(f"%{cadid}%")

        cursor.execute(query, params)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        df = pd.DataFrame.from_records(rows, columns=columns)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)

        output.seek(0)

        cursor.close()
        conn.close()

        return send_file(
            output,
            download_name="TaxRoll_2026.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return str(e)


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
