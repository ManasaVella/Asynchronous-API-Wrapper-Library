# SoftnexisGit Client

An asynchronous, type-safe, production-ready Python client for interacting with the GitHub API. Built using `aiohttp` for non-blocking I/O operations and `Pydantic` for strict data validation.

## Architectural Features
* **Asynchronous Engine:** Leverages `aiohttp` ClientSessions for seamless concurrency.
* **Type-Safe Validation:** Maps dynamic JSON payloads directly onto structured data models.
* **Automated Pagination Links:** Transparently traverses multi-page server responses via link headers.
* **Dynamic Rate Limit Tracking:** Inspects and holds contextual rate metrics per request cycle.

## Installation
Run the following command in the project directory to install the package locally:
```bash
pip install -e .