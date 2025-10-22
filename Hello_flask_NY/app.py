from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = "superhemmeligkey"

# Koble til SQL Server med Windows Authentication
def get_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=DESKTOP-PSA04RL\\SQLEXPRESS;'
            'DATABASE=VG32526;'
            'Trusted_Connection=yes;'
        )
        return conn
    except pyodbc.Error as e:
        print("Feil ved tilkobling:", e)
        return None

# Flask-WTF form for kontaktskjema
class KontaktForm(FlaskForm):
    navn = StringField("Navn", validators=[DataRequired()])
    epost = StringField("Epost", validators=[DataRequired(), Email()])
    melding = TextAreaField("Melding", validators=[DataRequired()])
    submit = SubmitField("Send melding")

# Flask-WTF form for redigere status
class StatusForm(FlaskForm):
    status = SelectField("Status", choices=[("Ny", "Ny"), ("Under behandling", "Under behandling"), ("Ferdig", "Ferdig")])
    submit = SubmitField("Oppdater status")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    form = KontaktForm()
    if form.validate_on_submit():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Kontakter (Navn, Epost, Melding, Tid, Status)
                VALUES (?, ?, ?, ?, ?)
            """, form.navn.data, form.epost.data, form.melding.data, datetime.now(), "Ny")
            conn.commit()
            cursor.close()
            conn.close()
            flash("Meldingen er sendt!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Feil ved sending: {e}", "danger")
    return render_template("kontakt.html", form=form)

@app.route("/vis", methods=["GET"])
def vis():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT KontaktId, Navn, Epost, Melding, Tid, Status FROM Kontakter")
        kontakter = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("vis.html", kontakter=kontakter)
    except Exception as e:
        flash(f"Kunne ikke hente meldinger: {e}", "danger")
        return redirect(url_for("index"))

@app.route("/kommentar/<int:kontakt_id>", methods=["GET", "POST"])
def kommentar(kontakt_id):
    if request.method == "POST":
        innhold = request.form.get("kommentar")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Kommentarer (KontaktId, Melding, Tidspunkt)
                VALUES (?, ?, ?)
            """, kontakt_id, innhold, datetime.now())
            conn.commit()
            cursor.close()
            conn.close()
            flash("Kommentar lagt til!", "success")
        except Exception as e:
            flash(f"Kunne ikke legge til kommentar: {e}", "danger")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Melding, Tidspunkt FROM Kommentarer WHERE KontaktId = ? ORDER BY Tidspunkt DESC", kontakt_id)
        kommentarer = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("vis_kommentarer.html", kommentarer=kommentarer, kontakt_id=kontakt_id)
    except Exception as e:
        flash(f"Kunne ikke hente kommentarer: {e}", "danger")
        return redirect(url_for("vis"))

@app.route("/rediger_status/<int:kontakt_id>", methods=["GET", "POST"])
def rediger_status(kontakt_id):
    form = StatusForm()
    if form.validate_on_submit():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Kontakter SET Status = ? WHERE KontaktId = ?", form.status.data, kontakt_id)
            conn.commit()
            cursor.close()
            conn.close()
            flash("Status oppdatert!", "success")
            return redirect(url_for("vis"))
        except Exception as e:
            flash(f"Kunne ikke oppdatere status: {e}", "danger")
    return render_template("rediger_status.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
