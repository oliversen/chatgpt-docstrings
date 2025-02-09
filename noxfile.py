"""All the action we need during build."""

import json
import urllib.request as url_lib
from pathlib import Path

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_venv = True

USE_PYTHON_VERSION = Path(".python-version").read_text()


def _dependency_group(group: str) -> list[str]:
    """Returns dependencies from `pyproject.toml` for the specified dependency group."""
    return nox.project.load_toml("pyproject.toml")["dependency-groups"][group]


def _get_python_versions(start_version: str, end_version: str) -> list[str]:
    """Generates a list of Python versions within a given minor version range."""
    start_major, start_minor, *_ = map(int, start_version.split("."))
    end_major, end_minor, *_ = map(int, end_version.split("."))

    if start_major != end_major:
        raise ValueError(
            f"Major python versions do not match ({start_version}, {end_version})."
        )

    versions = []
    for minor in range(start_minor, end_minor + 1):
        version = f"{start_major}.{minor}"
        if minor > end_minor:
            break
        versions.append(version)

    return versions


def _install_language_server_libs(session: nox.Session) -> None:
    tmp_dir = Path(session.create_tmp())
    requirements = tmp_dir.joinpath("requirements.txt")
    session.run(
        "uv",
        "export",
        "--locked",
        "--only-group",
        "language-server",
        "-o",
        requirements,
        silent=True,
    )
    session.install("pip")
    session.run(
        "pip",
        "install",
        "-t",
        "./language_server/libs",
        "--python-version",
        USE_PYTHON_VERSION,
        "--only-binary",
        ":all:",
        "--implementation",
        "py",
        "--abi",
        "none",
        "--platform",
        "any",
        "--no-cache-dir",
        "--no-deps",
        "--no-compile",
        "--upgrade",
        "-r",
        requirements,
    )


def _update_py_packages(session: nox.Session) -> None:
    session.run("uv", "lock", "--upgrade")
    _install_language_server_libs(session)


def _update_nodejs_packages(session: nox.Session) -> None:
    def get_package_data(package: str) -> dict:
        json_uri = f"https://registry.npmjs.org/{package}"
        with url_lib.urlopen(json_uri) as response:
            return json.loads(response.read())

    pinned = {
        "vscode-languageclient",
        "@types/vscode",
        "@types/node",
    }
    package_json_path = Path(__file__).parent / "package.json"
    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))

    for package in package_json["dependencies"]:
        if package not in pinned:
            data = get_package_data(package)
            latest = "^" + data["dist-tags"]["latest"]
            package_json["dependencies"][package] = latest

    for package in package_json["devDependencies"]:
        if package not in pinned:
            data = get_package_data(package)
            latest = "^" + data["dist-tags"]["latest"]
            package_json["devDependencies"][package] = latest

    # Ensure engine matches the package
    if (
        package_json["engines"]["vscode"]
        != package_json["devDependencies"]["@types/vscode"]  # noqa
    ):
        print(
            "Please check VS Code engine version and "
            "@types/vscode version in package.json."
        )

    new_package_json = json.dumps(package_json, indent=4)
    # JSON dumps uses \n for line ending on all platforms by default
    if not new_package_json.endswith("\n"):
        new_package_json += "\n"
    package_json_path.write_text(new_package_json, encoding="utf-8")
    session.run("npm", "install", external=True)


@nox.session(python=USE_PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    """Runs linter and formatter checks."""
    session.install(*_dependency_group("linting"))
    session.run("flake8")
    session.run("black", "--check", ".")
    session.run("npm", "run", "lint", external=True)


@nox.session(python=_get_python_versions(USE_PYTHON_VERSION, "3.13"))
def tests(session: nox.Session) -> None:
    """Runs tests for the extension."""
    session.install(*_dependency_group("testing"))
    session.run("pytest")


@nox.session(python=USE_PYTHON_VERSION)
def update_packages(session: nox.Session) -> None:
    """Updates Python and/or Node.js packages.

    Example:
        To update both Python and Node.js packages:
            nox -s update_packages

        To update only Python packages:
            nox -s update_packages -- only-python

        To update only Node.js packages:
            nox -s update_packages -- only-nodejs
    """
    if "only-nodejs" not in session.posargs:
        _update_py_packages(session)
    if "only-python" not in session.posargs:
        _update_nodejs_packages(session)


@nox.session(python=USE_PYTHON_VERSION)
def install_packages(session: nox.Session) -> None:
    """Installs required Python and/or Node.js packages.

    Example:
        To install both Python and Node.js packages:
            nox -s install_packages

        To install only Python packages:
            nox -s install_packages -- only-python

        To install only Node.js packages:
            nox -s install_packages -- only-nodejs
    """
    if "only-nodejs" not in session.posargs:
        _install_language_server_libs(session)
    if "only-python" not in session.posargs:
        session.run("npm", "install", external=True)


@nox.session(python=USE_PYTHON_VERSION)
def build_package(session: nox.Session) -> None:
    """Builds VSIX package for publishing."""
    session.run("npm", "run", "vsce-package", external=True)
