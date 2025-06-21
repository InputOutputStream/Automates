# Démonstration d'Automates

Une application web intuitive pour manipuler et visualiser des **automates finis**.

Construite avec :
- **Flask** pour le backend
- **Dominate** pour générer l'interface HTML
- **Tailwind CSS** pour le style
- **Cytoscape.js** pour la visualisation graphique

Fonctionnalités principales :
- Tester des mots
- Ajouter des états et transitions
- Exporter des automates en JSON
- Visualiser le parcours de reconnaissance avec animations fluides

---

## 🧰 Prérequis

- Python 3.8+
- Navigateur web moderne (Chrome, Firefox, Edge, etc.)
- Accès Internet pour charger Tailwind CSS via CDN *(ou configurez une version locale)*
- Un fichier `favicon.ico`

---

## ⚙️ Installation

1. **Clonez le projet :**

```bash
git clone https://github.com/InputOutputStream/Automates.git
cd app
```
2. **Installez les dépendances :**

```bash
pip install -r requirements.txt
```

3. **Vérifiez la structure des dossiers :**

``` arduino
app/
├── Automate.py
├── Etat.py
├── Mot.py
├── Langage.py
├── LangageReconnaissable.py
├── Monoids.py
├── app.py
├── front/
│   ├── templates/
│   │   ├── base.py
│   │   ├── main.py
│   │   └── results.py
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css
│   │   ├── js/
│   │       ├── cytoscape.min.js
│   │       └── main.js
├── requirements.txt
```
4. **Lancez l'application :**

``` bash
python app.py
```

5. **Accédez à l’application :**
http://127.0.0.1:8080

🗂️ Structure du projet
app.py : Point d’entrée Flask. Définit les routes.

front/templates/ :

base.py : Template général avec navbar, footer et modale.

main.py : Page principale (graphe, formulaires).

results.py : Affichage des messages.

front/static/ :

css/custom.css : Styles personnalisés.

js/cytoscape.min.js : Librairie de graphes.

js/main.js : Interactions frontend.

Fichiers métier :

Automate.py, Etat.py, Mot.py, Langage.py, etc.

🚀 Utilisation
1. Lancer l’application
Ouvrez http://127.0.0.1:8080 dans votre navigateur.

2. Interface
Navbar : Titre, bouton d’aide, thème clair/sombre

Sidebar : Ajouter états/transitions, exporter en JSON

Zone principale :

Gauche : Graphe interactif

Droite : Formulaire pour tester un mot et voir les propriétés

🧪 Actions disponibles
Tester un mot
Saisir un mot (ex: aba) → Tester
→ Animation du parcours et modale de résultat

Ajouter un état
Entrer un nom (ex: q3) → Valider

Ajouter une transition
Entrer État source, Symbole, État destination → Valider

Exporter en JSON
Cliquer sur Exporter en JSON → Fichier automate_export.json

Changer de thème
Utilisez le sélecteur dans la navbar (Clair / Sombre)

✨ Fonctionnalités
Visualisation graphique : Graphe interactif via Cytoscape.js

Test de mots : Vérification avec animation dynamique

Ajout dynamique : États et transitions

Export JSON : Sauvegarde et réutilisation

Informations utiles : Alphabet, états, déterminisme, etc.

Thèmes visuels : Clair / Sombre

Animations fluides :

Transitions CSS

Apparition des modales

Animation de parcours (surlignage progressif)

🧩 Dépannage
Erreur lors du test de mot :

Vérifiez que le mot contient uniquement des symboles de l'alphabet (par défaut a, b)

L’application ne démarre pas :

Assurez-vous que toutes les dépendances sont installées :

bash
Copier
Modifier
pip install -r requirements.txt