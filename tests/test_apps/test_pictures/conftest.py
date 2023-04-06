import json
import re
from typing import TYPE_CHECKING, Any, Iterator

import httpretty
import pytest
from django.db.models.query import QuerySet
from mimesis.schema import Schema
from plugins.pictures.picture import ExternalAPIPictureResponse

from server.apps.pictures.models import FavouritePicture

if TYPE_CHECKING:
    from mimesis import Field
    from plugins.pictures.picture import Picture, PictureDataFactory

    from server.apps.identity.models import User


@pytest.fixture()
def picture_data_factory(mimesis_field: 'Field') -> 'PictureDataFactory':
    """Returns factory for fake random picture data."""
    def factory(limit: int = 1) -> list['Picture']:
        schema = Schema(schema=lambda: {
            'foreign_id': mimesis_field('numeric.increment'),
            'url': mimesis_field('internet.uri'),
        })

        return schema.create(iterations=limit)

    return factory


@pytest.fixture()
def picture_data(picture_data_factory: 'PictureDataFactory') -> 'Picture':
    """Returns picture data."""
    return picture_data_factory(limit=1)[0]


@pytest.fixture()
def user_pictures(
    user: 'User',
    picture_data_factory: 'PictureDataFactory',
) -> QuerySet[FavouritePicture]:
    """Returns user pictures."""
    FavouritePicture.objects.bulk_create([
        FavouritePicture(
            foreign_id=picture['foreign_id'],
            url=picture['url'],
            user=user,
        ) for picture in picture_data_factory(limit=3)
    ])

    return user.pictures.all()


@pytest.fixture()
def external_api_picture_response(
    mimesis_field: 'Field',
) -> list['ExternalAPIPictureResponse']:
    """Create fake external API response for users."""
    schema = Schema(schema=lambda: {
        'id': mimesis_field('numeric.increment'),
        'url': mimesis_field('internet.uri'),
    })

    return schema.create(iterations=5)


@pytest.fixture()
def picture_external_api_mock(
    external_api_picture_response: 'ExternalAPIPictureResponse',
    settings: Any,
) -> Iterator['ExternalAPIPictureResponse']:
    """Mock external `/photos` call."""
    with httpretty.httprettized():
        httpretty.register_uri(
            method=httpretty.GET,
            body=json.dumps(external_api_picture_response),
            uri=re.compile('{0}.*'.format(settings.PLACEHOLDER_API_URL)),
        )

        yield external_api_picture_response
        assert httpretty.has_request()
