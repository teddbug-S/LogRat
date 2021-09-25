# MIT License
#
# Copyright (c) 2021 Divine Darkey
#
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
#


from enum import Enum, unique
from concurrent import futures
from threading import Thread
from multiprocessing import Process

from ..events.lograt_event_handler import LogRatHandler

from .lograt_observer_api import LogRatObserverAPI


@unique
class StartMethods(Enum):
    THREAD = 1
    MULTIPROCESSES = 2


class LogRatObserver:
    """
    LogRatObserver interfaces the LogRatObserverAPI by adding the functionality
    of creating and scheduling an observer or a group of observers to monitor
    a path or a list of paths. Also takes care of the handler and logging
    of filesystem events, generates a unique name for each observer from the path it 
    monitors.
    """

    def __init__(self):
        self.observer = LogRatObserverAPI
        self.handler = LogRatHandler()  # initialize the handler

    @staticmethod
    def generate_name(path) -> str:
        """ Generates a name for path """
        name = path.strip('/').split('/')[-1]  # take last dir name
        return name

    def generate_names(self, paths) -> list[str]:
        """ Generates a list of unique names for each path."""
        names = list()
        for path in paths:
            name = self.generate_name(path)
            while name in names:
                name = self.generate_name(path.removesuffix(f"/{name}"))
            names.append(name)
        return names

    def create_observer(self, path, name=None) -> LogRatObserverAPI:
        """ Create an observer. """
        observer_ = self.observer()
        observer_.schedule(self.handler, path)
        if name:
            observer_.name = name
        else:
            observer_.name = self.generate_name(path)
        return observer_

    def create_observers(self, paths, names=None) -> set[LogRatObserverAPI]:
        """ Creates observers for specified paths and names to specified names """
        observers_ = set()
        if not names:
            names = self.generate_names(paths)
        for path, name in zip(paths, names):
            observer_ = self.create_observer(path, name)
            observers_.add(observer_)
        return observers_

    @staticmethod
    def start_observer(observer_) -> None:
        """ Starts an observer. """
        observer_.start()  # start observer
        try:
            while True:
                observer_.join(1)
        except KeyboardInterrupt:
            observer_.stop()
        observer_.join()

    def start_observers(self, observers_, start_method=StartMethods.THREAD) -> list[Thread, Process]:
        """ Starts a list of observers all at once using threads. """
        max_workers = len(observers_)
        observers_names = [observer.name for observer in observers_]
        if start_method == StartMethods.THREAD:
            with futures.ThreadPoolExecutor(max_workers=max_workers) as thread_pool:
                threads = thread_pool._threads  # get threads
                for thread, name in zip(threads, observers_names):
                    thread.name = name
                thread_pool.map(self.start_observer, observers_)
                return threads

        elif start_method == StartMethods.MULTIPROCESSES:
            with futures.ProcessPoolExecutor(max_workers=max_workers) as process_pool:
                processes = process_pool._processes  # get processes
                for process, name in zip(processes, observers_names):
                    process.name = name
                process_pool.map(self.start_observer, observers_)
                return processes
