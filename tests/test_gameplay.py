import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from content import CATEGORIES, ROUNDS, TOTAL_ITEMS
from main import HEIGHT, INK, WIDTH, RecyclingGame


class RecyclingGameplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game = RecyclingGame()
        self.game.start_game()
        self.size = (WIDTH, HEIGHT)
        self.surface = pygame.Surface(self.size)

    def drag_to_category(self, category_id, size=None):
        size = size or self.size
        self.game.bin_rects = self.game._layout_bins(size)
        target = next(rect for category, rect in self.game.bin_rects if category.id == category_id)
        source = self.game.drag_rect.center
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=source), size)
        self.game.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=target.center, rel=(0, 0), buttons=(1, 0, 0)), size)
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=target.center), size)

    def test_correct_drop_awards_points_and_waits_for_next_action(self):
        item = self.game.current_item
        self.drag_to_category(item.category_id)

        self.assertEqual(self.game.score, 10)
        self.assertTrue(self.game.awaiting_next)
        self.assertEqual(self.game.item_index, 0)
        self.assertTrue(self.game.feedback)

    def test_wrong_drop_keeps_item_available_without_subtracting_points(self):
        item = self.game.current_item
        wrong_category = next(category.id for category in CATEGORIES if category.id != item.category_id)
        self.drag_to_category(wrong_category)

        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.item_index, 0)
        self.assertEqual(self.game.mistakes, 1)
        self.assertFalse(self.game.awaiting_next)
        self.assertIn("Tente de novo", self.game.feedback)

    def test_game_screen_draws(self):
        self.game.draw(self.surface)
        self.assertEqual(self.surface.get_size(), self.size)

    def test_menu_instructions_fit_above_start_button(self):
        for size in ((960, 720), (390, 844), (844, 390)):
            with self.subTest(size=size):
                panel = self.game._menu_instruction_panel(size)
                button = self.game._menu_button(size)
                surface = pygame.Surface(size)

                RecyclingGame().draw(surface)

                self.assertLessEqual(panel.bottom, button.top)
                self.assertGreaterEqual(button.left, 0)
                self.assertLessEqual(button.right, size[0])
                self.assertLessEqual(button.bottom, size[1] - 20)

    def test_left_aligned_wrapped_text_stays_inside_its_text_area(self):
        surface = pygame.Surface((400, 80))
        surface.fill((255, 255, 255))
        text_area = pygame.Rect(60, 10, 250, 50)

        RecyclingGame._wrapped_text(
            surface,
            "Olhe o resíduo.",
            text_area,
            20,
            INK,
            max_lines=1,
        )
        drawn_pixels = [
            (x, y)
            for x in range(surface.get_width())
            for y in range(surface.get_height())
            if surface.get_at((x, y))[:3] != (255, 255, 255)
        ]

        self.assertTrue(drawn_pixels)
        self.assertGreaterEqual(min(x for x, _ in drawn_pixels), text_area.left)
        self.assertLess(max(x for x, _ in drawn_pixels), text_area.right)

    def test_cardboard_icon_is_distinct_from_paper_sheet_icon(self):
        rendered_icons = []
        for item in (ROUNDS[0][0], ROUNDS[1][0]):
            surface = pygame.Surface((80, 80))
            surface.fill((255, 255, 255))
            RecyclingGame._draw_item_icon(surface, item, (40, 40), 36)
            rendered_icons.append(pygame.image.tobytes(surface, "RGB"))

        self.assertNotEqual(rendered_icons[0], rendered_icons[1])

    def test_item_and_bins_do_not_overlap_on_portrait_or_landscape(self):
        for size in ((960, 720), (390, 844), (844, 390)):
            with self.subTest(size=size):
                game = RecyclingGame()
                game.start_game(size)
                game.draw(pygame.Surface(size))

                self.assertLessEqual(game.drag_rect.right, size[0])
                self.assertLessEqual(game.drag_rect.bottom, size[1])
                self.assertTrue(
                    all(
                        rect.left >= 0 and rect.top >= 0 and rect.right <= size[0] and rect.bottom <= size[1]
                        for _, rect in game.bin_rects
                    )
                )
                self.assertFalse(any(game.drag_rect.colliderect(rect) for _, rect in game.bin_rects))

    def test_compact_feedback_button_fits_inside_confirmation_card(self):
        size = (844, 390)
        game = RecyclingGame()
        game.start_game(size)
        game.draw(pygame.Surface(size))
        target_category = game.current_item.category_id
        bins = dict((category.id, rect) for category, rect in game.bin_rects)
        source = game.drag_rect.center
        target = bins[target_category].center

        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=source), size)
        game.handle_event(
            pygame.event.Event(pygame.MOUSEMOTION, pos=target, rel=(0, 0), buttons=(1, 0, 0)),
            size,
        )
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=target), size)
        button = game._next_button(size)

        self.assertTrue(game.awaiting_next)
        self.assertTrue(game.drag_rect.contains(button))

    def test_touch_drop_uses_normalized_browser_coordinates(self):
        item = self.game.current_item
        self.game.bin_rects = self.game._layout_bins(self.size)
        target = next(rect for category, rect in self.game.bin_rects if category.id == item.category_id)
        source = self.game.drag_rect.center

        self.game.handle_event(
            pygame.event.Event(pygame.FINGERDOWN, x=source[0] / WIDTH, y=source[1] / HEIGHT),
            self.size,
        )
        self.game.handle_event(
            pygame.event.Event(pygame.FINGERMOTION, x=target.centerx / WIDTH, y=target.centery / HEIGHT),
            self.size,
        )
        self.game.handle_event(
            pygame.event.Event(pygame.FINGERUP, x=target.centerx / WIDTH, y=target.centery / HEIGHT),
            self.size,
        )

        self.assertTrue(self.game.awaiting_next)
        self.assertEqual(self.game.score, 10)

    def test_full_game_advances_through_both_rounds(self):
        while self.game.scene == "game":
            self.drag_to_category(self.game.current_item.category_id)
            self.game.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=self.game._next_button(self.size).center),
                self.size,
            )

        self.assertEqual(self.game.score, TOTAL_ITEMS * 10)
        self.assertEqual(self.game.scene, "done")

    def test_full_game_and_result_fit_compact_landscape(self):
        size = (844, 390)
        surface = pygame.Surface(size)
        game = RecyclingGame()
        game.start_game(size)

        while game.scene == "game":
            game.draw(surface)
            target = next(rect for category, rect in game.bin_rects if category.id == game.current_item.category_id)
            source = game.drag_rect.center
            game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=source), size)
            game.handle_event(
                pygame.event.Event(pygame.MOUSEMOTION, pos=target.center, rel=(0, 0), buttons=(1, 0, 0)),
                size,
            )
            game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=target.center), size)
            next_button = game._next_button(size)
            self.assertTrue(game.drag_rect.contains(next_button))
            game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=next_button.center), size)

        game.draw(surface)

        self.assertEqual(game.score, TOTAL_ITEMS * 10)
        self.assertEqual(game.scene, "done")
        self.assertLessEqual(game._replay_button(size).bottom, size[1] - 20)


if __name__ == "__main__":
    unittest.main()
