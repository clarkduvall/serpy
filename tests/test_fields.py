from .obj import Obj
from serpy.fields import (
    Field, MethodField, BoolField, IntField, FloatField, StrField)
import unittest


def make_fn_from_field(field, field_name):
    getter = field.as_getter(field_name, None)
    if field.call:
        fn = lambda x: getter(x)()
    else:
        fn = getter
    return lambda x: field.transform_value(fn(x))


class TestFields(unittest.TestCase):

    def test_simple(self):
        fn = Field().as_getter('a', None)
        self.assertEqual(fn(Obj(a=5)), 5)

    def test_call(self):
        fn = Field(call=True).as_getter('a', None)
        self.assertEqual(fn(Obj(a=lambda: 5))(), 5)

    def test_transform_noop(self):
        self.assertEqual(Field().transform_value(5), 5)
        self.assertEqual(Field().transform_value('a'), 'a')
        self.assertEqual(Field().transform_value(None), None)

    def test_is_transform_value_overriden(self):
        class TransField(Field):
            def transform_value(self, value):
                return value

        field = Field()
        self.assertFalse(field._is_transform_value_overriden())
        field = TransField()
        self.assertTrue(field._is_transform_value_overriden())
        field = IntField()
        self.assertTrue(field._is_transform_value_overriden())

    def test_transform(self):
        class Add5Field(Field):
            def transform_value(self, value):
                return value + 5

        fn = make_fn_from_field(Add5Field(), 'a')
        self.assertEqual(fn(Obj(a=5)), 10)

        fn = make_fn_from_field(Add5Field(call=True), 'b')
        self.assertEqual(fn(Obj(b=lambda: 6)), 11)

    def test_str_field(self):
        fn = make_fn_from_field(StrField(), 'a')
        self.assertEqual(fn(Obj(a='a')), 'a')
        self.assertEqual(fn(Obj(a=5)), '5')

    def test_bool_field(self):
        fn = make_fn_from_field(BoolField(), 'a')
        self.assertTrue(fn(Obj(a=True)))
        self.assertFalse(fn(Obj(a=False)))
        self.assertTrue(fn(Obj(a=1)))
        self.assertFalse(fn(Obj(a=0)))

    def test_int_field(self):
        fn = make_fn_from_field(IntField(), 'a')
        self.assertEqual(fn(Obj(a=5)), 5)
        self.assertEqual(fn(Obj(a=5.4)), 5)
        self.assertEqual(fn(Obj(a='5')), 5)

    def test_float_field(self):
        fn = make_fn_from_field(FloatField(), 'a')
        self.assertEqual(fn(Obj(a=5.2)), 5.2)
        self.assertEqual(fn(Obj(a='5.5')), 5.5)

    def test_custom_attr(self):
        fn = Field(attr='b').as_getter('a', None)
        self.assertEqual(fn(Obj(b=5, a=1)), 5)

        fn = Field(attr='b', call=True).as_getter('a', None)
        self.assertEqual(fn(Obj(b=lambda: 5, a=1))(), 5)

    def test_dotted_attr(self):
        fn = Field(attr='z.x').as_getter('a', None)
        self.assertEqual(fn(Obj(z=Obj(x='hi'), a=1)), 'hi')

        fn = Field(attr='z.x', call=True).as_getter('a', None)
        self.assertEqual(fn(Obj(z=Obj(x=lambda: 'hi'), a=1))(), 'hi')

    def test_method_field(self):
        class FakeSerializer(object):
            def get_a(self, obj):
                return obj.a

            def z_sub_1(self, obj):
                return obj.z - 1

        serializer = FakeSerializer()

        fn = MethodField().as_getter('a', serializer)
        self.assertEqual(fn(Obj(a=3)), 3)

        fn = MethodField('z_sub_1').as_getter('a', serializer)
        self.assertEqual(fn(Obj(z=3)), 2)

        self.assertTrue(MethodField.getter_takes_serializer)

if __name__ == '__main__':
    unittest.main()
