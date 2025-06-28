from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import json
import traceback
from typing import Dict, Any
import logging
import webbrowser
import threading
import time

from .GestionnaireOperations import GestionnaireOperations
from ..Automate import Automate
from ..Etat import Etat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatonServer:
    """
    Enhanced Automaton Server combining Flask API with local server capabilities
    """
    
    def __init__(self, host='localhost', port=8080, debug=True, auto_open_browser=False):
        self.app = Flask(__name__, template_folder='templates')  # Add template folder
        CORS(self.app)
        self.host = host
        self.port = port
        self.debug = debug
        self.auto_open_browser = auto_open_browser
        self.gestionnaire = GestionnaireOperations()
        self.server_thread = None
        self._setup_routes_simplified()
        self._debug_routes()
        self._setup_error_handlers()

    def _convert_automaton_format(self, data: Dict[str, Any], to_legacy: bool = False) -> Dict[str, Any]:
        """Conversion bidirectionnelle entre formats legacy et nouveau"""
        if to_legacy:
            # Nouveau vers legacy
            return {
                'alphabet': data.get('alphabet', []),
                'etats': data.get('states', []),
                'etat_initial': data.get('initial_state', ''),
                'etats_finaux': data.get('final_states', []),
                'transitions': [
                    {
                        'source': t.get('source', ''),
                        'symbole': t.get('symbol', ''),
                        'destination': t.get('destination', '')
                    }
                    for t in data.get('transitions', [])
                ]
            }
        else:
            # Legacy vers nouveau
            return {
                'alphabet': data.get('alphabet', []),
                'states': data.get('etats', data.get('states', [])),
                'initial_state': data.get('etat_initial', data.get('initial_state', '')),
                'final_states': data.get('etats_finaux', data.get('final_states', [])),
                'transitions': [
                    {
                        'source': t.get('source', ''),
                        'symbol': t.get('symbole', t.get('symbol', '')),
                        'destination': t.get('destination', '')
                    }
                    for t in data.get('transitions', [])
                ]
            }
    
    def _setup_binary_routes(self):
        """Configure les routes pour les opérations binaires"""
        operations = ['union', 'intersection', 'concatenation']
        
        for op in operations:
            self.app.add_url_rule(
                f'/api/automaton/{op}',
                f'{op}_automata',
                lambda op=op: self._handle_binary_operation(op),
                methods=['POST']
            )

    
    # Single automaton operations
    def _states_operations(self):
        """States operations for automaton (utiles, accessibles, coaccessibles)"""
        try:
            data = request.get_json()
            if not data or 'automaton' not in data or 'operation' not in data:
                # Support legacy format
                if 'automate' in data:
                    data['automaton'] = data['automate']
                else:
                    return jsonify({'error': 'Missing automaton or operation parameter'}), 400
            
            # Handle legacy JSON string format
            automaton_data = data['automaton']
            if isinstance(automaton_data, str):
                automaton_data = json.loads(automaton_data)
            
            if not self._validate_automaton_structure(automaton_data):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            automate = self._dict_to_automate(automaton_data)
            operation = data['operation']
            
            logger.info(f"Performing operation: {operation}")
            
            if operation == 'coaccessibles':
                result_states = self.gestionnaire.liste_etats_coaccessibles(automate)
            elif operation == 'accessibles':
                result_states = self.gestionnaire.liste_etats_accessibles(automate)
            elif operation == 'utiles':
                result_states = self.gestionnaire.liste_etats_utiles(automate)
            else:
                return jsonify({'error': f'Unknown operation: {operation}'}), 400
            
            if  not isinstance(result_states, (str, dict)):
                serializable_states = [state.nom for state in result_states]
            else:
                serializable_states = result_states

            print(serializable_states)
 
            return jsonify({
                'success': True,
                'states': serializable_states,
                'operation': operation,
                'message': f'Operation "{operation}" completed successfully'
            })
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return jsonify({'error': 'Invalid JSON format in automaton data'}), 400
        except Exception as e:
            logger.error(f"Error in states operation: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Operation failed: {str(e)}'}), 500

    def handle_api_errors(func):
        """Décorateur pour gérer les erreurs API"""
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'{func.__name__} failed: {str(e)}'}), 500
        return wrapper
    
    def _debug_routes(self):
        """Debug: Print all registered routes"""
        for rule in self.app.url_map.iter_rules():
            print(f"Route: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

    def _setup_routes_simplified(self):
        """Version simplifiée de la configuration des routes"""
        # Existing routes...
        routes_config = [
            ('/', 'index', self._serve_index, ['GET']),
            ('/api/health', 'health', self._health_check, ['GET']),
            ('/api/regex/convert', 'convert_regex', self._convert_regex, ['POST']),
            ('/api/regex/validate', 'validate_regex', self._validate_regex, ['POST']),
            ('/api/automaton/test', 'test_word', self.test_word_simplified, ['POST']),
            ('/api/automaton/transform', 'transform', self._transform_automaton, ['POST']),
            ('/api/automaton/states', 'states', self._states_operations, ['POST']),
            # ADD THESE MISSING ROUTES:
            ('/api/automaton/kleene', 'kleene_star', self.kleene_star, ['POST']),
            ('/api/automaton/compare', 'compare_automata', self.compare_automata, ['POST']),
            ('/api/automaton/export', 'export_automaton', self.export_automaton, ['POST']),
            ('/api/automaton/trace', 'trace_word', self.trace_word, ['POST']),
            # In _setup_routes_simplified, change:
            ('/api/automaton/history', 'get_history', self.get_operations_history, ['GET']),
            ('/api/automaton/clear-history', 'clear_history', self.clear_operations_history, ['DELETE']),  # Changed to DELETE
            ('/api/endpoints', 'list_endpoints', self.list_endpoints, ['GET']),
            ('/api/automaton/eqn2regex', 'eqn2regex', self.eqn2regex, ['POST']),
            # Legacy support:
            ('/api/operations', 'legacy_operations', self.legacy_operations, ['POST']),
        ]
        
        for route, endpoint, handler, methods in routes_config:
            self.app.add_url_rule(route, endpoint, handler, methods=methods)
        
        self.app.add_url_rule('/api/automaton/a2regex', 'a2regex_manual', self.a2regex, methods=['POST'])
        
        self._setup_binary_routes()
      
        
    def _serve_index(self):
        """Serve the main interface"""
        return render_template('index.html')

    def _health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'automaton-server',
            'version': '2.0.0',
            'features': ['regex_conversion', 'automaton_operations', 'word_testing', 'equivalence_checking']
        })

     

    # Regex operations
    def _convert_regex(self):
        """Convert regex to automaton"""
        try:
            data = request.get_json()
            if not data or 'regex' not in data:
                return jsonify({'error': 'Missing regex parameter'}), 400
            
            regex = data['regex']
            method = data['method']
            if not regex.strip():
                return jsonify({'error': 'Empty regex provided'}), 400
            
            logger.info(f"Converting regex: {regex}")
            automate = self.gestionnaire.regex_vers_automate(regex, method)
            result = self._automate_to_dict(automate)
            
            return jsonify({
                'success': True,
                'automaton': result,
                'message': f'Regex "{regex}" converted successfully'
            })
        except Exception as e:
            logger.error(f"Error converting regex: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Regex conversion failed: {str(e)}'}), 500

    @handle_api_errors 
    def _validate_regex(self):
        """Validate regex syntax"""
        try:
            data = request.get_json()
            if not data or 'regex' not in data:
                return jsonify({'error': 'Missing regex parameter'}), 400
            
            regex = data['regex']
            if not regex.strip():
                return jsonify({
                    'valid': False,
                    'message': 'Empty regex provided'
                })
            
            is_valid, message = self.gestionnaire.valider_syntaxe(regex)
            return jsonify({
                'valid': is_valid,
                'message': message
            })
        except Exception as e:
            logger.error(f"Error validating regex: {str(e)}")
            return jsonify({'error': f'Regex validation failed: {str(e)}'}), 500
        
    @handle_api_errors 
    def a2regex(self):
        """From automaton to regex using Arden Lemma"""
        """
            Doit retouner la regex vers l'api mais actu ne le fais pas encore
            de plus le lemme d'arden ne marche pas donc
        """
        try:
            data = request.get_json()
            if not data or 'automaton' not in data:
                # Support legacy format
                if 'automate' in data:
                    data['automaton'] = data['automate']
                else:
                    return jsonify({'error': 'Missing automaton or operation parameter'}), 400
            
            # Handle legacy JSON string format
            automaton_dict = data['automaton']
            if isinstance(automaton_dict, str):
                automaton_dict = json.loads(automaton_dict)
            
            if not self._validate_automaton_structure(automaton_dict):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            

            logger.info(f"Solving Automaton")
            
            result = self.gestionnaire.automaton2reg(automaton_dict)

            return jsonify({
                'success': True,
                'regex': result,
                'message': f'Operation completed successfully'
            })
        except Exception as e:
            logger.error(f"Error transforming automaton: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Resolution failed: {str(e)}'}), 500

    @handle_api_errors
    def eqn2regex(self):
        """From equations to regex using Arden Lemma"""
        try:
            data = request.get_json()
            if not data or 'equations' not in data:
                return jsonify({'error': 'Missing equations parameter'}), 400
            
            equations = data['equations']
            
            # Validation des équations
            if not self.gestionnaire.validate_equations(equations):
                return jsonify({'error': 'Invalid equations format structure'}), 400
            
            # Résolution
            result = self.gestionnaire.eqn2reg(equations)
            logger.info(f"Equations resolved to: {result}")
        
            return jsonify({
                'success': True,
                'regex': result,
                'message': 'Equations solved successfully'
            })
        
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return jsonify({'error': f'Validation failed: {str(ve)}'}), 400
        except Exception as e:
            logger.error(f"Error solving equation system: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Resolution failed: {str(e)}'}), 500



    # Single automaton operations
    @handle_api_errors 
    def _transform_automaton(self):
        """Transform automaton (determinize, minimize, complete, complement)"""
        try:
            data = request.get_json()
            if not data or 'automaton' not in data or 'operation' not in data:
                # Support legacy format
                if 'automate' in data:
                    data['automaton'] = data['automate']
                else:
                    return jsonify({'error': 'Missing automaton or operation parameter'}), 400
            
            # Handle legacy JSON string format
            automaton_data = data['automaton']
            if isinstance(automaton_data, str):
                automaton_data = json.loads(automaton_data)
            
            if not self._validate_automaton_structure(automaton_data):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            automate = self._dict_to_automate(automaton_data)
            operation = data['operation']
            
            logger.info(f"Performing operation: {operation}")
            
            if operation == 'determinize' or operation == 'determiniser':
                result_automate = self.gestionnaire.determiniser_automate(automate)
            elif operation == 'minimize' or operation == 'minimiser':
                result_automate = self.gestionnaire.minimiser_automate(automate)
            elif operation == 'complete' or operation == 'completer':
                result_automate = self.gestionnaire.completer_automate(automate)
            elif operation == 'complement' or operation == 'complementaire':
                result_automate = self.gestionnaire.complementaire_automate(automate)
            elif operation == 'canoniser' or operation == "canonizer":
                result_automate = self.gestionnaire.canoniser_automate(automate)
            else:
                return jsonify({'error': f'Unknown operation: {operation}'}), 400
            
            result_automate.afficher()
            result = self._automate_to_dict(result_automate)
            
            return jsonify({
                'success': True,
                'automaton': result,
                'operation': operation,
                'message': f'Operation "{operation}" completed successfully'
            })
        except Exception as e:
            logger.error(f"Error transforming automaton: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Transformation failed: {str(e)}'}), 500

    # Binary automaton operations
    def union_automata(self):
        """Union of two automata"""
        return self._binary_operation('union')

    def intersection_automata(self):
        """Intersection of two automata"""
        return self._binary_operation('intersection')

    def concatenation_automata(self):
        """Concatenation of two automata"""
        return self._binary_operation('concatenation')

    def legacy_operations(self):
        """Legacy endpoint for binary operations"""
        try:
            data = request.get_json()
            if not data or 'automate1' not in data or 'automate2' not in data or 'operation' not in data:
                return jsonify({'error': 'Missing required parameters'}), 400
            
            # Convert to new format
            new_data = {
                'automaton1': data['automate1'] if isinstance(data['automate1'], dict) else json.loads(data['automate1']),
                'automaton2': data['automate2'] if isinstance(data['automate2'], dict) else json.loads(data['automate2'])
            }
            
            operation = data['operation']
            if operation == 'union':
                return self._binary_operation_with_data('union', new_data)
            elif operation == 'intersection':
                return self._binary_operation_with_data('intersection', new_data)
            elif operation == 'concatenation':
                return self._binary_operation_with_data('concatenation', new_data)
            else:
                return jsonify({'error': f'Unknown operation: {operation}'}), 400
                
        except Exception as e:
            logger.error(f"Error in legacy operations: {str(e)}")
            return jsonify({'error': f'Operation failed: {str(e)}'}), 500

    def kleene_star(self):
        """Kleene star of automaton"""
        try:
            data = request.get_json()
            if not data or 'automaton' not in data:
                return jsonify({'error': 'Missing automaton parameter'}), 400
            
            if not self._validate_automaton_structure(data['automaton']):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            automate = self._dict_to_automate(data['automaton'])
            result_automate = self.gestionnaire.etoile_automate(automate)
            result = self._automate_to_dict(result_automate)
            
            return jsonify({
                'success': True,
                'automaton': result,
                'operation': 'kleene_star',
                'message': 'Kleene star completed successfully'
            })
        except Exception as e:
            logger.error(f"Error in kleene star operation: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Kleene star operation failed: {str(e)}'}), 500

        # Word testing
    @handle_api_errors
    def test_word_simplified(self):
        """Version simplifiée du test de mot"""
        data = self._get_json_data(['automaton', 'word'])
        
        # Support format legacy
        if 'automate' in data and 'mot' in data:
            data['automaton'] = data['automate']
            data['word'] = data['mot']
        
        if not self._validate_automaton_structure(data['automaton']):
            return self._create_error_response('Invalid automaton structure')
        
        automate = self._dict_to_automate(data['automaton'])
        word = data['word']
        accepted = self.gestionnaire.tester_mot(automate, word)
        
        return jsonify(self._create_success_response({
            'accepted': accepted,
            'result': accepted,  # Support legacy
            'word': word
        }, f'Word "{word}" {"accepted" if accepted else "rejected"}'))


    def compare_automata(self):
        """Compare automata equivalence"""
        try:
            data = request.get_json()
            if not data or 'automaton1' not in data or 'automaton2' not in data:
                return jsonify({'error': 'Missing automaton parameters'}), 400
            
            if not self._validate_automaton_structure(data['automaton1']) or \
                not self._validate_automaton_structure(data['automaton2']):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            auto1 = self._dict_to_automate(data['automaton1'])
            auto2 = self._dict_to_automate(data['automaton2'])
            equivalent = self.gestionnaire.tester_equivalence(auto1, auto2)
            
            return jsonify({
                'success': True,
                'equivalent': equivalent,
                'message': f'Automata are {"equivalent" if equivalent else "not equivalent"}'
            })
        except Exception as e:
            logger.error(f"Error comparing automata: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Comparison failed: {str(e)}'}), 500

    def export_automaton(self):
        """Export automaton in various formats"""
        try:
            data = request.get_json()
            if not data or 'automaton' not in data or 'format' not in data:
                return jsonify({'error': 'Missing automaton or format parameter'}), 400
            
            if not self._validate_automaton_structure(data['automaton']):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            automate = self._dict_to_automate(data['automaton'])
            export_format = data['format']
            filename = data.get('filename', 'automaton')
            
            if export_format == 'json':
                result = self.gestionnaire.generer_donnees_json(automate)
                return jsonify({
                    'success': True,
                    'format': 'json',
                    'data': json.loads(result),
                    'filename': f'{filename}.json'
                })
            elif export_format == 'dot':
                return jsonify({'error': 'DOT export not yet implemented'}), 501
            elif export_format == 'latex':
                return jsonify({'error': 'LaTeX export not yet implemented'}), 501
            else:
                return jsonify({'error': f'Unknown format: {export_format}'}), 400
        except Exception as e:
            logger.error(f"Error exporting automaton: {str(e)}")
            return jsonify({'error': f'Export failed: {str(e)}'}), 500

    def trace_word(self):
        """Trace word recognition through automaton"""
        try:
            data = request.get_json()
            if not data or 'automaton' not in data or 'word' not in data:
                return jsonify({'error': 'Missing automaton or word parameter'}), 400
            
            if not self._validate_automaton_structure(data['automaton']):
                return jsonify({'error': 'Invalid automaton structure'}), 400
            
            automate = self._dict_to_automate(data['automaton'])
            word = data['word']
            
            # Build execution path
            path = []
            current = automate.etat_initial
            path.append({'state': str(current)})
            
            # Handle empty word case
            if word == '':
                accepted = current in automate.etats_finaux
                return jsonify({
                    'success': True,
                    'path': path,
                    'accepted': accepted,
                    'word': word
                })
            
            # Process each symbol
            for i, sym in enumerate(word):
                if current in automate.transitions and sym in automate.transitions[current]:
                    destinations = automate.transitions[current][sym]
                    if destinations:
                        # Take first available transition (for deterministic behavior)
                        current = next(iter(destinations))
                        path.append({'state': str(current), 'symbol': sym})
                    else:
                        # No valid transition
                        return jsonify({
                            'success': True,
                            'path': path,
                            'accepted': False,
                            'word': word,
                            'error': f'No transition for symbol "{sym}" from state "{current}"'
                        })
                else:
                    # No transition defined for this symbol from current state
                    return jsonify({
                        'success': True,
                        'path': path,
                        'accepted': False,
                        'word': word,
                        'error': f'No transition for symbol "{sym}" from state "{current}"'
                    })
            
            accepted = current in automate.etats_finaux
            return jsonify({
                'success': True,
                'path': path,
                'accepted': accepted,
                'word': word
            })
            
        except Exception as e:
            logger.error(f"Error tracing word: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Word tracing failed: {str(e)}'}), 500

        # History and utility endpoints
    def get_operations_history(self):
        """Get operations history"""
        try:
            return jsonify({
                'success': True,
                'history': self.gestionnaire.operations_history
            })
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

    def clear_operations_history(self):
        """Clear operations history"""
        try:
            self.gestionnaire.operations_history.clear()
            return jsonify({
                'success': True,
                'message': 'Operations history cleared'
            })
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return jsonify({'error': f'Failed to clear history: {str(e)}'}), 500

        # API endpoints listing
    @handle_api_errors
    def list_endpoints(self):
        """List all available API endpoints"""
        endpoints = self.generer_api_endpoints()
        return jsonify({
            'success': True,
            'endpoints': list(endpoints.keys()),
            'total': len(endpoints)
        })
    
    @handle_api_errors
    def _setup_error_handlers(self):
        """Setup error handlers"""
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404

        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({'error': 'Method not allowed'}), 405

        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {str(error)}")
            return jsonify({'error': 'Internal server error'}), 500

    @handle_api_errors
    def _binary_operation(self, operation: str):
        """Helper method for binary operations"""
        try:
            data = request.get_json()
            return self._binary_operation_with_data(operation, data)
        except Exception as e:
            logger.error(f"Error in {operation} operation: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'{operation.title()} operation failed: {str(e)}'}), 500

    @handle_api_errors
    def _binary_operation_with_data(self, operation: str, data: dict):
        """Execute binary operation with given data"""
        if not data or 'automaton1' not in data or 'automaton2' not in data:
            return jsonify({'error': 'Missing automaton parameters'}), 400
        
        # Validate both automata
        if not self._validate_automaton_structure(data['automaton1']) or \
           not self._validate_automaton_structure(data['automaton2']):
            return jsonify({'error': 'Invalid automaton structure'}), 400
        
        auto1 = self._dict_to_automate(data['automaton1'])
        auto2 = self._dict_to_automate(data['automaton2'])
        
        if operation == 'union':
            result_automate = self.gestionnaire.union_automates(auto1, auto2)
        elif operation == 'intersection':
            result_automate = self.gestionnaire.intersection_automates(auto1, auto2)
        elif operation == 'concatenation':
            result_automate = self.gestionnaire.concatenation_automates(auto1, auto2)
        else:
            return jsonify({'error': f'Unknown operation: {operation}'}), 400
        
        result = self._automate_to_dict(result_automate)
        
        return jsonify({
            'success': True,
            'automaton': result,
            'operation': operation,
            'message': f'{operation.title()} completed successfully'
        })

    @handle_api_errors
    def _validate_automaton_structure(self, data: Dict[str, Any]) -> bool:
        """Version simplifiée de la validation"""
        try:
            # Conversion automatique du format legacy
            if 'etats' in data:
                data = self._convert_legacy_format(data)
            
            # Vérification des champs requis
            required = ['alphabet', 'states', 'initial_state', 'final_states', 'transitions']
            if not all(field in data for field in required):
                return False
            
            # Vérifications de base
            states_set = set(data['states'])
            return (
                len(data['states']) == len(states_set) and  # États uniques
                data['initial_state'] in states_set and     # État initial valide
                all(fs in states_set for fs in data['final_states']) and  # États finaux valides
                all(self._is_valid_transition(t, states_set, data['alphabet']) for t in data['transitions'])
            )
        except:
            return False
        
    @handle_api_errors    
    def _is_valid_transition(self, transition: dict, states: set, alphabet: list) -> bool:
        """Valide une transition individuelle"""
        symbol_field = 'symbol' if 'symbol' in transition else 'symbole'
        required_fields = ['source', 'destination', symbol_field]

        if not all(field in transition for field in required_fields):
            return False

        symbol = transition[symbol_field]
        return (
            transition['source'] in states and
            transition['destination'] in states and
            (symbol == '' or symbol in alphabet)
        )

    @handle_api_errors
    def _convert_legacy_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy format to new format"""
        return {
            'alphabet': data.get('alphabet', []),
            'states': data.get('etats', []),
            'initial_state': data.get('etat_initial', ''),
            'final_states': data.get('etats_finaux', []),
            'transitions': [
                {
                    'source': t.get('source', ''),
                    'symbol': t.get('symbole', t.get('symbol', '')),
                    'destination': t.get('destination', '')
                }
                for t in data.get('transitions', [])
            ]
        }

    @handle_api_errors
    def _automate_to_dict(self, automate: Automate) -> Dict[str, Any]:
        """Convert Automate object to dictionary format expected by client"""
        return {
            'alphabet': list(automate.alphabet),
            'states': [str(state) for state in automate.etats],
            'initial_state': str(automate.etat_initial),
            'final_states': [str(state) for state in automate.etats_finaux],
            'transitions': [
                {
                    'source': str(source),
                    'symbol': symbol,
                    'destination': str(dest)
                }
                for source, trans in automate.transitions.items()
                for symbol, destinations in trans.items()
                for dest in destinations
            ]
        }
    

    
    @handle_api_errors
    def _validate_binary_request(self, data: dict) -> bool:
        """Valide une requête d'opération binaire"""
        return (
            data and 
            'automaton1' in data and 
            'automaton2' in data and
            self._validate_automaton_structure(data['automaton1']) and
            self._validate_automaton_structure(data['automaton2'])
        )
    
    def _handle_binary_operation(self, operation_name: str):
        """Gestionnaire unifié pour toutes les opérations binaires"""
        data = request.get_json()
        if not self._validate_binary_request(data):
            return jsonify({'error': 'Invalid binary operation request'}), 400
        
        auto1 = self._dict_to_automate(data['automaton1'])
        auto2 = self._dict_to_automate(data['automaton2'])
        
        operations = {
            'union': self.gestionnaire.union_automates,
            'intersection': self.gestionnaire.intersection_automates,
            'concatenation': self.gestionnaire.concatenation_automates
        }
        
        if operation_name not in operations:
            return jsonify({'error': f'Unknown operation: {operation_name}'}), 400
        
        result_automate = operations[operation_name](auto1, auto2)
        result = self._automate_to_dict(result_automate)
        
        return jsonify({
            'success': True,
            'automaton': result,
            'operation': operation_name,
            'message': f'{operation_name.title()} completed successfully'
        })
    
    def _create_success_response(self, data: dict, message: str = None) -> dict:
        """Crée une réponse de succès standardisée"""
        response = {'success': True}
        response.update(data)
        if message:
            response['message'] = message
        return response

    def _create_error_response(self, error: str, code: int = 400) -> tuple:
        """Crée une réponse d'erreur standardisée"""
        return jsonify({'error': error}), code
    
    def _get_json_data(self, required_fields: list = None) -> dict:
        """Récupère et valide les données JSON de la requête"""
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data provided")
        
        if required_fields:
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise ValueError(f"Missing fields: {', '.join(missing)}")
        
        return data


    def _dict_to_automate(self, data: Dict[str, Any]) -> Automate:
        """Convert dictionary to Automate object"""
        # Handle legacy format
        if 'etats' in data:
            data = self._convert_legacy_format(data)
        
        # Create states
        etats = {Etat(name) for name in data['states']}
        etat_initial = None
        etats_finaux = set()
        
        # Set initial and final states
        for etat in etats:
            if str(etat) == data['initial_state']:
                etat.est_initial = True
                etat_initial = etat
            if str(etat) in data['final_states']:
                etat.est_final = True
                etats_finaux.add(etat)
        
        # Create automaton
        automate = Automate(
            alphabet=set(data['alphabet']),
            etats=etats,
            etat_initial=etat_initial,
            etats_finaux=etats_finaux
        )
        
        try:
            # Add transitions
            for transition in data['transitions']:
                source = next(e for e in etats if str(e) == transition['source'])
                dest = next(e for e in etats if str(e) == transition['destination'])
                symbol = transition.get('symbol', transition.get('symbole', ''))
                automate.ajouter_transition(source, symbol, dest)
        except Exception as e:
            logger.error(f"Error Converting dict to automaton: {str(e)}")
            return jsonify({'error': f'Failed Converting dict to automaton: {str(e)}'}), 500
        
        return automate

    def generer_api_endpoints(self) -> Dict[str, str]:
        """Generate API endpoints description"""
        return {
            # Regex operations
            "/api/regex/convert": "Convert regex to automaton",
            "/api/regex/validate": "Validate regex syntax",
            "/api/regex": "Legacy: Convert regex to automaton",
            
            # Single automaton operations
            "/api/automaton/transform": "Transform automaton (determinize, minimize, complete, complement)",
            "/api/transformer": "Legacy: Transform automaton",
            
            # Binary automaton operations
            "/api/automaton/union": "Union of two automata",
            "/api/automaton/intersection": "Intersection of two automata",
            "/api/automaton/concatenation": "Concatenation of two automata",
            "/api/operations": "Legacy: Binary operations on automata",
            
            # Unary operations
            "/api/automaton/kleene": "Kleene star of automaton",
            '/api/automaton/states': "Operations sur le traitements des etats de l'automate", 

            # Testing and comparison
            "/api/automaton/test": "Test word acceptance",
            "/api/tester": "Legacy: Test word acceptance",
            "/api/automaton/compare": "Compare automata equivalence",
            "/api/automaton/trace": "Trace word recognition",
            
            # Automaton to regex
            "/api/automaton/a2regex": "From Automaton to regex",
            "/api/automaton/eqn2regex": "From Eqn 2 regex" ,
            
            # Utility
            "/api/automaton/export": "Export automaton in various formats",
            "/api/automaton/history": "Get operations history",
            "/api/automaton/clear-history": "Clear operations history",
            "/api/endpoints": "List all available endpoints",
            "/api/health": "Health check"
        }

    def ouvrir_navigateur(self) -> None:
        """Open interface in browser"""
        if self.auto_open_browser:
            def open_browser():
                time.sleep(1.5)  # Wait for server to start
                webbrowser.open(f"http://{self.host}:{self.port}")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

    def demarrer_serveur(self) -> None:
        """Start the server (legacy method name)"""
        self.run()

    def arreter_serveur(self) -> None:
        """Stop the server (legacy method name)"""
        self.stop()

    def run(self):
        """Start the Flask server"""
        logger.info(f"Starting Enhanced Automaton Server on {self.host}:{self.port}")
        
        # Open browser if requested
        self.ouvrir_navigateur()
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )

    def run_threaded(self):
        """Run server in a separate thread"""
        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        return self.server_thread

    def stop(self):
        """Stop the server"""
        # Flask doesn't have a built-in stop method, 
        # this would need to be implemented with werkzeug
        logger.info("Server stop requested")








def create_app():
    """Factory function to create Flask app"""
    server = AutomatonServer()
    return server.app

def main():
    """Main entry point"""
    server = AutomatonServer(
        host='localhost',
        port=8080,
        debug=True,
        auto_open_browser=True
    )
    
    print("=" * 60)
    print("🤖 Automaton Server v2.0")
    print("=" * 60)
    print(f"🌐 Server: http://{server.host}:{server.port}")
    print(f"📚 Health: http://{server.host}:{server.port}/api/health")
    print("=" * 50)
    print("Available endpoints:")
    print("  • POST /api/regex/convert - Convert regex to automaton")
    print("  • POST /api/regex/validate - Validate regex syntax")
    print("  • POST /api/automaton/transform - Transform automaton")
    print("  • POST /api/automaton/a2regex - From Automaton to regex")
    print("  • POST /api/automaton/eqn2regex - From Eqn 2 regex")
    print("  • POST /api/automaton/union - Union of two automata")
    print("  • POST /api/automaton/intersection - Intersection of two automata")
    print("  • POST /api/automaton/concatenation - Concatenation of two automata")
    print("  • POST /api/automaton/kleene - Kleene star of automaton")
    print("  • POST /api/automaton/test - Test word acceptance")
    print("  • POST /api/automaton/compare - Compare automata equivalence")
    print("  • POST /api/automaton/export - Export automaton")
    print("  • POST /api/automaton/trace - Trace word recognition")
    print("  • GET /api/automaton/history - Get operations history")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")

if __name__ == '__main__':
    main()