from automates1 import Automate
from alpha import *

def menu():
    print("\n=== MENU PRINCIPAL ===")
    print("1. Créer un nouvel automate")
    print("2. Ajouter un état")
    print("3. Définir l’état initial")
    print("4. Ajouter un état final")
    print("5. Rendre un état normal")
    print("6. Supprimer un état")
    print("7. Ajouter une transition")
    print("8. Afficher l’automate courant")
    print("9. Tester la reconnaissance d’un mot")
    print("10. Tester si déterministe et complet")
    print("11. Lister tous les automates créés")
    print("0. Quitter")

def main():
    automates = {}
    courant = None

    print("=== Configuration de l'alphabet ===")
    alphabet = choisir_alphabet()

    while True:
        menu()
        choix = input("Choix : ").strip()

        if choix == '1':
            nom = input("Nom de l'automate : ").strip()
            courant = Automate(alphabet)
            automates[nom] = courant
            print(f"Automate '{nom}' créé et sélectionné.")

        elif choix == '2' and courant:
            etat = input("Nom de l’état à ajouter : ").strip()
            courant.ajouter_etat(etat)

        elif choix == '3' and courant:
            etat = input("Nom de l’état initial : ").strip()
            courant.definir_etat_initial(etat)

        elif choix == '4' and courant:
            etat = input("Nom de l’état final : ").strip()
            courant.ajouter_etat_final(etat)

        elif choix == '5' and courant:
            etat = input("Nom de l’état à rendre normal : ").strip()
            courant.rendre_etat_normal(etat)

        elif choix == '6' and courant:
            etat = input("Nom de l’état à supprimer : ").strip()
            courant.supprimer_etat(etat)

        elif choix == '7' and courant:
            source = input("État source : ").strip()
            symbole = input("Symbole de transition : ").strip()
            cible = input("État cible : ").strip()
            courant.ajouter_transition(source, symbole, cible)

        elif choix == '8' and courant:
            print(courant.afficher())

        elif choix == '9' and courant:
            mot = input("Mot à tester : ").strip()
            print(f"Reconnu ? {courant.reconnaitre_mot(mot)}")

        elif choix == '10' and courant:
            print(f"Déterministe ? {courant.est_deterministe()}")
            print(f"Complet ? {courant.est_complet()}")

        elif choix == '11':
            print("Automates disponibles :")
            for nom in automates:
                print(f"- {nom}")

        elif choix == '0':
            print("Au revoir !")
            break

        else:
            print("Option invalide ou aucun automate sélectionné.")

if __name__ == "__main__":
    main()
