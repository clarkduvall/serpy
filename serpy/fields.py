import six
import types
import warnings


class Field(object):
    """:class:`Field` is used to define what attributes will be serialized.

    A :class:`Field` maps a property or function on an object to a value in the
    serialized result. Subclass this to make custom fields. For most simple
    cases, overriding :meth:`Field.to_representation` should give enough
    flexibility. If more control is needed, override :meth:`Field.as_getter`.

    :param str attr: The attribute to get on the object, using the same format
        as ``operator.attrgetter``. If this is not supplied, the name this
        field was assigned to on the serializer will be used.
    :param bool call: Whether the value should be called after it is retrieved
        from the object. Useful if an object has a method to be serialized.
    :param bool required: Whether the field is required. If set to ``False``,
        :meth:`Field.to_representation` will not be called if the value is
        ``None``.
    :param bool read_only: Whether the field is read-only. If set to ``False``,
        the field won't be deserialized. If ``call`` is True, or if ``attr``
        contains a '.', then this param is set to True.
    """
    #: Set to ``True`` if the value function returned from
    #: :meth:`Field.as_getter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    getter_takes_serializer = False

    #: Set to ``True`` if the value function returned from
    #: :meth:`Field.as_setter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    setter_takes_serializer = False

    def __init__(self, attr=None, call=False, required=True, read_only=False):
        self.attr = attr
        self.call = call
        self.required = required
        self.read_only = (read_only or call or
                          (attr is not None and '.' in attr))

    def to_representation(self, value):
        """Transform the serialized value.

        Override this method to clean and validate values serialized by this
        field. For example to implement an ``int`` field: ::

            def to_representation(self, value):
                return int(value)

        :param value: The value fetched from the object being serialized.
        """
        return value
    to_representation._serpy_base_implementation = True

    def _is_to_representation_overridden(self):
        to_representation = self.to_representation
        # If to_representation isn't a method, it must have been overridden.
        if not isinstance(to_representation, types.MethodType):
            return True
        return not getattr(to_representation,
                           '_serpy_base_implementation',
                           False)

    def to_value(self, obj):
        warnings.warn(
            "`.to_value` method is deprecated, use `.to_representation` "
            "instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.to_representation(obj)

    def to_internal_value(self, data):
        """Transform the serialized value into Python object

        Override this method to clean and validate values deserialized by this
        field. For example to implement an ``int`` field: ::

            def to_internal_value(self, data):
                return data

        :param data: The data fetched from the object being deserialized.
        """
        return data
    to_internal_value._serpy_base_implementation = True

    def _is_to_internal_value_overridden(self):
        to_internal_value = self.to_internal_value
        # If to_internal_value isn't a method, it must have been overridden.
        if not isinstance(to_internal_value, types.MethodType):
            return True
        return not getattr(to_internal_value,
                           '_serpy_base_implementation',
                           False)

    def as_getter(self, serializer_field_name, serializer_cls):
        """Returns a function that fetches an attribute from an object.

        Return ``None`` to use the default getter for the serializer defined in
        :attr:`Serializer.default_getter`.

        When a :class:`Serializer` is defined, each :class:`Field` will be
        converted into a getter function using this method. During
        serialization, each getter will be called with the object being
        serialized, and the return value will be passed through
        :meth:`Field.to_representation`.

        If a :class:`Field` has ``getter_takes_serializer = True``, then the
        getter returned from this method will be called with the
        :class:`Serializer` instance as the first argument, and the object
        being serialized as the second.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The :class:`Serializer` this field is a part of.
        """
        return None

    def as_setter(self, serializer_field_name, serializer_cls):
        """Returns a function that sets an attribute on an object

        Return ``None`` to use the default setter for the serializer defined in
        :attr:`Serializer.default_setter`.

        When a :class:`Serializer` is defined, each :class:`Field` will be
        converted into a setter function using this method. During
        deserialization, each setter will be called with the object being
        deserialized with the argument passed as the return value of
        :meth:`Field.to_internal_value`.

        If a :class:`Field` has ``setter_takes_serializer = True``, then the
        setter returned from this method will be called with the
        :class:`Serializer` instance as the first argument, and the object
        being serialized as the second.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The :class:`Serializer` this field is a part of.
        """
        return None


class StrField(Field):
    """A :class:`Field` that converts the value to a string."""
    to_representation = staticmethod(six.text_type)
    to_internal_value = staticmethod(six.text_type)


class IntField(Field):
    """A :class:`Field` that converts the value to an integer."""
    to_representation = staticmethod(int)
    to_internal_value = staticmethod(int)


class FloatField(Field):
    """A :class:`Field` that converts the value to a float."""
    to_representation = staticmethod(float)
    to_internal_value = staticmethod(float)


class BoolField(Field):
    """A :class:`Field` that converts the value to a boolean."""
    to_representation = staticmethod(bool)
    to_internal_value = staticmethod(bool)


class MethodField(Field):
    """A :class:`Field` that calls a method on the :class:`Serializer`.

    This is useful if a :class:`Field` needs to serialize a value that may come
    from multiple attributes on an object. For example: ::

        class FooSerializer(Serializer):
            plus = MethodField()
            minus = MethodField('do_minus')

            def get_plus(self, foo_obj):
                return foo_obj.bar + foo_obj.baz

            def do_minus(self, foo_obj):
                return foo_obj.bar - foo_obj.baz

        foo = Foo(bar=5, baz=10)
        FooSerializer(foo).representation
        # {'plus': 15, 'minus': -5}

    :param str method: The method on the serializer to call. Defaults to
        ``'get_<field name>'``.
    """
    getter_takes_serializer = True
    setter_takes_serializer = True

    def __init__(self, getter=None, setter=None, **kwargs):
        super(MethodField, self).__init__(**kwargs)
        self.getter_method = getter
        self.setter_method = setter

    def as_getter(self, serializer_field_name, serializer_cls):
        method_name = self.getter_method
        if method_name is None:
            method_name = 'get_{0}'.format(serializer_field_name)
        return getattr(serializer_cls, method_name)

    def as_setter(self, serializer_field_name, serializer_cls):
        method_name = self.setter_method
        if method_name is None:
            method_name = 'set_{0}'.format(serializer_field_name)
        return getattr(serializer_cls, method_name, None)
