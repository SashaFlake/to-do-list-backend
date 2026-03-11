import pytest


# pytest-asyncio: all async tests use asyncio mode automatically
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
