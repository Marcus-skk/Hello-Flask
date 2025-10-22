from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email
from datetime import datetime

app = Flask(__name__)
app.secret_key = "superhemmelig"

class KontaktForm(FlaskForm):
    email = EmailField("E-post", validators=[DataRequired(), Email()])
    tittel = StringField("Tittel", validators=[DataRequired()])
    melding = TextAreaField("Melding", validators=[DataRequired()])
    tema = SelectField("Tema", choices=[
        ("Teknisk support", "Teknisk support"),
        ("Salg", "Salg"),
        ("Annen henvendelse", "Annen henvendelse")
    ], validators=[DataRequired()])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    form = KontaktForm()
    if form.validate_on_submit():
        email = form.email.data
        tittel = form.tittel.data
        melding = form.melding.data
        tema = form.tema.data
        tidspunkt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lagre til fil
        with open("kontakter.txt", "a", encoding="utf-8") as f:
            f.write(f"{tidspunkt} | {email} | {tittel} | {tema} | {melding}\n")

        flash(f"Takk for din henvendelse, {email}! Vi vil svare på {tema} snart.", "success")
        return redirect(url_for("kontakt"))

    return render_template("kontakt_wtf.html", form=form)

@app.route("/vis")
def vis():
    data = []
    try:
        with open("kontakter.txt", "r", encoding="utf-8") as f:
            for linje in f:
                deler = linje.strip().split(" | ")
                if len(deler) == 5:
                    data.append({
                        "tid": deler[0],
                        "email": deler[1],
                        "tittel": deler[2],
                        "tema": deler[3],
                        "melding": deler[4]
                    })
    except FileNotFoundError:
        pass

    return render_template("vis.html", kontakter=data)

if __name__ == "__main__":
    app.run(debug=True)
