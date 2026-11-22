*************
Custom Fields
*************

The most common way to create a custom field with **serpy** is to override
:meth:`serpy.Field.to_value`. This method is called on the value
retrieved from the object being serialized. For example, to create a field that
adds 5 to every value it serializes, do:

.. code-block:: python

   class Add5Field(serpy.Field):
      def to_value(self, value):
         return value + 5

Then to use it:

.. code-block:: python

   class Obj(object):
      pass

   class ObjSerializer(serpy.Serializer):
      foo = Add5Field()

   f = Obj()
   f.foo = 9
   ObjSerializer(f).data
   # {'foo': 14}

Another use for custom fields is data validation. For example, to validate that
every serialized value has a ``'.'`` in it:

.. code-block:: python

   class ValidateDotField(serpy.Field):
      def to_value(self, value):
         if '.' not in value:
            raise ValidationError('no dot!')
         return value

For more control over the behavior of the field, override
:meth:`serpy.Field.as_getter`. When the :class:`serpy.Serializer` class is
created, each field will be compiled to a getter, that will be called to get its
associated attribute from the object. For an example of this, see the
:meth:`serpy.MethodField` implementation.

Reusable Date and Datetime Fields
=================================

To serialize dates and datetimes, define a reusable field that calls
``isoformat()``. The same field can be declared on several serializers or
used for multiple attributes without repeating a ``MethodField`` method:

>>> import datetime
>>> import serpy
>>> class ISODateField(serpy.Field):
...     def to_value(self, value):
...         return None if value is None else value.isoformat()
...
>>> class EventSerializer(serpy.DictSerializer):
...     day = ISODateField()
...     updated = ISODateField(required=False)
...
>>> event = {"day": datetime.date(2026, 1, 2),
...          "updated": datetime.datetime(2026, 1, 2, 3, 4, 5)}
>>> EventSerializer(event).data == {
...     "day": "2026-01-02", "updated": "2026-01-02T03:04:05"}
True
>>> EventSerializer({"day": datetime.date(2026, 1, 2)}).data
{'day': '2026-01-02'}
>>> EventSerializer({"day": None, "updated": None}).data == {
...     "day": None, "updated": None}
True

``required=False`` allows a missing key to be omitted from the result;
an explicit ``None`` remains ``None``. An aware datetime's UTC offset is
preserved by ``isoformat()``. A naive datetime has no offset: this field
does not choose a timezone or convert to UTC. It expects date/datetime
objects, not strings to be parsed.
