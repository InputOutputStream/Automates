from app.Automate import AFDC, AFND, Automate,AD
from app.Etat import Etat
from typing import Dict


# ============================
# FONCTION D'UNION DE DEUX AUTOMATES
# ============================

def union_automates(a1: Automate, a2: Automate) -> Automate:
    """
    Retourne un automate représentant l’union de a1 et a2 avec :
    - un état initial unique,
    - un état final unique,
    - des transitions ε depuis le nouvel état initial vers les anciens,
    - des transitions ε depuis les anciens états finaux vers le nouvel état final.
    """
    from copy import deepcopy

    def renommer_etats(automate: Automate, prefix: str) -> Dict[Etat, Etat]:
        mapping = {}
        for etat in automate.etats:
            nouveau = Etat(f"{prefix}_{etat.nom}")
            nouveau.est_initial = False
            nouveau.est_final = False
            mapping[etat] = nouveau
        return mapping

    mapping_a1 = renommer_etats(a1, "A1")
    mapping_a2 = renommer_etats(a2, "A2")

    nouveaux_etats = set(mapping_a1.values()).union(mapping_a2.values())
    nouvel_alphabet = a1.alphabet.union(a2.alphabet)

    # Création d’un état initial et final uniques
    nouvel_initial = Etat("I", est_initial=True)
    nouvel_final = Etat("F", est_final=True)
    nouveaux_etats.update({nouvel_initial, nouvel_final})

    # Création de l'automate résultant
    automate_resultat = AFND(
        alphabet=nouvel_alphabet,
        etats=nouveaux_etats,
        etat_initial=nouvel_initial,
        etats_finaux={nouvel_final}
    )

    # Ajout des transitions de a1
    for etat_src in a1.transitions:
        for symbole in a1.transitions[etat_src]:
            for etat_dst in a1.transitions[etat_src][symbole]:
                automate_resultat.ajouter_transition(mapping_a1[etat_src], symbole, mapping_a1[etat_dst])

    # Ajout des transitions de a2
    for etat_src in a2.transitions:
        for symbole in a2.transitions[etat_src]:
            for etat_dst in a2.transitions[etat_src][symbole]:
                automate_resultat.ajouter_transition(mapping_a2[etat_src], symbole, mapping_a2[etat_dst])

    # Transitions ε depuis le nouvel état initial vers les anciens
    automate_resultat.ajouter_transition(nouvel_initial, '', mapping_a1[a1.etat_initial])
    automate_resultat.ajouter_transition(nouvel_initial, '', mapping_a2[a2.etat_initial])
    print(f"I --ε--> {mapping_a1[a1.etat_initial].nom}")
    print(f"I --ε--> {mapping_a2[a2.etat_initial].nom}")

    # Transitions ε depuis anciens états finaux vers le nouvel état final
    for etat_final_a1 in a1.etats_finaux:
        automate_resultat.ajouter_transition(mapping_a1[etat_final_a1], '', nouvel_final)
        print(f"{mapping_a1[etat_final_a1].nom} --ε--> F")

    for etat_final_a2 in a2.etats_finaux:
        automate_resultat.ajouter_transition(mapping_a2[etat_final_a2], '', nouvel_final)
        print(f"{mapping_a2[etat_final_a2].nom} --ε--> F")

    return automate_resultat



# ============================
# AUTRES FONCTIONS (VIDES OU À COMPLÉTER)
# ============================

def intersection_automates(a1: Automate, a2: Automate) -> Automate:
    """
    Renvoie l'automate de l'intersection de a1 et a2.
    L'intersection est calculée via le produit cartésien des états.
    """
    if not a1.est_deterministe() or not a2.est_deterministe():
        raise TypeError("Les deux automates doivent être déterministes pour faire l'intersection.")
    
    if not a1.est_complet() or not a2.est_complet():
        raise ValueError("Les deux automates doivent être complets pour faire l'intersection.")

    alphabet = a1.alphabet.intersection(a2.alphabet)
    nouveaux_etats = set()
    transitions = {}
    etats_finaux = set()

    mapping_etats = {}
    
    # Création des états du produit
    for e1 in a1.etats:
        for e2 in a2.etats:
            nom = f"{e1.nom}_{e2.nom}"
            est_initial = (e1 == a1.etat_initial and e2 == a2.etat_initial)
            est_final = (e1 in a1.etats_finaux and e2 in a2.etats_finaux)
            nouvel_etat = Etat(nom, est_initial, est_final)
            mapping_etats[(e1, e2)] = nouvel_etat
            nouveaux_etats.add(nouvel_etat)
            if est_final:
                etats_finaux.add(nouvel_etat)

    # Définition des transitions
    for (e1, e2), etat_produit in mapping_etats.items():
        for symb in alphabet:
            dest1 = list(a1.transitions.get(e1, {}).get(symb, []))
            dest2 = list(a2.transitions.get(e2, {}).get(symb, []))
            if dest1 and dest2:
                dest_etat = mapping_etats[(dest1[0], dest2[0])]  # car déterministes
                if etat_produit not in transitions:
                    transitions[etat_produit] = {}
                if symb not in transitions[etat_produit]:
                    transitions[etat_produit][symb] = set()
                transitions[etat_produit][symb].add(dest_etat)

    # Recherche de l’état initial
    for e in nouveaux_etats:
        if e.est_initial:
            etat_initial = e
            break

    # Construction de l'automate résultant
    automate_intersection = Automate(
        alphabet=alphabet,
        etats=nouveaux_etats,
        etat_initial=etat_initial,
        etats_finaux=etats_finaux
    )
    automate_intersection.transitions = transitions

    return automate_intersection



