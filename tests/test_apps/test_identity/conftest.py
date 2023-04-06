import json
import re
from typing import TYPE_CHECKING, Any, Iterator

import httpretty
import pytest
from mimesis.schema import Schema

if TYPE_CHECKING:
    from mimesis.schema import Field
    from plugins.identity.user import (
        ExternalAPIUserResponse,
        UserAssertion,
        UserData,
        UserExternalAssertion,
    )

    from server.apps.identity.models import User


@pytest.fixture()
def assert_correct_user(django_user_model: 'User') -> 'UserAssertion':
    """Returns assertion for user data."""
    def factory(email: str, expected: 'UserData') -> None:
        user = django_user_model.objects.get(email=email)

        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff

        # All other fields:
        for field, data_value in expected.items():
            assert getattr(user, field) == data_value

    return factory


@pytest.fixture()
def assert_correct_external_user(
    django_user_model: 'User',
) -> 'UserExternalAssertion':
    """Returns assertion for external user data."""
    def factory(email: str, external_api_mock):
        user = django_user_model.objects.get(email=email)
        assert user.lead_id == int(external_api_mock['id'])

    return factory


@pytest.fixture()
def external_api_user_response(
    mimesis_field: 'Field',
) -> 'ExternalAPIUserResponse':
    """Create fake external API response for users."""
    schema = Schema(schema=lambda: {
        'id': str(mimesis_field('numeric.increment')),
    })

    return schema.create(iterations=1)[0]


@pytest.fixture()
def external_api_mock(
    external_api_user_response: 'ExternalAPIUserResponse',
    settings: Any,
) -> Iterator['ExternalAPIUserResponse']:
    """Mock external `/users` call."""
    with httpretty.httprettized():
        httpretty.register_uri(
            method=httpretty.POST,
            body=json.dumps(external_api_user_response),
            uri=re.compile('{0}.*'.format(settings.PLACEHOLDER_API_URL)),
        )

        yield external_api_user_response
        assert httpretty.has_request()
