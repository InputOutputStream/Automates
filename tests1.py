from mots1 import Mot1
from alpha import *

def main():

    while True:
        try:

            print("=== Configuration de l'alphabet ===")
            alphabet_utilise = choisir_alphabet()

            print("\n=== Création du mot ===")
            contenu = input("Veuillez entrer le contenu du mot : ")

            # On crée un mot en utilisant l'alphabet courant (par ex. alphabet_ref_user)
            mot = Mot1(contenu, alphabet_utilise)

            # Si pas d'erreur, on sort de la boucle
            print(f"Mot créé avec succès : {mot.contenu}")

            print(f"\nMot créé : {mot.contenu}")
            print(f"Alphabet de référence : {''.join(sorted(mot.alphabet))}")

            print("Longueur:", mot.longueur())
            
            mot2 = mot.adjonction_occurrence_gauche("x")
            print("Après adjonction gauche:", mot2)
            
            mot3 = mot.adjonction_occurrence_droite("y")
            print("Après adjonction droite:", mot3)
            
            mot_autre = Mot1("bc", {"a", "b", "c"})
            
            mot_concat = mot.concatenation(mot_autre, fusion_alphabet=True)
            print("Concaténation stricte:", mot_concat)
            
            print("Liste facteurs (min 1):")
            for facteurs in mot.liste_facteurss():
                print("-", facteurs)
            
            print("Liste facteurs distincts (min 2):")
            for facteurs in mot.liste_facteurss(distinct=True, min_length=2):
                print("-", facteurs)

        except ValueError as e:
            print(f"Erreur : {e}")
            print("Veuillez réessayer.\n")

if __name__ == "__main__":
    main()
