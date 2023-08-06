from bertdotconfig.logger import Logger
from functools import reduce
from bertdotconfig.struct import Struct

# Setup Logging
logger = Logger().init_logger(__name__)

class ConfigUtils:

    def __init__(self, **kwargs):

        self.dict = kwargs.get('dict_input', {})
        self.logger = logger

    def __iter__(self):
        for key, item in self.dict.items():
            yield key, item

    def keys(self):
        if self.dict:
            return self.dict.keys()
        else:
            return []

    def items(self):
        if self.dict:
            return self.dict.items()
        else:
            return []

    def values(self):
        if self.dict:
            return self.dict.values()
        else:
            return []

    def __setitem__(self, key, value):
        if self.dict:
            if self.dict.get(key):
                self.dict[key] = value
            else:
                return None
        else:
            return None

    def __getitem__(self, key):
        if self.dict:
            if self.dict.get(key):
                self.dict.get(key)
            else:
                return None
        else:
            return None

    # def set_nested_attribute(self, nested_attr_k, nested_attr_v):
    #     if isinstance(dict, nested_attr_v):
    #         self.set_nested_attribute(nested_attr_v)
    #         setattr(self, nested_attr_k)
    #     print(nested_attr_v)

    def set_attributes(self, incoming_obj, **kwargs):
        """ Set attributes on self from key/values in incoming_dict
        :param self: Object onto which the attributes are ascribed
        :param incoming_dct: dictionary object used for the inputs
        :return: None
        """
        nested_attribute = kwargs.get('nested_attribute')
        nested_attribute_is_dict = kwargs.get('nested_attribute_is_dict')
        nested_attribute_is_list = kwargs.get('nested_attribute_is_list')
        children = kwargs.get('children')
        if nested_attribute and nested_attribute_is_dict:
            if hasattr(self, nested_attribute):
                new_nested_attribute = self.merge(self.topics.__dict__, source_dict=incoming_obj)
                setattr(self, nested_attribute, Struct(new_nested_attribute))
            else:
                setattr(self, nested_attribute, Struct(incoming_obj))
        elif nested_attribute and nested_attribute_is_list and not children:
            if len(incoming_obj) > 0:
                self.set_attributes(incoming_obj, nested_attribute=nested_attribute, children=True)
            else:
                setattr(self, nested_attribute, [])
        else:
            if isinstance(incoming_obj, dict) or isinstance(incoming_obj, ConfigUtils) :
                for k, v in incoming_obj.items():
                    in_v = incoming_obj.get(k)
                    attribute_is_dict = isinstance(in_v, dict)
                    attribute_is_list = isinstance(in_v, list)
                    if attribute_is_dict or attribute_is_list:
                        self.set_attributes(
                            in_v, nested_attribute=k,
                            nested_attribute_is_dict=attribute_is_dict,
                            nested_attribute_is_list=attribute_is_list
                        )
                    else:
                        setattr(self, k, in_v)
            if isinstance(incoming_obj, list):
                for e in incoming_obj:
                    attribute_is_dict = isinstance(e, dict)
                    attribute_is_list = isinstance(e, list)
                    if attribute_is_dict or attribute_is_list:
                        self.set_attributes(
                            e, nested_attribute=nested_attribute,
                            nested_attribute_is_dict=attribute_is_dict,
                            nested_attribute_is_list=attribute_is_list
                        )

    def merge(self, incoming_dct, **kwargs):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``incoming_dct`` is merged into
        ``self.dict``.
        :param self.dict: dict onto which the merge is executed
        :param incoming_dct: self.dict merged into self.dict
        :return: merged_dict
        """
        new_dict = kwargs.get('source_dict', self.dict)
        for k, v in incoming_dct.items():
            my_key = new_dict.get(k)
            source_is_dict = isinstance(my_key, dict)
            incoming_is_dict = isinstance(incoming_dct[k], dict)
            if (k in new_dict.keys() and source_is_dict
                    and incoming_is_dict):
                self.merge(my_key, incoming_dct[k])
            else:
                new_dict[k] = incoming_dct[k]
        return new_dict

    def update(self, dict_path, default=None):
        """Interpret wildcard paths for setting values in a dictionary object"""
        result = {}
        if isinstance(self.dict, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, dict_path.split('.'), self.dict)
        return(result)

    def get(self, dict_path, default=None):
        """Interpret wildcard paths for retrieving values from a dictionary object"""

        if isinstance(self.dict, dict):
            if '.*.' in dict_path:
                try:
                    ks = dict_path.split('.*.')
                    if len(ks) > 1:
                        data = []
                        path_string = ks[0]
                        ds = self.recurse(self.dict, path_string)
                        for d in ds:
                            sub_path_string = '{s}.{dd}.{dv}'.format(s=path_string, dd=d, dv=ks[1])
                            self.logger.debug('Path string is: %s' % sub_path_string)
                            result = self.recurse(self.dict, sub_path_string, default)
                            if result:
                                data.append(result)
                        return data
                    else:
                        data = self.recurse(self.dict, dict_path, default)
                        if not isinstance(data, dict):
                            return {}
                except Exception as e:
                    raise(e)
            else:
                data = self.recurse(self.dict, dict_path, default)
                return data
        else:
            self.logger.error('Input must be of type "dict"')
            return {}

    def recurse(self, data_input, keys, default=None):
        """Recursively retrieve values from a dictionary object"""
        result = ''
        if isinstance(data_input, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, keys.split('.'), data_input)
        return(result)

       
