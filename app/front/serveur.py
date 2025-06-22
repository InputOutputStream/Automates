from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import json
import traceback
from typing import Dict, Any
import logging

from .GestionnaireOperations import GestionnaireOperations
from .RegexParser import RegexParser
from ..Automate import Automate
from ..Etat import Etat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatonFlaskServer:
    def __init__(self, host='localhost', port=8080, debug=True):
        self.app = Flask(__name__)
        CORS(self.app)
        self.host = host
        self.port = port
        self.debug = debug
        self.gestionnaire = GestionnaireOperations()
        self.regex_parser = RegexParser()
        self._setup_routes()
        self._setup_error_handlers()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'service': 'automaton-server',
                'version': '1.0.0'
            })

        @self.app.route('/api/regex/convert', methods=['POST'])
        def convert_regex():
            try:
                data = request.get_json()
                if not data or 'regex' not in data:
                    return jsonify({'error': 'Missing regex parameter'}), 400
                
                regex = data['regex']
                if not regex.strip():
                    return jsonify({'error': 'Empty regex provided'}), 400
                
                logger.info(f"Converting regex: {regex}")
                automate = self.regex_parser.parser_regex(regex)
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
                
                is_valid, message = self.regex_parser.valider_syntaxe(regex)
                return jsonify({
                    'valid': is_valid,
                    'message': message
                })
            except Exception as e:
                logger.error(f"Error validating regex: {str(e)}")
                return jsonify({'error': f'Regex validation failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/transform', methods=['POST'])
        def transform_automaton():
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'operation' not in data:
                    return jsonify({'error': 'Missing automaton or operation parameter'}), 400
                
                # Validate automaton structure
                automaton_data = data['automaton']
                if not self._validate_automaton_structure(automaton_data):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                automate = self._dict_to_automate(automaton_data)
                operation = data['operation']
                
                logger.info(f"Performing operation: {operation}")
                
                if operation == 'determinize':
                    result_automate = self.gestionnaire.determiniser_automate(automate)
                elif operation == 'minimize':
                    result_automate = self.gestionnaire.minimiser_automate(automate)
                elif operation == 'complete':
                    result_automate = self.gestionnaire.completer_automate(automate)
                elif operation == 'complement':
                    result_automate = self.gestionnaire.complementaire_automate(automate)
                else:
                    return jsonify({'error': f'Unknown operation: {operation}'}), 400
                
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

        @self.app.route('/api/automaton/union', methods=['POST'])
        def union_automata():
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
                # Validate both automata
                if not self._validate_automaton_structure(data['automaton1']) or \
                   not self._validate_automaton_structure(data['automaton2']):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                auto1 = self._dict_to_automate(data['automaton1'])
                auto2 = self._dict_to_automate(data['automaton2'])
                result_automate = self.gestionnaire.union_automates(auto1, auto2)
                result = self._automate_to_dict(result_automate)
                
                return jsonify({
                    'success': True,
                    'automaton': result,
                    'operation': 'union',
                    'message': 'Union completed successfully'
                })
            except Exception as e:
                logger.error(f"Error in union operation: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Union operation failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/intersection', methods=['POST'])
        def intersection_automata():
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
                if not self._validate_automaton_structure(data['automaton1']) or \
                   not self._validate_automaton_structure(data['automaton2']):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                auto1 = self._dict_to_automate(data['automaton1'])
                auto2 = self._dict_to_automate(data['automaton2'])
                result_automate = self.gestionnaire.intersection_automates(auto1, auto2)
                result = self._automate_to_dict(result_automate)
                
                return jsonify({
                    'success': True,
                    'automaton': result,
                    'operation': 'intersection',
                    'message': 'Intersection completed successfully'
                })
            except Exception as e:
                logger.error(f"Error in intersection operation: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Intersection operation failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/concatenation', methods=['POST'])
        def concatenation_automata():
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
                if not self._validate_automaton_structure(data['automaton1']) or \
                   not self._validate_automaton_structure(data['automaton2']):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                auto1 = self._dict_to_automate(data['automaton1'])
                auto2 = self._dict_to_automate(data['automaton2'])
                result_automate = self.gestionnaire.concatenation_automates(auto1, auto2)
                result = self._automate_to_dict(result_automate)
                
                return jsonify({
                    'success': True,
                    'automaton': result,
                    'operation': 'concatenation',
                    'message': 'Concatenation completed successfully'
                })
            except Exception as e:
                logger.error(f"Error in concatenation operation: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Concatenation operation failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/kleene', methods=['POST'])
        def kleene_star():
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

        @self.app.route('/api/automaton/test', methods=['POST'])
        def test_word():
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'word' not in data:
                    return jsonify({'error': 'Missing automaton or word parameter'}), 400
                
                if not self._validate_automaton_structure(data['automaton']):
                    return jsonify({'error': 'Invalid automaton structure'}), 400
                
                automate = self._dict_to_automate(data['automaton'])
                word = data['word']
                
                # Handle empty word case
                if word == '':
                    logger.info("Testing empty word")
                
                accepted = self.gestionnaire.tester_mot(automate, word)
                
                return jsonify({
                    'success': True,
                    'accepted': accepted,
                    'word': word,
                    'message': f'Word "{word}" {"accepted" if accepted else "rejected"}'
                })
            except Exception as e:
                logger.error(f"Error testing word: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Word test failed: {str(e)}'}), 500

        @self.app.route('/api/automaton/compare', methods=['POST'])
        def compare_automata():
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

        @self.app.route('/api/automaton/history', methods=['GET'])
        def get_operations_history():
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
            try:
                self.gestionnaire.operations_history.clear()
                return jsonify({
                    'success': True,
                    'message': 'Operations history cleared'
                })
            except Exception as e:
                logger.error(f"Error clearing history: {str(e)}")
                return jsonify({'error': f'Failed to clear history: {str(e)}'}), 500

    def _setup_error_handlers(self):
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

    def _validate_automaton_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the automaton data has the required structure"""
        try:
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
                
                required_trans_fields = ['source', 'symbol', 'destination']
                for field in required_trans_fields:
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
                if transition['symbol'] not in data['alphabet']:
                    logger.error(f"Transition symbol {transition['symbol']} not in alphabet")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating automaton structure: {str(e)}")
            return False

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
        
        # Add transitions
        for transition in data['transitions']:
            source = next(e for e in etats if str(e) == transition['source'])
            dest = next(e for e in etats if str(e) == transition['destination'])
            automate.ajouter_transition(source, transition['symbol'], dest)
        
        return automate

    def run(self):
        logger.info(f"Starting Automaton Flask Server on {self.host}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )

def create_app():
    server = AutomatonFlaskServer()
    return server.app

def main():
    server = AutomatonFlaskServer(
        host='localhost',
        port=8080,
        debug=True
    )
    print("=" * 50)
    print("🤖 Automaton Flask Server")
    print("=" * 50)
    print(f"🌐 Server: http://{server.host}:{server.port}")
    print(f"📚 API Docs: http://{server.host}:{server.port}/api/health")
    print("=" * 50)
    print("Available endpoints:")
    print("  • POST /api/regex/convert - Convert regex to automaton")
    print("  • POST /api/regex/validate - Validate regex syntax")
    print("  • POST /api/automaton/transform - Transform automaton")
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