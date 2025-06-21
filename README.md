# 🤖 Projet Automates - Interface Web Interactive

Une interface web moderne pour manipuler et visualiser les automates finis, avec conversion d'expressions régulières et opérations avancées.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Reference](#-api-reference)
- [Développement](#-développement)
- [Contribution](#-contribution)
- [License](#-license)

## ✨ Fonctionnalités

### 🔄 Conversion d'expressions régulières
- Validation syntaxique des regex
- Conversion automatique en automate fini
- Visualisation du résultat

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
- Trace d'exécution détaillée
- Historique des tests

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
│       ├── ServeurLocal.py      # Serveur Flask
│       ├── APIHandler.py        # Gestionnaire API
│       ├── GestionnaireOperations.py # Logique métier
│       └── RegexParser.py       # Analyseur regex
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
# ou
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
→ Automate avec états q0, q1, q2...
```

#### Test d'acceptation
```
Automate: {"alphabet": ["a", "b"], "states": ["q0", "q1"], ...}
Mot: "abab"
→ Résultat: ACCEPTÉ/REJETÉ
```

#### Opérations binaires
```
Automate 1: {reconnaissance de "a*"}
Automate 2: {reconnaissance de "b*"}
Union → {reconnaissance de "a*|b*"}
```

## 📡 API Reference

### Endpoints disponibles

#### `POST /api/regex/convert`
Convertit une expression régulière en automate.

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
Applique une transformation à un automate.

**Paramètres:**
```json
{
  "automaton": {...},
  "operation": "determinize|minimize|complete|complement"
}
```

#### `POST /api/automaton/operations`
Effectue des opérations binaires sur automates.

**Paramètres:**
```json
{
  "automaton1": {...},
  "automaton2": {...},
  "operation": "union|intersection|concatenation"
}
```

#### `POST /api/automaton/test`
Teste l'acceptation d'un mot.

**Paramètres:**
```json
{
  "automaton": {...},
  "word": "abab"
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
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q2", "b": "q0"},
    "q2": {"a": "q2", "b": "q2"}
  }
}
```

## 🛠️ Développement

### Structure du code

```python
# Exemple d'utilisation des classes
from app.Automate import Automate
from app.Mot import Mot

# Créer un automate
automate = Automate(alphabet=['a', 'b'])
automate.ajouter_etat('q0', initial=True)
automate.ajouter_etat('q1', final=True)
automate.ajouter_transition('q0', 'a', 'q1')

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
   - Ajouter les méthodes dans les classes `app/`
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
git commit -m "feat: ajout de l'opération d'intersection d'automates

- Implémentation de l'algorithme d'intersection
- Tests unitaires pour tous les cas
- Documentation API mise à jour
- Interface web adaptée

Fixes #123"
```

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- **Développement Backend** : Classes Python pour automates
- **Développement Frontend** : Interface web moderne
- **API Design** : Endpoints RESTful
- **Tests & QA** : Couverture de tests complète

## 🔗 Liens utiles

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Théorie des automates](https://fr.wikipedia.org/wiki/Automate_fini)
- [Expressions régulières](https://regex101.com/)
- [JSON Schema](https://json-schema.org/)

---

**🚀 Prêt à explorer les automates ? Lancez `python main.py` et c'est parti !**