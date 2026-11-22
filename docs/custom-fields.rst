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

Lists of primitive values
==========================

The ``many=True`` option applies to serializers. Basic fields such as
``StrField`` do not take it. To serialize a list of strings, return the list
from a ``MethodField``, performing any per-item conversion in that method:

.. code-block:: python

    import serpy

    class Record(object):
        def __init__(self, tags):
            self.tags = tags

    class RecordSerializer(serpy.Serializer):
        tags = serpy.MethodField()

        def get_tags(self, obj):
            return [str(tag) for tag in obj.tags]

    assert RecordSerializer(Record(['news', 7])).data == {
        'tags': ['news', '7']}
    assert RecordSerializer(Record([])).data == {'tags': []}
    assert RecordSerializer(
        [Record(['news']), Record([])], many=True).data == [
            {'tags': ['news']}, {'tags': []}]

If a list already contains the exact output values you want, a plain
``serpy.Field()`` also passes it through unchanged. A ``StrField()`` would
convert the entire list to one string. For lists of structured objects, use a
nested serializer with ``many=True`` instead.

Custom getters
==============

For more control over the behavior of the field, override
:meth:`serpy.Field.as_getter`. When the :class:`serpy.Serializer` class is
created, each field will be compiled to a getter, that will be called to get its
associated attribute from the object. For an example of this, see the
:meth:`serpy.MethodField` implementation.
