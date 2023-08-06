from __future__ import annotations

import importlib.util
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List, Optional

from stresstest import errors


class Parameter:
    def __init__(
        self, name: str, default: Optional[str] = None, type: Optional[type] = None
    ):
        self.name = name
        self.default = default
        self.type = type
        self._value = None

    def set_value(self, value) -> None:
        self._value = None

    def get_value(self):
        if self._value is None:
            return self.default
        return self._value


class BaseStresstest(ABC):
    """Base class for all performance tests."""

    def __init__(self):
        self.time_start: Optional[float] = None
        self.time_end: Optional[float] = None

    def time(self):
        """Get duration of the test.

        Raises:
            errors.TestNotStartedError: Test has not been started.

        Returns:
            Test duration in seconds.
        """
        if self.time_end is None:
            raise errors.TestNotStartedError()
        return self.time_end - self.time_start

    @abstractmethod
    def run_test(self):
        """Abstract class to run the test."""
        pass

    def __enter__(self):
        """Method to call when test is started."""
        self.time_start = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        """Method to call when test is finished."""
        self.time_end = time.perf_counter()

    @staticmethod
    def discover() -> Iterator[BaseStresstest]:
        """Discover all tests."""
        stresstest_directory = Path(__file__).parent / "stresstests"
        yield from BaseStresstest._discover_directory(stresstest_directory)

    @staticmethod
    def _discover_directory(path: Path) -> Iterator[BaseStresstest]:
        for file in path.iterdir():
            if file.is_dir():
                yield from BaseStresstest._discover_directory(file)
            elif file.suffix == ".py":
                yield from BaseStresstest._discover_file(file)

    @staticmethod
    def _discover_file(file: Path) -> Iterator[BaseStresstest]:
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        imported_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(imported_module)

        for item_name, item in imported_module.__dict__.items():
            if not item_name.endswith("Stresstest") or item_name == "BaseStresstest":
                continue
            yield item

        yield from []
