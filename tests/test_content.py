import unittest

from content import CATEGORIES, CATEGORY_BY_ID, ROUNDS, TOTAL_ITEMS


class RecyclingContentTests(unittest.TestCase):
    def test_every_item_uses_a_known_category(self):
        for round_items in ROUNDS:
            for item in round_items:
                with self.subTest(item=item.id):
                    self.assertIn(item.category_id, CATEGORY_BY_ID)

    def test_rounds_have_unique_items_and_cover_all_categories(self):
        item_ids = [item.id for round_items in ROUNDS for item in round_items]
        self.assertEqual(len(item_ids), len(set(item_ids)))
        for round_items in ROUNDS:
            self.assertEqual({item.category_id for item in round_items}, {category.id for category in CATEGORIES})

    def test_every_category_has_educational_feedback(self):
        for category in CATEGORIES:
            with self.subTest(category=category.id):
                self.assertTrue(category.tip.strip())
                self.assertEqual(len(category.color), 3)
                self.assertTrue(all(0 <= channel <= 255 for channel in category.color))

    def test_total_item_count_matches_round_data(self):
        self.assertEqual(TOTAL_ITEMS, sum(len(round_items) for round_items in ROUNDS))


if __name__ == "__main__":
    unittest.main()
