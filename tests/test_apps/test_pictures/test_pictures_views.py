from http import HTTPStatus
from typing import TYPE_CHECKING

from django.db.models.query import QuerySet
from django.urls import reverse

if TYPE_CHECKING:
    from django.test import Client
    from plugins.pictures.picture import ExternalAPIPictureResponse, Picture

    from server.apps.identity.models import User
    from server.apps.pictures.models import FavouritePicture


def test_add_to_favourites(
    user: 'User',
    user_client: 'Client',
    picture_data: 'Picture',
) -> None:
    """Test that user can add picture to favourites."""
    response = user_client.post(
        reverse('pictures:dashboard'),
        data=picture_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert int(picture_data['foreign_id']) in user.pictures.values_list(
        'foreign_id',
        flat=True,
    )


def test_dashboard_page_with_pictures(
    user_client: 'Client',
    picture_external_api_mock: 'ExternalAPIPictureResponse',
) -> None:
    """Test that dashboard page contains pictures from external API."""
    response = user_client.get(reverse('pictures:dashboard'))
    page_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    for picture in picture_external_api_mock:
        assert picture['url'] in page_content


def test_favourite_page(
    user_client: 'Client',
    user_pictures: QuerySet['FavouritePicture'],
) -> None:
    """Test that favourite page contains user pictures."""
    response = user_client.get(reverse('pictures:favourites'))
    page_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    for picture in user_pictures:
        assert picture.url in page_content
