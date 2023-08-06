import json
import logging
from datetime import datetime
from typing import Any, cast, ClassVar, Dict, Generator, Optional, Type, TypeVar

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import (
    EID,
    EntityClass,
    EntityCreationRequestPayload,
    EntityShortDescription,
    EntityType,
    Response,
    ResponseData,
)
from signals_notebook.jinja_env import env

ChildClass = TypeVar('ChildClass', bound='Entity')

log = logging.getLogger(__name__)


class Entity(BaseModel):
    type: str = Field(allow_mutation=False)
    eid: EID = Field(allow_mutation=False)
    digest: Optional[str] = Field(allow_mutation=False, default=None)
    name: str = Field(title='Name')
    description: Optional[str] = Field(title='Description', default=None)
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    edited_at: datetime = Field(alias='editedAt', allow_mutation=False)
    _template_name: ClassVar = 'entity.html'

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    def __str__(self) -> str:
        return f'<{self.__class__.__name__} eid={self.eid}>'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        raise NotImplementedError

    @classmethod
    def get_subclasses(cls) -> Generator[Type['Entity'], None, None]:
        """Get all Entity subclasses

        Returns:
            One of the Entity subclasses
        """
        log.debug('Get subclasses for: %s', cls.__name__)
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    @classmethod
    def set_template_name(cls, template_name: str) -> None:
        """Set name of the template

        Args:
            template_name: template name

        Returns:

        """
        log.debug('Setting new template for: %s...', cls.__name__)
        cls._template_name = template_name
        log.debug('New template (%s) for %s was set', template_name, cls.__name__)

    @classmethod
    def get_template_name(cls) -> str:
        """Get Entity template name

        Returns:
            Template name
        """
        return cls._template_name

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'entities'

    @classmethod
    def _get_list_params(cls) -> Dict[str, Any]:
        return {
            'include_types': [cls._get_entity_type()],
        }

    @classmethod
    def get_list(cls) -> Generator['Entity', None, None]:
        """Get all entities

        Returns:
            list of entities
        """
        from signals_notebook.entities.entity_store import EntityStore

        return EntityStore.get_list(**cls._get_list_params())

    def delete(self) -> None:
        from signals_notebook.entities.entity_store import EntityStore

        EntityStore.delete(self.eid)
        log.debug('Entity: %s was deleted from EntityStore', self.eid)

    @classmethod
    def _create(cls, *, digest: str = None, force: bool = True, request: EntityCreationRequestPayload) -> EntityClass:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create Entity: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
            json=request.dict(exclude_none=True),
        )
        log.debug('Entity: %s was created.', cls.__name__)

        result = Response[cls](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def refresh(self) -> None:
        """Refresh entity with new changes values

        Returns:

        """
        from signals_notebook.entities import EntityStore

        EntityStore.refresh(self)

    def save(self, force: bool = True) -> None:
        """Update properties of a specified entity.

        Args:
            force: Force to update properties without doing digest check.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Save Entity: %s...', self.eid)

        request_body = []
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                request_body.append(
                    {'attributes': {'name': field.field_info.title, 'value': getattr(self, field.name)}}
                )

        api.call(
            method='PATCH',
            path=(self._get_endpoint(), self.eid, 'properties'),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            json={
                'data': request_body,
            },
        )
        log.debug('Entity: %s was saved.', self.eid)

    @property
    def short_description(self) -> EntityShortDescription:
        """Return EntityShortDescription of Entity

        Returns:
            EntityShortDescription
        """
        return EntityShortDescription(type=self.type, id=self.eid)

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered HTML in string format
        """
        data = {'name': self.name, 'edited_at': self.edited_at, 'type': self.type, 'description': self.description}
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
