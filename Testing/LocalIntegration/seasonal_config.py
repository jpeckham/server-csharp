"""Read-only regression checks for seasonal bot references; no server required."""
import argparse
import json
from pathlib import Path
import unittest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data", type=Path, required=True, help="SPT_Data directory")
args = parser.parse_args()
config = json.loads((args.data / "configs/seasonalevents.json").read_text(encoding="utf-8-sig"))
bots = {p.stem.lower() for p in (args.data / "database/bots/types").glob("*.json")}


class SeasonalConfigTests(unittest.TestCase):
    def test_all_seasonal_bot_references_exist(self):
        self.assertTrue(bots, "No bot database found")
        for section in ("eventGear", "eventLoot", "botAppearanceChanges"):
            for event, changes in config[section].items():
                for role in changes:
                    with self.subTest(section=section, event=event, role=role):
                        self.assertIn(role.lower(), bots)

    def test_both_pmc_factions_receive_seasonal_gear_and_appearances(self):
        for section, event in (("eventGear", "halloween"), ("eventGear", "christmas"),
                               ("botAppearanceChanges", "CHRISTMAS")):
            with self.subTest(section=section, event=event):
                roles = {key.lower() for key in config[section][event]}
                self.assertTrue({"pmcbear", "pmcusec"}.issubset(roles))


if __name__ == "__main__":
    unittest.main(argv=[__file__], verbosity=2)
