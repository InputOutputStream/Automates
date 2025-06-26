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
        self.app = Flask(__name__)
        CORS(self.app)
        self.host = host
        self.port = port
        self.debug = debug
        self.auto_open_browser = auto_open_browser
        self.gestionnaire = GestionnaireOperations()
        self.server_thread = None
        self._setup_routes()
        self._setup_error_handlers()

    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main interface"""
            return render_template('index.html')

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'automaton-server',
                'version': '2.0.0',
                'features': ['regex_conversion', 'automaton_operations', 'word_testing', 'equivalence_checking']
            })

        # Regex operations
        @self.app.route('/api/regex/convert', methods=['POST'])
        @self.app.route('/api/regex', methods=['POST'])  # Legacy endpoint
        def convert_regex():
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

        @self.app.route('/api/regex/validate', methods=['POST'])
        def validate_regex():
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
            
        @self.app.route('/api/automaton/a2regex', methods=['POST'])          
        @self.app.route('/api/a2regex', methods=['POST'])
        def a2regex():
            """From automaton to regex using Arden Lemma"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data:
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
                
                logger.info(f"Solving Automaton")
                
                result = self.gestionnaire.automaton2eqn(automate)
                return jsonify({
                    'success': True,
                    'regex': result,
                    'message': f'Operation completed successfully'
                })
            except Exception as e:
                logger.error(f"Error transforming automaton: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Resolution failed: {str(e)}'}), 500




        @self.app.route('/api/automaton/eqn2regex', methods=['POST'])
        @self.app.route('/api/eqn2regex', methods=['POST'])  # Legacy endpoint
        def eqn2regex():
            """From equations to regex using Arden Lemma"""
            try:
                data = request.get_json()
                if not data or 'equations' not in data:
                    # Support legacy format
                    if 'equations' in data:
                        data['equations'] = data['equations']
                    else:
                        return jsonify({'error': 'Missing equation or operation parameter'}), 400
                
                equations = data['equations']
                alphabet = data['alphabet']

                equations = dict(equations)
                
                if not self.gestionnaire.validate_equations(equations):
                    return jsonify({'error': 'Invalid equations format structure'}), 400
                
                result = self.gestionnaire.eqn2reg(equations, alphabet)
                logger.info(f"Solving Equations")
                
            except Exception as e:
                logger.error(f"Error solving eqn systeme: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Resolution failed: {str(e)}'}), 500



        # Single automaton operations
        @self.app.route('/api/automaton/transform', methods=['POST'])
        @self.app.route('/api/transformer', methods=['POST'])  # Legacy endpoint
        def transform_automaton():
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
        @self.app.route('/api/automaton/union', methods=['POST'])
        def union_automata():
            """Union of two automata"""
            return self._binary_operation('union')

        @self.app.route('/api/automaton/intersection', methods=['POST'])
        def intersection_automata():
            """Intersection of two automata"""
            return self._binary_operation('intersection')

        @self.app.route('/api/automaton/concatenation', methods=['POST'])
        def concatenation_automata():
            """Concatenation of two automata"""
            return self._binary_operation('concatenation')

        @self.app.route('/api/operations', methods=['POST'])  # Legacy endpoint
        def legacy_operations():
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

        @self.app.route('/api/automaton/kleene', methods=['POST'])
        def kleene_star():
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
        @self.app.route('/api/automaton/test', methods=['POST'])
        @self.app.route('/api/tester', methods=['POST'])  # Legacy endpoint
        def test_word():
            """Test word acceptance"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'word' not in data:
                    # Support legacy format
                    if 'automate' in data and 'mot' in data:
                        data['automaton'] = data['automate']
                        data['word'] = data['mot']
                    else:
                        return jsonify({'error': 'Missing automaton or word parameter'}), 400
                
                # Handle legacy JSON string format
                automaton_data = data['automaton']
                if isinstance(automaton_data, str):
                    automaton_data = json.loads(automaton_data)
                
                if not self._validate_automaton_structure(automaton_data):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                automate = self._dict_to_automate(automaton_data)
                word = data['word']
                
                # Handle empty word case
                if word == '':
                    logger.info("Testing empty word")
                
                accepted = self.gestionnaire.tester_mot(automate, word)
                
                print("est sorti ??")
                return jsonify({
                    'success': True,
                    'accepted': accepted,
                    'result': accepted,  # Legacy format support
                    'word': word,
                    'message': f'Word "{word}" {"accepted" if accepted else "rejected"}'
                })
            except Exception as e:
                logger.error(f"Error testing word: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Word test failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/compare', methods=['POST'])
        def compare_automata():
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

        @self.app.route('/api/automaton/export', methods=['POST'])
        def export_automaton():
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

        @self.app.route('/api/automaton/trace', methods=['POST'])
        def trace_word():
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
        @self.app.route('/api/automaton/history', methods=['GET'])
        def get_operations_history():
            """Get operations history"""
            try:
                return jsonify({
                    'success': True,
                    'history': self.gestionnaire.operations_history
                })
            except Exception as e:
                logger.error(f"Error getting history: {str(e)}")
                return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

        @self.app.route('/api/automaton/clear-history', methods=['POST'])
        def clear_operations_history():
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
        @self.app.route('/api/endpoints', methods=['GET'])
        def list_endpoints():
            """List all available API endpoints"""
            endpoints = self.generer_api_endpoints()
            return jsonify({
                'success': True,
                'endpoints': list(endpoints.keys()),
                'total': len(endpoints)
            })

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

    def _binary_operation(self, operation: str):
        """Helper method for binary operations"""
        try:
            data = request.get_json()
            return self._binary_operation_with_data(operation, data)
        except Exception as e:
            logger.error(f"Error in {operation} operation: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'{operation.title()} operation failed: {str(e)}'}), 500

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

    def _validate_automaton_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the automaton data has the required structure"""
        try:
            # Handle legacy format conversion
            if 'etats' in data:
                data = self._convert_legacy_format(data)
            
            required_fields = ['alphabet', 'states', 'initial_state', 'final_states', 'transitions']
            
            # Check all required fields exist
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate types
            if not isinstance(data['alphabet'], list):
                logger.error("Alphabet must be a list")
                return False
            
            if not isinstance(data['states'], list):
                logger.error("States must be a list")
                return False
            
            if not isinstance(data['initial_state'], str):
                logger.error("Initial state must be a string")
                return False
            
            if not isinstance(data['final_states'], list):
                logger.error("Final states must be a list")
                return False
            
            if not isinstance(data['transitions'], list):
                logger.error("Transitions must be a list")
                return False
            
            # Validate initial state exists in states
            if data['initial_state'] not in data['states']:
                logger.error("Initial state not in states list")
                return False
            
            # Validate final states exist in states
            for final_state in data['final_states']:
                if final_state not in data['states']:
                    logger.error(f"Final state {final_state} not in states list")
                    return False
            
            # Validate transition structure
            for transition in data['transitions']:
                if not isinstance(transition, dict):
                    logger.error("Each transition must be a dictionary")
                    return False
                
                # Support both formats
                required_trans_fields = ['source', 'destination']
                symbol_field = 'symbol' if 'symbol' in transition else 'symbole'
                
                for field in required_trans_fields + [symbol_field]:
                    if field not in transition:
                        logger.error(f"Transition missing field: {field}")
                        return False
                
                # Validate transition states exist
                if transition['source'] not in data['states']:
                    logger.error(f"Transition source {transition['source']} not in states")
                    return False
                
                if transition['destination'] not in data['states']:
                    logger.error(f"Transition destination {transition['destination']} not in states")
                    return False
                
                # Validate symbol is in alphabet
                symbol = transition[symbol_field]
                if symbol != '' and symbol not in data['alphabet']:
                    logger.error(f"Transition symbol {symbol} not in alphabet")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating automaton structure: {str(e)}")
            return False

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