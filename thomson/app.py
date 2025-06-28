from flask import Flask, render_template, request, jsonify
from collections import defaultdict

app = Flask(__name__)

class Etat:
    compteur = 0
    
    def __init__(self, nom=None):
        if nom is None:
            Etat.compteur += 1
            self.nom = f"q{Etat.compteur}"
        else:
            self.nom = nom
    
    def __str__(self):
        return self.nom
    
    def __repr__(self):
        return f"Etat({self.nom})"
    
    def __eq__(self, other):
        return isinstance(other, Etat) and self.nom == other.nom
    
    def __hash__(self):
        return hash(self.nom)
    
    def to_dict(self):
        return {"nom": self.nom}

class AFN:
    def __init__(self):
        self.etats = set()
        self.alphabet = set()
        self.transitions = defaultdict(lambda: defaultdict(set))
        self.etat_initial = None
        self.etats_finaux = set()
    
    def ajouter_etat(self, etat):
        self.etats.add(etat)
    
    def definir_etat_initial(self, etat):
        self.etat_initial = etat
        self.etats.add(etat)
    
    def ajouter_etat_final(self, etat):
        self.etats_finaux.add(etat)
        self.etats.add(etat)
    
    def ajouter_transition(self, etat_source, symbole, etat_destination):
        self.transitions[etat_source][symbole].add(etat_destination)
        self.etats.add(etat_source)
        self.etats.add(etat_destination)
        if symbole != 'ε':
            self.alphabet.add(symbole)
    
    def fusionner(self, autre_afn):
        self.etats.update(autre_afn.etats)
        self.alphabet.update(autre_afn.alphabet)
        for etat_source, transitions in autre_afn.transitions.items():
            for symbole, destinations in transitions.items():
                self.transitions[etat_source][symbole].update(destinations)
    
    def to_dict(self):
        transitions_list = []
        for etat_source in self.etats:
            if etat_source in self.transitions:
                for symbole in self.transitions[etat_source]:
                    for destination in self.transitions[etat_source][symbole]:
                        transitions_list.append({
                            'source': etat_source.nom,
                            'symbole': symbole,
                            'destination': destination.nom
                        })
        
        return {
            'etats': [etat.nom for etat in sorted(self.etats, key=lambda x: x.nom)],
            'alphabet': sorted(list(self.alphabet)),
            'etat_initial': self.etat_initial.nom if self.etat_initial else None,
            'etats_finaux': [etat.nom for etat in sorted(self.etats_finaux, key=lambda x: x.nom)],
            'transitions': transitions_list,
            'stats': {
                'nb_etats': len(self.etats),
                'nb_alphabet': len(self.alphabet),
                'nb_transitions': len(transitions_list)
            }
        }

class ConstructeurAFN:
    def __init__(self):
        self.reset_compteur()
    
    def reset_compteur(self):
        Etat.compteur = 0
    
    def construire_symbole(self, symbole):
        afn = AFN()
        q0 = Etat()
        q1 = Etat()
        
        afn.definir_etat_initial(q0)
        afn.ajouter_etat_final(q1)
        afn.ajouter_transition(q0, symbole, q1)
        
        return afn
    
    def construire_epsilon(self):
        afn = AFN()
        q0 = Etat()
        
        afn.definir_etat_initial(q0)
        afn.ajouter_etat_final(q0)
        
        return afn
    
    def construire_vide(self):
        afn = AFN()
        q0 = Etat()
        
        afn.definir_etat_initial(q0)
        
        return afn
    
    def construire_union(self, afn1, afn2):
        afn = AFN()
        
        afn.fusionner(afn1)
        afn.fusionner(afn2)
        
        q_new_start = Etat()
        q_new_final = Etat()
        
        afn.definir_etat_initial(q_new_start)
        afn.ajouter_etat_final(q_new_final)
        
        afn.ajouter_transition(q_new_start, 'ε', afn1.etat_initial)
        afn.ajouter_transition(q_new_start, 'ε', afn2.etat_initial)
        
        for etat_final in afn1.etats_finaux:
            afn.ajouter_transition(etat_final, 'ε', q_new_final)
        for etat_final in afn2.etats_finaux:
            afn.ajouter_transition(etat_final, 'ε', q_new_final)
        
        return afn
    
    def construire_concatenation(self, afn1, afn2):
        afn = AFN()
        
        afn.fusionner(afn1)
        afn.fusionner(afn2)
        
        afn.definir_etat_initial(afn1.etat_initial)
        
        for etat_final in afn2.etats_finaux:
            afn.ajouter_etat_final(etat_final)
        
        for etat_final in afn1.etats_finaux:
            afn.ajouter_transition(etat_final, 'ε', afn2.etat_initial)
        
        return afn
    
    def construire_etoile(self, afn_base):
        afn = AFN()
        
        afn.fusionner(afn_base)
        
        q_new_start = Etat()
        q_new_final = Etat()
        
        afn.definir_etat_initial(q_new_start)
        afn.ajouter_etat_final(q_new_final)
        
        afn.ajouter_transition(q_new_start, 'ε', afn_base.etat_initial)
        afn.ajouter_transition(q_new_start, 'ε', q_new_final)
        
        for etat_final in afn_base.etats_finaux:
            afn.ajouter_transition(etat_final, 'ε', afn_base.etat_initial)
            afn.ajouter_transition(etat_final, 'ε', q_new_final)
        
        return afn

class ParseurExpression:
    def __init__(self, expression):
        self.expression = expression.replace(' ', '')
        self.position = 0
        self.constructeur = ConstructeurAFN()
    
    def analyser(self):
        self.constructeur.reset_compteur()
        return self.analyser_union()
    
    def analyser_union(self):
        gauche = self.analyser_concatenation()
        
        while self.position < len(self.expression) and self.expression[self.position] == '+':
            self.position += 1
            droite = self.analyser_concatenation()
            gauche = self.constructeur.construire_union(gauche, droite)
        
        return gauche
    
    def analyser_concatenation(self):
        gauche = self.analyser_etoile()
        
        while (self.position < len(self.expression) and 
               self.expression[self.position] not in '+)'):
            droite = self.analyser_etoile()
            gauche = self.constructeur.construire_concatenation(gauche, droite)
        
        return gauche
    
    def analyser_etoile(self):
        base = self.analyser_facteur()
        
        while self.position < len(self.expression) and self.expression[self.position] == '*':
            self.position += 1
            base = self.constructeur.construire_etoile(base)
        
        return base
    
    def analyser_facteur(self):
        if self.position >= len(self.expression):
            return self.constructeur.construire_epsilon()
        
        char = self.expression[self.position]
        
        if char == '(':
            self.position += 1
            resultat = self.analyser_union()
            if self.position < len(self.expression) and self.expression[self.position] == ')':
                self.position += 1
            return resultat
        elif char == 'ε':
            self.position += 1
            return self.constructeur.construire_epsilon()
        elif char == '∅':
            self.position += 1
            return self.constructeur.construire_vide()
        else:
            self.position += 1
            return self.constructeur.construire_symbole(char)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/construire', methods=['POST'])
def construire():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        if not expression:
            return jsonify({'success': False, 'error': 'Expression vide'})
        
        parseur = ParseurExpression(expression)
        afn = parseur.analyser()
        afn_dict = afn.to_dict()
        
        return jsonify({'success': True, 'afn': afn_dict})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
