# -*- coding: utf-8 -*-
# Copyright 2020 Datacom (Teracom Telematica S/A) <datacom.com.br>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six import iteritems
from copy import deepcopy


class DictDiffer():
    _AUXILIARY_KEY = 'AUXILIARY_KEY'

    def __init__(self, base, comparable, config_keys=None):
        if isinstance(base, list) and isinstance(comparable, list):
            self._is_list = True
            self._base = deepcopy(self._add_aux_key(base))
            self._comparable = deepcopy(self._add_aux_key(comparable))
        elif isinstance(base, dict) and isinstance(comparable, dict):
            self._is_list = False
            self._base = deepcopy(base)
            self._comparable = deepcopy(comparable)
        else:
            raise AssertionError(
                "invalid or incompatible types of base and comparable")

        if config_keys is None:
            config_keys = {}
        self._config_keys = config_keys

    def _add_aux_key(self, raw_list):
        list_dict = dict()
        list_dict[self._AUXILIARY_KEY] = raw_list if raw_list is not None else []
        return list_dict

    def _del_aux_key(self, raw_dict):
        aux_key = raw_dict.get(self._AUXILIARY_KEY)
        return aux_key if aux_key is not None else []

    def _transform(self, config, level=0):
        if isinstance(config, list):
            if len(config) and not isinstance(config[0], dict):
                return config
            else:
                aux = {}
                for i in range(len(config)):
                    common_keys = set(
                        self._config_keys) & set(config[i])
                    for k in common_keys:
                        if level in self._config_keys[k]:
                            aux['id__{0}__{1}'.format(
                                k, config[i][k])] = config[i]
                config = aux
        if isinstance(config, dict):
            aux = config
            new_level = level + 1
            for sub_key in config:
                aux[sub_key] = self._transform(config[sub_key], new_level)
        return config

    def _dict_diff(self, base, comparable):
        if not isinstance(base, dict):
            raise AssertionError("`base` must be of type <dict>")
        if not isinstance(comparable, dict):
            raise AssertionError("`comparable` must be of type <dict>")

        updates = dict()

        for key, value in iteritems(base):
            if isinstance(value, dict):
                item = comparable.get(key)
                if item is not None:
                    sub_diff = self._dict_diff(value, comparable[key])
                    if sub_diff:
                        updates[key] = sub_diff
            elif isinstance(value, list):
                updates[key] = list(
                    set(comparable.get(key)) - set(base.get(key)))
            else:
                comparable_value = comparable.get(key)
                if comparable_value is not None:
                    if base[key] != comparable_value:
                        updates[key] = comparable_value

        for key in set(comparable.keys()).difference(base.keys()):
            updates[key] = comparable.get(key)

        return updates

    def _dict_intersect(self, base, comparable, erase=False):
        if not isinstance(base, dict):
            raise AssertionError("`base` must be of type <dict>")
        if not isinstance(comparable, dict):
            raise AssertionError("`comparable` must be of type <dict>")

        updates = dict()

        for key, value in iteritems(base):
            comparable_value = comparable.get(key)
            if comparable_value is None:
                continue
            if isinstance(value, dict):
                should_erase = erase
                if not comparable_value:
                    comparable_value = value
                    should_erase = True

                sub_intsec = self._dict_intersect(
                    value, comparable_value, should_erase)
                if sub_intsec:
                    splitted_key = next(iter(value)).split('__', 2)
                    if len(splitted_key) != 3:
                        sub_intsec['n_keys'] = 1 if erase else len(
                            comparable_value)
                    updates[key] = sub_intsec
            elif isinstance(value, list):
                if not len(comparable_value):
                    updates[key] = value
                    continue
                updates[key] = list(set(comparable_value)
                                    & set(base.get(key)))
            elif value is not None:
                updates[key] = value

        return updates

    def _untransform(self, config):
        if isinstance(config, dict):
            for key, value in iteritems(config):
                if isinstance(value, dict):
                    splitted_key = next(iter(value)).split('__', 2)
                    if len(splitted_key) == 3 and splitted_key[0] == 'id':
                        aux = []
                        for k, v in iteritems(value):
                            splitted_key = k.split('__', 2)
                            if len(splitted_key) == 3 and v.get(splitted_key[1]) is None:
                                v.update({splitted_key[1]: splitted_key[2]})
                            aux.append(v)
                        value = aux
                        config[key] = value
                        for i in range(len(value)):
                            self._untransform(value[i])
                    self._untransform(value)

    def _remove_null(self, cfg_dict):
        final_cfg = {}
        if not cfg_dict:
            return final_cfg

        for key, val in iteritems(cfg_dict):
            dct = None
            if isinstance(val, dict):
                child_val = self._remove_null(val)
                if child_val:
                    dct = {key: child_val}
            elif (isinstance(val, list) and val
                  and all([isinstance(x, dict) for x in val])):
                child_val = [self._remove_null(x) for x in val]
                if child_val:
                    dct = {key: child_val}
            elif val not in [None]:
                dct = {key: val}
            if dct:
                final_cfg.update(dct)
        return final_cfg

    def deepdiff(self):
        if not self._comparable:
            return {}
        if not self._base:
            return self._comparable
        self._base = self._transform(self._base)
        self._comparable = self._remove_null(self._comparable)
        self._comparable = self._transform(self._comparable)
        diff = self._dict_diff(self._base, self._comparable)
        self._untransform(diff)
        if self._is_list:
            return self._del_aux_key(diff)
        return diff

    def deepintersect(self):
        if not self._comparable and not self._base:
            return [] if self._is_list else {}
        self._base = self._transform(self._base)
        self._comparable = self._remove_null(self._comparable)
        self._comparable = self._transform(self._comparable)
        intsec = self._dict_intersect(self._base, self._comparable)
        self._untransform(intsec)
        if self._is_list:
            return self._del_aux_key(intsec)
        return intsec
