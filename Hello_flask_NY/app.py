from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email
from datetime import datetime
import pyodbc

app = Flask(__name__)
app.secret_key = "superhemmelig"  # Trenger for CSRF

# WTForms skjema
class KontaktForm(FlaskForm):
    email = EmailField("E-post", validators=[DataRequired(), Email()])
    tittel = StringField("Tittel", validators=[DataRequired()])
    melding = TextAreaField("Melding", validators=[DataRequired()])
    tema = SelectField("Tema", choices=[
        ("Teknisk support", "Teknisk support"),
        ("Salg", "Salg"),
        ("Annen henvendelse", "Annen henvendelse")
    ], validators=[DataRequired()])

# Koble til SQL Server med Windows Authentication
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

# Kontakt-side med WTForms
@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    form = KontaktForm()
    if form.validate_on_submit():
        email = form.email.data
        tittel = form.tittel.data
        melding = form.melding.data
        tema = form.tema.data
        tidspunkt = datetime.now()

        # Sett inn i SQL Server
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Kontakter (Tidspunkt, Email, Tittel, Tema, Melding) VALUES (?, ?, ?, ?, ?)",
            tidspunkt, email, tittel, tema, melding
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Takk for din henvendelse, {email}! Vi vil svare på {tema} snart.", "success")
        return redirect(url_for("kontakt"))

    return render_template("kontakt_wtf.html", form=form)

# Vis innsendte meldinger
@app.route("/vis")
def vis():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Tidspunkt, Email, Tittel, Tema, Melding FROM Kontakter ORDER BY Tidspunkt DESC")
    data = [
        {"tid": row[0], "email": row[1], "tittel": row[2], "tema": row[3], "melding": row[4]}
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return render_template("vis.html", kontakter=data)

if __name__ == "__main__":
    app.run(debug=True)
