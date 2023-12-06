import os
# fix for testing just this file
if __name__ == "__main__":
    import sys
    # Get the parent directory of the current script (api.py)
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))

    # Add the parent directory to the Python path
    PARENT_DIR = os.path.join(CURR_DIR, "..")  # Go up one level from utils to project folder
    sys.path.append(PARENT_DIR)
from utils.api import API
from utils.lazy import DictToObject

def forLater():
    import json
    results = """{
        "cards": [
            {
            "collectible": 1,
            "slug": "a-light-in-the-darkness",
            "artistName": "Zoltan Boros",
            "manaCost": 2,
            "name": "A Light in the Darkness",
            "text": "<b>Discover</b> a minion. Give it +1/+1.",
            "flavorText": "Wait, how can you have a light in the dark? If you turn on a light while it’s dark, doesn’t that mean it’s no longer dark?",
            "duels": {
                "relevant": true,
                "constructed": true
            },
            "hasImage": true,
            "hasImageGold": false,
            "hasCropImage": true,
            "keywords": [
                {
                "slug": "discover",
                "name": "Discover",
                "refText": "Choose one of three cards to add to your hand.",
                "text": "Choose one of three cards to add to your hand.",
                "gameModes": [
                    {
                    "slug": "constructed",
                    "name": "Standard & Wild Formats"
                    },
                    {
                    "slug": "battlegrounds",
                    "name": "Battlegrounds"
                    },
                    {
                    "slug": "duels",
                    "name": "Current Duels Cards"
                    },
                    {
                    "slug": "standard",
                    "name": "Standard"
                    }
                ]
                }
            ],
            "rarity": {
                "slug": "common",
                "craftingCost": [
                40,
                400
                ],
                "dustValue": [
                5,
                50
                ],
                "name": "Common"
            },
            "class": {
                "slug": "paladin",
                "name": "Paladin"
            },
            "type": {
                "slug": "spell",
                "name": "Spell",
                "gameModes": [
                {
                    "slug": "constructed",
                    "name": "Standard & Wild Formats"
                },
                {
                    "slug": "battlegrounds",
                    "name": "Battlegrounds"
                },
                {
                    "slug": "duels",
                    "name": "Current Duels Cards"
                },
                {
                    "slug": "standard",
                    "name": "Standard"
                }
                ]
            },
            "cardSet": {
                "name": "Whispers of the Old Gods",
                "slug": "whispers-of-the-old-gods",
                "type": "expansion",
                "collectibleCount": 134,
                "collectibleRevealedCount": 134,
                "nonCollectibleCount": 36,
                "nonCollectibleRevealedCount": 34
            },
            "spellSchool": {
                "slug": "holy",
                "name": "Holy"
            }
            }
        ]}"""
    results = json.loads(results)
class Hearthstone(API):
    @staticmethod
    def get_cards(page = 1, page_size = 10):
        query = {"page":page, "pageSize": page_size}
        results = API.get("/cards",query, "H_API")
        

        
        print(f"API Results: {results}")
        records = []
        # transform data
        if "cards" in results and results["cards"]:
            count = len(results["cards"])
            print(f"Num results {count}")
            for card in results["cards"]:
                if not card:
                    print(f"None card? {card}")
                    continue
                co = DictToObject(card)
                spell_school = ""
                print(f"Card Name: {co.name}")
                card_set = "No Set"
                if "spellSchool" in card and card["spellSchool"]:
                    spell_school = card["spellSchool"]["slug"]
                if "cardSet" in card and card["cardSet"]:
                    card_set = card["cardSet"]["slug"]
                record = {
                    "name": co.name,
                    "mana_cost": co.manaCost,
                    "text": co.text,
                    "flavor_text": co.flavorText,
                    "rarity": card["rarity"]["slug"],
                    "card_class": card["class"]["slug"],
                    "card_type": card["type"]["slug"],
                    "card_set":  card_set,
                    "spell_school":spell_school,
                    "source": "api"
                }
                records.append(record)
        return records

if __name__ == "__main__":
    Hearthstone.get_cards(1,1)