import random
import time
import ag_utilities
import db


def set_items(env, location):
    menu_idx = 0
    content_types = db.rec_list(env, "content_type", "name")
    for content_type in content_types:
        records = db.ret_recs(env, "content", [["location", location],
                                               ["content_type", content_type],
                                               ["available", True]])
        for idx in range(len(records)):
            # activate the items for current visit to location
            content_name = db.ret(records[idx], "name")
            menu_idx += 1
            env = db.upd_val(env, "content", "name", content_name,
                             "active", True)
            env = db.upd_val(env, "content", "name", content_name,
                             "menu_idx", str(menu_idx))
    return env


def get_items_prompt(env, location):
    prompt = ""
    prompt_options = []

    records = db.ret_recs(env, "content", [["location", location],
                                           ["active", True]])
    for record in records:
        content_type = db.ret(record, "content_type")
        name = db.ret(record, "name")
        action = db.ret_val(env, "content_type", "name",
                            content_type, "action")
        menu_idx = db.ret(record, "menu_idx")

        prompt += f"\n{action} {name} - {menu_idx}"
        prompt_options.append(str(menu_idx))
    return [prompt, prompt_options]


def get_items_display(env, location):
    contents_display = ""

    records = db.ret_recs(env, "content", [["location", location],
                                           ["active", True]])
    records_cnt = len(records)

    for records_idx in range(records_cnt):
        if contents_display != "":
            contents_display += ", "

            # only append "and" if more than one item in list
            if records_idx == records_cnt - 1:
                contents_display += "and "

        # content item name
        item_name = db.ret(records[records_idx], "name")
        contents_display += "a " + item_name

    if contents_display == "":
        contents_display = "nothing."
    else:
        contents_display += "."

    return contents_display


def look_around(env, location):
    contents_display = get_items_display(env, location)
    msg = f"Inside the {location} you see {contents_display}"
    ag_utilities.print_pause(msg)


def update_after_action(env, location, content_type, content_name):
    # update player score
    player_points_earned = ag_utilities.get_player_val(env, "points_earned")
    content_points = db.ret_val(env, content_type, "name",
                                content_name, "points")
    total_points = player_points_earned + content_points
    env = ag_utilities.set_player_val(env, "points_earned", total_points)

    # update player inventory
    inventory = ag_utilities.get_player_val(env, content_type)
    inventory.append(content_name)
    env = ag_utilities.set_player_val(env, content_type, inventory)

    # deactivate content
    env = db.upd_val(env, "content", "name", content_name, "available", False)
    env = db.upd_val(env, "content", "name", content_name, "active", False)
    env = db.upd_val(env, "content", "name", content_name, "menu_idx", "")

    # update the menu_indexes of the remaining content items
    records = db.ret_recs(env, "content",
                          [["location", location], ["active", True]])
    menu_idx = 0
    for record in records:
        menu_idx += 1
        content_name = db.ret(record, "name")
        env = db.upd_val(env, "content", "name", content_name,
                         "menu_idx", str(menu_idx))

    env = ag_utilities.game_over_check(env)

    return env


def fight(env, location, adversary_name):
    ag_utilities.print_pause(f"You are fighting the {adversary_name}...")

    while True:
        time.sleep(1)
        fight_data = get_fight_data(env, adversary_name)

        if ag_utilities.flip_coin():
            env = strike_by_player(env, location, fight_data, adversary_name)
            adversary_defeated = not db.ret_val(env, "content", "name",
                                                adversary_name, "active")
            if adversary_defeated:
                return env
        else:
            env = strike_by_adversary(env, fight_data, adversary_name)

        # check: game over
        if ag_utilities.get_player_val(env, "game_end_type") != "":
            return env
    return env


def strike_by_player(env, location, fight_data, adversary_name):
    adversary_health = db.ret(fight_data, "adversary_health")
    player_weapon_name = db.ret(fight_data, "player_weapon_name")
    player_weapon_power = db.ret(fight_data, "player_weapon_power")

    adversary_health -= player_weapon_power
    if adversary_health < 0:
        adversary_health = 0
    env = db.upd_val(env, "adversary", "name", adversary_name,
                     "health", adversary_health)

    msg = (f"You struck the {adversary_name} with your {player_weapon_name}."
           f" The {adversary_name}'s health is {adversary_health}.")
    ag_utilities.print_pause(msg)

    if adversary_health == 0:
        msg = f"Congratulations, you defeated the {adversary_name}!\n"
        ag_utilities.print_pause(msg)

        # update content records and player inventory
        return update_after_action(env, location, "adversary", adversary_name)

    return env


def strike_by_adversary(env, fight_data, adversary_name):
    # setup fight data
    player_armor_protection = db.ret(fight_data, "player_armor_protection")
    player_health = db.ret(fight_data, "player_health")
    adversary_power = db.ret(fight_data, "adversary_power")

    # adversary's power is reduced by the strength of the player's armor
    armor_protection = (1 - (player_armor_protection / 100))
    player_health -= int(adversary_power * armor_protection)

    if player_health <= 0:
        player_health = 0
    env = ag_utilities.set_player_val(env, "health", player_health)

    msg = f"The {adversary_name} struct you. Your health is {player_health}."
    ag_utilities.print_pause(msg)

    if player_health == 0:
        msg = f"You were defeated by the {adversary_name}."
        ag_utilities.print_pause(msg)

    # check: game over
    env = ag_utilities.game_over_check(env)
    if ag_utilities.get_player_val(env, "game_end_type") != "":
        return env

    return env


