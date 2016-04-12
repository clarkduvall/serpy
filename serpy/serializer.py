from serpy.fields import Field
import operator
import six


class SerializerBase(Field):
    _field_map = {}


def _compile_field_to_tuple(field, name, serializer_cls):
    getter = field.as_getter(name, serializer_cls)
    if getter is None:
        getter = serializer_cls.default_getter(field.attr or name)

    # Only set a to_value function if it has been overridden for performance.
    to_value = None
    if field._is_to_value_overridden():
        to_value = field.to_value

    # Set the field name to a supplied label; defaults to the attribute name.
    name = field.label or name

    return (name, getter, to_value, field.call, field.required,
            field.getter_takes_serializer)


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

    :param instance: The object or objects to serialize.
    :param bool many: If ``instance`` is a collection of objects, set ``many``
        to ``True`` to serialize to a list.
    :param context: Currently unused parameter for compatability with Django
        REST Framework serializers.
    """
    #: The default getter used if :meth:`Field.as_getter` returns None.
    default_getter = operator.attrgetter

    def __init__(self, instance=None, many=False, data=None, context=None,
                 **kwargs):
        if data is not None:
            raise RuntimeError(
                'serpy serializers do not support input validation')

        super(Serializer, self).__init__(**kwargs)
        self.instance = instance
        self.many = many
        self._data = None

    def _serialize(self, instance, fields):
        v = {}
        for name, getter, to_value, call, required, pass_self in fields:
            if pass_self:
                result = getter(self, instance)
            else:
                result = getter(instance)
                if required or result is not None:
                    if call:
                        result = result()
                    if to_value:
                        result = to_value(result)
            v[name] = result

        return v

    def to_value(self, instance):
        fields = self._compiled_fields
        if self.many:
            serialize = self._serialize
            return [serialize(o, fields) for o in instance]
        return self._serialize(instance, fields)

    @property
    def data(self):
        """Get the serialized data from the :class:`Serializer`.

        The data will be cached for future accesses.
        """
        # Cache the data for next time .data is called.
        if self._data is None:
            self._data = self.to_value(self.instance)
        return self._data


class DictSerializer(Serializer):
    """:class:`DictSerializer` serializes python ``dicts`` instead of objects.

    Instead of the serializer's fields fetching data using
    ``operator.attrgetter``, :class:`DictSerializer` uses
    ``operator.itemgetter``.

    Example: ::

        class FooSerializer(DictSerializer):
            foo = IntField()
            bar = FloatField()

        foo = {'foo': '5', 'bar': '2.2'}
        FooSerializer(foo).data
        # {'foo': 5, 'bar': 2.2}
    """
    default_getter = operator.itemgetter
