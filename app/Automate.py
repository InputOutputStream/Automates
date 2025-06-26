from abc import ABC
from typing import Set, Dict, List, Optional
from .Etat import Etat
from .Langage import Langage
from collections import deque
from .Mot import Mot



class Automate(ABC):
    """
    Classe représentant un automate selon la définition du cours.
    
    - alphabet: ensemble de symboles
    - etats: ensemble d'états
    - etat_initial: état de départ
    - etats_finaux: ensemble d'états finaux
    - fonction_transition: fonction de transition
    """
    
    def __init__(self, alphabet: Set[str], 
                 etats_finaux: Optional[Set[Etat]] = None,
                 etats: Optional[Set[Etat]] = None, 
                 etat_initial : Optional[Etat] = None) -> None:
        """
        Initialise l'automate avec ses composants de base.
        
        Args:
            alphabet: Ensemble des symboles de l'alphabet
            etats: Ensemble des états
            etat_initial: État initial
            etats_finaux: Ensemble des états finaux
        """
        self.alphabet = set(alphabet) if alphabet is not None else set()
        self.transitions = {}

        if etats is not None:
            self.etats = etats  
        else :
            raise ValueError("Un automate doit avoir des etats")
        
        if etat_initial is not None and etat_initial in self.etats:
            self.etat_initial = etat_initial  
            self.etat_initial.est_initial = True
        else :
            raise ValueError("L'état initial doit être défini et appartenir aux états")
        
        
        if not etats_finaux or not etats_finaux.issubset(self.etats):
            raise ValueError("Tous les états finaux doivent faire partie de l'ensemble des états.")

        else :
            self.etats_finaux = etats_finaux  
            for etat in self.etats_finaux:
                etat.est_final = True
                
    def ajouter_transition(self, source: Etat, symbole: str, destination: Etat):
        """Ajoute une transition à l'automate et enregistre les états concernés."""
        if source not in self.transitions:
            self.transitions[source] = {}
        if symbole not in self.transitions[source]:
            self.transitions[source][symbole] = set()
        self.transitions[source][symbole].add(destination)

        # Assure-toi d'ajouter les états dans l'ensemble des états
        self.etats.add(source)
        self.etats.add(destination)


    def fermeture_epsilon(self, etats: Set[Etat]) -> Set[Etat]:
        """
        Calcule la fermeture epsilon d'un ensemble d'états.
        Utilise '' ou 'ε' comme symbole epsilon.
        """
        fermeture = set(etats)
        pile = list(etats)
        
        while pile:
            etat_courant = pile.pop()
            
            # Vérifier les transitions epsilon ('' ou 'ε')
            for epsilon in ['', 'ε']:
                if (etat_courant in self.transitions and 
                    epsilon in self.transitions[etat_courant]):
                    
                    for etat_destination in self.transitions[etat_courant][epsilon]:
                        if etat_destination not in fermeture:
                            fermeture.add(etat_destination)
                            pile.append(etat_destination)
        
        return fermeture

    def determinisation_thompson(self) -> 'AD':
        """
        Déterminisation par l'algorithme de Thompson.
        Utilise la construction par sous-ensembles avec fermeture epsilon.
        """
        # État initial : fermeture epsilon de l'état initial
        etat_initial_det = self.fermeture_epsilon({self.etat_initial})
        
        # Structures pour la construction
        etats_det = {}  # Dict: frozenset -> Etat
        transitions_det = {}
        etats_a_traiter = deque()
        
        # Créer l'état initial déterministe
        nom_initial = "{" + ",".join(sorted(e.nom for e in etat_initial_det)) + "}"
        etat_initial_automate_det = Etat(nom_initial)
        etats_det[frozenset(etat_initial_det)] = etat_initial_automate_det
        etats_a_traiter.append(etat_initial_det)
        
        while etats_a_traiter:
            ensemble_courant = etats_a_traiter.popleft()
            etat_courant_det = etats_det[frozenset(ensemble_courant)]
            
            # Pour chaque symbole de l'alphabet
            for symbole in self.alphabet:
                if symbole in ['', 'ε']:  # Ignorer epsilon
                    continue
                    
                # Calculer l'ensemble des états accessibles
                etats_accessibles = set()
                
                for etat in ensemble_courant:
                    if (etat in self.transitions and 
                        symbole in self.transitions[etat]):
                        etats_accessibles.update(self.transitions[etat][symbole])
                
                if not etats_accessibles:
                    continue
                
                # Appliquer la fermeture epsilon
                nouvel_ensemble = self.fermeture_epsilon(etats_accessibles)
                
                if not nouvel_ensemble:
                    continue
                
                # Créer ou récupérer l'état déterministe correspondant
                if frozenset(nouvel_ensemble) not in etats_det:
                    nom_nouvel_etat = "{" + ",".join(sorted(e.nom for e in nouvel_ensemble)) + "}"
                    nouvel_etat_det = Etat(nom_nouvel_etat)
                    etats_det[frozenset(nouvel_ensemble)] = nouvel_etat_det
                    etats_a_traiter.append(nouvel_ensemble)
                else:
                    nouvel_etat_det = etats_det[frozenset(nouvel_ensemble)]
                
                # Ajouter la transition
                if etat_courant_det not in transitions_det:
                    transitions_det[etat_courant_det] = {}
                if symbole not in transitions_det[etat_courant_det]:
                    transitions_det[etat_courant_det][symbole] = set()
                transitions_det[etat_courant_det][symbole].add(nouvel_etat_det)
        
        # Déterminer les états finaux
        etats_finaux_det = set()
        for ensemble_etats, etat_det in etats_det.items():
            if any(etat in self.etats_finaux for etat in ensemble_etats):
                etats_finaux_det.add(etat_det)
        
        # Créer l'automate déterministe
        print(self.alphabet,
            set(etats_det.values()),
            etat_initial_automate_det,
            etats_finaux_det
        )

        automate_det = AD(
            alphabet=self.alphabet,
            etats=set(etats_det.values()),
            etat_initial=etat_initial_automate_det,
            etats_finaux=etats_finaux_det
        )
        automate_det.transitions = transitions_det
        
        return automate_det
    
    def deterterminisation_glushkov(self):
        pass

    def automate_a_matrice(self):
        """Conversion temporaire pour algorithmes matriciels"""
        etats_list = list(self.etats)
        alphabet_list = list(self.alphabet)
        n = len(etats_list)
        m = len(alphabet_list)
        
        matrice = [[set() for _ in range(m)] for _ in range(n)]
        
        for i, etat in enumerate(etats_list):
            if etat in self.transitions:
                for j, symbole in enumerate(alphabet_list):
                    if symbole in self.transitions[etat]:
                        for dest in self.transitions[etat][symbole]:
                            k = etats_list.index(dest)
                            matrice[i][j].add(k)
        
        return matrice, etats_list, alphabet_list

   
    def supprimer_transition(self, etat_source: str, symbole: str, etat_cible: str) -> None:
        """Supprime une transition de l'automate."""
        if (etat_source in self.transitions and 
            symbole in self.transitions[etat_source] and
            etat_cible in self.transitions[etat_source][symbole]):
            
            self.transitions[etat_source][symbole].remove(etat_cible)
            
            # Nettoyer les structures vides
            if not self.transitions[etat_source][symbole]:
                del self.transitions[etat_source][symbole]
            if not self.transitions[etat_source]:
                del self.transitions[etat_source]
        else:
            raise IndexError("etat_source, etat_cible ou transisions inconnu")
    
    def obtenir_transitions(self, etat: str, symbole: str) -> Set[str]:
        """Retourne l'ensemble des états accessibles depuis un état avec un symbole."""
        if etat in self.transitions and symbole in self.transitions[etat]:
            return self.transitions[etat][symbole]
        return set()    
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Détermine si un mot est reconnu par l'automate."""
        return self._reconnaitre_recursif(mot, self.etat_initial)

    def _reconnaitre_recursif(self, mot: str, etat_courant: Etat):
        """Fonction récursive pour la reconnaissance de mots."""

        if not mot:
            return etat_courant.est_final
    
        symbole = mot[0]
        reste_du_mot = mot[1:]

        etats_suivants = self.obtenir_transitions(etat_courant, symbole)

        for etat_suivant in etats_suivants:
            if self._reconnaitre_recursif(reste_du_mot, etat_suivant):
                return True
                
        return False
    
    def est_deterministe(self) -> bool:
        """Vérifie si l'automate est déterministe."""
        """
            En princippe ici "" est notre epsilon, mais on va voir comment il se comporte 
            avec les testes
        """
        for etat in self.etats:
            if etat in self.transitions:
                for symbole in self.alphabet:
                    if symbole in self.transitions[etat]:
                        if len(self.transitions[etat][symbole]) > 1:
                            return False
        return True
       
    def est_complet(self) -> bool:
        """Vérifie si l'automate est complet."""
        for etat in self.etats:
            for symbole in self.alphabet:
                if not self.obtenir_transitions(etat, symbole):
                    return False
        return True
    
    def afficher(self) -> str:
        result = []
        result.append(f"AD:")
        result.append(f"Alphabet: {sorted(self.alphabet)}")
        result.append(f"États: {[str(e) for e in sorted(self.etats, key=str)]}")
        result.append(f"État initial: {self.etat_initial}")
        result.append(f"États finaux: {[str(e) for e in sorted(self.etats_finaux, key=str)]}")
        result.append("Transitions:")
        
        for etat_source in sorted(self.etats, key=str):
            if etat_source in self.transitions:
                for symbole in sorted(self.transitions[etat_source]):
                    for dest in sorted(self.transitions[etat_source][symbole], key=str):
                        result.append(f"  {etat_source} --{symbole}--> {dest}")
        
        return "\n".join(result)


    
    def matrice_a_automate(self, matrice: list[list]):
        """
        Convertit une matrice de transitions en un automate.
        Args:
            matrice: Liste de listes où matrice[i][j] contient les indices des états destinations
                    pour l'état i et le symbole j de l'alphabet.
        """
        if not matrice or not matrice[0]:
            raise ValueError("Matrice invalide")

        n = len(matrice)  # Nombre d'états
        m = len(matrice[0])  # Nombre de symboles

        # Créer un alphabet par défaut (par exemple, 'a', 'b', ..., ou utiliser un alphabet donné)
        alphabet = {chr(97 + j) for j in range(m)}  # 'a', 'b', etc.
        
        # Créer les états
        etats = {Etat(f"q{i}") for i in range(n)}
        
        # Identifier l'état initial (par convention, q0)
        etat_initial = next(e for e in etats if e.nom == "q0")
        etat_initial.est_initial = True
        
        # Identifier les états finaux (par exemple, dernier état ou configurable)
        # Convention : dernier état est final (peut être modifié selon le contexte)
        etats_finaux = {next(e for e in etats if e.nom == f"q{n-1}")}
        for e in etats_finaux:
            e.est_final = True
        
        # Initialiser l'automate
        self.alphabet = alphabet
        self.etats = etats
        self.etat_initial = etat_initial
        self.etats_finaux = etats_finaux
        self.transitions = {}
        
        # Ajouter les transitions à partir de la matrice
        alphabet_list = sorted(list(alphabet))
        for i in range(n):
            source = next(e for e in etats if e.nom == f"q{i}")
            for j in range(m):
                symbole = alphabet_list[j]
                for dest_idx in matrice[i][j]:
                    if dest_idx < n:
                        destination = next(e for e in etats if e.nom == f"q{dest_idx}")
                        self.ajouter_transition(source, symbole, destination)
    



