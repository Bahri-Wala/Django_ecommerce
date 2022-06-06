from django.test import TestCase


from django.test import TestCase
from django.contrib.auth.models import User
from src.models import Item, OrderItem


class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Item.objects.create(title='Telephone', price='1500',category='PH', description='phone')

    def test_first_name_label(self):
        item = Item.objects.get(id=1)
        self.assertEquals(item.title, 'Telephone')

    def test_is_new_default_value(self):
        item=Item.objects.get(id=1)
        self.assertTrue(item.is_new)

    def test_first_name_max_length(self):
        item = Item.objects.get(id=1)
        max_length = item._meta.get_field('category').max_length
        self.assertEquals(max_length, 2)

    def test_str(self):
        item = Item.objects.get(id=1)
        expected_object_name = f'{item.title}'
        self.assertEquals(expected_object_name, str(item))

    def test_is_new_verif(self):
        item = Item.objects.get(id=1)
        self.assertTrue(item.is_new_verif())

class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email='aziz@gmail.com', username='aziz', password='azizaziz')
        item = Item.objects.create(title='Telephone', price='1500',category='PH', description='phone')
        OrderItem.objects.create(user=user, item=item, quantity=2)


    def test_sign_up(self):
        user = User.objects.get(id=1)
        self.assertEquals(user.username, 'aziz')

    def test_str(self):
        order_item = OrderItem.objects.get(id=1)
        expected_object_name = f"{order_item.quantity} of {order_item.item.title}"
        self.assertEquals(expected_object_name, str(order_item))

    def test_get_total_item_price(self):
        order_item = OrderItem.objects.get(id=1)
        expected_result = 3000
        self.assertEquals(expected_result, order_item.get_total_item_price())



