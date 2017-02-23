*************
Custom Fields
*************

The most common way to create a custom field with **serpy** is to override
:meth:`serpy.Field.to_representation`. This method is called on the value
retrieved from the object being serialized. For example, to create a field that
adds 5 to every value it serializes, do:

.. code-block:: python

   class Add5Field(serpy.Field):
      def to_representation(self, value):
         return value + 5

Then to use it:

.. code-block:: python

   class Obj(object):
      pass

   class ObjSerializer(serpy.Serializer):
      foo = Add5Field()

   f = Obj()
   f.foo = 9
   ObjSerializer(instance=f).data
   # {'foo': 14}

Another use for custom fields is data validation. For example, to validate that
every serialized value has a ``'.'`` in it:

.. code-block:: python

   class ValidateDotField(serpy.Field):
      def to_representation(self, value):
         if '.' not in value:
            raise ValidationError('no dot!')
         return value

For more control over the behavior of the field, override
:meth:`serpy.Field.as_getter`. When the :class:`serpy.Serializer` class is
created, each field will be compiled to a getter, that will be called to get its
associated attribute from the object. For an example of this, see the
:meth:`serpy.MethodField` implementation.