def complementaire_automate(a: Automate) -> Automate:
    """
    Renvoie le complémentaire de l'automate.
    Si ce n'est pas un AFDC, le rend déterministe et complet d'abord.
    """
    if not isinstance(a, AFDC):
        print("L’automate n’est pas un AFDC, déterminisation et complétion en cours...")
        a = a.determinisation_thompson()
        a = a.completer()

    # ⚠️ Trouver l'instance exacte de l'état initial dans a.etats
    etat_initial = None
    for e in a.etats:
        if e.nom == a.etat_initial.nom:
            etat_initial = e
            break

    if etat_initial is None:
        raise ValueError("Impossible de retrouver l’état initial dans les états")

    # Nouveaux états finaux = tous les états qui ne sont pas finaux dans a
    nouveaux_etats_finaux = {e for e in a.etats if e not in a.etats_finaux}

    # Créer l'automate complémentaire en réutilisant les mêmes états et transitions
    automate_complement = AFDC(
        alphabet=a.alphabet,
        etats=a.etats,
        etat_initial=etat_initial,
        etats_finaux=nouveaux_etats_finaux
    )

    # Copier les transitions
    for etat_source, dico in a.transitions.items():
        for symbole, cibles in dico.items():
            for cible in cibles:
                automate_complement.ajouter_transition(etat_source, symbole, cible)

    return automate_complement





def concatenation_automates(a1: Automate, a2: Automate) -> Automate:
    """
    Renvoie l'automate qui accepte le langage concaténé de a1.a2.
    """
    pass


# ============================
# DÉMONSTRATION
# ============================

if __name__ == "__main__":
    print("=== TESTS DE CLÔTURE D'AUTOMATES ===\n")

    # États de base
    q0 = Etat("q0", est_initial=True)
    q1 = Etat("q1", est_final=True)
    q2 = Etat("q2")

    # Automate 1
    print("Automate 1 : mots finissant par 'a'")
    automate1 = Automate(
        alphabet={'a', 'b'},
        etats={q0, q1},
        etat_initial=q0,
        etats_finaux={q1}
    )
    automate1.ajouter_transition(q0, 'a', q1)
    automate1.ajouter_transition(q0, 'b', q0)
    automate1.ajouter_transition(q1, 'a', q1)
    automate1.ajouter_transition(q1, 'b', q0)

    print(automate1.afficher())

    # Automate 2
    print("\nAutomate 2 : non-déterministe")
    q0b = Etat("q0", est_initial=True)
    q1b = Etat("q1")
    q2b = Etat("q2", est_final=True)

    automate2 = Automate(
        alphabet={'a', 'b'},
        etats={q0b, q1b, q2b},
        etat_initial=q0b,
        etats_finaux={q2b}
    )
    automate2.ajouter_transition(q0b, 'a', q1b)
    automate2.ajouter_transition(q0b, 'a', q2b)
    automate2.ajouter_transition(q1b, 'b', q2b)

    print(automate2.afficher())

    # Union des deux automates
    print("\nAutomate Union :")
    automate_union = union_automates(automate1, automate2)
    print(automate_union.afficher())

    # Test de mots sur l'automate union
    mots_test = ["a", "ba", "ab", "b", "bba", "", "aa"]
    for mot in mots_test:
        resultat = automate_union.reconnaitre_mot(mot)
        print(f"Mot '{mot}': {'✓' if resultat else '✗'}")

    
    # A1 : finit par 'a'
    q0 = Etat("q0", est_initial=True)
    q1 = Etat("q1", est_final=True)

    automate3 = AD(
        alphabet={'a', 'b'},
        etats={q0, q1},
        etat_initial=q0,
        etats_finaux={q1}
    )

    automate3.ajouter_transition(q0, 'a', q1)
    automate3.ajouter_transition(q0, 'b', q0)
    automate3.ajouter_transition(q1, 'a', q1)
    automate3.ajouter_transition(q1, 'b', q0)


    # A2 : contient au moins un 'b'
    p0 = Etat("p0", est_initial=True)
    p1 = Etat("p1", est_final=True)

    automate4 = AD(
        alphabet={'a', 'b'},
        etats={p0, p1},
        etat_initial=p0,
        etats_finaux={p1}
    )

    automate4.ajouter_transition(p0, 'a', p0)
    automate4.ajouter_transition(p0, 'b', p1)
    automate4.ajouter_transition(p1, 'a', p1)
    automate4.ajouter_transition(p1, 'b', p1)
    
    print("\n=== Automate d'intersection A1 ∩ A2 ===")
    automate_inter = intersection_automates(automate3, automate4)
    print(automate_inter.afficher())