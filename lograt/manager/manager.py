# MIT License

# Copyright (c) 2021 Divine Darkey

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from functools import cached_property
from multiprocessing import Process
from threading import Thread


class Manager:
    """
    An API to manage all process or threads created and used by LogRat, whether
    in watchdog or the upcoming features of LogRat.
    """

    def __init__(self, workers: set[Process, Thread], log_handler) -> None:
        self.workers = list(workers)
        self.killed = list()
        self.log_handler = log_handler

    @cached_property
    def workers_count(self) -> int:
        """ Returns the number of workers. Note that this gets cached once and never updates.
        for number of workers alive, use get_active_count method """
        return len(self.workers)

    @staticmethod
    def is_process(worker) -> bool:
        """ Returns True if a worker is a process False if it is a thread. """
        return hasattr(worker, 'kill')

    def are_processes(self) -> bool:
        """ Checks whether items given are threads or processes. """
        for item in self.workers:
            if hasattr(item, 'kill'):
                return True
        return False

    def get_active_count(self) -> int:
        """ Returns number of active or alive workers """
        return len(self.workers)

    def get_active_workers(self) -> list[Process, Thread]:
        """ Returns a list of active workers """
        active_workers = [worker for worker in self.workers if worker.is_alive()]
        return active_workers

    def get_killed_count(self) -> int:
        """ Returns number of killed workers """
        return len(self.killed)

    def get_killed(self) -> list[Thread, Process]:
        """ Returns a list of killed workers"""
        return self.killed

    def kill_worker(self, worker_name) -> None or Process or Thread:
        """ Kills an observer or a worker.
        Returns the worker if there is a success else None """
        # if we find the worker we should probably kill it
        if worker := [worker for worker in self.workers if worker.name == worker_name][0]:
            worker.kill()  # kill worker
            self.killed.append(worker)
            self.workers.remove(worker)  # remove worker
            return worker
        else:
            return None
