from Etat import Etat
from Automate import Automate

def lire_etats():
    nb = int(input("Nombre d'états : "))
    noms = [input(f"Nom de l'état {i+1} : ").strip() for i in range(nb)]
    return {Etat(n) for n in noms}

def lire_alphabet():
    return set(sym.strip() for sym in input("Alphabet (séparé par des virgules) : ").split(","))

def lire_etat_initial(etats_dict):
    while True:
        nom = input("Nom de l'état initial : ").strip()
        if nom in etats_dict:
            etat = etats_dict[nom]
            etat.est_initial = True
            return etat
        else:
            print("Nom incorrect. Réessaie.")

def lire_etats_finaux(etats_dict):
    noms = [n.strip() for n in input("États finaux (séparés par des virgules) : ").split(",")]
    finaux = set()
    for nom in noms:
        if nom in etats_dict:
            etats_dict[nom].est_final = True
            finaux.add(etats_dict[nom])
    return finaux

def lire_transitions(automate, etats_dict):
    n = int(input("Nombre de transitions : "))
    for i in range(n):
        print(f"Transition {i+1}")
        src = input("  État source : ").strip()
        symb = input("  Symbole(s) (ex: a ou a,b) : ").strip()
        dst = input("  État destination : ").strip()

        if src not in etats_dict or dst not in etats_dict:
            print("Erreur : État source ou destination invalide.")
            continue

        for sym in symb.split(","):
            sym = sym.strip()
            automate.ajouter_transition(etats_dict[src], sym, etats_dict[dst])

def test_etats(automate):
    print("\n=== Analyse des états ===")
    for e in automate.etats:
        print(f"\n>>> État {e.nom}")
        print(f"  - Accessible ? {e.est_accessible()}")
        print(f"  - Coaccessible ? {e.est_coaccessible()}")
        print(f"  - Utile ? {e.est_utile()}")
        print(f"  - Chemin vers initial : {e.chemin_vers_initial()}")
        print(f"  - Chemin vers final : {e.chemin_vers_final()}")
        print(f"  - États atteignables : {e.etats_atteignables()}")
        print(f"  - États précédents : {e.etats_precedents()}")
        print(f"  - Émondé ? {e.est_emonde()}")

if __name__ == "__main__":
    print("Création d'un automate (entrée utilisateur)")

    etats = lire_etats()
    etats_dict = {e.nom: e for e in etats}

    alphabet = lire_alphabet()
    etat_initial = lire_etat_initial(etats_dict)
    etats_finaux = lire_etats_finaux(etats_dict)

    automate = Automate(
        alphabet=alphabet,
        etats=etats,
        etat_initial=etat_initial,
        etats_finaux=etats_finaux
    )

    for e in etats:
        e.automate = automate

    lire_transitions(automate, etats_dict)

    print("\nRésumé de l'automate :")
    print(automate.afficher())

    test_etats(automate)

