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

class Message(object):
    def __init__(self):
        self.address = 0 # one byte
        self.waiting_bit = 0 # one bit
        self.function_code = 0 # 7 bit
        self.datah = 0 # high data byte
        self.datal = 0 # low data byte
        self.chksum = 0 # one byte

    def set_address(self, addr):
        self.address = addr & 0xFF

    def get_address(self):
        return self.address

    def set_function(self, function_code):
        self.function_code = function_code & 0x7F # dismiss highest byte (its for waiting_bit)

    def get_function(self):
        return self.function_code

    def set_waitingbit(self, waiting):
        if not waiting in [0, 1]:
            raise ValueError("Waiting bit must be either 0 or 1")

        self.waiting_bit = waiting

    def get_waitingbit(self):
        return self.waiting_bit

    def get_full_function(self):
        return self.waiting_bit << 7 | self.function_code

    def set_full_function(self, function):
        self.set_waitingbit(function & 0x80)
        self.set_function(function)

    def set_data(self, data):
        self.datal = data & 0x00FF
        self.datah = data & 0xFF00

    def get_data(self):
        return self.datah << 8 || self.datal

    def compute_checksum(self):
        data = [self.address, self.get_full_function(), self.datah, self.datal]
        chksum = 0
        for byte in data:
            chksum = chksum ^ byte

        return chksum

    def set_checksum(self, chksum):
        self.chksum = chksum & 0xFF

    def get_checksum(self):
        return self.chksum

    def get_raw(self):
        return [self.address, self.get_full_function(), self.datah, self.datal, self.chksum]

    @staticmethod
    def parse(raw_data):
        if not isinstance(raw_data, list):
            raise TypeError("raw_data must be of type list")

        if len(raw_data) != 5:
            raise ValueError("raw_data must be exactly 5 bytes long")

        msg = Message()
        msg.set_address(raw_data[0])
        msg.set_full_function(raw_data[1])
        msg.set_data(raw_data[2] << 8 | raw_data[3])
        msg.set_checksum(raw_data[4])

        return msg

class SimpleMessage(Message):
    def __init__(self, functioncode, data=0):
        super(SimpleMessage, self).__init__()
        self.set_function(functioncode)
        self.set_data(data)