document.addEventListener('DOMContentLoaded', function() {
    displayHistory();
    
    if (typeof cytoscape === 'undefined') {
        console.warn('Cytoscape library not loaded. Graph visualization will not work.');
    }
    
    const requiredElements = [
        'transform-form', 'binary-ops-form', 'test-form', 
        'automaton-input', 'operation-select', 'auto1-input', 
        'auto2-input', 'binary-op-select', 'test-automaton-input', 
        'word-input', 'auto-unary-input'
    ];
    
    requiredElements.forEach(id => {
        if (!document.getElementById(id)) {
            console.warn(`Required element with id '${id}' not found in DOM`);
        }
    });

    initializeFormListeners();
});

function initializeFormListeners() {
    // Regex Form Handler
    const regexForm = document.getElementById('regex-form');
    if (regexForm) {
        regexForm.addEventListener('submit', async function(e) {
            console.log('Regex form submitted');
            e.preventDefault();
            e.stopPropagation();
            
            const regex = document.getElementById('regex-input').value.trim();
            
            if (!regex) {
                showResult('regex-result', 'Please enter a regular expression.', 'error');
                return false;
            }

            showResult('regex-result', '<div class="loading"></div> Converting...', 'info');

            const result = await makeAPICall('/api/regex/convert', { regex }, 'regex-result');
            if (result) {
                addToHistory('Regex to Automaton', regex, result.automaton);
                showResult('regex-result', 
                    `<h3>Conversion Result:</h3><pre>${JSON.stringify(result.automaton, null, 2)}</pre>`, 
                    'success'
                );
                renderGraph(result.automaton, 'regex-graph');
            }
            
            return false;
        });
    } else {
        console.error('regex-form element not found!');
    }

    // Transform Form Handler
    const transformForm = document.getElementById('transform-form');
    if (transformForm) {
        transformForm.addEventListener('submit', async function(e) {
            console.log('Transform form submitted');
            e.preventDefault();
            e.stopPropagation();
            
            const automaton = document.getElementById('automaton-input').value.trim();
            const operation = document.getElementById('operation-select').value;

            if (!automaton) {
                showResult('transform-result', 'Please enter an automaton.', 'error');
                return false;
            }

            if (!operation) {
                showResult('transform-result', 'Please select an operation.', 'error');
                return false;
            }

            try {
                JSON.parse(automaton);
            } catch (error) {
                showResult('transform-result', 'Invalid JSON format for automaton.', 'error');
                return false;
            }

            showResult('transform-result', '<div class="loading"></div> Processing...', 'info');
            
            const response = await makeAPICall('/api/automaton/transform', {
                automaton: JSON.parse(automaton), 
                operation: operation
            }, 'transform-result');
            
            if (response) { 
                addToHistory(operation, automaton, response.automaton);
                showResult('transform-result', 
                    `<h3>${operation} Result:</h3><pre>${JSON.stringify(response.automaton, null, 2)}</pre>`, 
                    'success'
                );
                renderGraph(response.automaton, 'transform-graph');
            }
            
            return false;
        });
    }

    // Binary Operations Form Handler
    const binaryOpsForm = document.getElementById('binary-ops-form');
    if (binaryOpsForm) {
        binaryOpsForm.addEventListener('submit', async function(e) {
            console.log('Binary ops form submitted');
            e.preventDefault();
            e.stopPropagation();
            
            const auto1 = document.getElementById('auto1-input').value.trim();
            const auto2 = document.getElementById('auto2-input').value.trim();
            const operation = document.getElementById('binary-op-select').value;

            if (!auto1 || !auto2) {
                showResult('operations-result', 'Please enter both automata.', 'error');
                return false;
            }

            if (!operation) {
                showResult('operations-result', 'Please select an operation.', 'error');
                return false;
            }

            try {
                JSON.parse(auto1);
                JSON.parse(auto2);
            } catch (error) {
                showResult('operations-result', 'Invalid JSON format for one or both automata.', 'error');
                return false;
            }

            showResult('operations-result', '<div class="loading"></div> Processing...', 'info');

            const response = await makeAPICall(`/api/automaton/${operation}`, {
                automaton1: JSON.parse(auto1), 
                automaton2: JSON.parse(auto2)
            }, 'operations-result');
            
            if (response) {
                addToHistory(operation, {auto1, auto2}, response.automaton);
                showResult('operations-result', 
                    `<h3>${operation} Result:</h3><pre>${JSON.stringify(response.automaton, null, 2)}</pre>`, 
                    'success'
                );
                renderGraph(response.automaton, 'operations-graph');
            }
            
            return false;
        });
    }

    // Test Form Handler
    const testForm = document.getElementById('test-form');
    if (testForm) {
        testForm.addEventListener('submit', async function(e) {
            console.log('Test form submitted');
            e.preventDefault();
            e.stopPropagation();
            
            const automaton = document.getElementById('test-automaton-input').value.trim();
            const word = document.getElementById('word-input').value.trim();

            if (!automaton) {
                showResult('test-result', 'Please enter an automaton.', 'error');
                return false;
            }

            if (!word) {
                showResult('test-result', 'Please enter a word to test.', 'error');
                return false;
            }

            try {
                JSON.parse(automaton);
            } catch (error) {
                showResult('test-result', 'Invalid JSON format for automaton.', 'error');
                return false;
            }

            showResult('test-result', '<div class="loading"></div> Testing...', 'info');

            const response = await makeAPICall('/api/automaton/test', {
                automaton: JSON.parse(automaton), 
                word: word
            }, 'test-result');
            
            if (response) {
                addToHistory('Word Test', {automaton, word}, {accepted: response.accepted, word});
                showResult('test-result', 
                    `<h3>Test Result:</h3><p>Word "${word}" is <strong>${response.accepted ? 'ACCEPTED' : 'REJECTED'}</strong> by the automaton.</p>`, 
                    response.accepted ? 'success' : 'error'
                );
                animateRecognition(JSON.parse(automaton), word, 'test-graph');
            }
            
            return false;
        });
    }
}

