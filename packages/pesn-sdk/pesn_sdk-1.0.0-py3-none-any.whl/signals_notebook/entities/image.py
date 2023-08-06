import base64 as b64
import logging
import mimetypes
from typing import ClassVar, Literal

from pydantic import Field

from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class Image(ContentfulEntity):
    type: Literal[EntityType.IMAGE_RESOURCE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'image.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.IMAGE_RESOURCE

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content: bytes = b'',
        file_extension: str = '',
        force: bool = True,
    ) -> Entity:
        """Create Image Entity

        Args:
            container: Container where create new Image
            name: file name
            content: Image content
            file_extension: Image extension
            force: Force to post attachment

        Returns:
            Image
        """
        log.debug('Create entity: %s with name: %s in Container: %s', cls.__name__, name, container.eid)

        file_extension = file_extension.replace('.', '')
        content_type = mimetypes.types_map.get(f'.{file_extension}', 'application/octet-stream')
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self, base64: bool = False) -> File:
        """Get Image content

        Args:
            base64: parameter that allows to encode binary data

        Returns:
            File
        """
        file = super()._get_content()
        if base64:
            file.content = b64.b64encode(file.content)

        return file

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {'name': self.name}
        file = self.get_content()
        data['image'] = 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii'))

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
