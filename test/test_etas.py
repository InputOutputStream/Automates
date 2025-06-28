

from Etat import Etat
from Automate import Automate

# Création des états q0 à q7
q0 = Etat("q0", est_initial=True)
q1 = Etat("q1")
q2 = Etat("q2")
q3 = Etat("q3")
q4 = Etat("q4")
q5 = Etat("q5")
q6 = Etat("q6")
q7 = Etat("q7")

# Définir les états finaux
for e in [q1, q2, q3, q5, q6]:
    e.est_final = True

# Ensemble des états
etats = {q0, q1, q2, q3, q4, q5, q6, q7}

# Alphabet
alphabet = {"a", "b"}

# Création de l'automate
automate = Automate(
    alphabet=alphabet,
    etats=etats,
    etat_initial=q0,
    etats_finaux={e for e in etats if e.est_final}
)

# Lier chaque état à l'automate
for e in etats:
    e.automate = automate

# Définir les transitions
automate.ajouter_transition(q0, "a", q1)
automate.ajouter_transition(q0, "b", q4)

automate.ajouter_transition(q1, "a", q2)
automate.ajouter_transition(q1, "b", q3)

for sym in ["a", "b"]:
    automate.ajouter_transition(q2, sym, q7)

automate.ajouter_transition(q3, "a", q7)
automate.ajouter_transition(q3, "b", q3)

automate.ajouter_transition(q4, "a", q5)
automate.ajouter_transition(q4, "b", q6)

for sym in ["a", "b"]:
    automate.ajouter_transition(q5, sym, q7)

automate.ajouter_transition(q6, "a", q7)
automate.ajouter_transition(q6, "b", q6)

for sym in ["a", "b"]:
    automate.ajouter_transition(q7, sym, q7)

# === Tests ===
print("\n=== TEST DES ÉTATS ===")
for e in sorted(automate.etats, key=lambda x: x.nom):
    print(f"\n>>> État {e.nom}")
    print(f"  - Initial ? {e.est_initial}")
    print(f"  - Final ? {e.est_final}")
    print(f"  - Accessible ? {e.est_accessible()}")
    print(f"  - Coaccessible ? {e.est_coaccessible()}")
    print(f"  - Utile ? {e.est_utile()}")
    print(f"  - Chemin vers initial : {e.chemin_vers_initial()}")
    print(f"  - Chemin vers final : {e.chemin_vers_final()}")
    print(f"  - Atteignables : {e.etats_atteignables()}")
    print(f"  - Prédécesseurs : {e.etats_precedents()}")
    print(f"  - Émondé ? {e.est_emonde()}")

# === Résumé texte ===
print("\n=== RÉSUMÉ DE L'AUTOMATE ===")
print(automate.afficher())

