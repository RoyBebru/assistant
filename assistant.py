#!/usr/bin/env python3

import atexit
import json
import os
from pathlib import Path
import re
import sys


"""CONSTANTS"""
path = Path(sys.argv[0])
SCRIPT_NAME = path.name
SCRIPT_DIR = path.parent.resolve()
PHONEBOOK_PATHFILE = SCRIPT_DIR / (path.stem + ".pb")
HISTFILE = SCRIPT_DIR / (path.stem + ".history")

PATTERN_PHONE_NUMBER = re.compile(
        r"(?:\+\d{1,3})?\s*(?:\(\d{2,5}\)|\d{2,5})?"
        r"\s*\d{1,3}(?:\s*-)?\s*\d{1,3}(?:\s*-)?\s*\d{1,3}")

pattern_for_one_name = (r"\b\w(?![0-9_])"
                        r"(?:(?<![0-9_])(?:\w|['-])(?![0-9_]))*"
                        r"(:?\w(?![0-9_]))?\b")
PATTERN_USERNAME = re.compile(pattern_for_one_name
                              + r"(?:\s" + pattern_for_one_name
                              +   r"(?:\s" + pattern_for_one_name + r")?"
                              + r")?", re.IGNORECASE)


#<<< Turn on editable possibility in input()
try:
    import readline
    readline.read_history_file(HISTFILE)
    # default history len is -1 (infinite), which may grow unruly
    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, HISTFILE)
except FileNotFoundError:
    pass
except ModuleNotFoundError:
    pass
#>>>


g_phone_book = {}

def dump_phonebook():
    try:
        with open(PHONEBOOK_PATHFILE, "w") as fh:
            fh.write(json.dumps(g_phone_book, indent=2))
    except PermissionError:
        return

def load_phonebook():
    global g_phone_book
    try:
        with open(PHONEBOOK_PATHFILE, "r") as fh:
            g_phone_book = json.loads(fh.read())
    except FileNotFoundError:
        g_phone_book = {}
    except PermissionError:
        return

def get_name_phone_from_book(name: str):
    name = name.lower()
    for person in g_phone_book.keys():
        if name == person.lower():
            return (person, g_phone_book[person])
    return (name, "")

def cmd_hello(_: str):
    return "How can I help you?"

def cmd_add(arg: str): # raise ValueError
    global g_phone_book
    mn = PATTERN_USERNAME.search(arg)
    if not bool(mn):
        raise ValueError("Usage format: add <Name> <Phone Number>")
    if mn.start() != 0:
        raise ValueError(f"Uknown text '{arg[:mn.start()]}' in the beginning")
    name = arg[:mn.end()]
    arg = arg[mn.end():].lstrip()
    mp = PATTERN_PHONE_NUMBER.search(arg)
    if not bool(mp):
        raise ValueError("Absent <Phone Number>. Usage format: "
                         "add <Name> <Phone Number>")
    if mp.start() != 0:
        raise ValueError(f"Uknown text '{arg[:mp.start()]}' "
                         "between name and phone number")
    if mp.end() != len(arg):
        raise ValueError(f"Uknown text '{arg[mp.end():]}' in the end")
    arg = arg.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
    phone = get_name_phone_from_book(name)[1]
    if bool(phone):
        raise ValueError(f"{name} already has phone number {phone}")
    g_phone_book[name] = arg
    return ""

def cmd_change(arg: str):
    global g_phone_book
    mn = PATTERN_USERNAME.search(arg)
    if not bool(mn):
        raise ValueError("Usage format: change <Name> <Phone Number>")
    if mn.start() != 0:
        raise ValueError(f"Uknown text '{arg[:mn.start()]}' in the beginning")
    name = arg[:mn.end()]
    arg = arg[mn.end():].lstrip()
    mp = PATTERN_PHONE_NUMBER.search(arg)
    if not bool(mp):
        raise ValueError("Absent <Phone Number>. Usage format: "
                         "change <Name> <Phone Number>")
    if mp.start() != 0:
        raise ValueError(f"Uknown text '{arg[:mp.start()]}' "
                         "between name and phone number")
    if mp.end() != len(arg):
        raise ValueError(f"Uknown text '{arg[mp.end():]}' in the end")
    arg = arg.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
    (old_name, phone) = get_name_phone_from_book(name)
    if bool(phone):
        g_phone_book[old_name] = arg
        return f"Changed {phone} with {arg} for {old_name}"
    g_phone_book[name] = arg
    return f"add {arg} for {name}"

def formatted_result(names: list):
    names.sort(key=lambda n: n.lower()) # case insensitive sorting
    max_name_len = len(max(names, key=len))
    result = ""
    print_format = "{:>" + str(max_name_len) + "s}: {:s}"
    for name in names:
        if bool(result):
            result += os.linesep
        result += print_format.format(name, g_phone_book[name])
    return result

