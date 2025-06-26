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
    // Handle Regex Conversion 
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

            // Determine method based on which button was clicked
            const submitter = e.submitter;
            const method = submitter?.id === 'glushkov' ? 1 : 0;

            showResult('regex-result', '<div class="loading"></div> Converting...', 'info');

            const result = await makeAPICall('/api/regex/convert', {regex:regex, method: method }, 'regex-result');
            if (result) {
                addToHistory('Regex to Automaton', regex, result.automaton);
                showResult('regex-result', 
                    `<button type="button" class="btn" onclick="copyToClipboardById('regex-result-content')">
                    📋 Copy</button>
                    <h3>Conversion Result:</h3><pre id="regex-result-content">${JSON.stringify(result.automaton, null, 2)}</pre>`, 
                    'success'
                );
                renderGraph(result.automaton, 'regex-graph');
            }
            
            return false;
        });
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
                    `<button type="button" class="btn" onclick="copyToClipboardById('transform-result-content')">
                    📋 Copy</button>
                    <h3>${operation} Result:</h3><pre id="transform-result-content">${JSON.stringify(response.automaton, null, 2)}</pre>`, 
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
                    `<button type="button" class="btn" onclick="copyToClipboardById('operations-result-content')">
                    📋 Copy</button>
                    <h3>${operation} Result:</h3><pre id="operations-result-content">${JSON.stringify(response.automaton, null, 2)}</pre>`, 
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
                addToHistory('Test Word', automaton, response.accepted);
                showResult('test-result', 
                    `<h3>Test Result:</h3><pre>${JSON.stringify(response.accepted, null, 2)}</pre>`, 
                    'success'
                );
                renderGraph(JSON.parse(automaton), 'test-graph');
            }
            
            return false;
        });
    }

    // Handler for Add Equation Button (outside submit)
    const add_btn = document.getElementById("add-eqn");
    const rm_btn = document.getElementById("rm-eqn");
    const container = document.getElementById("equation-fields");
    const alphabet = document.getElementById("alphabet");

    if (add_btn && container && rm_btn) {
        add_btn.addEventListener("click", () => {
            const index = container.querySelectorAll("input").length + 1;
            const input = document.createElement("input");
            input.type = "text";
            input.id = `eqn-input-${index}`;
            input.placeholder = `e.g., X${index}=...`;
            input.required = false;
            container.appendChild(input);
        });

       rm_btn.addEventListener("click", () => {
        const inputs = container.querySelectorAll("input");
        if (inputs.length > 0) {  // Add this check
            const index = inputs.length;
            const last_input = document.getElementById(`eqn-input-${index}`);
            if (last_input) container.removeChild(last_input);
        }
    });
    }

    // Handler for Equation Form Submission
    const eqn_form = document.getElementById('eqn-form');
    if (eqn_form) {
        eqn_form.addEventListener('submit', async function(e) {
            e.preventDefault();
            e.stopPropagation();

            const automaton = document.getElementById('eqn-automaton-input').value.trim();

            if (!automaton) {
                showResult('eqn-result', 'Please enter an automaton before.', 'error');
                return false;
            }

            // Validate JSON
            try {
                JSON.parse(automaton);
            } catch (error) {
                showResult('eqn-result', 'Invalid JSON format for automaton.', 'error');
                return false;
            }

            showResult('eqn-result', '<div class="loading"></div> Calculating...', 'info');

            // Call API to convert automaton to regex
            const response = await makeAPICall('/api/automaton/a2regex', { automaton }, 'eqn-result');

            if (!response || !response.regex) {
                showResult('eqn-result', 'Failed to get regex from API.', 'error');
                return false;
            }

            const regex = response.regex;

            addToHistory('Automaton To Regex', { automaton }, { regex });
            showResult('eqn-result', `<h3>Regex Result:</h3><p>Regex "<strong>${regex}</strong>" is equivalent to the automaton.</p>`);
            animateRecognition(JSON.parse(automaton), regex, 't-graph');

            // Handle Equations
            if (!container) {
                showResult('eqn-result', 'Missing equation container.', 'error');
                return false;
            }

            if(!alphabet)
            {
                showResult('eqn-result', 'Missing Alphabet for equation', 'error');
                return false;     
            }

            try {
                const eqn_list = [];
                container.querySelectorAll("input").forEach(eqn => {
                    eqn_list.push(eqn.value.trim());
                });

                if (eqn_list.length === 0 || eqn_list.some(eq => eq === "")) {
                    showResult('eqn-result', 'Please fill all equations.', 'error');
                    return false;
                }

                const eqnResponse = await makeAPICall('/api/automaton/eqn2regex', {
                    regex,
                    equations: eqn_list,
                    alphabet: alphabet.value.trim()
                }, 'eqn-result');

                if (eqnResponse) {
                    addToHistory('Equation To Regex', { regex, equations: eqn_list });
                    showResult('eqn-result',
                        `<h3>Equation Solve Result:</h3><p><strong>${JSON.stringify(eqnResponse)}</strong></p>`);
                }

            } catch (error) {
                showResult('eqn-result', 'Invalid equation input format.', 'error');
            }

            return false;
        });
    }

}

