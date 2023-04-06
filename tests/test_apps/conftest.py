from typing import TYPE_CHECKING, Any

import pytest
from mimesis.schema import Schema
from typing_extensions import Unpack

if TYPE_CHECKING:
    from django.test import Client
    from mimesis.schema import Field
    from plugins.identity.user import (
        RegistrationData,
        RegistrationDataFactory,
        UserData,
    )

    from server.apps.identity.models import User

_START_YEAR = 1900


@pytest.fixture()
def registration_data_factory(
    mimesis_field: 'Field',
) -> 'RegistrationDataFactory':
    """Returns factory for fake random registration data."""
    def factory(  # type: ignore[misc]
        **fields: Unpack['RegistrationData'],
    ) -> 'RegistrationData':
        password = mimesis_field('password')  # by default passwords are equal
        schema = Schema(schema=lambda: {
            'email': mimesis_field('person.email'),
            'first_name': mimesis_field('person.first_name'),
            'last_name': mimesis_field('person.last_name'),
            'date_of_birth': mimesis_field(
                'datetime.date',
                start=_START_YEAR,
            ),
            'address': mimesis_field('address.city'),
            'job_title': mimesis_field('person.occupation'),
            'phone': mimesis_field('person.telephone'),
        })

        return {
            **schema.create(iterations=1)[0],
            **{'password1': password, 'password2': password},
            **fields,
        }

    return factory


@pytest.fixture()
def registration_data(
    registration_data_factory: 'RegistrationDataFactory',
) -> 'RegistrationData':
    """Returns random registration data."""
    return registration_data_factory()


@pytest.fixture()
def user_data(registration_data: 'RegistrationData') -> 'UserData':
    """We need to simplify registration data to drop password fields.

    Basically, it is the same as registration data, but without password fields.
    """
    return {
        key: value_part
        for key, value_part in registration_data.items()
        if not key.startswith('password')
    }


@pytest.fixture()
def user(
    mimesis_field: 'Field',
    user_data: 'UserData',
    django_user_model: 'User',
) -> 'User':
    """Returns app user."""
    fields: dict[str, Any] = dict(user_data)
    fields.update({
        'password': mimesis_field('password'),
    })

    return django_user_model.objects.create_user(**fields)


@pytest.fixture()
def user_client(user: 'User', client: 'Client') -> 'Client':
    """Returns logged in client."""
    client.force_login(user)

    return client
