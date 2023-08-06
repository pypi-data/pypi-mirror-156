import logging
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class PowerPoint(ContentfulEntity):
    type: Literal[EntityType.POWER_POINT] = Field(allow_mutation=False)
    _template_name: ClassVar = 'power_point.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.POWER_POINT

    @classmethod
    def create(cls, *, container: Container, name: str, content: str = '', force: bool = True) -> Entity:
        """Create PowerPoint Entity

        Args:
            container: Container where create new PowerPoint
            name: file name
            content: PowerPoint content
            force: Force to post attachment

        Returns:
            PowerPoint
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)
        return container.add_child(
            name=name,
            content=content.encode('utf-8'),
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            force=force,
        )

    def get_content(self) -> File:
        """Get PowerPoint content

        Returns:
            File
        """
        return super()._get_content()
