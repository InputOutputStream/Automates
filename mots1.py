from typing import Optional, Set, List
import itertools


SYMBOLE_MOT_VIDE = '&'
SYMBOLS_WHITESPACE = {' ', '\t', '\n', '\r', '\v', '\f'}

class Mot1:
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
       # Nettoyage du contenu (suppression des symboles blancs)
        contenu_nettoye = ''.join(c for c in contenu if c not in SYMBOLS_WHITESPACE)
        
        # Si on a supprimé des choses, informer l'utilisateur
        if contenu_nettoye != contenu:
            print(f"Votre mot contenait des symboles blancs qui ont été supprimés.")
            print(f"Ancien contenu : '{contenu}'")
            print(f"Nouveau contenu : '{contenu_nettoye}'")
            
            # Demander confirmation
            confirmation = input("Validez-vous ce nouveau mot ? (o/n) : ").strip().lower()
            if confirmation != 'o':
                raise ValueError("Mot non validé par l'utilisateur. Veuillez saisir un autre mot.")
        
        # Construction de l'alphabet à utiliser
        if alphabet is not None:
            alphabet_utilise = set(alphabet)
            alphabet_utilise.add(SYMBOLE_MOT_VIDE)
            
            # Vérification de conformité du contenu (hors SYMBOLE_MOT_VIDE)
            contenu_sans_vide = contenu_nettoye.replace(SYMBOLE_MOT_VIDE, "")
            if not set(contenu_sans_vide).issubset(alphabet_utilise):
                raise ValueError("Le contenu contient des symboles hors de l'alphabet.")
            
            self.alphabet = alphabet_utilise
        else:
            # Si pas d'alphabet fourni, on le déduit du contenu nettoyé
            self.alphabet = set(contenu_nettoye.replace(SYMBOLE_MOT_VIDE, ""))
            self.alphabet.add(SYMBOLE_MOT_VIDE)
        
        # Stocker le contenu nettoyé
        self.contenu = contenu_nettoye

    def __repr__(self) -> str:
        return f"mot : '{self.contenu}' "

    def longueur(self) -> int:
        """Retourne la longueur du mot en ignorant les espaces, tabulations, retours à la ligne et le symbole SYMBOLE_MOT_VIDE."""
        return len(self.contenu)

    def adjonction_occurrence_droite(self, symbole: str) -> 'Mot1':
        """Ajoute une occurrence d'un symbole à droite. Le symbole SYMBOLE_MOT_VIDE représente le mot vide."""
        if len(symbole) != 1:
            raise ValueError("Vous devez entrer un seul caractère pour l'adjonction.")
        if symbole == SYMBOLE_MOT_VIDE:
            return Mot1(self.contenu, self.alphabet)
        if self.alphabet and symbole not in self.alphabet:
            raise ValueError(f"Symbole {symbole} non présent dans l'alphabet.")
        return Mot1(self.contenu, self.alphabet)


    def adjonction_occurrence_gauche(self, symbole: str) -> 'Mot1':
        """Ajoute une occurrence d'un symbole à gauche. Le symbole SYMBOLE_MOT_VIDE représente le mot vide."""
        if len(symbole) != 1:
            raise ValueError("Vous devez entrer un seul caractère pour l'adjonction.")
        if symbole == SYMBOLE_MOT_VIDE:
            return Mot1(self.contenu, self.alphabet)
        if self.alphabet and symbole not in self.alphabet:
            raise ValueError(f"Symbole {symbole} non présent dans l'alphabet.")
        return Mot1(self.contenu, self.alphabet)

  
    def concatenation(self, autre_mot: 'Mot1', separateur: str = "") -> 'Mot1':
        """Concatène avec un autre mot."""
        if self.alphabet != autre_mot.alphabet:
            raise ValueError("Alphabets incompatibles pour la concaténation.")
        
        nouveau_contenu = self.contenu + separateur + autre_mot.contenu
        return Mot1(nouveau_contenu, self.alphabet)



    def liste_sous_mots(self, distinct: bool = False, min_length: int = 1) -> List['Mot1']:
    """
    Retourne la liste de tous les sous-mots (non nécessairement contigus, respectant l'ordre).

    Args:
        distinct: si True, retourne uniquement les sous-mots distincts
        min_length: longueur minimale des sous-mots à retourner
    """
    sous_mots = []
    contenu_nettoye = self.contenu.replace(SYMBOLE_MOT_VIDE, '')
    n = len(contenu_nettoye)
    
    # On génère toutes les longueurs possibles
    for length in range(min_length, n + 1):
        # Pour chaque combinaison d'indices, on construit le sous-mot
        for indices in itertools.combinations(range(n), length):
            sous_contenu = ''.join(contenu_nettoye[i] for i in indices)
            sous_mots.append(Mot1(sous_contenu, self.alphabet))
    
    if distinct:
        vus = set()
        sous_mots_uniques = []
        for mot in sous_mots:
            if mot.contenu not in vus:
                vus.add(mot.contenu)
                sous_mots_uniques.append(mot)
        return sous_mots_uniques
    else:
        return sous_mots


    def liste_facteurs(self, distinct: bool = False, min_length: int = 1) -> List['Mot1']:
        """
        Retourne la liste de tous les facteurs.

        Args:
            distinct: si True, retourne uniquement les facteurs distincts
            min_length: longueur minimale des facteurs à retourner
        """
        facteurs = []
        # Nettoyer le contenu en enlevant le symbole mot vide
        contenu_nettoye = self.contenu.replace(SYMBOLE_MOT_VIDE, '')
        n = len(contenu_nettoye)
        for i in range(n):
            for j in range(i + 1, n + 1):
                sous_contenu = contenu_nettoye[i:j]
                if len(sous_contenu) >= min_length:
                    facteurs.append(Mot1(sous_contenu, self.alphabet))
        
        if distinct:
            vus = set()
            facteurs_uniques = []
            for mot in facteurs:
                if mot.contenu not in vus:
                    vus.add(mot.contenu)
                    facteurs_uniques.append(mot)
            return facteurs_uniques
        else:
            return facteurs

