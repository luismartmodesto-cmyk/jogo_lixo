import asyncio

import pygame

from content import CATEGORIES, ROUNDS, CATEGORY_BY_ID, TOTAL_ITEMS


WIDTH = 960
HEIGHT = 720
BACKGROUND = (242, 248, 244)
INK = (35, 57, 48)
MUTED = (86, 108, 98)
WHITE = (255, 255, 255)
GREEN = (40, 125, 84)
RED = (177, 69, 61)


class RecyclingGame:
    def __init__(self):
        self.scene = "menu"
        self.round_index = 0
        self.item_index = 0
        self.score = 0
        self.mistakes = 0
        self.dragging = False
        self.awaiting_next = False
        self.drag_offset = (0, 0)
        self.drag_rect = pygame.Rect(0, 0, 320, 138)
        self.feedback = ""
        self.feedback_kind = "info"
        self.bin_rects = []

    @property
    def current_item(self):
        return ROUNDS[self.round_index][self.item_index]

    def start_game(self, size=(WIDTH, HEIGHT)):
        self.scene = "game"
        self.round_index = 0
        self.item_index = 0
        self.score = 0
        self.mistakes = 0
        self.dragging = False
        self.awaiting_next = False
        self.feedback = ""
        self.bin_rects = self._layout_bins(size)
        self._center_item(size)

    def handle_event(self, event, size):
        width, height = size

        if event.type == pygame.KEYDOWN:
            if self.scene == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game(size)
            elif self.scene == "game" and self.awaiting_next and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.advance(size)
            elif self.scene == "done" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game(size)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._pointer_down(event.pos, size)
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._pointer_move(event.pos, size)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._pointer_up(event.pos, size)
        elif event.type == pygame.FINGERDOWN:
            self._pointer_down((int(event.x * width), int(event.y * height)), size)
        elif event.type == pygame.FINGERMOTION and self.dragging:
            self._pointer_move((int(event.x * width), int(event.y * height)), size)
        elif event.type == pygame.FINGERUP:
            self._pointer_up((int(event.x * width), int(event.y * height)), size)

    def _pointer_down(self, pos, size):
        if self.scene == "menu":
            if self._menu_button(size).collidepoint(pos):
                self.start_game(size)
            return

        if self.scene == "done":
            if self._replay_button(size).collidepoint(pos):
                self.start_game(size)
            return

        if self.scene != "game":
            return

        if self.awaiting_next:
            if self._next_button(size).collidepoint(pos):
                self.advance(size)
            return

        if self.drag_rect.collidepoint(pos):
            self.dragging = True
            self.drag_offset = (pos[0] - self.drag_rect.x, pos[1] - self.drag_rect.y)

    def _pointer_move(self, pos, size):
        if self.dragging:
            self.drag_rect.topleft = (
                max(0, min(size[0] - self.drag_rect.width, pos[0] - self.drag_offset[0])),
                max(0, min(size[1] - self.drag_rect.height, pos[1] - self.drag_offset[1])),
            )

    def _pointer_up(self, pos, size):
        if not self.dragging:
            return

        self._pointer_move(pos, size)
        self.dragging = False
        target_category = None
        for category, rect in self.bin_rects:
            if rect.collidepoint(self.drag_rect.center):
                target_category = category.id
                break

        if target_category == self.current_item.category_id:
            self.score += 10
            self._center_item(size)
            self.awaiting_next = True
            self.feedback = CATEGORY_BY_ID[target_category].tip
            self.feedback_kind = "good"
        else:
            self.mistakes += 1
            correct = CATEGORY_BY_ID[self.current_item.category_id]
            self.feedback = "Quase! Este item combina com a lixeira de {}. Tente de novo.".format(correct.label.lower())
            self.feedback_kind = "try"
            self._center_item(size)

    def advance(self, size=(WIDTH, HEIGHT)):
        self.awaiting_next = False
        self.feedback = ""
        self.item_index += 1
        if self.item_index >= len(ROUNDS[self.round_index]):
            self.round_index += 1
            self.item_index = 0
            if self.round_index >= len(ROUNDS):
                self.scene = "done"
                return
        self.bin_rects = self._layout_bins(size)
        self._center_item(size)

    def _center_item(self, size):
        width, height = size
        card_width = min(320, max(1, width - 32))
        card_height = min(138, max(108, int(height * 0.19)))
        top_bins = min((rect.top for _, rect in self.bin_rects), default=height - 160)
        center_y = min(int(height * 0.36), top_bins - card_height // 2 - 16)
        self.drag_rect = pygame.Rect(0, 0, card_width, card_height)
        self.drag_rect.center = (width // 2, center_y)

    def draw(self, surface):
        surface.fill(BACKGROUND)
        if self.scene == "game":
            size = surface.get_size()
            self.bin_rects = self._layout_bins(size)
            if not self.dragging and not self.awaiting_next:
                self._center_item(size)
        if self.scene == "menu":
            self._draw_menu(surface)
        elif self.scene == "game":
            self._draw_game(surface)
        else:
            self._draw_done(surface)

    def _draw_menu(self, surface):
        width, height = surface.get_size()
        leaf_size = min(54, max(28, min(width, height) // 14))
        title_size = max(24, min(42, width // 22))
        step_size = max(17, min(22, width // 40))
        panel = self._menu_instruction_panel((width, height))
        self._draw_leaf(surface, (width // 2, int(height * 0.14)), leaf_size)
        self._text(
            surface,
            "Missão: Lixo no lugar certo",
            title_size,
            INK,
            (width // 2, int(height * 0.28)),
            center=True,
            bold=True,
        )
        self._text(
            surface,
            "Como jogar",
            max(20, min(26, width // 34)),
            MUTED,
            (width // 2, panel.y - 22),
            center=True,
            bold=True,
        )
        self._panel(surface, panel)
        steps = (
            "Olhe o resíduo.",
            "Arraste até a lixeira certa.",
            "Leia a dica e continue.",
        )
        row_height = panel.height // len(steps)
        for index, step in enumerate(steps):
            row_top = panel.y + index * row_height
            row_center_y = row_top + row_height // 2
            if index:
                pygame.draw.line(
                    surface,
                    (220, 232, 224),
                    (panel.x + 18, row_top),
                    (panel.right - 18, row_top),
                    1,
                )
            radius = min(18, max(13, row_height // 3))
            number_center = (panel.x + 30, row_center_y)
            pygame.draw.circle(surface, GREEN, number_center, radius)
            self._text(
                surface,
                str(index + 1),
                max(15, radius),
                WHITE,
                number_center,
                center=True,
                bold=True,
            )
            self._wrapped_text(
                surface,
                step,
                pygame.Rect(panel.x + 58, row_top, panel.width - 74, row_height),
                step_size,
                INK,
                bold=True,
                max_lines=1,
            )
        self._button(surface, self._menu_button((width, height)), "Começar", GREEN)
        self._text(
            surface,
            "As regras podem variar de cidade para cidade.",
            max(12, min(17, width // 55)),
            MUTED,
            (width // 2, height - 18),
            center=True,
        )

    def _draw_game(self, surface):
        width, height = surface.get_size()
        compact = height < 500
        title_size = max(22, min(30, width // 32))
        self._text(surface, "Missão: Lixo no lugar certo", title_size, INK, (width // 2, 30), center=True, bold=True)
        self._text(
            surface,
            "Etapa {} de {}     Item {} de {}     Pontos: {}".format(
                self.round_index + 1,
                len(ROUNDS),
                self.item_index + 1,
                len(ROUNDS[self.round_index]),
                self.score,
            ),
            max(15, min(19, width // 50)),
            MUTED,
            (width // 2, 70 if compact else 76),
            center=True,
        )

        self._draw_bins(surface)
        self._draw_item_area(surface)
        self._text(
            surface,
            "As cores são uma referência geral. Confira a coleta da sua cidade.",
            max(12, min(15, width // 55)),
            MUTED,
            (width // 2, height - 10 if compact else height - 16),
            center=True,
        )

    def _draw_item_area(self, surface):
        if self.awaiting_next:
            width, height = surface.get_size()
            compact = height < 500
            if compact:
                panel = self.drag_rect
                title_size = 18
                body_size = 13
                feedback = self.feedback.split(".", 1)[0].strip() + "."
            else:
                panel_height = min(190, max(160, int(height * 0.26)))
                panel = pygame.Rect(0, 0, min(500, width - 36), panel_height)
                panel.center = (width // 2, self.drag_rect.centery)
                title_size = 28
                body_size = 18
                feedback = self.feedback
            self._panel(surface, panel)
            self._text(
                surface,
                "Muito bem!",
                title_size,
                GREEN,
                (panel.centerx, panel.y + (18 if compact else 30)),
                center=True,
                bold=True,
            )
            next_button = self._next_button(surface.get_size())
            text_top = panel.y + (34 if compact else 54)
            text_bottom = next_button.top - (3 if compact else 8)
            self._wrapped_text(
                surface,
                feedback,
                pygame.Rect(panel.x + 12, text_top, panel.width - 24, max(1, text_bottom - text_top)),
                body_size,
                INK,
                center=True,
                max_lines=2 if compact else 3,
            )
            self._button(surface, next_button, self._next_label(), GREEN)
            return

        card = self.drag_rect
        self._panel(surface, card)
        compact = surface.get_height() < 500
        icon_size = min(42, max(30, card.height // 3))
        icon_x = card.x + int(card.width * 0.24)
        text_x = card.x + int(card.width * 0.42)
        item_font_size = max(17, min(25, int(card.width * 0.07)))
        self._draw_item_icon(surface, self.current_item, (icon_x, card.centery), icon_size)
        self._text(surface, self.current_item.label, item_font_size, INK, (text_x, card.centery - 12), bold=True)
        instruction = "Arraste para uma lixeira"
        instruction_color = MUTED
        if compact and self.feedback:
            correct = CATEGORY_BY_ID[self.current_item.category_id]
            instruction = "Quase! Use a lixeira de {}.".format(correct.label.lower())
            instruction_color = RED
        if compact:
            self._wrapped_text(
                surface,
                instruction,
                pygame.Rect(card.x + 10, card.bottom - 30, card.width - 20, 22),
                13,
                instruction_color,
                center=True,
                max_lines=1,
            )
        else:
            self._text(surface, instruction, 16, MUTED, (text_x, card.centery + 22))
        if self.feedback:
            if not compact:
                color = RED if self.feedback_kind == "try" else MUTED
                self._wrapped_text(
                    surface,
                    self.feedback,
                    pygame.Rect(36, card.bottom + 12, surface.get_width() - 72, 54),
                    17,
                    color,
                    center=True,
                    max_lines=2,
                )

    def _draw_bins(self, surface):
        for category, rect in self.bin_rects:
            self._panel(surface, rect)
            pygame.draw.rect(surface, category.color, (rect.x, rect.y, rect.width, 10), border_radius=8)
            if rect.height < 100:
                icon_size = 24
                icon_top = rect.y + 11
                label_top = rect.y + 44
                font_size = 13
            elif rect.height < 135:
                icon_size = 32
                icon_top = rect.y + 13
                label_top = rect.y + 54
                font_size = 16
            else:
                icon_size = 40
                icon_top = rect.y + 28
                label_top = rect.y + 82
                font_size = 18
            self._draw_bin_icon(surface, rect.centerx, icon_top, category.color, icon_size)
            self._wrapped_text(
                surface,
                category.label,
                pygame.Rect(rect.x + 6, label_top, rect.width - 12, rect.bottom - label_top - 4),
                font_size,
                INK,
                center=True,
                bold=True,
                max_lines=2,
            )

    def _draw_done(self, surface):
        width, height = surface.get_size()
        leaf_size = min(48, max(28, min(width, height) // 16))
        self._draw_leaf(surface, (width // 2, int(height * 0.18)), leaf_size)
        self._text(
            surface,
            "Missão cumprida!",
            max(28, min(40, width // 24)),
            INK,
            (width // 2, int(height * 0.36)),
            center=True,
            bold=True,
        )
        self._text(
            surface,
            "Você separou {} resíduos e fez {} pontos.".format(TOTAL_ITEMS, self.score),
            max(18, min(23, width // 42)),
            MUTED,
            (width // 2, int(height * 0.48)),
            center=True,
        )
        self._wrapped_text(
            surface,
            "Errar faz parte de aprender. Continue cuidando do planeta!",
            pygame.Rect(24, int(height * 0.54), width - 48, max(32, int(height * 0.1))),
            max(16, min(20, width // 48)),
            MUTED,
            center=True,
            max_lines=2,
        )
        self._button(surface, self._replay_button((width, height)), "Jogar de novo", GREEN)
        self._text(
            surface,
            "Lembre-se: confirme as orientações da coleta local.",
            max(12, min(17, width // 55)),
            MUTED,
            (width // 2, height - 18),
            center=True,
        )

    def _layout_bins(self, size):
        width, height = size
        columns = len(CATEGORIES) if width >= 820 else 3
        rows = (len(CATEGORIES) + columns - 1) // columns
        margin = max(14, int(width * 0.035))
        compact = height < 500
        gap = 8 if compact else 12
        card_width = (width - 2 * margin - (columns - 1) * gap) // columns
        if compact:
            card_height = 92 if rows == 1 else 72
        else:
            card_height = 142 if rows == 1 else 124
        total_height = rows * card_height + (rows - 1) * gap
        start_y = height - total_height - (24 if compact else 42)
        bins = []
        for index, category in enumerate(CATEGORIES):
            row, column = divmod(index, columns)
            row_start = 0 if row == 0 else (len(CATEGORIES) - columns)
            items_in_row = min(columns, len(CATEGORIES) - row_start)
            row_width = items_in_row * card_width + (items_in_row - 1) * gap
            row_x = (width - row_width) // 2
            rect = pygame.Rect(
                row_x + column * (card_width + gap),
                start_y + row * (card_height + gap),
                card_width,
                card_height,
            )
            bins.append((category, rect))
        return bins

    @staticmethod
    def _panel(surface, rect):
        pygame.draw.rect(surface, WHITE, rect, border_radius=18)
        pygame.draw.rect(surface, (220, 232, 224), rect, width=2, border_radius=18)

    @staticmethod
    def _text(surface, value, size, color, position, center=False, bold=False):
        font = pygame.font.SysFont("arial", size, bold=bold)
        rendered = font.render(value, True, color)
        rect = rendered.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        surface.blit(rendered, rect)

    @staticmethod
    def _wrapped_text(surface, value, rect, size, color, center=False, bold=False, max_lines=4):
        font = pygame.font.SysFont("arial", size, bold=bold)
        words = value.split()
        lines = []
        line = ""
        for word in words:
            candidate = word if not line else line + " " + word
            if font.size(candidate)[0] <= rect.width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        lines = lines[:max_lines]
        line_height = font.get_linesize()
        y = rect.y + max(0, (rect.height - len(lines) * line_height) // 2)
        for line in lines:
            rendered = font.render(line, True, color)
            line_rect = rendered.get_rect()
            if center:
                line_rect.centerx = rect.centerx
            else:
                line_rect.x = rect.x
            line_rect.y = y
            surface.blit(rendered, line_rect)
            y += line_height

    @staticmethod
    def _button(surface, rect, label, color):
        pygame.draw.rect(surface, color, rect, border_radius=16)
        font = pygame.font.SysFont("arial", 22, bold=True)
        rendered = font.render(label, True, WHITE)
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    @staticmethod
    def _menu_button(size):
        width, height = size
        button_width = min(220, max(1, width - 40))
        button_height = min(60, max(48, int(height * 0.09)))
        button_y = min(int(height * 0.78), height - button_height - 34)
        return pygame.Rect(width // 2 - button_width // 2, button_y, button_width, button_height)

    @staticmethod
    def _replay_button(size):
        width, height = size
        button_width = min(250, max(1, width - 40))
        button_height = min(60, max(48, int(height * 0.09)))
        button_y = min(int(height * 0.68), height - button_height - 34)
        return pygame.Rect(width // 2 - button_width // 2, button_y, button_width, button_height)

    def _next_button(self, size):
        width, height = size
        button_width = min(190, max(1, width - 48))
        if height < 500:
            button_height = 34
            button_y = self.drag_rect.bottom - button_height - 5
        else:
            button_height = 48
            panel_height = min(190, max(160, int(height * 0.26)))
            panel_bottom = self.drag_rect.centery + panel_height // 2
            button_y = panel_bottom - button_height - 10
        return pygame.Rect(width // 2 - button_width // 2, button_y, button_width, button_height)

    @staticmethod
    def _menu_instruction_panel(size):
        width, height = size
        panel_width = max(1, min(640, width - 32))
        panel_height = min(180, max(120, int(height * 0.25)))
        panel = pygame.Rect(0, int(height * 0.45), panel_width, panel_height)
        panel.centerx = width // 2
        return panel

    def _next_label(self):
        is_last_item = self.item_index == len(ROUNDS[self.round_index]) - 1
        is_last_round = self.round_index == len(ROUNDS) - 1
        if is_last_item and is_last_round:
            return "Ver resultado"
        if is_last_item:
            return "Próxima etapa"
        return "Próximo item"

    @staticmethod
    def _draw_leaf(surface, center, size):
        x, y = center
        pygame.draw.ellipse(surface, (105, 174, 112), (x - size, y - size // 2, size * 2, size))
        pygame.draw.line(surface, (48, 119, 72), (x - size // 2, y + size // 4), (x + size // 2, y - size // 4), 4)

    @staticmethod
    def _draw_bin_icon(surface, center_x, top, color, size=40):
        half = size // 2
        pygame.draw.rect(surface, color, (center_x - half, top + 6, size, size), border_radius=max(4, size // 7))
        pygame.draw.rect(surface, color, (center_x - half - 5, top, size + 10, 5), border_radius=3)
        for offset in (-size // 4, 0, size // 4):
            pygame.draw.line(
                surface,
                WHITE,
                (center_x + offset, top + 12),
                (center_x + offset, top + 6 + size - 5),
                2,
            )

    @staticmethod
    def _draw_item_icon(surface, item, center, size):
        x, y = center
        if item.id == "cardboard":
            half = size // 2
            body = pygame.Rect(x - half + 2, y - size // 5, size - 4, size // 2 + size // 5)
            outline = (143, 99, 53)
            pygame.draw.rect(surface, (201, 149, 91), body, border_radius=2)
            pygame.draw.rect(surface, outline, body, width=max(1, size // 18), border_radius=2)
            pygame.draw.polygon(
                surface,
                (222, 174, 113),
                ((body.left, body.top), (x - size // 4, y - half), (x, body.top)),
            )
            pygame.draw.polygon(
                surface,
                (222, 174, 113),
                ((x, body.top), (x + size // 4, y - half), (body.right, body.top)),
            )
            pygame.draw.line(
                surface,
                outline,
                (x, body.top),
                (x, body.bottom),
                max(1, size // 18),
            )
            pygame.draw.line(
                surface,
                outline,
                (body.left, body.top),
                (x - size // 4, y - half),
                max(1, size // 18),
            )
            pygame.draw.line(
                surface,
                outline,
                (body.right, body.top),
                (x + size // 4, y - half),
                max(1, size // 18),
            )
        elif item.category_id == "paper":
            rect = pygame.Rect(x - size // 2, y - size // 2, size, size + 8)
            pygame.draw.rect(surface, (250, 250, 242), rect, border_radius=4)
            pygame.draw.rect(surface, (156, 169, 158), rect, width=2, border_radius=4)
            for offset in (-9, 0, 9):
                pygame.draw.line(surface, (155, 175, 160), (x - 12, y + offset), (x + 12, y + offset), 2)
        elif item.category_id == "plastic":
            pygame.draw.rect(surface, (118, 195, 211), (x - 18, y - 18, 36, 44), border_radius=8)
            pygame.draw.rect(surface, (118, 195, 211), (x - 9, y - 29, 18, 13), border_radius=3)
            pygame.draw.rect(surface, (68, 148, 166), (x - 10, y - 33, 20, 5), border_radius=2)
        elif item.category_id == "glass":
            pygame.draw.rect(surface, (164, 213, 203), (x - 23, y - 18, 46, 42), border_radius=9)
            pygame.draw.rect(surface, (97, 158, 148), (x - 13, y - 28, 26, 12), border_radius=4)
            pygame.draw.rect(surface, (97, 158, 148), (x - 24, y - 18, 48, 44), width=3, border_radius=9)
        elif item.category_id == "metal":
            pygame.draw.rect(surface, (180, 193, 194), (x - 22, y - 23, 44, 48), border_radius=7)
            pygame.draw.ellipse(surface, (219, 228, 226), (x - 22, y - 28, 44, 12))
            pygame.draw.line(surface, (125, 143, 143), (x - 12, y - 2), (x + 12, y - 2), 3)
        else:
            points = [(x - 25, y + 15), (x - 15, y - 16), (x + 15, y - 22), (x + 27, y + 8), (x + 8, y + 22)]
            pygame.draw.polygon(surface, (244, 194, 66), points)
            pygame.draw.line(surface, (128, 135, 57), (x + 17, y - 16), (x + 25, y - 24), 4)
            pygame.draw.line(surface, (128, 135, 57), (x - 25, y + 15), (x - 32, y + 18), 4)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Missão: Lixo no lugar certo")
    game = RecyclingGame()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event, screen.get_size())

        game.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(1 / 60)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
