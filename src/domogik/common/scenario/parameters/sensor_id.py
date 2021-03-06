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

@author: Maxence Dunnewind <maxence@dunnewind.net>
@copyright: (C) 2007-2009 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.common.scenario.parameters.abstract import AbstractParameter

class SensorIdParameter(AbstractParameter):
    """ This parameter  simply provides a text entry
    This is the simplest exemple for to see how you can extend Parameter
    """

    def __init__(self, log = None, trigger = None):
        AbstractParameter.__init__(self, log, trigger)
        self.set_type("string")
        self.add_expected_entry("sensor_id", "integer", "The sensor id to check")

    def evaluate(self):
        """ Return string, or none if no string entered yet
        """
        p = self.get_parameters()
        if "sensor_id" in p:
            return p["sensor_id"]
        else:
            return None


#Some basic tests
if __name__ == "__main__":
    import logging
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    t = SensorIdParameter(logging, None)
    print("Expected entries : {0}".format(t.get_expected_entries()))
    print("Evaluate should be None : {0}".format(t.evaluate()))
    print("==> Setting some value for entry 'sensor_id'")
    data = { "sensor_id" : "1" }
    t.fill(data)
    print("Evaluate should now return the sensor id : {0}".format(t.evaluate()))
