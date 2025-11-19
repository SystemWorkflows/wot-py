#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes that represent the JSON and JSON-LD serialization formats of a Thing Description document.
"""

import json
from typing import Any, List

import jsonschema

from wotpy.wot.dictionaries.link import FormDict
from wotpy.wot.dictionaries.thing import ThingFragment
from wotpy.wot.thing import Thing
from wotpy.wot.validation import SCHEMA_THING, InvalidDescription


class ThingDescription(object):
    """Class that represents a Thing Description document.
    Contains logic to validate and transform a Thing to a serialized TD and vice versa.
    """

    def __init__(self, doc: dict | str | bytes):
        """Constructor.
        Validates that the document conforms to the TD schema."""

        self._doc:dict = json.loads(doc) if isinstance(doc, (str, bytes)) else doc
        if("@type" in self._doc):
            if self._doc["@type"] == "tm:ThingModel":
                self._doc["@type"] = "Thing"
            elif self._doc["@type"] is list:
                self._doc["@type"] = list(map(lambda x: "Thing" if x == "tm:ThingModel" else x, self._doc["@type"]))
        else:
            self._doc["@type"] = "Thing"
        

        self._thing_fragment = ThingFragment(self._doc)

        self.validate(doc=self._thing_fragment.to_dict())

    @classmethod
    def validate(cls, doc: dict) -> None:
        """Validates the given Thing Description document against its schema.
        Raises ValidationError if validation fails."""

        try:
            jsonschema.validate(doc, SCHEMA_THING)
        except (jsonschema.ValidationError, TypeError) as ex:
            raise InvalidDescription(str(ex)) from ex

    @classmethod
    def from_thing(cls, thing: Thing) -> ThingDescription:
        """Builds an instance of a JSON-serialized Thing Description from a Thing object."""

        return ThingDescription(thing.thing_fragment.to_dict())

    def __getattr__(self, name: str) -> Any:
        """Search for members that raised an AttributeError in
        the internal ThingFragment before propagating the exception."""

        return getattr(self._thing_fragment, name)

    def to_dict(self) -> dict:
        """Returns the JSON Thing Description as a dict."""

        return self._thing_fragment.to_dict()

    def to_str(self) -> str:
        """Returns the JSON Thing Description as a string."""

        return json.dumps(self._thing_fragment.to_dict())

    def to_thing_fragment(self) -> ThingFragment:
        """Returns a ThingFragment dictionary built from this TD."""

        return self._thing_fragment

    def build_thing(self) -> Thing:
        """Builds a new Thing object from the serialized Thing Description."""

        return Thing(thing_fragment=self.to_thing_fragment())

    def get_forms(self, name: str) -> List[FormDict]:
        """Returns a list of FormDict for the interaction that matches the given name."""

        if name in self.properties:
            return self.get_property_forms(name)

        if name in self.actions:
            return self.get_action_forms(name)

        if name in self.events:
            return self.get_event_forms(name)

        return []

    def get_property_forms(self, name: str) -> List[FormDict]:
        """Returns a list of FormDict for the property that matches the given name."""

        return self.properties[name].forms

    def get_action_forms(self, name: str) -> List[FormDict]:
        """Returns a list of FormDict for the action that matches the given name."""

        return self.actions[name].forms

    def get_event_forms(self, name: str) -> List[FormDict]:
        """Returns a list of FormDict for the event that matches the given name."""

        return self.events[name].forms
