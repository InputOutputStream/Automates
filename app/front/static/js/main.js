function showModal(content) {
    const modal = document.getElementById('modal');
    document.getElementById('modal-content').textContent = content;
    modal.classList.add('show');
}

function hideModal() {
    document.getElementById('modal').classList.remove('show');
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.querySelector('button').addEventListener('click', hideModal);
    }

    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.addEventListener('change', (e) => {
            document.body.classList.toggle('dark', e.target.value === 'dark');
        });
    }
});

async function animateRecognition(mot) {
    if (!window.cy) return;
    const response = await fetch('/api/trace_mot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mot })
    });
    const data = await response.json();
    if (data.error) {
        showModal(data.error);
        return;
    }

    const cy = window.cy;
    let i = 0;
    cy.nodes().removeClass('highlight');
    cy.edges().removeClass('highlight');
    const interval = setInterval(() => {
        cy.nodes().removeClass('highlight');
        cy.edges().removeClass('highlight');
        if (i < data.path.length) {
            cy.getElementById(data.path[i].state).addClass('highlight');
            if (i > 0) {
                const edgeId = `${data.path[i-1].state}-${data.path[i].symbol}-${data.path[i].state}`;
                cy.getElementById(edgeId).addClass('highlight');
            }
            i++;
        } else {
            clearInterval(interval);
            showModal(`Le mot '${mot}' est ${data.accepte ? 'accepté' : 'rejeté'}.`);
        }
    }, 500);
}