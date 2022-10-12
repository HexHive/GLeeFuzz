# ******************************************************
# * Copyright (C) 2022 the GLeeFuzz authors.
# * This file is part of GLeeFuzz.
# *
# * GLeeFuzz is free software: you can redistribute it
# * and/or modify it under the terms of the GNU General 
# * Public License as published by the Free Software 
# * Foundation, either version 3 of the License, or 
# * (at your option) any later version.
# *
# * GLeeFuzz is distributed in the hope that it will 
# * be useful, but WITHOUT ANY WARRANTY; without even
# * the implied warranty of MERCHANTABILITY or FITNESS
# * FOR A PARTICULAR PURPOSE. See the GNU General 
# * Public License for more details.
# *
# * You should have received a copy of the GNU 
# * General Public License along with GLeeFuzz. If not,
# * see <https://www.gnu.org/licenses/>.
# ******************************************************

from program.analysis.base_analyzer import BaseAnalyzer
from typing import Dict, List

import pickle
import os
import json

import logging
logger = logging.getLogger(__name__)

from .webgl_spec import WebGLSpec
from .webgl_spec import WebGLSpecJSONEncoder

from .api import WebGLArg, WebGLAPI
from .macro import WebGLMacro

WebGLSpecs:Dict[int, WebGLSpec] = {}

path = os.path.dirname(os.path.abspath(__file__))

def __config_listed_apis(spec, conf_val, list_val):
    for api_rep in conf_val.split(","):
        api_rep = api_rep.strip()

        try:
            api_id = int(api_rep)
            list_val.append(api_id)
        except:
            if api_rep not in spec.apis_map:
                continue

            for api in spec.apis_map[api_rep]:
                list_val.append(api.id)

def __config_spec(spec:WebGLSpec, cfg):
    conf_keys = ["disabled", "enabled"]

    for k in conf_keys:
        conf_val = cfg.get(k, None)

        if conf_val != None:
            __config_listed_apis(spec, conf_val, getattr(spec, k))

def __config_specs():
    import configparser
    specs_cfg = configparser.ConfigParser()
    specs_cfg.read(os.path.join(path, "specs_config.ini"))
    cfg_vals = ["v1", "v2"]
    m = {"v1":1, "v2":2}
    for v in cfg_vals:
        if v in specs_cfg:
            v_cfg = specs_cfg[v]
            __config_spec(WebGLSpecs[m[v]], v_cfg)

def __load_spec(version:int):
    with open(os.path.join(path, "spec_v" +  str(version) + ".pickle"), "rb") as f:
        WebGLSpecs[version] = pickle.load(f)

def __load_or_find_analyzer_object(fullpath:str,
                                   parse_map:Dict[str, BaseAnalyzer]):
    if fullpath in parse_map:
        return parse_map[fullpath]

    rdot = fullpath.rfind(".")
    assert rdot != -1
    analyzer_cls_name = fullpath[rdot + 1:]
    analyzer_mod_path = fullpath[:rdot]

    import importlib
    m = importlib.import_module(analyzer_mod_path)
    analyzer_cls = getattr(m, analyzer_cls_name, None)
    assert analyzer_cls != None

    analyzer = analyzer_cls()
    parse_map[fullpath] = analyzer
    return analyzer

def __setup_analyzers():
    '''
    read from the config file and load everything
    '''
    import configparser
    analyzer_cfg_file = os.path.join(path, 'api_analyzer_config.ini')
    analyzer_cfg = configparser.ConfigParser()
    analyzer_cfg.optionxform = str
    analyzer_cfg.read(analyzer_cfg_file)

    prefix = analyzer_cfg['config']['prefix']
    analyzer_map:Dict[str, BaseAnalyzer] = {}

    for api_name in analyzer_cfg['apis']:
        analyzers_path = analyzer_cfg['apis'][api_name]
        analyzers = []
        if isinstance(analyzers_path, str):
            analyzers_path = [analyzers_path]

        for a_path in analyzers_path:
            full_name = prefix + "." + a_path
            analyzer = __load_or_find_analyzer_object(full_name, analyzer_map)
            analyzers.append(analyzer)

        for gl in WebGLSpecs.values():
            for api in gl.apis_map[api_name]:
                for anal in analyzers:
                    api.add_analyzer(anal)

from ..mutation.mutators.enum_arg_mutator import enum_arg_mutator_match, EnumArgMutator
def __setup_enum_arg_mutators():
    '''
    for each API in each spec, if it contains a GLenum arg,
    add an `EnumARgMutator to its mutator list`
    '''
    for v, spec in WebGLSpecs.items():
        for api in spec.apis:
            has_enum_arg = False
            for arg in api.args:
                if arg.arg_type.name == "GLenum":
                    has_enum_arg = True
                    break

            if has_enum_arg:
                logger.debug("Adding EnumArgMuator to match_mutate_list " + \
                             " of `%s`, id=%d, version=%d",
                             api.name, api.id, v)
                api.mutate_dispatcher.match_mutate_list.append((enum_arg_mutator_match,
                                                                EnumArgMutator()))

import importlib
import inspect
import stringcase
from program.mutation.mutator_dispatcher import add_mutator_to_global_list
from program.mutation.mutator_dispatcher import setup_apidep_info
def __setup_mutators_from_modules(mutators_module):
    mutation_module = importlib.import_module(mutators_module)
    members = inspect.getmembers(mutation_module)

    for m_name, mm in members:
        if not inspect.ismodule(mm):
            continue

        if (not m_name.endswith("_mutator")) or \
           m_name == "enum_arg_mutator" or \
           m_name == "base_mutator":
            logger.debug("`%s` is a base mutator or a special mutator, skipping", m_name)
            continue

        try:
            api_names = getattr(mm, "_api_names")
            mutator_match_func = getattr(mm, m_name + "_match")
            mutator_cls = getattr(mm, stringcase.pascalcase(m_name))
        except:
            api_names = None
            mutator_match_func = None
            mutator_cls = None

        if api_names == None or mutator_match_func == None or mutator_cls == None:
            logger.error("%s does not contain all of _api_names, " + \
                         "match function and mutator cls, skipping", m_name)
            continue

        logger.debug("setting up mutators defined in '%s'", m_name)

        api_names = api_names.strip()
        if api_names == "*":
            logger.debug("adding `%s` to global_match_mutate_list", m_name)
            add_mutator_to_global_list(mutator_match_func, mutator_cls)
            continue

        api_names_lst = api_names.split(",")
        for ver, spec in WebGLSpecs.items():
            for api_name in api_names_lst:
                api_name = api_name.strip()

                if api_name not in spec.apis_map:
                    logger.error('%s is not defined spec %d, mutator: %s',
                                 api_name, ver, m_name)
                    continue

                for api in spec.apis_map[api_name]:
                    if api.mutate_dispatcher == None:
                        logger.warning("mutate_dispatcher for %s is None", api.name)
                        continue
                    logger.debug("adding `%s` to match_mutate_list of `%s`", m_name, api.name)
                    api.mutate_dispatcher.match_mutate_list.append((mutator_match_func,
                                                                    mutator_cls()))



if "__GEN_SPEC" not in os.environ:
    __load_spec(1)
    __load_spec(2)
    __config_specs()
    __setup_analyzers()


def get_apis_by_name(spec:WebGLSpec, name:str) -> List[WebGLAPI]:
    if name in spec.apis_map:
        return spec.apis_map[name]
    return None
