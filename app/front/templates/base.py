from dominate import document
from dominate.tags import *
from dominate.util import raw

def render_base_page(title, content):
    doc = document(title=title)
    with doc.head:
        meta(charset="UTF-8")
        meta(name="viewport", content="width=device-width, initial-scale=1.0")
        link(rel="icon", type="image/x-icon", href="/favicon.ico")
        link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")
        link(rel="stylesheet", href="/static/css/custom.css")
        script(src="/static/js/cytoscape.min.js")
        script(src="/static/js/main.js")

    with doc.body.add(div(_class="min-h-screen bg-gray-100 flex flex-col")):
        with nav(_class="bg-blue-600 text-white p-4 shadow-md"):
            with div(_class="container mx-auto flex justify-between items-center"):
                h1("Démonstration d'Automate", _class="text-xl font-bold")
                with div(_class="flex space-x-2"):
                    button("Aide", _class="px-4 py-2 bg-blue-700 rounded hover:bg-blue-800 transition duration-300", onclick="showModal('Utilisez la barre latérale pour ajouter des états ou transitions, tester des mots, ou exporter l\\'automate.')")
                    select(id="theme-select", _class="p-2 rounded bg-blue-700 text-white")
                    option("Clair", value="light")
                    option("Sombre", value="dark")

        with main(_class="flex-1 flex container mx-auto p-4"):
            content()

        with footer(_class="bg-gray-800 text-white p-4 text-center"):
            p("© 2025 Démonstration d'Automate")

        # Modal
        with div(id="modal", _class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"):
            with div(_class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full animate-fade-in"):
                p(id="modal-content", _class="mb-4")
                button("Fermer", _class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-300", onclick="hideModal()")

    return doc.render()