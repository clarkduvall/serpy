import operator
import six

from serpy.fields import Field


class SerializerBase(Field):
    pass


def _compile_read_field_to_tuple(field, name, serializer_cls):
    getter = field.as_getter(name, serializer_cls)
    if getter is None:
        getter = serializer_cls._meta.default_getter(field.attr or name)

    # Only set a to_representation function if it has been overridden
    # for performance.
    to_representation = None
    if field._is_to_representation_overridden():
        to_representation = field.to_representation

    return (name, getter, to_representation, field.call, field.required,
            field.getter_takes_serializer)


def _compile_write_field_to_tuple(field, name, serializer_cls):
    setter = field.as_setter(name, serializer_cls)
    if setter is None:
        setter = serializer_cls._meta.default_setter(field.attr or name)

    # Only set a to_internal_value function if it has been overridden
    # for performance.
    to_internal_value = None
    if field._is_to_internal_value_overridden():
        to_internal_value = field.to_internal_value

    return (name, setter, to_internal_value, field.call, field.required,
            field.setter_takes_serializer)


class SerializerMeta(type):

    @staticmethod
    def _compile_meta(direct_fields, serializer_meta, serializer_cls):
        field_map = {}
        meta_bases = ()
        # Get all the fields from base classes.
        for cls in serializer_cls.__bases__[::-1]:
            if issubclass(cls, SerializerBase) and cls is not SerializerBase:
                field_map.update(cls._meta._field_map)
                meta_bases = meta_bases + (type(cls._meta),)
        field_map.update(direct_fields)
        if serializer_meta:
            meta_bases = meta_bases + (serializer_meta,)

        # get the right order of meta bases
        meta_bases = meta_bases[::-1]

        compiled_read_fields = [
            _compile_read_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
            ]

        compiled_write_fields = [
            _compile_write_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
            if not field.read_only
            ]

        # automatically create an inner-class Meta that inherits from
        # parent class's inner-class Meta
        Meta = type('Meta', meta_bases, {})
        meta = Meta()
        meta._field_map = field_map
        meta._compiled_read_fields = compiled_read_fields
        meta._compiled_write_fields = compiled_write_fields

        return meta

    def __new__(cls, name, bases, attrs):
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        serializer_meta = attrs.pop('Meta', None)

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        real_cls._meta = cls._compile_meta(
            direct_fields, serializer_meta, real_cls
        )

        return real_cls


@staticmethod
def attrsetter(attr_name):
    """
    attrsetter(attr) --> attrsetter object

    Return a callable object that sets the given attribute(s) on its first
    operand as the second operand
    After f = attrsetter('name'), the call f(o, val) executes: o.name = val
    """
    def _attrsetter(obj, val):
        setattr(obj, attr_name, val)
    return _attrsetter


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
        FooSerializer(instance=foo).data
        # {'foo': 'hello', 'bar': 5}

    A particular Serializer object can either serialize or deserialize, but
    not both.

    :param instance: The object or objects to serialize.
    :param data: The data to deserialize.
    :param klass: The class for instantiating the deserialized object
    :param bool many: If ``obj`` is a collection of objects, set ``many`` to
        ``True`` to serialize to a list.
    """
    # Inner-class
    class Meta(object):
        cls = None
        default_getter = operator.attrgetter
        default_setter = attrsetter

    def __init__(self, instance=None, data=None, many=False, **kwargs):
        super(Serializer, self).__init__(**kwargs)
        self._can_serialize = instance is not None
        self._can_deserialize = not self._can_serialize and data is not None
        if self._can_serialize:
            self._initial_instance = instance
            self._data = None
        elif self._can_deserialize:
            self._initial_data = data
            self._instance = None
        self.many = many

    def _serialize(self, obj, fields):
        v = {}
        for name, getter, to_repr, call, required, pass_self in fields:
            if pass_self:
                result = getter(self, obj)
            else:
                result = getter(obj)
                if required or result is not None:
                    if call:
                        result = result()
                    if to_repr:
                        result = to_repr(result)
            v[name] = result

        return v

    def _deserialize(self, data, fields):
        v = self._meta.cls()
        for name, setter, to_internal, call, required, pass_self in fields:
            if pass_self:
                setter(self, v, data[name])
            else:
                if required:
                    value = data[name]
                else:
                    value = data.get(name)
                if to_internal and (required or value is not None):
                    value = to_internal(value)
                setter(v, value)
        return v

    def to_representation(self, obj):
        fields = self._meta._compiled_read_fields
        if self.many:
            serialize = self._serialize
            return [serialize(o, fields) for o in obj]
        return self._serialize(obj, fields)

    def to_internal_value(self, data):
        fields = self._meta._compiled_write_fields
        if self.many:
            deserialize = self._deserialize
            return [deserialize(o, fields) for o in data]
        return self._deserialize(data, fields)

    @property
    def data(self):
        """Get the serialized data from the :class:`Serializer`.

        The return value will be cached for future accesses.
        """
        # Cache the data for next time .data is called.
        if self._data is None:
            self._data = self.to_representation(self._initial_instance)
        return self._data

    @property
    def deserialized_value(self):
        """Get the deserialized value from the :class:`Serializer`.

        The return value will be cached for future accesses.
        """
        # Cache the deserialized_value for next time .deserialized_value is
        # called.
        if self._instance is None:
            self._instance = self.to_internal_value(self._initial_data)
        return self._instance


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
        FooSerializer(instance=foo).data
        # {'foo': 5, 'bar': 2.2}
    """
    class Meta:
        default_getter = operator.itemgetter
