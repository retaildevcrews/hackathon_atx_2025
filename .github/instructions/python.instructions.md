---
applyTo: "**/*.py"
---

## General Guidelines

- Use Pythonic patterns (PEP8, PEP257).
- Prefer named functions and class-based structures over inline lambdas.
- Use type hints where applicable (`typing` module).
- Follow black or isort for formatting and import order.
- Use meaningful naming; avoid cryptic variables.
- Emphasize simplicity, readability, and DRY principles.
- Use poetry for dependency management and packaging.

## Patterns

### Patterns to Follow

- Validate data using Pydantic models.
- Use custom exceptions and centralized error handling.
- Use environment variables via `dotenv` or `os.environ`.
- Use logging via the `logging` module or structlog.
- Write modular, reusable code organized by concerns
- Favor async endpoints for I/O-bound services (FastAPI, aiohttp).
- Document functions and classes with docstrings.

### Patterns to Avoid

- Don’t use wildcard imports (`from module import *`).
- Avoid global state unless encapsulated in a singleton or config manager.
- Don’t hardcode secrets or config values—use `.env`.
- Don’t expose internal stack traces in production environments.
- Avoid business logic inside views/routes.

## Testing Guidelines

- Use `pytest` or `unittest` for unit and integration tests.
- Mock external services with `unittest.mock` or `pytest-mock`.
- Use fixtures to set up and tear down test data.
- Aim for high coverage on core logic and low-level utilities.
- Test both happy paths and edge cases.

## 📚 References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [Pytest Documentation](https://docs.pytest.org/en/stable/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Poetry](https://python-poetry.org/docs/)
