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

from slave.protocol import Protocol
from slave.transport import Timeout
from message import Message


class CommunicationError(Exception):
    pass


class PFG600Protocol(Protocol):
    def __init__(self, address, logger):
        self.logger = logger
        self.address = address

    def _send_raw(self, transport, data):
        try:
            self.logger.debug('Sending message: %s', repr(data))
            transport.write(data)
        except slave.transport.Timeout:
            raise CommunicationError('Timeout while sending message %s' % repr(data))

    def _read_response(self, transport):
        try:
            resp = list(transport.read_bytes(5))
            self.logger.debug('Received message: %s', repr(resp))
            return resp
        except slave.transport.Timeout:
            raise CommunicationError('Timeout while receive response')

    def _parse_response(self, raw_response):
        return Message.parse(raw_response)

    def check_checksum(self, message):
        if message.compute_checksum() != message.get_checksum():
            raise CommunicationError('Received an invalid checksum')

    def _check_ack(self, message, check_ACK=False):
        function_code = message.get_function()

        if function_code == 0x15:  # NAK
            raise CommunicationError('Received a NAK')

        if check_ACK == True and function_code != 0x06:  # ACK
            raise CommunicationError('Received NOT a ACK')

    def query(self, transport, message):
        if not isinstance(message, Message):
            raise TypeError("message must be of instance Message")

        message.set_waitingbit(1)
        message.set_checksum(message.compute_checksum())

        raw_data = message.get_raw()
        data = "".join(map(chr, raw_data))

        self._send_raw(transport, data)
        response = self._parse_response(self._read_response(transport))

        self.check_checksum(response)
        self._check_ack(response)

        return response

    def write(self, transport, message):

        if not isinstance(message, Message):
            raise TypeError("message must be of instance Message")

        message.set_waitingbit(0)
        message.set_checksum(message.compute_checksum())

        raw_data = message.get_raw()
        data = "".join(map(chr, raw_data))

        self._send_raw(transport, data)
        response = self._parse_response(self._read_response(transport))

        self.check_checksum(response)
        self._check_ack(response, True)

    def clear(self, transport):
        while True:
            try:
                transport.read_bytes(25)
            except Timeout:
                return True
