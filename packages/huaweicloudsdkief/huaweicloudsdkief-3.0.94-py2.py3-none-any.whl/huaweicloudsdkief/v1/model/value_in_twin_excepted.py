# coding: utf-8

import re
import six



from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class ValueInTwinExcepted:

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'value': 'str',
        'metadata': 'ValueInTwinExceptedMetadata'
    }

    attribute_map = {
        'value': 'value',
        'metadata': 'metadata'
    }

    def __init__(self, value=None, metadata=None):
        """ValueInTwinExcepted

        The model defined in huaweicloud sdk

        :param value: 动态属性的初始值，最大长度512， value允许英文字母、数字、下划线、中划线、点、逗号、冒号、/、@、#
        :type value: str
        :param metadata: 
        :type metadata: :class:`huaweicloudsdkief.v1.ValueInTwinExceptedMetadata`
        """
        
        

        self._value = None
        self._metadata = None
        self.discriminator = None

        self.value = value
        if metadata is not None:
            self.metadata = metadata

    @property
    def value(self):
        """Gets the value of this ValueInTwinExcepted.

        动态属性的初始值，最大长度512， value允许英文字母、数字、下划线、中划线、点、逗号、冒号、/、@、#

        :return: The value of this ValueInTwinExcepted.
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this ValueInTwinExcepted.

        动态属性的初始值，最大长度512， value允许英文字母、数字、下划线、中划线、点、逗号、冒号、/、@、#

        :param value: The value of this ValueInTwinExcepted.
        :type value: str
        """
        self._value = value

    @property
    def metadata(self):
        """Gets the metadata of this ValueInTwinExcepted.


        :return: The metadata of this ValueInTwinExcepted.
        :rtype: :class:`huaweicloudsdkief.v1.ValueInTwinExceptedMetadata`
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this ValueInTwinExcepted.


        :param metadata: The metadata of this ValueInTwinExcepted.
        :type metadata: :class:`huaweicloudsdkief.v1.ValueInTwinExceptedMetadata`
        """
        self._metadata = metadata

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
        if not isinstance(other, ValueInTwinExcepted):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
