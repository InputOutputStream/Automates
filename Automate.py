from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional, Union, Any


class Automate(ABC):
    """
    Classe abstraite représentant un automate selon la définition du cours.
    
    Composants:
    - alphabet: ensemble de symboles
    - etats: ensemble d'états
    - etat_initial: état de départ
    - etats_finaux: ensemble d'états finaux
    - fonction_transition: fonction de transition
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, etats_finaux: Set[str]) -> None:
        """
        Initialise l'automate avec ses composants de base.
        
        Args:
            alphabet: Ensemble des symboles de l'alphabet
            etats: Ensemble des états
            etat_initial: État initial
            etats_finaux: Ensemble des états finaux
        """
        pass
    
    @abstractmethod
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition à l'automate."""
        pass
    
    @abstractmethod
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition de l'automate."""
        pass
    
    @abstractmethod
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne l'ensemble des états accessibles depuis un état avec un symbole."""
        pass
    
    @abstractmethod
    def reconnaitre_mot(self, mot: str) -> bool:
        """Détermine si un mot est reconnu par l'automate."""
        pass
    
    @abstractmethod
    def est_deterministe(self) -> bool:
        """Vérifie si l'automate est déterministe."""
        pass
    
    @abstractmethod
    def est_complet(self) -> bool:
        """Vérifie si l'automate est complet."""
        pass
    
    @abstractmethod
    def afficher(self) -> str:
        """Retourne une représentation textuelle de l'automate."""
        pass


class ADC(Automate):
    """
    Automate Déterministe Complet.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux ADC (déterminisme et complétude).
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, etats_finaux: Set[str]) -> None:
        """Initialise un ADC."""
        pass
    
    def ajouter_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Ajoute une transition en respectant le déterminisme."""
        pass
    
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition en maintenant la complétude."""
        pass
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne exactement un état (déterminisme)."""
        pass
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance déterministe d'un mot."""
        pass
    
    def est_deterministe(self) -> bool:
        """Retourne toujours True pour un ADC."""
        pass
    
    def est_complet(self) -> bool:
        """Retourne toujours True pour un ADC."""
        pass
    
    def completer(self) -> None:
        """Complète l'automate s'il ne l'est pas déjà."""
        pass
    
    def afficher(self) -> str:
        """Affichage spécifique aux ADC."""
        pass


class AFDC(ADC):
    """
    Automate Fini Déterministe Complet.
    
    Surcharge des méthodes d'ADC pour les propriétés spécifiques aux AFDC.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFDC."""
        pass
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        pass
    
    def minimiser(self) -> 'AFDC':
        """Retourne l'automate minimal équivalent."""
        pass
    
    def complementaire(self) -> 'AFDC':
        """Retourne l'automate complémentaire."""
        pass


class AND(Automate):
    """
    Automate Non Déterministe.
    
    Surcharge des méthodes de l'automate pour respecter les propriétés
    spécifiques aux automates non déterministes.
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AND."""
        pass
    
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
        pass
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        pass
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        pass
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        pass


class AFND(AND):
    """
    Automate Fini Non Déterministe.
    
    Composants:
    - alphabet: Σ ensemble fini de symboles
    - etats: Q ensemble fini d'états  
    - etat_initial: état initial
    - etats_finaux: F ⊂ Q états finaux
    - fonction_transition: δ ⊂ Q × Σ × Q relation de transition
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFND."""
        pass
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        pass
    
    def construction_sous_ensembles(self) -> AFDC:
        """Algorithme de construction des sous-ensembles pour déterminiser."""
        pass


class AFNS(AFND):
    """
    Automate Fini à Transitions Spontanées (ε-transitions).
    
    Composants:
    - alphabet: Σ ensemble fini de symboles
    - etats: Q ensemble fini d'états
    - etat_initial: I ∈ Q état initial
    - etats_finaux: F ⊂ Q états finaux
    - fonction_transition: δ ⊂ Q × (Σ ∪ {ε}) × Q relation de transition
    """
    
    def __init__(self, alphabet: Set[str], etats: Set[str], etat_initial: str, 
                 etats_finaux: Set[str]) -> None:
        """Initialise un AFNS."""
        pass
    
    def ajouter_transition_epsilon(self, etat_source: str, etat_cible: str) -> None:
        """Ajoute une ε-transition."""
        pass
    
    def supprimer_transition_epsilon(self, etat_source: str, etat_cible: str) -> None:
        """Supprime une ε-transition."""
        pass
    
    def epsilon_fermeture(self, etat: str) -> Set[str]:
        """Calcule l'ε-fermeture d'un état."""
        pass
    
    def epsilon_fermeture_ensemble(self, ensemble_etats: Set[str]) -> Set[str]:
        """Calcule l'ε-fermeture d'un ensemble d'états."""
        pass
    
    def transiter(self, ensemble_etats: Set[str], symbole: str) -> Set[str]:
        """Calcule les transitions depuis un ensemble d'états avec un symbole."""
        pass
    
    def construction_sous_ensembles(self) -> AFDC:
        """
        Construction des sous-ensembles.
        Entrée: Un AFNS
        Sortie: Un AFDC équivalent
        """
        pass
    
    def eliminer_epsilon_transitions(self) -> AFND:
        """Élimine les ε-transitions pour obtenir un AFND équivalent."""
        pass


