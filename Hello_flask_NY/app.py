from flask import Flask, render_template, request

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

        # Midlertidig respons
        return f"Takk for din henvendelse, {email}! Vi vil svare på {tema} snart."

    return render_template("kontakt.html")

if __name__ == "__main__":
    app.run(debug=True)
