from collections import deque
from typing import Optional, List, Set

class Etat:
    def __init__(self, nom: str, est_initial=False, est_final=False):
        self.nom = nom
        self.est_initial = est_initial
        self.est_final = est_final
        self.automate = None  # doit être assigné par l’automate parent

    def __str__(self): return self.nom
    def __repr__(self): return f"Etat('{self.nom}')"
    def __eq__(self, other): return isinstance(other, Etat) and self.nom == other.nom
    def __hash__(self): return hash(self.nom)

    def est_accessible(self) -> bool:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        visited = set()
        queue = deque([self.automate.etat_initial])
        while queue:
            etat = queue.popleft()
            if etat == self:
                return True
            for symbole in self.automate.alphabet:
                for suivant in self.automate.obtenir_transitions(etat, symbole):
                    if suivant not in visited:
                        visited.add(suivant)
                        queue.append(suivant)
        return False

    def est_coaccessible(self) -> bool:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        visited = set()
        queue = deque([self])
        while queue:
            etat = queue.popleft()
            if etat.est_final:
                return True
            for symbole in self.automate.alphabet:
                for suivant in self.automate.obtenir_transitions(etat, symbole):
                    if suivant not in visited:
                        visited.add(suivant)
                        queue.append(suivant)
        return False

    def est_utile(self) -> bool:
        return self.est_accessible() and self.est_coaccessible()

    def chemin_vers_initial(self) -> Optional[List[str]]:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        visited = {self.automate.etat_initial}
        queue = deque([(self.automate.etat_initial, [])])
        while queue:
            courant, chemin = queue.popleft()
            for symbole in self.automate.alphabet:
                for suivant in self.automate.obtenir_transitions(courant, symbole):
                    if suivant == self:
                        return chemin + [symbole]
                    if suivant not in visited:
                        visited.add(suivant)
                        queue.append((suivant, chemin + [symbole]))
        return None

    def chemin_vers_final(self) -> Optional[List[str]]:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        if self.est_final:
            return []
        
        visited = {self}
        queue = deque([(self, [])])
        while queue:
            courant, chemin = queue.popleft()
            for symbole in self.automate.alphabet:
                for suivant in self.automate.obtenir_transitions(courant, symbole):
                    if suivant.est_final:
                        return chemin + [symbole]
                    if suivant not in visited:
                        visited.add(suivant)
                        queue.append((suivant, chemin + [symbole]))
        return None

    def etats_atteignables(self) -> Set[str]:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        atteints = {self.nom}
        queue = deque([self])
        while queue:
            courant = queue.popleft()
            for symbole in self.automate.alphabet:
                for suivant in self.automate.obtenir_transitions(courant, symbole):
                    if suivant.nom not in atteints:
                        atteints.add(suivant.nom)
                        queue.append(suivant)
        return atteints

    def etats_precedents(self) -> Set[str]:
        if not self.automate:
            raise AttributeError("L'état doit être associé à un automate.")
        
        pred = set()
        for e in self.automate.etats:
            for symbole in self.automate.alphabet:
                if self in self.automate.obtenir_transitions(e, symbole):
                    pred.add(e.nom)

        full = set(pred)
        queue = deque(pred)
        while queue:
            nom = queue.popleft()
            etat = next(e for e in self.automate.etats if e.nom == nom)
            for e in self.automate.etats:
                for symbole in self.automate.alphabet:
                    if etat in self.automate.obtenir_transitions(e, symbole) and e.nom not in full:
                        full.add(e.nom)
                        queue.append(e.nom)
        return full

    def est_emonde(self) -> bool:
        return self.est_utile()

