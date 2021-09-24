from concurrent import futures

from ..events.lograt_event_handler import LogRatHandler

from .lograt_observer_api import LogRatObserverAPI


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
        self.handler = LogRatHandler() # initialize the handler

    @staticmethod
    def generate_name(path) -> str:
        """ Generates a name for path """
        name = path.strip('/').split('/')[-1] # take last dir name
        return name

    def generate_names(self, paths) -> str:
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
        observer_  = self.observer()
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
    
    def start_observer(self, observer_) -> None:
        """ Starts an observer. """
        observer_.start() # start observer
        try:
            while True:
                observer_.join(1)
        except KeyboardInterrupt:
            observer_.stop()
        observer_.join()
    
    def start_observers(self, observers_) -> None:
        """ Starts a list of observers all at once using threads. """
        with futures.ThreadPoolExecutor() as pool:
            pool.map(self.start_observer, observers_)
