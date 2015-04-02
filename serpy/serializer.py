from serpy.fields import Field
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

        function_fields = []
        method_fields = []
        for name, field in all_fields.items():
            value_fn = field.get_value_fn(name, serializer_cls)
            transform = None
            if field._is_transform_value_overriden():
                transform = field.transform_value

            if field.uses_self:
                method_fields.append((name, value_fn))
            else:
                function_fields.append((name, value_fn, transform))

        return all_fields, function_fields, method_fields

    def __new__(cls, name, bases, attrs):
        fields = {}
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                fields[attr_name] = field
        for k in fields.keys():
            del attrs[k]

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        all_fields, function_fields, method_fields = cls._make_field_lists(
            fields, real_cls)

        real_cls._fields = all_fields
        real_cls._function_fields = tuple(function_fields)
        real_cls._method_fields = tuple(method_fields)
        return real_cls


class Serializer(six.with_metaclass(SerializerMeta, SerializerBase)):

    def __init__(self, obj=None, many=False, **kwargs):
        super(Serializer, self).__init__(**kwargs)
        self.obj = obj
        self.many = many
        self._data = None

    def _to_value(self, obj, function_fields, method_fields):
        v = {}
        for name, getter, transform in function_fields:
            r = getter(obj)
            if transform:
                r = transform(r)
            v[name] = r
        for name, getter in method_fields:
            v[name] = getter(self, obj)
        return v

    def transform_value(self, obj):
        function_fields = self._function_fields
        method_fields = self._method_fields
        if self.many:
            to_value = self._to_value
            return [to_value(o, function_fields, method_fields) for o in obj]
        return self._to_value(obj, function_fields, method_fields)

    @property
    def data(self):
        if self._data is None:
            self._data = self.transform_value(self.obj)
        return self._data