class AD(Automate):
    """Automate Déterministe simple,on peut le completer,le minimiser"""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un ADC."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_deterministe():
            raise ValueError("L'automate doit être déterministe")
        #self.completer()
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Ajoute une transition en respectant le déterminisme."""
        if etat_source in self.transitions and symbole in self.transitions[etat_source]:
            if self.transitions[etat_source][symbole]:
                raise ValueError("Transition déjà définie - violation du déterminisme")
        super().ajouter_transition(etat_source, symbole, etat_cible)
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition en maintenant la complétude."""
        super().supprimer_transition(etat_source, symbole, etat_cible)
        self.completer()  # Maintenir la complétude
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        """Retourne exactement un état (déterminisme)."""
        transitions = super().obtenir_transitions(etat, symbole)
        return transitions  # Sera toujours de taille 0 ou 1 pour un ADC
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance déterministe d'un mot."""
        etat_courant = self.etat_initial
        for symbole in mot:
            transitions = self.obtenir_transitions(etat_courant, symbole)
            if not transitions:
                return False
            etat_courant = next(iter(transitions))  # Un seul état possible
        return etat_courant.est_final
    
    def est_deterministe(self) -> bool:
        """Retourne toujours True pour un ADC."""
        return True
    
    def est_complet(self) -> bool:
        """Retourne toujours True pour un ADC."""
        return True
    
    def completer(self) -> 'ADC':
        """
        Retourne un nouvel automate déterministe complet (ADC) en complétant l'automate actuel.
        """
        # Créer un nouvel automate avec les arguments requis
        adc = AD(
            alphabet=self.alphabet.copy(),
            etats_finaux=self.etats_finaux.copy(),
            etats=self.etats.copy(),
            etat_initial=self.etat_initial
        )

        # Ajouter les transitions de self à adc
        for source in self.transitions:
            for symbole, destinations in self.transitions[source].items():
                for dest in destinations:
                    adc.ajouter_transition(source, symbole, dest)

        # Ajouter l’état puits
        etat_puits = Etat("puits", est_final=False)
        adc.etats.add(etat_puits)

        # Compléter les transitions manquantes vers puits
        for etat in adc.etats:
            for symbole in adc.alphabet:
                if not adc.obtenir_transitions(etat, symbole):
                    adc.ajouter_transition(etat, symbole, etat_puits)

        # Compléter le puits avec des boucles sur lui-même
        for symbole in adc.alphabet:
            if not adc.obtenir_transitions(etat_puits, symbole):
                adc.ajouter_transition(etat_puits, symbole, etat_puits)

        return adc

    
    def afficher(self) -> str:
        """Affichage spécifique aux ADC."""
        return f"AD:\n{super().afficher()}"

    def minimiser(self) -> 'AFDC':
        """Retourne l'automate minimal équivalent."""
        # Algorithme de minimisation par classes d'équivalence
        classes = self._calculer_classes_equivalence()
        return self._construire_automate_minimal(classes)
    
    def _calculer_classes_equivalence(self) -> List[Set[Etat]]:
        """Calcule les classes d'équivalence pour la minimisation."""
        # Partition initiale : états finaux vs non-finaux
        finaux = set(self.etats_finaux)
        non_finaux = self.etats - finaux
        
        partition = []
        if finaux:
            partition.append(finaux)
        if non_finaux:
            partition.append(non_finaux)
        
        # Raffiner la partition
        changed = True
        while changed:
            changed = False
            nouvelle_partition = []
            
            for classe in partition:
                sous_classes = self._raffiner_classe(classe, partition)
                if len(sous_classes) > 1:
                    changed = True
                nouvelle_partition.extend(sous_classes)
            
            partition = nouvelle_partition
        
        return partition
    
    def _raffiner_classe(self, classe: Set[Etat], partition: List[Set[Etat]]) -> List[Set[Etat]]:
        """Raffine une classe d'équivalence."""
        if len(classe) <= 1:
            return [classe]
        
        sous_classes = {}
        for etat in classe:
            signature = []
            for symbole in sorted(self.alphabet):
                transitions = self.obtenir_transitions(etat, symbole)
                if transitions:
                    dest = next(iter(transitions))
                    # Trouver la classe de destination
                    classe_dest = None
                    for i, p in enumerate(partition):
                        if dest in p:
                            classe_dest = i
                            break
                    signature.append(classe_dest)
                else:
                    signature.append(None)
            
            signature_key = tuple(signature)
            if signature_key not in sous_classes:
                sous_classes[signature_key] = set()
            sous_classes[signature_key].add(etat)
        
        return list(sous_classes.values())
    
    def _construire_automate_minimal(self, classes: List[Set[Etat]]) -> 'AFDC':
        """Construit l'automate minimal à partir des classes d'équivalence."""
        # Créer les nouveaux états
        nouveaux_etats = set()
        classe_vers_etat = {}
        
        for i, classe in enumerate(classes):
            nouvel_etat = Etat(f"C{i}")
            nouveaux_etats.add(nouvel_etat)
            classe_vers_etat[i] = nouvel_etat
            
            # Vérifier si c'est un état final
            if any(etat.est_final for etat in classe):
                nouvel_etat.est_final = True
        
        # Trouver l'état initial
        etat_initial_classe = None
        for i, classe in enumerate(classes):
            if self.etat_initial in classe:
                etat_initial_classe = classe_vers_etat[i]
                break
        
        # États finaux
        etats_finaux = {etat for etat in nouveaux_etats if etat.est_final}
        
        # Créer le nouvel automate
        automate_minimal = AFDC(self.alphabet, etats_finaux, nouveaux_etats, etat_initial_classe)
        
        # Ajouter les transitions
        for i, classe in enumerate(classes):
            etat_representant = next(iter(classe))
            etat_source = classe_vers_etat[i]
            
            for symbole in self.alphabet:
                transitions = self.obtenir_transitions(etat_representant, symbole)
                if transitions:
                    dest = next(iter(transitions))
                    # Trouver la classe de destination
                    for j, classe_dest in enumerate(classes):
                        if dest in classe_dest:
                            etat_dest = classe_vers_etat[j]
                            automate_minimal.ajouter_transition(etat_source, symbole, etat_dest)
                            break
        
        return automate_minimal