def get_fight_data(env, adversary):
    data = []

    # setup adversary
    adversary_health = db.ret_val(env, "adversary", "name",
                                  adversary, "health")
    adversary_power = db.ret_val(env, "adversary", "name", adversary, "power")

    # setup player
    player_health = ag_utilities.get_player_val(env, "health")

    # setup player - weapon
    player_weapon_power = 0
    player_weapon_list = ag_utilities.get_player_val(env, "weapon")
    for weapon in player_weapon_list:
        power = db.ret_val(env, "weapon", "name", weapon, "power")
        if power > player_weapon_power:
            player_weapon_name = weapon
            player_weapon_power = power

    # player armor
    player_armor_protection = 0
    player_armor_list = ag_utilities.get_player_val(env, "armor")
    for armor in player_armor_list:
        player_armor_protection += db.ret_val(env, "armor", "name",
                                              armor, "protection")

    data.append(["adversary_health", adversary_health])
    data.append(["adversary_power", adversary_power])
    data.append(["player_health", player_health])
    data.append(["player_armor_protection", player_armor_protection])
    data.append(["player_weapon_name", player_weapon_name])
    data.append(["player_weapon_power", player_weapon_power])

    return data


def fight_before_gather(env, location):
    while True:
        # check for adversaries
        records = db.ret_recs(env, "content", [["location", location],
                                               ["active", True],
                                               ["content_type", "adversary"]])
        adversary_cnt = len(records)
        if adversary_cnt == 0:
            return env

        # select adversary to attack
        records_idx = random.randint(0, adversary_cnt - 1)
        adversary_name = db.ret(records[records_idx], "name")

        # process a single blow from the adversary
        ag_utilities.print_pause(f"\nThe {adversary_name} attacked you!")
        fight_data = get_fight_data(env, adversary_name)
        env = strike_by_adversary(env, fight_data, adversary_name)

        # check: game over after attack
        if ag_utilities.get_player_val(env, "game_end_type") != "":
            return env

        # ask to fight or leave
        prompt = (f"\nFight the {adversary_name} - 1"
                  f"\nExit the {location} - 2")
        action = ag_utilities.valid_input(prompt, ["1", "2"])
        if action == "1":
            env = fight(env, location, adversary_name)
            if ag_utilities.get_player_val(env, "game_end_type") != "":
                return env
        elif action == "2":
            # leave location
            return ag_utilities.set_player_val(env, "location", "")


def pickup(env, location, content_type, item_name):
    # player can only pickup content if there are no adversaries guarding it
    adversary_cnt = db.rec_cnt(env, "content", [["location", location],
                                                ["active", True],
                                                ["content_type", "adversary"]])
    if adversary_cnt > 0:
        msg = (f"You must defeat any adversaries before "
               f"you can pickup the {item_name}.")
        ag_utilities.print_pause(msg)
        return env

    # pick up item...
    ag_utilities.print_pause(f"You picked up the {item_name}.")

    # update content records and player inventory
    return update_after_action(env, location, content_type, item_name)


def process_action(env, location, menu_idx):
    records = db.ret_recs(env, "content", [["location", location],
                                           ["menu_idx", menu_idx]])

    name = db.ret(records[0], "name")
    content_type = db.ret(records[0], "content_type")
    action = db.ret_val(env, "content_type", "name",
                        content_type, "action").lower()

    if action == "fight":
        return fight(env, location, name)
    elif action == "pickup":
        return pickup(env, location, content_type, name)


def explore_location(env, location):
    while True:
        # get location content prompt info
        location_prompt = get_items_prompt(env, location)
        location_prompt_display = location_prompt[0]
        location_prompt_options = location_prompt[1]

        # set player prompt - display
        prompt = ("\nLook around - l"
                  f"{location_prompt_display}"
                  "\nDisplay quest objectives - o"
                  "\nDisplay scoreboard and inventory - d"
                  f"\nExit the {location} - e"
                  "\nQuit game - q")

        # set player prompt - options list
        prompt_options = ["l", "o", "d", "e", "q"]
        prompt_options.extend(location_prompt_options)

        # get player action
        action = ag_utilities.valid_input(prompt, prompt_options)

        # process player action
        if action == "l":
            look_around(env, location)
        elif action == "o":
            ag_utilities.display_quest_objectives(env)
        elif action == "d":
            ag_utilities.display_scoreboard(env)
        elif action == "e":
            ag_utilities.print_pause(f"You are leaving the {location}.")
            return env
        elif action == "q":
            exit()
        else:
            env = process_action(env, location, action)

            # check: game over
            if ag_utilities.get_player_val(env, "game_end_type") != "":
                return env

            # update location content status for player
            look_around(env, location)


def enter_location(env, location_idx):
    # init location
    location = db.ret_val_idx(env, "location", location_idx, "name")
    env = ag_utilities.set_player_val(env, "location", location)
    env = set_items(env, location)

    # orientate player
    ag_utilities.print_pause(f"\nYou have entered the {location}.")
    look_around(env, location)

    # fight before gather if set for this location
    if db.ret_val(env, "location", "name", location, "fight_before_gather"):
        env = fight_before_gather(env, location)

        # check: game over
        if ag_utilities.get_player_val(env, "game_end_type") != "":
            return env

        # check: leave location
        if ag_utilities.get_player_val(env, "location") == "":
            return env

    # explore location
    return explore_location(env, location)
