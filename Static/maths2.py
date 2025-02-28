from flask import Flask, request, jsonify, render_template_string
from sympy import symbols, Eq, solve, diff, integrate, pi, exp, sin, cos, tan, log, sqrt
from sympy.solvers.inequalities import solve_univariate_inequality
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
import re

app = Flask(__name__)

# Define symbols
x, y, z, t, a, b, c, n = symbols('x y z t a b c n')

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Math Problem Solver</title>
    <style>
        /* General Styles */
        body {
            font-family: 'Roboto', Arial, sans-serif;
            background: linear-gradient(to bottom right, #74ebd5, #9face6);
            margin: 0;
            padding: 0;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        /* Container Styles */
        .container {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            padding: 30px;
            margin: 20px;
            width: 90%;
        }

        /* Header Styles */
        h1 {
            font-size: 2.5rem;
            color: #007BFF;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        h2 {
            font-size: 1.8rem;
            color: #0056b3;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        /* Input and Button Styles */
        textarea,
        select,
        button {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 6px;
            transition: all 0.3s ease-in-out;
        }

        textarea:focus,
        select:focus,
        button:focus {
            outline: none;
            border-color: #007BFF;
            box-shadow: 0 0 8px rgba(0, 123, 255, 0.3);
        }

        button {
            background-color: #007BFF;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }

        button:hover {
            background-color: #0056b3;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        textarea {
            resize: none;
            height: 120px;
        }

        /* Example Box */
        .example-box {
            background-color: #f0f8ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            font-size: 14px;
        }

        .example-box h3 {
            margin-top: 0;
            color: #0056b3;
        }

        /* Output Styles */
        #output {
            margin-top: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .step {
            margin: 15px 0;
            padding: 10px 15px;
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            color: #0056b3;
            font-size: 16px;
            line-height: 1.5;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .step strong {
            color: #007BFF;
        }

        .error {
            color: #d9534f;
            font-weight: bold;
            background: #f2dede;
            border: 1px solid #ebccd1;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }

        .final-solution {
            background: #dff0d8;
            border: 1px solid #d6e9c6;
            color: #3c763d;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
        }

        /* History Section */
        #history {
            margin-top: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            display: none;
        }

        .history-item {
            padding: 10px;
            margin: 10px 0;
            background-color: #fff;
            border: 1px solid #eee;
            border-radius: 4px;
            cursor: pointer;
        }

        .history-item:hover {
            background-color: #f0f8ff;
        }

        /* Tabs */
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }

        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background-color: #f1f1f1;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }

        .tab.active {
            background-color: #007BFF;
            color: white;
            border-color: #007BFF;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* Graph Canvas */
        #graph-container {
            width: 100%;
            height: 300px;
            margin-top: 20px;
            border: 1px solid #ddd;
            border-radius: 6px;
            overflow: hidden;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }

            textarea,
            select,
            button {
                font-size: 14px;
            }
        }

        /* Loading Spinner */
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #007BFF;
            animation: spin 1s linear infinite;
            margin: 20px auto;
            display: none;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Advanced Math Problem Solver</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('solver')">Problem Solver</div>
            <div class="tab" onclick="switchTab('history')">Solution History</div>
            <div class="tab" onclick="switchTab('about')">About</div>
        </div>
        
        <div id="solver-tab" class="tab-content active">
            <label for="type">Select Problem Type:</label>
            <select id="type" onchange="updateExampleAndOptions()">
                <option value="linear">Linear Equation</option>
                <option value="quadratic">Quadratic Equation</option>
                <option value="system">System of Equations</option>
                <option value="inequality">Inequality</option>
                <option value="polynomial">Polynomial Equation</option>
                <option value="geometry">Geometry</option>
                <option value="differentiation">Differentiation</option>
                <option value="integration">Integration</option>
                <option value="trigonometry">Trigonometric Equations</option>
                <option value="limit">Limits</option>
                <option value="statistics">Statistics</option>
            </select>
            
            <div id="sub-options" style="display: none;">
                <label for="sub-type">Specific Type:</label>
                <select id="sub-type" onchange="updateExample()"></select>
            </div>

            <div class="example-box">
                <h3>Example:</h3>
                <p id="example-text">2*x + 3 = 7</p>
            </div>

            <label for="expression">Enter Expression:</label>
            <textarea id="expression" rows="4" placeholder="Enter your mathematical expression here..."></textarea>

            <button onclick="solveProblem()">Solve</button>
            
            <div class="spinner" id="loading-spinner"></div>
            
            <div id="graph-container" style="display: none;"></div>
            <div id="output"></div>
        </div>
        
        <div id="history-tab" class="tab-content">
            <h2>Solution History</h2>
            <p>Click on a previous problem to view its solution again.</p>
            <div id="history-list"></div>
            <button onclick="clearHistory()" style="margin-top: 20px; background-color: #dc3545;">Clear History</button>
        </div>
        
        <div id="about-tab" class="tab-content">
            <h2>About This Math Solver</h2>
            <p>This advanced mathematics problem solver is designed to help students and professionals solve a wide variety of mathematical problems. The solver provides step-by-step solutions to enhance understanding of the solution process.</p>
            
            <h3>Features:</h3>
            <ul>
                <li>Solves various types of mathematical problems</li>
                <li>Shows detailed solution steps</li>
                <li>Provides visual representations where applicable</li>
                <li>Saves solution history for future reference</li>
            </ul>
            
            <h3>Supported Problem Types:</h3>
            <ul>
                <li>Algebraic equations (linear, quadratic, polynomial, systems)</li>
                <li>Calculus (differentiation, integration, limits)</li>
                <li>Geometry (area, volume, perimeter calculations)</li>
                <li>Trigonometry</li>
                <li>Statistics (mean, median, standard deviation, etc.)</li>
            </ul>
            
            <p>This tool uses SymPy, a powerful symbolic mathematics library, to perform calculations and provide accurate solutions.</p>
        </div>
    </div>

    <script>
        // Initialize variables for storing history
        let solutionHistory = JSON.parse(localStorage.getItem('mathSolverHistory')) || [];
        
        // Initialize examples for different problem types
        const examples = {
            linear: "2*x + 3 = 7",
            quadratic: "x**2 + 5*x + 6 = 0",
            system: "x + y = 10; 2*x - y = 5",
            inequality: "x**2 - 4 < 0",
            polynomial: "x**3 - 6*x**2 + 11*x - 6 = 0",
            geometry: {
                "circle_area": "radius = 5",
                "circle_circumference": "radius = 5",
                "triangle_area": "base = 5; height = 8",
                "rectangle_area": "length = 5; width = 10",
                "sphere_volume": "radius = 3"
            },
            differentiation: "x**2 + 3*x + 2",
            integration: "2*x + 3",
            trigonometry: "sin(x) = 0.5",
            limit: "limit(x, 0, (sin(x)/x))",
            statistics: "data = [10, 20, 30, 40, 50]"
        };
        
        // Sub-options for problem types that need them
        const subOptions = {
            geometry: [
                { value: "circle_area", label: "Circle Area" },
                { value: "circle_circumference", label: "Circle Circumference" },
                { value: "triangle_area", label: "Triangle Area" },
                { value: "rectangle_area", label: "Rectangle Area" },
                { value: "sphere_volume", label: "Sphere Volume" }
            ],
            statistics: [
                { value: "mean", label: "Mean (Average)" },
                { value: "median", label: "Median" },
                { value: "mode", label: "Mode" },
                { value: "standard_deviation", label: "Standard Deviation" },
                { value: "variance", label: "Variance" },
                { value: "range", label: "Range" }
            ]
        };
        
        // Function to update example based on the selected problem type
        function updateExampleAndOptions() {
            const problemType = document.getElementById('type').value;
            const subOptionsContainer = document.getElementById('sub-options');
            const subTypeSelect = document.getElementById('sub-type');
            
            // Clear previous sub-options
            subTypeSelect.innerHTML = '';
            
            // Check if this problem type has sub-options
            if (subOptions[problemType]) {
                // Populate sub-options
                subOptions[problemType].forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option.value;
                    optionElement.textContent = option.label;
                    subTypeSelect.appendChild(optionElement);
                });
                
                // Show sub-options container
                subOptionsContainer.style.display = 'block';
            } else {
                // Hide sub-options container if not needed
                subOptionsContainer.style.display = 'none';
            }
            
            updateExample();
        }
        
        // Function to update example based on current selections
        function updateExample() {
            const problemType = document.getElementById('type').value;
            const exampleText = document.getElementById('example-text');
            
            if (typeof examples[problemType] === 'object') {
                // If there are sub-types, get the selected sub-type
                const subType = document.getElementById('sub-type').value;
                exampleText.textContent = examples[problemType][subType];
            } else {
                exampleText.textContent = examples[problemType];
            }
        }
        
        // Function to solve the problem
        async function solveProblem() {
            const type = document.getElementById('type').value;
            const expression = document.getElementById('expression').value.trim();
            const output = document.getElementById('output');
            const spinner = document.getElementById('loading-spinner');
            const graphContainer = document.getElementById('graph-container');
            
            // Get sub-type if applicable
            let subType = "";
            if (document.getElementById('sub-options').style.display !== 'none') {
                subType = document.getElementById('sub-type').value;
            }

            output.innerHTML = ""; // Clear previous output
            graphContainer.style.display = 'none'; // Hide graph container

            if (!expression) {
                output.innerHTML = `<div class="error">Please enter a valid expression.</div>`;
                return;
            }

            try {
                // Show loading spinner
                spinner.style.display = 'block';
                
                const response = await fetch('/solve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, expression, subType })
                });

                const data = await response.json();
                
                // Hide spinner
                spinner.style.display = 'none';

                if (data.error) {
                    output.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    // Build steps HTML
                    const stepsHTML = data.steps.map(
                        (step, index) => `<div class="step"><strong>Step ${index + 1}:</strong> ${step}</div>`
                    ).join("");
                    
                    // Build output HTML
                    let outputHTML = `<h3>Solution Steps:</h3>${stepsHTML}`;
                    
                    // Add final solution
                    outputHTML += `<div class="final-solution">Solution: ${data.solution}</div>`;
                    
                    // Set the output HTML
                    output.innerHTML = outputHTML;
                    
                    // Show graph if available
                    if (data.graph) {
                        graphContainer.style.display = 'block';
                        // Here you would render the graph using a library like Chart.js or plot.ly
                        // For now, just displaying a placeholder
                        graphContainer.innerHTML = `<div style="text-align: center; padding: 20px;">Graph would be displayed here</div>`;
                    }
                    
                    // Save to history
                    const historyItem = {
                        type,
                        subType,
                        expression,
                        solution: data.solution,
                        steps: data.steps,
                        timestamp: new Date().toISOString()
                    };
                    
                    solutionHistory.unshift(historyItem);
                    if (solutionHistory.length > 10) {
                        solutionHistory.pop(); // Keep only the 10 most recent items
                    }
                    localStorage.setItem('mathSolverHistory', JSON.stringify(solutionHistory));
                    
                    // Update history list
                    updateHistoryList();
                }
            } catch (err) {
                spinner.style.display = 'none';
                output.innerHTML = `<div class="error">An error occurred: ${err.message}</div>`;
            }
        }
        
        // Function to update the history list
        function updateHistoryList() {
            const historyList = document.getElementById('history-list');
            historyList.innerHTML = '';
            
            if (solutionHistory.length === 0) {
                historyList.innerHTML = '<p>No history yet. Solve some problems to see them here.</p>';
                return;
            }
            
            solutionHistory.forEach((item, index) => {
                const date = new Date(item.timestamp).toLocaleString();
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <strong>${item.type}${item.subType ? `: ${item.subType}` : ''}</strong>
                    <p>${item.expression}</p>
                    <small>${date}</small>
                `;
                historyItem.onclick = () => loadHistoryItem(index);
                historyList.appendChild(historyItem);
            });
        }
        
        // Function to load a history item
        function loadHistoryItem(index) {
            const item = solutionHistory[index];
            
            // Set the problem type
            document.getElementById('type').value = item.type;
            
            // Update sub-options if needed
            updateExampleAndOptions();
            
            // Set sub-type if applicable
            if (item.subType && document.getElementById('sub-options').style.display !== 'none') {
                document.getElementById('sub-type').value = item.subType;
            }
            
            // Set the expression
            document.getElementById('expression').value = item.expression;
            
            // Switch to solver tab
            switchTab('solver');
            
            // Display the solution
            const output = document.getElementById('output');
            
            // Build steps HTML
            const stepsHTML = item.steps.map(
                (step, index) => `<div class="step"><strong>Step ${index + 1}:</strong> ${step}</div>`
            ).join("");
            
            // Build output HTML
            let outputHTML = `<h3>Solution Steps:</h3>${stepsHTML}`;
            
            // Add final solution
            outputHTML += `<div class="final-solution">Solution: ${item.solution}</div>`;
            
            // Set the output HTML
            output.innerHTML = outputHTML;
        }
        
        // Function to clear history
        function clearHistory() {
            if (confirm('Are you sure you want to clear your solution history?')) {
                solutionHistory = [];
                localStorage.removeItem('mathSolverHistory');
                updateHistoryList();
            }
        }
        
        // Function to switch tabs
        function switchTab(tabName) {
            // Hide all tab contents
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Deactivate all tabs
            const tabs = document.getElementsByClassName('tab');
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Activate the selected tab
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Find and activate the corresponding tab button
            const tabButtons = document.getElementsByClassName('tab');
            for (let i = 0; i < tabButtons.length; i++) {
                if (tabButtons[i].textContent.toLowerCase().includes(tabName)) {
                    tabButtons[i].classList.add('active');
                }
            }
            
            // Update history list if switching to history tab
            if (tabName === 'history') {
                updateHistoryList();
            }
        }
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            updateExampleAndOptions();
            updateHistoryList();
        });
    </script>
</body>
</html>
"""

def safe_eval(expr_str, local_dict=None):
    """Safely evaluate a mathematical expression."""
    try:
        # Try to parse the expression with sympy's parser
        return parse_expr(expr_str)
    except Exception as e:
        # If sympy parsing fails, try direct evaluation with limited locals
        local_dict = local_dict or {"x": x, "y": y, "z": z, "t": t, "a": a, "b": b, "c": c, "n": n,
                               "sin": sin, "cos": cos, "tan": tan, "exp": exp, "log": log, "sqrt": sqrt, "pi": pi}
        return eval(expr_str, {"__builtins__": {}}, local_dict)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/solve', methods=['POST'])
def solve_problem():
    try:
        data = request.json
        problem_type = data.get('type')
        expression = data.get('expression')
        sub_type = data.get('subType', '')

        steps = []
        solution = None
        graph = False

        if problem_type == "linear":
            lhs, rhs = expression.split('=')
            lhs_expr = safe_eval(lhs.strip())
            rhs_expr = safe_eval(rhs.strip())
            eq = Eq(lhs_expr, rhs_expr)
            
            steps.append(f"Formulate the equation: {lhs} = {rhs}")
            steps.append(f"Move all terms to the left side: {lhs} - ({rhs}) = 0")
            simplified = lhs_expr - rhs_expr
            steps.append(f"Simplified equation: {simplified} = 0")
            
            # Check which variable to solve for
            var_to_solve = None
            for var in [x, y, z]:
                if var in simplified.free_symbols:
                    var_to_solve = var
                    break
            
            if var_to_solve:
                steps.append(f"Solve for {var_to_solve}")
                solution = solve(eq, var_to_solve)
                if solution:
                    steps.append(f"Solution: {var_to_solve} = {solution[0]}")
                    solution = f"{var_to_solve} = {solution[0]}"
                else:
                    steps.append("No solution found")
                    solution = "No solution"
            else:
                steps.append("No variable found to solve for")
                solution = "No variable found"

        elif problem_type == "quadratic":
            lhs, rhs = expression.split('=')
            lhs_expr = safe_eval(lhs.strip())
            rhs_expr = safe_eval(rhs.strip())
            eq = Eq(lhs_expr, rhs_expr)
            
            steps.append(f"Write the equation: {lhs} = {rhs}")
            steps.append(f"Move all terms to the left side: {lhs} - ({rhs}) = 0")
            
            # Move everything to the left side
            expr = lhs_expr - rhs_expr
            steps.append(f"Standard form: {expr} = 0")
            
            # Try to identify the variable
            var_to_solve = None
            for var in [x, y, z]:
                if var in expr.free_symbols:
                    var_to_solve = var
                    break
                    
            if not var_to_solve:
                return jsonify({"error": "No variable found in equation"}), 400
                
            steps.append(f"Identify this as a quadratic equation in {var_to_solve}")
            steps.append("Use the quadratic formula: x = [-b ± √(b² - 4ac)] / 2a")
            
            solutions = solve(eq, var_to_solve)
            
            if len(solutions) == 2:
                steps.append(f"Calculate the discriminant and find two roots")
                solution = f"{var_to_solve} = {solutions[0]} or {var_to_solve} = {solutions[1]}"
            elif len(solutions) == 1:
                steps.append(f"The discriminant is zero, giving a repeated root")
                solution = f"{var_to_solve} = {solutions[0]}"
            else:
                steps.append(f"No real solutions found")
                solution = "No real solutions"
                
            graph = True  # Indicate that we could display a graph

        elif problem_type == "system":
            equations = expression.split(';')
            system_eqs = []
            
            steps.append("Write the system of equations:")
            
            # Parse each equation and convert to SymPy equation objects
            for i, eq_str in enumerate(equations):
                if '=' not in eq_str:
                    return jsonify({"error": f"Equation {i+1} does not contain an equals sign"}), 400
                    
                lhs, rhs = eq_str.split('=')
                lhs_expr = safe_eval(lhs.strip())
                rhs_expr = safe_eval(rhs.strip())
                eq = Eq(lhs_expr, rhs_expr)
                system_eqs.append(eq)
                steps.append(f"Equation {i+1}: {lhs} = {rhs}")
            
            # Collect variables in the system
            variables = set()
            for eq in system_eqs:
                variables.update(eq.free_symbols)
            
            variables = list(variables)
            
            if len(variables) != len(system_eqs):
                steps.append(f"Note: The system has {len(variables)} variables and {len(system_eqs)} equations.")
            
            steps.append("Solving the system using substitution method.")
            
            try:
                solution_dict = solve(system_eqs, variables)
                
                if solution_dict:
                    solution_parts = []
                    for var, val in solution_dict.items():
                        solution_parts.append(f"{var} = {val}")
                    solution = ", ".join(solution_parts)
                    steps.append("Found solution: " + solution)
                else:
                    steps.append("No solution found for the system.")
                    solution = "No solution"
            except Exception as e:
                steps.append(f"Error solving system: {str(e)}")
                solution = "Could not solve system"

        elif problem_type == "inequality":
            try:
                # Try to parse directly as an inequality
                ineq_expr = eval(expression, {"__builtins__": {}}, 
                                {"x": x, "y": y, "z": z, "<": lambda a, b: a < b, 
                                 ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, 
                                 ">=": lambda a, b: a >= b})
                
                steps.append(f"Inequality: {expression}")
                
                # Find the variable
                variables = ineq_expr.free_symbols
                if not variables:
                    return jsonify({"error": "No variable found in inequality"}), 400
                
                var = list(variables)[0]
                steps.append(f"Solve for {var}")
                
                solution = solve_univariate_inequality(ineq_expr, var)
                steps.append(f"Solution: {solution}")
                
            except Exception:
                # If direct parsing fails, try to split by inequality operators
                for op in ['<=', '>=', '<', '>']:
                    if op in expression:
                        parts = expression.split(op)
                        if len(parts) == 2:
                            lhs = safe_eval(parts[0].strip())
                            rhs = safe_eval(parts[1].strip())
                            
                            steps.append(f"Inequality: {parts[0]} {op} {parts[1]}")
                            
                            # Find the variable
                            variables = set()
                            variables.update(lhs.free_symbols)
                            variables.update(rhs.free_symbols)
                            
                            if not variables:
                                return jsonify({"error": "No variable found in inequality"}), 400
                            
                            var = list(variables)[0]
                            steps.append(f"Solve for {var}")
                            
                            # Create the inequality expression
                            if op == '<':
                                ineq_expr = lhs < rhs
                            elif op == '>':
                                ineq_expr = lhs > rhs
                            elif op == '<=':
                                ineq_expr = lhs <= rhs
                            elif op == '>=':
                                ineq_expr = lhs >= rhs
                            
                            solution = solve_univariate_inequality(ineq_expr, var)
                            steps.append(f"Solution: {solution}")
                            break
                else:
                    return jsonify({"error": "Invalid inequality format"}), 400

        elif problem_type == "polynomial":
            if '=' not in expression:
                return jsonify({"error": "Equation must contain an equals sign"}), 400
                
            lhs, rhs = expression.split('=')
            lhs_expr = safe_eval(lhs.strip())
            rhs_expr = safe_eval(rhs.strip())
            eq = Eq(lhs_expr, rhs_expr)
            
            steps.append(f"Write the polynomial equation: {lhs} = {rhs}")
            steps.append(f"Move all terms to the left side: {lhs} - ({rhs}) = 0")
            
            # Move everything to the left side
            expr = lhs_expr - rhs_expr
            steps.append(f"Standard form: {expr} = 0")
            
            # Try to identify the variable
            var_to_solve = None
            for var in [x, y, z]:
                if var in expr.free_symbols:
                    var_to_solve = var
                    break
                    
            if not var_to_solve:
                return jsonify({"error": "No variable found in equation"}), 400
                
            steps.append(f"Find the roots of the polynomial in {var_to_solve}")
            
            solutions = solve(eq, var_to_solve)
            
            if solutions:
                solution_strs = [f"{var_to_solve} = {sol}" for sol in solutions]
                steps.append(f"Found {len(solutions)} solution(s)")
                solution = " or ".join(solution_strs)
            else:
                steps.append(f"No real solutions found")
                solution = "No real solutions"
                
            graph = True  # Indicate that we could display a graph

        elif problem_type == "geometry":
            steps.append(f"Geometry problem type: {sub_type}")
            
            try:
                # Parse the expression to extract values
                params = {}
                for part in expression.split(';'):
                    if '=' in part:
                        key, value = part.split('=')
                        params[key.strip()] = float(value.strip())
                
                if sub_type == "circle_area":
                    if 'radius' in params:
                        r = params['radius']
                        steps.append(f"Circle with radius = {r}")
                        steps.append(f"Area of a circle: A = π × r²")
                        area = pi * r**2
                        steps.append(f"A = π × {r}² = {area}")
                        solution = f"Area = {area}"
                        
                elif sub_type == "circle_circumference":
                    if 'radius' in params:
                        r = params['radius']
                        steps.append(f"Circle with radius = {r}")
                        steps.append(f"Circumference of a circle: C = 2π × r")
                        circumference = 2 * pi * r
                        steps.append(f"C = 2π × {r} = {circumference}")
                        solution = f"Circumference = {circumference}"
                        
                elif sub_type == "triangle_area":
                    if 'base' in params and 'height' in params:
                        b = params['base']
                        h = params['height']
                        steps.append(f"Triangle with base = {b} and height = {h}")
                        steps.append(f"Area of a triangle: A = (b × h) / 2")
                        area = (b * h) / 2
                        steps.append(f"A = ({b} × {h}) / 2 = {area}")
                        solution = f"Area = {area}"
                        
                elif sub_type == "rectangle_area":
                    if 'length' in params and 'width' in params:
                        l = params['length']
                        w = params['width']
                        steps.append(f"Rectangle with length = {l} and width = {w}")
                        steps.append(f"Area of a rectangle: A = l × w")
                        area = l * w
                        steps.append(f"A = {l} × {w} = {area}")
                        solution = f"Area = {area}"
                        
                elif sub_type == "sphere_volume":
                    if 'radius' in params:
                        r = params['radius']
                        steps.append(f"Sphere with radius = {r}")
                        steps.append(f"Volume of a sphere: V = (4/3) × π × r³")
                        volume = (4/3) * pi * r**3
                        steps.append(f"V = (4/3) × π × {r}³ = {volume}")
                        solution = f"Volume = {volume}"
                        
                else:
                    return jsonify({"error": "Unsupported geometry sub-type"}), 400
                    
            except Exception as e:
                return jsonify({"error": f"Error in geometry calculation: {str(e)}"}), 400

        elif problem_type == "differentiation":
            steps.append(f"Expression to differentiate: {expression}")
            steps.append("Find the derivative with respect to x")
            
            try:
                expr = safe_eval(expression)
                derivative = diff(expr, x)
                steps.append(f"Apply the rules of differentiation")
                steps.append(f"The derivative is: {derivative}")
                solution = f"f'(x) = {derivative}"
                graph = True
            except Exception as e:
                return jsonify({"error": f"Error in differentiation: {str(e)}"}), 400

        elif problem_type == "integration":
            steps.append(f"Expression to integrate: {expression}")
            steps.append("Find the indefinite integral with respect to x")
            
            try:
                expr = safe_eval(expression)
                integral = integrate(expr, x)
                steps.append(f"Apply the rules of integration")
                steps.append(f"The indefinite integral is: {integral} + C")
                solution = f"∫{expression} dx = {integral} + C"
                graph = True
            except Exception as e:
                return jsonify({"error": f"Error in integration: {str(e)}"}), 400

        elif problem_type == "trigonometry":
            if '=' not in expression:
                return jsonify({"error": "Trigonometric equation must contain an equals sign"}), 400
                
            lhs, rhs = expression.split('=')
            lhs_expr = safe_eval(lhs.strip())
            rhs_expr = safe_eval(rhs.strip())
            eq = Eq(lhs_expr, rhs_expr)
            
            steps.append(f"Trigonometric equation: {lhs} = {rhs}")
            
            # Try to identify the variable
            var_to_solve = None
            for var in [x, y, z]:
                if var in lhs_expr.free_symbols or var in rhs_expr.free_symbols:
                    var_to_solve = var
                    break
                    
            if not var_to_solve:
                return jsonify({"error": "No variable found in equation"}), 400
                
            steps.append(f"Solve for {var_to_solve}")
            
            try:
                solutions = solve(eq, var_to_solve)
                
                if solutions:
                    # Filter out complex solutions
                    real_solutions = [sol for sol in solutions if sol.is_real]
                    
                    if real_solutions:
                        steps.append(f"Found {len(real_solutions)} real solution(s)")
                        # Get one period of solutions
                        solutions_in_period = []
                        for sol in real_solutions:
                            solutions_in_period.append(f"{var_to_solve} = {sol}")
                            steps.append(f"General solution: {var_to_solve} = {sol} + 2πn, where n is an integer")
                        
                        solution = " or ".join(solutions_in_period)
                    else:
                        steps.append("No real solutions found")
                        solution = "No real solutions"
                else:
                    steps.append("No solutions found")
                    solution = "No solution"
                    
                graph = True
            except Exception as e:
                return jsonify({"error": f"Error solving trigonometric equation: {str(e)}"}), 400

        elif problem_type == "limit":
            steps.append(f"Limit problem: {expression}")
            
            # Parse limit expression
            if expression.startswith("limit"):
                # Extract variable, point, and expression from the limit notation
                match = re.match(r"limit\(\s*(\w+)\s*,\s*([^,]+)\s*,\s*(.+)\s*\)", expression)
                if match:
                    var_str, point_str, expr_str = match.groups()
                    
                    # Determine the variable
                    if var_str == 'x':
                        var = x
                    elif var_str == 'y':
                        var = y
                    elif var_str == 'z':
                        var = z
                    else:
                        return jsonify({"error": f"Unsupported variable: {var_str}"}), 400
                    
                    point = safe_eval(point_str)
                    expr = safe_eval(expr_str)
                    
                    steps.append(f"Computing the limit of {expr} as {var} approaches {point}")
                    
                    try:
                        from sympy import limit as sympy_limit
                        result = sympy_limit(expr, var, point)
                        steps.append(f"Apply limit rules and evaluate")
                        steps.append(f"The limit equals {result}")
                        solution = f"lim({var_str}→{point}) {expr_str} = {result}"
                    except Exception as e:
                        return jsonify({"error": f"Error computing limit: {str(e)}"}), 400
                else:
                    return jsonify({"error": "Invalid limit syntax. Use format: limit(x, a, f(x))"}), 400
            else:
                return jsonify({"error": "Invalid limit syntax. Use format: limit(x, a, f(x))"}), 400

        elif problem_type == "statistics":
            if sub_type:
                steps.append(f"Statistical analysis: {sub_type}")
                
                try:
                    # Parse the data
                    if expression.startswith("data ="):
                        data_str = expression.replace("data =", "").strip()
                        data = eval(data_str, {"__builtins__": {}}, {})
                        
                        if not isinstance(data, list):
                            return jsonify({"error": "Data must be a list of numbers"}), 400
                            
                        steps.append(f"Data set: {data}")
                        
                        if sub_type == "mean":
                            mean = sum(data) / len(data)
                            steps.append(f"Calculate the mean: sum(data) / n")
                            steps.append(f"Mean = ({' + '.join(map(str, data))}) / {len(data)} = {mean}")
                            solution = f"Mean = {mean}"
                            
                        elif sub_type == "median":
                            sorted_data = sorted(data)
                            steps.append(f"Sort the data: {sorted_data}")
                            
                            n = len(sorted_data)
                            if n % 2 == 0:  # Even number of elements
                                median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
                                steps.append(f"For even number of elements, median = (data[n/2 - 1] + data[n/2]) / 2")
                                steps.append(f"Median = ({sorted_data[n//2 - 1]} + {sorted_data[n//2]}) / 2 = {median}")
                            else:  # Odd number of elements
                                median = sorted_data[n//2]
                                steps.append(f"For odd number of elements, median = data[n/2]")
                                steps.append(f"Median = {median}")
                                
                            solution = f"Median = {median}"
                            
                        elif sub_type == "mode":
                            from collections import Counter
                            counter = Counter(data)
                            most_common = counter.most_common()
                            
                            if most_common[0][1] > 1:  # Check if any value appears more than once
                                mode_values = [val for val, count in most_common if count == most_common[0][1]]
                                steps.append(f"Find the value(s) that appear most frequently")
                                steps.append(f"Mode = {mode_values}")
                                solution = f"Mode = {mode_values}"
                            else:
                                steps.append("No value appears more than once")
                                solution = "No mode (all values appear exactly once)"
                                
                        elif sub_type == "standard_deviation":
                            mean = sum(data) / len(data)
                            steps.append(f"Calculate the mean: {mean}")
                            
                            variance = sum((x - mean) ** 2 for x in data) / len(data)
                            steps.append(f"Calculate the variance: sum((x - mean)² for x in data) / n")
                            steps.append(f"Variance = {variance}")
                            
                            std_dev = variance ** 0.5
                            steps.append(f"Standard deviation = √variance = {std_dev}")
                            solution = f"Standard Deviation = {std_dev}"
                            
                        elif sub_type == "variance":
                            mean = sum(data) / len(data)
                            steps.append(f"Calculate the mean: {mean}")
                            
                            variance = sum((x - mean) ** 2 for x in data) / len(data)
                            steps.append(f"Calculate the variance: sum((x - mean)² for x in data) / n")
                            steps.append(f"Variance = {variance}")
                            solution = f"Variance = {variance}"
                            
                        elif sub_type == "range":
                            data_range = max(data) - min(data)
                            steps.append(f"Range = maximum value - minimum value")
                            steps.append(f"Range = {max(data)} - {min(data)} = {data_range}")
                            solution = f"Range = {data_range}"
                            
                        else:
                            return jsonify({"error": f"Unsupported statistics sub-type: {sub_type}"}), 400
                            
                    else:
                        return jsonify({"error": "Data must be provided in format: data = [...]"}), 400
                        
                except Exception as e:
                    return jsonify({"error": f"Error in statistical calculation: {str(e)}"}), 400
            else:
                return jsonify({"error": "Statistics sub-type is required"}), 400
        else:
            return jsonify({"error": f"Unsupported problem type: {problem_type}"}), 400

        return jsonify({
            "steps": steps,
            "solution": solution,
            "graph": graph
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)