import re

from django.test import TestCase
from django.urls import reverse
from src.models import Item
from src.views import products_with_discount

class ViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 items for pagination tests
        items = 6

        for item in range(items):
            if item % 2 == 0:
                Item.objects.create(title=item,
                                    price=item,
                                    category=item,
                                    description=item,
                                    slug=item,
                                    discount_price=item
                                    )
            else:
                Item.objects.create(title=item,
                                    price=item,
                                    category=item,
                                    description=item,
                                    slug=item
                )

    def test_home_view_uses_correct_template(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_pagination_is_four(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['item_list']) == 4)

    def test_last_page(self):
        response = self.client.get(reverse('core:home')+'?page=2')
        expected_result = 2
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEquals(len(response.context['item_list']), expected_result)

    def test_all_products(self):
        expected_result = 6
        result = len(Item.objects.all())
        self.assertEquals(expected_result, result)

    def test_items_with_discount_price(self):
        expected_result = 3
        response = self.client.get(reverse('core:products_with_discount'))
        self.assertEquals(len(response.context['items']), expected_result)



