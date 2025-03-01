from devtools import step_debugger

@step_debugger(breakpoint_line=5)
def test_function():
    x = 5
    y = 10
    z = x + y
    print(f"Result: {z}")
    return z

test_function()