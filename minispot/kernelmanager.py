from functools import cached_property
from json import loads
from re import compile

from jupyter_client.session import Session
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager

from minispot import database


class KernelManager(AsyncMappingKernelManager):
    async def start_kernel(self, *args, **kwargs):
        kernels = self.list_kernels()
        if 0 < len(kernels):
            await self.shutdown_kernel(kernels[0]["id"])
        kernel_id = await super().start_kernel(*args, **kwargs)
        kernel = self.get_kernel(kernel_id)
        kernel._activity_stream.on_recv(_Callback(kernel))
        kernel._restart_count = 0
        return kernel_id

    async def restart_kernel(self, kernel_id, now=False):
        kernel = self.get_kernel(kernel_id)
        kernel._restart_count += 1
        return await super().restart_kernel(kernel_id, now)

    def new_kernel_id(self, **kwargs):
        n = database.get_session_id()
        return f"{n:08}-0000-0000-0000-000000000000"


class _Callback(object):
    def __init__(self, kernel):
        self._inputs = {}
        self._errors = {}
        self._kernel = kernel
        self._callback = kernel._activity_stream._recv_callback

    def __call__(self, lst):
        m = self.deserialize(lst)
        if m.ptype == "execute_request":
            if m.type == "execute_input":
                s = m.content["code"]
                n = m.content["execution_count"]
                self._inputs[m.pid] = s, n
            elif m.type == "error":
                t = m.content["traceback"]
                t = map(lambda x: _color.sub("", x), t)
                self._errors[m.pid] = "\n".join(t)
            elif m.type == "status":
                if m.content["execution_state"] == "idle":
                    k = int(self._kernel.kernel_id.split("-")[0])
                    r = self._kernel._restart_count
                    s, n = self._inputs.pop(m.pid)
                    e = self._errors.pop(m.pid, None)
                    database.put_history(k, r, n, s, e)
        self._callback(lst)

    def deserialize(self, lst):
        _, lst = self.session.feed_identities(lst)
        return _Message(self.session.deserialize(lst, False))

    @cached_property
    def session(self):
        return Session(
            config=self._kernel.session.config,
            key=self._kernel.session.key,
        )


class _Message(object):
    def __init__(self, data):
        self._data = data

    @cached_property
    def content(self):
        c = self._data.get("content")
        return loads(c) if c else None

    @cached_property
    def type(self):
        return self.head.get("msg_type")

    @cached_property
    def pid(self):
        return self.phead.get("msg_id")

    @cached_property
    def ptype(self):
        return self.phead.get("msg_type")

    @cached_property
    def head(self):
        return self._data.get("header", {})

    @cached_property
    def phead(self):
        return self._data.get("parent_header", {})


_color = compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
