from serpy.fields import Field
import six


class SerializerBase(Field):
    _field_map = {}


def _compile_field_to_tuple(field, name, serializer_cls):
    getter = field.as_getter(name, serializer_cls)

    # Only set a transform function if it has been overriden for performance.
    transform = None
    if field._is_transform_value_overriden():
        transform = field.transform_value

    return name, getter, transform, field.call, field.uses_self


class SerializerMeta(type):

    @staticmethod
    def _get_fields(direct_fields, serializer_cls):
        field_map = {}
        # Get all the fields from base classes.
        for cls in serializer_cls.__mro__[::-1]:
            if issubclass(cls, SerializerBase):
                field_map.update(cls._field_map)
        field_map.update(direct_fields)

        compiled_fields = [
            _compile_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
        ]

        return field_map, compiled_fields

    def __new__(cls, name, bases, attrs):
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        field_map, compiled_fields = cls._get_fields(direct_fields, real_cls)

        real_cls._field_map = field_map
        real_cls._compiled_fields = tuple(compiled_fields)
        return real_cls


class Serializer(six.with_metaclass(SerializerMeta, SerializerBase)):
    """:class:`Serializer` is used as a base for custom serializers.

    The :class:`Serializer` class is also a subclass of :class:`Field`, and can
    be used as a :class:`Field` to create nested schemas. A serializer is
    defined by subclassing :class:`Serializer` and adding each :class:`Field`
    as a class variable:

    Example: ::

        class FooSerializer(Serializer):
            foo = Field()
            bar = Field()

        foo = Foo(foo='hello', bar=5)
        FooSerializer(foo).data
        # {'foo': 'hello', 'bar': 5}

    :param obj: The object or objects to serialize.
    :param bool many: If ``obj`` is a collection of objects, set ``many`` to
        ``True`` to serialize to a list.
    """
    def __init__(self, obj=None, many=False, **kwargs):
        super(Serializer, self).__init__(**kwargs)
        self.obj = obj
        self.many = many
        self._data = None

    def _to_value(self, obj, fields):
        v = {}
        for name, getter, transform, call, uses_self in fields:
            if uses_self:
                result = getter(self, obj)
            else:
                result = getter(obj)
                if call:
                    result = result()
                if transform:
                    result = transform(result)
            v[name] = result

        return v

    def transform_value(self, obj):
        fields = self._compiled_fields
        if self.many:
            to_value = self._to_value
            return [to_value(o, fields) for o in obj]
        return self._to_value(obj, fields)

    @property
    def data(self):
        """Get the serialized data from the :class:`Serializer`.

        The data will be cached for future accesses.
        """
        # Cache the data for next time .data is called.
        if self._data is None:
            self._data = self.transform_value(self.obj)
        return self._data
