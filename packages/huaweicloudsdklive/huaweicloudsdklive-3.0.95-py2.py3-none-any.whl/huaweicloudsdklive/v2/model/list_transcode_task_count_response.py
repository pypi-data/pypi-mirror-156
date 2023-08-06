# coding: utf-8

import re
import six


from huaweicloudsdkcore.sdk_response import SdkResponse
from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class ListTranscodeTaskCountResponse(SdkResponse):

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'transcode_data_list': 'list[TranscodeCountData]',
        'x_request_id': 'str'
    }

    attribute_map = {
        'transcode_data_list': 'transcode_data_list',
        'x_request_id': 'X-request-id'
    }

    def __init__(self, transcode_data_list=None, x_request_id=None):
        """ListTranscodeTaskCountResponse

        The model defined in huaweicloud sdk

        :param transcode_data_list: 时间戳及相应时间的数值。
        :type transcode_data_list: list[:class:`huaweicloudsdklive.v2.TranscodeCountData`]
        :param x_request_id: 
        :type x_request_id: str
        """
        
        super(ListTranscodeTaskCountResponse, self).__init__()

        self._transcode_data_list = None
        self._x_request_id = None
        self.discriminator = None

        if transcode_data_list is not None:
            self.transcode_data_list = transcode_data_list
        if x_request_id is not None:
            self.x_request_id = x_request_id

    @property
    def transcode_data_list(self):
        """Gets the transcode_data_list of this ListTranscodeTaskCountResponse.

        时间戳及相应时间的数值。

        :return: The transcode_data_list of this ListTranscodeTaskCountResponse.
        :rtype: list[:class:`huaweicloudsdklive.v2.TranscodeCountData`]
        """
        return self._transcode_data_list

    @transcode_data_list.setter
    def transcode_data_list(self, transcode_data_list):
        """Sets the transcode_data_list of this ListTranscodeTaskCountResponse.

        时间戳及相应时间的数值。

        :param transcode_data_list: The transcode_data_list of this ListTranscodeTaskCountResponse.
        :type transcode_data_list: list[:class:`huaweicloudsdklive.v2.TranscodeCountData`]
        """
        self._transcode_data_list = transcode_data_list

    @property
    def x_request_id(self):
        """Gets the x_request_id of this ListTranscodeTaskCountResponse.


        :return: The x_request_id of this ListTranscodeTaskCountResponse.
        :rtype: str
        """
        return self._x_request_id

    @x_request_id.setter
    def x_request_id(self, x_request_id):
        """Sets the x_request_id of this ListTranscodeTaskCountResponse.


        :param x_request_id: The x_request_id of this ListTranscodeTaskCountResponse.
        :type x_request_id: str
        """
        self._x_request_id = x_request_id

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                if attr in self.sensitive_list:
                    result[attr] = "****"
                else:
                    result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        import simplejson as json
        if six.PY2:
            import sys
            reload(sys)
            sys.setdefaultencoding("utf-8")
        return json.dumps(sanitize_for_serialization(self), ensure_ascii=False)

    def __repr__(self):
        """For `print`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ListTranscodeTaskCountResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
