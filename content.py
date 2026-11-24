from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    id: str
    label: str
    color: tuple
    tip: str


@dataclass(frozen=True)
class WasteItem:
    id: str
    label: str
    category_id: str
    round_number: int


CATEGORIES = (
    Category("paper", "Papel", (57, 125, 190), "Papel limpo e seco costuma ser encaminhado à reciclagem. Papel sujo pode não ser aceito."),
    Category("plastic", "Plástico", (207, 79, 74), "Embalagens plásticas vazias e limpas podem ser recicláveis. Confira a coleta da sua cidade."),
    Category("glass", "Vidro", (72, 155, 111), "Frascos e potes de vidro podem ser recicláveis. Siga as orientações locais para o descarte seguro."),
    Category("metal", "Metal", (220, 176, 54), "Latas metálicas vazias costumam ser recicláveis. Confira as orientações da coleta local."),
    Category("organic", "Orgânico", (143, 102, 69), "Restos de frutas podem virar adubo na compostagem. Veja se há coleta orgânica ou composteira."),
)

CATEGORY_BY_ID = {category.id: category for category in CATEGORIES}

ROUNDS = (
    (
        WasteItem("newspaper", "Jornal limpo", "paper", 1),
        WasteItem("pet-bottle", "Garrafa PET vazia", "plastic", 1),
        WasteItem("glass-jar", "Pote de vidro", "glass", 1),
        WasteItem("aluminum-can", "Lata de alumínio", "metal", 1),
        WasteItem("banana-peel", "Casca de banana", "organic", 1),
    ),
    (
        WasteItem("cardboard", "Caixa de papelão", "paper", 2),
        WasteItem("yogurt-pot", "Pote plástico vazio", "plastic", 2),
        WasteItem("glass-bottle", "Garrafa de vidro", "glass", 2),
        WasteItem("food-can", "Lata de alimento", "metal", 2),
        WasteItem("coffee-grounds", "Borra de café", "organic", 2),
    ),
)

TOTAL_ITEMS = sum(len(round_items) for round_items in ROUNDS)
