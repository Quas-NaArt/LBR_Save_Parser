from base64 import b64decode
from datetime import datetime
from json import loads
import os
import platform


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
        headerstring = "\t".join([""] + targets + ["\n"])
        fileappend(self.out_file, headerstring.upper())
        layerstring = ".".join(layer)
        # print(layerstring)
        drilled_layer = self.layer_drill(layer)
        for item in drilled_layer:
            tempstring = ".".join([layerstring, item])
            for target in targets:
                tempstring = "\t".join([tempstring, str(drilled_layer[item][target])])
            tempstring = "\t".join([tempstring, "\n"])
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
            "average/second": {
                "layer": [
                    "profiles",
                    "def",
                    "objects",
                    "o_game",
                    "data",
                    "stats",
                    "resources_collected_avg",
                ],
                "targets": self._leaves,
            },
        }
        fileappend(self.out_file, "STAT\tVALUE\n")
        for combo in combinations:
            for stat in combinations[combo]["targets"]:
                stat_value = self.layer_drill(combinations[combo]["layer"] + [stat])
                fileappend(
                    self.out_file,
                    ".".join(combinations[combo]["layer"] + [stat])
                    + "\t"
                    + str(stat_value)
                    + "\n",
                )

    def parse_leafscends(self):
        fileappend(self.out_file, "LEAFSCENSION\tCOUNT\n")
        layer = ["profiles", "def", "resources"]
        tempdict = self.layer_drill(layer)
        for leaf in tempdict.keys():
            if len(tempdict[leaf]["leafscend_count"]) > 0:
                for tier in tempdict[leaf]["leafscend_count"].keys():
                    fileappend(
                        self.out_file,
                        ".".join(layer + [leaf, "leafscend", tier])
                        + "\t"
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
            file.write("CRAFTED LEAF PROPERTY\tTOTAL VALUE\n")
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
                        "\t".join(
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
                    "\t".join([".".join(drill_layer + [str(i)]), str(props[i]), "\n"]),
                )

    def parse_shops(self):
        """
        Read all items in all shops and extract target keys.
        i.e. layer[:][:][target_list]
        """

        layer = ["profiles", "def", "shops"]
        targets = ["count"]
        shop_dict = self.layer_drill(layer)
        fileappend(self.out_file, "\t".join(["SHOP.ITEM"] + targets).upper() + "\n")
        for shop in shop_dict:
            for shopitem in shop_dict[shop]:
                message = ".".join(layer + [shop, shopitem])
                for target in targets:
                    message = message + "\t" + str(shop_dict[shop][shopitem][target])
                fileappend(self.out_file, message + "\n")

    _multioptions = dict()

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
        "hematite",
        "plasma",
        "amber",
        "amethyst",
        "emerald",
        "kyanite",
        "rhodonite",
        "ruby",
        "tektite",
    ]

LBR_STEAM_APP_ID = "1468260"

def save_path():
    system = platform.system()

    if system == 'Windows':
        base_path = os.getenv("LOCALAPPDATA")
    elif system == 'Linux':
        home = os.getenv("XDG_DATA_HOME")
        if home is None:
            home = os.path.join(os.getenv("HOME"), ".local", "share")

        # Steam uses a simulated windows C drive to run Leaf Blower Revolution on linux.
        base_path = os.path.join(home, 'Steam', 'steamapps', 'compatdata', LBR_STEAM_APP_ID, 'pfx', 'drive_c', 'users', 'steamuser', 'AppData', 'Local')
    else:
        raise RuntimeError(f'Unknown platform {system=}')

    return os.path.join(base_path, 'blow_the_leaves_away', 'save.dat')


def out_file_path():
    system = platform.system()

    if system == 'Windows':
        home = os.getenv("USERPROFILE")
    elif system == 'Linux':
        home = os.getenv("HOME")
    else:
        raise RuntimeError(f'Unknown platform {system=}')

    return os.path.join(home, 'Desktop', 'LBR_Save.csv')


def main():
    save_file = save_path()
    print("Using save file at: ", save_file)
    out_file = out_file_path()
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


if __name__ == "__main__":
    main()
