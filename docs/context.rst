Context in method fields
========================

``Serializer`` accepts ``context`` for compatibility with Django REST
Framework (DRF), but does not store or propagate it. A custom base serializer
can retain the value so that ``MethodField`` methods can access it:

.. code-block:: python

   >>> import serpy
   >>> class ContextSerializer(serpy.Serializer):
   ...     def __init__(self, instance=None, many=False, data=None,
   ...                  context=None, **kwargs):
   ...         self.context = {} if context is None else context
   ...         super(ContextSerializer, self).__init__(
   ...             instance=instance, many=many, data=data,
   ...             context=context, **kwargs)

DRF supplies a dictionary, so use ``self.context['request']``, not
``self.context.request``. The following request stand-in keeps the example
independent of Django; in an application, pass the actual request instead:

.. code-block:: python

   >>> class User(object):
   ...     id = 7
   >>> class Request(object):
   ...     user = User()
   >>> class ItemSerializer(ContextSerializer):
   ...     owned = serpy.MethodField()
   ...     def get_owned(self, obj):
   ...         return obj['owner_id'] == self.context['request'].user.id
   >>> context = {'request': Request()}
   >>> ItemSerializer({'owner_id': 7}, context=context).data
   {'owned': True}
   >>> ItemSerializer([{'owner_id': 7}, {'owner_id': 8}],
   ...                many=True, context=context).data
   [{'owned': True}, {'owned': False}]

Inherit from the custom base for each serializer that needs context. Declaring
a nested serializer as a class-level field does not pass the parent's context
to it. For nested output that needs the same request, instantiate the child
in a method field and pass context explicitly:

.. code-block:: python

   >>> class CollectionSerializer(ContextSerializer):
   ...     items = serpy.MethodField()
   ...     def get_items(self, obj):
   ...         return ItemSerializer(obj['items'], many=True,
   ...                               context=self.context).data
   >>> CollectionSerializer({'items': [{'owner_id': 7}]},
   ...                      context=context).data
   {'items': [{'owned': True}]}

Create a new serializer instance for each request. Serialized ``data`` is
cached, so changing the context of an already evaluated instance will not
recompute its output. The example requires a request in context; omitting it
raises ``KeyError`` when the method field is evaluated.
