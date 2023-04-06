from typing import Protocol, TypedDict, final

from typing_extensions import TypeAlias


class Picture(TypedDict, total=False):
    """Represents the picture data."""

    foreign_id: str
    url: str


@final
class PictureDataFactory(Protocol):  # type: ignore[misc]
    """Picture data factory protocol."""

    def __call__(
        self,
        limit: int,
    ) -> list[Picture]:
        """Creates picture data."""


@final
class ExternalAPIPicture(TypedDict, total=False):
    """Represents the external API picture."""

    id: int
    url: str


ExternalAPIPictureResponse: TypeAlias = list[ExternalAPIPicture]
