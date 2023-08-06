# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paf_sapgui_flows',
 'paf_sapgui_flows.background_printing',
 'paf_sapgui_flows.cic',
 'paf_sapgui_flows.cic.msd_orders',
 'paf_sapgui_flows.cic.position_details',
 'paf_sapgui_flows.fi_keys',
 'paf_sapgui_flows.fi_keys.close_keys',
 'paf_sapgui_flows.fi_keys.get_keys',
 'paf_sapgui_flows.order',
 'paf_sapgui_flows.order.create',
 'paf_sapgui_flows.order.create.checks',
 'paf_sapgui_flows.random_order_to_invoice',
 'paf_sapgui_flows.random_order_to_invoice.jfdfs']

package_data = \
{'': ['*']}

install_requires = \
['paf_sapgui_eltrans>=1.0.8,<2.0.0']

setup_kwargs = {
    'name': 'paf-sapgui-flows',
    'version': '1.0.10',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
