import os
import pathlib
import typing as t
from dataclasses import dataclass
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE, DocTestParser, DocTestRunner

from xotl.plato.schema import CustomizedAttrType, SchemaBase
from xotl.plato.testing import ExtendedBaseTestCase

_DOCS_SOURCES = pathlib.Path(os.path.dirname(__file__)) / ".." / "docs" / "source"
_SCHEMA_API_DOC = _DOCS_SOURCES / "api" / "01-schema.rst"


class TestSchemata(ExtendedBaseTestCase):
    def test_schema_doctests(self):
        self.runModuleDoctest("xotl.plato.schema")

    def test_schema_api_documentation_tests(self):
        with open(_SCHEMA_API_DOC, "r") as f:
            content = f.read()
        parser = DocTestParser()
        doctests = parser.get_doctest(
            content,
            {},
            "01-schema.rst",
            _SCHEMA_API_DOC,
            0,
        )
        runner = DocTestRunner(optionflags=NORMALIZE_WHITESPACE | ELLIPSIS)
        runner.run(doctests)
        failed, attempted = runner.summarize(verbose=True)
        if failed:
            raise AssertionError(failed)

    def test_regression_inheriting_customized_attrs(self):
        @dataclass
        class Customized(SchemaBase, abstract=True):
            attr_path: t.Sequence[t.Union[int, str, None]]

            @classmethod
            def parse_attr_path(cls, raw_value):
                return raw_value

            @classmethod
            def dump_attr_path(cls, value, *, validate: bool = True):
                return value

        @dataclass
        class Inherited(Customized):
            pass

        self.assertIsInstance(
            Inherited.get_static_type().shape["attr_path"],
            CustomizedAttrType,
        )
