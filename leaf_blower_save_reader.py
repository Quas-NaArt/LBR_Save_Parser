from base64 import b64decode
from datetime import datetime
from json import loads
import os


"""
All damage Sources lists:
cards, 
leafscends, relics, 
equipment count, equipment levels, curse count, blc count, dig count, petting count, trade count, borb slap count, wizard bonus.
pet levels, pet equipped,
unique levels, 
tool levels, tool equipped,
equipped crafts (all sources),
counter,
scrolls active,
pyramid milestone -25, -50, -75, -105, max pyramid floor, max tower floor,
-130,

shop sources:
gem shop: better pets, better uniques, supporter damage T1, supporter damage T2,
platinum shop: slap force,
cosmic shop: leaf damage,
obsidian shop: leaf damage,
silicon shop: leaf damage,
benitoite shop: leaf damage,
malachite shop: focused items,
hematite shop: energy storage,
plasma shop: more type damage, energy storage,
energy shop: energy storage, energelics,
kyanite shop: leaf damage multiplier,
silver token shop: leaf damage+, leaf damage%, 
gold token shop: leaf damage+, leaf damage%,
"""


def decode_save(save_name):
    """creates ascii string from b64 encoded file"""
    with open(save_name, "r") as file:
        save_encoded = file.read()
        file.close()
    save_decode = str(b64decode(save_encoded))
    return save_decode[2:-43], save_decode[-42:-2]


def fileappend(file, text):
    with open(file, "a") as file:
        file.write(text)


