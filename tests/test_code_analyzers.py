from __future__ import annotations

from pytest import FixtureRequest, fixture, mark

from language_server.utils.code_analyzers.base import (
    BaseClass,
    BaseFunction,
    BaseModule,
    CodeEntity,
    Position,
    Range,
)
from language_server.utils.code_analyzers.factory import AnalyzerFactory, BaseAnalyzer

CODE = '''
class Foo:
    def __init__(self): pass

    def sum(self,
            x: int,
            y: int):
        result = x + y
        return result

def outer_func():
    def inner_func():
        pass
    return None

def with_docstring():
    """ docstring """
    return None

def with_multiline_docstring():
    """
    multiline
    docstring
    """
    return None

async def async_func():
    return None

def oneline_func(): return None

def with_ignore_typing(): # typing: ignore
    ...

def starting_with_comment():
    # some comment
    ...

def with_nested_class():
    class newcls:
        def __new__(cls):
            ...

for i in "123":
    print(i)
'''


@fixture(scope="module")
def cursor(request: FixtureRequest) -> Position:
    return Position(*request.param.get("position"))


@fixture(scope="module")
def analyzer(request: FixtureRequest) -> BaseAnalyzer:
    return AnalyzerFactory.create_analyzer(request.param.get("name"), CODE)


@fixture
def code_entity(analyzer: BaseAnalyzer, cursor: Position) -> CodeEntity | None:
    return analyzer.get_context(cursor)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize("cursor", [{"position": (2, 10)}], indirect=True)
