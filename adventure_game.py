import time
import random
import db  # pseudo DBMS with CRUD functionality that only uses the list object
import ag_setup  # used to initialize the game database
import ag_location  # activities that occur when the player enters a location
import ag_utilities  # functions shared across the game libraries


def intro(env):
    objectives = ag_utilities.get_quest_objectives(env)

    ag_utilities.print_pause("Greetings noble knight!")
    ag_utilities.print_pause("Congratulations on accepting the challenge "
                             "to rescue the kingdom.")
    ag_utilities.print_pause("You must travel the Road of Edridor and "
                             f"recover {objectives}")
    ag_utilities.print_pause("stolen from our queen and hidden "
                             "somewhere in the land.")
    ag_utilities.print_pause("During your quest you will encounter "
                             "formidable creatures that guard the treasure.")
    ag_utilities.print_pause("Throughout you journey collect armor and "
                             "weapons you'll need to fight and defeat them.")
    ag_utilities.print_pause("Good luck!")


def game_over(env):
    # check for game over
    game_end_type = ag_utilities.get_player_val(env, "game_end_type")
    if game_end_type == "":
        return False
    else:
        # create player game over msg
        msg = ""

        if game_end_type == "won":
            msg = ag_utilities.get_quest_objectives(env)
            msg = f"\nYou realized the quest by collecting {msg}!"

        # process game over
        ag_utilities.print_pause("\nGame Over")
        ag_utilities.print_pause(f"\nYou {game_end_type} the game." + msg)

        prompt = ("\nPlay again - 1\nQuit - 2")
        play_again = ag_utilities.valid_input(prompt, ["1", "2"])
        if play_again == "1":
            return True
        else:
            exit()


def get_action(env):
    # init location prompts
    prompt_options_display = ""
    prompt_options_valid = ["l", "o", "d", "q"]

    # set location prompts
    locations_display = ""
    locations = db.rec_list(env, "location", "name")
    locations_cnt = len(locations)

    for idx in range(locations_cnt):
        prompt_options_valid.append(str(idx))
        prompt_options_display += f"\nEnter the {locations[idx]} - {idx}"

        if idx > 0:
            locations_display += ", "
            if idx == locations_cnt - 1:
                locations_display += "and "
        locations_display += "a " + locations[idx]

    msg = f"\nYou are on the Road of Edridor and see {locations_display}."
    ag_utilities.print_pause(msg)

    prompt = ("\nLook around - l"
              f"{prompt_options_display}"
              "\nDisplay quest objectives - o"
              "\nDisplay scoreboard and inventory - d"
              "\nQuit game - q")

    return ag_utilities.valid_input(prompt, prompt_options_valid)


def process_action(env, action):
    if action == "l":
        # continue loop, location shows each iteration
        return env
    elif action == "o":
        ag_utilities.display_quest_objectives(env)
        return env
    elif action == "d":
        ag_utilities.display_scoreboard(env)
        return env
    elif action == "q":
        exit()
    else:
        return ag_location.enter_location(env, int(action))


def play(env):
    while True:
        action = get_action(env)
        env = process_action(env, action)
        if game_over(env):
            return True


def play_game():
    while True:
        env = ag_setup.setup()
        intro(env)
        if not play(env):
            break


play_game()
