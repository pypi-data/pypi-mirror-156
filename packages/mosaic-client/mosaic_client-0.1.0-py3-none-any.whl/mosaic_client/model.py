"""
This module contains model classes of objects, which are commonly used in E-PIX and gPAS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass(frozen=True)
class IdentifierDomain:
    """
    Describes a value domain used to generate identifiers.
    """
    name: str
    label: str
    oid: Optional[str] = None
    description: Optional[str] = None
    entry_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


@dataclass(frozen=True)
class Identifier:
    """
    Represents an identifier sourced from a specific value domain.
    """
    value: str
    identifier_domain: IdentifierDomain
    entry_date: Optional[datetime] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class Contact:
    """
    Assigned to an identity to designate contact details.
    """
    city: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    district: Optional[str] = None
    email: Optional[str] = None
    external_date: Optional[datetime] = None
    municipality_key: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    street: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass(frozen=True)
class FullContact(Contact):
    """
    Contact with additional metadata.
    """
    contact_created: Optional[datetime] = None
    contact_id: Optional[int] = None
    contact_last_edited: Optional[datetime] = None
    contact_version: Optional[int] = None
    deactivated: Optional[bool] = None
    identity_id: Optional[int] = None


@dataclass(frozen=True)
class Identity:
    """
    Identifying information about a real-world entity.
    """
    birth_date: Optional[datetime] = None
    birth_place: Optional[str] = None
    civil_status: Optional[str] = None
    degree: Optional[str] = None
    external_date: Optional[datetime] = None
    first_name: Optional[str] = None
    gender: Optional[str] = None
    identifiers: List[Identifier] = field(default_factory=list)
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    mother_tongue: Optional[str] = None
    mothers_maiden_name: Optional[str] = None
    nationality: Optional[str] = None
    prefix: Optional[str] = None
    race: Optional[str] = None
    religion: Optional[str] = None
    suffix: Optional[str] = None
    value_1: Optional[str] = None
    value_2: Optional[str] = None
    value_3: Optional[str] = None
    value_4: Optional[str] = None
    value_5: Optional[str] = None
    value_6: Optional[str] = None
    value_7: Optional[str] = None
    value_8: Optional[str] = None
    value_9: Optional[str] = None
    value_10: Optional[str] = None
    contacts: List[Contact] = field(default_factory=list)


@dataclass(frozen=True)
class Source:
    """
    Data source from which information is gathered.
    """
    name: str
    description: Optional[str] = None
    label: Optional[str] = None
    entry_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


@dataclass(frozen=True)
class FullIdentity(Identity):
    """
    Identity with additional metadata.
    """
    deactivated: Optional[bool] = None
    identity_created: Optional[datetime] = None
    identity_id: Optional[int] = None
    identity_last_edited: Optional[datetime] = None
    identity_version: Optional[int] = None
    person_id: Optional[int] = None
    source: Optional[Source] = None
    contacts: List[FullContact] = field(default_factory=list)


@dataclass(frozen=True)
class Person:
    """
    State of an identity inside a data source.
    """
    deactivated: bool
    mpi_id: Identifier
    person_created: datetime
    person_id: int
    person_last_edited: datetime
    other_identities: List[FullIdentity]
    reference_identity: FullIdentity

    def mpi(self) -> str:
        """
        Convenience function to quickly obtain the MPI of this person.

        :return: MPI associated to this person
        """
        return self.mpi_id.value

    def identity_id(self) -> int:
        """
        Convenience function to quickly obtain the identity ID of this person.

        :return: Identity ID associated to this person
        """
        return self.reference_identity.identity_id


@dataclass(frozen=True)
class ResponseEntry:
    """
    Response sent back by E-PIX on an MPI request. Contains information on whether the requested
    identity was already found in the data source.
    """
    match_status: str
    person: Person


@dataclass(frozen=True)
class BatchResponseEntry(ResponseEntry):
    """
    Response sent back by E-PIX on a batch MPI request. Contains the same info as a normal
    MPI request, but also includes the request identity.
    """
    identity: Identity


@dataclass(frozen=True)
class BatchRequestConfig:
    """
    Configuration on how a batch request should be handled.
    """
    force_reference_update: bool
    save_action: str
