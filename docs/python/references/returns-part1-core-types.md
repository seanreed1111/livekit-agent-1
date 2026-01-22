# Returns Library Guide - Part 1: Core Types and Containers

A comprehensive guide to the fundamental types and containers in the `returns` library for functional programming in Python.

## Table of Contents

1. [Introduction](#introduction)
2. [Maybe Container](#maybe-container)
   - [Basic Usage](#maybe-basic-usage)
   - [Creating Maybe Instances](#creating-maybe-instances)
   - [Working with Maybe](#working-with-maybe)
   - [Chaining Operations](#chaining-maybe-operations)
   - [Pattern Matching](#maybe-pattern-matching)
3. [Result Container](#result-container)
   - [Success and Failure](#success-and-failure)
   - [Creating Results](#creating-results)
   - [Transforming Results](#transforming-results)
   - [Error Handling](#result-error-handling)
   - [Pattern Matching](#result-pattern-matching)
4. [Safe Decorator](#safe-decorator)
   - [Basic Safe Usage](#basic-safe-usage)
   - [Filtering Exceptions](#filtering-exceptions)
   - [Composing Safe Functions](#composing-safe-functions)
5. [IO Container](#io-container)
   - [Marking Impure Operations](#marking-impure-operations)
   - [Creating IO Instances](#creating-io-instances)
   - [Composing IO Operations](#composing-io-operations)
   - [IO vs IOResult](#io-vs-ioresult)
6. [Future Container](#future-container)
   - [Basic Future Usage](#basic-future-usage)
   - [FutureResult](#futureresult)
   - [Composing Async Operations](#composing-async-operations)
7. [future_safe Decorator](#future_safe-decorator)
   - [Basic future_safe Usage](#basic-future_safe-usage)
   - [Error Handling in Async Code](#error-handling-in-async-code)
8. [Context Container](#context-container)
   - [RequiresContext Basics](#requirescontext-basics)
   - [Dependency Injection](#dependency-injection)
   - [Composing with Context](#composing-with-context)
9. [Pipelines](#pipelines)
   - [flow() Function](#flow-function)
   - [pipe() Function](#pipe-function)
   - [managed() Function](#managed-function)

---

## Introduction

The `returns` library brings functional programming patterns to Python, providing container types that make error handling, side effects, and asynchronous operations more explicit and composable. This guide covers the core types and their usage patterns.

**Installation:**
```bash
pip install returns
```

**Import conventions:**
```python
from returns.maybe import Maybe, Some, Nothing
from returns.result import Result, Success, Failure, safe
from returns.io import IO, IOResult, impure, impure_safe
from returns.future import Future, FutureResult, future_safe
from returns.context import RequiresContext
from returns.pipeline import flow, pipe, managed
```

---

## Maybe Container

The `Maybe` container eliminates `None`-related bugs by providing explicit `Some` and `Nothing` variants.

### Maybe Basic Usage

**Problem:** Traditional nullable code requires constant None checks:
```python
def get_user_email(user_id: int) -> str | None:
    user = find_user(user_id)
    if user is None:
        return None
    if user.profile is None:
        return None
    if user.profile.email is None:
        return None
    return user.profile.email.lower()
```

**Solution with Maybe:**
```python
from returns.maybe import Maybe, Some, Nothing

def get_user_email(user_id: int) -> Maybe[str]:
    return (
        find_user(user_id)
        .bind_optional(lambda user: user.profile)
        .bind_optional(lambda profile: profile.email)
        .map(str.lower)
    )
```

### Creating Maybe Instances

**Example 1: From Optional Values**
```python
from returns.maybe import Maybe

# Convert None to Nothing, values to Some
result1 = Maybe.from_optional(None)  # Nothing
result2 = Maybe.from_optional(42)    # Some(42)
result3 = Maybe.from_optional("hello")  # Some("hello")

print(result1)  # <Nothing>
print(result2)  # <Some: 42>
```

**Example 2: Explicit Construction**
```python
from returns.maybe import Some, Nothing

# Direct construction
success = Some(100)
failure = Nothing

# Even None can be wrapped if needed
wrapped_none = Maybe.from_value(None)  # Some(None)
```

**Example 3: From Functions**
```python
from returns.maybe import maybe

@maybe
def safe_divide(a: int, b: int) -> int | None:
    if b == 0:
        return None
    return a // b

result1 = safe_divide(10, 2)  # Some(5)
result2 = safe_divide(10, 0)  # Nothing
```

### Working with Maybe

**Example 1: Extracting Values**
```python
from returns.maybe import Some, Nothing

value = Some(42)
empty = Nothing

# Get value or provide default
print(value.value_or(0))   # 42
print(empty.value_or(0))   # 0

# Unwrap (raises if Nothing)
print(value.unwrap())      # 42
# empty.unwrap()           # Raises UnwrapFailedError

# Lazy default evaluation
expensive_default = lambda: expensive_computation()
result = empty.or_else_call(expensive_default)
```

**Example 2: Mapping Over Maybe**
```python
from returns.maybe import Some, Nothing

def double(x: int) -> int:
    return x * 2

result1 = Some(5).map(double)    # Some(10)
result2 = Nothing.map(double)     # Nothing

# Chain multiple maps
result3 = Some(3).map(double).map(lambda x: x + 1)  # Some(7)
```

**Example 3: Conditional Operations**
```python
from returns.maybe import Some, Nothing

def is_positive(x: int) -> bool:
    return x > 0

# Filter-like behavior
value = Some(10)
result = value if is_positive(value.unwrap()) else Nothing
# Better: use custom filter logic with bind
```

### Chaining Maybe Operations

**Example 1: Sequential Binds**
```python
from returns.maybe import Maybe, Some

def safe_int(s: str) -> Maybe[int]:
    try:
        return Some(int(s))
    except ValueError:
        return Maybe.empty

def safe_reciprocal(x: int) -> Maybe[float]:
    if x == 0:
        return Maybe.empty
    return Some(1.0 / x)

# Chain operations
result1 = safe_int("10").bind(safe_reciprocal)  # Some(0.1)
result2 = safe_int("0").bind(safe_reciprocal)   # Nothing
result3 = safe_int("abc").bind(safe_reciprocal) # Nothing
```

**Example 2: Working with Optionals**
```python
from returns.maybe import Maybe

class Address:
    def __init__(self, city: str | None):
        self.city = city

class User:
    def __init__(self, address: Address | None):
        self.address = address

def get_city(user: User | None) -> Maybe[str]:
    return (
        Maybe.from_optional(user)
        .bind_optional(lambda u: u.address)
        .bind_optional(lambda a: a.city)
    )

user1 = User(Address("New York"))
user2 = User(Address(None))
user3 = User(None)

print(get_city(user1))  # Some("New York")
print(get_city(user2))  # Nothing
print(get_city(user3))  # Nothing
```

**Example 3: Complex Composition**
```python
from returns.maybe import Maybe, Some

def parse_config(text: str) -> Maybe[dict]:
    """Parse configuration from text."""
    import json
    try:
        return Some(json.loads(text))
    except json.JSONDecodeError:
        return Maybe.empty

def get_database_url(config: dict) -> Maybe[str]:
    """Extract database URL from config."""
    return Maybe.from_optional(config.get('database', {}).get('url'))

def validate_url(url: str) -> Maybe[str]:
    """Validate URL format."""
    if url.startswith(('postgres://', 'mysql://')):
        return Some(url)
    return Maybe.empty

# Complete pipeline
config_text = '{"database": {"url": "postgres://localhost/mydb"}}'
result = (
    parse_config(config_text)
    .bind(get_database_url)
    .bind(validate_url)
)
print(result)  # Some("postgres://localhost/mydb")
```

### Maybe Pattern Matching

**Python 3.10+ Pattern Matching:**
```python
from returns.maybe import Maybe, Some

def describe_maybe(value: Maybe[int]) -> str:
    match value:
        case Some(n):
            return f"Got value: {n}"
        case Maybe.empty:
            return "Got nothing"

print(describe_maybe(Some(42)))    # "Got value: 42"
print(describe_maybe(Maybe.empty)) # "Got nothing"

# Match with guards
def classify_number(value: Maybe[int]) -> str:
    match value:
        case Some(n) if n > 0:
            return "Positive"
        case Some(n) if n < 0:
            return "Negative"
        case Some(0):
            return "Zero"
        case Maybe.empty:
            return "No value"
```

---

## Result Container

The `Result` container makes error handling explicit by returning either `Success` or `Failure` instead of raising exceptions.

### Success and Failure

**Example 1: Basic Usage**
```python
from returns.result import Success, Failure

# Successful operation
good_result: Result[int, str] = Success(42)

# Failed operation
bad_result: Result[int, str] = Failure("Something went wrong")

print(good_result)  # <Success: 42>
print(bad_result)   # <Failure: Something went wrong>
```

**Example 2: Type Safety**
```python
from returns.result import Result, Success, Failure

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Failure("Division by zero")
    return Success(a / b)

result1 = divide(10, 2)   # Success(5.0)
result2 = divide(10, 0)   # Failure("Division by zero")
```

**Example 3: Using ResultE Alias**
```python
from returns.result import ResultE, Success, Failure

# ResultE is Result[T, Exception]
def parse_int(s: str) -> ResultE[int]:
    try:
        return Success(int(s))
    except ValueError as e:
        return Failure(e)

result = parse_int("42")   # Success(42)
error = parse_int("abc")   # Failure(ValueError(...))
```

### Creating Results

**Example 1: From Try-Catch**
```python
from returns.result import Result, Success, Failure

def read_file(path: str) -> Result[str, str]:
    try:
        with open(path, 'r') as f:
            return Success(f.read())
    except FileNotFoundError:
        return Failure(f"File not found: {path}")
    except PermissionError:
        return Failure(f"Permission denied: {path}")
    except Exception as e:
        return Failure(f"Unexpected error: {e}")

content = read_file("config.txt")
```

**Example 2: Validation Functions**
```python
from returns.result import Result, Success, Failure

def validate_email(email: str) -> Result[str, str]:
    if '@' not in email:
        return Failure("Email must contain @")
    if '.' not in email.split('@')[1]:
        return Failure("Email domain must contain .")
    return Success(email)

def validate_age(age: int) -> Result[int, str]:
    if age < 0:
        return Failure("Age cannot be negative")
    if age > 150:
        return Failure("Age too high")
    return Success(age)

email_result = validate_email("user@example.com")  # Success
age_result = validate_age(25)                      # Success
```

**Example 3: Converting from Other Types**
```python
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing

def maybe_to_result(maybe_val: Maybe[int]) -> Result[int, str]:
    match maybe_val:
        case Some(value):
            return Success(value)
        case Maybe.empty:
            return Failure("No value provided")

result1 = maybe_to_result(Some(42))      # Success(42)
result2 = maybe_to_result(Maybe.empty)   # Failure("No value provided")
```

### Transforming Results

**Example 1: Mapping Success Values**
```python
from returns.result import Success, Failure

result = Success(5)
doubled = result.map(lambda x: x * 2)        # Success(10)
stringified = doubled.map(str)                # Success("10")

# Failure is unchanged by map
failure = Failure("error")
mapped_failure = failure.map(lambda x: x * 2) # Failure("error")
```

**Example 2: Transforming Errors with alt**
```python
from returns.result import Success, Failure

def make_error_user_friendly(error: str) -> str:
    return f"Oops! {error}"

result1 = Success(42).alt(make_error_user_friendly)  # Success(42)
result2 = Failure("DB error").alt(make_error_user_friendly)
# Failure("Oops! DB error")

# Chain multiple transformations
result3 = (
    Failure("connection timeout")
    .alt(str.upper)
    .alt(lambda e: f"ERROR: {e}")
)
# Failure("ERROR: CONNECTION TIMEOUT")
```

**Example 3: Binding Results**
```python
from returns.result import Result, Success, Failure

def safe_sqrt(x: float) -> Result[float, str]:
    if x < 0:
        return Failure("Cannot take square root of negative number")
    return Success(x ** 0.5)

def safe_reciprocal(x: float) -> Result[float, str]:
    if x == 0:
        return Failure("Cannot divide by zero")
    return Success(1 / x)

# Successful chain
result1 = Success(16.0).bind(safe_sqrt).bind(safe_reciprocal)
# Success(0.25)

# Fails at first step
result2 = Success(-4.0).bind(safe_sqrt).bind(safe_reciprocal)
# Failure("Cannot take square root of negative number")

# Fails at second step
result3 = Success(0.0).bind(safe_sqrt).bind(safe_reciprocal)
# Failure("Cannot divide by zero")
```

### Result Error Handling

**Example 1: Recovering from Errors with lash**
```python
from returns.result import Result, Success, Failure

def fetch_from_cache(key: str) -> Result[str, str]:
    return Failure("Cache miss")

def fetch_from_database(error: str) -> Result[str, str]:
    print(f"Cache failed ({error}), trying database")
    return Success("data from database")

def fetch_from_api(error: str) -> Result[str, str]:
    print(f"Database failed ({error}), trying API")
    return Success("data from API")

# Try cache, fallback to database
result = fetch_from_cache("user:123").lash(fetch_from_database)
# Prints: Cache failed (Cache miss), trying database
# Success("data from database")

# Chain multiple fallbacks
result2 = (
    fetch_from_cache("user:456")
    .lash(lambda _: Failure("DB down"))
    .lash(fetch_from_api)
)
# Prints: Database failed (DB down), trying API
# Success("data from API")
```

**Example 2: Value Extraction**
```python
from returns.result import Success, Failure

# Get value or default
result1 = Success(42).value_or(0)       # 42
result2 = Failure("error").value_or(0)  # 0

# Unwrap (raises on Failure)
value = Success(100).unwrap()           # 100
# Failure("error").unwrap()             # Raises UnwrapFailedError

# Get failure value
error = Failure("oops").failure()       # "oops"
# Success(42).failure()                 # Raises UnwrapFailedError
```

**Example 3: Swapping Success and Failure**
```python
from returns.result import Success, Failure

# Swap success and failure
result1 = Success(42).swap()        # Failure(42)
result2 = Failure("error").swap()   # Success("error")

# Useful for inverting logic
def is_not_found(result: Result[str, str]) -> Result[str, str]:
    """Convert 'not found' errors into success."""
    return result.swap().map(lambda e: "Item does not exist")

original = Failure("Not found")
inverted = is_not_found(original)  # Success("Item does not exist")
```

### Result Pattern Matching

**Python 3.10+ Pattern Matching:**
```python
from returns.result import Result, Success, Failure

def handle_result(result: Result[int, str]) -> str:
    match result:
        case Success(value):
            return f"Success! Value is {value}"
        case Failure(error):
            return f"Failed with error: {error}"

print(handle_result(Success(42)))        # "Success! Value is 42"
print(handle_result(Failure("oops")))    # "Failed with error: oops"

# With guards and nested matching
def classify_result(result: Result[int, Exception]) -> str:
    match result:
        case Success(n) if n > 0:
            return "Positive success"
        case Success(n) if n < 0:
            return "Negative success"
        case Success(0):
            return "Zero success"
        case Failure(ValueError()):
            return "Value error occurred"
        case Failure(error):
            return f"Other error: {type(error).__name__}"
```

---

## Safe Decorator

The `@safe` decorator automatically converts exception-throwing functions into functions that return `Result` containers.

### Basic Safe Usage

**Example 1: Simple Conversion**
```python
from returns.result import safe

@safe
def divide(a: int, b: int) -> float:
    return a / b

result1 = divide(10, 2)   # Success(5.0)
result2 = divide(10, 0)   # Failure(ZeroDivisionError(...))
```

**Example 2: Working with Files**
```python
from returns.result import safe, ResultE
import json

@safe
def load_json(filename: str) -> dict:
    with open(filename, 'r') as f:
        return json.load(f)

config = load_json("config.json")
# Success({...}) if file exists and is valid JSON
# Failure(FileNotFoundError(...)) if file doesn't exist
# Failure(JSONDecodeError(...)) if invalid JSON

# Use the result
match config:
    case Success(data):
        print(f"Loaded {len(data)} config items")
    case Failure(error):
        print(f"Failed to load config: {error}")
```

**Example 3: Database Operations**
```python
from returns.result import safe, ResultE

@safe
def fetch_user(user_id: int) -> dict:
    # Simulated database call that might raise
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"User {user_id} not found")
    return dict(row)

user = fetch_user(123)
# Success({...}) if user exists
# Failure(ValueError(...)) if not found
# Failure(sqlite3.Error(...)) for DB errors
```

### Filtering Exceptions

**Example 1: Catching Specific Exceptions**
```python
from returns.result import safe

@safe(exceptions=(ValueError,))
def parse_positive_int(s: str) -> int:
    value = int(s)
    if value <= 0:
        raise ValueError("Must be positive")
    return value

result1 = parse_positive_int("42")    # Success(42)
result2 = parse_positive_int("-5")    # Failure(ValueError(...))
# parse_positive_int("abc")           # Raises TypeError (not caught)
```

**Example 2: Multiple Exception Types**
```python
from returns.result import safe

@safe(exceptions=(FileNotFoundError, PermissionError, json.JSONDecodeError))
def load_config(path: str) -> dict:
    import json
    with open(path, 'r') as f:
        return json.load(f)

config = load_config("settings.json")
# Catches FileNotFoundError, PermissionError, JSONDecodeError
# Other exceptions (like MemoryError) would propagate
```

**Example 3: Custom Exception Handling**
```python
from returns.result import safe

class ValidationError(Exception):
    pass

class BusinessError(Exception):
    pass

@safe(exceptions=(ValidationError, BusinessError))
def process_payment(amount: float, account: str) -> str:
    if amount <= 0:
        raise ValidationError("Amount must be positive")
    if not account.startswith("ACC"):
        raise ValidationError("Invalid account format")
    if amount > 10000:
        raise BusinessError("Amount exceeds limit")
    return f"Payment of ${amount} to {account} processed"

result1 = process_payment(100, "ACC123")     # Success(...)
result2 = process_payment(-50, "ACC123")     # Failure(ValidationError(...))
result3 = process_payment(20000, "ACC123")   # Failure(BusinessError(...))
```

### Composing Safe Functions

**Example 1: Chaining Safe Operations**
```python
from returns.result import safe

@safe
def fetch_user_id(email: str) -> int:
    users = {"alice@example.com": 1, "bob@example.com": 2}
    if email not in users:
        raise KeyError(f"User not found: {email}")
    return users[email]

@safe
def fetch_user_data(user_id: int) -> dict:
    data = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    if user_id not in data:
        raise ValueError(f"No data for user {user_id}")
    return data[user_id]

def get_user(email: str) -> Result[dict, Exception]:
    return fetch_user_id(email).bind(fetch_user_data)

result = get_user("alice@example.com")
# Success({"name": "Alice"})

result2 = get_user("unknown@example.com")
# Failure(KeyError("User not found: unknown@example.com"))
```

**Example 2: Pipeline with Safe Functions**
```python
from returns.result import safe
from returns.pipeline import flow

@safe
def parse_int(s: str) -> int:
    return int(s)

@safe
def validate_positive(n: int) -> int:
    if n <= 0:
        raise ValueError("Must be positive")
    return n

@safe
def calculate_square(n: int) -> int:
    return n * n

# This won't work directly with flow because safe returns Result
# Instead, use bind:
def process_number(s: str) -> Result[int, Exception]:
    return (
        parse_int(s)
        .bind(validate_positive)
        .bind(calculate_square)
    )

result1 = process_number("5")    # Success(25)
result2 = process_number("-3")   # Failure(ValueError(...))
result3 = process_number("abc")  # Failure(ValueError(...))
```

**Example 3: Combining Safe with Manual Result Creation**
```python
from returns.result import safe, Success, Failure, Result

@safe
def fetch_from_api(url: str) -> dict:
    import requests
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def validate_response(data: dict) -> Result[dict, str]:
    if 'id' not in data:
        return Failure("Response missing 'id' field")
    if 'name' not in data:
        return Failure("Response missing 'name' field")
    return Success(data)

def fetch_and_validate(url: str) -> Result[dict, str]:
    return (
        fetch_from_api(url)
        .alt(lambda e: f"API error: {str(e)}")  # Convert exception to string
        .bind(validate_response)
    )

result = fetch_and_validate("https://api.example.com/users/1")
# Success({...}) if API call succeeds and validation passes
# Failure("API error: ...") for network/HTTP errors
# Failure("Response missing...") for validation errors
```

---

## IO Container

The `IO` container marks functions that perform side effects, making impure operations explicit in your type signatures.

### Marking Impure Operations

**Example 1: Pure vs Impure Functions**
```python
# Pure function - always returns same output for same input
def add(a: int, b: int) -> int:
    return a + b

# Impure function - output varies or has side effects
from returns.io import IO, impure
import random

@impure
def get_random_number() -> int:
    return random.randint(1, 100)

# Type signature shows it's impure
result: IO[int] = get_random_number()
# Result is wrapped, must be unwrapped to use
```

**Example 2: Marking Side Effects**
```python
from returns.io import IO, impure

@impure
def log_message(message: str) -> None:
    print(f"[LOG] {message}")
    with open('app.log', 'a') as f:
        f.write(message + '\n')

@impure
def get_current_time() -> float:
    import time
    return time.time()

# These return IO containers
log_io: IO[None] = log_message("Application started")
time_io: IO[float] = get_current_time()
```

**Example 3: Database Operations**
```python
from returns.io import IO, impure

@impure
def fetch_users() -> list[dict]:
    import sqlite3
    conn = sqlite3.connect('app.db')
    cursor = conn.execute('SELECT * FROM users')
    return [dict(row) for row in cursor.fetchall()]

@impure
def save_user(user: dict) -> int:
    import sqlite3
    conn = sqlite3.connect('app.db')
    cursor = conn.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        (user['name'], user['email'])
    )
    conn.commit()
    return cursor.lastrowid

users_io: IO[list[dict]] = fetch_users()
save_io: IO[int] = save_user({"name": "Alice", "email": "alice@example.com"})
```

### Creating IO Instances

**Example 1: Using @impure Decorator**
```python
from returns.io import IO, impure

@impure
def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

@impure
def write_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

content_io = read_file('data.txt')
write_io = write_file('output.txt', 'Hello, World!')
```

**Example 2: Manual Construction with from_value**
```python
from returns.io import IO
import os

def get_environment() -> IO[dict]:
    return IO.from_value(dict(os.environ))

def get_working_directory() -> IO[str]:
    return IO.from_value(os.getcwd())

env_io = get_environment()
cwd_io = get_working_directory()

# Execute IO to get values
env = env_io.unwrap()
cwd = cwd_io.unwrap()
```

**Example 3: Lifting Pure Functions**
```python
from returns.io import IO

# Pure function
def calculate_total(items: list[float]) -> float:
    return sum(items)

# Lift to IO context (though this is unusual since it's pure)
def calculate_total_io(items: list[float]) -> IO[float]:
    return IO(calculate_total(items))

result = calculate_total_io([1.0, 2.0, 3.0])  # IO[float]
```

### Composing IO Operations

**Example 1: Mapping Pure Functions**
```python
from returns.io import IO, impure
import datetime

@impure
def get_current_timestamp() -> float:
    return datetime.datetime.now().timestamp()

# Map pure functions over IO
result = (
    get_current_timestamp()
    .map(lambda ts: datetime.datetime.fromtimestamp(ts))
    .map(lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'))
)

formatted_time = result.unwrap()  # "2024-01-15 10:30:45"
```

**Example 2: Binding IO Operations**
```python
from returns.io import IO, impure

@impure
def read_config_file() -> dict:
    import json
    with open('config.json', 'r') as f:
        return json.load(f)

@impure
def setup_database(config: dict) -> str:
    db_url = config.get('database_url', 'sqlite:///default.db')
    print(f"Setting up database: {db_url}")
    # Perform actual setup...
    return db_url

@impure
def run_migrations(db_url: str) -> int:
    print(f"Running migrations on {db_url}")
    # Run migrations...
    return 5  # Number of migrations run

# Compose IO operations
result = (
    read_config_file()
    .bind(setup_database)
    .bind(run_migrations)
)

migrations_count = result.unwrap()
```

**Example 3: Complex IO Pipeline**
```python
from returns.io import IO, impure
from typing import List

@impure
def list_files(directory: str) -> List[str]:
    import os
    return os.listdir(directory)

@impure
def filter_text_files(files: List[str]) -> List[str]:
    return [f for f in files if f.endswith('.txt')]

@impure
def read_all_files(filenames: List[str]) -> str:
    contents = []
    for filename in filenames:
        with open(filename, 'r') as f:
            contents.append(f.read())
    return '\n---\n'.join(contents)

# Pipeline
result = (
    list_files('./data')
    .map(filter_text_files)
    .bind(read_all_files)
)

all_content = result.unwrap()
```

### IO vs IOResult

**Example 1: IO for Never-Failing Operations**
```python
from returns.io import IO, impure
import random
import datetime

@impure
def get_random() -> int:
    """Never fails, just returns random number."""
    return random.randint(1, 100)

@impure
def get_timestamp() -> float:
    """Never fails, just returns current time."""
    return datetime.datetime.now().timestamp()

# These use IO because they can't fail
random_io: IO[int] = get_random()
time_io: IO[float] = get_timestamp()
```

**Example 2: IOResult for Operations That Can Fail**
```python
from returns.io import IOResult, impure_safe
from returns.result import Success, Failure

@impure_safe
def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

@impure_safe
def fetch_url(url: str) -> str:
    import requests
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# These return IOResult because they can fail
file_content: IOResult[str, Exception] = read_file('data.txt')
# Success(...) if file exists, Failure(FileNotFoundError(...)) otherwise

web_content: IOResult[str, Exception] = fetch_url('https://example.com')
# Success(...) if request succeeds, Failure(...) for network errors
```

**Example 3: Converting Between IO and IOResult**
```python
from returns.io import IO, IOResult, impure, impure_safe

@impure
def always_succeeds() -> int:
    return 42

@impure_safe
def might_fail() -> int:
    import random
    if random.random() < 0.5:
        raise ValueError("Random failure")
    return 100

# Convert IO to IOResult
io_value = always_succeeds()
io_result = IOResult.from_io(io_value)  # IOSuccess(42)

# IOResult is already the right type
io_result_value = might_fail()  # IOSuccess(100) or IOFailure(...)

# Use both in a pipeline
result = (
    io_result_value
    .map(lambda x: x * 2)
    .alt(lambda e: f"Error occurred: {e}")
)
```

---

## Future Container

The `Future` container enables composing async operations in a sync context while maintaining exception safety.

### Basic Future Usage

**Example 1: Creating Future from Async Function**
```python
from returns.future import Future, future
import asyncio

@future
async def fetch_data() -> dict:
    await asyncio.sleep(0.1)  # Simulate network delay
    return {"id": 1, "name": "Alice"}

@future
async def process_data(data: dict) -> str:
    await asyncio.sleep(0.05)
    return f"Processed: {data['name']}"

# These return Future containers
data_future: Future[dict] = fetch_data()
# Can compose without await
```

**Example 2: Running Futures**
```python
from returns.future import Future, future
import asyncio

@future
async def get_user(user_id: int) -> dict:
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": f"User{user_id}"}

# Create future
user_future = get_user(123)

# Execute it
async def main():
    io_result = await user_future.awaitable()
    user = io_result.unwrap()
    print(user)  # {"id": 123, "name": "User123"}

asyncio.run(main())
```

**Example 3: Mapping Over Futures**
```python
from returns.future import Future, future

@future
async def fetch_number() -> int:
    import asyncio
    await asyncio.sleep(0.1)
    return 42

# Map sync functions over async values
result = (
    fetch_number()
    .map(lambda x: x * 2)
    .map(lambda x: f"Result: {x}")
)

# Execute
async def main():
    io_value = await result.awaitable()
    print(io_value.unwrap())  # "Result: 84"

import asyncio
asyncio.run(main())
```

### FutureResult

**Example 1: Creating FutureResult**
```python
from returns.future import FutureResult, future_safe

@future_safe
async def fetch_user(user_id: int) -> dict:
    import asyncio
    await asyncio.sleep(0.1)

    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    if user_id not in users:
        raise ValueError(f"User {user_id} not found")
    return users[user_id]

# Returns FutureResult
user_future: FutureResult[dict, Exception] = fetch_user(1)
# Success path

error_future: FutureResult[dict, Exception] = fetch_user(999)
# Failure path
```

**Example 2: Handling Success and Failure**
```python
from returns.future import FutureResult, future_safe
import asyncio

@future_safe
async def divide_async(a: int, b: int) -> float:
    await asyncio.sleep(0.05)
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

async def main():
    # Success case
    result1 = await divide_async(10, 2).awaitable()
    match result1.unwrap():
        case Success(value):
            print(f"Success: {value}")  # Success: 5.0
        case Failure(error):
            print(f"Error: {error}")

    # Failure case
    result2 = await divide_async(10, 0).awaitable()
    match result2.unwrap():
        case Success(value):
            print(f"Success: {value}")
        case Failure(error):
            print(f"Error: {error}")  # Error: Cannot divide by zero

asyncio.run(main())
```

**Example 3: Converting Future to FutureResult**
```python
from returns.future import Future, FutureResult, future
from returns.result import Success

@future
async def get_data() -> int:
    import asyncio
    await asyncio.sleep(0.1)
    return 42

# Future[int] -> FutureResult[int, Exception]
future_result = get_data().map(Success)

# Now it's a FutureResult
async def main():
    io_result = await future_result.awaitable()
    result = io_result.unwrap()  # Success(42)
    print(result.unwrap())  # 42

import asyncio
asyncio.run(main())
```

### Composing Async Operations

**Example 1: Chaining Async Operations**
```python
from returns.future import FutureResult, future_safe
import asyncio

@future_safe
async def fetch_user_id(email: str) -> int:
    await asyncio.sleep(0.1)
    users = {"alice@example.com": 1, "bob@example.com": 2}
    if email not in users:
        raise KeyError(f"User not found: {email}")
    return users[email]

@future_safe
async def fetch_user_profile(user_id: int) -> dict:
    await asyncio.sleep(0.1)
    profiles = {1: {"name": "Alice", "age": 30}, 2: {"name": "Bob", "age": 25}}
    if user_id not in profiles:
        raise ValueError(f"Profile not found for user {user_id}")
    return profiles[user_id]

@future_safe
async def format_profile(profile: dict) -> str:
    await asyncio.sleep(0.05)
    return f"{profile['name']} ({profile['age']} years old)"

# Compose async operations
async def get_formatted_profile(email: str) -> IOResult[str, Exception]:
    return await (
        fetch_user_id(email)
        .bind(fetch_user_profile)
        .bind(format_profile)
        .awaitable()
    )

async def main():
    result = await get_formatted_profile("alice@example.com")
    print(result.unwrap())  # "Alice (30 years old)"

asyncio.run(main())
```

**Example 2: Parallel Future Execution**
```python
from returns.future import FutureResult, future_safe
import asyncio

@future_safe
async def fetch_weather(city: str) -> dict:
    await asyncio.sleep(0.2)
    return {"city": city, "temp": 72, "conditions": "Sunny"}

@future_safe
async def fetch_news(city: str) -> list:
    await asyncio.sleep(0.15)
    return [f"News 1 for {city}", f"News 2 for {city}"]

@future_safe
async def fetch_events(city: str) -> list:
    await asyncio.sleep(0.1)
    return [f"Event 1 in {city}", f"Event 2 in {city}"]

async def fetch_city_data(city: str) -> dict:
    # Launch all fetches in parallel
    weather_future = fetch_weather(city).awaitable()
    news_future = fetch_news(city).awaitable()
    events_future = fetch_events(city).awaitable()

    # Wait for all
    weather, news, events = await asyncio.gather(
        weather_future,
        news_future,
        events_future
    )

    return {
        "weather": weather.unwrap().unwrap(),
        "news": news.unwrap().unwrap(),
        "events": events.unwrap().unwrap()
    }

async def main():
    data = await fetch_city_data("San Francisco")
    print(data)

asyncio.run(main())
```

**Example 3: Mixing Sync and Async**
```python
from returns.future import FutureResult, future_safe, asyncify
import asyncio

# Sync function
def validate_email(email: str) -> str:
    if '@' not in email:
        raise ValueError("Invalid email")
    return email

# Async function
@future_safe
async def send_email(email: str) -> str:
    await asyncio.sleep(0.1)
    return f"Email sent to {email}"

# Compose sync and async
async def process_email(email: str) -> IOResult[str, Exception]:
    # Need to lift sync validation into Future context
    validated = FutureResult.from_result(
        safe(validate_email)(email)
    )

    return await validated.bind(send_email).awaitable()

async def main():
    result = await process_email("user@example.com")
    print(result.unwrap().unwrap())  # "Email sent to user@example.com"

asyncio.run(main())
```

---

## future_safe Decorator

The `@future_safe` decorator converts async exception-throwing functions into functions returning `FutureResult`.

### Basic future_safe Usage

**Example 1: Converting Async Functions**
```python
from returns.future import future_safe, FutureResult
import asyncio

@future_safe
async def fetch_data(url: str) -> dict:
    await asyncio.sleep(0.1)
    if not url.startswith('https://'):
        raise ValueError("URL must use HTTPS")
    return {"url": url, "data": "..."}

# Returns FutureResult
result: FutureResult[dict, Exception] = fetch_data("https://example.com")
error: FutureResult[dict, Exception] = fetch_data("http://example.com")

async def main():
    success = await result.awaitable()
    print(success.unwrap())  # Success({"url": ..., "data": "..."})

    failure = await error.awaitable()
    print(failure.unwrap())  # Failure(ValueError("URL must use HTTPS"))

asyncio.run(main())
```

**Example 2: API Calls with Error Handling**
```python
from returns.future import future_safe
import asyncio
import aiohttp

@future_safe
async def fetch_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

async def main():
    # Success case
    result1 = await fetch_json("https://api.github.com/users/github").awaitable()
    match result1.unwrap():
        case Success(data):
            print(f"Got user: {data.get('login')}")
        case Failure(error):
            print(f"Error: {error}")

    # Failure case (404)
    result2 = await fetch_json("https://api.github.com/users/nonexistent999").awaitable()
    match result2.unwrap():
        case Success(data):
            print(f"Got user: {data.get('login')}")
        case Failure(error):
            print(f"Error: {error}")

# asyncio.run(main())  # Uncomment to run
```

**Example 3: Database Operations**
```python
from returns.future import future_safe, FutureResult
import asyncio
import asyncpg

@future_safe
async def fetch_users(conn_string: str) -> list[dict]:
    conn = await asyncpg.connect(conn_string)
    try:
        rows = await conn.fetch('SELECT * FROM users')
        return [dict(row) for row in rows]
    finally:
        await conn.close()

@future_safe
async def create_user(conn_string: str, name: str, email: str) -> int:
    conn = await asyncpg.connect(conn_string)
    try:
        user_id = await conn.fetchval(
            'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id',
            name, email
        )
        return user_id
    finally:
        await conn.close()

# Both return FutureResult and handle exceptions automatically
```

### Error Handling in Async Code

**Example 1: Fallback Chains**
```python
from returns.future import future_safe
import asyncio

@future_safe
async def fetch_from_primary(key: str) -> str:
    await asyncio.sleep(0.1)
    raise ConnectionError("Primary server down")

@future_safe
async def fetch_from_secondary(key: str) -> str:
    await asyncio.sleep(0.1)
    raise ConnectionError("Secondary server down")

@future_safe
async def fetch_from_cache(key: str) -> str:
    await asyncio.sleep(0.05)
    return f"Cached value for {key}"

async def fetch_with_fallback(key: str):
    return await (
        fetch_from_primary(key)
        .lash(lambda _: fetch_from_secondary(key))
        .lash(lambda _: fetch_from_cache(key))
        .awaitable()
    )

async def main():
    result = await fetch_with_fallback("user:123")
    print(result.unwrap())  # Success("Cached value for user:123")

asyncio.run(main())
```

**Example 2: Error Transformation**
```python
from returns.future import future_safe
import asyncio

class APIError(Exception):
    pass

@future_safe
async def call_external_api(endpoint: str) -> dict:
    await asyncio.sleep(0.1)
    raise ConnectionError("Network error")

async def call_api_with_friendly_errors(endpoint: str):
    return await (
        call_external_api(endpoint)
        .alt(lambda e: APIError(f"Failed to call {endpoint}: {str(e)}"))
        .awaitable()
    )

async def main():
    result = await call_api_with_friendly_errors("/users")
    match result.unwrap():
        case Failure(APIError() as error):
            print(f"API Error: {error}")
        case Failure(error):
            print(f"Other error: {error}")
        case Success(data):
            print(f"Success: {data}")

asyncio.run(main())
```

**Example 3: Retry Logic**
```python
from returns.future import future_safe, FutureResult
from returns.result import Success, Failure
import asyncio

@future_safe
async def unreliable_operation() -> str:
    import random
    await asyncio.sleep(0.1)
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Random failure")
    return "Success!"

async def retry_operation(max_retries: int = 3) -> IOResult[str, Exception]:
    for attempt in range(max_retries):
        result = await unreliable_operation().awaitable()
        inner_result = result.unwrap()

        match inner_result:
            case Success(value):
                return result
            case Failure(error):
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.5)
                else:
                    print(f"All {max_retries} attempts failed")
                    return result

async def main():
    result = await retry_operation(max_retries=3)
    print(result.unwrap())

asyncio.run(main())
```

---

## Context Container

The `Context` module provides dependency injection through `RequiresContext` and related containers.

### RequiresContext Basics

**Example 1: Simple Context Usage**
```python
from returns.context import RequiresContext

# Function that requires config
def get_database_url() -> RequiresContext[str, dict]:
    return RequiresContext(lambda config: config['database_url'])

def get_api_key() -> RequiresContext[str, dict]:
    return RequiresContext(lambda config: config['api_key'])

# Provide context
config = {
    'database_url': 'postgres://localhost/mydb',
    'api_key': 'secret123'
}

db_url = get_database_url()(config)  # "postgres://localhost/mydb"
api_key = get_api_key()(config)      # "secret123"
```

**Example 2: Using .ask() Method**
```python
from returns.context import RequiresContext

def create_connection_string() -> RequiresContext[str, dict]:
    # Access context with .ask()
    return RequiresContext.ask().map(
        lambda config: f"{config['db_type']}://{config['db_host']}/{config['db_name']}"
    )

config = {
    'db_type': 'postgresql',
    'db_host': 'localhost',
    'db_name': 'app_db'
}

conn_string = create_connection_string()(config)
# "postgresql://localhost/app_db"
```

**Example 3: Nested Context Access**
```python
from returns.context import RequiresContext

class AppConfig:
    def __init__(self, db_host: str, db_port: int, debug: bool):
        self.db_host = db_host
        self.db_port = db_port
        self.debug = debug

def get_db_connection() -> RequiresContext[str, AppConfig]:
    return RequiresContext.ask().map(
        lambda config: f"{config.db_host}:{config.db_port}"
    )

def should_log_queries() -> RequiresContext[bool, AppConfig]:
    return RequiresContext.ask().map(lambda config: config.debug)

# Provide context
app_config = AppConfig(db_host="localhost", db_port=5432, debug=True)

db_conn = get_db_connection()(app_config)      # "localhost:5432"
should_log = should_log_queries()(app_config)  # True
```

### Dependency Injection

**Example 1: Service Layer with DI**
```python
from returns.context import RequiresContext
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    cache_enabled: bool
    timeout: int
    api_url: str

class UserService:
    @staticmethod
    def fetch_user(user_id: int) -> RequiresContext[dict, ServiceConfig]:
        def _fetch(config: ServiceConfig) -> dict:
            # Use config values
            print(f"Fetching from {config.api_url} with timeout {config.timeout}")
            return {"id": user_id, "name": f"User{user_id}"}
        return RequiresContext(_fetch)

    @staticmethod
    def should_cache() -> RequiresContext[bool, ServiceConfig]:
        return RequiresContext.ask().map(lambda config: config.cache_enabled)

# Usage
config = ServiceConfig(cache_enabled=True, timeout=30, api_url="https://api.example.com")

user = UserService.fetch_user(123)(config)
cache_enabled = UserService.should_cache()(config)
```

**Example 2: Multi-Layer Application**
```python
from returns.context import RequiresContext
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str) -> list[dict]: ...

class Logger(Protocol):
    def log(self, message: str) -> None: ...

@dataclass
class Dependencies:
    db: Database
    logger: Logger
    max_retries: int

def fetch_users() -> RequiresContext[list[dict], Dependencies]:
    def _fetch(deps: Dependencies) -> list[dict]:
        deps.logger.log("Fetching users")
        return deps.db.query("SELECT * FROM users")
    return RequiresContext(_fetch)

def process_users(users: list[dict]) -> RequiresContext[int, Dependencies]:
    def _process(deps: Dependencies) -> int:
        deps.logger.log(f"Processing {len(users)} users")
        # Process users...
        return len(users)
    return RequiresContext(_process)

# Wire it together
def get_user_count() -> RequiresContext[int, Dependencies]:
    return fetch_users().bind(process_users)

# Provide dependencies at the edge
# deps = Dependencies(db=my_db, logger=my_logger, max_retries=3)
# count = get_user_count()(deps)
```

**Example 3: Testing with Different Contexts**
```python
from returns.context import RequiresContext

def send_email(to: str, subject: str) -> RequiresContext[bool, dict]:
    return RequiresContext.ask().map(
        lambda config: _send_via_smtp(to, subject, config['smtp_server'])
        if config.get('email_enabled', False)
        else _log_email(to, subject)
    )

def _send_via_smtp(to: str, subject: str, server: str) -> bool:
    print(f"Sending email to {to} via {server}")
    return True

def _log_email(to: str, subject: str) -> bool:
    print(f"[MOCK] Would send email to {to}: {subject}")
    return True

# Production config
prod_config = {'email_enabled': True, 'smtp_server': 'smtp.gmail.com'}
send_email("user@example.com", "Hello")(prod_config)
# Prints: Sending email to user@example.com via smtp.gmail.com

# Test config
test_config = {'email_enabled': False}
send_email("user@example.com", "Hello")(test_config)
# Prints: [MOCK] Would send email to user@example.com: Hello
```

### Composing with Context

**Example 1: Mapping and Binding**
```python
from returns.context import RequiresContext

def get_timeout() -> RequiresContext[int, dict]:
    return RequiresContext.ask().map(lambda config: config.get('timeout', 30))

def get_timeout_message() -> RequiresContext[str, dict]:
    return get_timeout().map(lambda t: f"Timeout is {t} seconds")

def validate_timeout() -> RequiresContext[bool, dict]:
    return get_timeout().map(lambda t: 0 < t < 3600)

config = {'timeout': 60}

message = get_timeout_message()(config)  # "Timeout is 60 seconds"
is_valid = validate_timeout()(config)    # True
```

**Example 2: Chaining Context-Dependent Operations**
```python
from returns.context import RequiresContext

def get_user_id() -> RequiresContext[int, dict]:
    return RequiresContext.ask().map(lambda ctx: ctx['current_user_id'])

def fetch_user(user_id: int) -> RequiresContext[dict, dict]:
    def _fetch(ctx: dict) -> dict:
        # Could use database from context
        db = ctx.get('database')
        return {'id': user_id, 'name': f'User{user_id}'}
    return RequiresContext(_fetch)

def get_permissions(user: dict) -> RequiresContext[list[str], dict]:
    def _get_perms(ctx: dict) -> list[str]:
        # Use role system from context
        if user['id'] == 1:
            return ['admin', 'read', 'write']
        return ['read']
    return RequiresContext(_get_perms)

# Chain operations
def get_current_user_permissions() -> RequiresContext[list[str], dict]:
    return get_user_id().bind(fetch_user).bind(get_permissions)

context = {'current_user_id': 1, 'database': None}
perms = get_current_user_permissions()(context)  # ['admin', 'read', 'write']
```

**Example 3: Modifying Environment**
```python
from returns.context import RequiresContext

def get_base_url() -> RequiresContext[str, dict]:
    return RequiresContext.ask().map(lambda config: config['base_url'])

def add_api_prefix(url: str) -> str:
    return f"{url}/api/v1"

# Modify environment type
def get_api_url() -> RequiresContext[str, dict]:
    return get_base_url().map(add_api_prefix)

# Transform context before passing
def use_with_modified_context() -> str:
    original_context = {'base_url': 'https://example.com'}

    # Could modify context here
    modified_context = {**original_context, 'base_url': 'https://api.example.com'}

    return get_api_url()(modified_context)

result = use_with_modified_context()  # "https://api.example.com/api/v1"
```

---

## Pipelines

The `returns` library provides powerful pipeline composition tools for chaining operations.

### flow() Function

The `flow()` function composes a value with multiple functions sequentially.

**Example 1: Basic Flow**
```python
from returns.pipeline import flow

# Simple data transformation
result = flow(
    '42',
    int,
    lambda x: x * 2,
    float,
    str
)
print(result)  # '84.0'

# More practical example
def normalize(s: str) -> str:
    return s.strip().lower()

def remove_spaces(s: str) -> str:
    return s.replace(' ', '')

def add_prefix(s: str) -> str:
    return f"user_{s}"

username = flow(
    '  John Doe  ',
    normalize,
    remove_spaces,
    add_prefix
)
print(username)  # 'user_johndoe'
```

**Example 2: Data Processing Pipeline**
```python
from returns.pipeline import flow
from typing import List

def parse_csv_line(line: str) -> List[str]:
    return line.split(',')

def strip_fields(fields: List[str]) -> List[str]:
    return [f.strip() for f in fields]

def validate_fields(fields: List[str]) -> List[str]:
    if len(fields) < 3:
        raise ValueError("Not enough fields")
    return fields

def create_record(fields: List[str]) -> dict:
    return {
        'name': fields[0],
        'email': fields[1],
        'age': int(fields[2])
    }

csv_line = 'Alice, alice@example.com, 30'
record = flow(
    csv_line,
    parse_csv_line,
    strip_fields,
    validate_fields,
    create_record
)
print(record)  # {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
```

**Example 3: Complex Business Logic**
```python
from returns.pipeline import flow
from decimal import Decimal

def parse_price(s: str) -> Decimal:
    return Decimal(s.replace('$', '').replace(',', ''))

def apply_discount(price: Decimal) -> Decimal:
    return price * Decimal('0.9')  # 10% discount

def add_tax(price: Decimal) -> Decimal:
    return price * Decimal('1.08')  # 8% tax

def round_price(price: Decimal) -> Decimal:
    return price.quantize(Decimal('0.01'))

def format_price(price: Decimal) -> str:
    return f'${price:,.2f}'

final_price = flow(
    '$1,234.56',
    parse_price,
    apply_discount,
    add_tax,
    round_price,
    format_price
)
print(final_price)  # '$1,199.47'
```

### pipe() Function

The `pipe()` function creates a reusable pipeline without an initial value.

**Example 1: Reusable Pipeline**
```python
from returns.pipeline import pipe

# Create reusable transformation
process_name = pipe(
    str.strip,
    str.lower,
    lambda s: s.replace(' ', '_')
)

# Use it multiple times
name1 = process_name('  John Doe  ')    # 'john_doe'
name2 = process_name('Jane Smith')      # 'jane_smith'
name3 = process_name('  Bob  Jones  ')  # 'bob_jones'

print(name1, name2, name3)
```

**Example 2: Data Validation Pipeline**
```python
from returns.pipeline import pipe

def validate_length(s: str) -> str:
    if len(s) < 3:
        raise ValueError("Too short")
    return s

def validate_chars(s: str) -> str:
    if not s.isalnum():
        raise ValueError("Must be alphanumeric")
    return s

def validate_not_empty(s: str) -> str:
    if not s:
        raise ValueError("Cannot be empty")
    return s

# Create validator pipeline
validate_username = pipe(
    str.strip,
    validate_not_empty,
    validate_length,
    validate_chars,
    str.lower
)

# Use it
try:
    username = validate_username('  Alice123  ')
    print(username)  # 'alice123'
except ValueError as e:
    print(f"Validation failed: {e}")

try:
    invalid = validate_username('ab')
except ValueError as e:
    print(f"Validation failed: {e}")  # "Validation failed: Too short"
```

**Example 3: Number Processing**
```python
from returns.pipeline import pipe

# Create pipeline for number processing
process_number = pipe(
    float,
    lambda x: x ** 2,
    lambda x: x + 10,
    int
)

result1 = process_number('5')   # int((5.0 ** 2) + 10) = 35
result2 = process_number('3')   # int((3.0 ** 2) + 10) = 19

print(result1, result2)  # 35 19

# Create another pipeline
calculate_discount = pipe(
    float,
    lambda x: x * 0.8,  # 20% discount
    lambda x: round(x, 2)
)

price1 = calculate_discount('100')  # 80.0
price2 = calculate_discount('50.5') # 40.4

print(price1, price2)
```

### managed() Function

The `managed()` function handles resource lifecycle management.

**Example 1: File Resource Management**
```python
from returns.pipeline import managed
from returns.io import IOResult, impure_safe

@impure_safe
def open_file(path: str):
    return open(path, 'r')

def use_file(file):
    return IOResult.from_value(file.read())

def close_file(file, _):
    file.close()
    return IOResult.from_value(None)

# Managed resource
# result = managed(
#     open_file('data.txt'),
#     use_file,
#     close_file
# )
# File is automatically closed even if error occurs
```

**Example 2: Database Connection**
```python
from returns.pipeline import managed
from returns.io import IOResult

class DatabaseConnection:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        print(f"Opening connection to {conn_string}")

    def execute(self, query: str):
        print(f"Executing: {query}")
        return [{'id': 1, 'name': 'Alice'}]

    def close(self):
        print("Closing connection")

def acquire_connection():
    return IOResult.from_value(DatabaseConnection('postgres://localhost/db'))

def use_connection(conn):
    result = conn.execute('SELECT * FROM users')
    return IOResult.from_value(result)

def release_connection(conn, _):
    conn.close()
    return IOResult.from_value(None)

# Managed database connection
# result = managed(
#     acquire_connection(),
#     use_connection,
#     release_connection
# )
# Connection is automatically closed
```

**Example 3: Multiple Resources**
```python
from returns.pipeline import managed
from returns.io import IOResult
from contextlib import contextmanager

@contextmanager
def managed_resources():
    # Acquire resources
    file1 = open('data1.txt', 'r')
    file2 = open('data2.txt', 'r')

    try:
        yield (file1, file2)
    finally:
        # Release resources
        file1.close()
        file2.close()

# Use with managed
def acquire():
    return IOResult.from_value(managed_resources().__enter__())

def use_resources(resources):
    file1, file2 = resources
    content1 = file1.read()
    content2 = file2.read()
    return IOResult.from_value(content1 + content2)

def release(resources, _):
    try:
        managed_resources().__exit__(None, None, None)
    except:
        pass
    return IOResult.from_value(None)

# Both files are properly closed
# result = managed(acquire(), use_resources, release)
```

---

## Conclusion

This guide covered the fundamental types and containers in the `returns` library:

- **Maybe**: Safe handling of optional values
- **Result**: Explicit error handling without exceptions
- **Safe decorator**: Converting exception-throwing functions to Results
- **IO**: Marking and composing impure operations
- **Future/FutureResult**: Async operations with exception safety
- **future_safe decorator**: Converting async functions to FutureResults
- **Context**: Dependency injection with RequiresContext
- **Pipelines**: Composing operations with flow, pipe, and managed

**Next Steps**: See Part 2 for methods, converters, helper functions, and advanced primitive types.

**Resources**:
- [Official Documentation](https://returns.readthedocs.io/)
- [GitHub Repository](https://github.com/dry-python/returns)
