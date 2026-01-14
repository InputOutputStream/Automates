ALPHABETS_PREDEFINIS = {
    "lettres": set("abcdefghijklmnopqrstuvwxyz"),
    "chiffres": set("0123456789"),
    "lettres_majuscules": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "lettres_et_chiffres": set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
}


def choisir_alphabet() -> set:
    import copy

    # On travaille sur une copie pour laisser les prédéfinis intacts
    alphabets_user = copy.deepcopy(ALPHABETS_PREDEFINIS)

    while True:
        print("\nAlphabets prédéfinis et personnalisés disponibles :")
        for idx, nom in enumerate(alphabets_user):
            print(f"  {idx + 1}. {nom} : {''.join(sorted(alphabets_user[nom]))}")
        
        print("""
Options :
  1 - Choisir un ou plusieurs alphabets existants
  2 - Créer un nouvel alphabet
  3 - Combiner des alphabets
  4 - Modifier un alphabet (ajouter/retirer des symboles)
  5 - Valider et utiliser l'alphabet choisi
""")
        choix = input("Votre choix : ")

        if choix == "1":
            selection = input("Saisir les numéros des alphabets à utiliser, séparés par des virgules : ")
            indices = [int(i.strip()) - 1 for i in selection.split(",")]
            alphabet_final = set()
            noms = list(alphabets_user.keys())
            for idx in indices:
                alphabet_final.update(alphabets_user[noms[idx]])
            print(f"\nAlphabet résultant : {''.join(sorted(alphabet_final))}")
            confirmation = input("Confirmer cet alphabet ? (o/n) : ")
            if confirmation.lower() == "o":
                return alphabet_final

        elif choix == "2":
            nom_nouvel_alpha = input("Nom de ce nouvel alphabet : ")
            contenu = input("Entrez les symboles de l'alphabet sans séparateurs : ")
            alphabets_user[nom_nouvel_alpha] = set(contenu)
            print(f"Nouvel alphabet '{nom_nouvel_alpha}' ajouté.")

        elif choix == "3":
            selection = input("Saisir les numéros des alphabets à combiner, séparés par des virgules : ")
            indices = [int(i.strip()) - 1 for i in selection.split(",")]
            noms = list(alphabets_user.keys())
            nouveau_alpha = set()
            for idx in indices:
                nouveau_alpha.update(alphabets_user[noms[idx]])
            nom_combinaison = input("Nom de cet alphabet combiné : ")
            alphabets_user[nom_combinaison] = nouveau_alpha
            print(f"Alphabet combiné '{nom_combinaison}' ajouté.")

        elif choix == "4":
            selection = input("Numéro de l'alphabet de base à utiliser pour créer l'alphabet de travail : ")
            idx = int(selection.strip()) - 1
            nom_alpha = list(alphabets_user.keys())[idx]

            # On crée une copie de l'alphabet sélectionné, sans modifier l'original
            alphabet_de_travail = set(alphabets_user[nom_alpha])
            print(f"\nVous travaillez sur une copie de '{nom_alpha}'.")

            while True:
                print(f"Alphabet de travail courant : {''.join(sorted(alphabet_de_travail))}")
                modif = input("Voulez-vous ajouter (a), retirer (r) des symboles, ou valider (v) cet alphabet ? (a/r/v) : ")
                
                if modif == "a":
                    ajout = input("Symboles à ajouter : ")
                    alphabet_de_travail.update(ajout)
                elif modif == "r":
                    retrait = input("Symboles à retirer : ")
                    alphabet_de_travail.difference_update(retrait)
                elif modif == "v":
                    print(f"\nAlphabet de travail validé : {''.join(sorted(alphabet_de_travail))}")
                    confirmation = input("Utiliser cet alphabet pour les mots ? (o/n) : ")
                    if confirmation.lower() == "o":
                        return alphabet_de_travail
                    else:
                        print("Retour au menu principal.")
                        break
                else:
                    print("Choix non reconnu.")


        elif choix == "5":
            print("Vous devez d'abord utiliser l'option 1 pour choisir un alphabet final.")

        else:
            print("Choix non reconnu. Veuillez réessayer.")
