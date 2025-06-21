
        // Global variables for operation history
        let operationHistory = [];

        // Tab switching functionality
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        // Utility functions
        function showResult(elementId, content, type = 'info') {
            const element = document.getElementById(elementId);
            element.innerHTML = content;
            element.className = `result ${type}`;
            element.style.display = 'block';
        }

        function addToHistory(operation, input, output) {
            const timestamp = new Date().toLocaleString();
            operationHistory.unshift({
                timestamp,
                operation,
                input: typeof input === 'object' ? JSON.stringify(input, null, 2) : input,
                output: typeof output === 'object' ? JSON.stringify(output, null, 2) : output
            });
            
            // Keep only last 10 operations
            if (operationHistory.length > 10) {
                operationHistory = operationHistory.slice(0, 10);
            }
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

        // Mock automaton operations (in a real implementation, these would call backend APIs)
        function mockAutomatonOperation(operation, input) {
            // Simulate processing time
            return new Promise(resolve => {
                setTimeout(() => {
                    const result = {
                        operation: operation,
                        input: input,
                        output: {
                            alphabet: ["a", "b"],
                            states: ["q0", "q1", "q2"],
                            startState: "q0",
                            finalStates: ["q2"],
                            transitions: {
                                "q0": {"a": "q1", "b": "q0"},
                                "q1": {"a": "q2", "b": "q0"},
                                "q2": {"a": "q2", "b": "q2"}
                            }
                        },
                        success: true,
                        message: `Successfully performed ${operation}`
                    };
                    resolve(result);
                }, 1000);
            });
        }

        // Regular expression validation and conversion
        function validateRegex() {
            const regex = document.getElementById('regex-input').value;
            if (!regex) {
                showResult('regex-result', 'Please enter a regular expression.', 'error');
                return;
            }

            try {
                // Basic regex validation
                new RegExp(regex);
                showResult('regex-result', 'Valid regular expression!', 'success');
            } catch (error) {
                showResult('regex-result', `Invalid regular expression: ${error.message}`, 'error');
            }
        }

        // Event listeners for forms
        document.getElementById('regex-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const regex = document.getElementById('regex-input').value;
            
            showResult('regex-result', '<div class="loading"></div> Converting...', 'info');
            
            const result = await mockAutomatonOperation('Regex Conversion', regex);
            addToHistory('Regex to Automaton', regex, result.output);
            
            showResult('regex-result', 
                `<h3>Conversion Result:</h3>
                <pre>${JSON.stringify(result.output, null, 2)}</pre>`, 
                'success'
            );
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
            
            const result = await mockAutomatonOperation(operation, automaton);
            addToHistory(operation, automaton, result.output);
            
            showResult('transform-result', 
                `<h3>${operation} Result:</h3>
                <pre>${JSON.stringify(result.output, null, 2)}</pre>`, 
                'success'
            );
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
            
            const result = await mockAutomatonOperation(operation, {auto1, auto2});
            addToHistory(operation, {auto1, auto2}, result.output);
            
            showResult('operations-result', 
                `<h3>${operation} Result:</h3>
                <pre>${JSON.stringify(result.output, null, 2)}</pre>`, 
                'success'
            );
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
            
            // Simulate word testing
            setTimeout(() => {
                const accepted = Math.random() > 0.5; // Random for demo
                addToHistory('Word Test', {automaton, word}, {accepted, word});
                
                showResult('test-result', 
                    `<h3>Test Result:</h3>
                    <p>Word "${word}" is <strong>${accepted ? 'ACCEPTED' : 'REJECTED'}</strong> by the automaton.</p>`, 
                    accepted ? 'success' : 'error'
                );
            }, 1000);
        });

        // Additional operation functions
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
            
            const result = await mockAutomatonOperation('Kleene Star', automaton);
            addToHistory('Kleene Star', automaton, result.output);
            
            showResult('operations-result', 
                `<h3>Kleene Star Result:</h3>
                <pre>${JSON.stringify(result.output, null, 2)}</pre>`, 
                'success'
            );
        }

        async function compareAutomata() {
            const automaton = document.getElementById('auto-unary-input').value;
            
            if (!automaton) {
                showResult('operations-result', 'Please enter an automaton to compare.', 'error');
                return;
            }
            
            // For demo purposes, we'll simulate a comparison
            showResult('operations-result', 
                `<h3>Comparison Result:</h3>
                <p>This feature would compare the automaton with another one. In a full implementation, this would show equivalence, subset relationships, etc.</p>`, 
                'info'
            );
        }

        function getHistory() {
            displayHistory();
        }

        function clearHistory() {
            operationHistory = [];
            document.getElementById('history-container').innerHTML = '<p>History cleared.</p>';
        }

        // Initialize the interface
        document.addEventListener('DOMContentLoaded', function() {
            displayHistory();
        });