class ADC(AD):
    """Automate Déterministe Complet."""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un ADC."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_deterministe():
            raise ValueError("L'automate doit être déterministe")
        if not self.est_complet():
            raise ValueError("L'automate doit être complet")

class AFDC(ADC):
    """Automate Fini Déterministe Complet."""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un AFDC."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_fini():
            raise ValueError("L'automate doit être fini")
        
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        return len(self.etats) < float('inf') and len(self.alphabet) < float('inf')
    
    
    
    def complementaire(self) -> 'AFDC':
        """Retourne l'automate complémentaire."""
        # Inverser les états finaux et non-finaux
        nouveaux_etats_finaux = self.etats - self.etats_finaux
        
        # Créer le nouvel automate
        automate_comp = AFDC(self.alphabet.copy(), self.etats.copy(), 
                            self.etat_initial, nouveaux_etats_finaux)
        
        # Copier les transitions
        automate_comp.transitions = self.transitions.copy()
        
        return automate_comp

    def canonisation(self) -> 'AutomateCanonique':
        return AutomateCanonique(langage=self.langage)

    
    def langage_accepte(self, longueur_max: int = 5) -> Langage:
        from app.Mot import Mot
        from app.Langage import Langage

        alphabet = self.alphabet
        mots_acceptes = set()

        def generer_mots(prefixe: str):
            if len(prefixe) > longueur_max:
                return
            if self.accepte(prefixe):
                mot_objet = Mot(prefixe, alphabet)
                mots_acceptes.add(mot_objet)
            for lettre in alphabet:
                generer_mots(prefixe + lettre)

        generer_mots("")

        return Langage(mots_acceptes, alphabet, est_infini=False)

    def accepte(self, mot: str) -> bool:
        """
        Vérifie si le mot est accepté par l'automate déterministe (AFD).
        """
        etat_courant = self.etat_initial
        for symbole in mot:
            transitions = self.obtenir_transitions(etat_courant, symbole)
            if not transitions:
                return False
            # Comme c'est déterministe, on prend la seule transition
            etat_courant = next(iter(transitions))
        return etat_courant in self.etats_finaux



