import re
import numpy as np
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class ValidateurSystemeEquations:
    """
    Validateur pour systèmes d'équations simultanées résolvables par Gauss
    avant application du lemme d'Arden.
    """
    
    def __init__(self):
        self.etats = set()
        self.alphabet = set()
        self.matrice_coefficients = None
        self.vecteur_termes_libres = None
    
    def validate_equations(self, equations: List[str]) -> Tuple[bool, str]:
        """
        Valide un système d'équations simultanées pour la résolution par Gauss.
        
        Args:
            equations (List[str]): Liste d'équations sous forme ['A = bA + aB', ...]
            
        Returns:
            Tuple[bool, str]: (est_valide, message_détaillé)
        """
        try:
            # Étape 1: Parser les équations
            equations_parsees = self._parser_equations(equations)
            if not equations_parsees:
                return False, "Impossible de parser les équations"
            
            # Étape 2: Extraire états et alphabet
            self._extraire_etats_alphabet(equations_parsees)
            
            # Étape 3: Vérifier la cohérence du système
            coherence_ok, msg_coherence = self._verifier_coherence_systeme(equations_parsees)
            if not coherence_ok:
                return False, f"Cohérence: {msg_coherence}"
            
            # Étape 4: Construire la matrice du système
            matrice_ok, msg_matrice = self._construire_matrice_systeme(equations_parsees)
            if not matrice_ok:
                return False, f"Matrice: {msg_matrice}"
            
            # Étape 5: Vérifier que le système est résolvable par Gauss
            gauss_ok, msg_gauss = self._verifier_resolvabilite_gauss()
            if not gauss_ok:
                return False, f"Gauss: {msg_gauss}"
            
            # Étape 6: Vérifier compatibilité avec lemme d'Arden
            arden_ok, msg_arden = self._verifier_compatibilite_arden(equations_parsees)
            if not arden_ok:
                return False, f"Arden: {msg_arden}"
            
            return True, self._generer_rapport_validation()
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def _parser_equations(self, equations: List[str]) -> Dict[str, Dict]:
        """Parse les équations au format 'A = bA + aB'."""
        equations_parsees = {}
        
        for eq in equations:
            if '=' not in eq:
                continue
                
            gauche, droite = eq.split('=', 1)
            etat = gauche.strip()
            
            # Parser le côté droit
            termes = self._parser_cote_droit(droite.strip())
            equations_parsees[etat] = {
                'termes_recursifs': termes['recursifs'],
                'termes_non_recursifs': termes['non_recursifs']
            }
        
        return equations_parsees
    
    def _parser_cote_droit(self, expression: str) -> Dict:
        """Parse une expression comme 'bA + aB + c'."""
        termes_recursifs = defaultdict(list)  # {état: [symboles]}
        termes_non_recursifs = []  # [symboles terminaux]
        
        # Nettoyer et diviser par '+'
        expression = expression.replace(' ', '')
        termes = [t.strip() for t in expression.split('+') if t.strip()]
        
        for terme in termes:
            if not terme or terme == 'ε':
                termes_non_recursifs.append('ε')
                continue
            
            # Détecter si c'est un terme récursif (contient un état)
            match_recursif = re.match(r'^([a-z]*)([A-Z]+)$', terme)
            if match_recursif:
                symbole, etat = match_recursif.groups()
                if not symbole:  # Cas comme 'A' (sans symbole devant)
                    symbole = 'ε'
                termes_recursifs[etat].append(symbole)
            else:
                # Terme non récursif (symbole terminal)
                termes_non_recursifs.append(terme)
        
        return {
            'recursifs': dict(termes_recursifs),
            'non_recursifs': termes_non_recursifs
        }
    
    def _extraire_etats_alphabet(self, equations_parsees: Dict):
        """Extrait tous les états et symboles du système."""
        self.etats = set(equations_parsees.keys())
        self.alphabet = set()
        
        for etat_data in equations_parsees.values():
            # Symboles des termes récursifs
            for symboles in etat_data['termes_recursifs'].values():
                self.alphabet.update(s for s in symboles if s != 'ε')
            
            # Symboles des termes non récursifs
            for symbole in etat_data['termes_non_recursifs']:
                if symbole != 'ε':
                    self.alphabet.add(symbole)
        
        # Ajouter tous les états référencés
        for etat_data in equations_parsees.values():
            self.etats.update(etat_data['termes_recursifs'].keys())
    
    def _verifier_coherence_systeme(self, equations_parsees: Dict) -> Tuple[bool, str]:
        """Vérifie la cohérence du système d'équations."""
        # Vérifier que tous les états référencés ont une équation
        etats_definis = set(equations_parsees.keys())
        etats_references = set()
        
        for etat_data in equations_parsees.values():
            etats_references.update(etat_data['termes_recursifs'].keys())
        
        etats_manquants = etats_references - etats_definis
        if etats_manquants:
            return False, f"États référencés mais non définis: {etats_manquants}"
        
        # Vérifier qu'il n'y a pas d'équations vides
        for etat, data in equations_parsees.items():
            if not data['termes_recursifs'] and not data['termes_non_recursifs']:
                return False, f"Équation vide pour l'état {etat}"
        
        return True, "Système cohérent"
    
    def _construire_matrice_systeme(self, equations_parsees: Dict) -> Tuple[bool, str]:
        """Construit la matrice du système linéaire."""
        etats_liste = sorted(list(self.etats))
        n = len(etats_liste)
        
        if n == 0:
            return False, "Aucun état dans le système"
        
        # Matrice des coefficients (I - A) où A contient les coefficients récursifs
        matrice = np.eye(n)  # Commencer par la matrice identité
        vecteur_b = [''] * n  # Termes non récursifs
        
        for i, etat in enumerate(etats_liste):
            if etat not in equations_parsees:
                continue
            
            data = equations_parsees[etat]
            
            # Termes récursifs: soustraire de la diagonale et ajouter aux autres positions
            for etat_ref, symboles in data['termes_recursifs'].items():
                if etat_ref in etats_liste:
                    j = etats_liste.index(etat_ref)
                    if i == j:  # Terme récursif direct
                        # Pour A = αA + ..., le coefficient devient (1 - α)
                        # Ici on compte le nombre d'occurrences
                        matrice[i, j] = 1 - len(symboles)
                    else:  # Terme récursif vers autre état
                        # Pour A = αB + ..., le coefficient devient -α
                        matrice[i, j] = -len(symboles)
            
            # Termes non récursifs
            vecteur_b[i] = ' + '.join(data['termes_non_recursifs']) if data['termes_non_recursifs'] else 'ε'
        
        self.matrice_coefficients = matrice
        self.vecteur_termes_libres = vecteur_b
        self.etats_liste = etats_liste
        
        return True, "Matrice construite avec succès"
    
    def _verifier_resolvabilite_gauss(self) -> Tuple[bool, str]:
        """Vérifie que le système est résolvable par élimination de Gauss."""
        try:
            # Calculer le déterminant
            det = np.linalg.det(self.matrice_coefficients)
            
            if abs(det) < 1e-10:  # Déterminant proche de zéro
                return False, f"Système singulier (det ≈ 0: {det:.2e}). Non résolvable par Gauss."
            
            # Calculer le rang de la matrice
            rang = np.linalg.matrix_rank(self.matrice_coefficients)
            n = self.matrice_coefficients.shape[0]
            
            if rang < n:
                return False, f"Matrice de rang {rang} < {n}. Système sous-déterminé."
            
            # Vérifier la condition number (stabilité numérique)
            cond = np.linalg.cond(self.matrice_coefficients)
            if cond > 1e12:
                return False, f"Matrice mal conditionnée (cond = {cond:.2e}). Résolution instable."
            
            return True, f"Système résolvable (det = {det:.3f}, rang = {rang}, cond = {cond:.2e})"
            
        except np.linalg.LinAlgError as e:
            return False, f"Erreur d'algèbre linéaire: {str(e)}"
    
    def _verifier_compatibilite_arden(self, equations_parsees: Dict) -> Tuple[bool, str]:
        """Vérifie la compatibilité avec le lemme d'Arden."""
        problemes = []
        
        for etat, data in equations_parsees.items():
            # Vérifier récursion directe pour Arden
            if etat in data['termes_recursifs']:
                symboles_recursifs = data['termes_recursifs'][etat]
                
                # Le lemme d'Arden nécessite qu'aucun symbole récursif direct ne soit ε
                if 'ε' in symboles_recursifs or '' in symboles_recursifs:
                    problemes.append(f"État {etat}: récursion directe avec ε interdite pour Arden")
                
                # Vérifier multiplicité des symboles récursifs
                if len(symboles_recursifs) > 1:
                    symboles_uniques = set(symboles_recursifs)
                    if len(symboles_uniques) != len(symboles_recursifs):
                        problemes.append(f"État {etat}: symboles récursifs dupliqués {symboles_recursifs}")
        
        if problemes:
            return False, "; ".join(problemes)
        
        return True, "Compatible avec le lemme d'Arden"
    
    def _generer_rapport_validation(self) -> str:
        """Génère un rapport détaillé de la validation."""
        rapport = [
            f"✓ Système valide pour résolution par Gauss + lemme d'Arden",
            f"  - États: {sorted(list(self.etats))}",
            f"  - Alphabet: {sorted(list(self.alphabet))}",
            f"  - Taille matrice: {self.matrice_coefficients.shape[0]}×{self.matrice_coefficients.shape[1]}",
            f"  - Déterminant: {np.linalg.det(self.matrice_coefficients):.6f}",
            f"  - Condition number: {np.linalg.cond(self.matrice_coefficients):.2e}"
        ]
        return "\n".join(rapport)
    
    def obtenir_matrice_systeme(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """Retourne la matrice du système, le vecteur b et la liste des états."""
        return self.matrice_coefficients, self.vecteur_termes_libres, self.etats_liste


# Fonction utilitaire pour utilisation simple
def valider_systeme_equations(equations: List[str]) -> Tuple[bool, str]:
    """
    Fonction utilitaire pour valider rapidement un système d'équations.
    
    Args:
        equations: Liste d'équations comme ['A = bA + aB', 'B = aA + bD', ...]
    
    Returns:
        Tuple[bool, str]: (est_valide, message)
    """
    validateur = ValidateurSystemeEquations()
    return validateur.validate_equations(equations)


# Exemple d'utilisation et test
if __name__ == "__main__":
    # Test avec votre exemple
    equations_test = [
        'A = bA + aB',
        'B = aA + bD', 
        'C = aA + bD',
        'D = bA + aD'
    ]
    
    validateur = ValidateurSystemeEquations()
    est_valide, message = validateur.validate_equations(equations_test)
    
    print(f"Système valide: {est_valide}")
    print(f"Message: {message}")
    
    if est_valide:
        matrice, vecteur_b, etats = validateur.obtenir_matrice_systeme()
        print(f"\nMatrice du système:")
        print(matrice)
        print(f"\nVecteur b: {vecteur_b}")
        print(f"États: {etats}")

