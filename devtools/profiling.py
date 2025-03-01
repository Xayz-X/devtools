import functools
import time
import psutil
import tracemalloc
import inspect
import asyncio
from collections import defaultdict
from .utils import console
from rich.table import Table
from rich.live import Live


def profiling(func):
    """Decorator to profile execution time, memory usage, and function calls."""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await _profile_func(func, *args, **kwargs, is_async=True)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(_profile_func(func, *args, **kwargs, is_async=False))

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
async def _profile_func(func, *args, is_async=False, **kwargs):
    """Handles profiling for both sync & async functions."""
    
    tracemalloc.start()
    start_time = time.time()

    line_times = defaultdict(float)

    def trace_calls(frame, event, arg):
        if event == "line":
            line_no = frame.f_lineno
            line_times[line_no] += time.time() - start_time

    inspect.currentframe().f_trace = trace_calls

    try:
        if is_async:
            result = await func(*args, **kwargs)  
        else:
            result = func(*args, **kwargs)
    finally:
        end_time = time.time()
        tracemalloc.stop()

    # Collect memory usage
    memory_stats = tracemalloc.get_traced_memory()
    execution_time = (end_time - start_time) * 1000  
    peak_memory = memory_stats[1] / 1024  

    _display_profile(func.__name__, execution_time, peak_memory, line_times)
    return result

def _display_profile(func_name, execution_time, peak_memory, line_times):
    """Formats and displays profiling results in a table."""
    
    table = Table(title=f"⚡ Profiling Report: {func_name}")
    table.add_column("Metric", style="magenta", justify="left")
    table.add_column("Value", style="cyan", justify="right")

    table.add_row("Execution Time", f"{execution_time:.2f} ms")
    table.add_row("Peak Memory Usage", f"{peak_memory:.2f} KB")

    console.print(table)

    if line_times:
        line_table = Table(title=f"📊 Line Execution Times: {func_name}")
        line_table.add_column("Line No.", style="magenta", justify="right")
        line_table.add_column("Execution Time (ms)", style="cyan", justify="right")

        for line, exec_time in sorted(line_times.items()):
            line_table.add_row(str(line), f"{exec_time:.2f}")

        console.print(line_table)
        
        
        


def memory_usage(func):
    """Decorator to measure memory usage of a function and track each variable with line numbers."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()

        snapshot_before = tracemalloc.take_snapshot()

        result = func(*args, **kwargs) 

        snapshot_after = tracemalloc.take_snapshot()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_diff = {}
        stats = snapshot_after.compare_to(snapshot_before, "lineno")

        for stat in stats:
            line_number = stat.traceback[0].lineno
            memory_used_kb = stat.size_diff / 1024  
            if memory_used_kb > 0:
                memory_diff[line_number] = memory_used_kb

        source_lines, start_line = inspect.getsourcelines(func)

        table = Table(title=f"Memory Usage Report for [cyan]{func.__name__}[/cyan]")
        table.add_column("Line", style="magenta", justify="right")
        table.add_column("Code", style="yellow", justify="left")
        table.add_column("Memory (KB)", style="red", justify="right")

        for i, code_line in enumerate(source_lines, start=start_line):
            if i in memory_diff:
                table.add_row(str(i), code_line.strip(), f"{memory_diff[i]:.2f} KB")

        console.print(table)
        console.print(f"[bold yellow]🔍 Total Memory Used:[/bold yellow] {current / 1024:.2f} KB")
        console.print(f"[bold red]🚀 Peak Memory Usage:[/bold red] {peak / 1024:.2f} KB\n")

        return result

    return wrapper



def performance(func):
    """Decorator to monitor CPU & memory usage during function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with Live(auto_refresh=False) as live:
            table = Table(title=f"Performance Monitoring: {func.__name__}()")
            table.add_column("Time (s)", justify="right", style="magenta")
            table.add_column("CPU (%)", justify="right", style="yellow")
            table.add_column("Memory (MB)", justify="right", style="red")

            start_time = time.time()
            result = None

            def update_table():
                elapsed = time.time() - start_time
                cpu_usage = psutil.cpu_percent()
                mem_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB
                table.add_row(f"{elapsed:.2f}", f"{cpu_usage}%", f"{mem_usage:.2f} MB")
                live.update(table, refresh=True)

            result = func(*args, **kwargs)
            update_table()

            return result
    return wrapper