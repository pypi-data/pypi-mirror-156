# encoding: utf-8
"""
dtalarm.base
------------------

This module contains the base functions of Dtalarm' teams alarm.
"""

import base64
import io
import os
import time
from PIL import Image
from base64 import b64encode
import plotly.graph_objects as go


class BaseCli:

    def __init__(self):
        self.compress_img = True

        self.title = ""
        self.text = ""
        self.table = {}
        self.message_title = ""
        self.message_text = ""
        self.type = ""
        self.images = []
        self.buttons = []
        self.status_buttons = []
        self.additional_functions = None
        self.severity = None

    def _compression_img(self, images):
        """
        Compress the images property of the alarm object,
        By default, a plotly firgure object is converted to a webp format encoding,

        If the compress_img attribute is False, the converted webp encoding will be used directly,
        Otherwise, the webp encoding will continue to be compressed until the size of each encoding is less than 15kb.

        During resize compression, the encoding size after each compression is 3/4 of the original.
        :param images: images list, member must be figure object.
        :return: compressed image list.
        """
        for index, figure in enumerate(images):
            images[index] = self.fig2img64(figure)

        if self.compress_img is False:
            return images

        ans = []
        for x in images:
            if self.check_img_size(x) > 15:
                # Figure is still > 15kB after being converted to webp image, perform the resize operation.

                # webp_img_encode, width, height = self.to_webp(x)
                webp_img_encode = x
                width, height = self._find_W_H(x)

                while self.check_img_size(webp_img_encode) > 15:
                    # Still > 15kb, width and height reduced by 1/4.
                    webp_img_encode, width, height = self.figure_resize(webp_img_encode, width * 0.75, height * 0.75)
                    # webp_img_encode, width, height = self.pil_resize(webp_img_encode, width * 0.75, height * 0.75)

                    # Reduced size: self.check_img_size(webp_img_encode),  width and height is: width, height
                ans.append(webp_img_encode)
            else:
                # Figure <= 15kb after converting to webp image.
                ans.append(x)

        return ans

    def _gen_kwargs(self):
        """
        Generate alarm request body corresponding to each template.
            - message_only_v1
            - message+image_v1
            - message+image_v2
        :return:
        """
        if self.template == "message_only_v1":
            return self._gen_msgov1()
        elif self.template == "message+image_v1":
            return self._gen_msgiv1()
        elif self.template == "message+image_v2":
            return self._gen_msgiv2()

    def _gen_msgov1(self):
        """
        Generate a request body with template name message_only_v1.
            - teams channel
            - teams personal

        Detail:
        {
            "secret_key": "",
            "platform": "teams",
            "platform_subitem": "channel",
            "data": {
                "channel_URI": "",
                "template": "message_only_v1",
                "content": {
                    "title": "",
                    "sub_title": "",
                    "table": df.to_json(),
                    "alarm_type": "",
                },
                "severity": 0,
                "additional_functions": ["valid_alarm_button", "invalid_alarm_button", "respond_button"],
                "status_buttons": ["Processing", "Processed"]
            }
        }
        :return:
        """
        payload = {
            "secret_key": self.secret_key,
            "platform": "teams",
            "platform_subitem": "channel",
            "data": {
                "channel_URI": self.channel_address,
                "template": "message_only_v1",
                "content": {}
            }
        }

        # fill data.content
        if self.title:
            payload["data"]["content"]["title"] = self.title
        if self.text:
            payload["data"]["content"]["sub_title"] = self.text
        if self.table:
            payload["data"]["content"]["table"] = self.table
        if self.type:
            payload["data"]["content"]["alarm_type"] = self.type

        # fill data.*
        if self.severity is not None:
            payload["data"]["severity"] = self.severity
        if self.status_buttons:
            payload["data"]["status_buttons"] = self.status_buttons
        if self.additional_functions is not None:
            payload["data"]["additional_functions"] = self.additional_functions

        return payload

    def _gen_msgiv1(self):
        """
        Generate a request body with template name message+image_v1.
            - teams channel
            - teams personal

        Detail:
        {
            "secret_key": "",
            "platform": "teams",
            "platform_subitem": "channel",
            "data": {
                "channel_URI": "",
                "template": "message+image_v1",
                "content": {
                    "alarm_title": "",
                    "alarm_type": "",
                    "image_base64": [],
                    "message_title": "",
                    "message_text": "",
                    "buttons": []
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
                "template": "message+image_v1",
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

        # fill data.*
        if self.severity is not None:
            payload["data"]["severity"] = self.severity
        if self.status_buttons:
            payload["data"]["status_buttons"] = self.status_buttons
        if self.additional_functions is not None:
            payload["data"]["additional_functions"] = self.additional_functions

        return payload

    def to_webp(self, base64_string):
        """
        Convert a base64 image encoding to webp format encoding.
        :param base64_string:
        :return: (webp decode, w, h)
        """
        header, img_string = base64_string.split(',')

        # PIL 转 webp
        fp2 = io.BytesIO()
        with io.BytesIO(base64.b64decode(img_string)) as iobj:
            im = Image.open(iobj)
            im.save(fp2, "WEBP")  # webp write
            width, height = im.size
            webp_string = base64.b64encode(fp2.getvalue()).decode()

        webp_base64 = header + ',' + webp_string
        return webp_base64, width, height

    def _find_W_H(self, base64_string):
        """
        Find the height and width of this base64 image.
        :param base64_string:
        :return: (w, h)
        """
        header, img_string = base64_string.split(',')

        with io.BytesIO(base64.b64decode(img_string)) as iobj:
            im = Image.open(iobj)
            width, height = im.size
        return width, height

    def check_img_size(self, base64_str):
        """
        calculate base64 string size,
        :param base64_str: a base64 string
        :return: kb size
        """
        return len(base64_str) * 0.75 / 1024

    def fig2img64(self, fig):
        """
        Figure object transfer type=webp base64 decode,
        use default style for to image, and allow self definition of figure style.
        :param fig: Plotly figure object
        :return: base64, include file header.
        """

        img_bytes = fig.to_image(format="webp", engine="kaleido")
        encoding = b64encode(img_bytes).decode()
        webp_img_encode = "data:image/webp;base64," + encoding

        return webp_img_encode

    def figure_resize(self, webp_string,  width, height):
        """
        Return the webp of the specified width and height.
        :param webp_string: figure webp base64 string
        :param width: required width
        :param height: required height
        :return:
        """
        fig = go.Figure(go.Image(source=webp_string))

        # strictly required that no paper area exists in the figure after resize.
        fig.update_layout(
            autosize=False,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=0
            )
        )
        fig.update_yaxes(showticklabels=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update_layout(width=width, height=height)

        webp_img_encode = self.fig2img64(fig)
        return webp_img_encode, width, height

    def pil_resize(self, webp_string,  width, height):
        """
        Resize using PIL's method.
        :param webp_string: image encoding to be compressed
        :param width: image width after compression
        :param height: image width after compression
        :return:
        """
        header, img_string = webp_string.split(',')

        # PIL 转 webp
        fp2 = io.BytesIO()
        with io.BytesIO(base64.b64decode(img_string)) as iobj:
            im = Image.open(iobj)
            out = im.resize((int(width), int(height)), Image.ANTIALIAS)
            out.save(fp2, "WEBP")  # webp write
            width, height = out.size
            webp_string = base64.b64encode(fp2.getvalue()).decode()

        webp_base64 = header + ',' + webp_string
        return webp_base64, width, height

    def _argsparser(self):
        """
        Parse the parameters assigned to the alarm object.
        :return:
        """
        pass
