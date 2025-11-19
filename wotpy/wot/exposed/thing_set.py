#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that represents a group or set of ExposedThing instances that exist in the same context.
"""

from typing import Dict, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from wotpy.wot.exposed.thing import ExposedThing
    from wotpy.wot.interaction import InteractionPattern


class ExposedThingSet(object):
    """Represents a group of ExposedThing objects.
    A group cannot contain two ExposedThing with the same Thing ID."""

    def __init__(self) -> None:
        self._exposed_things: Dict[str, ExposedThing] = {}

    @property
    def exposed_things(self) -> Iterator[ExposedThing]:
        """A generator that yields all the ExposedThing contained in this group."""

        for exposed_thing in self._exposed_things.values():
            yield exposed_thing

    def contains(self, exposed_thing: ExposedThing) -> bool:
        """Returns True if this group contains the given ExposedThing."""

        return exposed_thing in self._exposed_things.values()

    def add(self, exposed_thing: ExposedThing) -> None:
        """Add a new ExposedThing to this set."""

        if exposed_thing.thing.id in self._exposed_things:
            raise ValueError("Duplicate Exposed Thing: {}".format(exposed_thing.title))

        self._exposed_things[exposed_thing.thing.id] = exposed_thing

    def remove(self, thing_id: str) -> None:
        """Removes an existing ExposedThing by ID.
        The thing_id argument may be the original Thing ID or the URL-safe name."""

        exposed_thing = self.find_by_thing_id(thing_id)

        if exposed_thing is None or exposed_thing.thing.id not in self._exposed_things:
            raise ValueError("Unknown Exposed Thing: {}".format(thing_id))

        self._exposed_things.pop(exposed_thing.thing.id)

    def find_by_thing_id(self, thing_id: str) -> Optional[ExposedThing]:
        """Finds an existing ExposedThing by Thing ID.
        The ID argument may be the original Thing ID or the URL-safe name
        (which is also unique and based on the ID)."""

        def is_match(exp_thing: ExposedThing) -> bool:
            return (
                exp_thing.thing.id == thing_id or exp_thing.thing.url_name == thing_id
            )

        return next(
            (item for item in self._exposed_things.values() if is_match(item)), None
        )

    def find_by_interaction(self, interaction: InteractionPattern) -> Optional[ExposedThing]:
        """Finds the ExposedThing whose Thing contains the given Interaction."""

        def is_match(exp_thing: ExposedThing) -> bool:
            return exp_thing.thing is interaction.thing

        return next(
            (item for item in self._exposed_things.values() if is_match(item)), None
        )
