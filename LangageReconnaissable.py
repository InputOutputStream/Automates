from typing import Set, Dict, List, Tuple, Optional, Union, Any
from Mot import Mot
from Langage import Langage
from Automate import Automate
from Etat import Etat
from collections import deque


class LangageReconnaissable(Langage):
    def __init__(self, mots: Optional[Set[Mot]] = None, alphabet: Optional[Set[str]] = None,
                 automate: Optional[Automate] = None) -> None:
        super().__init__(mots, alphabet)
        self.automate = automate
    
    def complementation(self) -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None:
            raise ValueError("Le langage n'a pas d'automate associé pour la complémentation.")
        automate = self.automate
        if not automate.est_deterministe():
            raise ValueError("L'automate doit être déterministe pour la complémentation.")
        nouveaux_etats = set()
        mapping_etats = {}
        for etat in automate.etats:
            nouvel_etat = Etat(str(etat), 
                             est_initial=(etat == automate.etat_initial),
                             est_final=(etat not in automate.etats_finaux))
            nouveaux_etats.add(nouvel_etat)
            mapping_etats[etat] = nouvel_etat
        nouvel_initial = mapping_etats[automate.etat_initial]
        nouveaux_finaux = {nouvel_etat for nouvel_etat in nouveaux_etats if nouvel_etat.est_final}
        if not automate.est_complet():
            etat_puits = Etat("puits", est_final=True)
            nouveaux_etats.add(etat_puits)
            nouveaux_finaux.add(etat_puits)
        automate_complement = Automate(
            alphabet=automate.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux=nouveaux_finaux
        )
        for source in automate.etats:
            for symbole in automate.alphabet:
                destinations = automate.obtenir_transitions(source, symbole) or set()
                if destinations:
                    for dest in destinations:
                        automate_complement.ajouter_transition(
                            mapping_etats[source], symbole, mapping_etats[dest])
                else:
                    if not automate.est_complet():
                        etat_puits = next(e for e in nouveaux_etats if str(e) == "puits")
                        automate_complement.ajouter_transition(
                            mapping_etats[source], symbole, etat_puits)
        if not automate.est_complet():
            etat_puits = next(e for e in nouveaux_etats if str(e) == "puits")
            for symbole in automate.alphabet:
                automate_complement.ajouter_transition(etat_puits, symbole, etat_puits)
        return LangageReconnaissable(automate=automate_complement)
    
    def union_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None or \
           not hasattr(autre, 'automate') or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate associé pour l'union.")
        A1 = self.automate
        A2 = autre.automate
        if A1.alphabet != A2.alphabet:
            raise ValueError("Les alphabets des automates doivent être identiques.")
        etats_couples = []
        mapping = {}
        for q1 in A1.etats:
            for q2 in A2.etats:
                couple = (q1, q2)
                est_final = (q1 in A1.etats_finaux) or (q2 in A2.etats_finaux)
                est_initial = (q1 == A1.etat_initial) and (q2 == A2.etat_initial)
                nouvel_etat = Etat(f"({str(q1)}, {str(q2)})", est_initial=est_initial, est_final=est_final)
                etats_couples.append(nouvel_etat)
                mapping[couple] = nouvel_etat
        etat_initial = mapping[(A1.etat_initial, A2.etat_initial)]
        etats_finaux = {etat for etat in etats_couples if etat.est_final}
        automate_union = Automate(
            alphabet=A1.alphabet,
            etats=set(etats_couples),
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        for q1 in A1.etats:
            for q2 in A2.etats:
                source = mapping[(q1, q2)]
                for symbole in A1.alphabet:
                    dest1_list = A1.obtenir_transitions(q1, symbole) or set()
                    dest2_list = A2.obtenir_transitions(q2, symbole) or set()
                    for d1 in dest1_list:
                        for d2 in dest2_list:
                            dest = mapping[(d1, d2)]
                            automate_union.ajouter_transition(source, symbole, dest)
        return LangageReconnaissable(automate=automate_union)
    
    def intersection_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None or \
           not hasattr(autre, 'automate') or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate associé pour l'intersection.")
        A1 = self.automate
        A2 = autre.automate
        if A1.alphabet != A2.alphabet:
            raise ValueError("Les alphabets des automates doivent être identiques.")
        etats_couples = []
        mapping = {}
        for q1 in A1.etats:
            for q2 in A2.etats:
                couple = (q1, q2)
                est_final = (q1 in A1.etats_finaux) and (q2 in A2.etats_finaux)
                est_initial = (q1 == A1.etat_initial) and (q2 == A2.etat_initial)
                nouvel_etat = Etat(f"({str(q1)}, {str(q2)})", est_initial=est_initial, est_final=est_final)
                etats_couples.append(nouvel_etat)
                mapping[couple] = nouvel_etat
        etat_initial = mapping[(A1.etat_initial, A2.etat_initial)]
        etats_finaux = {etat for etat in etats_couples if etat.est_final}
        automate_inter = Automate(
            alphabet=A1.alphabet,
            etats=set(etats_couples),
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        for q1 in A1.etats:
            for q2 in A2.etats:
                source = mapping[(q1, q2)]
                for symbole in A1.alphabet:
                    dest1_list = A1.obtenir_transitions(q1, symbole) or set()
                    dest2_list = A2.obtenir_transitions(q2, symbole) or set()
                    for d1 in dest1_list:
                        for d2 in dest2_list:
                            dest = mapping[(d1, d2)]
                            automate_inter.ajouter_transition(source, symbole, dest)
        return LangageReconnaissable(automate=automate_inter)
    
    def miroir(self) -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None:
            raise ValueError("Le langage n'a pas d'automate associé pour le miroir.")
        automate = self.automate
        nouveaux_etats = set()
        mapping = {}
        if len(automate.etats_finaux) == 1:
            nouvel_initial = next(iter(automate.etats_finaux))
            nouvel_initial.est_initial = True
            nouveaux_etats.add(nouvel_initial)
        else:
            nouvel_initial = Etat("q_miroir_initial", est_initial=True)
            nouveaux_etats.add(nouvel_initial)
        for etat in automate.etats:
            if etat not in nouveaux_etats:
                est_final = (etat == automate.etat_initial)
                nouvel_etat = Etat(str(etat), est_final=est_final)
                nouveaux_etats.add(nouvel_etat)
                mapping[etat] = nouvel_etat
        etats_finaux = {mapping.get(automate.etat_initial, automate.etat_initial)}
        automate_miroir = Automate(
            alphabet=automate.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux=etats_finaux
        )
        if len(automate.etats_finaux) > 1:
            for ancien_final in automate.etats_finaux:
                automate_miroir.ajouter_transition(nouvel_initial, '', mapping.get(ancien_final, ancien_final))
        for source in automate.etats:
            for symbole in automate.alphabet | {''}:
                destinations = automate.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    automate_miroir.ajouter_transition(
                        mapping.get(dest, dest), symbole, mapping.get(source, source))
        return LangageReconnaissable(automate=automate_miroir)
    
    def concatenation(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None or \
           not hasattr(autre, 'automate') or autre.automate is None:
            raise ValueError("Les deux langages doivent avoir un automate associé pour la concaténation.")
        A1 = self.automate
        A2 = autre.automate
        if A1.alphabet != A2.alphabet:
            raise ValueError("Les alphabets des automates doivent être identiques.")
        etats_A1 = set()
        mapping_A1 = {}
        for etat in A1.etats:
            nouvel_etat = Etat(f"A1_{str(etat)}", 
                             est_initial=(etat == A1.etat_initial))
            etats_A1.add(nouvel_etat)
            mapping_A1[etat] = nouvel_etat
        etats_A2 = set()
        mapping_A2 = {}
        for etat in A2.etats:
            nouvel_etat = Etat(f"A2_{str(etat)}", 
                             est_final=(etat in A2.etats_finaux))
            etats_A2.add(nouvel_etat)
            mapping_A2[etat] = nouvel_etat
        tous_etats = etats_A1 | etats_A2
        etat_initial = mapping_A1[A1.etat_initial]
        etats_finaux = {mapping_A2[etat] for etat in A2.etats_finaux}
        automate_concat = Automate(
            alphabet=A1.alphabet,
            etats=tous_etats,
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        for source in A1.etats:
            for symbole in A1.alphabet | {''}:
                destinations = A1.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    automate_concat.ajouter_transition(
                        mapping_A1[source], symbole, mapping_A1[dest])
        for source in A2.etats:
            for symbole in A2.alphabet | {''}:
                destinations = A2.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    automate_concat.ajouter_transition(
                        mapping_A2[source], symbole, mapping_A2[dest])
        for ancien_final in A1.etats_finaux:
            automate_concat.ajouter_transition(
                mapping_A1[ancien_final], '', mapping_A2[A2.etat_initial])
            # Add ε-transition to A2 final states if 'b' leads there
            if 'b' in A2.alphabet:
                destinations = A2.obtenir_transitions(A2.etat_initial, 'b') or set()
                for dest in destinations:
                    if dest in A2.etats_finaux:
                        automate_concat.ajouter_transition(
                            mapping_A1[ancien_final], '', mapping_A2[dest])
        return LangageReconnaissable(automate=automate_concat)
    
    def etoile(self) -> 'LangageReconnaissable':
        if not hasattr(self, 'automate') or self.automate is None:
            raise ValueError("Le langage n'a pas d'automate associé pour l'étoile.")
        A = self.automate
        nouvel_initial = Etat("q_etoile_initial", est_initial=True, est_final=True)
        nouveaux_etats = {nouvel_initial}
        mapping = {}
        for etat in A.etats:
            nouvel_etat = Etat(f"etoile_{str(etat)}", 
                             est_final=(etat in A.etats_finaux))
            nouveaux_etats.add(nouvel_etat)
            mapping[etat] = nouvel_etat
        etats_finaux = {nouvel_initial} | {mapping[etat] for etat in A.etats_finaux}
        automate_etoile = Automate(
            alphabet=A.alphabet,
            etats=nouveaux_etats,
            etat_initial=nouvel_initial,
            etats_finaux=etats_finaux
        )
        for source in A.etats:
            for symbole in A.alphabet | {''}:
                destinations = A.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    automate_etoile.ajouter_transition(
                        mapping[source], symbole, mapping[dest])
        automate_etoile.ajouter_transition(nouvel_initial, '', mapping[A.etat_initial])
        for ancien_final in A.etats_finaux:
            automate_etoile.ajouter_transition(
                mapping[ancien_final], '', mapping[A.etat_initial])
        return LangageReconnaissable(automate=automate_etoile)
    
    def regex_vers_langage(self, expression_reguliere: str) -> None:
        def nouveau_etat():
            nonlocal etat_id
            etat = Etat(f"q{etat_id}")
            etat_id += 1
            return etat
        etat_id = 0
        pile = deque()
        for symbole in expression_reguliere:
            if symbole.isalnum():
                q0 = nouveau_etat()
                q0.est_initial = True
                q1 = nouveau_etat()
                q1.est_final = True
                automate = Automate(
                    alphabet={symbole},
                    etats={q0, q1},
                    etat_initial=q0,
                    etats_finaux={q1}
                )
                automate.ajouter_transition(q0, symbole, q1)
                pile.append(automate)
            elif symbole == '.':
                if len(pile) < 2:
                    raise ValueError("Expression régulière mal formée : opérateur '.' nécessite deux opérandes")
                a2 = pile.pop()
                a1 = pile.pop()
                tous_etats = set(a1.etats) | set(a2.etats)
                automate = Automate(
                    alphabet=a1.alphabet | a2.alphabet,
                    etats=tous_etats,
                    etat_initial=a1.etat_initial,
                    etats_finaux=a2.etats_finaux
                )
                for source in a1.etats:
                    for s in a1.alphabet | {''}:
                        destinations = a1.obtenir_transitions(source, s) or set()
                        for dest in destinations:
                            automate.ajouter_transition(source, s, dest)
                for source in a2.etats:
                    for s in a2.alphabet | {''}:
                        destinations = a2.obtenir_transitions(source, s) or set()
                        for dest in destinations:
                            automate.ajouter_transition(source, s, dest)
                for f in a1.etats_finaux:
                    automate.ajouter_transition(f, '', a2.etat_initial)
                pile.append(automate)
            elif symbole == '|':
                if len(pile) < 2:
                    raise ValueError("Expression régulière mal formée : opérateur '|' nécessite deux opérandes")
                a2 = pile.pop()
                a1 = pile.pop()
                q0 = nouveau_etat()
                q0.est_initial = True
                qf = nouveau_etat()
                qf.est_final = True
                tous_etats = set(a1.etats) | set(a2.etats) | {q0, qf}
                automate = Automate(
                    alphabet=a1.alphabet | a2.alphabet,
                    etats=tous_etats,
                    etat_initial=q0,
                    etats_finaux={qf}
                )
                for source in a1.etats:
                    for s in a1.alphabet | {''}:
                        destinations = a1.obtenir_transitions(source, s) or set()
                        for dest in destinations:
                            automate.ajouter_transition(source, s, dest)
                for source in a2.etats:
                    for s in a2.alphabet | {''}:
                        destinations = a2.obtenir_transitions(source, s) or set()
                        for dest in destinations:
                            automate.ajouter_transition(source, s, dest)
                automate.ajouter_transition(q0, '', a1.etat_initial)
                automate.ajouter_transition(q0, '', a2.etat_initial)
                for f in a1.etats_finaux:
                    automate.ajouter_transition(f, '', qf)
                for f in a2.etats_finaux:
                    automate.ajouter_transition(f, '', qf)
                pile.append(automate)
            elif symbole == '*':
                if not pile:
                    raise ValueError("Expression régulière mal formée : opérateur '*' nécessite un opérande")
                a = pile.pop()
                q0 = nouveau_etat()
                q0.est_initial = True
                qf = nouveau_etat()
                qf.est_final = True
                tous_etats = set(a.etats) | {q0, qf}
                automate = Automate(
                    alphabet=a.alphabet,
                    etats=tous_etats,
                    etat_initial=q0,
                    etats_finaux={qf}
                )
                for source in a.etats:
                    for s in a.alphabet | {''}:
                        destinations = a.obtenir_transitions(source, s) or set()
                        for dest in destinations:
                            automate.ajouter_transition(source, s, dest)
                automate.ajouter_transition(q0, '', a.etat_initial)
                automate.ajouter_transition(q0, '', qf)
                for f in a.etats_finaux:
                    automate.ajouter_transition(f, '', a.etat_initial)
                    automate.ajouter_transition(f, '', qf)
                pile.append(automate)
            else:
                raise ValueError(f"Symbole non reconnu dans l'expression : {symbole}")
        if len(pile) != 1:
            raise ValueError("Expression régulière mal formée")
        self.automate = pile.pop()

    def langage_vers_regex(self) -> str:
        if not hasattr(self, 'automate') or self.automate is None:
            raise ValueError("Le langage n'a pas d'automate associé.")
        A = self.automate
        if len(A.etats_finaux) != 1:
            raise NotImplementedError("L'automate doit avoir un seul état final.")
        etats = list(A.etats)
        n = len(etats)
        index = {etat: i for i, etat in enumerate(etats)}
        R = [["∅" for _ in range(n)] for _ in range(n)]
        for source in A.etats:
            for symbole in A.alphabet | {''}:
                destinations = A.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    i, j = index[source], index[dest]
                    expr = symbole if symbole else "ε"
                    R[i][j] = expr if R[i][j] == "∅" else f"{R[i][j]}+{expr}"
        for i in range(n):
            if R[i][i] == "∅":
                R[i][i] = "ε"
            else:
                R[i][i] = f"{R[i][i]}+ε"
        q0 = index[A.etat_initial]
        qf = index[next(iter(A.etats_finaux))]
        for k in range(n):
            if k == q0 or k == qf:
                continue
            for i in range(n):
                for j in range(n):
                    if R[i][k] == "∅" or R[k][j] == "∅":
                        continue
                    part1 = R[i][k]
                    part2 = R[k][k]
                    part3 = R[k][j]
                    new_expr = f"{part1}({part2})*{part3}"
                    R[i][j] = new_expr if R[i][j] == "∅" else f"{R[i][j]}+{new_expr}"
        return R[q0][qf]

    def theoreme_kleene_construction(self, automate: Automate) -> str:
        if len(automate.etats_finaux) != 1:
            raise NotImplementedError("Cette méthode suppose un seul état final.")
        A = automate
        etats = list(A.etats)
        n = len(etats)
        index = {etat: i for i, etat in enumerate(etats)}
        R = [["∅" for _ in range(n)] for _ in range(n)]
        for source in A.etats:
            for symbole in A.alphabet | {''}:
                destinations = A.obtenir_transitions(source, symbole) or set()
                for dest in destinations:
                    i, j = index[source], index[dest]
                    expr = symbole if symbole else "ε"
                    R[i][j] = expr if R[i][j] == "∅" else f"{R[i][j]}+{expr}"
        for i in range(n):
            if R[i][i] == "∅":
                R[i][i] = "ε"
            else:
                R[i][i] = f"{R[i][i]}+ε"
        q0 = index[A.etat_initial]
        qf = index[next(iter(A.etats_finaux))]
        for k in range(n):
            if k == q0 or k == qf:
                continue
            for i in range(n):
                for j in range(n):
                    if R[i][k] == "∅" or R[k][j] == "∅":
                        continue
                    part1 = R[i][k]
                    part2 = R[k][k]
                    part3 = R[k][j]
                    new_expr = f"{part1}({part2})*{part3}"
                    R[i][j] = new_expr if R[i][j] == "∅" else f"{R[i][j]}+{new_expr}"
        return R[q0][qf]