def test_class(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseClass)
    assert code_entity.name == "Foo"
    assert code_entity.code == (
        "class Foo:\n"
        "    def __init__(self): pass\n"
        "\n"
        "    def sum(self,\n"
        "            x: int,\n"
        "            y: int):\n"
        "        result = x + y\n"
        "        return result"
    )
    assert code_entity.code_lines == [
        "class Foo:",
        "    def __init__(self): pass",
        "",
        "    def sum(self,",
        "            x: int,",
        "            y: int):",
        "        result = x + y",
        "        return result",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(2, 10)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize("cursor", [{"position": (40, 10)}], indirect=True)
def test_nested_class(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseClass)
    assert code_entity.name == "newcls"
    assert code_entity.code == (
        "    class newcls:\n        def __new__(cls):\n            ..."
    )
    assert code_entity.code_lines == [
        "    class newcls:",
        "        def __new__(cls):",
        "            ...",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 1
    assert code_entity.signature_end == Position(40, 17)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [{"position": (3, 5)}, {"position": (3, 28)}],
    indirect=True,
)
def test_class_oneline_method(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "__init__"
    assert code_entity.code == "    def __init__(self): pass"
    assert code_entity.code_lines == ["    def __init__(self): pass"]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 1
    # `ast` and `jedi` have difference
    assert code_entity.signature_end == Position(
        3, 24
    ) or code_entity.signature_end == Position(3, 23)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [{"position": (5, 5)}, {"position": (7, 20)}, {"position": (9, 15)}],
    indirect=True,
)
def test_class_method(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "sum"
    assert code_entity.code == (
        "    def sum(self,\n"
        "            x: int,\n"
        "            y: int):\n"
        "        result = x + y\n"
        "        return result"
    )
    assert code_entity.code_lines == [
        "    def sum(self,",
        "            x: int,",
        "            y: int):",
        "        result = x + y",
        "        return result",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 1
    assert code_entity.signature_end == Position(7, 20)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor", [{"position": (11, 10)}, {"position": (14, 11)}], indirect=True
)
def test_outer_func(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "outer_func"
    assert code_entity.code == (
        "def outer_func():\n"
        "    def inner_func():\n"
        "        pass\n"
        "    return None"
    )
    assert code_entity.code_lines == [
        "def outer_func():",
        "    def inner_func():",
        "        pass",
        "    return None",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(11, 17)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor", [{"position": (12, 5)}, {"position": (13, 12)}], indirect=True
)
def test_inner_func(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "inner_func"
    assert code_entity.code == "    def inner_func():\n        pass"
    assert code_entity.code_lines == ["    def inner_func():", "        pass"]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 1
    assert code_entity.signature_end == Position(12, 21)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [{"position": (16, 21)}, {"position": (17, 12)}, {"position": (18, 15)}],
    indirect=True,
)
def test_func_with_docstring(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "with_docstring"
    assert (
        code_entity.code
        == 'def with_docstring():\n    """ docstring """\n    return None'
    )
    assert code_entity.code_lines == [
        "def with_docstring():",
        '    """ docstring """',
        "    return None",
    ]
    assert code_entity.docstring_range == Range(Position(17, 4), Position(17, 21))

    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(16, 21)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [{"position": (20, 16)}, {"position": (22, 7)}, {"position": (25, 4)}],
    indirect=True,
)
def test_func_with_multiline_docstring(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "with_multiline_docstring"
    assert code_entity.code == (
        "def with_multiline_docstring():\n"
        '    """\n'
        "    multiline\n"
        "    docstring\n"
        '    """\n'
        "    return None"
    )
    assert code_entity.code_lines == [
        "def with_multiline_docstring():",
        '    """',
        "    multiline",
        "    docstring",
        '    """',
        "    return None",
    ]
    assert code_entity.docstring_range == Range(Position(21, 4), Position(24, 7))
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(20, 31)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor", [{"position": (27, 13)}, {"position": (28, 15)}], indirect=True
)
def test_async_func(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "async_func"
    assert code_entity.code == "async def async_func():\n    return None"
    assert code_entity.code_lines == ["async def async_func():", "    return None"]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(27, 23)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor", [{"position": (30, 8)}, {"position": (30, 31)}], indirect=True
)
def test_oneline_func(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "oneline_func"
    assert code_entity.code == "def oneline_func(): return None"
    assert code_entity.code_lines == ["def oneline_func(): return None"]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end in (
        Position(30, 19),
        Position(30, 20),
    )  # `ast` and `jedi` have difference


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [
        {"position": (32, 12)},
        {"position": (32, 34)},
        {"position": (33, 6)},
    ],
    indirect=True,
)
def test_func_with_ignore_typing(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "with_ignore_typing"
    assert code_entity.code == "def with_ignore_typing(): # typing: ignore\n    ..."
    assert code_entity.code_lines == [
        "def with_ignore_typing(): # typing: ignore",
        "    ...",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(line=32, character=42)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [{"position": (35, 12)}, {"position": (36, 12)}, {"position": (37, 7)}],
    indirect=True,
)
def test_func_starting_with_comment(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "starting_with_comment"
    assert (
        code_entity.code == "def starting_with_comment():\n    # some comment\n    ..."
    )
    assert code_entity.code_lines == [
        "def starting_with_comment():",
        "    # some comment",
        "    ...",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(line=35, character=28)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize("cursor", [{"position": (39, 24)}], indirect=True)
def test_func_with_nested_class(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseFunction)
    assert code_entity.name == "with_nested_class"
    assert code_entity.code == (
        "def with_nested_class():\n"
        "    class newcls:\n"
        "        def __new__(cls):\n"
        "            ..."
    )
    assert code_entity.code_lines == [
        "def with_nested_class():",
        "    class newcls:",
        "        def __new__(cls):",
        "            ...",
    ]
    assert code_entity.docstring_range is None
    assert code_entity.indent_level == 0
    assert code_entity.signature_end == Position(line=39, character=24)


@mark.parametrize("analyzer", [{"name": "ast"}, {"name": "jedi"}], indirect=True)
@mark.parametrize(
    "cursor",
    [
        {"position": (4, 0)},
        {"position": (10, 0)},
        {"position": (15, 0)},
        {"position": (19, 0)},
        {"position": (26, 0)},
        {"position": (29, 0)},
        {"position": (31, 0)},
        {"position": (34, 0)},
        {"position": (38, 0)},
        {"position": (43, 0)},
        {"position": (44, 5)},
        {"position": (45, 8)},
    ],
    indirect=True,
)
def test_module(code_entity: CodeEntity | None) -> None:
    assert isinstance(code_entity, BaseModule)
    assert code_entity.docstring_range is None
    assert len(code_entity.code_lines) == 45
    assert len(code_entity.code) in (669, 668)  # `ast` and `jedi` have difference
