# Automates
Implementations des opérations de base des automates en python

# Automate Simulator

# Description
Automate Interfaces est une application graphique permettant de créer, visualiser et tester des automates finis. L'interface utilisateur, développée avec CustomTkinter, offre trois zones principales :

    - Zone de saisie : Pour définir un automate (exemple prédéfini ou manuel) et entrer des mots à tester.
    - Zone de visualisation : Pour afficher la représentation textuelle et graphique (via Turtle) de l'automate, ainsi que les résultats des tests.
    - Zone de résultats : Pour afficher les propriétés de l'automate (déterminisme, complétude) et l'historique des opérations.

Le projet est structuré en deux modules principaux :

    - back/ : Contient la logique métier (classes Automate, Etat, Mot, Langage).
    - front/ : Contient l'interface graphique et les visualisations.
    - interfaces/ : Contient toutes les class abstraites des interfaces

# Prérequis-requis
    Système d'exploitation : Windows/Linux (testé sur Windows 10/11)
    Python : Version 3.13
    Git : Pour cloner le dépôt
    VS code

# Installation
Suivez ces étapes pour cloner, configurer et exécuter le projet.

1. Cloner le dépôt
```git clone https://github.com/InputOutputStream/Automates.git
    cd Automates
```

2. Installer les dépendances

``` sudo apt install python3
    python3 install pip
    pip install customtkinter
    pip install Pillow
```
3. Exécuter le projet
    Depuis la racine du projet (dossier Automate), faire :
    ```    python3 main.py
    ```
    Une fenêtre graphique devrait s'ouvrir avec :

    - Une zone de saisie à gauche avec un bouton "Créer Exemple" et un champ pour entrer des mots à tester.
    - Une zone de visualisation en haut avec un textbox, des boutons "Effacer" et "Exporter Image", et une fenêtre Turtle pour la visualisation graphique.
    - Une zone de résultats en bas avec des onglets pour les propriétés, tests et transformations.

5. Utilisation
    * Créer un automate :
        Cliquez sur "Créer Exemple" dans la zone de saisie pour générer un automate prédéfini (reconnaît les mots se terminant par 'a' sur l'alphabet {a, b}).
    * Tester des mots :
        Entrez des mots séparés par des virgules dans le champ de saisie (par défaut : "a, ba, bba").
        Les résultats des tests (accepté/rejeté) s’affichent dans la zone de visualisation.
    * Visualiser l’automate :
        La représentation textuelle de l’automate apparaît dans le textbox de la zone de visualisation.
        Une représentation graphique (états et transitions) est dessinée dans la fenêtre Turtle.
    * Exporter une image :
        Cliquez sur "Exporter Image" pour sauvegarder la visualisation Turtle au format PostScript (automate.ps).
        (Avec Pillow) : Support pour PNG/JPEG possible.
    * Effacer :
        Cliquez sur "Effacer" pour vider le textbox de la zone de visualisation.

