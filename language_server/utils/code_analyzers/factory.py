from typing import Callable

from .base import BaseAnalyzer


class UnsupportedAnalyzer(Exception):
    """Exception raised when an unsupported analyzer is requested."""


class AnalyzerFactory:
    """A factory class that manages the registration and creation of analyzers."""

    _analyzers = {}

    @classmethod
    def available_analyzers(cls) -> list[str]:
        """Returns a list of names of all registered analyzers."""
        return list(cls._analyzers.keys())

    @classmethod
    def create_analyzer(cls, name: str, source_code: str) -> BaseAnalyzer:
        """Returns an analyzer instance based on the given name and source code."""
        if not (analyzer := cls._analyzers.get(name)):
            raise UnsupportedAnalyzer(f'"{name}" analyzer is not supported.')
        return analyzer(source_code)

    @classmethod
    def register_analyzer(cls, name: str) -> Callable:
        """A decorator to register an analyzer class with a given name."""

        def wrapper(analyzer: type[BaseAnalyzer]) -> type[BaseAnalyzer]:
            cls._analyzers[name] = analyzer
            return analyzer

        return wrapper
