import functools
import time
import asyncio
import requests
import json
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich.console import Console
import concurrent.futures

console = Console()


executor = concurrent.futures.ThreadPoolExecutor() 

def run_async(func):
    """Decorator to run a function in a separate thread (non-blocking)."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        console.print(f"[bold cyan]🚀 Starting {func.__name__}...[/bold cyan]")

        future = executor.submit(func, *args, **kwargs)  

        def done_callback(f):
            try:
                console.print(f"[bold green]✅ {func.__name__} completed successfully![/bold green]")
            except Exception as e:
                console.print(f"[bold red]❌ {func.__name__} failed: {e}[/bold red]")

        future.add_done_callback(done_callback)
        return future 
    return wrapper



def retry(max_attempts=3, backoff=1.5, exceptions=(Exception,)):
    """Decorator to retry a function (sync or async) on specific exceptions with exponential backoff.
    
    Args:
        max_attempts (int): Maximum retry attempts.
        backoff (float): Exponential backoff multiplier.
        exceptions (tuple): Tuple of exception types to retry on.
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Handles retrying for async functions."""
            attempts = 0
            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    wait_time = backoff ** attempts
                    console.print(f"[bold yellow]⚠️ Attempt {attempts}/{max_attempts} failed: {e}. Retrying in {wait_time:.2f}s...[/bold yellow]")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    console.print(f"[bold red]❌ {func.__name__} failed with an unexpected error: {e}[/bold red]")
                    break 
            console.print(f"[bold red]❌ {func.__name__} failed after {max_attempts} attempts.[/bold red]")
            return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Handles retrying for sync functions."""
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    wait_time = backoff ** attempts
                    console.print(f"[bold yellow]⚠️ Attempt {attempts}/{max_attempts} failed: {e}. Retrying in {wait_time:.2f}s...[/bold yellow]")
                    time.sleep(wait_time)
                except Exception as e:
                    console.print(f"[bold red]❌ {func.__name__} failed with an unexpected error: {e}[/bold red]")
                    break  
            console.print(f"[bold red]❌ {func.__name__} failed after {max_attempts} attempts.[/bold red]")
            return None
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator





class RequestLogger:
    """Context manager to log API requests and their performance with session support."""
    
    def __init__(self, log_to: str | None = None, iterations: int = 1):
        """Initialize the request logger.
        
        Args:
            log_to (str | None): File path to log requests.
            iterations (int): Number of times to make the request.
        """
        self.log_to = log_to
        self.iterations = iterations
        self.start_time = None
        self.end_time = None
        self.responses = []
        self.request_info = None
        self.session = requests.Session() 

    def __enter__(self):
        """Start timing the request session when entering the context."""
        self.start_time = time.time()
        return self

    def request(self, method, url, **kwargs):
        """Perform an API request multiple times and log details."""
        self.request_info = {
            "Method": method,
            "URL": url,
            "Headers": kwargs.get("headers", {}),
            "Payload": kwargs.get("json") or kwargs.get("data", {}),
            "Proxies": kwargs.get("proxies", {})
        }

        for i in range(1, self.iterations + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                self.responses.append(response)
                console.print(f"[bold cyan]✔ Request {i}/{self.iterations} completed[/bold cyan]")
            except Exception as e:
                console.print(f"[bold red]❌ Request {i} failed: {e}[/bold red]")
                self.responses.append(None)
        
        return self.responses[-1] if self.responses else None 

    def __exit__(self, exc_type, exc_value, traceback):
        """Log request details when exiting the context."""
        self.end_time = time.time()
        if not self.responses:
            return 
        duration = (self.end_time - self.start_time) * 1000  

        # Table 1: Request Info
        request_table = Table(title="🌐 API Request Info", show_header=True)
        request_table.add_column("Field", style="magenta", justify="left")
        request_table.add_column("Value", style="cyan", justify="right")
        request_table.add_row("Method", self.request_info["Method"])
        request_table.add_row("URL", self.request_info["URL"])
        request_table.add_row("Headers", str(self.request_info["Headers"]))
        request_table.add_row("Payload", str(self.request_info["Payload"]))
        request_table.add_row("Proxies", str(self.request_info["Proxies"]))

        console.print(request_table)

        stats_table = Table(title="📊 API Response Stats", show_header=True)
        stats_table.add_column("Iteration", style="magenta", justify="right")
        stats_table.add_column("Status Code", style="cyan", justify="right")
        stats_table.add_column("Response Size", style="red", justify="right")
        stats_table.add_column("Time Taken", style="yellow", justify="right")

        for i, response in enumerate(self.responses, start=1):
            if response:
                response_size = len(response.content) if response.content else 0
                stats_table.add_row(str(i), str(response.status_code), f"{response_size} bytes", f"{duration:.2f} ms")
            else:
                stats_table.add_row(str(i), "Failed", "-", "-")

        console.print(stats_table)

        if self.responses[-1]:
            try:
                json_response = self.responses[-1].json()
                console.print(Panel.fit(JSON(json.dumps(json_response, indent=2)), title="📜 JSON Response", border_style="green"))
            except json.JSONDecodeError:
                console.print(Panel.fit(self.responses[-1].text, title="📜 Plain Text Response", border_style="yellow"))

        if self.log_to:
            with open(self.log_to, "a") as f:
                for i, response in enumerate(self.responses, start=1):
                    if response:
                        f.write(f"{self.request_info['Method']} {self.request_info['URL']} - Iteration {i} - {response.status_code}\n")

        self.session.close() 
