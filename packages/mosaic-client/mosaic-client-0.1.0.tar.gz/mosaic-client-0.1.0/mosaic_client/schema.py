"""
This module contains classes for easy (de-)serialization of SOAP requests and responses
using marshmallow.
"""

from datetime import datetime
from typing import Any, Optional, Mapping

from marshmallow import Schema, fields, post_load, ValidationError

from .model import Source, IdentifierDomain, Identifier, Contact, FullContact, Identity, FullIdentity, Person, \
    ResponseEntry, BatchRequestConfig


class RawDateTimeField(fields.Field):

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        if value is None:
            return None

        return value

    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs,
    ):
        if not isinstance(value, datetime):
            raise ValidationError("Date time object must be an instance of datetime.datetime")

        return value


class SourceSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()
    label = fields.Str()
    entry_date = RawDateTimeField(data_key="entryDate")
    update_date = RawDateTimeField(data_key="updateDate")

    @post_load
    def make_source(self, data, **kwargs):
        return Source(**data)


class IdentifierDomainSchema(Schema):
    name = fields.Str(required=True)
    label = fields.Str(required=True)
    oid = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    entry_date = RawDateTimeField(data_key="entryDate", load_default=None)
    update_date = RawDateTimeField(data_key="updateDate", load_default=None)

    @post_load
    def make_identifier_domain(self, data, **kwargs):
        return IdentifierDomain(**data)


class IdentifierSchema(Schema):
    value = fields.Str(required=True)
    identifier_domain = fields.Nested(IdentifierDomainSchema(), required=True, data_key="identifierDomain")
    entry_date = RawDateTimeField(data_key="entryDate", load_default=None)
    description = fields.Str(load_default=None)

    @post_load
    def make_identifier(self, data, **kwargs):
        return Identifier(**data)


class ContactSchema(Schema):
    city = fields.Str(load_default=None)
    country = fields.Str(load_default=None)
    country_code = fields.Str(data_key="countryCode", load_default=None)
    district = fields.Str(load_default=None)
    email = fields.Str(load_default=None)
    external_date = RawDateTimeField(data_key="externalDate", load_default=None)
    municipality_key = fields.Str(data_key="municipalityKey", load_default=None)
    phone = fields.Str(load_default=None)
    state = fields.Str(load_default=None)
    street = fields.Str(load_default=None)
    zip_code = fields.Str(data_key="zipCode", load_default=None)

    @post_load
    def make_contact(self, data, **kwargs):
        return Contact(**data)


class FullContactSchema(ContactSchema):
    contact_created = RawDateTimeField(data_key="contactCreated", load_default=None)
    contact_id = fields.Int(data_key="contactId", load_default=None)
    contact_last_edited = RawDateTimeField(data_key="contactLastEdited", load_default=None)
    contact_version = fields.Int(data_key="contactVersion", load_default=None)
    deactivated = fields.Bool()
    identity_id = fields.Int(data_key="identityId", load_default=None)

    @post_load
    def make_contact(self, data, **kwargs):
        return FullContact(**data)


class IdentitySchema(Schema):
    birth_date = RawDateTimeField(data_key="birthDate", load_default=None)
    birth_place = fields.Str(data_key="birthPlace", load_default=None)
    civil_status = fields.Str(data_key="civilStatus", load_default=None)
    degree = fields.Str(load_default=None)
    external_date = RawDateTimeField(data_key="externalDate", load_default=None)
    first_name = fields.Str(data_key="firstName", load_default=None)
    gender = fields.Str(load_default=None)
    identifiers = fields.List(fields.Nested(IdentifierSchema()))
    last_name = fields.Str(data_key="lastName", load_default=None)
    middle_name = fields.Str(data_key="middleName", load_default=None)
    mother_tongue = fields.Str(data_key="motherTongue", load_default=None)
    mothers_maiden_name = fields.Str(data_key="mothersMaidenName", load_default=None)
    nationality = fields.Str(load_default=None)
    prefix = fields.Str(load_default=None)
    race = fields.Str(load_default=None)
    religion = fields.Str(load_default=None)
    suffix = fields.Str(load_default=None)
    value_1 = fields.Str(data_key="value1", load_default=None)
    value_2 = fields.Str(data_key="value2", load_default=None)
    value_3 = fields.Str(data_key="value3", load_default=None)
    value_4 = fields.Str(data_key="value4", load_default=None)
    value_5 = fields.Str(data_key="value5", load_default=None)
    value_6 = fields.Str(data_key="value6", load_default=None)
    value_7 = fields.Str(data_key="value7", load_default=None)
    value_8 = fields.Str(data_key="value8", load_default=None)
    value_9 = fields.Str(data_key="value9", load_default=None)
    value_10 = fields.Str(data_key="value10", load_default=None)
    contacts = fields.List(fields.Nested(ContactSchema()))

    @post_load
    def make_identity(self, data, **kwargs):
        return Identity(**data)


class FullIdentitySchema(IdentitySchema):
    deactivated = fields.Bool()
    identity_created = RawDateTimeField(data_key="identityCreated", load_default=None)
    identity_id = fields.Int(data_key="identityId", load_default=None)
    identity_last_edited = RawDateTimeField(data_key="identityLastEdited", load_default=None)
    identity_version = fields.Int(data_key="identityVersion", load_default=None)
    person_id = fields.Int(data_key="personId", load_default=None)
    source = fields.Nested(SourceSchema(), load_default=None)
    contacts = fields.List(fields.Nested(FullContactSchema()))

    @post_load
    def make_identity(self, data, **kwargs):
        return FullIdentity(**data)


class PersonSchema(Schema):
    deactivated = fields.Bool(required=True)
    mpi_id = fields.Nested(IdentifierSchema(), required=True, data_key="mpiId")
    person_created = RawDateTimeField(required=True, data_key="personCreated")
    person_id = fields.Int(required=True, data_key="personId")
    person_last_edited = RawDateTimeField(required=True, data_key="personLastEdited")
    other_identities = fields.List(fields.Nested(FullIdentitySchema()), data_key="otherIdentities")
    reference_identity = fields.Nested(FullIdentitySchema(), required=True, data_key="referenceIdentity")

    @post_load
    def make_person(self, data, **kwargs):
        return Person(**data)


class ResponseEntrySchema(Schema):
    match_status = fields.Str(required=True, data_key="matchStatus")
    person = fields.Nested(PersonSchema(), required=True)

    @post_load
    def make_response_entry(self, data, **kwargs):
        return ResponseEntry(**data)


class BatchRequestConfigSchema(Schema):
    force_reference_update = fields.Bool(required=True, data_key="forceReferenceUpdate")
    save_action = fields.Str(required=True, data_key="saveAction")

    @post_load
    def make_batch_request_config(self, data, **kwargs):
        return BatchRequestConfig(**data)
