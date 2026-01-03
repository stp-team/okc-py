# OKC Python Wrapper

[![PyPI](https://img.shields.io/pypi/v/okc-py)](https://pypi.org/project/okc-py/)
[![Python](https://img.shields.io/pypi/pyversions/okc-py)](https://pypi.org/project/okc-py/)
[![License](https://img.shields.io/pypi/l/okc-py)](LICENSE)

Asynchronous Python wrapper for the OKC API with modern async/await syntax, type hints, and comprehensive error handling.

## Installation

```bash
pip install okc-py
```

or

```bash
uv add okc-py
```

## Configuration

Set your environment variables in a `.env` file:

```bash
OKC_BASE_URL=https://okc.example.com
OKC_USERNAME=your_username
OKC_PASSWORD=your_password
```

Or configure via `Settings`:

```python
from okc_py import OKC, Settings

settings = Settings(
    BASE_URL="https://okc.example.com",
    REQUEST_TIMEOUT=30,
    RATE_LIMIT_ENABLED=True,
    REQUESTS_PER_SECOND=5.0,
)

async with OKC(settings=settings) as okc:
    # Use the client
    pass
```

## Quick Start

```python
import asyncio
from okc_py import OKC

async def main():
    async with OKC() as okc:
        # Access different API repositories
        dossier = await okc.dossier.get(...)
        print(f"Dossier: {dossier}")

asyncio.run(main())
```

## Features

- **Modern async/await**: Built with `asyncio` and `aiohttp` for efficient async operations
- **Type hints**: Full type annotations for better IDE support and type checking
- **Error handling**: Comprehensive exception hierarchy for easy error handling
- **Rate limiting**: Built-in rate limiting to respect API limits
- **Retry logic**: Automatic retries with exponential backoff
- **Logging**: Structured logging with `loguru`
- **Context managers**: Support for async context managers

## API Repositories

The OKC client provides access to the following API repositories:

- `dossier` - Dossier management
- `premium` - Premium features
- `ure` - URE operations
- `sl` - SL operations
- `tests` - Tests management
- `tutors` - Tutors information

## Error Handling

```python
from okc_py import OKC
from okc_py.exceptions import (
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    OKCError,
)

async def main():
    try:
        async with OKC() as okc:
            result = await okc.dossier.get(...)
    except AuthenticationError:
        print("Authentication failed")
    except RateLimitError as e:
        print(f"Rate limited, retry after {e.retry_after} seconds")
    except NotFoundError as e:
        print(f"Resource not found: {e.resource}")
    except OKCError as e:
        print(f"OKC API error: {e}")

asyncio.run(main())
```

## Advanced Usage

### Using the Client Directly

```python
from okc_py import Client, Settings

settings = Settings(BASE_URL="https://okc.example.com")
client = Client(username="user", password="pass", settings=settings)

await client.connect()
# Use the client directly
await client.close()
```

### Custom Configuration

```python
from okc_py import OKC, Settings

settings = Settings(
    BASE_URL="https://okc.example.com",
    REQUEST_TIMEOUT=60,
    MAX_RETRIES=5,
    RETRY_DELAY=2.0,
    RATE_LIMIT_ENABLED=True,
    REQUESTS_PER_SECOND=10.0,
    LOG_LEVEL="DEBUG",
)

async with OKC(settings=settings) as okc:
    # Your code here
    pass
```

## License

MIT License - see LICENSE file for details.

## Links

- [Repository](https://github.com/STP-Team/okc-py)
- [Issues](https://github.com/STP-Team/okc-py/issues)
- [Changelog](https://github.com/STP-Team/okc-py/releases)
