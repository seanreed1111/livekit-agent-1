# Python Match Statement Reference Guide

Comprehensive guide to Python's structural pattern matching (Python 3.10+) with correct and incorrect usage examples.

## Table of Contents
1. [Basic Syntax](#basic-syntax)
2. [Pattern Types](#pattern-types)
3. [Common Pitfalls](#common-pitfalls)
4. [Best Practices](#best-practices)
5. [Advanced Examples](#advanced-examples)

---

## Basic Syntax

### Correct Usage

```python
def http_error(status):
    match status:
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"
        case _:
            return "Something's wrong with the internet"
```

### Execution Flow

1. Subject expression is evaluated once
2. Each pattern is tried in order until one matches
3. If a pattern matches, its guard (if present) is evaluated
4. If guard is true or absent, the corresponding block executes
5. Name bindings from successful patterns persist after the match statement
6. Only the first matching case executes (no fall-through)

---

## Pattern Types

### 1. Literal Patterns

Match specific values using `==` comparison (except `None`, `True`, `False` which use `is`).

#### Correct Usage
```python
match value:
    case 42:
        print("The answer")
    case "hello":
        print("Greeting")
    case None:
        print("Nothing")
    case True:
        print("Truthy")
    case 3.14:
        print("Approximately pi")
    case 3 + 4j:
        print("Complex number")
```

#### Incorrect Usage
```python
# WRONG: Cannot use f-strings in patterns
match value:
    case f"{x}":  # SyntaxError
        pass

# WRONG: Variables are capture patterns, not literal comparisons
expected_value = 42
match value:
    case expected_value:  # This CAPTURES value, doesn't compare!
        print("This always matches and binds expected_value")
```

**Fix:** Use dotted names for constants or value patterns
```python
# CORRECT: Use dotted name for constant
import math
match value:
    case math.pi:  # Value pattern - compares to math.pi
        print("Matched pi")

# CORRECT: Use class attribute
class Constants:
    EXPECTED = 42

match value:
    case Constants.EXPECTED:  # Value pattern
        print("Matched expected value")
```

---

### 2. Capture Patterns

Always succeed and bind the subject to a name.

#### Correct Usage
```python
match value:
    case x:  # Captures any value
        print(f"Captured: {x}")

match point:
    case (x, y):  # Captures both elements
        print(f"X={x}, Y={y}")
```

#### Incorrect Usage
```python
# WRONG: Cannot bind same name twice
match point:
    case (x, x):  # SyntaxError: multiple assignments to name 'x' in pattern
        pass

# WRONG: Using _ as a capture pattern (it's a wildcard)
match value:
    case _:  # This is a wildcard, NOT a capture
        print(_)  # NameError: _ is not bound
```

---

### 3. Wildcard Pattern

The `_` pattern matches anything without binding a variable.

#### Correct Usage
```python
match value:
    case 1 | 2 | 3:
        print("Small number")
    case _:  # Catch-all
        print("Something else")

match point:
    case (0, _):  # Match x=0, ignore y
        print("On Y-axis")
```

#### Incorrect Usage
```python
# WRONG: Trying to use _ value
match value:
    case _:
        print(_)  # NameError: name '_' is not defined
```

---

### 4. OR Patterns

Combine multiple patterns with `|`.

#### Correct Usage
```python
match status:
    case 401 | 403 | 404:
        return "Not allowed"

match value:
    case int() | float():
        return "Number"

match point:
    case (0, y) | (y, 0):  # All branches bind 'y'
        print(f"On axis, non-zero coord: {y}")
```

#### Incorrect Usage
```python
# WRONG: OR patterns must bind same names
match point:
    case (x, 0) | (0, y):  # Error: 'x' not in both branches
        print(x)  # Which variable is bound?

# WRONG: Mixing incompatible patterns
match value:
    case 1 | "one":  # Works, but likely logic error
        pass  # Which type is value?
```

**Fix:** Ensure consistent bindings
```python
# CORRECT: All branches bind same variables
match point:
    case (x, 0) | (0, x):  # Both bind 'x'
        print(f"On axis: {x}")

# CORRECT: Use separate cases for different types
match value:
    case 1:
        handle_int(value)
    case "one":
        handle_string(value)
```

---

### 5. AS Patterns

Match a pattern and bind the entire subject.

#### Correct Usage
```python
match point:
    case (x, y) as p:
        print(f"Point {p} has coords {x}, {y}")

match value:
    case (1 | 2 | 3) as small:
        print(f"Small number: {small}")

match data:
    case {"name": str(n), **rest} as full:
        print(f"Full record: {full}, Name: {n}")
```

#### Incorrect Usage
```python
# WRONG: AS must be last in the pattern
match value:
    case (as x) | 5:  # SyntaxError
        pass
```

---

### 6. Sequence Patterns

Match lists, tuples, and other sequences.

#### Correct Usage
```python
# Fixed-length matching
match point:
    case [x, y]:
        print(f"2D point: {x}, {y}")
    case [x, y, z]:
        print(f"3D point: {x}, {y}, {z}")

# Variable-length with star pattern
match command:
    case ["load", filename]:
        load_file(filename)
    case ["save", filename, *options]:
        save_file(filename, options)
    case [*all_items]:
        process_all(all_items)

# Tuple patterns (parentheses)
match coords:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On X-axis at {x}")
```

#### Incorrect Usage
```python
# WRONG: Strings are not matched by sequence patterns
match value:
    case ["h", "e", "l", "l", "o"]:  # Only matches list, not "hello" string
        pass

# WRONG: Multiple star patterns
match items:
    case [*start, *end]:  # SyntaxError: multiple starred expressions
        pass

# WRONG: Star pattern must capture to a name
match items:
    case [first, *]:  # SyntaxError: starred assignment must be to a name
        pass
```

**Fix:** Use single star pattern with name
```python
# CORRECT: Single star pattern
match items:
    case [first, *rest]:
        print(f"First: {first}, Rest: {rest}")
    case [*init, last]:
        print(f"Last: {last}, Init: {init}")
    case [first, *middle, last]:
        print(f"First: {first}, Middle: {middle}, Last: {last}")
```

---

### 7. Mapping Patterns

Match dictionaries and other mappings.

#### Correct Usage
```python
match config:
    case {"host": host, "port": port}:
        connect(host, port)
    case {"host": host}:  # Extra keys OK
        connect(host, 8080)
    case {"type": "server", "port": p, **rest}:
        setup_server(p, rest)

# Nested patterns
match response:
    case {"status": 200, "data": {"name": n, "age": a}}:
        print(f"{n} is {a} years old")
```

#### Incorrect Usage
```python
# WRONG: Multiple ** patterns
match data:
    case {"a": 1, **rest1, **rest2}:  # SyntaxError
        pass

# WRONG: ** pattern must be last
match data:
    case {**rest, "key": value}:  # SyntaxError
        pass

# WRONG: Non-literal keys (without value pattern)
match data:
    case {some_var: value}:  # SyntaxError - bare name not allowed as key
        pass
```

**Fix:** Use literal or value patterns for keys
```python
# CORRECT: Literal keys
match data:
    case {"name": n, "age": a, **rest}:
        print(f"{n}, {a}, extras: {rest}")

# CORRECT: Value pattern (dotted name) as key
class Keys:
    NAME = "name"

match data:
    case {Keys.NAME: n}:  # Value pattern as key
        print(n)
```

---

### 8. Class Patterns

Match class instances with attribute checking.

#### Correct Usage
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# Keyword matching
match point:
    case Point(x=0, y=0):
        print("Origin")
    case Point(x=0, y=y):
        print(f"On Y-axis at {y}")

# Positional matching with __match_args__
@dataclass
class Point2D:
    x: float
    y: float
    __match_args__ = ("x", "y")

match point:
    case Point2D(0, 0):  # Equivalent to Point2D(x=0, y=0)
        print("Origin")
    case Point2D(0, y):
        print(f"Y={y}")
    case Point2D(x, y):
        print(f"Point at {x}, {y}")

# Type checking
match value:
    case int():
        print("It's an integer")
    case str():
        print("It's a string")
```

#### Incorrect Usage
```python
# WRONG: Using class name as bare identifier
class Point:
    x: int
    y: int

match point:
    case Point:  # This is a CAPTURE pattern, not isinstance check!
        print("This binds Point to the value!")

# WRONG: Positional args without __match_args__
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

match Point(1, 2):
    case Point(0, y):  # TypeError: Point() accepts 0 positional sub-patterns
        print(y)

# WRONG: Type checking without parentheses
match value:
    case int:  # CAPTURE pattern, not type check!
        print(int)  # This rebinds the int builtin!

# WRONG: Too many positional arguments
match value:
    case int(x, y):  # int() accepts at most 1 positional argument
        pass
```

**Fix:** Use correct syntax
```python
# CORRECT: Use isinstance in guard or use class pattern with parens
match point:
    case p if isinstance(p, Point):
        print("It's a Point instance")
    case Point():  # With parens - matches any Point instance
        print("It's a Point")

# CORRECT: Define __match_args__ for positional matching
class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

match Point(1, 2):
    case Point(0, y):  # Now works!
        print(f"On Y-axis at {y}")

# CORRECT: Type checking with parentheses
match value:
    case int():  # Correct type check
        print("It's an integer")

# CORRECT: Single positional for built-in types
match value:
    case int(0 | 1):  # Matches 0 or 1
        print("Boolean-like")
```

---

### 9. Guards

Add conditional logic with `if` clause after pattern.

#### Correct Usage
```python
match point:
    case (x, y) if x == y:
        print("On diagonal")
    case (x, y) if x > 0 and y > 0:
        print("First quadrant")
    case (x, y):
        print("Somewhere else")

# Guard evaluated only after pattern matches
match value:
    case x if x > 0 and expensive_check(x):
        print("Passed expensive check")

# Guards can access bound variables
match data:
    case {"user": u, "score": s} if u in approved_users:
        grant_access(u, s)
```

#### Incorrect Usage
```python
# WRONG: Guard must be after pattern
match value:
    case if x > 0:  # SyntaxError
        pass

# WRONG: Guard exceptions bubble up
match value:
    case x if risky_function(x):  # If raises, whole match fails
        pass

# WRONG: Side effects in guards can be confusing
counter = 0
match value:
    case x if (counter := counter + 1) and x > 0:  # Runs even if x <= 0!
        pass
    case y if (counter := counter + 1) and y < 0:  # Counter increments multiple times
        pass
```

**Best Practice:** Keep guards pure and simple
```python
# GOOD: Simple, clear guard
match value:
    case x if x > 0:
        process_positive(x)
    case x if x < 0:
        process_negative(x)
    case 0:
        process_zero()
```

---

## Common Pitfalls

### 1. Variable Shadowing

```python
# PITFALL: Variables shadow outer scope
x = 10
match value:
    case x:  # This CAPTURES, doesn't compare to outer x!
        print(x)  # Prints value, not 10
print(x)  # x is now rebound to value!
```

**Fix:** Use dotted name or class attribute
```python
# CORRECT: Use a class for constants
class Expected:
    X = 10

match value:
    case Expected.X:  # Value pattern - compares
        print("Matched!")
```

### 2. Order Matters

```python
# WRONG: Unreachable case
match value:
    case x:  # Matches everything!
        print("Caught by capture")
    case 42:  # NEVER REACHED
        print("Never printed")

# WRONG: Specific after general
match point:
    case (x, y):  # Matches all 2-tuples
        print("Any point")
    case (0, 0):  # NEVER REACHED
        print("Origin")
```

**Fix:** Order from specific to general
```python
# CORRECT: Specific cases first
match value:
    case 42:
        print("The answer")
    case x:
        print(f"Something else: {x}")

match point:
    case (0, 0):
        print("Origin")
    case (x, y):
        print("Any point")
```

### 3. Type Checking Confusion

```python
# WRONG: Bare type name is capture, not type check
match value:
    case int:  # CAPTURES value into variable named 'int'!
        print(int)  # Shadows built-in int!

# WRONG: isinstance() in pattern
match value:
    case isinstance(value, int):  # SyntaxError
        pass
```

**Fix:** Use parentheses for type checking
```python
# CORRECT: Parentheses for type checking
match value:
    case int():
        print("It's an integer")
    case str():
        print("It's a string")
    case _:
        print("Something else")
```

### 4. Missing Default Case

```python
# RISKY: No catch-all
match status:
    case 200:
        return "OK"
    case 404:
        return "Not found"
    # What if status is 500?
```

**Fix:** Always include default case for robustness
```python
# CORRECT: Explicit default
match status:
    case 200:
        return "OK"
    case 404:
        return "Not found"
    case _:
        return "Unknown status"
```

### 5. String Matching

```python
# WRONG: Sequence pattern doesn't match strings
match value:
    case ['h', 'i']:  # Only matches list ['h', 'i'], not string "hi"
        print("Never matches string")
```

**Fix:** Use literal pattern for strings
```python
# CORRECT: String literal
match value:
    case "hi":
        print("Matched string")
    case ['h', 'i']:
        print("Matched list")
```

---

## Best Practices

### 1. Use Specific Patterns First

```python
# GOOD: Specific to general
match data:
    case {"type": "error", "code": 404}:
        handle_not_found()
    case {"type": "error", "code": c}:
        handle_error(c)
    case {"type": "success", "data": d}:
        handle_success(d)
    case _:
        handle_unknown()
```

### 2. Leverage Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Command:
    action: str
    target: str
    options: dict = None

# Clean, readable matching
match cmd:
    case Command(action="move", target=t):
        move_to(t)
    case Command(action="attack", target=t, options={"weapon": w}):
        attack(t, weapon=w)
```

### 3. Use Guards Sparingly

```python
# GOOD: Guard for complex conditions
match point:
    case (x, y) if is_valid_coordinate(x, y):
        process(x, y)

# AVOID: Simple conditions in guards
match value:
    case x if x > 0:  # Consider restructuring
        pass

# BETTER: Use pattern structure when possible
match value:
    case int(x) if x > 0:  # Type + guard when needed
        pass
```

### 4. Prefer Exhaustive Matching

```python
# GOOD: Handle all cases explicitly
match status:
    case "pending":
        start_processing()
    case "running":
        continue_processing()
    case "completed":
        finish()
    case _:
        raise ValueError(f"Unknown status: {status}")
```

### 5. Use AS Patterns for Logging/Debugging

```python
# GOOD: Capture full value while destructuring
match response:
    case {"status": 200, "data": data} as full_response:
        log.debug(f"Full response: {full_response}")
        process(data)
```

### 6. Combine Patterns for Validation

```python
# GOOD: Validate structure and types
match config:
    case {"host": str(h), "port": int(p)} if 0 < p < 65536:
        connect(h, p)
    case {"host": str(h)}:
        connect(h, default_port)
    case _:
        raise ConfigError("Invalid config")
```

---

## Advanced Examples

### Pattern Matching with Nested Structures

```python
# Complex nested matching
match event:
    case {
        "type": "user_action",
        "user": {"id": user_id, "name": name},
        "action": {"kind": "purchase", "items": [*items]}
    }:
        process_purchase(user_id, name, items)

    case {
        "type": "system",
        "level": "error" | "critical",
        "message": msg
    } as full_event:
        log_error(full_event, msg)
```

### State Machine Pattern

```python
from enum import Enum
from dataclasses import dataclass

class State(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"

@dataclass
class Event:
    type: str
    data: dict = None

def process_event(state: State, event: Event) -> State:
    match (state, event):
        case (State.IDLE, Event(type="start")):
            return State.RUNNING
        case (State.RUNNING, Event(type="pause")):
            return State.PAUSED
        case (State.PAUSED, Event(type="resume")):
            return State.RUNNING
        case (State.RUNNING | State.PAUSED, Event(type="stop")):
            return State.STOPPED
        case _:
            return state
```

### API Response Handling

```python
def handle_api_response(response):
    match response:
        case {"status": 200, "data": data, "meta": {"page": p, "total": t}}:
            return f"Page {p}/{t}: {len(data)} items"

        case {"status": 200, "data": data}:
            return f"Success: {len(data)} items"

        case {"status": 404}:
            raise NotFoundError()

        case {"status": code, "error": {"message": msg}} if 400 <= code < 500:
            raise ClientError(msg)

        case {"status": code, "error": {"message": msg}} if 500 <= code < 600:
            raise ServerError(msg)

        case _:
            raise UnknownResponseError(response)
```

### Parser/Interpreter Pattern

```python
# AST node matching
match node:
    case ("number", value):
        return value

    case ("add", left, right):
        return evaluate(left) + evaluate(right)

    case ("multiply", left, right):
        return evaluate(left) * evaluate(right)

    case ("let", var, value, body):
        env[var] = evaluate(value)
        return evaluate(body)

    case _:
        raise SyntaxError(f"Unknown node: {node}")
```

### Custom Pattern Matching with __eq__

```python
import re

class RegexPattern:
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __eq__(self, other):
        return bool(self.pattern.match(str(other)))

# Usage
EMAIL = RegexPattern(r'^[\w\.-]+@[\w\.-]+\.\w+$')
PHONE = RegexPattern(r'^\+?1?\d{9,15}$')

match user_input:
    case EMAIL:
        send_email_verification(user_input)
    case PHONE:
        send_sms_verification(user_input)
    case _:
        raise ValueError("Invalid contact info")
```

### Set Membership Pattern

```python
class OneOf:
    def __init__(self, *values):
        self.values = set(values)

    def __eq__(self, other):
        return other in self.values

VOWELS = OneOf('a', 'e', 'i', 'o', 'u')
OPERATORS = OneOf('+', '-', '*', '/', '%')

match char:
    case VOWELS:
        print("Vowel")
    case OPERATORS:
        print("Math operator")
    case _:
        print("Other")
```

---

## Quick Reference Card

| Pattern Type | Syntax | Example |
|-------------|--------|---------|
| Literal | `42`, `"text"`, `None` | `case 42:` |
| Capture | `x`, `name` | `case x:` |
| Wildcard | `_` | `case _:` |
| OR | `pattern1 \| pattern2` | `case 1 \| 2 \| 3:` |
| AS | `pattern as name` | `case [x, y] as point:` |
| Sequence | `[a, b]`, `(a, b)` | `case [x, y]:` |
| Mapping | `{"key": value}` | `case {"name": n}:` |
| Class | `ClassName(attr=val)` | `case Point(x=0, y=0):` |
| Guard | `pattern if condition` | `case x if x > 0:` |

### Key Reminders

- `_` = wildcard (not a variable)
- Bare names = capture patterns
- Dotted names = value patterns
- Type checks need `()`
- OR patterns must bind same names
- Patterns match top-to-bottom
- Guards run after pattern success
- No fall-through between cases

---

## References

- [PEP 634](https://peps.python.org/pep-0634/) - Structural Pattern Matching: Specification
- [PEP 636](https://peps.python.org/pep-0636/) - Structural Pattern Matching: Tutorial
- [Official Python Docs](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement)
- [Tutorial - Control Flow](https://docs.python.org/3/tutorial/controlflow.html#match-statements)