let operationHistory = [];
let currentAnimationInterval = null; 


function showTab(tabName, event) { 
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    document.getElementById(tabName + '-tab').classList.add('active');
    if (event && event.target) { 
        event.target.classList.add('active');
    }

    // Clear graphs when switching tabs
    ['regex', 'transform', 'operations', 'test'].forEach(tab => {
        const container = document.getElementById(`${tab}-graph`);
        if (container) { 
            container.innerHTML = '';
        }
    });
}

function showResult(elementId, content, type = 'info') {
    const element = document.getElementById(elementId);
    if (!element) { 
        console.error(`Element with id '${elementId}' not found`);
        return;
    }
    element.innerHTML = content;
    element.className = `result ${type}`;
    element.style.display = 'block';
}


function showModal(message, type = 'info') {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    if (!modal || !modalMessage) { 
        console.error('Modal elements not found');
        return;
    }
    modalMessage.textContent = message;
    modal.classList.add('active');
    modal.className = `modal ${type}`;
}

function hideModal() {
    const modal = document.getElementById('modal');
    if (modal) { 
        modal.classList.remove('active');
    }
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
    if (!container) { 
        console.error('History container not found');
        return;
    }
    
    if (operationHistory.length === 0) {
        container.innerHTML = '<p>No operations performed yet.</p>';
        return;
    }

    let html = '';
    operationHistory.forEach((item, index) => {
        const truncatedInput = item.input.substring(0, 100);
        html += `
            <div class="history-item">
                <strong>${item.operation}</strong> - ${item.timestamp}
                <br><small>Input: ${truncatedInput}${item.input.length > 100 ? '...' : ''}</small>
            </div>
        `;
    });
    container.innerHTML = html;
}


