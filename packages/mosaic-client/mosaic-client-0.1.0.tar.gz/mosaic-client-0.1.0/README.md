# MOSAIC client

The `mosaic_client` library provides wrappers around the SOAP interfaces of E-PIX and gPAS by the [THS Greifswald](https://www.ths-greifswald.de/en/projekte/mosaic-project).
The main entrypoints are `mosaic_client.EPIXClient` and `mosaic_client.GPASClient`, which are classes that simply take the URL to the WSDL endpoint of their respective services and expose functions to interact with the services.

## Documentation

The documentation of the latest commit on the `master` branch [can be seen on GitLab](https://pprl.gitlab.io/mosaic-client-python/).

## Installation

Run `pip install mosaic_client`.
You can then import the `mosaic_client` module in your project.

## Usage

This is an example for requesting a new MPI for an identity.
It is assumed that first and last name, gender and birthdate are required and that there exists a data domain called "default" and a source called "dummy_safe_source".

```py
from datetime import datetime, timezone
from mosaic_client.epix import EPIXClient
from mosaic_client import Identity

epix = EPIXClient("http://localhost:8080/epix/epixService?wsdl")
mpi_response = epix.request_mpi("default", "dummy_safe_source", Identity(
    first_name="Foo",
    last_name="Bar",
    gender="M",
    birth_date=datetime(1970, 1, 1, tzinfo=timezone.utc)
))

# prints out the MPI assigned to the identity
print(f"MPI: {mpi_response.person.mpi()}")
```

The same works with gPAS.
Simply provide the WSDL endpoint URL and use the provided methods as you please.
In this example, a new pseudonym is requested inside the "default" domain.

```py
from mosaic_client.gpas import GPASClient

gpas = GPASClient("http://localhost:8080/gpas/gpasService?wsdl")
psn = gpas.get_or_create_pseudonym_for("default", "value123")

# prints out the generated pseudonym
print(f"Pseudonym: {psn}")
```