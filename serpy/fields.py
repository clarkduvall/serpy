from operator import attrgetter
import six
import types


class Field(object):
    uses_self = False

    def __init__(self, attr=None, call=False):
        self.attr = attr
        self.call = call

    def transform_value(self, value):
        return value
    transform_value._base_implementation = True

    def _is_transform_overriden(self):
        transform = self.transform_value
        if not isinstance(transform, types.MethodType):
            return True
        return not getattr(transform, '_base_implementation', False)

    def to_value_fn(self, serializer_field_name, serializer_cls):
        attr_name = self.attr
        if attr_name is None:
            attr_name = serializer_field_name
        basic_getter = attrgetter(attr_name)

        transform = None
        if self._is_transform_overriden():
            transform = self.transform_value

        if self.call:
            getter = lambda x: basic_getter(x)()
        else:
            getter = basic_getter
        return getter, transform


class StrField(Field):
    transform_value = staticmethod(six.text_type)


class IntField(Field):
    transform_value = staticmethod(int)


class FloatField(Field):
    transform_value = staticmethod(float)


class BooleanField(Field):
    transform_value = staticmethod(bool)


class MethodField(Field):
    uses_self = True

    def __init__(self, method=None, **kwargs):
        super(MethodField, self).__init__(**kwargs)
        self.method = method

    def to_value_fn(self, serializer_field_name, serializer_cls):
        method_name = self.method
        if method_name is None:
            method_name = 'get_{0}'.format(serializer_field_name)
        return getattr(serializer_cls, method_name), None
