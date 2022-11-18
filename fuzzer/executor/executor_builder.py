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

import os
import configparser
import logging
logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

from .executor import WebGLExecutor

__browser_cap = {
    "chrome": DesiredCapabilities.CHROME,
    "firefox": DesiredCapabilities.FIREFOX,
    "edge": DesiredCapabilities.EDGE,
    "safari": DesiredCapabilities.SAFARI
}

__defined_cap_names = ["platform", "platformName", "platformVersion",
                       "browserName", "automationName",
                       "deviceName", "machine",
                       "udid", "chromedriverPort",
                       "mjpegServerPort", "systemPort",
                       "wdaLocalPort", "derivedDataPath",
                       "noReset"]

class ExecutorsConfig:

    def __init__(self, cfg_file):
        self.__cfg_file = cfg_file
        self.__cfg = None
        self.__root_cfg = None
        self.__test_page = None
        self.__command_executor = None
        self.__local_executor_cfgs = {}
        self.__remote_executor_cfgs = {}

        self.__parse()

    @property
    def root_cfg(self):
        return self.__root_cfg

    @property
    def cfg(self):
        return self.__cfg

    @property
    def test_page(self):
        return self.__test_page

    @property
    def command_executor(self):
        return self.__command_executor

    @property
    def local_executor_cfgs(self):
        return self.__local_executor_cfgs

    @property
    def remote_executor_cfgs(self):
        return self.__remote_executor_cfgs

    def __parse(self):
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read(self.__cfg_file)
        self.__cfg = cfg

        if "root_config" not in self.__cfg:
            return
        self.__root_cfg = self.__cfg["root_config"]

        if "test_page" in self.__root_cfg:
            self.__test_page = self.__root_cfg["test_page"]

        if "command_executor" in self.__root_cfg:
            self.__command_executor = self.__root_cfg["command_executor"]

        if "local_executors" in self.__root_cfg:
            les_str = self.__root_cfg["local_executors"]
            les = les_str.split(",")
            self.__populate_executor_configs_to_dict(les, self.__local_executor_cfgs)

        if "remote_executors" in self.__root_cfg:
            res_str = self.__root_cfg["remote_executors"]
            res = res_str.split(",")
            self.__populate_executor_configs_to_dict(res, self.__remote_executor_cfgs)

    def __populate_executor_configs_to_dict(self, names, d):
        for n in names:
            n = n.strip()
            sname = "config_" + n

            if sname in self.__cfg:
                d[n] = self.__cfg[sname]
            else:
                logger.warning("config for `%s` not found in `%s`",
                               n, self.__cfg_file)

def _get_default_cap_for_browser(browser):
    return __browser_cap.get(browser)

def _create_browser_cap(browser, e_cap, **kwargs):
    '''
    create a browser cap object with extended caps in `e_cap` (dict)
    '''

    cap = _get_default_cap_for_browser(browser)
    if cap == None:
        return None

    cap = cap.copy()
    cap.update(e_cap, **kwargs)

    return cap

def __handle_additional_options(browser_cfg):
    bname = browser_cfg["browserName"]
    if bname == "chrome":
        opts = webdriver.ChromeOptions()
    elif bname == "firefox":
        opts = webdriver.FirefoxOptions()
    else:
        return None

    if "option_binary_location" in browser_cfg:
        opts.binary_location = browser_cfg["option_binary_location"]


    if "option_args" in browser_cfg:
        args = browser_cfg["option_args"]
        args_x = args.split(",")
        for arg in args_x:
            arg = arg.strip()
            opts.add_argument(arg)

    return opts

def build_one_executor_from_cfg(executor_name,
                                browser_cfg,
                                executors_cfg,
                                remote=False):
    browser_name = browser_cfg["browserName"]
    options = None
    if browser_name == "chrome":
        options = __handle_additional_options(browser_cfg)

    kwargs = {}
    if "master" in browser_cfg:
        kwargs["master"] = browser_cfg["master"]

    caps = {}
    for cn in __defined_cap_names:
        if cn in browser_cfg:
            caps[cn] = browser_cfg[cn]

    if "browserName_cap" in browser_cfg:
        caps["browserName"] = browser_cfg["browserName_cap"]

    command_executor = None
    if "command_executor" in browser_cfg:
        command_executor = browser_cfg["command_executor"]
    else:
        command_executor = executors_cfg.command_executor


    return build_one_executor(executor_name,
                              executors_cfg.test_page,
                              browser_name,
                              remote=remote,
                              command_executor=command_executor,
                              desired_capabilities=caps,
                              options=options,
                              **kwargs)


def __build_executors_from_dict(executors_dict, executors_cfg, res, remote):
    for exe_name, browser_cfg in executors_dict.items():
        logger.debug("building executor: `%s`", exe_name)
        exe = build_one_executor_from_cfg(exe_name,
                                          browser_cfg,
                                          executors_cfg,
                                          remote=remote)
        if exe is None:
            logger.warning("executor `%s` not created", exe_name)
            continue
        res.append(exe)


def build_executors_from_config(config_file):

    ret = []
    execs_cfg = ExecutorsConfig(config_file)

    __build_executors_from_dict(execs_cfg.local_executor_cfgs,
                                execs_cfg,
                                ret,
                                False)
    __build_executors_from_dict(execs_cfg.remote_executor_cfgs,
                                execs_cfg,
                                ret,
                                remote=True)

    return ret

def get_default_executors():
    cur_dir = os.path.dirname(__file__)
    def_conf_file = os.path.join(cur_dir, "executors_def.ini")

    return build_executors_from_config(def_conf_file)

def build_one_executor(name, test_page_url, browser_name,
                       remote=False, command_executor=None,
                       platform=None, desired_capabilities = None, options=None,
                       **kwargs):
    '''
    Building one executor using various configs provided by arguments
    '''

    if command_executor == None and remote:
        return None

    e_cap = {}
    if platform is not None:
        e_cap = {"platform":platform}
    if desired_capabilities is not None:
        e_cap.update(desired_capabilities)

    cap = _create_browser_cap(browser_name, e_cap)

    return WebGLExecutor(name, test_page_url,
                         browser_name,
                         remote=remote,
                         command_executor=command_executor,
                         desired_capabilities=cap,
                         options=options,
                         **kwargs)
