# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_mapper']

package_data = \
{'': ['*']}

install_requires = \
['json-stream>=1.3.0']

setup_kwargs = {
    'name': 'json-position-mapper',
    'version': '0.1.0',
    'description': 'Map file-based JSON inputs from the file keys to their locations in the original file',
    'long_description': '# JSON Mapper\n\nTooling that can map a given JSON key to either a file offset or a line/column pair\n\nThis tooling is still in beta and the API is subject to change.\n\n## Purpose\n\nThis was designed to support a custom VS code JSON validator in an unrelated product. We needed to be able to know information such as `people.0.name` started at line 8 column 2 and ended at line 8 column 12, or that `people.0` (the entire sub-object) spanned from line 6 column 1 through line 18 column 1.\n\n## Interface\n\nThe primary interface to the JSON mapper is `json_mapper.mapper.JSONMapper`. This is initialized with a seekable IO object (such as a file or StringIO) and has the following public properties and methods:\n\n- `JSONMapper.offsets`: A cached property that contains a mapping of all the keys in the object to their relative file positions. The keys are tuples representing the path to get to a given JSON object(`(\'people\', 0, \'name\')`) in my example above and the offsets are named tuples with `start` and `end` parameters. The offsets are inclusive at the start and non-inclusive at the end - the same as Python slice mechanics. \n- `JSONMapper.get_position(key: Tuple)`: Get the start and end line/column offsets for a given JSON key. A `json_mapper.mapper.Position` object is returned which has `start_line`, `start_col`, `end_line`, and `end_col` stored values, and an `editor` calculated property, which returns a `json_mapper.mapper.EditorPosition`\n- `JSONMapper.get_position(key: Tuple).editor`: Get the `json_mapper.mapper.EditorPosition` object for a given JSON key. This is very similar to the non-editor based object, except that it uses inclusive starts and ends and all values are one based. This is what you will want to use if you are trying to use this library to write a VS Code task that highlights JSON files for problems.\n\n## Example\n\nInstallation: `pip install json-position-mapper`\n\nSample JSON file: `example.json`\n\n```json\n{\n    "people": [\n        {\n            "name": "Adam",\n            "favoriteFood": "pie",\n            "attributes": {\n                "eyeColor": "orange",\n                "height": "12 foot",\n                "happy": true\n            }\n        },\n        {\n            "name": "David",\n            "favoriteFood": "sushi",\n            "attributes": {\n                "eyeColor": "fuschia",\n                "height": "4 inches",\n                "happy": null\n            }\n        }\n    ]\n}\n```\n\nExample Python file: `example.py`\n\n```python\nfrom io import StringIO\nfrom json_mapper.mapper import JSONMapper, Position, Offset\n\nwith open("example.json") as f_in:\n    in_memory = StringIO(f_in.read())\n\nmapper = JSONMapper(in_memory)\n\n# Get the entire slice offset of the \'people\' key\nprint(mapper.offsets[("people",)])\n# Output: Offset(start=16, end=488)\n\n# Get the slice offset for people.0.name\nprint(mapper.offsets[("people", 0, "name")])\n# Output: Offset(start=48, end=54)\n\n# Get the line/column start and end for people.0\n# This is what we would use if we were to use Python to split the file on line and then use slice mechanics\nprint(mapper.get_position(("people", 0)))\n# Output: Position(start_line=2, start_col=8, end_line=10, end_col=9)\n\n# This is what we would use to highlight in something like VS Code\nprint(mapper.get_position(("people", 0)).editor)\n# Output: EditorPosition(start_line=3, start_col=9, end_line=11, end_col=9)\n\n```\n',
    'author': 'Adam Peacock',
    'author_email': 'apeacock@atlantistech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/atlantistechnology/json-position-mapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
