class State:
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Automaton:
    def __init__(self, alphabet, states, initial, finals, transitions):
        self.alphabet = alphabet
        self.states = states
        self.initial = initial
        self.finals = finals
        self.transitions = transitions

def build_glushkov_automaton(regex: str) -> Automaton:
    # Étape 1: Validation syntaxique
    if not regex or not isinstance(regex, str):
        raise ValueError("Expression invalide")
    
    # Étape 2: Construire l'AST
    ast, positions = _parse_regex(regex)
    
    # Étape 3: Calculer les propriétés Glushkov
    props = _compute_glushkov_properties(ast, positions)
    
    # Étape 4: Construire l'automate
    return _build_automaton_from_properties(props)

def _parse_regex(regex: str) -> tuple:
    """Parse l'expression en AST avec positions"""
    # Implémentation simplifiée (remplacer par un vrai parser en pratique)
    # Retourne (AST, positions) avec positions = {pos: symbole}
    return {}, {}  # Placeholder

def _compute_glushkov_properties(ast, positions) -> dict:
    """Calcule nullable/first/last/follow"""
    # Retourne un dictionnaire avec:
    #   nullable: bool
    #   first: set[int]
    #   last: set[int]
    #   follow: dict[int, set[int]]
    #   positions: dict[int, str]
    return {}  # Placeholder

def _build_automaton_from_properties(props) -> Automaton:
    # Créer les états
    initial = State("q0")
    states = {initial}
    state_map = {}
    
    # Créer états pour chaque position
    for pos, symbol in props['positions'].items():
        if symbol != '#':  # Ignore symbole de fin
            state = State(f"q{pos}")
            states.add(state)
            state_map[pos] = state
    
    # Alphabet (exclut le marqueur de fin)
    alphabet = {s for s in props['positions'].values() if s != '#'}
    
    # Transitions (dict[State, dict[str, set[State]]])
    transitions = {}
    
    # Depuis l'état initial
    src = initial
    for pos in props['first']:
        symbol = props['positions'][pos]
        if symbol == '#': continue
            
        dest = state_map[pos]
        transitions.setdefault(src, {}).setdefault(symbol, set()).add(dest)
    
    # Transitions entre positions
    for src_pos, follow_set in props['follow'].items():
        src_symbol = props['positions'].get(src_pos)
        if not src_symbol or src_symbol == '#': 
            continue
            
        src_state = state_map[src_pos]
        for dest_pos in follow_set:
            dest_symbol = props['positions'].get(dest_pos)
            if not dest_symbol or dest_symbol == '#': 
                continue
                
            dest_state = state_map[dest_pos]
            transitions.setdefault(src_state, {}).setdefault(dest_symbol, set()).add(dest_state)
    
    # États finaux
    finals = set()
    if props['nullable']:
        finals.add(initial)
    finals.update(state_map[p] for p in props['last'] if p in state_map)
    
    return Automaton(
        alphabet=alphabet,
        states=states,
        initial=initial,
        finals=finals,
        transitions=transitions
    )