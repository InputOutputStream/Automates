import dominate
from dominate.tags import *

def build_interface():
    doc = dominate.document(title='TP INF3421 : Automates')

    with doc.head:
        link(rel='stylesheet', href='/static/index.css')
        script(src='/static/animation.js')

    with doc:
        with div(cls='container'):
            h1("TP INF3421 : Opérations sur les Automates")
            h2("Reconnaissance de mots")
            with form(action='/recognize', method='post'):
                label("Mot à reconnaître : ", for_='mot')
                input_(type='text', name='mot', id='mot')
                button("Tester le mot", type='submit')

    return str(doc)
