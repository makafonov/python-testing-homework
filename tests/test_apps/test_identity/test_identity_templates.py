from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db()
@pytest.mark.parametrize(('fixture_name', 'url', 'template'), [
    ('client', 'identity:login', 'identity/pages/login.html'),
    ('client', 'identity:registration', 'identity/pages/registration.html'),
    ('user_client', 'identity:user_update', 'identity/pages/user_update.html'),
])
def test_pages(
    fixture_name: 'str',
    url: str,
    template: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test the pages."""
    client = request.getfixturevalue(fixture_name)

    response = client.get(reverse(url))

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, template)
