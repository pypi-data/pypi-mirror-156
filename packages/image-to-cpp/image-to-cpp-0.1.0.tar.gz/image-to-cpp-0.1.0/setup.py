# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['image_to_cpp']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0']

entry_points = \
{'console_scripts': ['image-to-cpp = image_to_cpp.main:main']}

setup_kwargs = {
    'name': 'image-to-cpp',
    'version': '0.1.0',
    'description': 'Convert an image into a c++ header file containing a bytes array. Useful for electronic projects using a thermal printer or a LCD display.',
    'long_description': '# Image to cpp\n\nConvert an image into a c++ header file containing a bytes array. Useful for electronic projects using a thermal printer or a LCD display.\n\n## Usage\n\n```\n> image-to-cpp --help\nusage: main.py [-h] [-r RESIZE] [-s] [-o OUTPUT] [-v] [-d] [-t THRESHOLD] image_path\n\nConvert an image into a byte array c++ code.\n\npositional arguments:\n  image_path            Path of image to convert, use `--` to read from stdin.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -r RESIZE, --resize RESIZE\n                        Resize image to specified width, keeping aspect ratio.\n  -s, --show            Only show converted image.\n  -o OUTPUT, --output OUTPUT\n                        Store to specified file (default: image_name.h), use `--` to output on stdout.\n  -v, --verbose         Deactivate information messages.\n  -d, --dither          Activate dithering.\n  -t THRESHOLD, --threshold THRESHOLD\n                        Threshold level when converting to black and white, from 0 to 255 (default: 128).\n```\n\n## License\n\nMIT\n',
    'author': 'Roipoussiere',
    'author_email': 'roipoussiere@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://framagit.org/roipoussiere/image-to-cpp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