def cmd_phone(arg: str):
    mn = PATTERN_USERNAME.search(arg)
    if not bool(mn):
        raise ValueError("Usage format: phone <Name> <Phone Number>")
    if mn.start() != 0:
        raise ValueError(f"Uknown text '{arg[:mn.start()]}' in the beginning")
    name = arg[:mn.end()]
    namelow = name.lower()

    names = []
    for key_name in g_phone_book.keys():
        if key_name.lower().find(namelow) != -1:
            names.append(key_name)

    if len(names) == 0:
        raise ValueError(f"THere is absent phone number for {name}")
    
    return formatted_result(names)

def cmd_show_all(_: str):
    names = list(g_phone_book.keys())
    if len(names) == 0:
        return ""
    return formatted_result(names)

def cmd_good_bye(_: str):
    dump_phonebook()
    return """
⠀⠀⠀⠀⣠⣶⡾⠏⠉⠙⠳⢦⡀⠀⠀⠀ ⢠⠞⠉⠙⠉⠙⠲⡀⠀
⠀⠀⠀⣴⠿⠏⠀⠀⠀⠀⠀⠀ ⢳⡀⠀ ⡏⠀⠀⠀⠀   ⢷
⠀⠀⢠⣟⣋⡀⢀⣀⣀⡀ ⣀⡀ ⣧  ⢸ Good   ⡇
⠀⠀⢸⣯⡭⠁⠸⣛⣟⠆⡴⣻⡲ ⣿⠀⣸⠀        ⡇
⠀⠀⣟⣿⡭⠀⠀⠀⠀ ⢱⠀⠀ ⣿⠀⢹    bye! ⡇
⠀⠀⠙⢿⣯⠄⠀⠀⠀⢀⡀⠀⠀⡿⠀⠀ ⡇⠀⠀⠀⠀   ⡼
⠀⠀⠀⠀⠹⣶⠆⠀⠀⠀⠀⠀⡴⠃⠀⠀ ⠘⠤⣄⣠⣄⣠⣄⠞⠀
⠀⠀⠀⠀⠀⢸⣷⡦⢤⡤⢤⣞⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣤⣴⣿⣏⠁⠀⠀⠸⣏⢯⣷⣖⣦⡀⠀⠀⠀⠀⠀⠀
⢀⣾⣽⣿⣿⣿⣿⠛⢲⣶⣾⢉⡷⣿⣿⠵⣿⠀⠀⠀⠀⠀⠀
⣼⣿⠍⠉⣿⡭⠉⠙⢺⣇⣼⡏⠀⠀⠀⣄⢸⠀⠀⠀⠀⠀⠀
⣿⣿⣧⣀⣿.........⣀⣰⣏⣘⣆⣀⠀⠀
"""


def normalize(cmd: str) -> str:
    # Change many spaces with single
    norm_cmd = " ".join(cmd.split())
    return norm_cmd

def parse(norm_cmd: str, cmd_pattern) -> tuple:
    m = cmd_pattern.search(norm_cmd)
    if bool(m):
        return (norm_cmd[:m.end("cmd")].lower(), norm_cmd[m.end("cmd"):].lstrip())
    return ("", norm_cmd)

def re_pattern_from_cmd(handlers: dict):
    keys = list(handlers.keys())
    keys.sort(reverse=True)
    cmd_pattern = re.compile(r"^(?P<cmd>" + "|".join(keys) + r")\b(.*)$", re.IGNORECASE)
    return cmd_pattern


HANDLERS = {
      "hello": cmd_hello
    , "add": cmd_add
    , "change": cmd_change
    , "phone": cmd_phone
    , "show all": cmd_show_all
    , "good bye": cmd_good_bye
    , "close": cmd_good_bye
    , "exit": cmd_good_bye
    , "quit": cmd_good_bye
}

def input_error(func):
    def decor(cmd: str, cmd_data: str):
        try:
            result = func(cmd, cmd_data)
        except KeyError:
            return "unknown command"
        except ValueError as e:
            return e.args[0]
        except IndexError as e:
            return e.args[0]
        return result
    return decor

@input_error
def handler(cmd: str, cmd_data: str):
    return HANDLERS[cmd](cmd_data)

def main() -> None:
    load_phonebook()
    cmd_pattern = re_pattern_from_cmd(HANDLERS)
    print("Your ASSISTANT")
    print("Run me under Unix. I look terrible under Windows!")
    try:
        while True:
            cmd_raw = input("((̲̅ ̲̅(̲̅C̲̅o̲̅m̲̅m̲̅a̲̅n̲̲̅̅d̲̅( ̲̅((> ")
            if cmd_raw.find(".") != -1:
                break
            (cmd, cmd_data) = parse(normalize(cmd_raw), cmd_pattern)
            result_text = handler(cmd, cmd_data)
            if bool(result_text):
                print(result_text)
                if result_text.find("⣠⣶⡾") != -1:
                    break

    except KeyboardInterrupt:
        print("")
        return
    except EOFError:
        print("")
        return

if __name__ == "__main__":
    main()