class AND(Automate):
    """Automate Non Déterministe."""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un AND."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
    
    def ajouter_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Ajoute une transition non déterministe."""
        super().ajouter_transition(etat_source, symbole, etat_cible)
    
    def supprimer_transition(self, etat_source: Etat, symbole: str, etat_cible: Etat) -> None:
        """Supprime une transition non déterministe."""
        super().supprimer_transition(etat_source, symbole, etat_cible)
    
    def obtenir_transitions(self, etat: Etat, symbole: str) -> Set[Etat]:
        """Retourne un ensemble d'états (non déterminisme)."""
        return super().obtenir_transitions(etat, symbole)
    
    def reconnaitre_mot(self, mot: str) -> bool:
        """Reconnaissance non déterministe d'un mot."""
        return super().reconnaitre_mot(mot)
    
    def est_deterministe(self) -> bool:
        """Vérifie le déterminisme."""
        return super().est_deterministe()
    
    def est_complet(self) -> bool:
        """Vérifie la complétude."""
        return super().est_complet()
    
    def determiniser(self) -> ADC:
        """Convertit en automate déterministe équivalent."""
        # Construction des sous-ensembles
        nouvel_alphabet = self.alphabet.copy()
        nouveaux_etats = set()
        nouvelles_transitions = {}
        
        # État initial = {etat_initial}
        etat_initial_ensemble = frozenset([self.etat_initial])
        nouveaux_etats.add(etat_initial_ensemble)
        
        # File pour BFS
        file = deque([etat_initial_ensemble])
        traites = set([etat_initial_ensemble])
        
        while file:
            ensemble_courant = file.popleft()
            
            for symbole in self.alphabet:
                # Calculer l'ensemble des états accessibles
                nouvel_ensemble = set()
                for etat in ensemble_courant:
                    nouvel_ensemble.update(self.obtenir_transitions(etat, symbole))
                
                if nouvel_ensemble:
                    nouvel_ensemble_frozen = frozenset(nouvel_ensemble)
                    
                    if nouvel_ensemble_frozen not in traites:
                        nouveaux_etats.add(nouvel_ensemble_frozen)
                        file.append(nouvel_ensemble_frozen)
                        traites.add(nouvel_ensemble_frozen)
                    
                    # Ajouter la transition
                    if ensemble_courant not in nouvelles_transitions:
                        nouvelles_transitions[ensemble_courant] = {}
                    if symbole not in nouvelles_transitions[ensemble_courant]:
                        nouvelles_transitions[ensemble_courant][symbole] = set()
                    nouvelles_transitions[ensemble_courant][symbole].add(nouvel_ensemble_frozen)
        
        # Créer les états du nouvel automate
        etat_mapping = {}
        etats_adc = set()
        
        for i, ensemble in enumerate(nouveaux_etats):
            nom_etat = "{" + ",".join(sorted([str(e) for e in ensemble])) + "}"
            nouvel_etat = Etat(nom_etat)
            etat_mapping[ensemble] = nouvel_etat
            etats_adc.add(nouvel_etat)
        
        # État initial
        etat_initial_adc = etat_mapping[etat_initial_ensemble]
        
        # États finaux (contiennent au moins un état final original)
        etats_finaux_adc = set()
        for ensemble in nouveaux_etats:
            if any(etat.est_final for etat in ensemble):
                etats_finaux_adc.add(etat_mapping[ensemble])
        
        # Créer l'ADC
        adc = ADC(nouvel_alphabet, etats_adc, etat_initial_adc, etats_finaux_adc)
        
        # Ajouter les transitions
        for source, transitions_source in nouvelles_transitions.items():
            for symbole, destinations in transitions_source.items():
                for dest in destinations:
                    adc.ajouter_transition(etat_mapping[source], symbole, etat_mapping[dest])
        
        return adc
    
    def afficher(self) -> str:
        """Affichage spécifique aux AND."""
        return f"AND:\n{super().afficher()}"


