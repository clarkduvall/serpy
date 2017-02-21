import unittest
import warnings

from serpy.fields import (
    Field, MethodField, BoolField, IntField, FloatField, StrField)
from tests.obj import Obj


class TestFields(unittest.TestCase):

    def test_to_value_noop(self):
        self.assertEqual(Field().to_representation(5), 5)
        self.assertEqual(Field().to_representation('a'), 'a')
        self.assertEqual(Field().to_representation(None), None)

    def test_to_internal_value_noop(self):
        self.assertEqual(Field().to_internal_value(5), 5)
        self.assertEqual(Field().to_internal_value('a'), 'a')
        self.assertEqual(Field().to_internal_value(None), None)

    def test_as_getter_none(self):
        self.assertEqual(Field().as_getter(None, None), None)

    def test_as_setter_none(self):
        self.assertEqual(Field().as_setter(None, None), None)

    def test_is_to_representation_overridden(self):
        class TransField(Field):
            def to_representation(self, value):
                return value

        field = Field()
        self.assertFalse(field._is_to_representation_overridden())
        field = TransField()
        self.assertTrue(field._is_to_representation_overridden())
        field = IntField()
        self.assertTrue(field._is_to_representation_overridden())

    def test_is_to_internal_value_overridden(self):
        class TransField(Field):
            def to_internal_value(self, value):
                return value

        field = Field()
        self.assertFalse(field._is_to_internal_value_overridden())
        field = TransField()
        self.assertTrue(field._is_to_internal_value_overridden())

    def test_str_field(self):
        field = StrField()
        self.assertEqual(field.to_representation('a'), 'a')
        self.assertEqual(field.to_representation(5), '5')
        self.assertEqual(field.to_internal_value('a'), 'a')
        self.assertEqual(field.to_internal_value(5), '5')

    def test_bool_field(self):
        field = BoolField()
        self.assertTrue(field.to_representation(True))
        self.assertFalse(field.to_representation(False))
        self.assertTrue(field.to_representation(1))
        self.assertFalse(field.to_representation(0))
        self.assertTrue(field.to_internal_value(True))
        self.assertFalse(field.to_internal_value(False))
        self.assertTrue(field.to_internal_value(1))
        self.assertFalse(field.to_internal_value(0))

    def test_int_field(self):
        field = IntField()
        self.assertEqual(field.to_representation(5), 5)
        self.assertEqual(field.to_representation(5.4), 5)
        self.assertEqual(field.to_representation('5'), 5)
        self.assertEqual(field.to_internal_value(5), 5)
        self.assertEqual(field.to_internal_value(5.4), 5)
        self.assertEqual(field.to_internal_value('5'), 5)

    def test_float_field(self):
        field = FloatField()
        self.assertEqual(field.to_representation(5.2), 5.2)
        self.assertEqual(field.to_representation('5.5'), 5.5)
        self.assertEqual(field.to_internal_value(5.2), 5.2)
        self.assertEqual(field.to_internal_value('5.5'), 5.5)

    def test_method_field(self):
        class FakeSerializer(object):
            def get_a(self, obj):
                return obj.a

            def set_a(self, obj, value):
                obj.a = value

            def z_sub_1(self, obj):
                return obj.z - 1

            def z_add_1(self, obj, value):
                obj.z = value + 1

        serializer = FakeSerializer()

        field = MethodField()
        fn = field.as_getter('a', serializer)
        self.assertEqual(fn(Obj(a=3)), 3)

        fn = field.as_setter('a', serializer)
        o = Obj(a=-1)
        fn(o, 3)
        self.assertEqual(o.a, 3)

        field = MethodField('z_sub_1', 'z_add_1')
        fn = field.as_getter('z', serializer)
        self.assertEqual(fn(Obj(z=3)), 2)

        fn = field.as_setter('z', serializer)
        o = Obj(a=-1)
        fn(o, 2)
        self.assertEqual(o.z, 3)

        self.assertTrue(MethodField.getter_takes_serializer)
        self.assertTrue(MethodField.setter_takes_serializer)

    def test_to_value_backwards_compatibility(self):
        class AddOneIntField(IntField):
            def to_value(self, value):
                return super(AddOneIntField, self).to_value(value) + 1

        self.assertEqual(AddOneIntField().to_value('1'), 2)

        self.assertEqual(IntField().to_value('1'), 1)

    def test_to_value_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always', DeprecationWarning)
            IntField().to_value('1')
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertTrue('deprecated' in str(w[-1].message))


    def test_field_label(self):
        field1 = StrField(label="@id")
        self.assertEqual(field1.label, "@id")


if __name__ == '__main__':
    unittest.main()