class AutomateCanonique(AFDC):
    """
    Automate canonique selon le théorème de Myhill-Nerode.
    
    Implémente les concepts de:
    - Théorème 15 (De Myhill-Nerode)
    - Théorème 16 (Automate canonique)
    - Minimisation
    """
    
    def __init__(self, langage: 'LangageReconnaissable') -> None:
        """Construit l'automate canonique d'un langage."""
        pass
    
    def relation_equivalence_droite(self, mot1: str, mot2: str) -> bool:
        """Vérifie si deux mots sont équivalents à droite."""
        pass
    
    def classe_equivalence(self, mot: str) -> Set[str]:
        """Retourne la classe d'équivalence d'un mot."""
        pass
    
    def nombre_classes_equivalence(self) -> int:
        """Retourne le nombre de classes d'équivalence."""
        pass
    
    def construire_depuis_langage(self, langage: 'LangageReconnaissable') -> None:
        """Construit l'automate canonique depuis un langage."""
        pass
    
    def est_minimal(self) -> bool:
        """Vérifie si l'automate est minimal."""
        pass


class Mot:
    """
    Classe représentant un mot sur un alphabet.
    """
    
    def __init__(self, contenu: str = "", alphabet: Optional[Set[str]] = None) -> None:
        """
        Initialise un mot.
        
        Args:
            contenu: Chaîne de caractères représentant le mot
            alphabet: Alphabet du mot
        """
        pass
    
    def longueur(self) -> int: #Fonction_CHAP2
        """Retourne la longueur du mot."""
        pass
    
    def adjonction_occurrence_droite(self, symbole: str) -> 'Mot':##Fonction_CHAP2
        """Ajoute une occurrence d'un symbole à droite."""
        pass
    
    def adjonction_occurrence_gauche(self, symbole: str) -> 'Mot':##Fonction_CHAP2
        """Ajoute une occurrence d'un symbole à gauche."""
        pass
    
    def concatenation(self, autre_mot: 'Mot') -> 'Mot':##Fonction_CHAP2
        """Concatène avec un autre mot."""
        pass
    
    def liste_sous_mots(self) -> List['Mot']:##Fonction_CHAP2
        """Retourne la liste de tous les sous-mots."""
        pass
    
    def facteur_gauche(self, longueur: int) -> 'Mot':##Fonction_CHAP2
        """Retourne le facteur gauche de longueur donnée."""
        pass
    
    def facteur_droit(self, longueur: int) -> 'Mot':##Fonction_CHAP2
        """Retourne le facteur droit de longueur donnée."""
        pass
    
    def est_periodique(self, periode: int) -> bool:##Fonction_CHAP2
        """Vérifie si le mot est périodique avec la période donnée."""
        pass
    
    def est_primitif(self) -> bool:##Fonction_CHAP2
        """Vérifie si le mot est primitif."""
        pass
    
    def alphabet(self) -> Set[str]:##Fonction_CHAP2
        """Retourne l'alphabet du mot."""
        pass
    
    def est_reconnaissable(self, automate: Automate) -> bool:#Fonction_CHAP3
        """Vérifie si le mot est reconnaissable par un automate."""
        pass
    
    def sont_equivalents(self, autre_mot: 'Mot', automate: Automate) -> bool:#Fonction_CHAP3
        """Vérifie si deux mots sont équivalents relativement à un automate."""
        pass
    
    def __str__(self) -> str:
        """Représentation textuelle du mot."""
        pass
    
    def __eq__(self, autre: 'Mot') -> bool:
        """Égalité entre mots."""
        pass
    
    def __add__(self, autre: 'Mot') -> 'Mot':
        """Surcharge de + pour la concaténation."""
        pass


