"""
This module contains functions for interacting with the E-PIX SOAP interface.
"""

from typing import Optional, List

from zeep import Client

from .helper import _read_key_value_entry_response, _serialize_dict, WSDLClient
from .model import Person, Identity, BatchRequestConfig, ResponseEntry, BatchResponseEntry, FullIdentity
from .schema import PersonSchema, IdentitySchema, ResponseEntrySchema, BatchRequestConfigSchema, FullIdentitySchema


def request_mpi(
        client: Client,
        domain_name: str,
        source_name: str,
        identity: Identity,
        comment: Optional[str] = None
) -> ResponseEntry:
    """
    Requests an MPI for an identity. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identity belongs
    :param source_name: source name from which the identity stems
    :param identity: identity to request MPI for
    :param comment: optional comment on this transaction
    :return: MPI response, indicating whether the identity already exists and containing the assigned MPI
    """
    identity_soap = IdentitySchema().dump(identity)
    response_entry_soap = client.service.requestMPI(domainName=domain_name, identity=identity_soap,
                                                    sourceName=source_name, comment=comment)

    return ResponseEntrySchema().load(_serialize_dict(response_entry_soap))


def get_person_by_mpi(client: Client, domain_name: str, mpi_id: str) -> Person:
    """
    Returns a person by their MPI. This function throws a Fault if the MPI is not present.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for the person
    :param mpi_id: MPI of the desired person
    :return: person assigned to the specified MPI
    """
    person_soap = client.service.getPersonByMPI(domainName=domain_name, mpiId=mpi_id)
    return PersonSchema().load(_serialize_dict(person_soap))


def _malformed_mpi_response(reason: str) -> ValueError:
    """
    Returns an error to indicate a malformed E-PIX response.

    :param reason: reason for error
    :return: ValueError with specified reason
    """
    return ValueError(f"MPI response is malformed: {reason}")


def update_person(client: Client, domain_name: str, source_name: str, mpi_id: str, identity: Identity,
                  force: bool = False, comment: Optional[str] = None) -> ResponseEntry:
    """
    Updates an identity, addressed by their MPI. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identity belongs
    :param source_name: source name from which the identity stems
    :param mpi_id: MPI of the person to update
    :param identity: identity with updated information
    :param force: undocumented API option
    :param comment: optional comment on this transaction
    :return: updated person record
    """
    identity_soap = IdentitySchema().dump(identity)
    response_entry_soap = client.service.updatePerson(domainName=domain_name, sourceName=source_name, mpiId=mpi_id,
                                                      identity=identity_soap,
                                                      force=force, comment=comment)

    return ResponseEntrySchema().load(_serialize_dict(response_entry_soap))


def get_persons_for_domain(client: Client, domain_name: str) -> List[Person]:
    """
    Returns a list of persons stored in a domain. This function throws a Fault if the specified domain
    doesn't exist.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for persons
    :return: list of persons inside the specified domain
    """
    persons_lst = _serialize_dict(client.service.getPersonsForDomain(domainName=domain_name))

    return [
        PersonSchema().load(person) for person in persons_lst
    ]


def get_identities_for_domain(client: Client, domain_name: str) -> List[FullIdentity]:
    """
    Returns a list of identities stored in a domain. This function throws a Fault if the specified domain
    doesn't exist.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for identities
    :return: list of identities inside the specified domain
    """
    identity_lst = _serialize_dict(client.service.getIdentitiesForDomain(domainName=domain_name))

    return [
        FullIdentitySchema().load(identity) for identity in identity_lst
    ]


def deactivate_identity(client: Client, identity_id: int) -> None:
    """
    Deactivates an identity based on their identity ID (not MPI!). This function throws a Fault if the
    specified identity ID cannot be found.

    :param client: Zeep client with E-PIX service definitions
    :param identity_id: ID of the identity to deactivate
    :return: nothing
    """
    client.service.deactivateIdentity(identityId=identity_id)


def deactivate_person(client: Client, domain_name: str, mpi_id: str) -> None:
    """
    Deactivates a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
    in the provided data domain.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look up the MPI
    :param mpi_id: MPI of the person to deactivate
    :return: nothing
    """
    client.service.deactivatePerson(domainName=domain_name, mpiId=mpi_id)


def delete_identity(client: Client, identity_id: int) -> None:
    """
    Deletes an identity based on their identity ID (not MPI!). This function throws a Fault if the
    specified identity ID cannot be found, or if the identity with the ID has not been deactivated yet.


    :param client: Zeep client with E-PIX service definitions
    :param identity_id: ID of the identity to delete
    :return: nothing
    """
    client.service.deleteIdentity(identityId=identity_id)


def delete_person(client: Client, domain_name: str, mpi_id: str) -> None:
    """
    Deletes a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
    in the provided data domain, or if the identity with the ID has not been deactivated yet.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look up the MPI
    :param mpi_id: MPI of the person to delete
    :return: nothing
    """
    client.service.deletePerson(domainName=domain_name, mpiId=mpi_id)