class LeafParser:
    def __init__(self, json, out_file) -> None:
        self.root = json
        self.out_file = out_file
        self._multioptions = {
            "trade_resources_multiplier": dict.fromkeys(self._leaves, 0),
            "resources_leaf_add": dict.fromkeys(self._leaves, 0),
            "damage_types": {
                "ancient": 0,
                "cosmic": 0,
                "cursed": 0,
                "exotic": 0,
                "gold": 0,
                "ice": 0,
                "lava": 0,
                "platinum": 0,
                "regular": 0,
            },
            "max_resource_storage": {"energy_electrical": 0},
            "max_resource_storage_pct": {"energy_electrical": 0},
        }

    def layer_drill(self, layer_path):
        dict_ = self.root
        for layer in layer_path:
            dict_ = dict_[layer]
        return dict_

    def read_layer_targets(self, layer, targets):
        """
        Reads a set list of target keys from every parent key in a given layer.
        i.e. layer[:][target_list]
        """

        # print(layer)
        # print(targets)
        headerstring = ",".join([""] + targets + ["\n"])
        fileappend(self.out_file, headerstring.upper())
        layerstring = ".".join(layer)
        # print(layerstring)
        drilled_layer = self.layer_drill(layer)
        for item in drilled_layer:
            tempstring = ".".join([layerstring, item])
            for target in targets:
                tempstring = ",".join([tempstring, str(drilled_layer[item][target])])
            tempstring = ",".join([tempstring, "\n"])
            # print(tempstring)
            fileappend(self.out_file, tempstring)

    def read_by_name(self, name):
        # print(self._layer_targets[name]["layer"])
        # print(self._layer_targets[name]["targets"])
        self.read_layer_targets(
            self._layer_targets[name]["layer"], self._layer_targets[name]["targets"]
        )

    def read_all(self):
        for name in self._layer_targets:
            fileappend(self.out_file, name.upper())
            self.read_by_name(name)

    _layer_targets = {
        "cards": {"layer": ["profiles", "def", "cards"], "targets": ["count"]},
        "relics": {"layer": ["profiles", "def", "relics"], "targets": ["count"]},
        "equipment": {
            "layer": ["profiles", "def", "equipment"],
            "targets": [
                "count",
                "upgrade_unlocked",
                "level",
            ],
        },
        "unique leaves": {
            "layer": ["profiles", "def", "unique_leaves"],
            "targets": ["upgrade_unlocked", "level", "active"],
        },
        "pets": {
            "layer": ["profiles", "def", "pets"],
            "targets": ["upgrade_unlocked", "level", "active"],
        },
        "weapons": {
            "layer": ["profiles", "def", "shops", "weapons"],
            "targets": ["level"],
        },
        "house items": {
            "layer": ["house_items"],
            "targets": ["unlocked"],
        },
        "scrolls": {
            "layer": [
                "profiles",
                "def",
                "scrolls",
            ],
            "targets": ["active"],
        },
        "challenges": {
            "layer": [
                "challenges",
            ],
            "targets": ["finished"],
        },
        "areas": {
            "layer": [
                "profiles",
                "def",
                "areas",
            ],
            "targets": ["highest_floor_stats"],
        },
        "pyramid milestones": {
            "layer": ["profiles", "def", "milestones", "inner_pyramid"],
            "targets": ["claimed"],
        },
        "tower milestones": {
            "layer": ["profiles", "def", "milestones", "tower"],
            "targets": ["claimed"],
        },
        "gem store": {
            "layer": ["shops_persist", "gems"],
            "targets": ["count", "inventory"],
        },
        "chests": {
            "layer": [
                "profiles",
                "def",
                "chests",
            ],
            "targets": [
                "count",
            ],
        },
    }

    def parse_stats(self):
        """
        groups of stats that have similar paths and single outputs
        i.e. layer[target_list]
        """
        combinations = {
            "simple_stats": {
                "layer": [
                    "profiles",
                    "def",
                    "objects",
                    "o_game",
                    "data",
                    "stats",
                ],
                "targets": [
                    "cursed_count",
                    "pets_pet",
                    "digs",
                    "prestige_crunch",
                    "trades_finished",
                    "borb_slapped",
                    "prestige_random_number",
                    "leaf_pub_counter",
                    "prestige",
                    "prestige_mlc",
                ],
            },
            "weapon": {
                "layer": [
                    "profiles",
                    "def",
                    "objects",
                    "o_game",
                    "data",
                ],
                "targets": [
                    "current_weapon_key",
                ],
            },
        }
        fileappend(self.out_file, "STAT,VALUE,\n")
        for combo in combinations:
            for stat in combinations[combo]["targets"]:
                stat_value = self.layer_drill(combinations[combo]["layer"] + [stat])
                fileappend(
                    self.out_file,
                    ".".join(combinations[combo]["layer"] + [stat])
                    + ","
                    + str(stat_value)
                    + ",\n",
                )

    def parse_leafscends(self):
        fileappend(self.out_file, "LEAFSCENSION,COUNT\n")
        layer = ["profiles", "def", "resources"]
        tempdict = self.layer_drill(layer)
        for leaf in tempdict.keys():
            if len(tempdict[leaf]["leafscend_count"]) > 0:
                for tier in tempdict[leaf]["leafscend_count"].keys():
                    fileappend(
                        self.out_file,
                        ".".join(layer + [leaf, "leafscend", tier])
                        + ","
                        + str(tempdict[leaf]["leafscend_count"][tier])
                        + "\n",
                    )

    def parse_crafts(self):

        # Instantiate property dict with all crafted leaf properties currently in the game.
        props = dict.fromkeys(
            self.layer_drill(
                [
                    "profiles",
                    "def",
                    "objects",
                    "o_game",
                    "data",
                    "stats",
                    "crafted_vars_seen",
                ]
            ),
            0,
        )

        # Some properties can affect different types of leaves or damage types.
        # Update the property dict to use a dict of values instead of a scalar for them.
        for i in self._multioptions.keys():
            props[i] = self._multioptions[i]

        with open(self.out_file, "a") as file:
            file.write("CRAFTED LEAF PROPERTY,TOTAL VALUE,\n")
        # For each equipped leaf, read its properties and add them to the running total.
        drill_layer = ["profiles", "def", "crafted_leaves"]
        leaflist = self.layer_drill(drill_layer)
        for leaf in leaflist:
            for prop in leaf["props"]:
                if prop in self._multioptions:
                    # print(prop)
                    if "__resource_key" in leaf["props"][prop]:
                        subproperty = leaf["props"][prop]["__resource_key"]
                    if "__collection_key" in leaf["props"][prop]:
                        subproperty = leaf["props"][prop]["__collection_key"]
                    # print(subproperty)
                    subproperty_value = leaf["props"][prop][subproperty]
                    # print(subproperty_value)
                    if subproperty in props[prop]:
                        # print("old:", props[prop][subproperty])
                        props[prop][subproperty] += subproperty_value
                    else:
                        props[prop][subproperty] = subproperty_value
                    # print("new:", props[prop][subproperty])
                else:
                    # print(prop)
                    props[prop] += leaf["props"][prop]
        for i in props:
            try:
                for j in props[i]:
                    fileappend(
                        self.out_file,
                        ",".join(
                            [
                                ".".join(drill_layer + [str(i), str(j)]),
                                str(props[i][j]),
                                "\n",
                            ]
                        ),
                    )
            except:
                # normal outputs
                fileappend(
                    self.out_file,
                    ",".join([".".join(drill_layer + [str(i)]), str(props[i]), "\n"]),
                )

    def parse_shops(self):
        """
        Read all items in all shops and extract target keys.
        i.e. layer[:][:][target_list]
        """

        layer = ["profiles", "def", "shops"]
        targets = ["count"]
        shop_dict = self.layer_drill(layer)
        fileappend(self.out_file, ",".join(["SHOP.ITEM"] + targets).upper() + ",\n")
        for shop in shop_dict:
            for shopitem in shop_dict[shop]:
                message = ".".join(layer + [shop, shopitem])
                for target in targets:
                    message = message + "," + str(shop_dict[shop][shopitem][target])
                fileappend(self.out_file, message + ",\n")

    _multioptions = dict()

    # _rarities = ["common_", "uncommon_", "rare_", "epic_", "mythical_", "legendary_"]

    # _enemies = [
    #     "alb",
    #     "angry_leaf",
    #     "bat",
    #     "bee",
    #     "bird",
    #     "bug",
    #     "carrot",
    #     "crab",
    #     "elk",
    #     "frog",
    #     "hare",
    #     "hyena",
    #     "ice_leaf",
    #     "scorpion",
    #     "snowman",
    #     "skull",
    #     "vulture",
    #     "tower_frog",
    #     "evil_bat",
    #     "evil_hare",
    #     "evil_crab",
    #     "evil_scorpion",
    #     "evil_snowman",
    #     "evil_brain",
    #     "evil_bird",
    #     "evil_carrot",
    #     "evil_skull",
    #     "evil_stone",
    #     "evil_factory",
    #     "evil_fire",
    #     "evil_ghast",
    #     "evil_head",
    #     "evil_hulk",
    #     "evil_klackon",
    #     "evil_lurker",
    #     "evil_mask",
    #     "evil_skull02",
    #     "boss_frog",
    #     "boss_bat",
    #     "boss_hare",
    #     "boss_crab",
    #     "boss_scorpion",
    #     "boss_snowman",
    #     "boss_brain",
    #     "boss_dragon",
    #     "boss_lavagolem",
    #     "boss_bob",
    #     "boss_stonegolem",
    #     "boss_factory",
    #     "boss_fire",
    #     "boss_ghast",
    #     "boss_head",
    #     "boss_hulk",
    #     "boss_lurker",
    #     "boss_mask",
    #     "boss_bob02",
    #     "boss_bob03",
    #     "boss_bob04",
    #     "boss_bob05",
    #     "boss_witch",
    #     "boss_centaur",
    #     "boss_vile_creature",
    #     "boss_air_elemental",
    #     "boss_spark_bubble",
    #     "boss_terror_blue",
    #     "boss_terror_green",
    #     "boss_terror_red",
    #     "boss_terror_purple",
    #     "boss_terror_super",
    #     "boss_energy_guard",
    # ]

    _leaves = [
        "leaves",
        "gold",
        "platinum",
        "bismuth",
        "cosmic",
        "void",
        "exotic",
        "celestial",
        "mythical",
        "lava",
        "ice",
        "obsidian",
        "silicon",
        "benitoite",
        "moonstone",
        "sand",
        "ancient",
        "sacred",
        "biotite",
        "malachite",
        "plasma",
        "hematite",
        "amber",
        "amethyst",
        "emerald",
        "kyanite",
        "rhodonite",
        "ruby",
        "tektite",
    ]

    # _equipments = [
    #     "Flail",
    #     "cheese_boots",
    #     "cursed_cheese",
    #     "hammer",
    #     "leaf_armor",
    #     "leaf_helm",
    #     "leaf_shield",
    #     "lil_doggo",
    #     "medkit",
    #     "mini_shovel",
    #     "ring_blc",
    #     "ring_zoo",
    #     "traders_suitcase",
    #     "viking_borb",
    #     "wizard_hat",
    # ]

    # _tools = [
    #     "hands",
    #     "leaf_rake",
    #     "leaf_rake_advanced",
    #     "leaf_blower",
    #     "leaf_blower_advanced",
    #     "nuclear_leaf_blower",
    #     "airplane_turbine",
    #     "leaf_powered_leaf_blower",
    #     "paint_roller",
    #     "rocket_engine",
    #     "lazer",
    #     "alien_turbine",
    #     "ace_of_spades",
    #     "blowfish",
    #     "gfx_card",
    #     "drill",
    #     "fan",
    #     "compressor",
    #     "bellows",
    #     "celestial_blower",
    #     "drill_ht",
    #     "carpenters_cup",
    #     "holy_grail",
    #     "bellows_ht",
    #     "ace_of_spades_ht",
    #     "shovel",
    #     "shovel_ht",
    #     "shovel_nuclear",
    #     "trout",
    #     "trout_ht",
    #     "trout_nuclear",
    #     "sword",
    # ]


