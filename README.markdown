# 🤖 Projet Automates - Interface Web Interactive

Une interface web moderne pour manipuler, visualiser et analyser les automates finis, avec conversion d'expressions régulières, opérations avancées, et analyse des monoïdes.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Fonctionnement de l'application](#-fonctionnement-de-lapplication)
- [API Reference](#-api-reference)
- [Développement](#-développement)
- [Dépannage](#-dépannage)
- [Contribution](#-contribution)
- [License](#-license)
- [Équipe](#-équipe)
- [Liens utiles](#-liens-utiles)

## ✨ Fonctionnalités

### 🔄 Conversion d'expressions régulières
- Validation syntaxique des regex
- Conversion automatique en automate fini non déterministe (NFA)
- Visualisation graphique interactive

### 🔧 Transformations d'automates
- **Déterminisation** : Conversion NFA → DFA
- **Minimisation** : Réduction du nombre d'états
- **Complétion** : Ajout d'états puits
- **Complémentation** : Inversion des états finaux

### ⚡ Opérations sur automates
- **Union** : A₁ ∪ A₂
- **Intersection** : A₁ ∩ A₂
- **Concaténation** : A₁ · A₂
- **Étoile de Kleene** : A*
- **Comparaison** : Équivalence et inclusion

### 🧪 Test d'acceptation
- Vérification si un mot est accepté
- Trace d'exécution animée
- Historique des tests

### 🔍 Analyse avancée
- Analyse des états : Accessibilité, coaccessibilité, utilité, émondage
- Visualisation des chemins vers initial/final
- Identification des états atteignables/précédents
- Création d'automates à partir de matrices
- Analyse des monoïdes : Validation de l'élément neutre, construction de sous-monoïdes

## 🏗️ Architecture

```
Automates/
├── app/                          # Backend Python
│   ├── Automate.py              # Classe principale Automate
│   ├── Etat.py                  # Gestion des états
│   ├── Langage.py               # Opérations sur langages
│   ├── LangageReconnaissable.py # Langages reconnaissables
│   ├── Monoids.py               # Structures algébriques
│   ├── Mot.py                   # Manipulation de mots
│   └── front/                   # Interface web
│       ├── serveur.py      # Serveur Flask
│       ├── GestionnaireOperations.py # Logique métier
│       ├── RegexParser.py       # Analyseur regex
├── index.html                   # Interface utilisateur
├── index.css                    # Styles CSS
├── index.js                     # Logique frontend
├── main.py                      # Point d'entrée
└── requirements.txt             # Dépendances Python
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Navigateur web moderne

### Installation rapide

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd Automates

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

### Installation détaillée

```bash
# Vérifier la version Python
python --version

# Créer l'environnement virtuel
python -m venv python
source python/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install flask flask-cors

# Optionnel : Installer les dépendances de développement
pip install pytest black flake8
```

## 🎯 Utilisation

### Démarrage rapide

1. **Lancer le serveur**
   ```bash
   python main.py
   ```

2. **Ouvrir l'interface web**
   - Naviguer vers `http://localhost:5000`
   - L'interface est prête à utiliser !

### Exemples d'utilisation

#### Conversion d'une regex
```
Regex: (a|b)*
→ Automate avec états q0, q1, boucles sur a et b
```

#### Test d'acceptation
```
Automate: {"alphabet": ["a", "b"], "states": ["q0", "q1"], ...}
Mot: "abab"
→ Résultat: ACCEPTÉ avec trace animée
```

#### Création depuis une matrice
```
Matrice: [[[0], [1]], [[1], [0]]]
Alphabet: a,b
→ Automate avec q0 initial, q1 final
```

## 🖥️ Fonctionnement de l'application

L'application permet de créer, manipuler, tester et analyser des automates finis et des monoïdes via une interface web intuitive. Voici les principales fonctionnalités, les champs d'entrée et les résultats attendus.

### 🔄 Conversion d'expressions régulières
- **Où** : Onglet "Regex"
- **Entrées** :
  - **Expression régulière** : Texte (ex. `(a|b)*`, `a*b`, `ab|c`)
    - Syntaxe : Lettres (a-z), `|` (union), `*` (étoile), `.` (concaténation implicite), parenthèses
    - Valide : `(a|b)*abb`
    - Invalide : `a**`, `(ab`
- **Action** : Cliquer sur "Convertir"
- **Résultat** :
  - Graphe de l'automate (états en cercles, transitions en flèches)
  - État initial (flèche entrante), états finaux (double cercle)
  - Ex. `(a|b)*` : Automate avec boucles `a`, `b` sur un état initial/final
  - Erreur si regex invalide (ex. "Parenthèse non fermée")

### 🔨 Création d'automates
- **Où** : Onglet "Créer Automate"
- **Entrées** :
  - **Manuellement** :
    - **Alphabet** : Symboles séparés par virgules (ex. `a,b`)
    - **États** : Noms d'états (ex. `q0,q1,q2`)
    - **État initial** : Un état (ex. `q0`)
    - **États finaux** : Liste d'états (ex. `q1,q2`)
    - **Transitions** : `état,symbole,destination` (ex. `q0,a,q1`)
  - **Depuis une matrice** :
    - **Matrice** : JSON (ex. `[[[0], [1]], [[1], [0]]]`)
      - Ligne = état, colonne = symbole, valeur = indices destinations
    - **Alphabet** (optionnel) : Symboles (ex. `a,b`), sinon `a,b,...`
- **Action** : Cliquer sur "Créer"
- **Résultat** :
  - Graphe de l'automate
  - Matrice : `q0` initial, dernier état final (par défaut)
  - Erreur si entrées invalides (ex. état inconnu dans transition)

### 🔧 Transformations d'automates
- **Où** : Onglet "Transformations"
- **Entrées** :
  - **Automate** : Sélection via menu déroulant
  - **Opération** : Déterminisation, Minimisation, Complétion, Complémentation
- **Action** : Cliquer sur "Appliquer"
- **Résultat** :
  - Nouvel automate affiché
  - Ex. :
    - **Déterminisation** : NFA → DFA, supprime transitions ε
    - **Minimisation** : Moins d'états, même langage
    - **Complétion** : Ajoute état puits
    - **Complémentation** : Inverse états finaux

### ⚡ Opérations sur automates
- **Où** : Onglet "Opérations"
- **Entrées** :
  - **Automate 1** : Sélection d'un automate
  - **Automate 2** : Second automate (sauf pour Étoile)
  - **Opération** : Union, Intersection, Concaténation, Étoile, Comparaison
- **Action** : Cliquer sur "Exécuter"
- **Résultat** :
  - Nouvel automate pour Union, Intersection, Concaténation, Étoile
  - Comparaison : Message d'équivalence/inclusion
  - Ex. : Union de `a*` et `b*` → Automate pour `a*|b*`

### 🧪 Test d'acceptation
- **Où** : Onglet "Tester Mot"
- **Entrées** :
  - **Automate** : Sélection d'un automate
  - **Mot** : Texte (ex. `abab`)
    - Symboles doivent être dans l'alphabet
- **Action** : Cliquer sur "Tester"
- **Résultat** :
  - "ACCEPTÉ" ou "REJETÉ"
  - Animation des transitions dans le graphe
  - Historique dans panneau latéral
  - Ex. : `(ab)*`, mot `abab` → ACCEPTÉ

### 🔍 Analyse des automates
- **Où** : Onglet "Analyse"
- **Entrées** :
  - **Automate** : Sélection d'un automate
  - **État** (optionnel) : État spécifique
- **Action** : Cliquer sur "Analyser"
- **Résultat** :
  - Pour chaque état :
    - Accessible : Oui/Non
    - Coaccessible : Oui/Non
    - Utile : Oui/Non
    - Émondé : Oui/Non
    - États atteignables : Liste
    - Prédécesseurs : Liste
    - Chemin vers initial/final : Liste de symboles
  - Visualisation : États colorés (vert=utile, rouge=non accessible)
  - Ex. : `q1` : Accessible=True, Chemin vers initial=[a]

### 📊 Analyse des monoïdes
- **Où** : Onglet "Monoïdes"
- **Entrées** :
  - **Ensemble** : Éléments séparés par virgules (ex. `0,1,2`)
  - **Opération** : Prédéfinie (ex. addition modulo 3) ou personnalisée
  - **Élément neutre** : Élément (ex. `0`)
  - **Sous-ensemble** (optionnel) : Éléments (ex. `0,1`)
- **Action** : Cliquer sur "Vérifier"
- **Résultat** :
  - Neutre : "Valide" ou "Invalide" (ex. "0 * 1 ≠ 1")
  - Sous-monoïde : Valide si fermé et contient neutre
  - Ex. : `{0,1,2}`, addition modulo 3, neutre=0 → Valide

### 💾 Exportation/Importation
- **Où** : Boutons "Exporter"/"Importer" dans la barre d'outils
- **Entrées** :
  - **Exporter** : Automate actuel
  - **Importer** : Fichier JSON ou texte (automate/matrice)
- **Action** : Cliquer sur les boutons
- **Résultat** :
  - Export : Fichier JSON avec automate
  - Import : Automate chargé et affiché
  - Ex. JSON :
    ```json
    {
      "alphabet": ["a", "b"],
      "states": ["q0", "q1"],
      "startState": "q0",
      "finalStates": ["q1"],
      "transitions": {"q0": {"a": ["q1"], "b": ["q0"]}, ...}
    }
    ```

## 📡 API Reference

### Endpoints disponibles

#### `POST /api/regex/convert`
Convertit une regex en automate.

**Paramètres:**
```json
{
  "regex": "(a|b)*"
}
```

**Réponse:**
```json
{
  "success": true,
  "data": {
    "alphabet": ["a", "b"],
    "states": ["q0", "q1"],
    "startState": "q0",
    "finalStates": ["q1"],
    "transitions": {...}
  }
}
```

#### `POST /api/automaton/transform`
Applique une transformation.

**Paramètres:**
```json
{
  "automaton": {...},
  "operation": "determinize|minimize|complete|complement"
}
```

#### `POST /api/automaton/operations`
Effectue une opération binaire.

**Paramètres:**
```json
{
  "automaton1": {...},
  "automaton2": {...},
  "operation": "union|intersection|concatenation|kleene|comparison"
}
```

#### `POST /api/automaton/test`
Teste un mot.

**Paramètres:**
```json
{
  "automaton": {...},
  "word": "abab"
}
```

#### `POST /api/automaton/from_matrix`
Crée un automate depuis une matrice.

**Paramètres:**
```json
{
  "matrix": [[[0], [1]], [[1], [0]]],
  "alphabet": ["a", "b"]
}
```

#### `POST /api/automaton/analyze`
Analyse les états.

**Paramètres:**
```json
{
  "automaton": {...},
  "state": "q1"
}
```

**Réponse:**
```json
{
  "states": {
    "q1": {
      "accessible": true,
      "coaccessible": false,
      "useful": false,
      "reachable": ["q2"],
      "predecessors": ["q0"],
      "path_to_initial": ["a"],
      "path_to_final": ["b"],
      "is_pruned": false
    }
  }
}
```

#### `POST /api/monoid/analyze`
Analyse un monoïde.

**Paramètres:**
```json
{
  "ensemble": ["0", "1", "2"],
  "operation": "addition_mod_3",
  "neutral": "0",
  "subset": ["0", "1"]
}
```

**Réponse:**
```json
{
  "neutral_valid": true,
  "submonoid_valid": true,
  "submonoid": ["0", "1"]
}
```

### Format des automates JSON

```json
{
  "alphabet": ["a", "b"],
  "states": ["q0", "q1", "q2"],
  "startState": "q0",
  "finalStates": ["q2"],
  "transitions": {
    "q0": {"a": ["q1"], "b": ["q0"]},
    "q1": {"a": ["q2"], "b": ["q0"]},
    "q2": {"a": ["q2"], "b": ["q2"]}
  }
}
```

## 🛠️ Développement

### Structure du code

```python
from app.Automate import Automate
from app.Mot import Mot

# Créer un automate
automate = Automate(alphabet=['a', 'b'])
automate.ajouter_etat('q0', initial=True)
automate.ajouter_etat('q1', final=True)
automate.ajouter_transition('q0', 'a', 'q1')

# Analyser un état
print(f"q0 accessible: {automate.etats[0].est_accessible()}")  # True

# Tester un mot
mot = Mot('a')
resultat = automate.accepte(mot)
print(f"Le mot '{mot}' est {'accepté' if resultat else 'rejeté'}")
```

### Tests

```bash
# Lancer les tests
python -m pytest tests/

# Tests avec couverture
python -m pytest --cov=app tests/

# Tests spécifiques
python -m pytest tests/test_automate.py::test_determinisation
```

### Formatage du code

```bash
# Formatter avec Black
black app/ tests/

# Vérifier le style avec flake8
flake8 app/ tests/

# Type checking avec mypy
mypy app/
```

### Ajout de nouvelles fonctionnalités

1. **Backend (Python)**
   - Ajouter les méthodes dans `app/`
   - Créer les endpoints dans `app/front/ServeurLocal.py`
   - Ajouter les tests correspondants

2. **Frontend (JavaScript)**
   - Ajouter les fonctions dans `index.js`
   - Mettre à jour l'interface dans `index.html`
   - Styliser avec `index.css`

## 🐛 Dépannage

### Problèmes courants

#### Le serveur ne démarre pas
```bash
# Vérifier le port
lsof -ti:5000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :5000   # Windows

# Changer le port
export PORT=8080
python main.py
```

#### Erreurs d'import
```bash
# Vérifier PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

#### L'interface ne se charge pas
```bash
# Vérifier les fichiers statiques
ls -la index.html index.css index.js

# Serveur de test simple
python -m http.server 8000
```

### Logs et debug

```python
# Activer les logs détaillés
import logging
logging.basicConfig(level=logging.DEBUG)

# Dans main.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🤝 Contribution

### Guidelines

1. **Fork** le projet
2. Créer une **branche** pour votre fonctionnalité
3. **Commiter** vos changements
4. **Pousser** vers la branche
5. Ouvrir une **Pull Request**

### Standards de code

- Suivre **PEP8** pour Python
- Utiliser **JSDoc** pour JavaScript
- Ajouter des **tests** pour toute nouvelle fonctionnalité
- Documenter les **API** endpoints

### Exemple de commit

```bash
git commit -m "feat: ajout analyse avancée des automates

- Implémentation de est_accessible, chemin_vers_initial, etc.
- Nouvel endpoint /api/automaton/analyze
- Tests unitaires pour les nouvelles méthodes
- Interface web avec visualisation des propriétés

Fixes #125"
```

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- **Développement Backend** : Classes Python pour automates et monoïdes
- **Développement Frontend** : Interface web interactive avec visualisations
- **API Design** : Endpoints RESTful
- **Tests & QA** : Couverture de tests complète

## 🔗 Liens utiles

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Théorie des automates](https://fr.wikipedia.org/wiki/Automate_fini)
- [Expressions régulières](https://regex101.com/)
- [JSON Schema](https://json-schema.org/)

---

**🚀 Prêt à explorer les automates ? Lancez `python main.py` et plongez dans l'univers des langages formels !**
