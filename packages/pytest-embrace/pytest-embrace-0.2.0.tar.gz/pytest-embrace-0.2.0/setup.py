# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_embrace']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'pyperclip>=1.8.2,<2.0.0', 'pytest>=7.0,<8.0']

entry_points = \
{'console_scripts': ['embrace = pytest_embrace.cli:main'],
 'pytest11': ['pytest_embrace = pytest_embrace.plugin']}

setup_kwargs = {
    'name': 'pytest-embrace',
    'version': '0.2.0',
    'description': 'Use modern Python type hints to design expressive tests. Reject boilerplate. Embrace complexity.',
    'long_description': '# pytest-embrace :gift_heart:\n\nThe `pytest-embrace` plugin enables judicious, repeatable, lucid unit testing.\n\n## Philosophy :bulb:\n\n1. Table-oriented (parametrized) tests are indespensible.\n2. Type hints and modern Python dataclasses are very good.\n3. Language-level APIs (like namespaces) are a honkin\' great idea.\n4. Code generation is *really* underrated.\n5. The wave of type-driven Python tools like Pydantic and Typer (both dependencies of this library) is very cowabunga––and only just beginning :ocean:\n\n## Features :white_check_mark:\n\n- [x] Completely customizable test design\n- [x] Type hints everywhere\n- [x] Table-oriented testing\n- [x] Strongly-typed test namespaces\n- [ ] Highly cusomizable code generation––powered by Pep 593\n- [x] Readable errors, early and often\n- [ ] Reporting / discovery\n\n## Basic Usage :wave:\n\nLike any pytest plugin, `pytest-embrace` is configured in `conftest.py`.\n\nThe main ingredients are:\n\n1. The "case" –– which can be any class decorated with `builtins.dataclasses.dataclass`.\n2. The "runner" –– which is just a tricked out Pytest fixture to run assertions against your case.\n3. The "caller" –– which is is another tricked out fixture that your tests will use.\n\n```python\n# conftest.py\nfrom dataclasses import dataclass\nfrom typing import Callable\n\nfrom pytest_embrace import CaseArtifact, Embrace\n\n\n@dataclass\nclass Case:\n    arg: str\n    func: Callable\n    expect: str\n\n\nembrace = Embrace(Case)\n\n@embrace.register_case_runner\ndef run_simple(case: Case):\n    result = case.func(case.arg)\n    assert result == case.expect\n    return result\n\n\nsimple_case = embrace.caller_fixture_factory(\'simple_case\')\n```\n\nWith the above conftest, you can write tests like so:\n\n1. Make a module with attributes matching your `Embrace()`\'d object\n2. Request your caller fixture in normal Pytest fashion\n\n```python\n# test_func.py\narg = \'Ainsley\'\nfunc = lambda x: x * 2\nexpect = \'AinsleyAinsley\'\n\n\ndef test(simple_case):\n\t...\n```\n\nOr you can go table-oriented and run many tests from one module––just like with `pytest.mark.parametrize`.\n\n```python\n# test_many_func.py\nfrom conftest import Case\n\ntable = [\n    Case(arg="haha", func=lambda x: x.upper(), expect="HAHA"),\n    Case(arg="wow damn", func=lambda x: len(x), expect=8),\n    Case(arg="sure", func=lambda x: hasattr(x, "beep"), expect=False),\n]\n\n\ndef test(simple_case):\n    ...\n```\n\n### Strongly Typed Namespaces :muscle:\n\nBefore even completing the setup phase of your `Embrace()`\'d tests, this plugin uses [Pydantic](https://pydantic-docs.helpmanual.io/) to validate the values set in your test modules. No type hints required.\n\nThat means there\'s no waiting around for expensive setups before catching simple mistakes.\n\n```python\n# given this case...\narg = "Ainsley"\nfunc = lambda x: x * 2\nexpect = b"AinsleyAinsley"\n\n\ndef test(simple_case):\n    ...\n```\n\nRunning the above immediately produces this error:\n\n```python\nE   pytest_embrace.exc.CaseConfigurationError: 1 invalid attr values in module \'test_wow\':\nE       Variable \'expect\' should be of type str\n```\n\nThe auxilary benefit of this feature is hardening the design of your code\'s interfaces––even interfaces that exist beyond the "vanishing point" of incoming data that you can\'t be certain of: Command line inputs, incoming HTTP requests, structured file inputs, etc.\n\n## Code Generation :robot:\n\nInstalling `pytest-embrace` adds a flag to `pytest` called `--embrace`.\n\nIt can be used to scaffold tests based on any of your registered cases.\n\nWith the example from above, you can do this out of the box:\n\n```shell\npytest --embrace simple_case\n```\n\nWhich puts this in your clipboard:\n\n```python\n# test_more.py\nfrom pytest_embrace import CaseArtifact\nfrom conftest import Case\n\narg: str\nfunc: "Callable"\nexpect: str\n\n\ndef test(simple_case: CaseArtifact[Case]):\n    ...\n```\n\nCopypasta\'d test cases like this can also be table-style: [Soon.]\n\n```shell\npytest --embrace-table 3\n```\n\nThe value passed to the `--table` flag will produce that many rows.\n\n```python\n# test_table_style.py\nfrom pytest_embrace import CaseArtifact\nfrom conftest import Case\n\ntable = [\n    # Case(arg=..., func=..., expect=...),\n    # Case(arg=..., func=..., expect=...),\n    # Case(arg=..., func=..., expect=...),\n]\n\ndef test(simple_case: CaseArtifact[Case]):\n    ...\n```\n\nBy default, each item is commented out so you don\'t end up with linter errors upon opening your new file.\n\nIf that\'s not cool, don\'t worry! It\'s configurable. :sunglasses:\n\n### Config With Pep 593 :star2:\n\nIn order to customize the behavior of your test cases, `pytest-embrace` :flushed: embraces :flushed:  the new `Annotated` type.\n\n> :information_source:\n> If you\'ve never heard of Pep 593 or `Annotated`, the **tl;dr** is that `Annotated[<type>, ...]` takes any number of arguments after the first one (the actual hint) that developers (me) can use at rumtime.\n\nThe `pytest_embrace.anno` namespace provides a number of utilities for controlling test parsing and code generation via `Annotated`.\n\n```python\nfrom dataclasses import dataclass\nfrom typing import Annotations\n\nfrom pytest_embrace import anno\n\n\n@dataclass\nclass FancyCase:\n    prop_1: Annotated[str, anno.TopDown()]\n    prop_2: Annotated[list[int], anno.OnlyWith(\'prop_3\')]\n    prop_3: Annotated[dict[str, set], anno.GenComment(\'Please enjoy prop_3!\')]\n\n\ne = Embrace(FancyCase, comment_out_table_values=False)\n```\n',
    'author': 'Ainsley McGrath',
    'author_email': 'mcgrath.ainsley@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
