from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any

#Import
import itertools


class Monoids:#Fonction_CHAP2
    """
    Classe représentant un monoïde.
    Implémentation selon la compréhension du cours de chaque développeur.
    """
    
    def __init__(self, ensemble: Set[Any], operation: callable, element_neutre: Any) -> None:
        """
        Initialise un monoïde.
        
        Args:
            ensemble: Ensemble de base
            operation: Opération binaire
            element_neutre: Élément neutre
        """
        self.ensemble = ensemble
        self.operation = operation
        self.element_neutre = element_neutre
        if element_neutre not in ensemble:
            print(f"Element neutre absent dans {self.ensemble}")
            exit(0)

    
    def est_associatif(self) -> bool:#Fonction_CHAP2
        """Vérifie l'associativité de l'opération."""
        
        for a,b,c in itertools.combinations(self.ensemble,3):
            if self.operation(self.operation(a,b),c) == self.operation(a,self.operation(b,c)):
                associatif = True
        return associatif
        
    
    def verifier_element_neutre(self) -> bool:
        """Vérifie l'existence de l'élément neutre."""
        pass
    
    def sous_monoide(self, sous_ensemble: Set[Any]) -> 'Monoids':#Fonction_CHAP2
        """Construit un sous-monoïde."""
        pass
    
    def morphisme(self, autre_monoide: 'Monoids', application: callable) -> bool:#Fonction_CHAP2
        """Vérifie si une fonction est un morphisme de monoïdes."""
        condition1 = False
        condition2 = True
        
        if application(self.element_neutre) == autre_monoide.element_neutre:
            condition1 = True

        for a,b in itertools.combinations(self.ensemble,2):          
            if application(self.operation(a,b)) != autre_monoide.operation(application(a),application(b)):
                condition2 = False
        
        if condition1 == True and condition2 == True:
            return True
        
        return False 



def produit(a,b):
    return int(a)*int(b)

def concatenation(a,b):
    return str(a)+str(b) 

def addition(a,b):
    return int(a)+int(b)


def Test():
    D = Monoids({"","1","3","10","14"},concatenation,"")
    B = Monoids({0,1,3,10,14},addition,0)
    def longeur(a):
        return len(str(a))

    print(D.est_associatif())
    print(D.morphisme(B,longeur))
