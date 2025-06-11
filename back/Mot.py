from typing import List, Set






from typing import List, Set

class Mot:
    """
    Classe représentant un mot sur un alphabet 
    Le mot vide est représenté par une chaîne vide ""
    """
    
    def __init__(self, contenu=None, alphabet: list = None) -> None:
        """
        Initialise un mot.
        
        Args:
            contenu: Chaîne de caractères représentant le mot ou une instance de Mot pour le constructeur de copie 
            alphabet: Alphabet du mot (sera converti en set pour l'efficacité)
        """
        if isinstance(contenu, Mot):
            # Constructeur de copie
            self.contenu = contenu.contenu
            self.alphabet = contenu.alphabet.copy()  
            self.alphabet_set = contenu.alphabet_set.copy()  
        else:
            # Constructeur normal
            self.contenu = contenu or ""  # Mot vide = chaîne vide, pas de maux de tetes
            
            if alphabet is not None:
                alphabet_copy = alphabet.copy()
                self.alphabet_set = set(alphabet_copy)
                self.alphabet = list(self.alphabet_set)
                self.__validate_entry(self.contenu, self.alphabet_set)
            else:
                self.alphabet_set = self.__calculer_alphabet_set__(self.contenu)
                self.alphabet = list(self.alphabet_set)
    
    def est_mot_vide(self) -> bool:
        """Vérifie si le mot est le mot vide (epsilon)."""
        return self.contenu == ""
    
    def longueur(self) -> int:
        """Retourne la longueur du mot."""
        return len(self.contenu)
        
    def adjonction_occurrence_droite(self, symbole: str) -> 'Mot':
        """Ajoute une occurrence d'un symbole à droite."""
        if symbole not in self.alphabet_set:
            raise ValueError(f"Le symbole '{symbole}' n'est pas dans l'alphabet")
        return Mot(self.contenu + symbole, self.alphabet)
    
    def adjonction_occurrence_gauche(self, symbole: str) -> 'Mot':
        """Ajoute une occurrence d'un symbole à gauche."""
        if symbole not in self.alphabet_set:
            raise ValueError(f"Le symbole '{symbole}' n'est pas dans l'alphabet")
        return Mot(symbole + self.contenu, self.alphabet)
    
    def concatenation(self, autre_mot: 'Mot') -> 'Mot':
        """Concatène avec un autre mot."""
        if self.alphabet_set != autre_mot.alphabet_set:
            raise ValueError("Les alphabets sont différents")
        return Mot(self.contenu + autre_mot.contenu, self.alphabet)    
    
    def liste_sous_mots(self) -> List['Mot']:
        """Retourne la liste de tous les sous-mots (facteurs)."""
        if self.est_mot_vide():
            return [Mot("", self.alphabet)]  
        
        sous_mots = []
        n = len(self.contenu)
        
        sous_mots.append(Mot("", self.alphabet))
        
        for i in range(n):
            for j in range(i+1, n+1):
                sous_mots.append(Mot(self.contenu[i:j], self.alphabet))
        
        return sous_mots
    
    def facteur_gauche(self, longueur: int) -> 'Mot':
        """Retourne le facteur gauche de longueur donnée."""
        if longueur < 0:
            raise ValueError("La longueur doit être positive ou nulle")
        
        if longueur == 0:
            return Mot("", self.alphabet)  # Mot vide
        
        if longueur > len(self.contenu):
            raise ValueError(f"Longueur demandée {longueur} > longueur du mot {len(self.contenu)}")
        
        return Mot(self.contenu[:longueur], self.alphabet)
    
    def facteur_droit(self, longueur: int) -> 'Mot':
        """Retourne le facteur droit de longueur donnée."""
        if longueur < 0:
            raise ValueError("La longueur doit être positive ou nulle")
        
        if longueur == 0:
            return Mot("", self.alphabet)  # Mot vide
        
        if longueur > len(self.contenu):
            raise ValueError(f"Longueur demandée {longueur} > longueur du mot {len(self.contenu)}")
        
        return Mot(self.contenu[-longueur:], self.alphabet)

    def caracteres_utilises(self) -> Set[str]:
        """Retourne l'ensemble des caractères réellement utilisés dans le mot."""
        return set(self.contenu)
    
    def est_dans_alphabet(self, symbole: str) -> bool:
        """Vérifier si un symbole appartient à l'alphabet - VERSION OPTIMISÉE"""
        # Recherche ultra-rapide avec le set !
        return symbole in self.alphabet_set
    
    
    def caracteres_non_utilises(self) -> Set[str]:
        """Retourne les caractères de l'alphabet non utilisés dans le mot."""
        return self.alphabet_set - set(self.contenu)
    
    def est_periodique(self, periode: int) -> bool:
        """Vérifie si le mot est périodique avec la période donnée."""
        if self.est_mot_vide():
            return True  # Le mot vide est périodique pour toute période
        
        if periode <= 0:
            return False
        
        if len(self.contenu) % periode != 0:
            return False
        
        pattern = self.contenu[:periode]
        for i in range(periode, len(self.contenu), periode):
            if self.contenu[i:i+periode] != pattern:
                return False
        return True
    
    def est_primitif(self) -> bool:
        """Vérifie si le mot est primitif."""
        if self.est_mot_vide():
            return True  # Convention : le mot vide est primitif
        
        return not any(self.est_periodique(i) for i in range(1, len(self.contenu)//2 + 1))
    
    def __str__(self) -> str:
        return self.contenu if self.contenu else "ε"  # Affichage epsilon pour mot vide
    
    def __repr__(self) -> str:
        if self.est_mot_vide():
            return "Mot(ε)"
        return f"'{self.contenu}'"
    
    def __len__(self) -> int:
        return len(self.contenu)
    
    def __eq__(self, autre: 'Mot') -> bool:
        """Égalité entre mots."""
        return (self.contenu == autre.contenu and 
                self.alphabet_set == autre.alphabet_set)
    
    def __add__(self, autre: 'Mot') -> 'Mot':
        """Surcharge de + pour la concaténation."""
        return self.concatenation(autre)
    
    def __getitem__(self, key) -> str:
        return self.contenu[key]

    def __calculer_alphabet_set__(self, contenu: str) -> Set[str]: 
        return set(contenu) if contenu else set()
    
    def __hash__(self):
        return hash((self.contenu, frozenset(self.alphabet_set)))
    
    def __iter__(self):
        """Permet l'itération sur les caractères du mot."""
        return iter(self.contenu)
        
    def __validate_entry(self, contenu: str, alphabet_set: Set[str]):
        """Validation avec set"""
        if not contenu:  # Mot vide toujours valide
            return
        
        contenu_set = set(contenu)
        caracteres_invalides = contenu_set - alphabet_set
        
        if caracteres_invalides:
            raise ValueError(f"Caractères non autorisés trouvés : {caracteres_invalides}")










if __name__ == "__main__":

    # ==========================================
    # DÉMONSTRATION D'UTILISATION
    # ==========================================

    print("\n=== DÉMONSTRATION ===")

    # Création d'un mot avec alphabet
    mot1 = Mot("abcabc", ['a', 'b', 'c'])
    print(f"Mot 1 : {mot1}")
    print(f"Alphabet (set) : {mot1.alphabet_set}")
    print(f"Caractères utilisés : {mot1.caracteres_utilises()}")
    print(f"Caractères non utilisés : {mot1.caracteres_non_utilises()}")

    # Test de vitesse - vérification d'appartenance
    print(f"'a' dans l'alphabet ? {mot1.est_dans_alphabet('a')}")
    print(f"'z' dans l'alphabet ? {mot1.est_dans_alphabet('z')}")

    # Création d'un autre mot
    mot2 = Mot("def", ['d', 'e', 'f'])
    print(f"Mot 2 : {mot2}")

    # Test de concaténation (doit échouer - alphabets différents)
    try:
        mot3 = mot1 + mot2
    except ValueError as e:
        print(f"Erreur attendue : {e}")