function renderGraph(automaton, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container '${containerId}' not found`);
        return null;
    }

    if (typeof cytoscape === 'undefined') {
        console.error('Cytoscape library not loaded');
        container.innerHTML = '<p>Graph visualization not available. Please load Cytoscape library.</p>';
        return null;
    }

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
    if (currentAnimationInterval) {
        clearInterval(currentAnimationInterval);
        currentAnimationInterval = null;
    }

    const cy = renderGraph(automaton, containerId);
    if (!cy) return; 

    try {
        const response = await fetch('/api/automaton/trace', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ automaton, word })
        });

        if (!response.ok) { 
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
            showModal(data.error, 'error');
            return;
        }

        let i = 0;
        cy.nodes().removeClass('highlight');
        cy.edges().removeClass('highlight');
        
        currentAnimationInterval = setInterval(() => {
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
                clearInterval(currentAnimationInterval);
                currentAnimationInterval = null;
                showModal(`Word "${word}" is ${data.accepted ? 'ACCEPTED' : 'REJECTED'}.`, data.accepted ? 'success' : 'error');
            }
        }, 500);
    } catch (error) {
        console.error('Animation error:', error);
        showModal(`Error during animation: ${error.message}`, 'error');
    }
}


function validateJSON(jsonString, fieldName) {
    try {
        return JSON.parse(jsonString);
    } catch (error) {
        const errorMsg = `Invalid JSON format for ${fieldName}: ${error.message}`;
        console.error(errorMsg);
        throw new Error(errorMsg);
    }
}


async function validateRegex() {
    const regex = document.getElementById('regex-input').value;
    if (!regex) {
        showResult('regex-result', 'Please enter a regular expression.', 'error');
        return;
    }

    const result = await makeAPICall('/api/regex/validate', { regex }, 'regex-result');
    if (result) {
        showResult('regex-result', result.message, result.valid ? 'success' : 'error');
    }
}


async function makeAPICall(url, data, resultElementId, successMessage) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.error) {
            showResult(resultElementId, result.error, 'error');
            return null;
        }
        
        return result;
    } catch (error) {
        const errorMsg = `Network error: ${error.message}. Please check if the server is running.`;
        showResult(resultElementId, errorMsg, 'error');
        console.error('API call failed:', error);
        return null;
    }
}

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

    const response = await makeAPICall('/api/automaton/kleene', {
        automaton: JSON.parse(automaton)
    }, 'operations-result');
    
    if (response) {
        addToHistory('Kleene Star', automaton, response.automaton);
        showResult('operations-result', 
            `<h3>Kleene Star Result:</h3><pre>${JSON.stringify(response.automaton, null, 2)}</pre>`, 
            'success'
        );
        renderGraph(response.automaton, 'operations-graph');
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

    const response = await makeAPICall('/api/automaton/compare', {
        automaton1: JSON.parse(auto1), 
        automaton2: JSON.parse(auto2)
    }, 'operations-result');
    
    if (response) {
        addToHistory('Compare Automata', {auto1, auto2}, {equivalent: response.equivalent});
        showResult('operations-result', 
            `<h3>Comparison Result:</h3><p>Automata are <strong>${response.equivalent ? 'EQUIVALENT' : 'NOT EQUIVALENT'}</strong>.</p>`, 
            response.equivalent ? 'success' : 'error'
        );
    }
}

async function getHistory() {
    try {
        const response = await fetch('/api/automaton/history', {
            method: 'GET'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            showModal(data.error, 'error');
            return;
        }
        
        if (Array.isArray(data.history)) {
            operationHistory = data.history.map((op, index) => ({
                timestamp: new Date().toLocaleString(),
                operation: op,
                input: 'N/A',
                output: 'N/A'
            }));
        } else {
            operationHistory = [];
        }
        
        displayHistory();
    } catch (error) {
        console.error('Error fetching history:', error);
        showModal(`Error fetching history: ${error.message}`, 'error');
    }
}

async function clearHistory() {
    try {
        const response = await fetch('/api/automaton/clear-history', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            showModal(data.error, 'error');
            return;
        }
        
        operationHistory = [];
        displayHistory();
        showModal(data.message || 'History cleared successfully', 'success');
    } catch (error) {
        console.error('Error clearing history:', error);
        showModal(`Error clearing history: ${error.message}`, 'error');
    }
}