def request_mpi_batch(
        client: Client,
        domain_name: str,
        source_name: str,
        identities: List[Identity],
        config: Optional[BatchRequestConfig] = None,
        comment: Optional[str] = None
) -> List[BatchResponseEntry]:
    """
    Requests MPIs for a list of identities. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identities belong
    :param source_name: source name from which the identities stem
    :param identities: identities to request MPIs for
    :param config: optional configuration on how to handle this request
    :param comment: optional comment on this transaction
    :return: list of MPI responses, indicating whether an identity already exists and containing the assigned MPI
    """
    # load config if present
    if config is not None:
        config = BatchRequestConfigSchema().dump(config)

    response_soap = client.service.requestMPIBatch(mpiRequest={
        "comment": comment,
        "domainName": domain_name,
        "requestConfig": config,
        "requestEntries": [
            IdentitySchema().dump(identity) for identity in identities
        ],
        "sourceName": source_name
    })

    key_value_lst = _read_key_value_entry_response(_serialize_dict(response_soap))
    batch_response_entry_lst: List[BatchResponseEntry] = []

    for kv_entry in key_value_lst:
        identity = IdentitySchema().load(kv_entry[0])
        response_entry = ResponseEntrySchema().load(kv_entry[1])

        batch_response_entry_lst.append(BatchResponseEntry(
            match_status=response_entry.match_status,
            person=response_entry.person,
            identity=identity
        ))

    return batch_response_entry_lst


class EPIXClient(WSDLClient):
    """
    This class is a wrapper around the E-PIX service functions.
    """

    def request_mpi(self, domain_name: str, source_name: str,
                    identity: Identity, comment: Optional[str] = None) -> ResponseEntry:
        """
        Requests an MPI for an identity. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identity belongs
        :param source_name: source name from which the identity stems
        :param identity: identity to request MPI for
        :param comment: optional comment on this transaction
        :return: MPI response, indicating whether the identity already exists and containing the assigned MPI
        """
        return request_mpi(self._client, domain_name, source_name, identity, comment)

    def request_mpi_batch(
            self,
            domain_name: str,
            source_name: str,
            identities: List[Identity],
            config: Optional[BatchRequestConfig] = None,
            comment: Optional[str] = None
    ) -> List[BatchResponseEntry]:
        """
        Requests MPIs for a list of identities. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identities belong
        :param source_name: source name from which the identities stem
        :param identities: identities to request MPIs for
        :param config: optional configuration on how to handle this request
        :param comment: optional comment on this transaction
        :return: list of MPI responses, indicating whether an identity already exists and containing the assigned MPI
        """
        return request_mpi_batch(self._client, domain_name, source_name, identities, config, comment)

    def get_person_by_mpi(self, domain_name: str, mpi_id: str) -> Person:
        """
        Returns a person by their MPI. This function throws a Fault if the MPI is not present.

        :param domain_name: data domain in which to look for the person
        :param mpi_id: MPI of the desired person
        :return: person assigned to the specified MPI
        """
        return get_person_by_mpi(self._client, domain_name, mpi_id)

    def update_person(
            self,
            domain_name: str,
            source_name: str,
            mpi_id: str,
            identity: Identity,
            force: bool = False,
            comment: Optional[str] = None
    ) -> ResponseEntry:
        """
        Updates an identity, addressed by their MPI. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identity belongs
        :param source_name: source name from which the identity stems
        :param mpi_id: MPI of the person to update
        :param identity: identity with updated information
        :param force: undocumented API option
        :param comment: optional comment on this transaction
        :return: updated person record
        """
        return update_person(self._client, domain_name, source_name, mpi_id, identity, force, comment)

    def get_persons_for_domain(self, domain_name: str) -> List[Person]:
        """
        Returns a list of persons stored in a domain. This function throws a Fault if the specified domain
        doesn't exist.

        :param domain_name: data domain in which to look for persons
        :return: list of persons inside the specified domain
        """
        return get_persons_for_domain(self._client, domain_name)

    def get_identities_for_domain(self, domain_name: str) -> List[FullIdentity]:
        """
        Returns a list of identities stored in a domain. This function throws a Fault if the specified domain
        doesn't exist.

        :param domain_name: data domain in which to look for identities
        :return: list of identities inside the specified domain
        """
        return get_identities_for_domain(self._client, domain_name)

    def deactivate_identity(self, identity_id: int) -> None:
        """
        Deactivates an identity based on their identity ID (not MPI!). This function throws a Fault if the
        specified identity ID cannot be found.

        :param identity_id: ID of the identity to deactivate
        :return: nothing
        """
        return deactivate_identity(self._client, identity_id)

    def deactivate_person(self, domain_name: str, mpi_id: str) -> None:
        """
        Deactivates a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
        in the provided data domain.

        :param domain_name: data domain in which to look up the MPI
        :param mpi_id: MPI of the person to deactivate
        :return: nothing
        """
        return deactivate_person(self._client, domain_name, mpi_id)

    def delete_identity(self, identity_id: int) -> None:
        """
        Deletes an identity based on their identity ID (not MPI!). This function throws a Fault if the
        specified identity ID cannot be found, or if the identity with the ID has not been deactivated yet.

        :param identity_id: ID of the identity to delete
        :return: nothing
        """
        return delete_identity(self._client, identity_id)

    def delete_person(self, domain_name: str, mpi_id: str) -> None:
        """
        Deletes a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
        in the provided data domain, or if the identity with the ID has not been deactivated yet.

        :param domain_name: data domain in which to look up the MPI
        :param mpi_id: MPI of the person to delete
        :return: nothing
        """
        return delete_person(self._client, domain_name, mpi_id)
