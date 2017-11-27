from .obj import Obj
from serpy.fields import Field, MethodField, IntField, FloatField, StrField
from serpy.serializer import Serializer, DictSerializer
import unittest


class TestSerializer(unittest.TestCase):

    def test_simple(self):
        class ASerializer(Serializer):
            a = Field()

        a = Obj(a=5)
        self.assertEqual(ASerializer(a).data['a'], 5)

    def test_data_cached(self):
        class ASerializer(Serializer):
            a = Field()

        a = Obj(a=5)
        serializer = ASerializer(a)
        data1 = serializer.data
        data2 = serializer.data
        # Use assertTrue instead of assertIs for python 2.6.
        self.assertTrue(data1 is data2)

    def test_inheritance(self):
        class ASerializer(Serializer):
            a = Field()

        class CSerializer(Serializer):
            c = Field()

        class ABSerializer(ASerializer):
            b = Field()

        class ABCSerializer(ABSerializer, CSerializer):
            pass

        a = Obj(a=5, b='hello', c=100)
        self.assertEqual(ASerializer(a).data['a'], 5)
        data = ABSerializer(a).data
        self.assertEqual(data['a'], 5)
        self.assertEqual(data['b'], 'hello')
        data = ABCSerializer(a).data
        self.assertEqual(data['a'], 5)
        self.assertEqual(data['b'], 'hello')
        self.assertEqual(data['c'], 100)

    def test_many(self):
        class ASerializer(Serializer):
            a = Field()

        objs = [Obj(a=i) for i in range(5)]
        data = ASerializer(objs, many=True).data
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]['a'], 0)
        self.assertEqual(data[1]['a'], 1)
        self.assertEqual(data[2]['a'], 2)
        self.assertEqual(data[3]['a'], 3)
        self.assertEqual(data[4]['a'], 4)

    def test_serializer_as_field(self):
        class ASerializer(Serializer):
            a = Field()

        class BSerializer(Serializer):
            b = ASerializer()

        b = Obj(b=Obj(a=3))
        self.assertEqual(BSerializer(b).data['b']['a'], 3)

    def test_serializer_as_field_many(self):
        class ASerializer(Serializer):
            a = Field()

        class BSerializer(Serializer):
            b = ASerializer(many=True)

        b = Obj(b=[Obj(a=i) for i in range(3)])
        b_data = BSerializer(b).data['b']
        self.assertEqual(len(b_data), 3)
        self.assertEqual(b_data[0]['a'], 0)
        self.assertEqual(b_data[1]['a'], 1)
        self.assertEqual(b_data[2]['a'], 2)

    def test_serializer_as_field_call(self):
        class ASerializer(Serializer):
            a = Field()

        class BSerializer(Serializer):
            b = ASerializer(call=True)

        b = Obj(b=lambda: Obj(a=3))
        self.assertEqual(BSerializer(b).data['b']['a'], 3)

    def test_serializer_method_field(self):
        class ASerializer(Serializer):
            a = MethodField()
            b = MethodField('add_9')

            def get_a(self, obj):
                return obj.a + 5

            def add_9(self, obj):
                return obj.a + 9

        a = Obj(a=2)
        data = ASerializer(a).data
        self.assertEqual(data['a'], 7)
        self.assertEqual(data['b'], 11)

    def test_to_value_called(self):
        class ASerializer(Serializer):
            a = IntField()
            b = FloatField(call=True)
            c = StrField(attr='foo.bar.baz')

        o = Obj(a='5', b=lambda: '6.2', foo=Obj(bar=Obj(baz=10)))
        data = ASerializer(o).data
        self.assertEqual(data['a'], 5)
        self.assertEqual(data['b'], 6.2)
        self.assertEqual(data['c'], '10')

    def test_dict_serializer(self):
        class ASerializer(DictSerializer):
            a = IntField()
            b = Field(attr='foo')

        d = {'a': '2', 'foo': 'hello'}
        data = ASerializer(d).data
        self.assertEqual(data['a'], 2)
        self.assertEqual(data['b'], 'hello')

    def test_dotted_attr(self):
        class ASerializer(Serializer):
            a = Field('a.b.c')

        o = Obj(a=Obj(b=Obj(c=2)))
        data = ASerializer(o).data
        self.assertEqual(data['a'], 2)

    def test_custom_field(self):
        class Add5Field(Field):
            def to_value(self, value):
                return value + 5

        class ASerializer(Serializer):
            a = Add5Field()

        o = Obj(a=10)
        data = ASerializer(o).data
        self.assertEqual(data['a'], 15)

    def test_optional_field(self):
        class ASerializer(Serializer):
            a = IntField(required=False)
            b = IntField(required=False)

        o = Obj(a=None)
        data = ASerializer(o).data
        self.assertNotIn('a', data)
        self.assertNotIn('b', data)

        o = Obj(a='5', b='10', x='y')
        data = ASerializer(o).data
        self.assertEqual(data['a'], 5)
        self.assertEqual(data['b'], 10)
        # Check that an object value does not make it to the
        # serialized value
        self.assertNotIn('x', data)

        class BSerializer(Serializer):
            a = IntField()
            b = IntField()

        o = Obj(a='5')
        # Test that a required field raises a type error.
        with self.assertRaises(TypeError):
            BSerializer(o).data

    def test_optional_methodfield(self):
        class ASerializer(Serializer):
            a = MethodField(required=False)

            def get_a(self, obj):
                return obj.a

        # Check that an optional method field with a None value
        # will not put the value in the output.
        o = Obj(a=None)
        data = ASerializer(o).data
        self.assertNotIn('a', data)

        # Check that an optional method field will pass the field
        # if there is a value in it.
        o = Obj(a='5')
        data = ASerializer(o).data
        self.assertIn('a', data)
        self.assertEqual(data['a'], '5')

        class BSerializer(Serializer):
            b = MethodField()

            def get_b(self, obj):
                return obj.b

        # Check that a required method field with a none return value
        # will not serialize output in the data
        o = Obj(b=None)
        data = BSerializer(o).data
        self.assertNotIn('b', data)

        class CSerializer(Serializer):
            c = MethodField()

            def get_c(self, obj):
                return obj.c

        # Check that a required method field without a required object
        # attribute will raise a type error.
        o = Obj()
        with self.assertRaises(TypeError):
            CSerializer(o).data

    def test_error_on_data(self):
        with self.assertRaises(RuntimeError):
            Serializer(data='foo')

    def test_serializer_with_custom_output_label(self):
        class ASerializer(Serializer):
            context = StrField(label='@context')
            content = MethodField(label='@content')

            def get_content(self, obj):
                return obj.content

        o = Obj(context='http://foo/bar/baz/', content='http://baz/bar/foo/')
        data = ASerializer(o).data

        self.assertIn('@context', data)
        self.assertEqual(data['@context'], 'http://foo/bar/baz/')
        self.assertIn('@content', data)
        self.assertEqual(data['@content'], 'http://baz/bar/foo/')


if __name__ == '__main__':
    unittest.main()