def main():
    save_file = os.path.join(
        os.getenv("LOCALAPPDATA"), "blow_the_leaves_away", "save.dat"
    )
    print("Using save file at: ", save_file)
    out_file = os.path.join(os.getenv("USERPROFILE"), "Desktop", "LBR_Save.csv")
    print("Exporting results to: ", out_file)
    save_contents, contents_hash = decode_save(save_file)
    message = "Hash of save: " + str(contents_hash) + "\n"
    with open(out_file, "w") as file:
        file.write(message)
    message = "Time of export: " + str(datetime.now()) + "\n"
    fileappend(out_file, message)

    LP = LeafParser(loads(save_contents), out_file)
    del save_contents
    LP.parse_leafscends()
    LP.read_all()
    LP.parse_crafts()
    LP.parse_stats()
    LP.parse_shops()
    # csv_titles = ['path', 'value']
    # card_dict = create_dict(card_list(), save["profiles"]["def"]["cards"], 'count')

    # leafscend_dict = all_leafscend_values(save)
    # relic_dict = create_dict(relic_list(), save["profiles"]["def"]["relics"], 'count')

    # equip_count_dict = create_dict(equipments, save["profiles"]["def"]["equipment"], 'count')
    # equip_level_dict = create_dict(equipments, save["profiles"]["def"]["equipment"], 'level')
    # unique_level_dict = create_dict(sorted(return_keys(save["profiles"]["def"]["unique_leaves"])),
    #                                 save["profiles"]["def"]["unique_leaves"], 'level')
    # pet_level_dict = create_dict(sorted(return_keys(save["profiles"]["def"]["pets"])),
    #                              save["profiles"]["def"]["pets"], 'level')
    # pet_active_dict = create_dict(sorted(return_keys(save["profiles"]["def"]["pets"])),
    #                               save["profiles"]["def"]["pets"], 'active')
    # tool_level_dict = create_dict(tools, save["profiles"]["def"]["shops"]["weapons"], 'level')
    # tool_active = save["profiles"]["def"]["objects"]["o_game"]["data"]["current_weapon_key"]

    # dlc_active = create_dict(return_keys(dict(list(gen_dict_extract("dlc", save))[0])),
    #                          dict(list(gen_dict_extract("dlc", save))[0]), 'count')

    # print((return_keys(save["profiles"]["def"]["crafted_leaves"])))
    # crafted_leaves = save["profiles"]["def"]["crafted_leaves"]
    # slap_multiplier_craft = 0
    # for leaf in crafted_leaves:
    #     slap_multiplier_craft += leaf['props']["slap_multiplier_craft"]
    # print(slap_multiplier_craft)

    # print(dict(list(gen_dict_extract("dlc", save))[0]))
    # print(card_dict)
    # with open('test.csv', 'wb') as f:
    #     writer = csv.writer(f, delimiter=':')
    #     for row in card_dict.items():
    #         writer.writerow(row)

if __name__ == "__main__":
    main()
