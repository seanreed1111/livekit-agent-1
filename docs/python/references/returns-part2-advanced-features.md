# Returns Library Guide - Part 2: Advanced Features

A comprehensive guide to advanced features, methods, converters, and primitive types in the `returns` library.

## Table of Contents

1. [Introduction](#introduction)
2. [Methods Module](#methods-module)
   - [cond() Function](#cond-function)
   - [unwrap_or_failure() Function](#unwrap_or_failure-function)
   - [partition() Function](#partition-function)
   - [is_successful() Function](#is_successful-function)
3. [RequiresContext Deep Dive](#requirescontext-deep-dive)
   - [RequiresContext Basics](#requirescontext-basics-1)
   - [RequiresContextResult](#requirescontextresult)
   - [RequiresContextIOResult](#requirescontextioresult)
   - [RequiresContextFutureResult](#requirescontextfutureresult)
   - [Complex Context Patterns](#complex-context-patterns)
4. [Converters](#converters)
   - [result_to_maybe()](#result_to_maybe)
   - [maybe_to_result()](#maybe_to_result)
   - [flatten()](#flatten)
   - [Advanced Conversions](#advanced-conversions)
5. [Helper Functions (Pointfree)](#helper-functions-pointfree)
   - [map_() Function](#map_-function)
   - [bind() Function](#bind-function)
   - [alt() Function](#alt-function)
   - [lash() Function](#lash-function)
   - [apply() Function](#apply-function)
   - [Specialized Binds](#specialized-binds)
6. [Primitive Types](#primitive-types)
   - [IOResult](#ioresult)
   - [FutureResult](#futureresult-1)
   - [RequiresContextResult](#requirescontextresult-1)
   - [RequiresContextIOResult](#requirescontextioresult-1)
   - [RequiresContextFutureResult](#requirescontextfutureresult-1)

---

## Introduction

This guide covers advanced features of the `returns` library including utility methods, type converters, pointfree helpers, and composite primitive types that combine multiple effects.

**Import conventions:**
```python
from returns import methods
from returns.converters import result_to_maybe, maybe_to_result, flatten
from returns.pointfree import map_, bind, alt, lash, apply
from returns.io import IOResult, impure_safe
from returns.future import FutureResult, future_safe
from returns.context import (
    RequiresContext,
    RequiresContextResult,
    RequiresContextIOResult,
    RequiresContextFutureResult,
)
```

---

## Methods Module

The `methods` module provides utility functions for working with container types.

### cond() Function

The `cond()` function provides a functional alternative to if/else statements for container types.

**Example 1: Basic Conditional**
```python
from returns import methods
from returns.result import Result

def check_number(n: int) -> Result[str, str]:
    return methods.cond(
        Result,
        n > 0,
        'Positive number',
        'Non-positive number'
    )

result1 = check_number(5)    # Success('Positive number')
result2 = check_number(-3)   # Failure('Non-positive number')
result3 = check_number(0)    # Failure('Non-positive number')

print(result1)  # <Success: Positive number>
print(result2)  # <Failure: Non-positive number>
```

**Example 2: Validation with cond**
```python
from returns import methods
from returns.result import Result

def validate_age(age: int) -> Result[int, str]:
    return methods.cond(
        Result,
        0 <= age <= 150,
        age,
        f'Invalid age: {age}'
    )

def validate_email(email: str) -> Result[str, str]:
    return methods.cond(
        Result,
        '@' in email and '.' in email,
        email,
        f'Invalid email: {email}'
    )

age_result = validate_age(25)              # Success(25)
invalid_age = validate_age(200)            # Failure('Invalid age: 200')

email_result = validate_email('a@b.com')   # Success('a@b.com')
invalid_email = validate_email('notanemail') # Failure('Invalid email: notanemail')
```

**Example 3: Pipeline Integration**
```python
from returns import methods
from returns.result import Result, Success
from returns.pipeline import flow

def is_even(n: int) -> bool:
    return n % 2 == 0

def process_number(n: int) -> Result[str, str]:
    return methods.cond(
        Result,
        is_even(n),
        f'{n} is even',
        f'{n} is odd'
    )

# Use in a chain
def validate_and_check(s: str) -> Result[str, str]:
    return (
        Success(s)
        .map(int)
        .bind(lambda n: methods.cond(
            Result,
            n > 0,
            n,
            'Number must be positive'
        ))
        .bind(process_number)
    )

result1 = validate_and_check('4')   # Success('4 is even')
result2 = validate_and_check('5')   # Success('5 is odd')
result3 = validate_and_check('-2')  # Failure('Number must be positive')
```

### unwrap_or_failure() Function

Extracts values from container types, retrieving either the success or failure value.

**Example 1: Basic Unwrapping**
```python
from returns import methods
from returns.result import Success, Failure

success_value = Success(42)
failure_value = Failure('error')

# Extract the inner value (success or failure)
value1 = methods.unwrap_or_failure(success_value)  # 42
value2 = methods.unwrap_or_failure(failure_value)  # 'error'

print(value1)  # 42
print(value2)  # 'error'
```

**Example 2: After bimap Transformation**
```python
from returns import methods
from returns.result import Success, Failure

def double(x: int) -> int:
    return x * 2

def error_to_upper(e: str) -> str:
    return e.upper()

success = Success(21)
failure = Failure('network error')

# Transform both channels
transformed_success = success.bimap(double, error_to_upper)
transformed_failure = failure.bimap(double, error_to_upper)

# Unwrap the transformed values
print(methods.unwrap_or_failure(transformed_success))  # 42
print(methods.unwrap_or_failure(transformed_failure))  # 'NETWORK ERROR'
```

**Example 3: Logging Results**
```python
from returns import methods
from returns.result import Result, Success, Failure

def process_data(data: str) -> Result[int, str]:
    try:
        return Success(int(data))
    except ValueError:
        return Failure(f'Invalid data: {data}')

def log_result(result: Result[int, str]) -> None:
    value = methods.unwrap_or_failure(result)
    result_type = 'Success' if result.is_success() else 'Failure'
    print(f'{result_type}: {value}')

log_result(process_data('42'))   # Success: 42
log_result(process_data('abc'))  # Failure: Invalid data: abc
```

### partition() Function

Converts a list of container instances into separate lists of successes and failures.

**Example 1: Basic Partitioning**
```python
from returns import methods
from returns.result import Success, Failure

results = [
    Success(1),
    Failure('error 1'),
    Success(2),
    Success(3),
    Failure('error 2'),
]

successes, failures = methods.partition(results)

print(successes)  # [1, 2, 3]
print(failures)   # ['error 1', 'error 2']
```

**Example 2: Batch Processing**
```python
from returns import methods
from returns.result import Result, Success, Failure

def parse_int(s: str) -> Result[int, str]:
    try:
        return Success(int(s))
    except ValueError:
        return Failure(f'Cannot parse: {s}')

inputs = ['1', '2', 'abc', '3', 'def', '4']
results = [parse_int(s) for s in inputs]

valid, invalid = methods.partition(results)

print(f'Valid numbers: {valid}')      # Valid numbers: [1, 2, 3, 4]
print(f'Invalid inputs: {invalid}')   # Invalid inputs: ['Cannot parse: abc', ...]
```

**Example 3: Validation Report**
```python
from returns import methods
from returns.result import Result, Success, Failure
from typing import List

def validate_email(email: str) -> Result[str, str]:
    if '@' not in email:
        return Failure(f'{email}: missing @')
    if '.' not in email.split('@')[1]:
        return Failure(f'{email}: invalid domain')
    return Success(email)

def validate_all_emails(emails: List[str]) -> dict:
    results = [validate_email(email) for email in emails]
    valid, invalid = methods.partition(results)

    return {
        'valid_count': len(valid),
        'invalid_count': len(invalid),
        'valid_emails': valid,
        'errors': invalid
    }

emails = [
    'alice@example.com',
    'invalid',
    'bob@test.com',
    'missing@domain',
    'charlie@company.org'
]

report = validate_all_emails(emails)
print(f"Valid: {report['valid_count']}, Invalid: {report['invalid_count']}")
print(f"Errors: {report['errors']}")
```

### is_successful() Function

Determines whether a container represents a success state.

**Example 1: Basic Success Checking**
```python
from returns import methods
from returns.result import Success, Failure
from returns.maybe import Some, Nothing

# Result types
assert methods.is_successful(Success(42)) == True
assert methods.is_successful(Failure('error')) == False

# Maybe types
assert methods.is_successful(Some(100)) == True
assert methods.is_successful(Nothing) == False
```

**Example 2: Filtering Successful Results**
```python
from returns import methods
from returns.result import Result, Success, Failure
from typing import List

def process_batch(items: List[str]) -> List[Result[int, str]]:
    results = []
    for item in items:
        try:
            results.append(Success(int(item)))
        except ValueError:
            results.append(Failure(f'Invalid: {item}'))
    return results

def get_successful_results(results: List[Result]) -> List[Result]:
    return [r for r in results if methods.is_successful(r)]

def get_failed_results(results: List[Result]) -> List[Result]:
    return [r for r in results if not methods.is_successful(r)]

items = ['1', '2', 'abc', '3']
results = process_batch(items)

successful = get_successful_results(results)
failed = get_failed_results(results)

print(f'Successful: {len(successful)}')  # Successful: 3
print(f'Failed: {len(failed)}')          # Failed: 1
```

**Example 3: Conditional Processing**
```python
from returns import methods
from returns.result import Result, Success, Failure

def process_with_retry(result: Result[int, str], retries: int = 3) -> Result[int, str]:
    if methods.is_successful(result):
        return result

    # Retry logic for failures
    for attempt in range(retries):
        print(f'Retry attempt {attempt + 1}')
        # Simulate retry (in real code, would retry the operation)
        new_result = Success(42) if attempt == retries - 1 else result

        if methods.is_successful(new_result):
            return new_result

    return result

# First call succeeds
result1 = process_with_retry(Success(100))
print(result1)  # <Success: 100>

# First call fails, retries
result2 = process_with_retry(Failure('timeout'))
print(result2)  # <Success: 42> (after retries)
```

---

## RequiresContext Deep Dive

The Context module provides several specialized containers for dependency injection combined with different effects.

### RequiresContext Basics

**Example 1: Simple Context Function**
```python
from returns.context import RequiresContext

def get_api_key() -> RequiresContext[str, dict]:
    """Extract API key from config context."""
    return RequiresContext.ask().map(lambda config: config['api_key'])

def get_timeout() -> RequiresContext[int, dict]:
    """Extract timeout from config context."""
    return RequiresContext.ask().map(lambda config: config.get('timeout', 30))

# Provide context
config = {
    'api_key': 'secret-key-123',
    'timeout': 60,
    'debug': True
}

api_key = get_api_key()(config)  # 'secret-key-123'
timeout = get_timeout()(config)   # 60
```

**Example 2: Composing Context Operations**
```python
from returns.context import RequiresContext

class AppConfig:
    def __init__(self, base_url: str, api_version: str):
        self.base_url = base_url
        self.api_version = api_version

def get_base_url() -> RequiresContext[str, AppConfig]:
    return RequiresContext.ask().map(lambda c: c.base_url)

def get_api_version() -> RequiresContext[str, AppConfig]:
    return RequiresContext.ask().map(lambda c: c.api_version)

def build_api_url(endpoint: str) -> RequiresContext[str, AppConfig]:
    return RequiresContext.ask().map(
        lambda c: f'{c.base_url}/api/{c.api_version}/{endpoint}'
    )

# Alternative: compose existing functions
def build_api_url_v2(endpoint: str) -> RequiresContext[str, AppConfig]:
    def _build(base_url: str) -> RequiresContext[str, AppConfig]:
        return get_api_version().map(
            lambda version: f'{base_url}/api/{version}/{endpoint}'
        )
    return get_base_url().bind(_build)

config = AppConfig('https://api.example.com', 'v2')
url = build_api_url('users')(config)
# 'https://api.example.com/api/v2/users'
```

**Example 3: Complex Context Transformations**
```python
from returns.context import RequiresContext
from typing import List

class DatabaseConfig:
    def __init__(self, host: str, port: int, database: str, pool_size: int):
        self.host = host
        self.port = port
        self.database = database
        self.pool_size = pool_size

def get_connection_string() -> RequiresContext[str, DatabaseConfig]:
    return RequiresContext.ask().map(
        lambda c: f'postgresql://{c.host}:{c.port}/{c.database}'
    )

def get_pool_config() -> RequiresContext[dict, DatabaseConfig]:
    return RequiresContext.ask().map(
        lambda c: {
            'pool_size': c.pool_size,
            'max_overflow': c.pool_size * 2,
            'pool_timeout': 30
        }
    )

def create_engine_config() -> RequiresContext[dict, DatabaseConfig]:
    def _combine(conn_str: str) -> RequiresContext[dict, DatabaseConfig]:
        return get_pool_config().map(
            lambda pool: {
                'connection_string': conn_str,
                **pool
            }
        )
    return get_connection_string().bind(_combine)

db_config = DatabaseConfig('localhost', 5432, 'myapp', 10)
engine_config = create_engine_config()(db_config)
# {'connection_string': 'postgresql://localhost:5432/myapp',
#  'pool_size': 10, 'max_overflow': 20, 'pool_timeout': 30}
```

### RequiresContextResult

Combines context dependency with Result for operations that require config and can fail.

**Example 1: Basic RequiresContextResult**
```python
from returns.context import RequiresContextResult
from returns.result import Success, Failure

def validate_api_key(key: str) -> RequiresContextResult[str, str, dict]:
    """Validate API key against config."""
    def _validate(config: dict) -> Result[str, str]:
        expected_key = config.get('expected_api_key')
        if key == expected_key:
            return Success(key)
        return Failure('Invalid API key')

    return RequiresContextResult(_validate)

config = {'expected_api_key': 'secret123'}

result1 = validate_api_key('secret123')(config)  # Success('secret123')
result2 = validate_api_key('wrong')(config)      # Failure('Invalid API key')
```

**Example 2: Database Operations with Context**
```python
from returns.context import RequiresContextResult
from returns.result import Success, Failure, Result

class DbContext:
    def __init__(self, connection_string: str, max_retries: int):
        self.connection_string = connection_string
        self.max_retries = max_retries

def fetch_user(user_id: int) -> RequiresContextResult[dict, str, DbContext]:
    """Fetch user from database using connection from context."""
    def _fetch(ctx: DbContext) -> Result[dict, str]:
        print(f'Connecting to {ctx.connection_string}')
        # Simulate database query
        if user_id > 0:
            return Success({'id': user_id, 'name': f'User{user_id}'})
        return Failure('Invalid user ID')

    return RequiresContextResult(_fetch)

def update_user(user_id: int, name: str) -> RequiresContextResult[bool, str, DbContext]:
    """Update user in database."""
    def _update(ctx: DbContext) -> Result[bool, str]:
        print(f'Updating user {user_id} with {ctx.max_retries} max retries')
        # Simulate update
        if user_id > 0:
            return Success(True)
        return Failure('Cannot update invalid user')

    return RequiresContextResult(_update)

# Use with context
db_ctx = DbContext('postgresql://localhost/db', 3)

user_result = fetch_user(123)(db_ctx)
# Connects and returns Success({'id': 123, 'name': 'User123'})

update_result = update_user(123, 'Alice')(db_ctx)
# Returns Success(True)
```

**Example 3: Chaining Context-Result Operations**
```python
from returns.context import RequiresContextResult
from returns.result import Success, Failure, Result

class AppContext:
    def __init__(self, db_url: str, cache_enabled: bool):
        self.db_url = db_url
        self.cache_enabled = cache_enabled

def check_cache(key: str) -> RequiresContextResult[str, str, AppContext]:
    """Check cache if enabled."""
    def _check(ctx: AppContext) -> Result[str, str]:
        if not ctx.cache_enabled:
            return Failure('Cache disabled')
        # Simulate cache lookup
        if key == 'user:1':
            return Success('Cached data for user:1')
        return Failure('Cache miss')

    return RequiresContextResult(_check)

def fetch_from_db(error: str) -> RequiresContextResult[str, str, AppContext]:
    """Fallback to database on cache miss."""
    def _fetch(ctx: AppContext) -> Result[str, str]:
        print(f'Cache failed: {error}, fetching from {ctx.db_url}')
        return Success('Fresh data from database')

    return RequiresContextResult(lambda ctx: _fetch(ctx))

def get_data(key: str) -> RequiresContextResult[str, str, AppContext]:
    """Get data with cache fallback."""
    return check_cache(key).lash(fetch_from_db)

ctx = AppContext('postgresql://localhost/db', True)
result = get_data('user:1')(ctx)  # Success('Cached data for user:1')

ctx_no_cache = AppContext('postgresql://localhost/db', False)
result2 = get_data('user:1')(ctx_no_cache)
# Prints: Cache failed: Cache disabled, fetching from postgresql://localhost/db
# Success('Fresh data from database')
```

### RequiresContextIOResult

Combines context, IO effects, and Result for impure operations that need config and can fail.

**Example 1: File Operations with Context**
```python
from returns.context import RequiresContextIOResult
from returns.io import IOResult
from returns.result import Success, Failure

class FileContext:
    def __init__(self, base_path: str, encoding: str):
        self.base_path = base_path
        self.encoding = encoding

def read_config_file(filename: str) -> RequiresContextIOResult[str, str, FileContext]:
    """Read file using base path from context."""
    def _read(ctx: FileContext) -> IOResult[str, str]:
        import os
        full_path = os.path.join(ctx.base_path, filename)
        try:
            with open(full_path, 'r', encoding=ctx.encoding) as f:
                return IOResult.from_result(Success(f.read()))
        except FileNotFoundError:
            return IOResult.from_result(Failure(f'File not found: {full_path}'))
        except Exception as e:
            return IOResult.from_result(Failure(str(e)))

    return RequiresContextIOResult(_read)

def write_log(message: str) -> RequiresContextIOResult[None, str, FileContext]:
    """Write to log file."""
    def _write(ctx: FileContext) -> IOResult[None, str]:
        import os
        log_path = os.path.join(ctx.base_path, 'app.log')
        try:
            with open(log_path, 'a', encoding=ctx.encoding) as f:
                f.write(message + '\n')
            return IOResult.from_result(Success(None))
        except Exception as e:
            return IOResult.from_result(Failure(str(e)))

    return RequiresContextIOResult(_write)

# Usage
file_ctx = FileContext('/app/data', 'utf-8')

# These return IOResult when executed
# config = read_config_file('config.json')(file_ctx)
# log_result = write_log('Application started')(file_ctx)
```

**Example 2: HTTP Requests with Context**
```python
from returns.context import RequiresContextIOResult
from returns.io import IOResult, impure_safe
from returns.result import Success, Failure

class APIContext:
    def __init__(self, base_url: str, api_key: str, timeout: int):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

def make_request(endpoint: str) -> RequiresContextIOResult[dict, str, APIContext]:
    """Make HTTP request using API context."""
    def _request(ctx: APIContext) -> IOResult[dict, str]:
        import requests

        @impure_safe
        def _do_request() -> dict:
            url = f'{ctx.base_url}/{endpoint}'
            headers = {'Authorization': f'Bearer {ctx.api_key}'}
            response = requests.get(url, headers=headers, timeout=ctx.timeout)
            response.raise_for_status()
            return response.json()

        return _do_request().alt(lambda e: f'Request failed: {str(e)}')

    return RequiresContextIOResult(_request)

def fetch_user_data(user_id: int) -> RequiresContextIOResult[dict, str, APIContext]:
    """Fetch user data from API."""
    return make_request(f'users/{user_id}')

# Usage
api_ctx = APIContext('https://api.example.com', 'secret-key', 30)
# user_data = fetch_user_data(123)(api_ctx)
```

**Example 3: Database with Transaction Context**
```python
from returns.context import RequiresContextIOResult
from returns.io import IOResult
from returns.result import Success, Failure

class TransactionContext:
    def __init__(self, conn_string: str, isolation_level: str):
        self.conn_string = conn_string
        self.isolation_level = isolation_level
        self.transaction = None

def begin_transaction() -> RequiresContextIOResult[None, str, TransactionContext]:
    """Begin database transaction."""
    def _begin(ctx: TransactionContext) -> IOResult[None, str]:
        print(f'Beginning transaction with {ctx.isolation_level} isolation')
        ctx.transaction = {'active': True}
        return IOResult.from_result(Success(None))

    return RequiresContextIOResult(_begin)

def execute_query(query: str) -> RequiresContextIOResult[list, str, TransactionContext]:
    """Execute query in transaction."""
    def _execute(ctx: TransactionContext) -> IOResult[list, str]:
        if not ctx.transaction or not ctx.transaction.get('active'):
            return IOResult.from_result(Failure('No active transaction'))

        print(f'Executing: {query}')
        # Simulate query execution
        return IOResult.from_result(Success([{'id': 1}]))

    return RequiresContextIOResult(_execute)

def commit_transaction() -> RequiresContextIOResult[None, str, TransactionContext]:
    """Commit transaction."""
    def _commit(ctx: TransactionContext) -> IOResult[None, str]:
        if ctx.transaction:
            print('Committing transaction')
            ctx.transaction['active'] = False
        return IOResult.from_result(Success(None))

    return RequiresContextIOResult(_commit)

# Chain transaction operations
def run_transaction() -> RequiresContextIOResult[list, str, TransactionContext]:
    return (
        begin_transaction()
        .bind(lambda _: execute_query('INSERT INTO users VALUES (1)'))
        .bind(lambda result: commit_transaction().map(lambda _: result))
    )

tx_ctx = TransactionContext('postgresql://localhost/db', 'READ_COMMITTED')
# result = run_transaction()(tx_ctx)
```

### RequiresContextFutureResult

Combines context, async operations, and Result for async operations that need config and can fail.

**Example 1: Async API Calls with Context**
```python
from returns.context import RequiresContextFutureResult
from returns.future import FutureResult, future_safe
import asyncio

class AsyncAPIContext:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

def async_fetch_user(user_id: int) -> RequiresContextFutureResult[dict, str, AsyncAPIContext]:
    """Fetch user asynchronously using API context."""
    def _fetch(ctx: AsyncAPIContext) -> FutureResult[dict, str]:
        @future_safe
        async def _do_fetch() -> dict:
            await asyncio.sleep(0.1)  # Simulate network delay
            print(f'Fetching from {ctx.base_url} with key {ctx.api_key}')

            # Simulate API response
            if user_id > 0:
                return {'id': user_id, 'name': f'User{user_id}'}
            raise ValueError('Invalid user ID')

        return _do_fetch()

    return RequiresContextFutureResult(_fetch)

def async_fetch_posts(user_id: int) -> RequiresContextFutureResult[list, str, AsyncAPIContext]:
    """Fetch user posts asynchronously."""
    def _fetch(ctx: AsyncAPIContext) -> FutureResult[list, str]:
        @future_safe
        async def _do_fetch() -> list:
            await asyncio.sleep(0.1)
            print(f'Fetching posts for user {user_id}')
            return [
                {'id': 1, 'title': 'Post 1'},
                {'id': 2, 'title': 'Post 2'}
            ]

        return _do_fetch()

    return RequiresContextFutureResult(_fetch)

# Chain async operations
def get_user_with_posts(user_id: int) -> RequiresContextFutureResult[dict, str, AsyncAPIContext]:
    def _combine(user: dict) -> RequiresContextFutureResult[dict, str, AsyncAPIContext]:
        return async_fetch_posts(user_id).map(
            lambda posts: {**user, 'posts': posts}
        )

    return async_fetch_user(user_id).bind(_combine)

# Usage
async def main():
    api_ctx = AsyncAPIContext('https://api.example.com', 'secret-key')
    future_result = get_user_with_posts(123)(api_ctx)
    io_result = await future_result.awaitable()
    result = io_result.unwrap()
    print(result)

# asyncio.run(main())
```

**Example 2: Parallel Async Operations with Context**
```python
from returns.context import RequiresContextFutureResult
from returns.future import FutureResult, future_safe
import asyncio

class ServiceContext:
    def __init__(self, timeout: int, max_concurrent: int):
        self.timeout = timeout
        self.max_concurrent = max_concurrent

def fetch_data_async(source: str) -> RequiresContextFutureResult[str, str, ServiceContext]:
    """Fetch data from source asynchronously."""
    def _fetch(ctx: ServiceContext) -> FutureResult[str, str]:
        @future_safe
        async def _do_fetch() -> str:
            await asyncio.sleep(0.2)
            print(f'Fetched from {source} with timeout {ctx.timeout}')
            return f'Data from {source}'

        return _do_fetch()

    return RequiresContextFutureResult(_fetch)

async def fetch_all_data(sources: list[str], ctx: ServiceContext):
    """Fetch from multiple sources in parallel."""
    futures = [
        fetch_data_async(source)(ctx).awaitable()
        for source in sources[:ctx.max_concurrent]
    ]

    results = await asyncio.gather(*futures)
    return [r.unwrap() for r in results]

# Usage
async def main():
    ctx = ServiceContext(timeout=30, max_concurrent=3)
    sources = ['api1', 'api2', 'api3', 'api4']
    results = await fetch_all_data(sources, ctx)
    print(results)

# asyncio.run(main())
```

**Example 3: Complex Async Pipeline with Context**
```python
from returns.context import RequiresContextFutureResult
from returns.future import FutureResult, future_safe
import asyncio

class PipelineContext:
    def __init__(self, stage1_url: str, stage2_url: str, cache_enabled: bool):
        self.stage1_url = stage1_url
        self.stage2_url = stage2_url
        self.cache_enabled = cache_enabled

def stage1_process(data: str) -> RequiresContextFutureResult[dict, str, PipelineContext]:
    """First processing stage."""
    def _process(ctx: PipelineContext) -> FutureResult[dict, str]:
        @future_safe
        async def _do_process() -> dict:
            await asyncio.sleep(0.1)
            print(f'Stage 1 processing at {ctx.stage1_url}')
            return {'processed': data, 'stage': 1}

        return _do_process()

    return RequiresContextFutureResult(_process)

def stage2_process(data: dict) -> RequiresContextFutureResult[dict, str, PipelineContext]:
    """Second processing stage."""
    def _process(ctx: PipelineContext) -> FutureResult[dict, str]:
        @future_safe
        async def _do_process() -> dict:
            await asyncio.sleep(0.1)
            print(f'Stage 2 processing at {ctx.stage2_url}')
            return {**data, 'stage': 2, 'cached': ctx.cache_enabled}

        return _do_process()

    return RequiresContextFutureResult(_process)

def run_pipeline(input_data: str) -> RequiresContextFutureResult[dict, str, PipelineContext]:
    """Run complete processing pipeline."""
    return stage1_process(input_data).bind(stage2_process)

# Usage
async def main():
    ctx = PipelineContext(
        stage1_url='https://stage1.example.com',
        stage2_url='https://stage2.example.com',
        cache_enabled=True
    )

    future_result = run_pipeline('test data')(ctx)
    io_result = await future_result.awaitable()
    result = io_result.unwrap()
    print(result)
    # {'processed': 'test data', 'stage': 2, 'cached': True}

# asyncio.run(main())
```

### Complex Context Patterns

**Example 1: Multi-Environment Context**
```python
from returns.context import RequiresContextResult
from returns.result import Success, Failure, Result
from dataclasses import dataclass
from typing import Literal

@dataclass
class EnvironmentConfig:
    env: Literal['dev', 'staging', 'prod']
    db_url: str
    api_url: str
    debug: bool

def get_feature_flag(feature: str) -> RequiresContextResult[bool, str, EnvironmentConfig]:
    """Get feature flag based on environment."""
    def _get_flag(ctx: EnvironmentConfig) -> Result[bool, str]:
        # Different features enabled per environment
        if ctx.env == 'dev':
            return Success(True)  # All features in dev
        elif ctx.env == 'staging':
            return Success(feature in ['feature_a', 'feature_b'])
        else:  # prod
            return Success(feature == 'feature_a')

    return RequiresContextResult(_get_flag)

def execute_if_enabled(
    feature: str,
    action: str
) -> RequiresContextResult[str, str, EnvironmentConfig]:
    """Execute action only if feature is enabled."""
    def _execute_with_flag(enabled: bool) -> RequiresContextResult[str, str, EnvironmentConfig]:
        if enabled:
            return RequiresContextResult(lambda ctx: Success(f'Executed {action} in {ctx.env}'))
        return RequiresContextResult(lambda ctx: Failure(f'Feature {feature} disabled'))

    return get_feature_flag(feature).bind(_execute_with_flag)

# Use with different environments
dev_config = EnvironmentConfig('dev', 'postgres://localhost/dev', 'http://localhost:8000', True)
prod_config = EnvironmentConfig('prod', 'postgres://prod/db', 'https://api.example.com', False)

dev_result = execute_if_enabled('feature_x', 'process_data')(dev_config)
# Success('Executed process_data in dev')

prod_result = execute_if_enabled('feature_x', 'process_data')(prod_config)
# Failure('Feature feature_x disabled')
```

**Example 2: Hierarchical Context**
```python
from returns.context import RequiresContext
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str

@dataclass
class CacheConfig:
    host: str
    ttl: int

@dataclass
class ApplicationConfig:
    db: DatabaseConfig
    cache: CacheConfig
    app_name: str

def get_db_url() -> RequiresContext[str, ApplicationConfig]:
    """Extract database URL from nested config."""
    return RequiresContext.ask().map(
        lambda config: f'postgresql://{config.db.host}:{config.db.port}/{config.db.database}'
    )

def get_cache_url() -> RequiresContext[str, ApplicationConfig]:
    """Extract cache URL from nested config."""
    return RequiresContext.ask().map(
        lambda config: f'redis://{config.cache.host}'
    )

def get_full_config() -> RequiresContext[dict, ApplicationConfig]:
    """Build complete config dictionary."""
    def _build_with_db(db_url: str) -> RequiresContext[dict, ApplicationConfig]:
        return get_cache_url().map(
            lambda cache_url: RequiresContext.ask().map(
                lambda config: {
                    'app_name': config.app_name,
                    'database': db_url,
                    'cache': cache_url,
                    'cache_ttl': config.cache.ttl
                }
            )
        ).bind(lambda x: x)

    return get_db_url().bind(_build_with_db)

# Usage
app_config = ApplicationConfig(
    db=DatabaseConfig('localhost', 5432, 'myapp'),
    cache=CacheConfig('localhost', 3600),
    app_name='MyApp'
)

config_dict = get_full_config()(app_config)
# {
#     'app_name': 'MyApp',
#     'database': 'postgresql://localhost:5432/myapp',
#     'cache': 'redis://localhost',
#     'cache_ttl': 3600
# }
```

**Example 3: Context Transformation**
```python
from returns.context import RequiresContext
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: int
    roles: list[str]

@dataclass
class RequestContext:
    user: UserContext
    request_id: str
    ip_address: str

def has_role(role: str) -> RequiresContext[bool, RequestContext]:
    """Check if user has specific role."""
    return RequiresContext.ask().map(
        lambda ctx: role in ctx.user.roles
    )

def is_admin() -> RequiresContext[bool, RequestContext]:
    """Check if user is admin."""
    return has_role('admin')

def get_user_id() -> RequiresContext[int, RequestContext]:
    """Extract user ID from request context."""
    return RequiresContext.ask().map(lambda ctx: ctx.user.user_id)

def log_request(message: str) -> RequiresContext[str, RequestContext]:
    """Create log message with request context."""
    return RequiresContext.ask().map(
        lambda ctx: f'[{ctx.request_id}] [{ctx.ip_address}] User {ctx.user.user_id}: {message}'
    )

# Modify context for sub-operations
def with_user_context(
    operation: RequiresContext[str, UserContext]
) -> RequiresContext[str, RequestContext]:
    """Transform operation requiring UserContext to work with RequestContext."""
    return RequiresContext(
        lambda request_ctx: operation(request_ctx.user)
    )

# Usage
request_ctx = RequestContext(
    user=UserContext(user_id=123, roles=['admin', 'user']),
    request_id='req-456',
    ip_address='192.168.1.1'
)

admin_check = is_admin()(request_ctx)  # True
log_msg = log_request('Accessed resource')(request_ctx)
# '[req-456] [192.168.1.1] User 123: Accessed resource'
```

---

## Converters

The converters module provides functions to transform between different container types.

### result_to_maybe()

Converts a `Result` container to a `Maybe` container, discarding error information.

**Example 1: Basic Conversion**
```python
from returns.converters import result_to_maybe
from returns.result import Success, Failure
from returns.maybe import Some, Nothing

success = Success(42)
failure = Failure('error')

maybe_success = result_to_maybe(success)  # Some(42)
maybe_failure = result_to_maybe(failure)  # Nothing

print(maybe_success)  # <Some: 42>
print(maybe_failure)  # <Nothing>
```

**Example 2: Pipeline Integration**
```python
from returns.converters import result_to_maybe
from returns.result import safe
from returns.maybe import Maybe

@safe
def divide(a: int, b: int) -> float:
    return a / b

def safe_divide_maybe(a: int, b: int) -> Maybe[float]:
    """Divide and convert to Maybe, ignoring error details."""
    return result_to_maybe(divide(a, b))

result1 = safe_divide_maybe(10, 2)  # Some(5.0)
result2 = safe_divide_maybe(10, 0)  # Nothing

# Use with Maybe operations
result3 = safe_divide_maybe(20, 4).map(lambda x: x * 2).value_or(0)
# 10.0
```

**Example 3: Optional Value Extraction**
```python
from returns.converters import result_to_maybe
from returns.result import Result, Success, Failure
from returns.maybe import Maybe

def find_user(user_id: int) -> Result[dict, str]:
    """Find user by ID."""
    users = {1: {'name': 'Alice'}, 2: {'name': 'Bob'}}
    if user_id in users:
        return Success(users[user_id])
    return Failure(f'User {user_id} not found')

def get_user_optional(user_id: int) -> Maybe[dict]:
    """Get user as Maybe, discarding error message."""
    return result_to_maybe(find_user(user_id))

# Process without caring about error details
user = get_user_optional(1).map(lambda u: u['name']).value_or('Unknown')
# 'Alice'

missing_user = get_user_optional(999).map(lambda u: u['name']).value_or('Unknown')
# 'Unknown'
```

### maybe_to_result()

Converts a `Maybe` container to a `Result`, optionally specifying the error value for `Nothing`.

**Example 1: Basic Conversion**
```python
from returns.converters import maybe_to_result
from returns.maybe import Some, Nothing
from returns.result import Success, Failure

some_value = Some(42)
nothing_value = Nothing

# Convert without custom error
result1 = maybe_to_result(some_value)  # Success(42)
result2 = maybe_to_result(nothing_value)  # Failure(None)

# Convert with custom error
result3 = maybe_to_result(nothing_value, default_error='No value found')
# Failure('No value found')

print(result1)  # <Success: 42>
print(result2)  # <Failure: None>
print(result3)  # <Failure: No value found>
```

**Example 2: Adding Error Context**
```python
from returns.converters import maybe_to_result
from returns.maybe import Maybe

def parse_optional_config(key: str) -> Maybe[str]:
    """Get optional configuration value."""
    config = {'api_key': 'secret', 'timeout': '30'}
    return Maybe.from_optional(config.get(key))

def require_config(key: str) -> Result[str, str]:
    """Convert optional config to required, with error message."""
    return maybe_to_result(
        parse_optional_config(key),
        default_error=f'Required configuration {key} is missing'
    )

api_key = require_config('api_key')  # Success('secret')
missing = require_config('database_url')
# Failure('Required configuration database_url is missing')
```

**Example 3: Validation Pipeline**
```python
from returns.converters import maybe_to_result
from returns.maybe import Maybe, Some, Nothing
from returns.result import Result

def find_in_list(items: list, predicate) -> Maybe[any]:
    """Find first item matching predicate."""
    for item in items:
        if predicate(item):
            return Some(item)
    return Nothing

def require_item(
    items: list,
    predicate,
    error_message: str
) -> Result[any, str]:
    """Require an item to exist in list."""
    return maybe_to_result(
        find_in_list(items, predicate),
        default_error=error_message
    )

users = [
    {'id': 1, 'name': 'Alice', 'active': True},
    {'id': 2, 'name': 'Bob', 'active': False},
]

# Find active user
active_user = require_item(
    users,
    lambda u: u['active'],
    'No active user found'
)
# Success({'id': 1, 'name': 'Alice', 'active': True})

# Find admin user (doesn't exist)
admin_user = require_item(
    users,
    lambda u: u.get('role') == 'admin',
    'No admin user found'
)
# Failure('No admin user found')
```

### flatten()

Flattens nested containers of the same type.

**Example 1: Flatten Nested Results**
```python
from returns.converters import flatten
from returns.result import Success, Failure

# Nested Success
nested_success = Success(Success(42))
flat_success = flatten(nested_success)  # Success(42)

# Success containing Failure
success_with_failure = Success(Failure('error'))
flat_failure = flatten(success_with_failure)  # Failure('error')

# Failure containing Success
failure_with_success = Failure(Success(42))
still_failure = flatten(failure_with_success)  # Failure(Success(42))

print(flat_success)   # <Success: 42>
print(flat_failure)   # <Failure: error>
```

**Example 2: Flatten Nested Maybe**
```python
from returns.converters import flatten
from returns.maybe import Some, Nothing

# Nested Some
nested_some = Some(Some(100))
flat_some = flatten(nested_some)  # Some(100)

# Some containing Nothing
some_nothing = Some(Nothing)
flat_nothing = flatten(some_nothing)  # Nothing

print(flat_some)      # <Some: 100>
print(flat_nothing)   # <Nothing>
```

**Example 3: Flatten IO Containers**
```python
from returns.converters import flatten
from returns.io import IO

# Nested IO
def get_value() -> int:
    return 42

nested_io = IO(IO(get_value()))
flat_io = flatten(nested_io)

# Both execute to same value
print(flat_io.unwrap())  # Prints value
```

### Advanced Conversions

**Example 1: Chaining Conversions**
```python
from returns.converters import result_to_maybe, maybe_to_result
from returns.result import Success, Failure
from returns.maybe import Maybe

# Round-trip conversion
original = Success(42)
as_maybe = result_to_maybe(original)  # Some(42)
back_to_result = maybe_to_result(as_maybe)  # Success(42)

# Information loss with Failure
original_failure = Failure('detailed error')
as_maybe_fail = result_to_maybe(original_failure)  # Nothing
back_to_result_fail = maybe_to_result(as_maybe_fail)  # Failure(None) - lost error detail!

# Preserve error information with custom error
back_with_error = maybe_to_result(as_maybe_fail, default_error='Operation failed')
# Failure('Operation failed')
```

**Example 2: Complex Pipeline with Conversions**
```python
from returns.converters import result_to_maybe, maybe_to_result
from returns.result import safe, Success
from returns.maybe import Maybe

@safe
def parse_int(s: str) -> int:
    return int(s)

def process_optional_number(s: str | None) -> Maybe[int]:
    """Process an optional string as number."""
    if s is None:
        return Maybe.empty

    # Convert Result to Maybe
    return result_to_maybe(parse_int(s))

def require_positive_number(maybe_num: Maybe[int]) -> Result[int, str]:
    """Require number to be positive."""
    result = maybe_to_result(maybe_num, default_error='No number provided')

    return result.bind(lambda n:
        Success(n) if n > 0 else Failure(f'{n} is not positive')
    )

# Use the pipeline
result1 = require_positive_number(process_optional_number('42'))
# Success(42)

result2 = require_positive_number(process_optional_number('-5'))
# Failure('-5 is not positive')

result3 = require_positive_number(process_optional_number(None))
# Failure('No number provided')

result4 = require_positive_number(process_optional_number('abc'))
# Failure('No number provided')
```

**Example 3: Converting IO Containers**
```python
from returns.converters import flatten
from returns.io import IO, IOResult, impure, impure_safe
from returns.result import Success

@impure
def get_config() -> dict:
    return {'timeout': 30}

@impure_safe
def load_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

# Convert IO[Result] to IOResult using flatten conceptually
def safe_get_config() -> IOResult[dict, Exception]:
    return IOResult.from_io(get_config())

# Flatten nested IO operations
@impure
def nested_operation() -> IO[int]:
    return IO(42)

nested = IO(nested_operation())
flat = flatten(nested)
# Now flat is IO[int] instead of IO[IO[int]]
```

---

## Helper Functions (Pointfree)

The pointfree module provides functions that enable functional composition by reversing the typical method call order.

### map_() Function

Lifts regular functions to work with containers, transforming `a -> b` into `Container[a] -> Container[b]`.

**Example 1: Basic Mapping**
```python
from returns.pointfree import map_
from returns.result import Success, Failure
from returns.maybe import Some, Nothing

def double(x: int) -> int:
    return x * 2

# Create a pointfree version
double_in_container = map_(double)

# Apply to different containers
result1 = double_in_container(Success(5))   # Success(10)
result2 = double_in_container(Failure('e')) # Failure('e')
maybe1 = double_in_container(Some(3))       # Some(6)
maybe2 = double_in_container(Nothing)       # Nothing

print(result1)  # <Success: 10>
print(maybe1)   # <Some: 6>
```

**Example 2: Pipeline Composition**
```python
from returns.pointfree import map_
from returns.result import Success
from returns.pipeline import flow

def add_one(x: int) -> int:
    return x + 1

def to_string(x: int) -> str:
    return str(x)

def add_prefix(s: str) -> str:
    return f'Value: {s}'

# Compose pointfree operations
transform = flow(
    Success(5),
    map_(add_one),      # Success(6)
    map_(to_string),    # Success('6')
    map_(add_prefix),   # Success('Value: 6')
)

print(transform)  # <Success: Value: 6>
```

**Example 3: Reusable Transformations**
```python
from returns.pointfree import map_
from returns.result import Result, Success, Failure

# Create reusable transformations
to_upper = map_(str.upper)
strip = map_(str.strip)
length = map_(len)

def process_string(result: Result[str, str]) -> Result[int, str]:
    """Chain multiple map operations."""
    return length(to_upper(strip(result)))

input1 = Success('  hello  ')
output1 = process_string(input1)  # Success(5)

input2 = Failure('error')
output2 = process_string(input2)  # Failure('error')

print(output1)  # <Success: 5>
```

### bind() Function

Handles functions returning containers, converting `a -> Container[b]` to `Container[a] -> Container[b]`.

**Example 1: Basic Binding**
```python
from returns.pointfree import bind
from returns.result import Result, Success, Failure

def safe_divide(x: int) -> Result[float, str]:
    if x == 0:
        return Failure('Division by zero')
    return Success(1.0 / x)

# Create pointfree version
divide_in_container = bind(safe_divide)

# Apply to containers
result1 = divide_in_container(Success(2))   # Success(0.5)
result2 = divide_in_container(Success(0))   # Failure('Division by zero')
result3 = divide_in_container(Failure('e')) # Failure('e')

print(result1)  # <Success: 0.5>
print(result2)  # <Failure: Division by zero>
```

**Example 2: Chaining Operations**
```python
from returns.pointfree import bind
from returns.result import Result, Success, Failure
from returns.pipeline import flow

def parse_int(s: str) -> Result[int, str]:
    try:
        return Success(int(s))
    except ValueError:
        return Failure(f'Cannot parse: {s}')

def validate_positive(n: int) -> Result[int, str]:
    if n > 0:
        return Success(n)
    return Failure(f'Not positive: {n}')

def calculate_square(n: int) -> Result[int, str]:
    return Success(n * n)

# Create pipeline
process = lambda input: flow(
    input,
    bind(parse_int),
    bind(validate_positive),
    bind(calculate_square),
)

result1 = process(Success('5'))    # Success(25)
result2 = process(Success('-3'))   # Failure('Not positive: -3')
result3 = process(Success('abc'))  # Failure('Cannot parse: abc')

print(result1)  # <Success: 25>
```

**Example 3: Complex Bind Chains**
```python
from returns.pointfree import bind, map_
from returns.result import Result, Success, Failure

def fetch_user(user_id: int) -> Result[dict, str]:
    users = {1: {'name': 'Alice', 'email': 'alice@example.com'}}
    if user_id in users:
        return Success(users[user_id])
    return Failure(f'User {user_id} not found')

def fetch_preferences(user: dict) -> Result[dict, str]:
    email = user.get('email')
    prefs = {'alice@example.com': {'theme': 'dark'}}
    if email in prefs:
        return Success(prefs[email])
    return Failure(f'No preferences for {email}')

def get_theme(prefs: dict) -> Result[str, str]:
    if 'theme' in prefs:
        return Success(prefs['theme'])
    return Failure('No theme set')

# Compose with pointfree
get_user_theme = lambda user_id: flow(
    Success(user_id),
    bind(fetch_user),
    bind(fetch_preferences),
    bind(get_theme),
)

result = get_user_theme(1)  # Success('dark')
print(result)
```

### alt() Function

Operates on error states, transforming `a -> b` into `Container[_, a] -> Container[_, b]`.

**Example 1: Basic Error Transformation**
```python
from returns.pointfree import alt
from returns.result import Success, Failure

def make_error_friendly(error: str) -> str:
    return f'Oops! {error}'

# Create pointfree version
friendly_errors = alt(make_error_friendly)

# Apply to containers
result1 = friendly_errors(Success(42))          # Success(42) - unchanged
result2 = friendly_errors(Failure('db error'))  # Failure('Oops! db error')

print(result1)  # <Success: 42>
print(result2)  # <Failure: Oops! db error>
```

**Example 2: Error Message Enhancement**
```python
from returns.pointfree import alt
from returns.result import Result, Success, Failure

def add_context(error: str) -> str:
    return f'[USER_SERVICE] {error}'

def to_upper_error(error: str) -> str:
    return error.upper()

# Chain error transformations
enhance_errors = lambda result: flow(
    result,
    alt(add_context),
    alt(to_upper_error),
)

from returns.pipeline import flow

result1 = enhance_errors(Failure('connection failed'))
# Failure('[USER_SERVICE] CONNECTION FAILED')

result2 = enhance_errors(Success(100))
# Success(100) - unchanged
```

**Example 3: Converting Error Types**
```python
from returns.pointfree import alt
from returns.result import Result, Failure, Success

class APIError:
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code

    def __str__(self):
        return f'APIError({self.code}): {self.message}'

def exception_to_api_error(e: Exception) -> APIError:
    return APIError(str(e), 500)

# Create converter
convert_errors = alt(exception_to_api_error)

# Apply
result1 = convert_errors(Failure(ValueError('Invalid input')))
# Failure(APIError(500): Invalid input)

result2 = convert_errors(Success({'data': 'value'}))
# Success({'data': 'value'})
```

### lash() Function

Like bind but for failed containers, enabling recovery operations.

**Example 1: Basic Error Recovery**
```python
from returns.pointfree import lash
from returns.result import Result, Success, Failure

def fallback_value(error: str) -> Result[int, str]:
    print(f'Recovering from error: {error}')
    return Success(0)

# Create pointfree version
with_fallback = lash(fallback_value)

# Apply to containers
result1 = with_fallback(Success(42))          # Success(42) - unchanged
result2 = with_fallback(Failure('db error'))  # Success(0) - recovered
# Prints: Recovering from error: db error

print(result1)  # <Success: 42>
print(result2)  # <Success: 0>
```

**Example 2: Cascading Fallbacks**
```python
from returns.pointfree import lash
from returns.result import Result, Success, Failure
from returns.pipeline import flow

def try_cache(error: str) -> Result[str, str]:
    print('Trying cache...')
    return Failure('Cache miss')

def try_database(error: str) -> Result[str, str]:
    print('Trying database...')
    return Success('Data from database')

def try_default(error: str) -> Result[str, str]:
    print('Using default...')
    return Success('Default data')

# Create cascading fallback
fetch_with_fallbacks = lambda: flow(
    Failure('Initial failure'),
    lash(try_cache),
    lash(try_database),
    lash(try_default),
)

result = fetch_with_fallbacks()
# Prints:
# Trying cache...
# Trying database...
# Result: Success('Data from database')
```

**Example 3: Conditional Recovery**
```python
from returns.pointfree import lash
from returns.result import Result, Success, Failure

class NetworkError(Exception):
    pass

class ValidationError(Exception):
    pass

def recover_network_error(error: Exception) -> Result[dict, Exception]:
    if isinstance(error, NetworkError):
        print('Network error detected, using cached data')
        return Success({'cached': True, 'data': []})
    return Failure(error)  # Don't recover from other errors

# Create recovery function
with_network_recovery = lash(recover_network_error)

# Apply
result1 = with_network_recovery(Failure(NetworkError('Timeout')))
# Success({'cached': True, 'data': []})

result2 = with_network_recovery(Failure(ValidationError('Invalid input')))
# Failure(ValidationError('Invalid input'))

result3 = with_network_recovery(Success({'data': [1, 2, 3]}))
# Success({'data': [1, 2, 3]})
```

### apply() Function

Enables using container-wrapped functions as callables.

**Example 1: Basic Apply**
```python
from returns.pointfree import apply
from returns.result import Success, Failure

# Container with function
def add_ten(x: int) -> int:
    return x + 10

func_container = Success(add_ten)
value_container = Success(5)

# Apply the wrapped function
result = apply(func_container)(value_container)  # Success(15)

print(result)  # <Success: 15>
```

**Example 2: Partial Application Pattern**
```python
from returns.pointfree import apply
from returns.result import Success, Failure

def multiply(x: int) -> callable:
    def _multiply(y: int) -> int:
        return x * y
    return _multiply

# Create partially applied function in container
double = Success(multiply(2))
triple = Success(multiply(3))

# Apply to values
result1 = apply(double)(Success(5))   # Success(10)
result2 = apply(triple)(Success(5))   # Success(15)

# Failure propagates
result3 = apply(Failure('e'))(Success(5))   # Failure('e')
result4 = apply(double)(Failure('e'))       # Failure('e')
```

**Example 3: Function Composition in Containers**
```python
from returns.pointfree import apply
from returns.result import Success, Result

def compose_functions(f, g):
    """Compose two functions."""
    def _composed(x):
        return f(g(x))
    return _composed

# Functions in containers
add_one = Success(lambda x: x + 1)
double = Success(lambda x: x * 2)

# Compose them
composed = Success(compose_functions).apply(add_one).apply(double)

# Wait, apply doesn't work this way. Let me fix:
# apply is used differently

# Correct usage with apply
func_in_container = Success(lambda x: x * 2)
value_in_container = Success(21)

result = apply(func_in_container)(value_in_container)  # Success(42)
print(result)
```

### Specialized Binds

**Example 1: bind_result for Result Types**
```python
from returns.pointfree import bind_result
from returns.io import IOResult, impure_safe

@impure_safe
def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

def parse_json(content: str) -> Result[dict, Exception]:
    import json
    try:
        return Success(json.loads(content))
    except json.JSONDecodeError as e:
        return Failure(e)

# bind_result works with IOResult
process_file = lambda path: bind_result(parse_json)(read_file(path))

# result = process_file('config.json')
# IOResult[dict, Exception]
```

**Example 2: bind_io for IO Types**
```python
from returns.pointfree import bind_io
from returns.io import IO, impure

@impure
def get_timestamp() -> float:
    import time
    return time.time()

@impure
def format_timestamp(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).isoformat()

# Compose IO operations
formatted_time = bind_io(format_timestamp)(get_timestamp())

# Execute
# print(formatted_time.unwrap())
```

**Example 3: bind_async for Async Operations**
```python
from returns.pointfree import bind_async
from returns.future import Future, future
import asyncio

@future
async def fetch_user_id(email: str) -> int:
    await asyncio.sleep(0.1)
    return 123

@future
async def fetch_user_data(user_id: int) -> dict:
    await asyncio.sleep(0.1)
    return {'id': user_id, 'name': 'Alice'}

# Compose async operations
get_user_by_email = lambda email: bind_async(fetch_user_data)(fetch_user_id(email))

# Execute
async def main():
    io_result = await get_user_by_email('alice@example.com').awaitable()
    print(io_result.unwrap())

# asyncio.run(main())
```

---

## Primitive Types

The `returns` library provides several composite primitive types that combine multiple effects.

### IOResult

Combines IO effects with Result for impure operations that can fail.

**Example 1: File Operations**
```python
from returns.io import IOResult, impure_safe

@impure_safe
def read_config(path: str) -> dict:
    import json
    with open(path, 'r') as f:
        return json.load(f)

@impure_safe
def write_config(path: str, data: dict) -> None:
    import json
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# These return IOResult[T, Exception]
config_result = read_config('config.json')
# IOSuccess({...}) or IOFailure(FileNotFoundError(...))

write_result = write_config('config.json', {'key': 'value'})
# IOSuccess(None) or IOFailure(PermissionError(...))

# Execute and handle
match config_result.unwrap():
    case Success(data):
        print(f'Config loaded: {data}')
    case Failure(error):
        print(f'Failed to load config: {error}')
```

**Example 2: Database Operations**
```python
from returns.io import IOResult, impure_safe
from returns.result import Success, Failure

@impure_safe
def query_database(sql: str) -> list[dict]:
    # Simulated database query
    if 'SELECT' in sql:
        return [{'id': 1, 'name': 'Alice'}]
    raise ValueError('Only SELECT queries allowed')

@impure_safe
def insert_record(table: str, data: dict) -> int:
    # Simulated insert
    print(f'Inserting into {table}: {data}')
    return 1  # Return ID

# Compose database operations
def fetch_and_update_user(user_id: int) -> IOResult[int, Exception]:
    return (
        query_database(f'SELECT * FROM users WHERE id = {user_id}')
        .map(lambda rows: rows[0] if rows else None)
        .bind(lambda user: insert_record('audit_log', {'user_id': user['id']}))
    )

# result = fetch_and_update_user(1)
```

**Example 3: Network Requests**
```python
from returns.io import IOResult, impure_safe
import requests

@impure_safe
def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

@impure_safe
def post_json(url: str, data: dict) -> dict:
    response = requests.post(url, json=data, timeout=10)
    response.raise_for_status()
    return response.json()

# Compose HTTP operations
def fetch_and_post(get_url: str, post_url: str) -> IOResult[dict, Exception]:
    return (
        fetch_json(get_url)
        .map(lambda data: {**data, 'processed': True})
        .bind(lambda processed: post_json(post_url, processed))
    )

# response = fetch_and_post('https://api.example.com/data', 'https://api.example.com/submit')
```

### FutureResult

Combines async operations with Result for async operations that can fail.

**Example 1: Async API Calls**
```python
from returns.future import FutureResult, future_safe
import asyncio
import aiohttp

@future_safe
async def async_fetch_user(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.example.com/users/{user_id}') as response:
            response.raise_for_status()
            return await response.json()

@future_safe
async def async_fetch_posts(user_id: int) -> list:
    await asyncio.sleep(0.1)
    # Simulate API call
    return [{'id': 1, 'title': 'Post 1'}, {'id': 2, 'title': 'Post 2'}]

# Compose async operations
def get_user_with_posts(user_id: int) -> FutureResult[dict, Exception]:
    def _add_posts(user: dict) -> FutureResult[dict, Exception]:
        return async_fetch_posts(user_id).map(
            lambda posts: {**user, 'posts': posts}
        )

    return async_fetch_user(user_id).bind(_add_posts)

# Execute
async def main():
    io_result = await get_user_with_posts(1).awaitable()
    match io_result.unwrap():
        case Success(data):
            print(f'User data: {data}')
        case Failure(error):
            print(f'Error: {error}')

# asyncio.run(main())
```

**Example 2: Parallel Async Operations**
```python
from returns.future import FutureResult, future_safe
import asyncio

@future_safe
async def fetch_weather() -> dict:
    await asyncio.sleep(0.2)
    return {'temp': 72, 'conditions': 'Sunny'}

@future_safe
async def fetch_news() -> list:
    await asyncio.sleep(0.15)
    return ['News 1', 'News 2']

@future_safe
async def fetch_stocks() -> dict:
    await asyncio.sleep(0.1)
    return {'AAPL': 150.25, 'GOOGL': 2800.50}

async def fetch_dashboard_data() -> dict:
    # Launch all in parallel
    weather_future = fetch_weather().awaitable()
    news_future = fetch_news().awaitable()
    stocks_future = fetch_stocks().awaitable()

    # Wait for all
    weather, news, stocks = await asyncio.gather(
        weather_future,
        news_future,
        stocks_future
    )

    # Combine results
    return {
        'weather': weather.unwrap().unwrap(),
        'news': news.unwrap().unwrap(),
        'stocks': stocks.unwrap().unwrap()
    }

# async def main():
#     dashboard = await fetch_dashboard_data()
#     print(dashboard)
```

**Example 3: Retry Logic with FutureResult**
```python
from returns.future import FutureResult, future_safe
from returns.result import Success, Failure
import asyncio

@future_safe
async def unreliable_async_call() -> str:
    await asyncio.sleep(0.1)
    import random
    if random.random() < 0.7:
        raise Exception('Random failure')
    return 'Success!'

async def retry_async(
    operation: FutureResult,
    max_retries: int = 3
) -> IOResult[str, Exception]:
    for attempt in range(max_retries):
        result = await operation.awaitable()
        inner = result.unwrap()

        match inner:
            case Success(value):
                return result
            case Failure(error):
                if attempt < max_retries - 1:
                    print(f'Attempt {attempt + 1} failed, retrying...')
                    await asyncio.sleep(0.5)
                else:
                    print('All retries exhausted')
                    return result

# async def main():
#     result = await retry_async(unreliable_async_call())
#     print(result.unwrap())
```

### RequiresContextResult

**Already covered in detail in [RequiresContext Deep Dive](#requirescontextresult)**

### RequiresContextIOResult

**Already covered in detail in [RequiresContext Deep Dive](#requirescontextioresult)**

### RequiresContextFutureResult

**Already covered in detail in [RequiresContext Deep Dive](#requirescontextfutureresult)**

---

## Conclusion

This guide covered advanced features of the `returns` library:

- **Methods Module**: Utilities like `cond()`, `partition()`, and `is_successful()`
- **RequiresContext**: Comprehensive dependency injection patterns
- **Converters**: Transforming between container types
- **Pointfree Helpers**: Functional composition tools
- **Primitive Types**: Composite types combining multiple effects

**Key Takeaways:**

1. Use `methods.cond()` for functional conditionals
2. Use `partition()` to separate successful and failed results
3. RequiresContext variants enable typed dependency injection
4. Converters allow flexible transformation between types
5. Pointfree style enables cleaner function composition
6. Primitive types like IOResult and FutureResult combine effects safely

**Next Steps:**
- Explore the [official documentation](https://returns.readthedocs.io/)
- Review Part 1 for core types and containers
- Practice combining these patterns in real applications

**Resources:**
- [Official Documentation](https://returns.readthedocs.io/)
- [GitHub Repository](https://github.com/dry-python/returns)
- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
