# MIT License
#
# Copyright (c) 2022 Anavereum Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import hashlib
from asyncio import AbstractEventLoop, get_running_loop, new_event_loop
from typing import Any
from aiohttp import WSCloseCode

from aiohttp.web import run_app, Application, Request, WebSocketResponse
from wirestack.app import App

def get_loop():
    try:
        return get_running_loop()
    except:
        return new_event_loop()

class AppManager:
    def __init__(
        self,
        app: App,
        service: str = 'wirestack',
        region: str = 'global',
        node_id: int | str = 0,
        mode: str = 'canary',
        locale: str = 'en-US',
        *,
        timeout: int = 45.0,
        client_max_size: int = 1024,
        debug: bool = False,
        loop: AbstractEventLoop | None = None
    ):
        self.app = app
        self.find_handlers()

        self._loop = loop or get_loop()
        self.client_max_size = client_max_size
        self.debug = debug
        self.service = service
        self.timeout = timeout
        self._authorize = None
        self.region = region
        self.node = node_id
        self.mode = mode
        self.on_connects = []
        self._on_connects = []
        self.locale = locale

    def find_handlers(self):
        dired = dir(self.app)

        for l in dired:
            if l.startswith('__') and l.endswith('__'):
                dired.remove(l)
            elif l.startswith('on_connect'):
                self.on_connects.append(getattr(self.app, l))
                self._on_connects.append(
                    self.service + '-' + hashlib.sha512(l.encode()).hexdigest() + '-calls'
                )

        if 'authorize' in dired:
            self.needs_authorization = True
            self.authorize = getattr(self.app, 'authorize')

        self._handlers = [
            getattr(self.app, attr) for attr in dired
        ]

    def to_json(self, obj: Any) -> str:
        if isinstance(obj, dict):
            obj['_trace'] = f'{self.service}-{self.mode}-{self.region}-{self.node}'
        try:
            import orjson
        except:
            import json

            return json.dumps(obj=obj)
        else:
            return orjson.dumps(obj=obj).decode()

    async def request_handler(self, request: Request):
        # TODO: Finish
        ws = WebSocketResponse(timeout=self.timeout)
        await ws.prepare(request=request)

        await ws.send_str(
            self.to_json({
                't': 'HELLO',
                'pl': {
                    'timeout': self.timeout,
                    'needs_authorization': self.needs_authorization
                },
                'lc': self.locale,
                'calls': self._on_connects
            })
        )

        try:
            await self.authorize(ws)
        except:
            await ws.close(
                code=WSCloseCode.GOING_AWAY,
                message='Invalid authorization'
            )

        for call in self.on_connects:
            await call(ws)

    def run(self, *args, **kwargs):
        """
        Runs the app using aiohttp's run_app.
        """
        self._app = Application(
            *args,
            **kwargs,
            client_max_size=self.client_max_size,
            loop=self.loop,
            debug=self.debug,
        )
        self._app.router.add_get('/', self.request_handler)
        run_app(self._app)