class Langage:
    """
    Classe représentant un langage (ensemble de mots).
    Surcharge d'opérateurs pour les opérations sur les langages.
    """
    
    def __init__(self, mots: Optional[Set[Mot]] = None, alphabet: Optional[Set[str]] = None) -> None:
        """
        Initialise un langage.
        
        Args:
            mots: Ensemble de mots du langage
            alphabet: Alphabet du langage
        """
        pass
    
    def taille_du_langage(self) -> Union[int, float]:#Fonction_CHAP2
        """Retourne la taille du langage (peut être infinie)."""
        pass
    
    def reunion_finie_des_langages(self, autres_langages: List['Langage']) -> 'Langage':#Fonction_CHAP2
        """Réunion finie de langages."""
        pass
    
    def concatenation_des_langages(self, autre_langage: 'Langage') -> 'Langage':#Fonction_CHAP2
        """Concaténation de deux langages."""
        pass
    
    def iteration_sur_langages(self) -> 'Langage':#Fonction_CHAP2
        """Étoile de Kleene du langage."""
        pass
    
    def quotient_de_langages(self, autre_langage: 'Langage') -> 'Langage':#Fonction_CHAP2
        """Quotient de langages."""
        pass
    
    def lemme_darden(self) -> bool:#Fonction_CHAP2
        """Application du lemme d'Arden."""
        pass
    
    def resolution_partielle_gauss(self, systeme_equations: List[str]) -> Dict[str, 'Langage']:#Fonction_CHAP2
        """Résolution partielle par méthode de Gauss."""
        pass
    
    def substitution_gauss(self, variable: str, expression: 'Langage') -> 'Langage':#Fonction_CHAP2
        """Substitution dans un système d'équations."""
        pass
    
    def type_de_langage(self) -> str:#Fonction_CHAP2
        """Détermine le type du langage dans la hiérarchie de Chomsky."""
        pass
    
    def __add__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de + pour l'union."""
        pass
    
    def __mul__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de * pour la concaténation."""
        pass
    
    def __sub__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de - pour la différence."""
        pass
    
    def __and__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de & pour l'intersection."""
        pass
    
    def __or__(self, autre: 'Langage') -> 'Langage':
        """Surcharge de | pour l'union."""
        pass


class LangageReconnaissable(Langage):#Fonction_CHAP3
    """
    Langage reconnaissable (régulier).
    Implémente les propriétés de clôture des langages reconnaissables.
    """
    
    def __init__(self, mots: Optional[Set[Mot]] = None, alphabet: Optional[Set[str]] = None,
                 automate: Optional[Automate] = None) -> None:
        """Initialise un langage reconnaissable."""
        pass
    
    def complementation(self) -> 'LangageReconnaissable':
        """Clôture par complémentation."""
        pass
    
    def union_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par union ensembliste."""
        pass
    
    def intersection_ensembliste(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par intersection ensembliste."""
        pass
    
    def miroir(self) -> 'LangageReconnaissable':
        """Clôture par miroir."""
        pass
    
    def concatenation(self, autre: 'LangageReconnaissable') -> 'LangageReconnaissable':
        """Clôture par concaténation."""
        pass
    
    def etoile(self) -> 'LangageReconnaissable':
        """Clôture par étoile (étoile de Kleene)."""
        pass
    
    def regex_vers_langage(self, expression_reguliere: str) -> None:
        """Construit le langage depuis une expression régulière."""
        pass
    
    def langage_vers_regex(self) -> str:
        """Convertit le langage en expression régulière."""
        pass
    
    def theoreme_kleene_construction(self, automate: Automate) -> str:
        """Application du théorème de Kleene pour la construction."""
        pass
    
    def lemme_pompage_verification(self, mot: Mot) -> Tuple[bool, Dict[str, Any]]:
        """Vérifie le lemme de pompage pour un mot."""
        pass
    
    def lemme_pompage_application(self) -> bool:
        """Application du lemme de pompage au langage."""
        pass


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
        pass
    
    def est_associatif(self) -> bool:#Fonction_CHAP2
        """Vérifie l'associativité de l'opération."""
        pass
    
    def verifier_element_neutre(self) -> bool:#Fonction_CHAP2
        """Vérifie l'existence de l'élément neutre."""
        pass
    
    def est_commutatif(self) -> bool:#Fonction_CHAP2
        """Vérifie si le monoïde est commutatif."""
        pass
    
    def sous_monoide(self, sous_ensemble: Set[Any]) -> 'Monoids':#Fonction_CHAP2
        """Construit un sous-monoïde."""
        pass
    
    def morphisme(self, autre_monoide: 'Monoids', fonction: callable) -> bool:#Fonction_CHAP2
        """Vérifie si une fonction est un morphisme de monoïdes."""
        pass


class Etat:#Fonction_CHAP3
    """
    Classe représentant un état dans un automate avec ses propriétés.
    """
    
    def __init__(self, nom: str, automate: Automate) -> None:
        """
        Initialise un état.
        
        Args:
            nom: Nom de l'état
            automate: Automate auquel appartient l'état
        """
        pass
    
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
    