class AFND(AND):
    """Automate Fini Non Déterministe."""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un AFND."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        if not self.est_fini():
            raise ValueError("L'automate doit être fini")
    
    def est_fini(self) -> bool:
        """Vérifie que l'automate est fini."""
        return len(self.etats) < float('inf') and len(self.alphabet) < float('inf')
    
    def construction_sous_ensembles(self) -> AFDC:
        """Algorithme de construction des sous-ensembles pour déterminiser."""
        adc = self.determiniser()
        # Convertir ADC en AFDC
        return AFDC(adc.alphabet, adc.etats, adc.etat_initial, adc.etats_finaux)


class AFNS(AFND):
    """Automate Fini à Transitions Spontanées (ε-transitions)."""
    
    def __init__(self, alphabet: Set[str], etats_finaux: Set[Etat], etats: Set[Etat],
                 etat_initial: Etat) -> None:
        """Initialise un AFNS."""
        super().__init__(alphabet, etats_finaux, etats, etat_initial)
        self.epsilon = ""  # Représentation d'epsilon
    
    def ajouter_transition_epsilon(self, etat_source: Etat, etat_cible: Etat) -> None:
        """Ajoute une ε-transition."""
        self.ajouter_transition(etat_source, self.epsilon, etat_cible)
    
    def supprimer_transition_epsilon(self, etat_source: Etat, etat_cible: Etat) -> None:
        """Supprime une ε-transition."""
        self.supprimer_transition(etat_source, self.epsilon, etat_cible)
    
    def epsilon_fermeture(self, etat: Etat) -> Set[Etat]:
        """Calcule l'ε-fermeture d'un état."""
        fermeture = {etat}
        pile = [etat]
        
        while pile:
            etat_courant = pile.pop()
            transitions_epsilon = self.obtenir_transitions(etat_courant, self.epsilon)
            
            for etat_suivant in transitions_epsilon:
                if etat_suivant not in fermeture:
                    fermeture.add(etat_suivant)
                    pile.append(etat_suivant)
        
        return fermeture
    
    def epsilon_fermeture_ensemble(self, ensemble_etats: Set[Etat]) -> Set[Etat]:
        """Calcule l'ε-fermeture d'un ensemble d'états."""
        fermeture = set()
        for etat in ensemble_etats:
            fermeture.update(self.epsilon_fermeture(etat))
        return fermeture
    
    def transiter(self, ensemble_etats: Set[Etat], symbole: str) -> Set[Etat]:
        """Calcule les transitions depuis un ensemble d'états avec un symbole."""
        if symbole == self.epsilon:
            return self.epsilon_fermeture_ensemble(ensemble_etats)
        
        etats_atteignables = set()
        for etat in ensemble_etats:
            etats_atteignables.update(self.obtenir_transitions(etat, symbole))
        
        return self.epsilon_fermeture_ensemble(etats_atteignables)
    
    def construction_sous_ensembles(self) -> AFDC:
        """Construction des sous-ensembles pour un AFNS."""
        nouvel_alphabet = self.alphabet.copy()
        nouvel_alphabet.discard(self.epsilon)  # Retirer epsilon de l'alphabet
        
        nouveaux_etats = set()
        nouvelles_transitions = {}
        
        # État initial = ε-fermeture(etat_initial)
        etat_initial_ensemble = self.epsilon_fermeture(self.etat_initial)
        etat_initial_frozen = frozenset(etat_initial_ensemble)
        nouveaux_etats.add(etat_initial_frozen)
        
        # File pour BFS
        file = deque([etat_initial_frozen])
        traites = set([etat_initial_frozen])
        
        while file:
            ensemble_courant = file.popleft()
            
            for symbole in nouvel_alphabet:
                nouvel_ensemble = self.transiter(set(ensemble_courant), symbole)
                
                if nouvel_ensemble:
                    nouvel_ensemble_frozen = frozenset(nouvel_ensemble)
                    
                    if nouvel_ensemble_frozen not in traites:
                        nouveaux_etats.add(nouvel_ensemble_frozen)
                        file.append(nouvel_ensemble_frozen)
                        traites.add(nouvel_ensemble_frozen)
                    
                    # Ajouter la transition
                    if ensemble_courant not in nouvelles_transitions:
                        nouvelles_transitions[ensemble_courant] = {}
                    if symbole not in nouvelles_transitions[ensemble_courant]:
                        nouvelles_transitions[ensemble_courant][symbole] = set()
                    nouvelles_transitions[ensemble_courant][symbole].add(nouvel_ensemble_frozen)
        
        # Créer les états du nouvel automate
        etat_mapping = {}
        etats_afdc = set()
        
        for i, ensemble in enumerate(nouveaux_etats):
            nom_etat = "{" + ",".join(sorted([str(e) for e in ensemble])) + "}"
            nouvel_etat = Etat(nom_etat)
            etat_mapping[ensemble] = nouvel_etat
            etats_afdc.add(nouvel_etat)
        
        # État initial
        etat_initial_afdc = etat_mapping[etat_initial_frozen]
        
        # États finaux
        etats_finaux_afdc = set()
        for ensemble in nouveaux_etats:
            if any(etat.est_final for etat in ensemble):
                etats_finaux_afdc.add(etat_mapping[ensemble])
        
        # Créer l'AFDC
        afdc = AFDC(nouvel_alphabet, etats_afdc, etat_initial_afdc, etats_finaux_afdc)
        
        # Ajouter les transitions
        for source, transitions_source in nouvelles_transitions.items():
            for symbole, destinations in transitions_source.items():
                for dest in destinations:
                    afdc.ajouter_transition(etat_mapping[source], symbole, etat_mapping[dest])
        
        return afdc
    
    def eliminer_epsilon_transitions(self) -> AFND:
        """Élimine les ε-transitions pour obtenir un AFND équivalent."""
        nouvel_alphabet = self.alphabet.copy()
        nouvel_alphabet.discard(self.epsilon)
        
        # Créer le nouvel automate sans epsilon
        afnd = AFND(nouvel_alphabet, self.etats.copy(), self.etat_initial, set())
        
        # Recalculer les états finaux
        nouveaux_etats_finaux = set()
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            if any(e.est_final for e in fermeture):
                nouveaux_etats_finaux.add(etat)
        
        afnd.etats_finaux = nouveaux_etats_finaux
        
        # Ajouter les nouvelles transitions
        for etat in self.etats:
            fermeture = self.epsilon_fermeture(etat)
            for symbole in nouvel_alphabet:
                etats_atteignables = set()
                for e in fermeture:
                    etats_atteignables.update(self.obtenir_transitions(e, symbole))
                
                for etat_dest in etats_atteignables:
                    fermeture_dest = self.epsilon_fermeture(etat_dest)
                    for e_dest in fermeture_dest:
                        afnd.ajouter_transition(etat, symbole, e_dest)
        
        return afnd




