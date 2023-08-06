__version__ = "0.1.0"


from queue import Queue
from threading import Thread
from typing import Any, Callable

# Channel is an alias for Queue in the context of CSP.
Channel = Queue[Any]
# Function is a callable that takes two Channels and returns any value.
Function = Callable[[Any], Any]


class Runner:
    """
    Runner is a construct in CSP that handles the execution of a function and
    its inputs and outputs via Channels.
    """

    def __init__(
        self,
        in_channel: Channel,
        out_channel: Channel,
        fn: Function,
        num_procs: int,
    ):
        self.in_channel = in_channel
        self.out_channel = out_channel
        self.fn = fn
        self.num_procs = num_procs

    def start(self):
        """
        start creates threads for executing the functions outside the main
        thread.
        """

        def inner_func(in_channel: Channel, out_channel: Channel):
            """
            inner_func wraps the actual function for connecting in_channel and
            out_channel, as well as proper task handling.
            """
            while True:
                value = in_channel.get()
                # Just calling self.fn(*value) will have unexpected consequences
                # for strings. If you know how to fix this elegantly, please open
                # a pull request with suggestions. 😬
                if isinstance(value, (list, tuple, set)):
                    result = self.fn(*value)
                else:
                    result = self.fn(value)
                out_channel.put(result)
                in_channel.task_done()

        for _ in range(self.num_procs):
            thread = Thread(
                target=inner_func,
                args=(self.in_channel, self.out_channel),
                daemon=True,
            )
            thread.start()


class Monitor:
    """Monitor supervises the execution of Runners."""

    channels: list[Channel]
    num_procs: int
    runners: list[Runner]

    def __init__(self, num_procs: int):
        self.channels = []
        self.num_procs = num_procs
        self.runners = []

    @classmethod
    def from_functions(cls, functions: list[Function], num_procs: int) -> "Monitor":
        """
        from_functions creates a new Monitor instance from a list of functions
        """
        monitor = Monitor(num_procs=num_procs)
        for function in functions:
            monitor.register_function(function)
        return monitor

    def collect(self):
        """collect collects the result from the last output channel."""
        while (
            any(channel.unfinished_tasks > 0 for channel in self.channels[:-1])
            or not self.channels[-1].empty()
        ):
            yield self.channels[-1].get()

    def register_function(self, fn: Function):
        """
        register_function creates a new Runner and connects it with the output
        channel of the previous Runner, if present.
        """
        if self.channels:
            in_channel = self.channels[-1]
        else:
            in_channel = Channel()
            self.channels.append(in_channel)
        out_channel = Channel()
        self.channels.append(out_channel)

        runner = Runner(
            in_channel=in_channel,
            out_channel=out_channel,
            fn=fn,
            num_procs=self.num_procs,
        )
        self.runners.append(runner)

    def start(self):
        """start starts all registered Runners."""
        for runner in self.runners:
            runner.start()

    def submit(self, value: Any):
        """
        submit sends a new value to the first Runner registered with the
        Monitor.
        """
        self.channels[0].put(value)
