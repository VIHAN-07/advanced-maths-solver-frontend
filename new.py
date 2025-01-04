from flask import Flask, request, jsonify, render_template_string
from sympy import symbols, Eq, solve, diff, integrate, sin, cos, exp, log, pi
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Define symbols
x, y, z, r = symbols('x y z r')

# HTML Template for the UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Math Solver</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        body { background-color: #f7f9fc; font-family: Arial, sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        textarea, select, button { margin-top: 10px; }
        .output { background-color: #e9f5ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Interactive Math Solver</h1>
        <p class="text-center">Solve various mathematical problems step-by-step or plot graphs.</p>
        <label for="type" class="form-label">Select Problem Type:</label>
        <select id="type" class="form-select">
            <option value="linear">Linear Equation (e.g., 2*x + 3 = 7)</option>
            <option value="quadratic">Quadratic Equation (e.g., x**2 + 3*x + 2 = 0)</option>
            <option value="system">System of Equations (e.g., 2*x + y = 5; x - y = 1)</option>
            <option value="inequality">Inequality (e.g., 2*x + 3 <= 7)</option>
            <option value="geometry">Geometry (Circle Area or Circumference, e.g., circle_area=5)</option>
            <option value="differentiation">Differentiation (e.g., x**2 + 3*x)</option>
            <option value="integration">Integration (e.g., x**2 + 3*x)</option>
            <option value="graphing">Graphing Calculator (e.g., sin(x), x**2)</option>
        </select>

        <label for="expression" class="form-label">Enter Expression:</label>
        <textarea id="expression" class="form-control" rows="3" placeholder="Enter your mathematical expression here"></textarea>

        <button class="btn btn-primary w-100" onclick="solveProblem()">Solve</button>

        <div id="output" class="output"></div>
    </div>

    <script>
        async function solveProblem() {
            const type = document.getElementById('type').value;
            const expression = document.getElementById('expression').value;
            const output = document.getElementById('output');

            output.innerHTML = ""; // Clear previous output

            try {
                const response = await fetch('/solve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, expression })
                });

                const data = await response.json();

                if (data.error) {
                    output.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    if (type === "graphing" && data.graph) {
                        output.innerHTML = `<h3>Graph:</h3><img src="data:image/png;base64,${data.graph}" alt="Graph" class="img-fluid mt-3">`;
                    } else {
                        const steps = data.steps.map(step => `<div>${step}</div>`).join("");
                        output.innerHTML = `<h3>Solution Steps:</h3>${steps}<h3>Final Solution:</h3><div>${data.solution}</div>`;

                        if (data.graph) {
                            output.innerHTML += `<img src="data:image/png;base64,${data.graph}" alt="Graph" class="img-fluid mt-3">`;
                        }
                    }
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

        solution_steps = []
        solution = None
        graph = None

        if problem_type == "linear":
            lhs, rhs = expression.split('=')
            eq = Eq(eval(lhs), eval(rhs))
            solution = solve(eq, x)
            solution_steps.append(f"Solve for x: {eq}")
            solution_steps.append(f"Solution: x = {solution[0]}")

        elif problem_type == "quadratic":
            lhs, rhs = expression.split('=')
            eq = Eq(eval(lhs), eval(rhs))
            solution = solve(eq, x)
            solution_steps.append(f"Quadratic Equation: {eq}")
            solution_steps.append(f"Roots: {solution}")

        elif problem_type == "differentiation":
            expr = eval(expression)
            derivative = diff(expr, x)
            solution = derivative
            solution_steps.append(f"Expression: {expr}")
            solution_steps.append(f"Derivative: {derivative}")

            # Plot the function and its derivative
            fig, ax = plt.subplots()
            x_vals = [i for i in range(-10, 11)]
            y_vals = [expr.evalf(subs={x: val}) for val in x_vals]
            dy_vals = [derivative.evalf(subs={x: val}) for val in x_vals]
            ax.plot(x_vals, y_vals, label='Function')
            ax.plot(x_vals, dy_vals, label='Derivative', linestyle='--')
            ax.legend()
            ax.set_title('Function and Derivative')
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graph = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        elif problem_type == "integration":
            expr = eval(expression)
            integral = integrate(expr, x)
            solution = f"{integral} + C"
            solution_steps.append(f"Expression: {expr}")
            solution_steps.append(f"Integral: {integral} + C")

            # Plot the function and its integral
            fig, ax = plt.subplots()
            x_vals = [i for i in range(-10, 11)]
            y_vals = [expr.evalf(subs={x: val}) for val in x_vals]
            int_vals = [integrate(expr, (x, -10, val)).evalf() for val in x_vals]
            ax.plot(x_vals, y_vals, label='Function')
            ax.plot(x_vals, int_vals, label='Integral', linestyle='--')
            ax.legend()
            ax.set_title('Function and Integral')
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graph = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        elif problem_type == "graphing":
            expr = eval(expression)

            # Plot the graph for the given expression
            fig, ax = plt.subplots()
            x_vals = [i for i in range(-10, 11)]
            y_vals = [expr.evalf(subs={x: val}) for val in x_vals]
            ax.plot(x_vals, y_vals, label='Graph of the Equation')
            ax.legend()
            ax.set_title('Graphing Calculator')
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graph = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        else:
            return jsonify({"error": "Unsupported problem type."}), 400

        return jsonify({"steps": solution_steps, "solution": str(solution), "graph": graph})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
