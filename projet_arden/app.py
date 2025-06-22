from flask import Flask, request
import dominate
from dominate.tags import div, form, input_, label, textarea, h1, h2, h3, p, style
from backend_solver import appliquer_lemmes_arden

app = Flask(__name__)

CSS_STYLE = """
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #ccdfff;
        color: #1a1a1a;
        margin: 0; padding: 0;
        display: flex;
        justify-content: center;
        min-height: 100vh;
    }
    .container {
        background: white;
        margin: 30px;
        padding: 30px 40px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0, 70, 170, 0.3);
        max-width: 800px;
        width: 100%;
        color: #1a1a1a;
    }
    h1, h2, h3 {
        font-weight: 700;
        margin-bottom: 15px;
        color: #003366;
        text-align: center;
    }
    .system-section, .result-section {
        margin-bottom: 40px;
        padding: 25px;
        border-radius: 12px;
        background-color: #ccdfff;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .input-block {
        background-color: #003366;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    .input-block label {
        color: white;
        font-weight: bold;
        display: block;
        margin-bottom: 10px;
    }
    input[type="text"], textarea {
        width: 100%;
        padding: 12px 14px;
        border: 2px solid #0059b3;
        border-radius: 10px;
        background-color: #dce8ff;
        font-size: 16px;
        margin-top: 5px;
        color: #000000;
    }
    .button-center {
        text-align: center;
    }
    input[type="submit"] {
        background-color: #004080;     /* Bleu foncé */
        color: #e6f0ff;               /* Blanc bleuté clair */
        border: none;
        padding: 14px 28px;
        font-size: 18px;
        border-radius: 12px;
        cursor: pointer;
        font-weight: 700;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 64, 128, 0.6);
        margin: 20px auto 0 auto;
        display: block;
        max-width: 220px;
        text-align: center;
    }
    input[type="submit"]:hover {
        background-color: #0059cc;
        box-shadow: 0 6px 12px rgba(0, 89, 204, 0.7);
    }
    .result {
        background: #003366;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: inset 0 0 12px #99bbff;
        white-space: pre-wrap;
        font-family: monospace;
        font-size: 16px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #f0f0f0;
    }
    .result-var {
        font-weight: 700;
        color: #ffffff;
        min-width: 40px;
        text-align: right;
    }
    .error-message {
        background-color: #ffcccc;
        color: #990000;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        font-weight: bold;
        text-align: center;
    }
"""

@app.route("/", methods=["GET", "POST"])
def index():
    doc = dominate.document(title="Résolution par le lemme d'Arden")
    with doc.head:
        style(CSS_STYLE)

    with doc:
        with div(cls="container"):
            h1("Système d'équations rationnelles")

            with div(cls="system-section"):
                with form(method="POST"):
                    with div(cls="input-block"):
                        label("Entrez les symboles de l'alphabet (ex: a b c):")
                        input_(type="text", name="alphabet", placeholder="a b c", required=True)

                    with div(cls="input-block"):
                        label("Entrez les équations (une par ligne, ex: X = aX + bY + e):")
                        textarea(name="equations", rows=6, placeholder="X = aX + bY + e\nY = aY + e", required=True)

                    with div(cls="button-center"):
                        input_(type="submit", value="Résoudre")

            if request.method == "POST":
                alphabet_input = request.form["alphabet"].strip().split()
                alphabet = set(alphabet_input)
                alphabet.add('e')

                lignes = request.form["equations"].strip().split("\n")
                systeme = []
                variables = set()

                for ligne in lignes:
                    if '=' in ligne:
                        var, expr = map(str.strip, ligne.split('=', 1))
                        variables.add(var)
                        expr = expr.replace(" ", "")
                        systeme.append((var, expr))

                # Appeler le solver, récupère aussi une erreur possible
                solutions, reste, erreur = appliquer_lemmes_arden(systeme, alphabet, variables)

                if erreur:
                    with div(cls="error-message"):
                        p(f"Erreur : {erreur}")
                else:
                    with div(cls="result-section"):
                        h2("Résultats")
                        for var in sorted(variables):
                            if var in solutions:
                                with div(cls="result"):
                                    div(var, cls="result-var")
                                    div(solutions[var])
                            else:
                                p(f"{var} : non résolu")

                        if reste:
                            h3("Équations non résolues :")
                            for var, expr in reste:
                                p(f"{var} = {expr}")

    return str(doc)

if __name__ == "__main__":
    app.run(debug=True)
