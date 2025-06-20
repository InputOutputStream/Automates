try:
    from dominate import document
    from dominate.tags import *
    DOMINATE_AVAILABLE = True
except ImportError:
    DOMINATE_AVAILABLE = False
    print("Warning: dominate library not available. HTML generation will be limited.")


class ZoneSaisieHTML:
    """
    Générateur de la zone de saisie en HTML
    """
    
    def __init__(self):
        """Initialise le générateur de zone de saisie"""
        self.use_dominate = DOMINATE_AVAILABLE
    
    def generer_formulaire_regex(self):
        """Génère le formulaire de saisie regex"""
        if self.use_dominate:
            return div(
                div(
                    label("Expression régulière:", for_="regex-input", cls="form-label"),
                    input_(type="text", id="regex-input", cls="form-control", 
                          placeholder="Exemple: (a|b)*abb"),
                    small("Opérateurs supportés: | (union), * (étoile), + (plus), ? (optionnel), () (groupement)",
                          cls="form-text text-muted"),
                    cls="mb-3"
                ),
                button("Parser Regex", id="parse-regex-btn", cls="btn btn-primary me-2"),
                button("Effacer", id="clear-regex-btn", cls="btn btn-secondary"),
                cls="card-body"
            )
        else:
            return '''
            <div class="card-body">
                <div class="mb-3">
                    <label for="regex-input" class="form-label">Expression régulière:</label>
                    <input type="text" id="regex-input" class="form-control" 
                           placeholder="Exemple: (a|b)*abb">
                    <small class="form-text text-muted">
                        Opérateurs supportés: | (union), * (étoile), + (plus), ? (optionnel), () (groupement)
                    </small>
                </div>
                <button id="parse-regex-btn" class="btn btn-primary me-2">Parser Regex</button>
                <button id="clear-regex-btn" class="btn btn-secondary">Effacer</button>
            </div>
            '''
    
    def generer_formulaire_automate_manuel(self):
        """Génère les champs pour saisie manuelle d'automate"""
        if self.use_dominate:
            return div(
                div(
                    label("Alphabet (séparés par des virgules):", for_="alphabet-input", cls="form-label"),
                    input_(type="text", id="alphabet-input", cls="form-control", 
                          placeholder="a,b"),
                    cls="mb-3"
                ),
                div(
                    label("États (séparés par des virgules):", for_="states-input", cls="form-label"),
                    input_(type="text", id="states-input", cls="form-control", 
                          placeholder="q0,q1,q2"),
                    cls="mb-3"
                ),
                div(
                    label("État initial:", for_="initial-state-input", cls="form-label"),
                    input_(type="text", id="initial-state-input", cls="form-control", 
                          placeholder="q0"),
                    cls="mb-3"
                ),
                div(
                    label("États finaux (séparés par des virgules):", for_="final-states-input", cls="form-label"),
                    input_(type="text", id="final-states-input", cls="form-control", 
                          placeholder="q1,q2"),
                    cls="mb-3"
                ),
                div(
                    label("Transitions (format: source,symbole,destination par ligne):", 
                          for_="transitions-input", cls="form-label"),
                    textarea(id="transitions-input", cls="form-control", rows="5",
                            placeholder="q0,a,q1\nq1,b,q2"),
                    cls="mb-3"
                ),
                button("Créer Automate", id="create-automaton-btn", cls="btn btn-success"),
                cls="card-body"
            )
        else:
            return '''
            <div class="card-body">
                <div class="mb-3">
                    <label for="alphabet-input" class="form-label">Alphabet (séparés par des virgules):</label>
                    <input type="text" id="alphabet-input" class="form-control" placeholder="a,b">
                </div>
                <div class="mb-3">
                    <label for="states-input" class="form-label">États (séparés par des virgules):</label>
                    <input type="text" id="states-input" class="form-control" placeholder="q0,q1,q2">
                </div>
                <div class="mb-3">
                    <label for="initial-state-input" class="form-label">État initial:</label>
                    <input type="text" id="initial-state-input" class="form-control" placeholder="q0">
                </div>
                <div class="mb-3">
                    <label for="final-states-input" class="form-label">États finaux (séparés par des virgules):</label>
                    <input type="text" id="final-states-input" class="form-control" placeholder="q1,q2">
                </div>
                <div class="mb-3">
                    <label for="transitions-input" class="form-label">Transitions (format: source,symbole,destination par ligne):</label>
                    <textarea id="transitions-input" class="form-control" rows="5" 
                              placeholder="q0,a,q1\nq1,b,q2"></textarea>
                </div>
                <button id="create-automaton-btn" class="btn btn-success">Créer Automate</button>
            </div>
            '''
    
    def generer_zone_mots_test(self):
        """Génère la zone de saisie des mots de test"""
        if self.use_dominate:
            return div(
                div(
                    label("Mots à tester (un par ligne):", for_="test-words-input", cls="form-label"),
                    textarea(id="test-words-input", cls="form-control", rows="4",
                            placeholder="abb\naabb\nba"),
                    cls="mb-3"
                ),
                button("Tester Mots", id="test-words-btn", cls="btn btn-info"),
                cls="card-body"
            )
        else:
            return '''
            <div class="card-body">
                <div class="mb-3">
                    <label for="test-words-input" class="form-label">Mots à tester (un par ligne):</label>
                    <textarea id="test-words-input" class="form-control" rows="4" 
                              placeholder="abb\naabb\nba"></textarea>
                </div>
                <button id="test-words-btn" class="btn btn-info">Tester Mots</button>
            </div>
            '''
    
    def generer_boutons_action(self):
        """Génère les boutons d'action"""
        boutons = [
            ("Déterminiser", "determinize-btn", "btn-warning"),
            ("Minimiser", "minimize-btn", "btn-info"),
            ("Compléter", "complete-btn", "btn-secondary"),
            ("Complémentaire", "complement-btn", "btn-dark")
        ]
        
        if self.use_dominate:
            container = div(cls="d-grid gap-2")
            for texte, id_btn, classe in boutons:
                container.add(button(texte, id=id_btn, cls=f"btn {classe}"))
            return div(container, cls="card-body")
        else:
            html = '<div class="card-body"><div class="d-grid gap-2">'
            for texte, id_btn, classe in boutons:
                html += f'<button id="{id_btn}" class="btn {classe}">{texte}</button>'
            html += '</div></div>'
            return html
    
    def generer_selecteur_exemples(self):
        """Génère le sélecteur d'exemples prédéfinis"""
        exemples = [
            ("Sélectionner un exemple...", ""),
            ("Mots finissant par 'ab'", "(a|b)*ab"),
            ("Nombre pair de 'a'", "b*(ab*ab*)*"),
            ("Au moins un 'a'", "(a|b)*a(a|b)*"),
            ("Alternance a-b", "(ab)*")
        ]
        
        if self.use_dominate:
            select_elem = select(id="examples-select", cls="form-select")
            for texte, valeur in exemples:
                select_elem.add(option(texte, value=valeur))
            return div(
                label("Exemples prédéfinis:", for_="examples-select", cls="form-label"),
                select_elem,
                cls="mb-3"
            )
        else:
            html = '''
            <div class="mb-3">
                <label for="examples-select" class="form-label">Exemples prédéfinis:</label>
                <select id="examples-select" class="form-select">
            '''
            for texte, valeur in exemples:
                html += f'<option value="{valeur}">{texte}</option>'
            html += '</select></div>'
            return html
    
    def generer_zone_import_export(self):
        """Génère les contrôles d'import/export"""
        if self.use_dominate:
            return div(
                div(
                    button("Exporter JSON", id="export-json-btn", cls="btn btn-outline-primary me-2"),
                    button("Exporter DOT", id="export-dot-btn", cls="btn btn-outline-secondary me-2"),
                    cls="mb-3"
                ),
                div(
                    input_(type="file", id="import-file", cls="form-control", accept=".json"),
                    button("Importer", id="import-btn", cls="btn btn-outline-success mt-2"),
                    cls="mb-3"
                ),
                cls="card-body"
            )
        else:
            return '''
            <div class="card-body">
                <div class="mb-3">
                    <button id="export-json-btn" class="btn btn-outline-primary me-2">Exporter JSON</button>
                    <button id="export-dot-btn" class="btn btn-outline-secondary me-2">Exporter DOT</button>
                </div>
                <div class="mb-3">
                    <input type="file" id="import-file" class="form-control" accept=".json">
                    <button id="import-btn" class="btn btn-outline-success mt-2">Importer</button>
                </div>
            </div>
            '''
    
    def generer_js_validation(self) -> str:
        """JavaScript pour validation côté client"""
        return '''
        function validerRegex(regex) {
            if (!regex.trim()) {
                return { valide: false, message: "Expression vide" };
            }
            
            // Validation basique des parenthèses
            let compteur = 0;
            for (let i = 0; i < regex.length; i++) {
                if (regex[i] === '(') compteur++;
                else if (regex[i] === ')') {
                    compteur--;
                    if (compteur < 0) {
                        return { valide: false, message: `Parenthèse fermante non appariée à la position ${i}` };
                    }
                }
            }
            
            if (compteur !== 0) {
                return { valide: false, message: "Parenthèses non équilibrées" };
            }
            
            return { valide: true, message: "Syntaxe valide" };
        }
        
        function validerAutomate(alphabet, etats, etatInitial, etatsFinaux) {
            if (!alphabet.trim()) return { valide: false, message: "Alphabet vide" };
            if (!etats.trim()) return { valide: false, message: "États vides" };
            if (!etatInitial.trim()) return { valide: false, message: "État initial vide" };
            if (!etatsFinaux.trim()) return { valide: false, message: "États finaux vides" };
            
            const listeEtats = etats.split(',').map(s => s.trim());
            if (!listeEtats.includes(etatInitial.trim())) {
                return { valide: false, message: "L'état initial doit être dans la liste des états" };
            }
            
            return { valide: true, message: "Données valides" };
        }
        '''
