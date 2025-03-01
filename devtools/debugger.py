import sys
import time
import inspect
import asyncio
import functools

from .utils import console
from rich.tree import Tree
from rich.traceback import install
from rich.table import Table

install()

CALL_STACK = [] 
DEBUG_TREE = None  

__all__: tuple[str, ...] = ("dbg", "step_debugger")


def dbg(func):
    """Decorator to visualize function execution in a nested tree format with proper function signature and return values."""

    def trace_calls(frame, event, arg):
        """Trace function calls, ensuring proper nesting inside a single tree."""
        global CALL_STACK, DEBUG_TREE

        if frame.f_code.co_name == func.__name__: 
            if event == "call":
                func_name = func.__name__
                func_args = inspect.signature(func)
                full_signature = f"{func_name}{func_args}"

                node = Tree(f"[bold cyan]▶ Function Called: {full_signature}[/bold cyan]", guide_style="cyan")

                if CALL_STACK: 
                    CALL_STACK[-1].add(node)
                else:
                    DEBUG_TREE = node 
                
                CALL_STACK.append(node)  
            
            elif event == "return":
                CALL_STACK[-1].add(f"[bold green]✔ Return:[/bold green] {arg}")
                CALL_STACK.pop()  
            
            return trace_lines  
        return None  

    def trace_lines(frame, event, arg):
        """Log each line execution and variable values inside the active function."""
        if event == "line" and CALL_STACK:
            local_vars = frame.f_locals.copy() 

            if local_vars:
                vars_tree = Tree(f"[blue]Line {frame.f_lineno} in `{frame.f_code.co_name}`[/blue]", guide_style="blue")
                for var, val in local_vars.items():
                    vars_tree.add(f"[magenta]{var}[/magenta]: [yellow]{repr(val)}[/yellow]")
                CALL_STACK[-1].add(vars_tree) 
        
        return trace_lines

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global CALL_STACK, DEBUG_TREE
        is_top_level = not CALL_STACK 

        start_time = time.time()
        sys.settrace(trace_calls) 
        try:
            result = func(*args, **kwargs)
        finally:
            sys.settrace(None) 
            execution_time = (time.time() - start_time) * 1000
            
            if is_top_level and DEBUG_TREE:  
                DEBUG_TREE.add(f"[bold green]✔ Return:[/bold green] {result}")  
                console.print(DEBUG_TREE)
                console.print(f"\n[bold yellow]⏱ Execution Time:[/bold yellow] {execution_time:.2f} ms", style="yellow")
                DEBUG_TREE = None  
        return result

    return wrapper



def step_debugger(breakpoint_line: int = None):
    """Decorator to enable step-by-step debugging for sync & async functions."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _debug_function_async(func, *args, breakpoint_line=breakpoint_line, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _debug_function_sync(func, *args, breakpoint_line=breakpoint_line, **kwargs)
            return sync_wrapper
    return decorator

def _debug_function_sync(func, *args, breakpoint_line=None, **kwargs):
    """Step-debugging for synchronous functions."""
    step_mode = False 

    def trace_calls(frame, event, arg):
        nonlocal step_mode
      
        if frame.f_code.co_name != func.__name__:
            return
        if event == "line":
            line_no = frame.f_lineno
            code = inspect.getframeinfo(frame).code_context[0].strip()
            console.print(f"\n🔎 [bold yellow]Executing Line {line_no}:[/bold yellow] {code}")
            _display_variables(frame.f_locals)
            if breakpoint_line and line_no == breakpoint_line:
                console.print(f"\n🛑 [bold red]Breakpoint Hit at Line {line_no}[/bold red]")
                step_mode = True
            while step_mode:
                cmd = console.input("[bold cyan](n: next, c: continue, q: quit)[/bold cyan] > ").strip().lower()
                if cmd == "n":
                    break
                elif cmd == "c":
                    step_mode = False
                    break
                elif cmd == "q":
                    console.print("[bold red]❌ Debugging Stopped.[/bold red]")
                    sys.exit(0)
        return trace_calls

    sys.settrace(trace_calls)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(None)
    return result

async def _debug_function_async(func, *args, breakpoint_line=None, **kwargs):
    """Step-debugging for asynchronous functions."""
    step_mode = False 

    def trace_calls(frame, event, arg):
        nonlocal step_mode
        if frame.f_code.co_name != func.__name__:
            return
        if event == "line":
            line_no = frame.f_lineno
            code = inspect.getframeinfo(frame).code_context[0].strip()
            console.print(f"\n🔎 [bold yellow]Executing Line {line_no}:[/bold yellow] {code}")
            _display_variables(frame.f_locals)
            if breakpoint_line and line_no == breakpoint_line:
                console.print(f"\n🛑 [bold red]Breakpoint Hit at Line {line_no}[/bold red]")
                step_mode = True
            while step_mode:
                cmd = console.input("[bold cyan](n: next, c: continue, q: quit)[/bold cyan] > ").strip().lower()
                if cmd == "n":
                    break
                elif cmd == "c":
                    step_mode = False
                    break
                elif cmd == "q":
                    console.print("[bold red]❌ Debugging Stopped.[/bold red]")
                    sys.exit(0)
        return trace_calls

    sys.settrace(trace_calls)
    try:
        result = await func(*args, **kwargs)
    finally:
        sys.settrace(None)
    return result

def _display_variables(local_vars):
    """Displays the function's local variables in a formatted table."""
    if not local_vars:
        console.print("📭 No local variables yet.", style="dim")
        return

    table = Table(title="📌 Local Variables", show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="yellow")
    for var, value in local_vars.items():
        if not var.startswith("__"):
            try:
                table.add_row(var, repr(value))
            except Exception:
                table.add_row(var, "[red]⚠ Cannot display value[/red]")
    console.print(table)

