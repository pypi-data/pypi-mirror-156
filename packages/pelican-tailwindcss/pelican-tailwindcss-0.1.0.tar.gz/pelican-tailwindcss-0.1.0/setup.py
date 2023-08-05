# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pelican', 'pelican.plugins.tailwindcss', 'pelican.plugins.tailwindcss.utils']

package_data = \
{'': ['*']}

install_requires = \
['pelican>=4.5']

extras_require = \
{'markdown': ['markdown>=3.2']}

setup_kwargs = {
    'name': 'pelican-tailwindcss',
    'version': '0.1.0',
    'description': 'Pelican plugin to add TailwindCSS to your website.',
    'long_description': '# TailwindCSS Plugin for Pelican 🌬\n\n[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/tailwindcss/build)](https://github.com/pelican-plugins/tailwindcss/actions)\n[![PyPI Version](https://img.shields.io/pypi/v/pelican-tailwindcss)](https://pypi.org/project/pelican-tailwindcss/)\n![License](https://img.shields.io/pypi/l/pelican-tailwindcss?color=blue)\n\nThis plugin helps you use [TailwindCSS][] in your Pelican website.\n\n|    Author     |                       GitHub                       |                        Twitter                         |\n| :-----------: | :------------------------------------------------: | :----------------------------------------------------: |\n| Luca Fedrizzi | [https://github.com/lcfd](https://github.com/lcfd) | [https://twitter.com/lc_fd](https://twitter.com/lc_fd) |\n\n## Why Use This Plugin?\n\nBecause you want use [TailwindCSS][] in seconds.\nNot hours.\n\n## Installation\n\nThis plugin can be installed via:\n\n`python -m pip install pelican-tailwindcss`\n\nor\n\n`poetry add pelican-tailwindcss`\n\n## Basic Usage\n\n1. Create a `tailwind.config.js` file in your Pelican project root folder containing:\n\n    ```js\n    /** @type {import(\'tailwindcss\').Config} */\n    module.exports = {\n    content: ["./themes/**/*.html", "./themes/**/*.js"],\n    theme: {\n        extend: {},\n    },\n    plugins: [],\n    };\n    ```\n\n    The `content` property values are just suggestions. Feel free to modify them according to your needs.\n\n2. Create a `input.css` file in your Pelican project root folder containing:\n\n    ```css\n    @tailwind base;\n    @tailwind components;\n    @tailwind utilities;\n    ```\n\n3. Add the build file (`output.css`) in your `base.html`.\n\n    ```html\n    <link rel="stylesheet" href="/output.css" />\n    ```\n\n4. Done! You should be ready to use [TailwindCSS][] in your website template.\n\n## Advanced Usage\n\nIn your settings you can configure the plugin\'s behavior using the `TAILWIND` setting.\n\nAn example of a complete `TAILWIND` setting:\n\n```python\nTAILWIND = {\n    "version": "3.0.0"\n}\n```\n\n## Contributing\n\nContributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].\n\nTo start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.\n\n[existing issues]: https://github.com/pelican-plugins/tailwindcss/issues\n[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html\n\n## License\n\nThis project is licensed under the AGPL-3.0 license.\n\n[TailwindCSS]: https://github.com/tailwindlabs/tailwindcss\n',
    'author': 'Luca Fedrizzi',
    'author_email': 'github@lcfd.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pelican-plugins/tailwindcss',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
