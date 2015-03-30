from serpy.fields import Field
from six.moves import map
import six


class SerializerBase(Field):
    _fields = {}


class SerializerMeta(type):

    @staticmethod
    def _make_field_lists(fields, serializer_cls):
        all_fields = {}
        for cls in serializer_cls.__mro__[::-1]:
            if issubclass(cls, SerializerBase):
                all_fields.update(cls._fields)
        all_fields.update(fields)

        simple_fields = []
        method_fields = []
        for name, field in all_fields.items():
            value_fn = field.to_value_fn(name, serializer_cls)
            if field.uses_self:
                method_fields.append((name, value_fn))
            else:
                simple_fields.append((name, value_fn))

        return all_fields, simple_fields, method_fields

    def __new__(cls, name, bases, attrs):
        fields = {}
        for attr_name, field in six.iteritems(attrs):
            if isinstance(field, Field):
                fields[attr_name] = field
        for k in fields.keys():
            del attrs[k]

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        all_fields, simple_fields, method_fields = cls._make_field_lists(
            fields, real_cls)

        real_cls._fields = all_fields
        real_cls._simple_fields = tuple(simple_fields)
        real_cls._method_fields = tuple(method_fields)
        return real_cls


class Serializer(six.with_metaclass(SerializerMeta, SerializerBase)):

    def __init__(self, obj=None, many=False, **kwargs):
        super(Serializer, self).__init__(**kwargs)
        self.obj = obj
        self.many = many
        self._data = None

    def to_value_fn(self, name, cls):
        value_fn = super(Serializer, self).to_value_fn(name, cls)

        def get_data(x):
            return self._get_data(value_fn(x))
        return get_data

    def _to_value(self, obj):
        v = {}
        for n, f in self._simple_fields:
            v[n] = f(obj)
        for n, f in self._method_fields:
            v[n] = f(self, obj)
        return v

    def _get_data(self, obj):
        if self.many:
            return list(map(self._to_value, obj))
        return self._to_value(obj)

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data(self.obj)
        return self._data
