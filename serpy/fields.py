from operator import attrgetter
import six
import types


class Field(object):
    """:class:`Field` is used to define what attributes will be serialized.

    A :class:`Field` maps a property or function on an object to a value in the
    serialized result. Subclass this to make custom fields. For most simple
    cases, overriding :meth:`Field.transform_value` should give enough
    flexibility. If more control is needed, override :meth:`Field.as_getter`.

    :param str attr: The attribute to get on the object, using the same format
        as ``operator.attrgetter``. If this is not supplied, the name this
        field was assigned to on the serializer will be used.
    :param bool call: Whether the value should be called after it is retrieved
        from the object. Useful if an object has a method to be serialized.
    """
    #: Set to ``True`` if the value function returned from
    #: :meth:`Field.as_getter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    uses_self = False

    def __init__(self, attr=None, call=False):
        self.attr = attr
        self.call = call

    def transform_value(self, value):
        """Transform the serialized value.

        Override this method to clean and validate values serialized by this
        field. For example to implement an ``int`` field: ::

            def transform_value(self, value):
                return int(value)

        :param value: The value fetched from the object being serialized.
        """
        return value
    transform_value._serpy_base_implementation = True

    def _is_transform_value_overriden(self):
        transform = self.transform_value
        # If transform isn't a method, it must have been overriden.
        if not isinstance(transform, types.MethodType):
            return True
        return not getattr(transform, '_serpy_base_implementation', False)

    def as_getter(self, serializer_field_name, serializer_cls):
        """Returns a function that fetches an attribute from an object.

        When a :class:`Serializer` is defined, each :class:`Field` will be
        converted into a getter function using this method. During
        serialization, each getter will be called with the object being
        serialized, and the return value will be passed through
        :meth:`Field.transform_value`.

        If a :class:`Field` has ``uses_self = True``, then the getter returned
        from this method will be called with the :class:`Serializer` instance
        as the first argument, and the object being serialized as the second.
        Otherwise the getter will be called with the object as the only
        argument.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The :class:`Serializer` this field is a part of.
        """
        attr_name = self.attr
        if attr_name is None:
            attr_name = serializer_field_name
        return attrgetter(attr_name)


class StrField(Field):
    """A :class:`Field` that converts the value to a string."""
    transform_value = staticmethod(six.text_type)


class IntField(Field):
    """A :class:`Field` that converts the value to an integer."""
    transform_value = staticmethod(int)


class FloatField(Field):
    """A :class:`Field` that converts the value to a float."""
    transform_value = staticmethod(float)


class BooleanField(Field):
    """A :class:`Field` that converts the value to a boolean."""
    transform_value = staticmethod(bool)


class MethodField(Field):
    """A :class:`Field` that calls a method on the :class:`Serializer`.

    This is useful if a :class:`Field` needs to serialize a value that may come
    from multiple attributes on an object. For example: ::

        class FooSerializer(Serializer):
            foo = MethodField()

            def get_foo(self, foo_obj):
                return foo_obj.bar + foo_obj.baz

        foo = Foo(bar=5, baz=10)
        FooSerializer(foo).data
        # {'foo': 15}

    :param str method: The method on the serializer to call. Defaults to
        ``'get_<field name>'``.
    """
    uses_self = True

    def __init__(self, method=None, **kwargs):
        super(MethodField, self).__init__(**kwargs)
        self.method = method

    def as_getter(self, serializer_field_name, serializer_cls):
        method_name = self.method
        if method_name is None:
            method_name = 'get_{0}'.format(serializer_field_name)
        return getattr(serializer_cls, method_name)
