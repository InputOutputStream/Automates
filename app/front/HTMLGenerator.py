try:
    from dominate import document
    from dominate.tags import *
    DOMINATE_AVAILABLE = True
except ImportError:
    DOMINATE_AVAILABLE = False
    print("Warning: dominate library not available. HTML generation will be limited.")


class HTMLGenerator:
    """
    Générateur de pages HTML complètes avec ou sans Dominate
    """
    
    def __init__(self, titre: str = "Interface Automates"):
        """Initialise le générateur HTML"""
        self.titre = titre
        self.use_dominate = DOMINATE_AVAILABLE
    
    def creer_document_base(self):
        """Crée la structure HTML de base"""
        if self.use_dominate:
            doc = document(title=self.titre)
            doc.head.add(meta(charset="utf-8"))
            doc.head.add(meta(name="viewport", content="width=device-width, initial-scale=1"))
            return doc
        else:
            return self._creer_html_basique()
    
    def _creer_html_basique(self) -> str:
        """Crée HTML basique sans dominate"""
        return f"""<!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{self.titre}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                <script src="https://d3js.org/d3.v7.min.js"></script>
            </head>
            <body>
                <div class="container-fluid">
                    <h1 class="text-center my-4">{self.titre}</h1>
                    <div id="main-content"></div>
                </div>
            </body>
            </html>"""
    
    def ajouter_css_bootstrap(self, doc) -> None:
        """Ajoute Bootstrap pour le responsive"""
        if self.use_dominate:
            doc.head.add(link(
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
                rel="stylesheet"
            ))
    
    def ajouter_css_personnalise(self, doc, styles: str) -> None:
        """Ajoute les styles CSS personnalisés"""
        if self.use_dominate:
            doc.head.add(style(styles))
    
    def ajouter_js_bibliotheques(self, doc) -> None:
        """Ajoute jQuery, D3.js ou autres bibliothèques"""
        if self.use_dominate:
            doc.head.add(script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"))
            doc.head.add(script(src="https://d3js.org/d3.v7.min.js"))
    
    def ajouter_js_personnalise(self, doc, code_js: str) -> None:
        """Ajoute le JavaScript personnalisé"""
        if self.use_dominate:
            doc.body.add(script(code_js))
    
    def generer_fichier_html(self, doc, nom_fichier: str) -> str:
        """Génère et sauvegarde le fichier HTML"""
        if self.use_dominate:
            contenu = str(doc)
        else:
            contenu = doc
        
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            f.write(contenu)
        
        return contenu


