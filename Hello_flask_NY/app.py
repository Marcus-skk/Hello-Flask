from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email
from datetime import datetime
import pyodbc

app = Flask(__name__)
app.secret_key = "superhemmelig"

# WTForms skjema for kontakt
class KontaktForm(FlaskForm):
    email = EmailField("E-post", validators=[DataRequired(), Email()])
    tittel = StringField("Tittel", validators=[DataRequired()])
    melding = TextAreaField("Melding", validators=[DataRequired()])
    tema = SelectField("Tema", choices=[
        ("Teknisk support", "Teknisk support"),
        ("Salg", "Salg"),
        ("Annen henvendelse", "Annen henvendelse")
    ], validators=[DataRequired()])

# WTForms skjema for kommentar
class KommentarForm(FlaskForm):
    melding = TextAreaField("Ny kommentar", validators=[DataRequired()])

# Koble til SQL Server
def get_connection():
    server = 'DESKTOP-PSA04RL\\SQLEXPRESS'
    database = 'VG32526'
    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )
    return cnxn

# Hovedside
@app.route("/")
def home():
    return render_template("index.html")

# Kontakt-side
@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    form = KontaktForm()
    if form.validate_on_submit():
        email = form.email.data
        tittel = form.tittel.data
        melding = form.melding.data
        tema = form.tema.data
        tidspunkt = datetime.now()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Kontakter (Tidspunkt, Email, Tittel, Tema, Melding, Status) VALUES (?, ?, ?, ?, ?, ?)",
            tidspunkt, email, tittel, tema, melding, "Åpen"
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Takk for din henvendelse, {email}! Vi vil svare på {tema} snart.", "success")
        return redirect(url_for("kontakt"))

    return render_template("kontakt_wtf.html", form=form)

# Vis meldinger med status og kommentarer
@app.route("/vis", methods=["GET", "POST"])
def vis():
    conn = get_connection()
    cursor = conn.cursor()

    # Håndter statusendring
    if request.method == "POST" and "status" in request.form:
        melding_id = request.form.get("melding_id")
        ny_status = request.form.get("status")
        if melding_id and ny_status:
            cursor.execute("UPDATE Kontakter SET Status = ? WHERE Id = ?", ny_status, melding_id)
            conn.commit()
            flash(f"Status oppdatert til {ny_status}", "success")

    # Håndter nye kommentarer
    if request.method == "POST" and "ny_kommentar" in request.form:
        kontakt_id = request.form.get("kontakt_id")
        ny_kommentar = request.form.get("ny_kommentar")
        if kontakt_id and ny_kommentar:
            cursor.execute(
                "INSERT INTO Kommentarer (KontaktId, Melding) VALUES (?, ?)",
                kontakt_id, ny_kommentar
            )
            conn.commit()
            flash("Ny kommentar lagt til!", "success")

    # Hent kontakter
    cursor.execute("SELECT Id, Tidspunkt, Email, Tittel, Tema, Melding, Status FROM Kontakter ORDER BY Tidspunkt DESC")
    kontakter = []
    for row in cursor.fetchall():
        kontakt = {"id": row[0], "tid": row[1], "email": row[2], "tittel": row[3],
                   "tema": row[4], "melding": row[5], "status": row[6]}

        # Hent kommentarer for denne kontakten
        cursor.execute("SELECT Tidspunkt, Melding FROM Kommentarer WHERE KontaktId = ? ORDER BY Tidspunkt ASC", row[0])
        kontakt["kommentarer"] = [{"tid": k[0], "melding": k[1]} for k in cursor.fetchall()]

        kontakter.append(kontakt)

    cursor.close()
    conn.close()
    return render_template("vis_kommentarer.html", kontakter=kontakter)

if __name__ == "__main__":
    app.run(debug=True)
