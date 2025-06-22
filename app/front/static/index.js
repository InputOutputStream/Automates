let operationHistory = [];

function showTab(tabName) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');

    // Clear graphs when switching tabs
    ['regex', 'transform', 'operations', 'test'].forEach(tab => {
        const container = document.getElementById(`${tab}-graph`);
        container.innerHTML = '';
    });
}

function showResult(elementId, content, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = content;
    element.className = `result ${type}`;
    element.style.display = 'block';
}

function showModal(message, type = 'info') {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    modalMessage.textContent = message;
    modal.classList.add('active');
    modal.className = `modal ${type}`;
}

function hideModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('active');
}

function addToHistory(operation, input, output) {
    const timestamp = new Date().toLocaleString();
    operationHistory.unshift({
        timestamp,
        operation,
        input: typeof input === 'object' ? JSON.stringify(input, null, 2) : input,
        output: typeof output === 'object' ? JSON.stringify(output, null, 2) : output
    });

    if (operationHistory.length > 10) {
        operationHistory = operationHistory.slice(0, 10);
    }
    displayHistory();
}

function displayHistory() {
    const container = document.getElementById('history-container');
    if (operationHistory.length === 0) {
        container.innerHTML = '<p>No operations performed yet.</p>';
        return;
    }

    let html = '';
    operationHistory.forEach((item, index) => {
        html += `
            <div class="history-item">
                <strong>${item.operation}</strong> - ${item.timestamp}
                <br><small>Input: ${item.input.substring(0, 100)}${item.input.length > 100 ? '...' : ''}</small>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderGraph(automaton, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const elements = [
        ...automaton.states.map(state => ({
            data: {
                id: state,
                label: state,
                isInitial: state === automaton.initial_state,
                isFinal: automaton.final_states.includes(state)
            }
        })),
        ...automaton.transitions.map(t => ({
            data: {
                id: `${t.source}-${t.symbol}-${t.destination}`,
                source: t.source,
                target: t.destination,
                label: t.symbol
            }
        }))
    ];

    const cy = cytoscape({
        container,
        elements,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#60a5fa',
                    'label': 'data(label)',
                    'shape': 'circle',
                    'width': 50,
                    'height': 50,
                    'text-valign': 'center',
                    'color': '#fff',
                    'border-width': 'data(isFinal) ? 3 : 1',
                    'border-color': 'data(isFinal) ? #ef4444 : #000',
                    'font-size': 12
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#4b5563',
                    'target-arrow-color': '#4b5563',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': 10,
                    'text-rotation': 'autorotate'
                }
            },
            {
                selector: 'node[isInitial]',
                style: {
                    'background-color': '#22c55e'
                }
            },
            {
                selector: '.highlight',
                style: {
                    'background-color': '#f59e0b',
                    'line-color': '#f59e0b'
                }
            }
        ],
        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 500
        }
    });

    return cy;
}

async function animateRecognition(automaton, word, containerId) {
    const cy = renderGraph(automaton, containerId);
    const response = await fetch('/api/automaton/trace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ automaton, word })
    });

    const data = await response.json();
    if (data.error) {
        showModal(data.error, 'error');
        return;
    }

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
            showModal(`Word "${word}" is ${data.accepted ? 'ACCEPTED' : 'REJECTED'}.`, data.accepted ? 'success' : 'error');
        }
    }, 500);
}

async function validateRegex() {
    const regex = document.getElementById('regex-input').value;
    if (!regex) {
        showResult('regex-result', 'Please enter a regular expression.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/regex/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ regex })
        });
        const data = await response.json();
        showResult('regex-result', data.message, data.valid ? 'success' : 'error');
    } catch (error) {
        showResult('regex-result', `Error: ${error.message}`, 'error');
    }
}

document.getElementById('regex-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const regex = document.getElementById('regex-input').value;

    showResult('regex-result', '<div class="loading"></div> Converting...', 'info');

    try {
        const response = await fetch('/api/regex/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ regex })
        });
        const data = await response.json();
        if (data.error) {
            showResult('regex-result', data.error, 'error');
            return;
        }
        addToHistory('Regex to Automaton', regex, data.automaton);
        showResult('regex-result', 
            `<h3>Conversion Result:</h3><pre>${JSON.stringify(data.automaton, null, 2)}</pre>`, 
            'success'
        );
        renderGraph(data.automaton, 'regex-graph');
    } catch (error) {
        showResult('regex-result', `Error: ${error.message}`, 'error');
    }
});

document.getElementById('transform-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const automaton = document.getElementById('automaton-input').value;
    const operation = document.getElementById('operation-select').value;

    try {
        JSON.parse(automaton);
    } catch (error) {
        showResult('transform-result', 'Invalid JSON format for automaton.', 'error');
        return;
    }

    showResult('transform-result', '<div class="loading"></div> Processing...', 'info');

    try {
        const response = await fetch('/api/automaton/transform', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton: JSON.parse(automaton), operation })
        });
        const data = await response.json();
        if (data.error) {
            showResult('transform-result', data.error, 'error');
            return;
        }
        addToHistory(operation, automaton, data.automaton);
        showResult('transform-result', 
            `<h3>${operation} Result:</h3><pre>${JSON.stringify(data.automaton, null, 2)}</pre>`, 
            'success'
        );
        renderGraph(data.automaton, 'transform-graph');
    } catch (error) {
        showResult('transform-result', `Error: ${error.message}`, 'error');
    }
});

document.getElementById('binary-ops-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const auto1 = document.getElementById('auto1-input').value;
    const auto2 = document.getElementById('auto2-input').value;
    const operation = document.getElementById('binary-op-select').value;

    try {
        JSON.parse(auto1);
        JSON.parse(auto2);
    } catch (error) {
        showResult('operations-result', 'Invalid JSON format for one or both automata.', 'error');
        return;
    }

    showResult('operations-result', '<div class="loading"></div> Processing...', 'info');

    try {
        const response = await fetch(`/api/automaton/${operation}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton1: JSON.parse(auto1), automaton2: JSON.parse(auto2) })
        });
        const data = await response.json();
        if (data.error) {
            showResult('operations-result', data.error, 'error');
            return;
        }
        addToHistory(operation, {auto1, auto2}, data.automaton);
        showResult('operations-result', 
            `<h3>${operation} Result:</h3><pre>${JSON.stringify(data.automaton, null, 2)}</pre>`, 
            'success'
        );
        renderGraph(data.automaton, 'operations-graph');
    } catch (error) {
        showResult('operations-result', `Error: ${error.message}`, 'error');
    }
});

