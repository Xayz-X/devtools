from devtools import step_debugger

import asyncio

@step_debugger(breakpoint_line=8)
def test_function():
    x = 5
    y = 10
    z = x + y
    print(f"Result: {z}")
    return z

@step_debugger(breakpoint_line=18)
async def async_task():
    a = 100
    b = 200
    await asyncio.sleep(1)
    c = a + b
    print(f"Async Result: {c}")
    return c

test_function()
asyncio.run(async_task()) 
