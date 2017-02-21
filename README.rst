*********************************************
serpy: ridiculously fast object serialization
*********************************************

.. container:: badges

    .. image:: https://travis-ci.org/clarkduvall/serpy.svg?branch=master
        :target: https://travis-ci.org/clarkduvall/serpy?branch=master
        :alt: Travis-CI


    .. image:: https://coveralls.io/repos/clarkduvall/serpy/badge.svg?branch=master
        :target: https://coveralls.io/r/clarkduvall/serpy?branch=master
        :alt: Coveralls

    .. image:: https://readthedocs.org/projects/serpy/badge/?version=latest
        :target: https://readthedocs.org/projects/serpy/?badge=latest
        :alt: Documentation Status

    .. image:: https://pypip.in/download/serpy/badge.svg
        :target: https://pypi.python.org/pypi/serpy/
        :alt: Downloads


**serpy** is a super simple object serialization framework built for speed.
**serpy** serializes complex datatypes (Django Models, custom classes, ...) to
simple native types (dicts, lists, strings, ...). The native types can easily
be converted to JSON or any other format needed.

The goal of **serpy** is to be able to do this *simply*, *reliably*, and
*quickly*. Since serializers are class based, they can be combined, extended
and customized with very little code duplication. Compared to other popular
Python serialization frameworks like `marshmallow
<http://marshmallow.readthedocs.org>`_ or `Django Rest Framework Serializers
<http://www.django-rest-framework.org/api-guide/serializers/>`_ **serpy** is at
least an `order of magnitude
<http://serpy.readthedocs.org/en/latest/performance.html>`_ faster.


Source
======
Source at: https://github.com/clarkduvall/serpy

If you want a feature, send a pull request!

Documentation
=============
Full documentation at: http://serpy.readthedocs.org/en/latest/

Installation
============
.. code-block:: bash

    $ pip install serpy

Examples
========

Simple Example
--------------
.. code-block:: python

    import serpy

    class Foo(object):
        """The object to be serialized."""
        y = 'hello'
        z = 9.5

        def __init__(self, x):
            self.x = x


    class FooSerializer(serpy.Serializer):
        """The serializer schema definition."""
        # Use a Field subclass like IntField if you need more validation.
        x = serpy.IntField()
        y = serpy.Field()
        z = serpy.Field()

    f = Foo(1)
    FooSerializer(instance=f).data
    # {'x': 1, 'y': 'hello', 'z': 9.5}

    fs = [Foo(i) for i in range(100)]
    FooSerializer(instance=fs, many=True).data
    # [{'x': 0, 'y': 'hello', 'z': 9.5}, {'x': 1, 'y': 'hello', 'z': 9.5}, ...]

Nested Example
--------------
.. code-block:: python

    import serpy

    class Nestee(object):
        """An object nested inside another object."""
        n = 'hi'


    class Foo(object):
        x = 1
        nested = Nestee()


    class NesteeSerializer(serpy.Serializer):
        n = serpy.Field()


    class FooSerializer(serpy.Serializer):
        x = serpy.Field()
        # Use another serializer as a field.
        nested = NesteeSerializer()

    f = Foo()
    FooSerializer(instance=f).data
    # {'x': 1, 'nested': {'n': 'hi'}}

Complex Example
---------------
.. code-block:: python

    import serpy

    class Foo(object):
        y = 1
        z = 2
        super_long_thing = 10

        def x(self):
            return 5


    class FooSerializer(serpy.Serializer):
        w = serpy.Field(attr='super_long_thing')
        x = serpy.Field(call=True)
        plus = serpy.MethodField()

        def get_plus(self, obj):
            return obj.y + obj.z

    f = Foo()
    FooSerializer(instance=f).data
    # {'w': 10, 'x': 5, 'plus': 3}

Inheritance Example
-------------------
.. code-block:: python

    import serpy

    class Foo(object):
        a = 1
        b = 2


    class ASerializer(serpy.Serializer):
        a = serpy.Field()


    class ABSerializer(ASerializer):
        """ABSerializer inherits the 'a' field from ASerializer.

        This also works with multiple inheritance and mixins.
        """
        b = serpy.Field()

    f = Foo()
    ASerializer(instance=f).data
    # {'a': 1}
    ABSerializer(instance=f).data
    # {'a': 1, 'b': 2}

License
=======
serpy is free software distributed under the terms of the MIT license. See the
`LICENSE <https://github.com/clarkduvall/serpy/blob/master/LICENSE>`_ file.
