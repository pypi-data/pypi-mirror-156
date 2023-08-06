# encoding: utf-8
"""
dtalarm.client
------------------

This module contains the create of Dtalarm' teams alarm.
"""
import requests
from plotly.graph_objs._figure import Figure

from .base import BaseCli
from .config import DTAlarmConfig


class TeamsChannelAlarm(BaseCli):

    def __init__(self, secret_key=None, channel_address=None, template=None):
        super(TeamsChannelAlarm, self).__init__()
        self.secret_key = secret_key
        self.template = template
        self.channel_address = channel_address

    def _argsparser(self):
        """
        Parse the parameters assigned to the alarm object.

        The attribute in the images list must be a plotly figure object.
        :return:
        """

        for figure in self.images:
            if isinstance(figure, Figure) is False:
                raise Exception("Images should be a plotly graph object list.")

    def _gen_msgiv2(self):
        """
        Generate a request body with the teams channel template name message+image_v2.

        Detail:
        {
            "secret_key": "",
            "platform": "teams",
            "platform_subitem": "channel",
            "data": {
                "channel_URI": "",
                "template": "message+image_v2",
                "content": {
                    "alarm_title": "",
                    "alarm_type": "",
                    "image_base64": [],
                    "message_title": "",
                    "message_text": "",
                    "buttons": [],
                    "table": df.to_json()
                },
                "severity": 0,
                "additional_functions": [],
                "status_buttons": []
            }
        }
        :return:
        """
        self._argsparser()
        payload = {
            "secret_key": self.secret_key,
            "platform": "teams",
            "platform_subitem": "channel",
            "data": {
                "channel_URI": self.channel_address,
                "template": "message+image_v2",
                "content": {}
            }
        }

        # fill data.content
        if self.title:
            payload["data"]["content"]["alarm_title"] = self.title
        if self.message_title:
            payload["data"]["content"]["message_title"] = self.message_title
        if self.message_text:
            payload["data"]["content"]["message_text"] = self.message_text
        if self.images:
            images = self._compression_img(self.images)
            payload["data"]["content"]["image_base64"] = images
        if self.type:
            payload["data"]["content"]["alarm_type"] = self.type
        if self.buttons:
            payload["data"]["content"]["buttons"] = self.buttons
        if self.table:
            payload["data"]["content"]["table"] = self.table

        # fill data.*
        if self.severity is not None:
            payload["data"]["severity"] = self.severity
        if self.status_buttons:
            payload["data"]["status_buttons"] = self.status_buttons
        if self.additional_functions is not None:
            payload["data"]["additional_functions"] = self.additional_functions

        return payload

    def send(self, timeout=None):
        """
        :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :return: :class:`Response <Response>` object
        """
        payload = self._gen_kwargs()
        kwarg = {"json": payload}
        if timeout is not None:
            kwarg.update({"timeout": timeout})
        response = requests.post(DTAlarmConfig.SERVER, **kwarg)
        return response


class TeamsPersonalAlarm(BaseCli):

    def __init__(self, secret_key=None, accepter=None, template=None):
        super(TeamsPersonalAlarm, self).__init__()
        self.secret_key = secret_key
        self.template = template
        self.accepter = accepter

    def _argsparser(self):
        """
        Parse the parameters assigned to the alarm object.

        The attribute in the images list must be a plotly figure object.
        Aaccepter need to be a list, and the maximum number cannot exceed 10.
        :return:
        """

        if isinstance(self.accepter, list) is False:
            raise Exception("Accpter should be a list.")

        if len(self.accepter) > DTAlarmConfig.MAX_ACCEPTER or len(self.accepter) < 1:
            raise Exception("Accpter should have at least 1 person and at most 10 persons.")

        for figure in self.images:
            if isinstance(figure, Figure) is False:
                raise Exception("Images should be a plotly graph object list.")

    def _gen_msgiv2(self):
        """
        Generate a request body with the teams personal template name message+image_v2.

        Detail:
        {
            "secret_key": "",
            "platform": "teams",
            "platform_subitem": "personal",
            "data": {
                "accepter": "",
                "template": "message+image_v2",
                "content": {
                    "alarm_title": "",
                    "alarm_type": "",
                    "image_base64": [],
                    "message_title": "",
                    "message_text": "",
                    "buttons": [],
                    "table": df.to_json()
                },
                "severity": 0,
                "additional_functions": [],
                "status_buttons": []
            }
        }
        :return:
        """

        self._argsparser()
        payload = {
            "secret_key": self.secret_key,
            "platform": "teams",
            "platform_subitem": "personal",
            "data": {
                "accepter": self.accepter,
                "template": "message+image_v2",
                "content": {}
            }
        }

        # fill data.content
        if self.title:
            payload["data"]["content"]["alarm_title"] = self.title
        if self.message_title:
            payload["data"]["content"]["message_title"] = self.message_title
        if self.message_text:
            payload["data"]["content"]["message_text"] = self.message_text
        if self.images:
            images = self._compression_img(self.images)
            payload["data"]["content"]["image_base64"] = images
        if self.type:
            payload["data"]["content"]["alarm_type"] = self.type
        if self.buttons:
            payload["data"]["content"]["buttons"] = self.buttons
        if self.table:
            payload["data"]["content"]["table"] = self.table

        # fill data.*
        if self.severity is not None:
            payload["data"]["severity"] = self.severity
        if self.status_buttons:
            payload["data"]["status_buttons"] = self.status_buttons
        if self.additional_functions is not None:
            payload["data"]["additional_functions"] = self.additional_functions

        return payload

    def send(self, timeout=None):
        """
        :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :return: :class:`Response <Response>` object
        """
        payload = self._gen_kwargs()
        kwarg = {"json": payload}
        if timeout is not None:
            kwarg.update({"timeout": timeout})

        response = requests.post(DTAlarmConfig.SERVER, **kwarg)
        return response
