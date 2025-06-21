"""
Interface Web pour la manipulation des Automates
Structure de base avec génération HTML/CSS/JS via Dominate
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import traceback
from typing import Dict, Any
import logging

from .GestionnaireOperations import GestionnaireOperations
from .RegexParser import RegexParser
from ..Automate import Automate
from ..Etat import Etat

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatonFlaskServer:
    """
    Flask-based server for automaton operations
    """
    
    def __init__(self, host='localhost', port=8080, debug=True):
        """Initialize the Flask server"""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web app integration
        
        self.host = host
        self.port = port
        self.debug = debug
        
        # Initialize core components
        self.gestionnaire = GestionnaireOperations()
        self.regex_parser = RegexParser()
        
        # Setup routes
        self._setup_routes()
        
        # Setup error handlers
        self._setup_error_handlers()
    
    def _setup_routes(self):
        """Setup all Flask routes"""
        
        # Home route - serve main interface
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        # API Routes
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'automaton-server',
                'version': '1.0.0'
            })
        
        # Regex conversion endpoints
        @self.app.route('/api/regex/convert', methods=['POST'])
        def convert_regex():
            """Convert regex to automaton"""
            try:
                data = request.get_json()
                if not data or 'regex' not in data:
                    return jsonify({'error': 'Missing regex parameter'}), 400
                
                regex = data['regex']
                logger.info(f"Converting regex: {regex}")
                
                # Use regex parser instead of simple conversion
                automate = self.regex_parser.parser_regex(regex)
                result = self._automate_to_dict(automate)
                
                return jsonify({
                    'success': True,
                    'automaton': result,
                    'message': f'Regex "{regex}" converted successfully'
                })
                
            except Exception as e:
                logger.error(f"Error converting regex: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/regex/validate', methods=['POST'])
        def validate_regex():
            """Validate regex syntax"""
            try:
                data = request.get_json()
                if not data or 'regex' not in data:
                    return jsonify({'error': 'Missing regex parameter'}), 400
                
                regex = data['regex']
                is_valid, message = self.regex_parser.valider_syntaxe(regex)
                
                return jsonify({
                    'valid': is_valid,
                    'message': message
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Automaton transformation endpoints
        @self.app.route('/api/automaton/transform', methods=['POST'])
        def transform_automaton():
            """Transform automaton (determinize, minimize, etc.)"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'operation' not in data:
                    return jsonify({'error': 'Missing automaton or operation parameter'}), 400
                
                automate = self._dict_to_automate(data['automaton'])
                operation = data['operation']
                
                logger.info(f"Performing operation: {operation}")
                
                # Perform the requested operation
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
                return jsonify({'error': str(e)}), 500
        
        # Automaton operations endpoints
        @self.app.route('/api/automaton/union', methods=['POST'])
        def union_automata():
            """Union of two automata"""
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
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
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automaton/intersection', methods=['POST'])
        def intersection_automata():
            """Intersection of two automata"""
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
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
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automaton/concatenation', methods=['POST'])
        def concatenation_automata():
            """Concatenation of two automata"""
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
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
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automaton/kleene', methods=['POST'])
        def kleene_star():
            """Kleene star of an automaton"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data:
                    return jsonify({'error': 'Missing automaton parameter'}), 400
                
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
                return jsonify({'error': str(e)}), 500
        
        # Word testing endpoints
        @self.app.route('/api/automaton/test', methods=['POST'])
        def test_word():
            """Test if a word is accepted by the automaton"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'word' not in data:
                    return jsonify({'error': 'Missing automaton or word parameter'}), 400
                
                automate = self._dict_to_automate(data['automaton'])
                word = data['word']
                
                accepted = self.gestionnaire.tester_mot(automate, word)
                
                return jsonify({
                    'success': True,
                    'accepted': accepted,
                    'word': word,
                    'message': f'Word "{word}" {"accepted" if accepted else "rejected"}'
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automaton/compare', methods=['POST'])
        def compare_automata():
            """Compare two automata for equivalence"""
            try:
                data = request.get_json()
                if not data or 'automaton1' not in data or 'automaton2' not in data:
                    return jsonify({'error': 'Missing automaton parameters'}), 400
                
                auto1 = self._dict_to_automate(data['automaton1'])
                auto2 = self._dict_to_automate(data['automaton2'])
                
                equivalent = self.gestionnaire.tester_equivalence(auto1, auto2)
                
                return jsonify({
                    'success': True,
                    'equivalent': equivalent,
                    'message': f'Automata are {"equivalent" if equivalent else "not equivalent"}'
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Export/Import endpoints
        @self.app.route('/api/automaton/export', methods=['POST'])
        def export_automaton():
            """Export automaton in various formats"""
            try:
                data = request.get_json()
                if not data or 'automaton' not in data or 'format' not in data:
                    return jsonify({'error': 'Missing automaton or format parameter'}), 400
                
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
                    # Implement DOT export
                    return jsonify({'error': 'DOT export not yet implemented'}), 501
                elif export_format == 'latex':
                    # Implement LaTeX export
                    return jsonify({'error': 'LaTeX export not yet implemented'}), 501
                else:
                    return jsonify({'error': f'Unknown format: {export_format}'}), 400
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Utility endpoints
        @self.app.route('/api/automaton/history', methods=['GET'])
        def get_operations_history():
            """Get the history of operations performed"""
            return jsonify({
                'success': True,
                'history': self.gestionnaire.operations_history
            })
        
        @self.app.route('/api/automaton/clear-history', methods=['POST'])
        def clear_operations_history():
            """Clear the operations history"""
            self.gestionnaire.operations_history.clear()
            return jsonify({
                'success': True,
                'message': 'Operations history cleared'
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
    
    def _automate_to_dict(self, automate: Automate) -> Dict[str, Any]:
        """Convert automaton object to dictionary"""
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
        """Convert dictionary to automaton object"""
        # Create states
        etats = {Etat(name) for name in data['states']}
        
        # Find initial and final states
        etat_initial = None
        etats_finaux = set()
        
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
        """Run the Flask server"""
        logger.info(f"Starting Automaton Flask Server on {self.host}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )

# Main execution
def create_app():
    """Factory function to create Flask app"""
    server = AutomatonFlaskServer()
    return server.app

def main():
    """Main entry point"""
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