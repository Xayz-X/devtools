# DevTools: Advanced Debugging and Profiling for Python

## 📌 Overview

**DevTools** is a collection of powerful Python decorators for debugging, profiling, and optimizing code. It provides:

- **Function execution visualization**
- **Step-by-step debugging**
- **Performance and memory profiling**
- **Exception handling**
- **Async execution and automatic retries**
- **API request logging**

With **DevTools**, you can gain deep insights into your code execution while improving debugging efficiency.

[!INFO] Currently, the library offers partial support for both synchronous and asynchronous functions. I originally developed it for my own debugging purposes, but if anyone finds it useful, feel free to use it, fork the codebase or make any changes you'd like. You have full freedom to modify and adapt it as needed.

---

## 🔧 Installation

Install using pip:
```bash
pip install ...
```

## 🚀 Features & Usage

### Debugging Decorators

### 🔍 `dbg`: Function Execution Visualization
The `dbg` decorator helps in visualizing function execution in a nested tree format with proper function signatures and return values.

#### **Usage:**
```python
from devtools import dbg

@dbg
def test_function():
    x = 5
    y = 10
    z = x + y
    print(f"Result: {z}")
    return z
```

[!TIP] Use this decorator to understand the flow of function calls and track variable changes at each step.

---

### 🛑 `step_debugger`: Step-by-Step Debugging
The `step_debugger` decorator enables **interactive debugging**, allowing you to **pause execution** at a specific line and inspect local variables.

#### **Usage:**
```python
from devtools import step_debugger

@step_debugger(breakpoint_line=3)
def test_function():
    x = 5
    y = 10
    z = x + y
    print(f"Result: {z}")
    return z
```

🔹 **Commands Available:**
- `(n) next` → Move to the next step
- `(c) continue` → Continue execution until the next breakpoint
- `(q) quit` → Stop debugging

[!TIP] This is useful for troubleshooting complex logic.

---

### Profiling Decorators

### ⏳ `profiling`: Execution Time & Performance Analysis
This decorator measures **execution time, memory usage, and function calls** for both **sync and async functions**.

#### **Usage:**
```python
from devtools import profiling

@profiling
def test_function():
    x = [i for i in range(10000)]
    return x
```

[!TIP] Identify slow-performing parts of your application easily!

---

### 💾 `memory_usage`: Track Memory Usage
The `memory_usage` decorator measures how much memory each **variable** consumes inside a function.

#### **Usage:**
```python
from devtools import memory_usage

@memory_usage
def test_function():
    x = [i for i in range(10000)]
    return x
```

🔹 **Output Example:**
```
📊 Memory Usage Report for test_function
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Line ┃ Variable ┃ Memory (KB) ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│    3 │ x        │  78.23 KB   │
└──────┴──────────┴─────────────┘
🔍 Total Memory Used: 78.23 KB
```

[!TIP] Use this to optimize large data processing functions.

---

### Exception Handling Decorator

### 🚨 `catch_exception`: Automatically Handle & Log Errors
This decorator catches exceptions and logs them instead of crashing your program.

#### **Usage:**
```python
from devtools import catch_exception

@catch_exception(log_to="errors.log", return_value=None)
def test_function():
    x = 1 / 0  # Raises ZeroDivisionError
    return x
```

[!TIP] This is useful for production environments where you want to log errors instead of stopping execution.

---

### Utility Decorators

### ⚡ `run_async`: Run Functions in a Separate Thread (Non-Blocking)
Runs a function asynchronously in the background without blocking execution.

#### **Usage:**
```python
from devtools import run_async

@run_async
def test_function():
    time.sleep(2)
    print("Function completed")
```

[!TIP] Ideal for running time-consuming tasks without freezing your main application.

---

### 🔁 `retry`: Automatically Retry Failed Functions
Retries a function **if it raises an exception**, with a configurable number of attempts and delay.

#### **Usage:**
```python
from devtools import retry
import requests

@retry(max_attempts=3, backoff=1.5, exceptions=(requests.RequestException,))
def test_function():
    response = requests.get("https://example.com")
    return response
```

[!TIP] Useful for **unstable API calls** or functions that may occasionally fail.

---

### 🌍 `RequestLogger`: API Request Logger
A context manager that logs API requests and responses, including headers, status codes, and response times.

#### **Usage:**
```python
from devtools import RequestLogger

with RequestLogger(log_to="requests.log", iterations=3) as logger:
    response = logger.request("GET", "https://example.com")
```

[!TIP] Use this for **API performance monitoring** and debugging.

---

