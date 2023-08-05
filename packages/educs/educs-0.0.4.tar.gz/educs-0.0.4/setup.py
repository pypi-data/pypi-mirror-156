# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['educs']

package_data = \
{'': ['*']}

install_requires = \
['multipledispatch>=0.6.0,<0.7.0',
 'numpy>=1.22.2,<2.0.0',
 'pygame>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'educs',
    'version': '0.0.4',
    'description': 'A package wrapping pygame functionality in p5.js calling conventions. Used in computer science highschool course',
    'long_description': '# educs - Education in CS\n\nI built this repl for use in my AP Computer Science Principles course. I wanted my students to be able to learn Python and to program graphical applications. Pygame is suitable for beginner graphics projects, but might be overwhelming for some students to learn while also learning Python. educs wraps Pygame and attempts to follow the more intuitive p5js naming conventions.\n\nHopefully this repl is helpful for other AP CSP teachers or students, or anyone else that might be familiar with p5.js but want to program in Python!',
    'author': 'Joshua Bas',
    'author_email': 'joshua.n.bas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JBas/educs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.9',
}


setup(**setup_kwargs)