class AutomateCanonique:
    def __init__(self, langage: Langage, suffixe_longueur_max: int = 3):
        """
        Initialise un automate canonique à partir d'un langage fini.
        
        Args:
            langage: Langage fini sur lequel construire l'automate canonique.
            suffixe_longueur_max: longueur max des suffixes testés pour la relation d'équivalence.
        """
        if langage.langage_fini is False:
            raise ValueError("Le langage doit être fini pour construire un automate canonique.")
        
        self.langage = langage
        self.alphabet = langage.alphabet
        self.suffixe_longueur_max = suffixe_longueur_max
        
        self.etats: Dict[str, Etat] = {}  # clé = mot représentant la classe
        self.transitions: Dict[Etat, Dict[str, Etat]] = {}  # transitions : état x symbole -> état
        
        # Construire l'automate
        self._construire_automate()
    
    def _sont_equivalents(self, u: Mot, v: Mot) -> bool:
        """
        Teste si deux mots u et v sont équivalents selon Myhill-Nerode:
        Pour tout suffixe w (de longueur jusqu'à suffixe_longueur_max),
        uw ∈ L ⇔ vw ∈ L
        """
        # Générer tous les suffixes w possibles sur l'alphabet jusqu'à longueur max
        suffixes = self._generer_suffixes(max_len=self.suffixe_longueur_max)
        
        for w in suffixes:
            uw = u.concatenation(w)
            vw = v.concatenation(w)
            if self.langage.accepte(uw) != self.langage.accepte(vw):
                return False
        return True
    
    def _generer_suffixes(self, max_len: int) -> List[Mot]:
        """
        Génère tous les mots (suffixes) sur l'alphabet jusqu'à longueur max_len (incluse).
        """
        from itertools import product
        
        suffixes = []
        for l in range(max_len + 1):
            for lettres in product(self.alphabet, repeat=l):
                mot = Mot(''.join(lettres), list(self.alphabet))
                suffixes.append(mot)
        return suffixes
    
    def _trouver_classe_equivalence(self, mot: Mot) -> Etat:
        """
        Trouve ou crée un état représentant la classe d'équivalence du mot donné.
        """
        # Cherche un état existant équivalent
        for rep_mot, etat in self.etats.items():
            mot_rep = Mot(rep_mot, list(self.alphabet))
            if self._sont_equivalents(mot, mot_rep):
                return etat
        
        # Sinon crée un nouvel état
        nom_etat = mot.contenu if mot.contenu != '' else 'ε'
        est_final = self.langage.accepte(mot)
        nouvel_etat = Etat(nom_etat, est_initial=False, est_final=est_final)
        
        # Associer l'automate à l'état pour pouvoir utiliser les méthodes d'accessibilité si besoin
        nouvel_etat.automate = self  
        
        self.etats[mot.contenu] = nouvel_etat
        return nouvel_etat
    
    def _construire_automate(self):
        """
        Construit l'automate canonique en explorant les classes d'équivalence.
        """
        # Etat initial = classe du mot vide
        mot_vide = Mot("", list(self.alphabet))
        etat_initial = self._trouver_classe_equivalence(mot_vide)
        etat_initial.est_initial = True
        
        self.etat_initial = etat_initial
        
        # File pour exploration BFS des états
        file = deque([etat_initial])
        self.transitions[etat_initial] = {}
        
        while file:
            etat_courant = file.popleft()
            mot_courant = Mot(etat_courant.nom if etat_courant.nom != 'ε' else "", list(self.alphabet))
            
            for a in self.alphabet:
                mot_suivant = mot_courant.concatenation(Mot(a, list(self.alphabet)))
                etat_suivant = self._trouver_classe_equivalence(mot_suivant)
                
                if etat_courant not in self.transitions:
                    self.transitions[etat_courant] = {}
                
                if a not in self.transitions[etat_courant]:
                    self.transitions[etat_courant][a] = etat_suivant
                
                # Découverte d'un nouvel état
                if etat_suivant not in self.transitions:
                    self.transitions[etat_suivant] = {}
                    file.append(etat_suivant)
    
    def affiche(self):
        """
        Affiche l'automate (états, initiaux, finaux, transitions).
        """
        print(f"Alphabet: {self.alphabet}")
        print(f"État initial: {self.etat_initial}")
        print(f"États ({len(self.etats)}):")
        for etat in self.etats.values():
            fin_str = "(final)" if etat.est_final else ""
            init_str = "(initial)" if etat.est_initial else ""
            print(f"  - {etat} {init_str} {fin_str}")
        
        print("Transitions:")
        for etat_src, trans in self.transitions.items():
            for symb, etat_dst in trans.items():
                print(f"  δ({etat_src}, {symb}) -> {etat_dst}")





