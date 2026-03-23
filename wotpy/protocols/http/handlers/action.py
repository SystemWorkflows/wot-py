#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Request handler for Action interactions.
"""

import json
import logging
import pprint
import time
import uuid

from tornado.web import HTTPError, RequestHandler

import wotpy.protocols.http.handlers.utils as handler_utils


class ActionInvokeHandler(RequestHandler):
    """Handler for Action invocation requests."""

    def initialize(self, http_server):
        self._server = http_server
        self._logr = logging.getLogger(__name__)

    async def post(self, thing_name: str, name: str):
        """Invokes the action and returns the invocation result."""

        exposed_thing = handler_utils.get_exposed_thing(self._server, thing_name)
        sync = exposed_thing.actions[name].synchronous
        print(sync)
        if sync:  # synchronous
            input_value = json.loads(self.request.body)
            result = await exposed_thing.actions[name].invoke(input_value)
            if type(result) == int or type(result) == float or type(result) == bool:
                result = str(result)
            if type(result) == str:
                result = "\"" + result + "\""
            self._logr.debug("Action result: {}".format(result))
            self.write(result)

        else: # asynchronous
            input_value = json.loads(self.request.body)
            future_result = exposed_thing.actions[name].invoke(input_value)
            invocation_id = uuid.uuid4().hex
            self._server.pending_actions[invocation_id] = future_result
            self.write({"invocation": "/invocation/{}".format(invocation_id)})


    async def options(self, thing_name: str, name: str):
        # no body
        # `*args` is for route with `path arguments` supports
        self.set_status(204)
        self.finish()


class PendingInvocationHandler(RequestHandler):
    """Handler to check the status of pending action invocations."""

    def initialize(self, http_server):
        self._server = http_server
        self._logr = logging.getLogger(__name__)

    def _clean_expired(self):
        """Removes the Action invocations that are expired and
        have already been checked by at least one client."""

        now = time.time()

        expired_invocations = [
            inv_id
            for inv_id, tstamp in self._server.invocation_check_times.items()
            if (now - tstamp) > self._server.action_ttl
        ]

        if len(expired_invocations):
            self._logr.debug(
                "Expired invocations: {}".format(pprint.pformat(expired_invocations))
            )

        for invocation_id in expired_invocations:
            self._server.invocation_check_times.pop(invocation_id)
            fut_result = self._server.pending_actions.get(invocation_id, None)

            if fut_result and fut_result.done():
                self._logr.debug(
                    "Removing completed invocation Future: {}".format(invocation_id)
                )

                self._server.pending_actions.pop(invocation_id, None)

    async def get(self, invocation_id):
        """Checks and returns the status of the Future that represents an action invocation."""

        if invocation_id not in self._server.pending_actions:
            raise HTTPError(log_message="Unknown invocation: {}".format(invocation_id))

        try:
            result = await self._server.pending_actions[invocation_id]
            self.write({"done": True, "result": result})
        except Exception as ex:
            self.write({"done": True, "error": str(ex)})
        finally:
            self._logr.debug("Updating invocation check time: {}".format(invocation_id))
            self._server.invocation_check_times[invocation_id] = time.time()
            self._clean_expired()
