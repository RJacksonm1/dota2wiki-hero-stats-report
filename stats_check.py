from wikitools import *
from config import config
import json
import urllib2
import vdf
import re


infobox_re = re.compile("{{Hero infobox\s(.+?)\s}}", re.DOTALL | re.MULTILINE)
param_re = re.compile("^\s*\|\s*(.+?)\s*=\s*(.+)$", re.MULTILINE)

def main():
    with open("npc_heroes.txt", "r") as f:
        hero_data = vdf.loads(f.read())["DOTAHeroes"]
    heroes = json.loads(urllib2.urlopen("http://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1/?key={}&language=en_us&itemizedonly".format(config["webapi_key"])).read())["result"]["heroes"]
    w = wiki.Wiki(config["api"])

    report_data = {}
    for hero in heroes:
        print(hero)
        report_data[hero["localized_name"]] = []
        text = page.Page(w, title=hero["localized_name"]).getWikiText()
        infobox_params = infobox_re.search(text).group(1)
        params = {k.lower(): v for k, v in param_re.findall(infobox_params)}
        vdf_base_data = hero_data["npc_dota_hero_base"]
        vdf_hero_data = hero_data[hero["name"]]

        # Do comparisons
        def compare(tuple1, tuple2):
            k1, v1 = tuple1
            k2, v2 = tuple2

            return (v1 == v2), tuple1, tuple2

        for a, b in [
            # ("attack backswing",    ""),  # Not sure where this data is from.
            # ("cast backswing",      ""),
            # ("cast point",          ""),
            ("agility",             "AttributeBaseAgility"),
            ("agility growth",      "AttributeAgilityGain"),
            ("armor",               "ArmorPhysical"),
            ("attack point",        "AttackAnimationPoint"),
            ("attack range",        "AttackRange"),
            ("bat",                 "AttackRate"),
            ("damage max",          "AttackDamageMax"),
            ("damage min",          "AttackDamageMin"),
            ("intelligence",        "AttributeBaseIntelligence"),
            ("intelligence growth", "AttributeIntelligenceGain"),
            ("movement speed",      "MovementSpeed"),
            ("missile speed",       "ProjectileSpeed"),
            ("sight range day",     "VisionDaytimeRange"),
            ("sight range night",   "VisionNighttimeRange"),
            ("strength",            "AttributeBaseStrength"),
            ("strength growth",     "AttributeStrengthGain"),
            ("turn rate",           "MovementTurnRate"),
        ]:

            val1 = params[a] if a in params else "-"
            val2 = vdf_hero_data.get(b, vdf_base_data.get(b))
            report_data[hero["localized_name"]].append(compare((a, val1), (b, val2)))

    report_to_wicky(w, report_data)


def report_to_wicky(w, report_data):
    p = page.Page(w, title="User:Robjackson/Hero stats report")
    text = "Comparison of Wiki hero stats vs npc_heroes.txt stats"

    for hero_name in sorted(report_data):
        # Table per heroes cause giant table 503's for some reason.
        text += """
=== {} ===
{{|
! Hero
! Parameter
! Wiki
! Game
! Match?
|-
""".format(hero_name)
        for t in report_data[hero_name]:
            data = (hero_name, t[1][0], t[1][1], t[2][1], " style='background:" + ("green" if t[0] is True else "red") + "' | " + str(t[0]))
            text += """| {0}
| {1}
| {2}
| {3}
| {4}
|-
""".format(*data)
        text += "|}\n"
    p.edit(text)


if __name__ == '__main__':
    main()