let operationHistory = [];
let currentAnimationInterval = null; 

function showTab(tabName, clickedElement) { 
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Trouver et activer l'onglet cliqué
    if (clickedElement) {
        clickedElement.classList.add('active');
    } else {
        // Fallback : chercher l'onglet par son contenu
        tabs.forEach(tab => {
            if (tab.onclick && tab.onclick.toString().includes(tabName)) {
                tab.classList.add('active');
            }
        });
    }

    // Clear graphs when switching tabs
    ['regex', 'transform', 'operations', 'test', 'eqn'].forEach(tab => {
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

    if (operationHistory.length >= 10) {
        operationHistory = operationHistory.slice(0, 9);
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


function validateEquation(equation) {
    // Format attendu : X1=aX2+bX1 ou similaire
    const pattern = /^X\d+\s*=\s*[a-zA-Z0-9+\(\)X\s]+$/;
    return pattern.test(equation.trim());
}

// Fonction pour extraire les variables d'une équation
function extractVariables(equation) {
    const matches = equation.match(/X\d+/g);
    return matches ? [...new Set(matches)] : [];
}

// Fonction pour valider la cohérence des variables dans toutes les équations
function validateEquationSystem(equations) {
    const allVariables = new Set();
    const definedVariables = new Set();
    
    equations.forEach(eq => {
        const variables = extractVariables(eq);
        variables.forEach(v => allVariables.add(v));
        
        // Variable définie (côté gauche de =)
        const leftSide = eq.split('=')[0].trim();
        if (leftSide.match(/^X\d+$/)) {
            definedVariables.add(leftSide);
        }
    });
    
    // Vérifier que toutes les variables utilisées sont définies
    const undefinedVars = [...allVariables].filter(v => !definedVariables.has(v));
    
    return {
        valid: undefinedVars.length === 0,
        undefinedVariables: undefinedVars
    };
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
            `<button type="button" class="btn" onclick="copyToClipboardById('result1')">
                    📋 </button>
            <h3>Kleene Star Result:</h3><pre id="result1">${JSON.stringify(response.automaton, null, 2)}</pre>`, 
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


function copyToClipboardById(elementId) {
    const el = document.getElementById(elementId);

    if (!el) {
        alert("Element not found.");
        return;
    }

    const text = el.innerText || el.textContent;

    if (!text.trim()) {
        alert("Nothing to copy!");
        return;
    }

    navigator.clipboard.writeText(text)
        .then(() => alert("Copied to clipboard!"))
        .catch(err => {
            try {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert("Copied to clipboard!");
            } catch (fallbackErr) {
                alert("Failed to copy: " + err);
            }
        });
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

