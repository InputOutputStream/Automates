from typing import Set, Dict

class Automate:
    def __init__(self, alphabet: Set[str]) -> None:
        self.alphabet = alphabet
        self.etats: Set[str] = set()
        self.etat_initial: Optional[str] = None
        self.etats_finaux: Set[str] = set()
        self.fonction_transition: Dict[str, Dict[str, Set[str]]] = {}

    def ajouter_etat(self, etat: str) -> None:
        self.etats.add(etat)
        if etat not in self.fonction_transition:
            self.fonction_transition[etat] = {symb: set() for symb in self.alphabet}

    def supprimer_etat(self, etat: str) -> None:
        self.etats.discard(etat)
        self.etats_finaux.discard(etat)
        if self.etat_initial == etat:
            self.etat_initial = None
        self.fonction_transition.pop(etat, None)
        for transitions in self.fonction_transition.values():
            for symb in self.alphabet:
                transitions[symb].discard(etat)

    def definir_etat_initial(self, etat: str) -> None:
        if etat in self.etats:
            self.etat_initial = etat

    def ajouter_etat_final(self, etat: str) -> None:
        if etat in self.etats:
            self.etats_finaux.add(etat)

    def supprimer_etat_final(self, etat: str) -> None:
        self.etats_finaux.discard(etat)

    def rendre_etat_normal(self, etat: str) -> None:
        if self.etat_initial == etat:
            self.etat_initial = None
        self.etats_finaux.discard(etat)

    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        if etat_source in self.etats and etat_cible in self.etats and symbole in self.alphabet:
            self.fonction_transition[etat_source][symbole].add(etat_cible)

    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        if etat_source in self.etats and symbole in self.alphabet:
            self.fonction_transition[etat_source][symbole].discard(etat_cible)

    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        if etat in self.etats and symbole in self.alphabet:
            return self.fonction_transition[etat][symbole]
        return set()

    def reconnaitre_mot(self, mot: str) -> bool:
        etats_courants = {self.etat_initial}
        for symbole in mot:
            if symbole not in self.alphabet:
                return False
            prochains_etats = set()
            for etat in etats_courants:
                prochains_etats.update(self.obtenir_transitions(etat, symbole))
            etats_courants = prochains_etats
        return any(etat in self.etats_finaux for etat in etats_courants)

    def est_deterministe(self) -> bool:
        for etat in self.etats:
            for symbole in self.alphabet:
                if len(self.fonction_transition[etat][symbole]) > 1:
                    return False
        return True

    def est_complet(self) -> bool:
        for etat in self.etats:
            for symbole in self.alphabet:
                if not self.fonction_transition[etat][symbole]:
                    return False
        return True

    def afficher(self) -> str:
        lignes = []
        lignes.append(f"États: {self.etats}")
        lignes.append(f"Alphabet: {self.alphabet}")
        lignes.append(f"État initial: {self.etat_initial}")
        lignes.append(f"États finaux: {self.etats_finaux}")
        lignes.append("Transitions:")
        for etat in self.etats:
            for symbole in self.alphabet:
                cibles = self.fonction_transition[etat][symbole]
                for cible in cibles:
                    lignes.append(f"  {etat} --{symbole}--> {cible}")
        return "\n".join(lignes)
