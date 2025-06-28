from dataclasses import dataclass
from typing import Set, Dict, List, Tuple, Optional, Deque

class Etat:
    """
    Classe représentant un état dans un automate avec ses propriétés.
    """
    
    def __init__(self, nom: str, est_initial = False, est_final = False) -> None:
        """
        Initialise un état.
        
        Args:
            nom: Nom de l'état
            suivant: etat(s) suivant ou sucesseurs de l'état courrant
            transitions: valeures des transitions
        """
        self.nom = nom
        self.est_initial = est_initial
        self.est_final = est_final
        
    
    def est_accessible(self) -> bool:
        """Vérifie si l'état est accessible depuis l'état initial."""
        pass
    
    def est_utile(self) -> bool:
        """Vérifie si l'état est utile (accessible et coaccessible)."""
        pass
    
    def est_coaccessible(self) -> bool:
        """Vérifie si l'état est coaccessible (peut atteindre un état final)."""
        pass
    
    def chemin_vers_initial(self) -> Optional[List[str]]:
        """Retourne un chemin vers l'état initial s'il existe."""
        pass
    
    def chemin_vers_final(self) -> Optional[List[str]]:
        """Retourne un chemin vers un état final s'il existe."""
        pass
    
    def etats_atteignables(self) -> Set[str]:
        """Retourne l'ensemble des états atteignables depuis cet état."""
        pass
    
    def etats_precedents(self) -> Set[str]:
        """Retourne l'ensemble des états qui peuvent atteindre cet état."""
        pass
    
    def est_emonde(self) -> bool:
        """Vérifie si l'état fait partie de l'automate émondé."""
        pass

    """Surcharge d'operateur"""

    def __eq__(self, other):
        if not isinstance(other, Etat):
            return NotImplemented
        return self.nom == other.nom

    def __hash__(self):
        return hash(self.nom)

    def __str__(self):
        return self.nom
    
    def __repr__(self):
        return f"Etat('{self.nom}')"
    
  

        

    def est_accessible(self) -> bool:
        """
        Vérifie si l'état est accessible depuis l'état initial.
        Nécessite un accès à l'automate parent (assumé via un attribut automate).
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        automate = self.automate
        if self == automate.etat_initial:
            return True
        
        # BFS pour vérifier l'accessibilité
        visited = set()
        queue = Deque([automate.etat_initial])
        visited.add(automate.etat_initial)
        
        while queue:
            current = queue.popleft()
            if current in automate.transitions:
                for symbole in automate.transitions[current]:
                    for next_state in automate.transitions[current][symbole]:
                        if next_state == self:
                            return True
                        if next_state not in visited:
                            visited.add(next_state)
                            queue.append(next_state)
        return False

    def est_utile(self) -> bool:
        """
        Vérifie si l'état est utile (accessible et coaccessible).
        """
        return self.est_accessible() and self.est_coaccessible()

    def est_coaccessible(self) -> bool:
        """
        Vérifie si l'état peut atteindre un état final.
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        if self.est_final:
            return True
        
        automate = self.automate
        visited = set()
        queue = Deque([self])
        visited.add(self)
        
        while queue:
            current = queue.popleft()
            if current in automate.transitions:
                for symbole in automate.transitions[current]:
                    for next_state in automate.transitions[current][symbole]:
                        if next_state.est_final:
                            return True
                        if next_state not in visited:
                            visited.add(next_state)
                            queue.append(next_state)
        return False

    def chemin_vers_initial(self) -> Optional[List[str]]:
        """
        Retourne un chemin (liste de symboles) depuis l'état initial jusqu'à cet état.
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        automate = self.automate
        if self == automate.etat_initial:
            return []
        
        # BFS avec reconstruction du chemin
        visited = {automate.etat_initial: None}
        queue = Deque([(automate.etat_initial, [])])
        
        while queue:
            current, path = queue.popleft()
            if current in automate.transitions:
                for symbole in automate.transitions[current]:
                    for next_state in automate.transitions[current][symbole]:
                        if next_state == self:
                            return path + [symbole]
                        if next_state not in visited:
                            visited[next_state] = current
                            queue.append((next_state, path + [symbole]))
        return None

    def chemin_vers_final(self) -> Optional[List[str]]:
        """
        Retourne un chemin (liste de symboles) depuis cet état jusqu'à un état final.
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        if self.est_final:
            return []
        
        automate = self.automate
        visited = {self: None}
        queue = Deque([(self, [])])
        
        while queue:
            current, path = queue.popleft()
            if current in automate.transitions:
                for symbole in automate.transitions[current]:
                    for next_state in automate.transitions[current][symbole]:
                        if next_state.est_final:
                            return path + [symbole]
                        if next_state not in visited:
                            visited[next_state] = current
                            queue.append((next_state, path + [symbole]))
        return None

    def etats_atteignables(self) -> Set[str]:
        """
        Retourne l'ensemble des noms des états atteignables depuis cet état.
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        automate = self.automate
        reachable = set()
        queue = Deque([self])
        reachable.add(self.nom)
        
        while queue:
            current = queue.popleft()
            if current in automate.transitions:
                for symbole in automate.transitions[current]:
                    for next_state in automate.transitions[current][symbole]:
                        if next_state.nom not in reachable:
                            reachable.add(next_state.nom)
                            queue.append(next_state)
        return reachable

    def etats_precedents(self) -> Set[str]:
        """
        Retourne l'ensemble des noms des états qui peuvent atteindre cet état.
        """
        if not hasattr(self, 'automate'):
            raise AttributeError("L'état doit être associé à un automate")
        
        automate = self.automate
        predecessors = set()
        
        # Parcourir tous les états et leurs transitions
        for state in automate.etats:
            if state in automate.transitions:
                for symbole in automate.transitions[state]:
                    if self in automate.transitions[state][symbole]:
                        predecessors.add(state.nom)
        
        # Vérifier récursivement les prédécesseurs des prédécesseurs
        queue = Deque(predecessors.copy())
        while queue:
            current = queue.popleft()
            current_state = next(e for e in automate.etats if e.nom == current)
            for state in automate.etats:
                if state in automate.transitions:
                    for symbole in automate.transitions[state]:
                        if current_state in automate.transitions[state][symbole] and state.nom not in predecessors:
                            predecessors.add(state.nom)
                            queue.append(state.nom)
        
        return predecessors

    def est_emonde(self) -> bool:
        """
        Vérifie si l'état fait partie de l'automate émondé (accessible et coaccessible).
        """
        return self.est_utile()
