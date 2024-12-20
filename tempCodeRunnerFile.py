from flask import Flask, request, jsonify, render_template_string
from sympy import symbols, Eq, solve, diff, integrate, pi
from sympy.solvers.inequalities import solve_univariate_inequality

app = Flask(__name__)

# Define symbols
x, y, z, r = symbols('x y z r')

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Math Solver</title>
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

    </style>
</head>
<body>
    <h1>Interactive Math Solver</h1>
    <div class="container">
        <label for="type">Select Problem Type:</label>
        <select id="type">
            <option value="linear">Linear Equation</option>
            <option value="quadratic">Quadratic Equation</option>
            <option value="system">System of Equations</option>
            <option value="inequality">Inequality</option>
            <option value="geometry">Geometry (Circle Area or Circumference)</option>
            <option value="differentiation">Differentiation</option>
            <option value="integration">Integration</option>
        </select>

        <label for="expression">Enter Expression:</label>
        <textarea id="expression" rows="4" placeholder="Enter your mathematical expression here..."></textarea>

        <button onclick="solveProblem()">Solve</button>

        <div id="output"></div>
    </div>

    <script>
        async function solveProblem() {
            const type = document.getElementById('type').value;
            const expression = document.getElementById('expression').value.trim();
            const output = document.getElementById('output');

            output.innerHTML = ""; // Clear previous output

            if (!expression) {
                output.innerHTML = `<div class="error">Please enter a valid expression.</div>`;
                return;
            }

            try {
                output.innerHTML = "<div>Solving... Please wait.</div>";
                const response = await fetch('/solve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, expression })
                });

                const data = await response.json();

                if (data.error) {
                    output.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    const stepsHTML = data.steps.map(
                        (step, index) => `<div class="step"><strong>Step ${index + 1}:</strong> ${step}</div>`
                    ).join("");
                    output.innerHTML = `<h3>Solution Steps:</h3>${stepsHTML}<h3>Final Solution:</h3><div>${data.solution}</div>`;
                }
            } catch (err) {
                output.innerHTML = `<div class="error">An error occurred: ${err.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/solve', methods=['POST'])
def solve_problem():
    try:
        data = request.json
        problem_type = data.get('type')
        expression = data.get('expression')

        steps = []
        solution = None

        if problem_type == "linear":
            lhs, rhs = expression.split('=')
            eq = Eq(eval(lhs), eval(rhs))
            steps.append(f"Step 1: Formulate the equation: {lhs} = {rhs}")
            solution = solve(eq, x)
            steps.append(f"Step 2: Solve for x using isolation: x = {solution[0]}")

        elif problem_type == "quadratic":
            lhs, rhs = expression.split('=')
            eq = Eq(eval(lhs), eval(rhs))
            steps.append(f"Step 1: Write the equation: {lhs} = {rhs}")
            steps.append("Step 2: Identify coefficients (a, b, c) from ax² + bx + c = 0")
            solution = solve(eq, x)
            steps.append("Step 3: Use the quadratic formula: x = [-b ± √(b² - 4ac)] / 2a")
            steps.append(f"Roots are: {solution}")

        elif problem_type == "system":
            equations = expression.split(';')
            eqs = [Eq(eval(e.split('=')[0]), eval(e.split('=')[1])) for e in equations]
            steps.append("Step 1: Write the system of equations:")
            for eq in equations:
                steps.append(f"    {eq}")
            steps.append("Step 2: Use substitution or elimination.")
            solution = solve(eqs, [x, y])
            steps.append(f"Step 3: Solve the system. Solutions are: x = {solution[x]}, y = {solution[y]}")

        elif problem_type == "inequality":
            inequality = eval(expression)
            steps.append(f"Step 1: Write the inequality: {expression}")
            steps.append("Step 2: Solve the inequality using the inequality rules.")
            solution = solve_univariate_inequality(inequality, x)
            steps.append(f"Solution is: {solution}")

        elif problem_type == "geometry":
            if "circle_area" in expression:
                radius = eval(expression.split('=')[1])
                steps.append(f"Step 1: Extract radius: r = {radius}")
                steps.append("Step 2: Use the formula for area: A = πr²")
                solution = pi * radius**2
                steps.append(f"Step 3: Calculate: A = {solution}")
            elif "circle_circumference" in expression:
                radius = eval(expression.split('=')[1])
                steps.append(f"Step 1: Extract radius: r = {radius}")
                steps.append("Step 2: Use the formula for circumference: C = 2πr")
                solution = 2 * pi * radius
                steps.append(f"Step 3: Calculate: C = {solution}")

        elif problem_type == "differentiation":
            expr = eval(expression)
            steps.append(f"Step 1: Write the expression: {expression}")
            steps.append("Step 2: Differentiate with respect to x.")
            solution = diff(expr, x)
            steps.append(f"Step 3: Derivative is: {solution}")

        elif problem_type == "integration":
            expr = eval(expression)
            steps.append(f"Step 1: Write the expression: {expression}")
            steps.append("Step 2: Integrate with respect to x.")
            solution = integrate(expr, x)
            steps.append(f"Step 3: Integral is: {solution} + C")

        else:
            return jsonify({"error": "Invalid problem type!"}), 400

        return jsonify({"steps": steps, "solution": str(solution)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
