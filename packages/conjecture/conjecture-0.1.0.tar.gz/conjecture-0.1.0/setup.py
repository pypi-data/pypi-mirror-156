# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['conjecture']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'conjecture',
    'version': '0.1.0',
    'description': 'A pythonic assertion library',
    'long_description': '# Conjecture\n\nA pythonic assertion library.\n\n## 🛠 Installing\n\n### Poetry\n\n```\npoetry add conjecture\n```\n\n### pip\n\n```\npip install conjecture\n```\n\n## 🎓 Usage\n\n\n### Basic\n\nA basic assertion.\n\n```pycon\n>>> import conjecture\n>>> assert 5 == conjecture.has(lambda v: v < 10)\n>>> assert 5 == conjecture.has(lambda v: v > 10)\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n```\n\n### Built-in conjectures\n\n#### General\n\nMatching none.\n\n```pycon\n>>> import conjecture\n>>> assert None == conjecture.none()\n```\n\nMatching anything.\n\n```pycon\n>>> import conjecture\n>>> assert None == conjecture.anything()\n>>> assert 123 == conjecture.anything()\n>>> assert "abc" == conjecture.anything()\n```\n\n#### Mapping\n\nMatching keys.\n\n```pycon\n>>> import conjecture\n>>> assert {"a": 1} == conjecture.has_key("a")\n>>> assert {"a": 1} == conjecture.has_key("a", of=1)\n>>> assert {"a": 1} == conjecture.has_key("a", of=conjecture.less_than(5))\n```\n\n#### Object\n\nMatching instances of a class.\n\n```pycon\n>>> import conjecture\n>>> assert 123 == conjecture.instance_of(int)\n>>> assert "abc" == conjecture.instance_of((str, bytes))\n```\n\nMatching values.\n\n```pycon\n>>> import conjecture\n>>> assert 123 == conjecture.equal_to(123)\n>>> assert "abc" == conjecture.equal_to("abc")\n```\n\nMatching attributes.\n\n```pycon\n>>> import conjecture\n>>> assert 1 == conjecture.has_attribute("__class__")\n>>> assert 1 == conjecture.has_attribute("__class__", of=int)\n>>> assert 1 == conjecture.has_attribute("__class__", of=conjecture.instance_of(type))\n```\n\n#### Rich ordering\n\nMatching lesser values.\n\n```pycon\n>>> import conjecture\n>>> assert 5 == conjecture.greater_than(1)\n>>> assert 5 == conjecture.greater_than_or_equal_to(1)\n```\n\nMatching greater values.\n\n```pycon\n>>> import conjecture\n>>> assert 1 == conjecture.less_than(5)\n>>> assert 1 == conjecture.less_than_or_equal_to(5)\n```\n\n#### Size\n\nMatching empty collections.\n\n```pycon\n>>> import conjecture\n>>> assert list() == conjecture.empty()\n>>> assert set() == conjecture.empty()\n>>> assert tuple() == conjecture.empty()\n>>> assert dict() == conjecture.empty()\n```\n\nMatching length of collections.\n\n```pycon\n>>> import conjecture\n>>> assert [1, 2, 3, 4, 5] == conjecture.length_of(5)\n>>> assert [1, 2, 3] == conjecture.length_of(conjecture.less_than(5))\n```\n\n#### String\n\nMatching string prefixes.\n\n```pycon\n>>> import conjecture\n>>> assert "foo bar baz" == conjecture.prefixed_with("foo")\n>>> assert b"foo bar baz" == conjecture.prefixed_with(b"foo")\n```\n\nMatching string suffixes.\n\n```pycon\n>>> import conjecture\n>>> assert "foo bar baz" == conjecture.suffixed_with("baz")\n>>> assert b"foo bar baz" == conjecture.suffixed_with(b"baz")\n```\n\n### Combined conjectures\n\nMatching all conditions.\n\n```pycon\n>>> import conjecture\n>>> assert 5 == conjecture.has(lambda v: v <= 5) & conjecture.has(lambda v: v => 5)\n>>> assert 6 == conjecture.has(lambda v: v <= 5) & conjecture.has(lambda v: v => 5)\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n>>> assert 5 == conjecture.all_of(\n...     conjecture.has(lambda v: v <= 5),\n...     conjecture.has(lambda v: v => 5)\n... )\n>>> assert 6 == conjecture.all_of(\n...     conjecture.has(lambda v: v <= 5),\n...     conjecture.has(lambda v: v => 5)\n... )\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n```\n\nMatching any conditions.\n\n```pycon\n>>> import conjecture\n>>> assert 0 == conjecture.has(lambda v: v == 5) | conjecture.has(lambda v: v == 0)\n>>> assert 5 == conjecture.has(lambda v: v == 5) | conjecture.has(lambda v: v == 0)\n>>> assert 6 == conjecture.has(lambda v: v == 5) | conjecture.has(lambda v: v == 0)\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n>>> assert 5 == conjecture.any_of(\n...     conjecture.has(lambda v: v == 5),\n...     conjecture.has(lambda v: v == 0)\n... )\n>>> assert 6 == conjecture.any_of(\n...     conjecture.has(lambda v: v == 5),\n...     conjecture.has(lambda v: v == 0)\n... )\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n```\n\n### Negation\n\nA negative assertion.\n\n```pycon\n>>> import conjecture\n>>> assert 5 != conjecture.has(lambda v: v == 10)\n>>> assert 5 == ~conjecture.has(lambda v: v == 10)\n>>> assert 10 == ~conjecture.has(lambda v: v == 10)\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nAssertionError\n```\n\n## ⚖️ Licence\n\nThis project is licensed under the [MIT licence](http://dan.mit-license.org/).\n\nAll documentation and images are licenced under the \n[Creative Commons Attribution-ShareAlike 4.0 International License][cc_by_sa].\n\n[cc_by_sa]: https://creativecommons.org/licenses/by-sa/4.0/\n\n## 📝 Meta\n\nThis project uses [Semantic Versioning](http://semver.org/).\n',
    'author': 'Daniel Knell',
    'author_email': 'contact@danielknell.co.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/artisanofcode/python-conjecture',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
