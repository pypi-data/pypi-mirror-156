import pytest
import itertools
from setuptools_github import tools

# this is the output from ${{ toJson(github) }}
GITHUB = {
    "beta": {
        "ref": "refs/heads/beta/0.0.4",
        "sha": "2169f90c22e",
        "run_number": "8",
    },
    "release": {
        "ref": "refs/tags/release/0.0.3",
        "sha": "5547365c82",
        "run_number": "3",
    },
    "master": {
        "ref": "refs/heads/master",
        "sha": "2169f90c",
        "run_number": "20",
    },
}


def test_abort_exception():
    a = tools.AbortExecution(
        "a one-line error message",
        """
        A multi line
          explaination of
           what happened
         with some detail
    """,
        """
    Another multiline hint how
      to fix the issue
    """,
    )

    assert a.message == "a one-line error message"
    assert (
        f"\n{a.explain}\n"
        == """
A multi line
  explaination of
   what happened
 with some detail
"""
    )
    assert (
        f"\n{a.hint}\n"
        == """
Another multiline hint how
  to fix the issue
"""
    )

    assert (
        f"\n{str(a)}\n"
        == """
a one-line error message
  A multi line
    explaination of
     what happened
   with some detail
hint:
  Another multiline hint how
    to fix the issue
"""
    )

    a = tools.AbortExecution("hello world")
    assert a.message == "hello world"
    assert a.explain == ""
    assert a.hint == ""
    assert str(a) == "hello world"


def test_indent():
    txt = """
    This is a simply
       indented text
      with some special
         formatting
"""
    expected = """
..This is a simply
..   indented text
..  with some special
..     formatting
"""

    found = tools.indent(txt[1:], "..")
    assert f"\n{found}" == expected


def test_hubversion():
    "extracts from a GITHUB a (version, hash) tuple"

    fallbacks = [
        "123",
        "",
    ]

    expects = {
        ("beta", ""): ("0.0.4b8", "2169f90c22e"),
        ("beta", "123"): ("0.0.4b8", "2169f90c22e"),
        ("release", "123"): ("0.0.3", "5547365c82"),
        ("release", ""): ("0.0.3", "5547365c82"),
        ("master", "123"): ("123", "2169f90c"),
        ("master", ""): ("", "2169f90c"),
    }

    itrange = itertools.product(GITHUB, fallbacks)
    for key, fallback in itrange:
        gdata = GITHUB[key]
        expected = expects[(key, fallback)]
        assert expected == tools.hubversion(gdata, fallback)


def test_get_module_var(tmp_path):
    "pulls variables from a file"
    path = tmp_path / "in0.txt"
    path.write_text(
        """
# a test file
A = 12
B = 3+5
C = "hello"
# end of test
"""
    )
    assert 12 == tools.get_module_var(path, "A")
    assert "hello" == tools.get_module_var(path, "C")
    pytest.raises(AssertionError, tools.get_module_var, path, "B")


def test_set_module_var_empty_file(tmp_path):
    "check if the set_module_var will create a bew file"
    path = tmp_path / "in1.txt"

    path.write_text("# a fist comment line\n")
    assert (
        path.read_text().strip()
        == """
# a fist comment line
""".strip()
    )

    tools.set_module_var(path, "__version__", "1.2.3")
    tools.set_module_var(path, "__hash__", "4.5.6")
    assert (
        path.read_text().strip()
        == """
# a fist comment line
__version__ = "1.2.3"
__hash__ = "4.5.6"
""".strip()
    )


def test_set_module_var(tmp_path):
    "handles set_module_var cases"
    path = tmp_path / "in2.txt"

    path.write_text(
        """
# a fist comment line
__hash__ = "4.5.6"
# end of test
"""
    )

    version, txt = tools.set_module_var(path, "__version__", "1.2.3")
    assert not version
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "1.2.3"
""".rstrip()
    )

    version, txt = tools.set_module_var(path, "__version__", "6.7.8")
    assert version == "1.2.3"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )

    version, txt = tools.set_module_var(path, "__hash__", "9.10.11")
    assert version == "4.5.6"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "9.10.11"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )
    return


def test_update_version(tmp_path):
    "test the update_version processing"
    from hashlib import sha224

    def writeinit(path):
        path.write_text(
            """
# a test file
__version__ = "1.2.3"
__hash__ = "4.5.6"

# end of test
"""
        )
        return sha224(path.read_bytes()).hexdigest()

    initfile = tmp_path / "__init__.py"
    hashval = writeinit(initfile)

    # verify nothing has changed
    assert "1.2.3" == tools.update_version(initfile)
    assert hashval == sha224(initfile.read_bytes()).hexdigest()

    # we update the __version__/__hash__ from a master branch
    tools.update_version(initfile, GITHUB["master"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "1.2.3"
__hash__ = "2169f90c"

# end of test
"""
    )

    # we update __version__/__hash__ from a beta branch (note the b<build-number>)
    writeinit(initfile)
    tools.update_version(initfile, GITHUB["beta"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "0.0.4b8"
__hash__ = "2169f90c22e"

# end of test
"""
    )

    writeinit(initfile)
    tools.update_version(initfile, GITHUB["release"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "0.0.3"
__hash__ = "5547365c82"

# end of test
"""
    )


def test_bump_version():
    "bump version test"
    assert tools.bump_version("0.0.1", "micro") == "0.0.2"
    assert tools.bump_version("0.0.2", "micro") == "0.0.3"
    assert tools.bump_version("0.0.2", "minor") == "0.1.0"
    assert tools.bump_version("1.2.3", "major") == "2.0.0"
    assert tools.bump_version("1.2.3", "release") == "1.2.3"


def test_gitwrapper(tmp_path):
    repo = tools.GitWrapper(tmp_path / "wow").init()
    path = repo / "abc.txt"
    path.write_text("hello")
    repo(["add", path])
    repo(["commit", "-m", "initial", path])
    assert repo(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "master"
