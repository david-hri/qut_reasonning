def f(x):
    return x**7 + 7.2 * x - 8.4

def bisection_method(a, b, tol):
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) and f(b) must have opposite signs.")

    steps = []
    steps.append(f"Initial interval: [{a}, {b}]")
    while (b - a) / 2 > tol:
        midpoint = (a + b) / 2
        steps.append(f"Midpoint: {midpoint}, f(midpoint): {f(midpoint)}")

        if f(midpoint) == 0:
            return midpoint  # Found exact root
        elif f(a) * f(midpoint) < 0:
            b = midpoint
        else:
            a = midpoint

    return (a + b) / 2  # Return the midpoint as the approximation

# Define the interval and tolerance
a = -2  # Starting point for the interval
b = 2   # Ending point for the interval
tolerance = 1e-6

# Create a text file to log steps
with open("bisection_method_steps.txt", "w") as file:
    try:
        root = bisection_method(a, b, tolerance)
        file.write(f"Approximate root: {root}\n")
    except ValueError as e:
        file.write(str(e) + "\n")