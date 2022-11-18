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
import sys
import concurrent.futures
import time
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


import logging

logger = logging.getLogger(__name__)

class WebGLExecutor(object):

    def __init__(self, name:str, test_page_url:str,
                 browser_name:str,
                 remote:bool=False,
                 command_executor:str=None,
                 desired_capabilities=None,
                 options=None,
                 **kwargs):
        self.name = name
        self.test_page_url = test_page_url
        self.browser_name = browser_name
        self.remote=remote
        self.command_executor=command_executor

        master:bool = kwargs.get("master")
        if master:
            self.master = True
        else:
            self.master = False

        if desired_capabilities != None:
            self.desired_capabilities = desired_capabilities
        else:
            self.desired_capabilities = {}

        if "loggingPrefs" not in self.desired_capabilities and master:
            self.desired_capabilities["goog:loggingPrefs"] = {'browser':'ALL'}

        d_kwargs = {}
        if options == None and browser_name == "firefox":
            ff_opts = webdriver.FirefoxOptions()
            ff_opts.set_preference("gfx.offscreencanvas.enabled", True)
            d_kwargs["service_log_path"] = os.path.devnull


            self.options = ff_opts
        else:
            self.options = options

        self.d_kwargs = d_kwargs
        self.webdriver_instance = None
        self.__new_browser(**self.d_kwargs)
        self.threaded_executor = concurrent.futures.ThreadPoolExecutor(1)

        self.enabled = True

    def _load_test_page(self):
        self.webdriver_instance.get(self.test_page_url)

    def refresh_test_page(self):
        try:
            self.webdriver_instance.refresh()
        except Exception as e:
            logger.debug("executor name: %s  ,exception: %s",
                         self.name, str(e))

            return False
        time.sleep(1)
        return True

    def __new_browser(self, **kwargs):
        if not self.remote:
            if self.browser_name == "firefox":
                self.webdriver_instance = webdriver.Firefox(executable_path=GeckoDriverManager().install(),
                                                            options=self.options, **kwargs)
            elif self.browser_name == "chrome":
                if "NOT_USE_WDM" in os.environ:
                    self.webdriver_instance = webdriver.Chrome(options=self.options, **kwargs)
                else:
                    self.webdriver_instance = webdriver.Chrome(ChromeDriverManager().install(),
                                                               options=self.options, **kwargs)
            elif self.browser_name == "edge":
                options = {}
                if "platform" in self.desired_capabilities and \
                   self.desired_capabilities["platform"] == "MAC":
                    cap = {}
                    cap["platformName"] = "mac os x"
                    options["capabilities"] = cap

                self.webdriver_instance = webdriver.Edge(EdgeChromiumDriverManager().install(),
                                                         **options)

            elif self.browser_name == "safari":
                self.webdriver_instance = webdriver.Safari(**kwargs)
            else:
                logger.fatal("browser type not supported %s", self.browser_name)
                sys.exit(-1)
        else:
            self.webdriver_instance = webdriver.Remote(command_executor=self.command_executor,
                                                       desired_capabilities=self.desired_capabilities,
                                                       options=self.options)

        self._load_test_page()


    def _quit(self):
        '''
        close the browser and delete the session (remote)
        '''
        logger.debug("'%s'  _quit called", self.name)
        if self.webdriver_instance != None:
            while True:
                try:
                    logger.debug("trying to kill browser")
                    self.webdriver_instance.quit()
                    self.webdriver_instance.stop_client()
                    self.webdriver_instance = None
                except:
                    break;

    def restart(self):
        cnt = 0
        succeeded = False
        while cnt < 5:
            try:
                self._quit()
                self.__new_browser(**self.d_kwargs)
                self.enabled = True
                return True
            except:
                continue

        self.enabled = False
        return False

    def execute(self, program):
        return self.threaded_executor.submit(self.__execute_webgl_program, program)

    def execute_direct(self, program):
        return self.__execute_webgl_program(program)

    def get_result(self, res, timeout=5):
        if res == None:
            return None, None

        r = None
        ex = None
        try:
            r = res.result(timeout=timeout)
        except Exception as e:
            ex = e
        finally:
            pass


        return ex, r

    def is_crash(self, ex, r):
        try:
            title = self.webdriver_instance.title
        except Exception as e:
            logger.debug("crash detected, failed to get the title of the test page")
            return True

        if ex == None and r == None:
            logger.debug("crash detected, both r and ex are None")
            return True

        if ex != None and hasattr(ex, "msg"):
            res = ex.msg.find("session deleted because of page crash") != -1
            if res:
                logger.debug("page crash detected in exception message")
            return res

        return False

    def get_execution_log(self):
        if self.webdriver_instance != None:
            return self.webdriver_instance.get_log("browser")
        return None

    def __execute_webgl_program(self, program):
        return self.webdriver_instance.execute_script("return run_a_test(arguments[0]);", program.to_json())

    def execute_script(self, script):
        return self.webdriver_instance.execute_script(script)

    def __del__(self):
        try:
            self._quit()
        except:
            pass


    def __str__(self):
        return "<Executor, name: " + self.name + ", browserName:" + \
            self.browser_name + ", remote:" + str(self.remote)  + \
            ", master: " + str(self.master) + " >"

    def __repr__(self):
        return self.__str__()
