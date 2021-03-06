#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Tool to automaticly run a testdirectory

Implements
==========

- TestRunner

@author: Maikel Punie <maikel.punie@gmail.com>
@copyright: (C) 2007-2013 Domogik project
@license: GPL(v3)
@organization: Domogik
"""
from domogik.xpl.common.plugin import XplPlugin
from domogik import __version__ as DMG_VERSION
from domogik.common import logger
from domogik.common.utils import is_already_launched, STARTED_BY_MANAGER
from argparse import ArgumentParser
import os
import json
import traceback
import imp
import unittest
import sys
from subprocess import Popen, PIPE

LOW = "low"
MEDIUM = "medium"
HIGH = "high"

criticity_level = { LOW : 0, MEDIUM : 1, HIGH : 2 }

class TestRunner():
    """ Package installer class
    """
    def __init__(self):
        """ Init
        """
        l = logger.Logger("testrunner")
        l.set_format_mode("messageOnly")
        self.log = l.get_logger()

        parser = ArgumentParser(description="Launch all the tests that don't need hardware.")
	parser.add_argument("directory",
                          help="What directory to run")
        parser.add_argument("-a", 
                          "--allow-alter", 
                          dest="allow_alter",
                          action="store_true",
                          help="Launch the tests that can alter the configuration of the plugin or the setup (devices, ...)")
        parser.add_argument("-c", 
                          "--criticity", 
                          dest="criticity", 
                          help="Set the minimum level of criticity to use to filter the tests to execute. low/medium/high. Default is low.")
        self.options = parser.parse_args()
	self.testcases = {}
        self.results = {}

        # options
        self.log.info("Domogik release : {0}".format(DMG_VERSION))
        self.log.info("Running test with the folowing parameters:")
	if self.options.allow_alter:
	    self.log.info("- allow to alter the configuration or setup.")
	if self.options.criticity not in (LOW, MEDIUM, HIGH):
            self.options.criticity = LOW
	self.log.info("- criticity : {0}".format(self.options.criticity))

        # check tests folder
	self.log.info("- path {0}".format(self.options.directory))
        if not self.check_dir():
            return False

        # check and load the json file
        self.log.info("- json file {0}".format(self.json_file))
	if not self.load_json():
	    return False

        self._run_testcases()
        print self.results
        # TODO : return False is some tests fails
        return True

    def check_dir(self):
        self.path = None
	
	if self.options.directory == ".":
            self.path = os.path.dirname(os.path.realpath(__file__))
        elif self.options.directory.startswith('/'):
            self.path = self.options.directory
        else:
            self.path = "{0}/{1}".format(os.path.dirname(os.path.realpath(__file__)), self.options.directory)
	
        # check if self.path is a directory
	if not os.path.isdir(self.path):
	    self.log.error("Path {0} is not a directory".format(self.path))
	    return False

	# cehck if we have a json file
	self.json_file = "{0}/tests.json".format(self.path)
        if not os.path.isfile(self.json_file):
	    self.log.error("Path {0} has no tests.json file".format(self.path))
	    return False

	return True

    def load_json(self):
        try:
            self.json = json.loads(open(self.json_file).read())
	except:
            self.log.error("Error during json file reading: {0}".format(traceback.format_exc()))
            return False

        self.log.info("List of the tests (keep in mind that tests which need hardware will be skipped) :")
        for (test, config) in self.json.iteritems():
            to_run = True
            if config['need_hardware']:
                to_run = False
            if (not self.options.allow_alter) and config['alter_configuration_or_setup']:
                to_run = False
            if criticity_level[self.options.criticity] > criticity_level[config['criticity']]:
                to_run = False
            if to_run:
                indicator = "[ TO RUN  ]"
                self.testcases[test] = config
            else:
                indicator = "[ SKIPPED ]"
            self.log.info("{0} {1} : need hardware={2}, alter config or setup={3}, criticity={4}".format(indicator, test, config['need_hardware'], config['alter_configuration_or_setup'], config['criticity']))
        return True

    def _run_testcases(self):
        for (test, config) in self.testcases.items():
            # we add the STARTED_BY_MANAGER useless command to allow the plugin to ignore this command line when it checks if it is already laucnehd or not
            self.log.info("")
            self.log.info("Launching {0}".format(test))
            cmd = "{0} && cd {1} && python ./{2}.py".format(STARTED_BY_MANAGER, self.path, test)
            subp = Popen(cmd,
                         shell=True)
            pid = subp.pid
            subp.communicate()
            self.results[test] = { 'return_code' : subp.returncode }



def main():
    try:
        testr = TestRunner()
        if testr == False:
            sys.exit(1)
    except:
        sys.exit(2)

if __name__ == "__main__":
    main()
