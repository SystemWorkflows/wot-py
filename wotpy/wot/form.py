#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that represents the form entities exposed by interactions.
"""

from typing import Any, TYPE_CHECKING

from wotpy.wot.dictionaries.link import FormDict

if TYPE_CHECKING:
    from wotpy.wot.interaction import InteractionPattern


class Form(object):
    """Communication metadata where a service can be accessed by a client application."""

    def __init__(self, interaction: InteractionPattern, protocol: Any, form_dict: FormDict | None = None, **kwargs):
        self._interaction = interaction
        self._protocol = protocol
        self._form_dict: FormDict = form_dict if form_dict else FormDict(**kwargs)

    def __getattr__(self, name: str) -> Any:
        """Search for members that raised an AttributeError in
        the internal Form init dict before propagating the exception."""

        return getattr(self._form_dict, name)

    @property
    def form_dict(self) -> FormDict:
        """The Form dictionary of this Form."""

        return self._form_dict

    @property
    def interaction(self) -> InteractionPattern:
        """Interaction that contains this Form."""

        return self._interaction

    @property
    def protocol(self) -> Any:
        """Form protocol."""

        return self._protocol

    @property
    def id(self) -> int:
        """Returns the ID of this Form.
        The ID is a hash that is based on the Form attributes.
        No two Forms with the same ID may exist within the same Interaction.
        The ID of a Form could change during its lifetime if some attributes are updated."""

        return hash((
            self.protocol,
            self.href,
            self.content_type,
            tuple(self.op) if isinstance(self.op, list) else self.op
        ))
