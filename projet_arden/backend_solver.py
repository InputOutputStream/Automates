import re

class AlphabetError(Exception):
    """Exception levée quand un symbole non autorisé est détecté."""
    pass

def decomposer_expression(expr, alphabet, variables):
    """
    Découpe l'expression en symboles reconnus : variables, alphabet, opérateurs.
    """
    # Utiliser un pattern qui capture variables, alphabet, opérateurs, parenthèses
    # On autorise +, *, (, ) comme opérateurs
    tokens = re.findall(r'[A-Za-z0-9e]+|[+*()]', expr)
    sequence = []
    for token in tokens:
        i = 0
        while i < len(token):
            match = False
            # Vérifier si le début du token correspond à une variable
            for var in sorted(variables, key=lambda x: -len(x)):
                if token[i:].startswith(var):
                    sequence.append(var)
                    i += len(var)
                    match = True
                    break
            if match:
                continue
            # Vérifier si le début du token correspond à un symbole de l'alphabet
            for sym in sorted(alphabet, key=lambda x: -len(x)):
                if token[i:].startswith(sym):
                    sequence.append(sym)
                    i += len(sym)
                    match = True
                    break
            if not match:
                # Le caractère isolé est ajouté (ex: opérateur ou parenthèse)
                sequence.append(token[i])
                i += 1
    return sequence

def verifier_alphabet(expr, alphabet, variables):
    """
    Vérifie que tous les symboles dans expr sont dans alphabet, variables, ou opérateurs reconnus.
    Retourne (True, None) si ok, sinon (False, symbole_invalide).
    """
    autorises = set(alphabet) | set(variables) | set(['+', '*', '(', ')'])
    symboles = decomposer_expression(expr, alphabet, variables)
    for s in symboles:
        if s not in autorises:
            return False, s
    return True, None

def substituer(expr, solutions):
    sorted_solutions_items = sorted(solutions.items(), key=lambda item: -len(item[0]))
    for var, val in sorted_solutions_items:
        val_to_substitute = f"({val})" if '+' in val or '*' in val else val
        expr = re.sub(rf'(?<![A-Z]){re.escape(var)}(?![A-Z])', val_to_substitute, expr)
    return expr

def trouver_equations_resolvables(systeme, alphabet, variables, solutions):
    resolvables = []
    non_resolvables = []
    for var, expr in systeme:
        expr_sub = substituer(expr, solutions).replace('++', '+').strip('+')

        # Vérifier alphabet avant d'aller plus loin
        ok, symbole_invalide = verifier_alphabet(expr_sub, alphabet, variables)
        if not ok:
            raise AlphabetError(f"Symbole inconnu dans l'expression : '{symbole_invalide}'")

        symboles = decomposer_expression(expr_sub, alphabet, variables)
        vars_dans_expr = [s for s in symboles if s in variables]

        if not vars_dans_expr:
            resolvables.append((var, expr_sub))
        elif len(set(vars_dans_expr)) == 1 and vars_dans_expr[0] == var:
            parts = expr_sub.split(var)
            if len(parts) == 2:
                prefix = parts[0].rstrip('+')
                suffix = parts[1].lstrip('+')

                if prefix == "":
                    new_expr = suffix
                else:
                    prefix_paren = f"({prefix})" if '+' in prefix or (prefix and len(prefix) > 1 and '*' in prefix) else prefix
                    suffix_paren = f"({suffix})" if '+' in suffix or (suffix and len(suffix) > 1 and '*' in suffix) else suffix
                    new_expr = f"{prefix_paren}*{suffix_paren}"
                resolvables.append((var, new_expr))
            else:
                non_resolvables.append((var, expr_sub))
        else:
            non_resolvables.append((var, expr_sub))
    return resolvables, non_resolvables

def appliquer_lemmes_arden(systeme, alphabet, variables):
    solutions = {}
    systeme_courant = systeme.copy()
    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        # print(f"\n Itération {iteration}...")

        try:
            resolvables, non_resolvables = trouver_equations_resolvables(systeme_courant, alphabet, variables, solutions)
        except AlphabetError as e:
            # On renvoie l'erreur pour qu'elle soit gérée en frontend
            return None, None, str(e)

        if not resolvables and not non_resolvables:
            # print("\n Toutes les équations ont été résolues.")
            break
        
        if not resolvables:
            # print(" Plus aucune équation résoluble trouvée dans le système restant. Stagnation.")
            break

        for var, expr in resolvables:
            solutions[var] = expr
        
        systeme_pour_prochaine_iteration = []
        for var_non_res, expr_non_res_original in non_resolvables:
            expr_sub_updated = substituer(expr_non_res_original, solutions).replace('++', '+').strip('+')
            systeme_pour_prochaine_iteration.append((var_non_res, expr_sub_updated))
        
        systeme_courant = systeme_pour_prochaine_iteration

        if not systeme_courant:
            # print("\n Toutes les équations ont été résolues.")
            break

    return solutions, systeme_courant, None

# Exemple d'utilisation pour debug
if __name__ == "__main__":
    alphabet = {'a', 'b', 'e'}  # e = epsilon
    variables = {'X', 'Y'}
    systeme = [('X', 'aX + bY + e'), ('Y', 'aY + e')]
    solutions, reste, erreur = appliquer_lemmes_arden(systeme, alphabet, variables)
    if erreur:
        print("Erreur détectée :", erreur)
    else:
        print("Solutions :", solutions)
        print("Reste :", reste)