# =============================================
# DÉMONSTRATION D'UTILISATION
# =============================================

if __name__ == "__main__":
    print("=== DÉMONSTRATION DE LA CLASSE AUTOMATE ===\n")
    
    # Création des états
    q0 = Etat("q0", est_initial=True)
    q1 = Etat("q1", est_final=True) 
    q2 = Etat("q2")
    
    # Exemple 1: Automate simple qui accepte les mots finissant par 'a'
    print("1. Automate acceptant les mots finissant par 'a'")
    automate1 = Automate(
        alphabet={'a', 'b'},
        etats_finaux={q1},
        etats={q0, q1},
        etat_initial=q0
    )
    
    # Ajout des transitions
    automate1.ajouter_transition(q0, 'a', q1)  # q0 --a--> q1
    automate1.ajouter_transition(q0, 'b', q0)  # q0 --b--> q0  
    automate1.ajouter_transition(q1, 'a', q1)  # q1 --a--> q1
    automate1.ajouter_transition(q1, 'b', q0)  # q1 --b--> q0
    
    print(automate1.afficher())
    print(f"Déterministe: {automate1.est_deterministe()}")
    print(f"Complet: {automate1.est_complet()}")
    
    # Test de reconnaissance
    mots_test = ["a", "ba", "bba", "ab", "bb", ""]
    for mot in mots_test:
        resultat = automate1.reconnaitre_mot(mot)
        print(f"Mot '{mot}': {'✓' if resultat else '✗'}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 2: Automate non-déterministe
    print("2. Automate non-déterministe (deux transitions pour 'a' depuis q0)")
    automate2 = Automate(
        alphabet={'a', 'b'},
        etats_finaux={q2},
        etats={q0, q1, q2},
        etat_initial=q0
    )
    
    # Transitions non-déterministes
    automate2.ajouter_transition(q0, 'a', q1)  # q0 --a--> q1
    automate2.ajouter_transition(q0, 'a', q2)  # q0 --a--> q2 (non-déterministe!)
    automate2.ajouter_transition(q1, 'b', q2)  # q1 --b--> q2
    
    print(automate2.afficher())
    print(f"Déterministe: {automate2.est_deterministe()}")
    print(f"Complet: {automate2.est_complet()}")
    
    # Test de reconnaissance
    mots_test2 = ["a", "ab", "b", "aa"]
    for mot in mots_test2:
        resultat = automate2.reconnaitre_mot(mot)
        print(f"Mot '{mot}': {'✓' if resultat else '✗'}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 3: Conversion en matrice
    print("3. Conversion automate → matrice")
    matrice, etats_list, alphabet_list = automate1.automate_a_matrice()
    
    print(f"États: {[str(e) for e in etats_list]}")
    print(f"Alphabet: {alphabet_list}")
    print("Matrice de transitions:")
    for i, etat in enumerate(etats_list):
        for j, symbole in enumerate(alphabet_list):
            destinations = matrice[i][j]
            if destinations:
                dest_noms = [str(etats_list[k]) for k in destinations]
                print(f"  {etat} --{symbole}--> {dest_noms}")
    
    print("\n" + "="*50 + "\n")
    
    # Exemple 4: Manipulation des transitions
    print("4. Suppression de transitions")
    print("Avant suppression:")
    print(automate1.afficher())
    
    # Supprimer une transition
    automate1.supprimer_transition(q1, 'b', q0)
    print("\nAprès suppression de q1 --b--> q0:")
    print(automate1.afficher())
    print(f"Complet après suppression: {automate1.est_complet()}")
    print("\n" + "="*50 + "\n")

    # === 1. Création d’un AD (automate déterministe) ===
    q0 = Etat("q0", est_initial=True)
    q1 = Etat("q1")
    q2 = Etat("q2", est_final=True)

    # Création de l'automate déterministe
    ad = AD(
        alphabet={'a', 'b'},
        etats_finaux={q2},
        etats={q0, q1, q2},
        etat_initial=q0
        
    )

    # Ajout des transitions (non complet à ce stade)
    ad.ajouter_transition(q0, 'a', q1)
    ad.ajouter_transition(q1, 'b', q2)
    
    print("\n=== Automate Deterministe non complet ===")
    print(ad.afficher())
    
    ad_min= ad.minimiser()
    print("\n=== Automate Minimal obtenu de l'AD precedent(juste pour verifier la minimisation) ===")
    print(ad_min.afficher())

    # === 2. Complétion de l’automate ===
    print("\n=== ADC obtenu apres la completion de l'AD precedent ===")
    adc=ad.completer()
    print(adc.afficher())
    
    # === 4. Canonisation ===

    # Étape 1 : Générer un langage fini depuis l'automate minimal
    adc_min=adc.minimiser()
    print(adc_min.afficher())
    langage_fini = Langage.depuis_automate(adc_min, longueur_max=3)

    # Étape 2 : Construire l'automate canonique à partir de ce langage
    automate_canonique = AutomateCanonique(langage_fini)

    # Étape 3 : Afficher l'automate canonique
    print("\n=== Automate Canonique resultant de l'Ad apres completion et minimisation===")
    print(automate_canonique.affiche())

    
    