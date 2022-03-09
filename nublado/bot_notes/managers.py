import logging

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('django')


class GroupNoteManager(BaseUserManager):
    def create_group_note(
        self, group_id=None, note_tag=None, message_id=None, content=None, **kwargs
    ):
        if not note_tag:
            raise ValueError(_("Note tag is required."))
        if not group_id:
            raise ValueError(_("Group id is required."))

        if content:
            group_note = self.model(
                note_tag=note_tag,
                group_id=group_id,
                message_id=None,
                content=content
                **kwargs
            )
            group_note.clean()
            group_note.save(using=self._db)
            return group_note
        elif message_id:
            group_note = self.model(
                note_tag=note_tag,
                group_id=group_id,
                message_id=message_id,
                content=None
                **kwargs
            )
            group_note.clean()
            group_note.save(using=self._db)
            return group_note
        else:
            raise ValueError(_("Message id or content is required."))

    def create(
        self, group_id=None, note_tag=None, message_id=None, content=None, **kwargs
    ):
        return self.create_group_note(
            note_tag=note_tag,
            group_id=group_id,
            message_id=message_id,
            content=content,
            **kwargs
        )