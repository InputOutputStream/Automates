
from typing import Set, Dict, List, Tuple, Optional, Union, Any
from .Mot import Mot

class Langage:
    """
    Classe représentant un langage (ensemble de mots).
    Surcharge d'opérateurs pour les opérations sur les langages.
    """
    
    def __init__(self, mots: Optional[Set[Mot]] = None, 
                 alphabet: Optional[Set[str]] = None, 
                 est_infini : bool = True,
                valeur_max : int = 1_000_000) -> None:
        """
        Initialise un langage.
        
        Args:
            mots: Ensemble de mots du langage
            alphabet: Alphabet du langage
        """
        self.mots = set(mots) if mots is not None else set()
        self.alphabet = set(alphabet) if alphabet is not None else set()
        self.langage_fini = est_infini
        self.valeur_max = valeur_max

        if alphabet is None and mots:
            self.alphabet = self._calculer_alphabet_depuis_mots()
    
    def _calculer_alphabet_depuis_mots(self) -> Set[str]:
        """Calcule l'alphabet à partir des mots du langage."""
        alphabet = set()
        for mot in self.mots:
            alphabet.update(mot.alphabet)  # Union des alphabets
        return alphabet
    
    
    def taille_du_langage(self) -> Union[int, float]:
        """Retourne la taille du langage (peut être infinie)."""
        if not self.langage_fini:
            return float('inf')
        return len(self.mots)
    
    def ajouter_mot(self, mot: Mot) -> None:
        """Ajoute un mot au langage."""
        
        if not self.alphabet.issubset(mot.alphabet) and self.alphabet:
            raise ValueError(f"Le mot {mot} n'est pas sur l'alphabet {self.alphabet}")
        self.mots.add(mot) 

    def reunion_finie_des_langages(self, autres_langages: List['Langage']) -> 'Langage':
        """Réunion finie de langages."""
        if not self.langage_fini:
            raise TypeError("Le langage est infini, impossible de faire la réunion")
        
        nouveaux_mots = self.mots.copy()
        nouvel_alphabet = self.alphabet.copy()
        
        for langage in autres_langages:
            if not langage.langage_fini:
                raise TypeError("Un des langages est infini")
                
            if self.alphabet != langage.alphabet:
                raise ValueError(f"Attention: alphabets différents {self.alphabet} vs {langage.alphabet}")
            
            nouveaux_mots.update(langage.mots)
        
        return Langage(nouveaux_mots, nouvel_alphabet)

    def contient_mot(self, mot: Mot) -> bool:
        """Appartenance d'un mot a un langage langages."""
        return mot in self.mots  
    
    def concatenation_des_langages(self, autre_langage: 'Langage') -> 'Langage':
        """Concaténation de deux langages."""

        if self.alphabet != autre_langage.alphabet:
            raise ValueError("The alphabets for both languages are different")
    
        if len(self.mots) == 0 or len(autre_langage.mots) == 0:
            return Langage({}, self.alphabet)
        
         
        # Utilisation d'un set pour éviter les doublons automatiquement
        mots_concatenes = set()
        
        for mot1 in self.mots:
            for mot2 in autre_langage.mots:
                mot_concatene = mot1 + mot2
                mots_concatenes.add(mot_concatene)
        
        return Langage(mots_concatenes, self.alphabet)
        
    def puissance(self, n: int) -> 'Langage':

        if n < 0:
            raise ValueError("La puissance doit être positive")
        
        if n == 0:
            # L^0 = {ε} (langage contenant le mot vide)
            mot_vide = Mot("", self.alphabet)
            return Langage({mot_vide}, self.alphabet)
        
        if n == 1:
            return Langage(self.mots.copy(), self.alphabet.copy())
               
        resultat = Langage(self.mots.copy(), self.alphabet.copy())
        for i in range(1, n):
            resultat = resultat.concatenation_des_langages(self)
        
        return resultat
    
    def iteration_sur_langages(self) -> 'Langage':
        """Étoile de Kleene du langage."""
        return self.kleene_tronquee(self.valeur_max)
    
    def quotient_gauche_de_langages(self, autre_langage: 'Langage') -> 'Langage':
        """Quotient de langages."""
        """L1^-1.L2"""
        L2 = set()
        for mot in self.mots:
            for autre_mot in autre_langage.mots:
                """ Verifier que le debut de mot est bien un mot de autre langage """
                if mot.contenu.startswith(autre_mot.contenu):
                   suffixe = mot.contenu[len(autre_mot.contenu):]
                   L2.add(suffixe)
        return Langage(L2)
    
    def quotient_droit_de_langages(self, autre_langage: 'Langage') -> 'Langage':
        """Quotient de langages."""
        """L2.L1^-1"""
        L2 = set()
        for mot in self.mots:
            for autre_mot in autre_langage.mots:
                """ Verifier que la fin de mot est bien un mot de autre langage """
                if mot.contenu.endswith(autre_mot.contenu):
                    prefixe = mot.contenu[:-len(autre_mot.contenu)]
                    L2.add(prefixe)
        return Langage(L2)


    def kleene_tronquee(self, max_longueur):
        if max_longueur < 0:
            raise ValueError("La longueur maximale doit être positive")
        
        # Commencer avec {ε}
        mot_vide = Mot("", self.alphabet)
        resultat = Langage({mot_vide}, self.alphabet)
        
        # Ajouter L, L², L³, ...L* jusqu'à max_longueur, ici max_longeur est un peu comme notre etoile 
        puissance_courante = Langage({mot_vide}, self.alphabet)
        
        for i in range(1, max_longueur + 1):
            puissance_courante = puissance_courante.concatenation_des_langages(self)
            
            # Filtrer par longueur pour éviter l'explosion
            mots_filtres = {mot for mot in puissance_courante.mots if len(mot.contenu) <= max_longueur}
            puissance_courante = Langage(mots_filtres, self.alphabet)
            resultat = resultat.reunion_finie_des_langages([puissance_courante])
        
        return resultat
    
    def est_vide(self) -> bool:
        """Vérifie si le langage est vide."""
        return len(self.mots) == 0
    
    def est_sous_langage_de(self, autre_langage: 'Langage') -> bool:
        """Vérifie si ce langage est un sous-langage d'un autre."""
        # Utilisation de issubset() pour les sets - TRÈS EFFICACE !
        return self.mots.issubset(autre_langage.mots)
    
    def mots_de_longueur(self, longueur: int) -> Set[Mot]:
        """Retourne tous les mots de longueur donnée."""
        return {mot for mot in self.mots if len(mot.contenu) == longueur}
    
    def longueur_maximale(self) -> int:
        """Retourne la longueur du mot le plus long."""
        if not self.mots:
            return 0
        return max(len(mot.contenu) for mot in self.mots)

    # C'est approximatif ca, on ne peut pas se prononcer 
    def type_de_langage(self) -> str:
        """Détermine le type du langage dans la hiérarchie de Chomsky."""
        if not self.langage_fini:
            return "Type indéterminé (langage infini)"
        
        if len(self.mots) == 0:
            return "Langage vide"
        
        if len(self.mots) == 1 and list(self.mots)[0].contenu == "":
            return "Langage {ε}"
        
        # Analyse basique - peut être étendue
        longueurs = [len(mot.contenu) for mot in self.mots]
        
        if all(l == longueurs[0] for l in longueurs):
            return f"Langage de mots de longueur {longueurs[0]}"
        else:
            return "Langage général (analyse approfondie nécessaire)"
        

    def difference_langages(self, autre):
        nouveaux_mots = self.mots - autre.mots
        return Langage(nouveaux_mots, self.alphabet)

    def intersection_langages(self, autre):
        mots_communs = self.mots & autre.mots
        return Langage(mots_communs, self.alphabet)
    
    # ===== SURCHARGES D'OPÉRATEURS OPTIMISÉES =====
    
    def __add__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de + pour l'union."""
        return self.reunion_finie_des_langages([autre])
    
    def __mul__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de * pour la concaténation."""
        return self.concatenation_des_langages(autre)
    
    def __sub__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de - pour la différence."""
        return self.difference_langages(autre)
    
    def __and__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de & pour l'intersection."""
        return self.intersection_langages(autre)
    
    def __or__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de | pour l'union."""
        return self.reunion_finie_des_langages([autre])
    
    def __len__(self) -> int:
        """Retourne la taille du langage."""
        return len(self.mots)
    
    def __iter__(self):
        """Permet l'itération sur les mots du langage."""
        return iter(self.mots)
    
    def __contains__(self, mot: Mot) -> bool:
        """Surcharge de 'in' pour vérifier l'appartenance."""
        return mot in self.mots
    
    def __eq__(self, autre: 'Langage') -> bool:
        """Égalité entre langages."""
        return (self.mots == autre.mots and 
                self.alphabet == autre.alphabet)
    
    def __str__(self) -> str:
        """Représentation textuelle du langage."""
        if not self.langage_fini:
            return f"Langage infini sur alphabet {self.alphabet}"
        
        if len(self.mots) == 0:
            return "(langage vide)"
        
        mots_str = ", ".join(str(mot) for mot in sorted(self.mots, key=lambda m: m.contenu))
        return f"{{{mots_str}}}"
    
    def __repr__(self) -> str:
        return f"Langage({self.mots}, {self.alphabet})"




