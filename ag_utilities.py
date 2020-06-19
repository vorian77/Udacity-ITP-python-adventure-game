"""
utilites used throughout the adventure game program
"""

import time
import random
import db


def print_pause(msg):
    print(msg.upper())
    time.sleep(1)


def valid_input(prompt, options):
    prompt = "\nEnter an action..." + prompt
    while True:
        response = input(prompt + "\n\n").lower()
        time.sleep(1)
        if response in options:
            return response
        print_pause("Sorry, I don't understand.")


def get_quest_objectives(env):
    # create a list of items required to win the game
    msg = ""
    objectives = get_player_val(env, "objectives")
    obj_cnt = len(objectives)
    for idx in range(obj_cnt):
        if idx > 0:
            msg += ", "
            if idx == obj_cnt - 1:
                msg += "and "
        msg += f"the {objectives[idx]}"
    return msg


def display_quest_objectives(env):
    objectives = get_quest_objectives(env)
    msg = f"\nIn order to realize your quest, you must collect {objectives}."
    print_pause(msg)


def display_scoreboard(env):
    points_earned = get_player_val(env, "points_earned")
    health = get_player_val(env, "health")
    treasure = ", ".join(get_player_val(env, "treasure"))
    armor = ", ".join(get_player_val(env, "armor"))
    weapons = ", ".join(get_player_val(env, "weapon"))
    adversary = ", ".join(get_player_val(env, "adversary"))

    print("\nSCOREBOARD AND INVENTORY",
          "\nPoints-Earned:", points_earned,
          "\nHealth:", health,
          "\nTreasure:", treasure,
          "\nArmor:", armor,
          "\nWeapon(s):", weapons,
          "\nAdversary(s):", adversary
          )


def game_over_check(env):
    # check - health
    player_health = get_player_val(env, "health")
    if player_health == 0:
        env = set_player_val(env, "game_end_type", "loss")
        return env

    # check - collected required inventory
    player_treasures = get_player_val(env, "treasure")
    inventory_objectives = get_player_val(env, "objectives")

    objectives_met = True
    for obj in inventory_objectives:
        if obj not in player_treasures:
            objectives_met = False
            break
    if objectives_met:
        env = set_player_val(env, "game_end_type", "won")
        return env

    return env


def sample(env, source_list):
    # provide scrambled list of records in table
    # like random.sample() function
    source_list_cnt = len(source_list)
    new_list = []

    while len(new_list) < source_list_cnt:
        idx = random.randint(0, source_list_cnt - 1)
        val = source_list[idx]
        if val not in new_list:
            new_list.append(val)

    return new_list


def flip_coin():
    return random.choice([True, False])


def get_player_val(env, key):
    return db.ret_val(env, "player", "id", 0, key)


def set_player_val(env, key, value):
    return db.upd_val(env, "player", "id", 0, key, value)
