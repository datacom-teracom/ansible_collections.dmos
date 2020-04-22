#
# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from ansible.module_utils.six import iteritems


def dict_has_key(dict, key):
    return True if key in dict else False


def get_command_list_from_curly_braces(output):
    ret = output.split("\n")

    cmds = []
    while(len(ret)):
        cmd = ""
        discart_command = True
        for i, word in enumerate(ret, 0):
            cmd += word
            if word == "":
                ret.pop(i)
                break

            if ";" in word:
                ret.pop(i)
                discart_command = False
                break

            if "}" in word:
                ret.pop(i)
                for j in range(i - 1, -1, -1):
                    if "{" in ret[j]:
                        ret.pop(j)
                        break
                break

        if not discart_command:
            cmd = cmd.replace("{", "").replace(";", "").replace("}", "")
            cmd = re.sub(' +', ' ', cmd)
            cmds.append(cmd)

    return cmds


def get_command_list_diff(configs, candidates=None):
    out = []
    if candidates:
        for candidate in candidates:
            command = re.sub(' +', ' ', candidate)

            its_no = False
            if command.split()[0] == "no":
                its_no = True
                command = command.replace("no ", "")

            contains = True
            for config in configs:
                contains = True
                for word in command.split():
                    if word not in config:
                        contains = False
                        break
                if contains:
                    break

            if contains:
                if its_no:
                    out.append("no " + command)
            else:
                if not its_no:
                    out.append(command)

    return out


def build_regex(pref, suf, last, tp):
    # builds regex of every common node
    ret = ".*/" + re.sub('_', '-', pref)
    if suf == 1:
        ret += "{(.*)}"
    elif last and tp != 'str':
        ret += ".*"

    return ret


def build_regex_dict_key(pref, suf, last):
    # builds regex of dict keys
    ret = ".*/" + pref
    if suf == 1 and last:
        # this breaks if the list id has a '{' character and it is the last thing on keypath. Feel free to improve on this
        ret += "{([^{]*)}$"
    elif suf == 1:
        ret += "{(.*)}"

    return ret


def build_replace(pref, suf, idx):
    # builds replace string
    ret = "###" + re.sub('-', '_', pref)
    if suf == 1:
        ret += "@@@\\{0}@@@".format(str(idx))

    return ret


def generate_search_replace(prefix, suffix, value, type_of_node):
    # generate search and replace regex
    search = replace = ""
    count = 0
    for i in range(len(prefix)):
        count += suffix[i]
        if type_of_node == "dict-key":
            search += build_regex_dict_key(prefix[i],
                                           suffix[i], i == len(prefix) - 1)
        elif type_of_node == "leaf":
            search += build_regex(prefix[i], suffix[i],
                                  i == len(prefix) - 1, value['type'])
        replace += build_replace(prefix[i], suffix[i], count)

    if type_of_node == "leaf":
        search += " (.*)"
        replace += "@@@\\" + str(sum(suffix) + 1)

    return (search, replace)


def parse_spec_to_regex(key, value, prefix, suffix, dict_keys):
    # parse argument spec to regex
    generated_regex = {}
    prefix.append(key)
    suffix.append(1 if key in dict_keys else 0)

    if key in dict_keys or value['type'] == 'dict' or value['type'] == 'list':
        # recursion only occurs when new
        for k, v in value['options'].items():
            generated_regex.update(parse_spec_to_regex(
                k, v, prefix, suffix, dict_keys))

        if key in dict_keys:
            search, replace = generate_search_replace(
                prefix, suffix, value, "dict-key")
            generated_regex[search] = replace
    else:
        search, replace = generate_search_replace(
            prefix, suffix, value, "leaf")
        generated_regex[search] = replace

    prefix.pop()
    suffix.pop()

    return generated_regex


def parse_current_config(switch_config, arg_spec, module, dict_keys):
    # pass current switch configuration, arg_spec dictionary, module name and dict_keys
    generated_regex = parse_spec_to_regex(
        module, arg_spec['config'], [], [], dict_keys)

    res = set()
    rows = switch_config.split("\n")
    for row in rows:
        for k, v in generated_regex.items():
            aux = re.sub(k, v, row)  # change switch keypaths
            if aux != row:
                # add only if search and replace worked
                res.add(aux)

    config = {}
    for replace in res:
        current = config
        raw_key_value = replace.split("###")
        for each in raw_key_value:
            if each != '':
                KEY = 0
                VALUE = 1
                key_value = each.split("@@@")
                if key_value[KEY] in dict_keys:
                    # should find and create new array member
                    found = False
                    name = key_value[KEY] if key_value[KEY] != module else 'config'
                    if name not in current:
                        # create if not present already
                        current[name] = []
                    for arr in current[name]:
                        # iterate through dicts in array and search to find current context
                        if arr[dict_keys[key_value[KEY]]] == key_value[VALUE]:
                            current = arr
                            found = True
                            break
                    if not found:
                        # there are no dicts with this id, so create a new dict with only the id value
                        current[name].append(
                            {dict_keys[key_value[KEY]]: key_value[VALUE]})
                        current = current[name][-1]

                elif len(key_value) == 1:
                    # should just enter a new dict
                    name = key_value[KEY] if key_value[KEY] != module else 'config'
                    if name not in current:
                        # create if not present already
                        current[name] = {}
                    current = current[name]

                else:
                    # only assing value
                    current[key_value[KEY]] = key_value[1]

    return config
