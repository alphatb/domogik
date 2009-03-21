#!/usr/bin/python
# -*- encoding:utf-8 -*-

# Copyright 2008 Domogik project

# This file is part of Domogik.
# Domogik is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Domogik is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Domogik.  If not, see <http://www.gnu.org/licenses/>.

# Author: Maxence Dunnewind <maxence@dunnewind.net>

# $LastChangedBy: maxence $
# $LastChangedDate: 2009-02-22 13:34:47 +0100 (dim 22 fév 2009) $
# $LastChangedRevision: 395 $

from domogik.xpl.lib.xplconnector import *
from domogik.common.configloader import *
import os
import sys


class SysManager(xPLModule):
    '''
    System management from domogik
    At the moment, can only start a module by receiving an xPL message
    '''

    def __init__(self):
        '''
        Init manager and start listeners
        '''
        self._components = {'x10' : 'x10Main()',
                        'datetime' : 'xPLDateTime()',
                        'onewire' : 'OneWireTemp()',
                        'trigger' : 'main()',
                        'dawndusk' : 'main()'}
        cfgloader = Loader('sysmanager')
        config = cfgloader.load()
        self._config = config[0]
        l = logger.Logger('sysmanager')
        self._log = l.get_logger()
        self.__myxpl = Manager(source = config[1]["source"], module_name = 'send')
        self._log.debug("Init system manager")
        Listener(self._sys_cb, self.__myxpl, {'schema':'domogik.system','type':'xpl-cmnd'})


    def _sys_cb(self, message):
        '''
        Internal callback for receiving system messages
        '''
        self._log.debug("Incoming message")
        print "Incoming message"
        cmd = message.get_key_value('command')
        mod = message.get_key_value('module')
        force = 0
        if message.has_key('force'):
            force = message.get_key_value('force')
        error = ""
        if mod not in self._components:
            error = "Invalide component.\n"
        elif not force and self._is_component_running(mod):
            self._log.info("The component seems already running and force is disabled")
            error += "The component seems already running and force is disabled"
        if error == "":
            if cmd == "start":
                pid = self._start_comp(mod)
                if pid:
                    self._write_pid_file(mod, pid)
                    self._log.debug("Component %s started with pid %i" %(mod, pid))
                    mess = Message()
                    mess.set_type('xpl-trig')
                    mess.set_schema('domogik.system')
                    mess.set_data_key('command',cmd)
                    mess.set_data_key('module',mod)
                    mess.set_data_key('force',force)
                    mess.set_data_key('error',error)
                    self.__myxpl.send(mess)
            elif cmd == "stop":
                ret = self._stop_comp(mod)
                if ret == 0:
                    error = ''
                elif ret == 1:
                    error = 'The component was not started (no pid file)'
                elif ret == 2:
                    error = 'An error occurs during sending signal, check logs'
                if not error:
                    self._log.debug("Component %s stopped" % (mod))
                else:
                    self._log.debug("Error during stop of component %s : %s" % (mod, error))
                mess = Message()
                mess.set_type('xpl-trig')
                mess.set_schema('domogik.system')
                mess.set_data_key('command',cmd)
                mess.set_data_key('module',mod)
                mess.set_data_key('force',force)
                mess.set_data_key('error',error)
                self.__myxpl.send(mess)
    
    def _stop_comp(self, name):
        '''
        Internal method
        Try to stop a component by getting its pid and sending signal
        @param name : the name of the component to stop
        @return 0 if stop is OK, 1 if the pid file doesn't exist, 2 in case of other problem
        '''
        if not os.path.isfile("%s/%s.pid" % (self._config['pid_dir_path'], name)):
            return 1
        else:
            try:
                f = open("%s/%s.pid"%  (self._config['pid_dir_path'], name),"r")
                data = f.readlines().replace('\n','')
            except:
                return 2

    def _start_comp(self,name):
        '''
        Internal method
        Fork the process then start the component
        @param name : the name of the component to start
        This method does *not* check if the component exists
        '''
        self._log.info("Start the component %s" % name)
        mod_path = "domogik.xpl.bin." + name
        __import__(mod_path)
        module = sys.modules[mod_path]
        lastpid = os.fork()
        if not lastpid:
            eval("module.%s" % self._components[name])
            self._log.debug("%s process started" % name)
            exit(0)
        return lastpid

    def _is_component_running(self, component):
        '''
        Check if one component is still running == the pid file exists
        '''
        return os.path.isfile('%s/%s.pid' % (self._config['pid_dir_path'], component))

    def _write_pid_file(self,component, pid):
        '''
        Write the pid in a file
        '''
        f = open("%s/%s.pid" % (self._config['pid_dir_path'], component), "w")
        f.write("%s"  % pid)
        f.close()

if __name__ == "__main__":
    s = SysManager()
