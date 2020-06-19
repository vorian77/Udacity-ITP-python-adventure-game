import random
import db
import ag_utilities


def setup():
    # init game data storage...
    # provides efficient configurability and extensibility of game
    # includes locations (that player can enter), and content that
    # will be available in the locations
    # also initiates player status - score, health, inventory, etc.

    env = []

    # init content_type table and meta data
    env = db.ins_tab(env, "content_type")
    env = db.ins_rec(env, "content_type", [["name", "armor"],
                                           ["action", "Pickup"]])
    env = db.ins_rec(env, "content_type", [["name", "adversary"],
                                           ["action", "Fight"]])
    env = db.ins_rec(env, "content_type", [["name", "treasure"],
                                           ["action", "Pickup"]])
    env = db.ins_rec(env, "content_type", [["name", "weapon"],
                                           ["action", "Pickup"]])

    # init table - adversary
    env = db.ins_tab(env, "adversary")
    env = db.ins_rec(env, "adversary", [["name", "dragon"],
                                        ["health", 100],
                                        ["power", 40],
                                        ["points", 75]])
    env = db.ins_rec(env, "adversary", [["name", "dementor"],
                                        ["health", 80],
                                        ["power", 30],
                                        ["points", 60]])
    env = db.ins_rec(env, "adversary", [["name", "troll"],
                                        ["health", 60],
                                        ["power", 20],
                                        ["points", 50]])
    env = db.ins_rec(env, "adversary", [["name", "ogre"],
                                        ["health", 40],
                                        ["power", 10],
                                        ["points", 40]])
    env = db.ins_rec(env, "adversary", [["name", "nymph"],
                                        ["health", 30],
                                        ["power", 5],
                                        ["points", 20]])

    # init table - armor
    env = db.ins_tab(env, "armor")
    env = db.ins_rec(env, "armor", [["name", "breast plate"],
                                    ["protection", 40],
                                    ["points", 30]])
    env = db.ins_rec(env, "armor", [["name", "shield"],
                                    ["protection", 30],
                                    ["points", 20]])
    env = db.ins_rec(env, "armor", [["name", "helmet"],
                                    ["protection", 20],
                                    ["points", 10]])

    # init table - treasure
    env = db.ins_tab(env, "treasure")
    env = db.ins_rec(env, "treasure", [["name", "crown"], ["points", 75]])
    env = db.ins_rec(env, "treasure", [["name", "chalis"], ["points", 60]])
    env = db.ins_rec(env, "treasure", [["name", "necklace"], ["points", 45]])
    env = db.ins_rec(env, "treasure", [["name", "ring"], ["points", 30]])

    # init table - weapon
    env = db.ins_tab(env, "weapon")
    env = db.ins_rec(env, "weapon", [["name", "sword"],
                                     ["power", 30],
                                     ["points", 50]])
    env = db.ins_rec(env, "weapon", [["name", "staff"],
                                     ["power", 20],
                                     ["points", 40]])
    env = db.ins_rec(env, "weapon", [["name", "dagger"],
                                     ["power", 15],
                                     ["points", 30]])
    env = db.ins_rec(env, "weapon", [["name", "hand"],
                                     ["power", 5],
                                     ["points", 10]])

    # init table - locations
    # scramble locations so order is different each play
    locations = ["castle", "cave", "field", "forest", "village"]
    locations = ag_utilities.sample(env, locations)

    env = db.ins_tab(env, "location")
    for location in locations:
        fbg_mode = ag_utilities.flip_coin()
        env = db.ins_rec(env, "location", [["name", location],
                                           ["fight_before_gather", fbg_mode]])

    # init table - content
    # distribute content among locations
    env = db.ins_tab(env, "content")

    content_types = db.rec_list(env, "content_type", "name")
    locations = db.rec_list(env, "location", "name")
    locations_cnt = len(locations)
    idx_item = -1

    for content_type in content_types:
        # get list of contents of type content_type
        contents = db.rec_list(env, content_type, "name")

        # scramble list so locations have different content each play
        contents = ag_utilities.sample(env, contents)

        for item in contents:
            idx_item += 1
            location_idx = idx_item % locations_cnt

            # add data of content record
            # create content record
            env = db.ins_rec(env, "content",
                             [["location", locations[location_idx]],
                              ["content_type", content_type],
                              ["name", item],
                              ["available", True],
                              ["active", False],
                              ["menu_idx", ""]
                              ])

    # set health based on the number of adversaries
    adversary_count = db.rec_cnt(env, "adversary", [[]])
    health_per_adversary = 35
    health = adversary_count * health_per_adversary

    # init table - player
    # use id=0 to represent single player in game
    env = db.ins_tab(env, "player")
    env = db.ins_rec(env, "player",
                     [["id", 0],
                      ["points_earned", 0],
                      ["objectives", ["crown"]],
                      ["health", health],
                      ["location", ""],
                      ["adversary", []],
                      ["armor", []],
                      ["treasure", []],
                      ["weapon", []],
                      ["game_end_type", ""]
                      ])

    # init player with "hand" by adding "hand" to players weapon inventory
    env = db.upd_val(env, "player", "id", 0, "weapon", ["hand"])
    env = db.upd_val(env, "content", "name", "hand", "available", False)

    return env
