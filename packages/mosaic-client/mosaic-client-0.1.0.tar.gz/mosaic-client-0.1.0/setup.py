# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mosaic_client']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.16.0,<4.0.0', 'zeep>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'mosaic-client',
    'version': '0.1.0',
    'description': 'Easy consumption of SOAP interfaces provided by E-PIX and gPAS of the MOSAIC suite',
    'long_description': '# MOSAIC client\n\nThe `mosaic_client` library provides wrappers around the SOAP interfaces of E-PIX and gPAS by the [THS Greifswald](https://www.ths-greifswald.de/en/projekte/mosaic-project).\nThe main entrypoints are `mosaic_client.EPIXClient` and `mosaic_client.GPASClient`, which are classes that simply take the URL to the WSDL endpoint of their respective services and expose functions to interact with the services.\n\n## Documentation\n\nThe documentation of the latest commit on the `master` branch [can be seen on GitLab](https://pprl.gitlab.io/mosaic-client-python/).\n\n## Installation\n\nRun `pip install mosaic_client`.\nYou can then import the `mosaic_client` module in your project.\n\n## Usage\n\nThis is an example for requesting a new MPI for an identity.\nIt is assumed that first and last name, gender and birthdate are required and that there exists a data domain called "default" and a source called "dummy_safe_source".\n\n```py\nfrom datetime import datetime, timezone\nfrom mosaic_client.epix import EPIXClient\nfrom mosaic_client import Identity\n\nepix = EPIXClient("http://localhost:8080/epix/epixService?wsdl")\nmpi_response = epix.request_mpi("default", "dummy_safe_source", Identity(\n    first_name="Foo",\n    last_name="Bar",\n    gender="M",\n    birth_date=datetime(1970, 1, 1, tzinfo=timezone.utc)\n))\n\n# prints out the MPI assigned to the identity\nprint(f"MPI: {mpi_response.person.mpi()}")\n```\n\nThe same works with gPAS.\nSimply provide the WSDL endpoint URL and use the provided methods as you please.\nIn this example, a new pseudonym is requested inside the "default" domain.\n\n```py\nfrom mosaic_client.gpas import GPASClient\n\ngpas = GPASClient("http://localhost:8080/gpas/gpasService?wsdl")\npsn = gpas.get_or_create_pseudonym_for("default", "value123")\n\n# prints out the generated pseudonym\nprint(f"Pseudonym: {psn}")\n```',
    'author': 'Maximilian Jugl',
    'author_email': 'Maximilian.Jugl@medizin.uni-leipzig.de',
    'maintainer': 'Maximilian Jugl',
    'maintainer_email': 'Maximilian.Jugl@medizin.uni-leipzig.de',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
