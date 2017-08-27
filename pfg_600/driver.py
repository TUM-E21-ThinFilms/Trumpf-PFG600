# Copyright (C) 2016, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from protocol import PFG600Protocol
from message import SimpleMessage

class PFG600Driver(object):

    REGULATE_POWER = 1
    REGULATE_VOLTAGE = 2
    REGULATE_DELTAP = 3
    REGULATE_RFPEAK = 4

    ON = 1
    OFF = 0

    LIMIT_POWER = 1
    LIMIT_VOLTAGE = 2
    LIMIT_DELTAP = 3
    LIMIT_RFPEAK = 4

    def __init__(self, transport, protocol=None):

        if protocol is None:
            protocol = PFG600Protocol()

        self._transport = transport
        self._protocol = protocol

        self._target_power = 0x41
        self._target_voltage = 0x42
        self._regulate = 0x4D
        self._operatingmode = 0xCE # or 0x4E (also possible)
        self._operatingstatus = 0x4F
        self._actual_power = 0xD1
        self._actual_voltage = 0xD2
        self._actual_power_backward = 0xD4
        self._limit = 0x57
        self._error = 0xDA
        self._reset = 0x50

    def clear(self):
        self._protocol.clear(self._transport)

    def _query(self, msg):
        return self._protocol.query(self._transport, msg)

    def _write(self, msg):
        self._protocol.write(self._transport, msg)

    def get_target_power(self):
        return self._query(SimpleMessage(self._target_power)).get_data()

    def set_target_power(self, power):
        if power < 0 or power > 1000:
            raise ValueError("power must be in range [0, 1000] Watt")

        self._write(SimpleMessage(self._target_power, power))

    def set_target_voltage(self, voltage):
        if voltage < 0 or voltage > 1000:
            raise ValueError("voltage must be in range [0, 1000] voltage")

        self._write(SimpleMessage(self._target_voltage, voltage))

    def get_target_voltage(self):
        return self._query(SimpleMessage(self._target_voltage)).get_data()

    def get_errors(self):
        return self._query(SimpleMessage(self._error)).get_data()

    def get_regulate(self):
        return self._query(SimpleMessage(self._regulate)).get_data()

    def set_regulate(self, regulate):
        if not regulate in [self.REGULATE_DELTAP, self.REGULATE_POWER, self.REGULATE_RFPEAK, self.REGULATE_VOLTAGE]:
            raise ValueError("unknown regulation parameter")

        self._write(SimpleMessage(self._regulate, regulate))

    def get_operating_mode(self):
        return self._query(SimpleMessage(self._operatingmode)).get_data()

    def set_operating_status(self, status):
        if not status in [self.ON, self.OFF]:
            raise ValueError("unknown status parameter")

        self._write(SimpleMessage(self._operatingstatus, status))

    def get_operating_status(self):
        return self._query(SimpleMessage(self._operatingstatus)).get_data()

    def get_actual_power(self):
        return self._query(SimpleMessage(self._actual_power)).get_data()

    def get_actual_voltage(self):
        return self._query(SimpleMessage(self._actual_voltage)).get_data()

    def get_actual_power_backward(self):
        return self._query(SimpleMessage(self._actual_power_backward)).get_data()

    def get_limit(self):
        return self._query(SimpleMessage(self._limit)).get_data()

    def set_limit(self, limit):
        if not limit in [self.LIMIT_DELTAP, self.LIMIT_POWER, self.LIMIT_RFPEAK, self.LIMIT_VOLTAGE]:
            raise ValueError("unknown limit parameter given")

        self._write(SimpleMessage(self._limit, limit))

    def reset(self):
        self._write(SimpleMessage(self._reset))
