# coding: utf-8

import re
import six



from huaweicloudsdkcore.utils.http_utils import sanitize_for_serialization


class TwinUpdateDetail:

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """

    sensitive_list = []

    openapi_types = {
        'twin': 'ValueInTwin',
        'property_visitors': 'TwinUpdateDetailPropertyVisitors'
    }

    attribute_map = {
        'twin': 'twin',
        'property_visitors': 'property_visitors'
    }

    def __init__(self, twin=None, property_visitors=None):
        """TwinUpdateDetail

        The model defined in huaweicloud sdk

        :param twin: 
        :type twin: :class:`huaweicloudsdkief.v1.ValueInTwin`
        :param property_visitors: 
        :type property_visitors: :class:`huaweicloudsdkief.v1.TwinUpdateDetailPropertyVisitors`
        """
        
        

        self._twin = None
        self._property_visitors = None
        self.discriminator = None

        if twin is not None:
            self.twin = twin
        if property_visitors is not None:
            self.property_visitors = property_visitors

    @property
    def twin(self):
        """Gets the twin of this TwinUpdateDetail.


        :return: The twin of this TwinUpdateDetail.
        :rtype: :class:`huaweicloudsdkief.v1.ValueInTwin`
        """
        return self._twin

    @twin.setter
    def twin(self, twin):
        """Sets the twin of this TwinUpdateDetail.


        :param twin: The twin of this TwinUpdateDetail.
        :type twin: :class:`huaweicloudsdkief.v1.ValueInTwin`
        """
        self._twin = twin

    @property
    def property_visitors(self):
        """Gets the property_visitors of this TwinUpdateDetail.


        :return: The property_visitors of this TwinUpdateDetail.
        :rtype: :class:`huaweicloudsdkief.v1.TwinUpdateDetailPropertyVisitors`
        """
        return self._property_visitors

    @property_visitors.setter
    def property_visitors(self, property_visitors):
        """Sets the property_visitors of this TwinUpdateDetail.


        :param property_visitors: The property_visitors of this TwinUpdateDetail.
        :type property_visitors: :class:`huaweicloudsdkief.v1.TwinUpdateDetailPropertyVisitors`
        """
        self._property_visitors = property_visitors

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
        if not isinstance(other, TwinUpdateDetail):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