document.getElementById('test-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const automaton = document.getElementById('test-automaton-input').value;
    const word = document.getElementById('word-input').value;

    try {
        JSON.parse(automaton);
    } catch (error) {
        showResult('test-result', 'Invalid JSON format for automaton.', 'error');
        return;
    }

    showResult('test-result', '<div class="loading"></div> Testing...', 'info');

    try {
        const response = await fetch('/api/automaton/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton: JSON.parse(automaton), word })
        });
        const data = await response.json();
        if (data.error) {
            showResult('test-result', data.error, 'error');
            return;
        }
        addToHistory('Word Test', {automaton, word}, {accepted: data.accepted, word});
        showResult('test-result', 
            `<h3>Test Result:</h3><p>Word "${word}" is <strong>${data.accepted ? 'ACCEPTED' : 'REJECTED'}</strong> by the automaton.</p>`, 
            data.accepted ? 'success' : 'error'
        );
        animateRecognition(JSON.parse(automaton), word, 'test-graph');
    } catch (error) {
        showResult('test-result', `Error: ${error.message}`, 'error');
    }
});

async function kleeneStar() {
    const automaton = document.getElementById('auto-unary-input').value;

    if (!automaton) {
        showResult('operations-result', 'Please enter an automaton.', 'error');
        return;
    }

    try {
        JSON.parse(automaton);
    } catch (error) {
        showResult('operations-result', 'Invalid JSON format for automaton.', 'error');
        return;
    }

    showResult('operations-result', '<div class="loading"></div> Applying Kleene Star...', 'info');

    try {
        const response = await fetch('/api/automaton/kleene', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton: JSON.parse(automaton) })
        });
        const data = await response.json();
        if (data.error) {
            showResult('operations-result', data.error, 'error');
            return;
        }
        addToHistory('Kleene Star', automaton, data.automaton);
        showResult('operations-result', 
            `<h3>Kleene Star Result:</h3><pre>${JSON.stringify(data.automaton, null, 2)}</pre>`, 
            'success'
        );
        renderGraph(data.automaton, 'operations-graph');
    } catch (error) {
        showResult('operations-result', `Error: ${error.message}`, 'error');
    }
}

async function compareAutomata() {
    const auto1 = document.getElementById('auto-unary-input').value;
    const auto2 = document.getElementById('auto2-input').value;

    if (!auto1 || !auto2) {
        showResult('operations-result', 'Please enter both automata.', 'error');
        return;
    }

    try {
        JSON.parse(auto1);
        JSON.parse(auto2);
    } catch (error) {
        showResult('operations-result', 'Invalid JSON format for one or both automata.', 'error');
        return;
    }

    showResult('operations-result', '<div class="loading"></div> Comparing...', 'info');

    try {
        const response = await fetch('/api/automaton/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton1: JSON.parse(auto1), automaton2: JSON.parse(auto2) })
        });
        const data = await response.json();
        if (data.error) {
            showResult('operations-result', data.error, 'error');
            return;
        }
        addToHistory('Compare Automata', {auto1, auto2}, {equivalent: data.equivalent});
        showResult('operations-result', 
            `<h3>Comparison Result:</h3><p>Automata are <strong>${data.equivalent ? 'EQUIVALENT' : 'NOT EQUIVALENT'}</strong>.</p>`, 
            data.equivalent ? 'success' : 'error'
        );
    } catch (error) {
        showResult('operations-result', `Error: ${error.message}`, 'error');
    }
}

async function getHistory() {
    try {
        const response = await fetch('/api/automaton/history', {
            method: 'GET'
        });
        const data = await response.json();
        operationHistory = data.history.map((op, index) => ({
            timestamp: new Date().toLocaleString(),
            operation: op,
            input: 'N/A',
            output: 'N/A'
        }));
        displayHistory();
    } catch (error) {
        showModal(`Error fetching history: ${error.message}`, 'error');
    }
}

async function clearHistory() {
    try {
        const response = await fetch('/api/automaton/clear-history', {
            method: 'POST'
        });
        const data = await response.json();
        operationHistory = [];
        displayHistory();
        showModal(data.message, 'success');
    } catch (error) {
        showModal(`Error clearing history: ${error.message}`, 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    displayHistory();
});