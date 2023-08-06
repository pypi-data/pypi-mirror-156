# --------------------------------------------------------------------------- #
#   wsc-grempy-transport                                                      #
#   Copyright (c) 2022 the contributors                                       #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# --------------------------------------------------------------------------- #

from gremlin_python.driver.transport import AbstractBaseTransport
import websocket


class WebsocketClientTransport(AbstractBaseTransport):

    def __init__(self, **kwargs):
        self.ws = websocket.WebSocket(**kwargs)

    def connect(self, url, headers=None):
        headers = headers or []
        self.ws.connect(url, header=headers)

    def write(self, message):
        self.ws.send_binary(message)

    def read(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()

    @property
    def closed(self):
        return not self.ws.connected


def websocket_client_transport_factory(**kwargs):
    return WebsocketClientTransport(**kwargs)
