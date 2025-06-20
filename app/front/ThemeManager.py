

class ThemeManager:
    """
    Gestionnaire des thèmes visuels
    """
    
    def __init__(self):
        """Initialise le gestionnaire de thèmes"""
        self.themes = ["clair", "sombre", "contraste_eleve"]
    
    def generer_theme_clair(self) -> str:
        """Génère le CSS pour le thème clair"""
        return """
        body { background-color: #f8f9fa; color: #212529; }
        .bg-light { background-color: #ffffff; }
        .text-dark { color: #212529; }
        """
    
    def generer_theme_sombre(self) -> str:
        """Génère le CSS pour le thème sombre"""
        return """
        body { background-color: #212529; color: #f8f9fa; }
        .bg-light { background-color: #343a40; }
        .text-dark { color: #f8f9fa; }
        """
    
    def generer_theme_contraste_eleve(self) -> str:
        """Génère le CSS pour l'accessibilité"""
        return """
        body { background-color: #000000; color: #ffffff; }
        .bg-light { background-color: #333333; }
        .text-dark { color: #ffffff; }
        """
    
    def generer_selecteur_theme(self) -> str:
        """Génère le sélecteur de thème"""
        options = [f"<option value='{theme}'>{theme.capitalize()}</option>" for theme in self.themes]
        return f"""
        <select id="theme-selector" class="border rounded px-2 py-1">
            {''.join(options)}
        </select>
        """
    
    def generer_js_changement_theme(self) -> str:
        """Génère JS pour changer de thème"""
        return """
        document.getElementById('theme-selector').addEventListener('change', (e) => {
            document.body.className = e.target.value;
        });
        """