# =============================================
# DÉMONSTRATION D'UTILISATION
# =============================================

if __name__ == "__main__":

    print("=== DÉMONSTRATION DE LA CLASSE LANGAGE OPTIMISÉE ===\n")
    
    # Création de mots
    alphabet = {'a', 'b'}
    mot1 = Mot("a", alphabet)
    mot2 = Mot("b", alphabet)
    mot3 = Mot("ab", alphabet)
    mot4 = Mot("ba", alphabet)
    
    # Création de langages
    L1 = Langage({mot1, mot2}, alphabet)
    L2 = Langage({mot3, mot4}, alphabet)
    
    print(f"L1 = {L1}")
    print(f"L2 = {L2}")
    print(f"Taille de L1: {len(L1)}")
    print(f"Taille de L2: {len(L2)}")
    
    # Tests d'appartenance (très rapides avec les sets !)
    print(f"\nTests d'appartenance:")
    print(f"'a' ∈ L1 ? {mot1 in L1}")
    print(f"'ab' ∈ L1 ? {mot3 in L1}")
    
    # Opérations sur les langages
    print(f"\nOpérations:")
    union = L1 + L2
    print(f"L1 ∪ L2 = {union}")
    
    concatenation = L1 * L2
    print(f"L1 · L2 = {concatenation}")
    
    intersection = L1 & L2
    print(f"L1 ∩ L2 = {intersection}")
    
    # Puissance
    L1_carre = L1.puissance(2)
    print(f"L1² = {L1_carre}")
    
    # Étoile de Kleene tronquée
    L1_etoile_3 = L1.kleene_tronquee(3)
    print(f"L1* (tronquée à longueur 3) = {L1_etoile_3}")
    
    # Analyse du type de langage
    print(f"\nAnalyse:")
    print(f"Type de L1: {L1.type_de_langage()}")
    print(f"Type de L1²: {L1_carre.type_de_langage()}")
    
    print(f"\nMots de longueur 2 dans L1*: {L1_etoile_3.mots_de_longueur(2)}")
    

