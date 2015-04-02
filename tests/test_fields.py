from .obj import Obj
from serpy.fields import (
    Field, MethodField, BooleanField, IntField, FloatField, StrField)
import unittest


def make_fn(value_fns):
    value_fn, transform = value_fns
    if transform is None:
        return value_fn
    return lambda x: transform(value_fn(x))


class TestFields(unittest.TestCase):

    def test_simple(self):
        fn, _ = Field().to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=5)), 5)

    def test_call(self):
        fn, _ = Field(call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=lambda: 5)), 5)

    def test_transform_noop(self):
        self.assertEqual(Field().transform_value(5), 5)
        self.assertEqual(Field().transform_value('a'), 'a')
        self.assertEqual(Field().transform_value(None), None)

    def test_is_transform_overriden(self):
        class TransField(Field):
            def transform_value(self, value):
                return value

        field = Field()
        self.assertFalse(field._is_transform_overriden())
        field = TransField()
        self.assertTrue(field._is_transform_overriden())
        field = IntField()
        self.assertTrue(field._is_transform_overriden())

    def test_transform(self):
        class Add5Field(Field):
            def transform_value(self, value):
                return value + 5

        fn = make_fn(Add5Field().to_value_fn('a', None))
        self.assertEqual(fn(Obj(a=5)), 10)

        fn = make_fn(Add5Field(call=True).to_value_fn('b', None))
        self.assertEqual(fn(Obj(b=lambda: 6)), 11)

    def test_str_field(self):
        fn = make_fn(StrField().to_value_fn('a', None))
        self.assertEqual(fn(Obj(a='a')), 'a')
        self.assertEqual(fn(Obj(a=5)), '5')

    def test_boolean_field(self):
        fn = make_fn(BooleanField().to_value_fn('a', None))
        self.assertTrue(fn(Obj(a=True)))
        self.assertFalse(fn(Obj(a=False)))
        self.assertTrue(fn(Obj(a=1)))
        self.assertFalse(fn(Obj(a=0)))

    def test_int_field(self):
        fn = make_fn(IntField().to_value_fn('a', None))
        self.assertEqual(fn(Obj(a=5)), 5)
        self.assertEqual(fn(Obj(a=5.4)), 5)
        self.assertEqual(fn(Obj(a='5')), 5)

    def test_float_field(self):
        fn = make_fn(FloatField().to_value_fn('a', None))
        self.assertEqual(fn(Obj(a=5.2)), 5.2)
        self.assertEqual(fn(Obj(a='5.5')), 5.5)

    def test_custom_attr(self):
        fn, _ = Field(attr='b').to_value_fn('a', None)
        self.assertEqual(fn(Obj(b=5, a=1)), 5)

        fn, _ = Field(attr='b', call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(b=lambda: 5, a=1)), 5)

    def test_dotted_attr(self):
        fn, _ = Field(attr='z.x').to_value_fn('a', None)
        self.assertEqual(fn(Obj(z=Obj(x='hi'), a=1)), 'hi')

        fn, _ = Field(attr='z.x', call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(z=Obj(x=lambda: 'hi'), a=1)), 'hi')

    def test_method_field(self):
        class FakeSerializer(object):
            def get_a(self, obj):
                return obj.a

            def z_sub_1(self, obj):
                return obj.z - 1

        serializer = FakeSerializer()

        fn, _ = MethodField().to_value_fn('a', serializer)
        self.assertEqual(fn(Obj(a=3)), 3)

        fn, _ = MethodField('z_sub_1').to_value_fn('a', serializer)
        self.assertEqual(fn(Obj(z=3)), 2)

        self.assertTrue(MethodField.uses_self)

if __name__ == '__main__':
    unittest.main()
