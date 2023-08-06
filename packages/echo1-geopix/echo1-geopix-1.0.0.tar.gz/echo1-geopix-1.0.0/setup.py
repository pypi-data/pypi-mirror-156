# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['echo1_geopix']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.10.4,<0.11.0', 'loguru>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'echo1-geopix',
    'version': '1.0.0',
    'description': 'Helper functions to convert geo coords to pixel coords and back.',
    'long_description': '# echo1-geopix\n\n## Installation\n```sh\npip install echo1-geopix\n```\n\n## Getting Started\n```python\nfrom loguru import logger\nfrom echo1_geopix.echo1_geopix import (\n    geo_point_2_pix_point,\n    geo_box_2_pixel_box,\n    pixel_point_2_geo_point,\n    pixel_box_2_geo_box,\n)\nx_min = 0.35596034\ny_min = 0.94408214\nx_max = 0.4102673\ny_max = 0.9986186\ntop = 19.013473367825767\nbottom = 19.003535899073533\nleft = -98.27081680297852\nright = -98.26036944570143\n\n##\n# pixel_point_2_geo_point\n##\ntmp_geo_coords = pixel_point_2_geo_point(left, right, top, bottom, x_min, y_min)\nlogger.debug("pixel_point_2_geo_point: {}".format(tmp_geo_coords))\n\n##\n# geo_point_2_pix_point\n##\ntmp_pixel_coords = geo_point_2_pix_point(\n    left, right, top, bottom, tmp_geo_coords["lon"], tmp_geo_coords["lat"]\n)\nlogger.debug("geo_point_2_pix_point: {}".format(tmp_pixel_coords))\n\n##\n# pixel_box_2_geo_box\n##\ntmp_geo_box = pixel_box_2_geo_box(\n    x_min, y_min, x_max, y_max, left, right, top, bottom\n)\n\n##\n# geo_box_2_pixel_box\n##\ntemp_pixel_box = geo_box_2_pixel_box(\n    tmp_geo_box["lon_min"],\n    tmp_geo_box["lat_min"],\n    tmp_geo_box["lon_max"],\n    tmp_geo_box["lat_max"],\n    left,\n    right,\n    top,\n    bottom,\n)\nlogger.debug("geo_box_2_pixel_box: {}".format(temp_pixel_box))\n```\n',
    'author': 'Michael Mohamed',
    'author_email': 'michael.mohamed@echo1.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/e1-io/echo1-geopix',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
