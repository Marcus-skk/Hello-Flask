from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    if request.method == "POST":
        email = request.form.get("email")
        tittel = request.form.get("tittel")
        melding = request.form.get("melding")
        tema = request.form.get("tema")
        tidspunkt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lagre data i fil
        with open("kontakter.txt", "a", encoding="utf-8") as f:
            f.write(f"{tidspunkt} | {email} | {tittel} | {tema} | {melding}\n")

        return f"Takk for din henvendelse, {email}! Vi vil svare på {tema} snart."

    return render_template("kontakt.html")

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
