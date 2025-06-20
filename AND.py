from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any

#Import
import itertools
from Automate import Automate,ADC



class AND(Automate):
    """
    Automate Non Déterministe.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux automates non déterministes.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, etats_finaux: Set[str], Value: dict) -> None:
        """Initialise un AND."""
        super().__init__(alphabet,etats,etat_initial,etats_finaux)
        self.Value = Value
        
    
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition non déterministe."""
        pass
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition non déterministe."""
        pass
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne un ensemble d'états (non déterminisme)."""
        pass
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance non déterministe d'un mot."""
        pass
    
    def est_deterministe(self) -> bool:
        """Vérifie le déterminisme."""
        deterministe = True
        for value in self.Value:
            for sub_value in self.Value[value]:
                if len(self.Value[value][sub_value]) != 1:
                    return False
        return deterministe
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        
        pass
    
    #Add 
    def get_tableau_transition(self) -> dict:
        """
            Fonction qui retourne le tableau de transitions d'un AND 
        """
        tableau_transition = {}
        elements = {}
        liste_etats = [self.etat_initial]
        treated = []
        while liste_etats != []:
            etat = liste_etats[0]
            elements = {}
            for a in self.alphabet: 
                elements.update({a:""})
            
            if isinstance(etat, str) == False:
                for j in self.alphabet:
                    if j in self.Value[etat]:
                        if elements[j] == "":
                            elements[j] = self.Value[etat][j]
                        else:
                            elements[j] = {elements[j],self.Value[etat][j]}
                        tableau_transition.update({etat: elements})
            else:
                nouvel_etat = etat.split(".")
                for t in nouvel_etat:
                    for j in self.alphabet:
                        if j in self.Value[int(t)]:
                            if elements[j] == "":
                                elements[j] = self.Value[int(t)][j]
                            else:
                                elements[j] = {elements[j],self.Value[int(t)][j]}
                tableau_transition.update({etat: elements})
            
            for m in elements:
                if (elements[m] not in liste_etats) and (elements[m] != ""):
                    if isinstance(elements[m],set) == True:
                        nouvel_etat = ""
                        for value in elements[m]:
                            nouvel_etat += "." + str(value)
                        elements[m] = nouvel_etat[1:]
                        if elements[m] not in treated:    
                            liste_etats.append(elements[m])
                    else:
                        if elements[m] not in treated:    
                            liste_etats.append(elements[m])
            treated.append(etat)
            liste_etats.pop(liste_etats.index(etat))
            
            
            if liste_etats == []:
                return tableau_transition
                        
        return tableau_transition
        
            
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        tableau_transition = self.get_tableau_transition()
        
        pass
        
        
        
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        pass


auto = {1: {"a":{2,3}},
        2: {"b":3},
        3: {"a":2,"b":2}
    }

and_ = AND({"a","b"},{1,2,3},1,{3},auto)
print(and_.get_tableau_transition())
