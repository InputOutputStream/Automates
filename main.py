#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application Automates
"""
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.front.serveur import create_app

if __name__ == '__main__':
    print("🤖 Démarrage du serveur Automates...")
    print("📱 Interface web disponible sur: http://localhost:5000")
    print("🔗 API disponible sur: http://localhost:5000/api/")
    
    # Démarrer le serveur Flask
    app = create_app()
    app.run(
        host='0.0.0.0',  # Accessible depuis l'extérieur
        port=5000,       # Port par défaut
        debug=True       # Mode debug pour le développement
    )

