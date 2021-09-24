from os.path import isdir

from watchdog.events import (EVENT_TYPE_CLOSED, EVENT_TYPE_CREATED,
                             EVENT_TYPE_DELETED, EVENT_TYPE_MODIFIED,
                             EVENT_TYPE_MOVED, FileSystemEventHandler)


class LogRatHandler(FileSystemEventHandler):
    """
    LogRatHandler, subclasses watchdog.events.FileSystemEventHandler
    to dispatch the name of the specific thread triggering the event
    so that we can identify each thread when monitoring multiple directories.
    """

    def __init__(self, log_file='logs/fsevents_analysis.json', analysis_file='logs/fsevents_log.log'):
        super().__init__()
        self.event_logger = LogRatEventLogger(log_file=log_file, analysis_file=analysis_file)

    def dispatch(self, event, name):
        """Dispatches events to the appropriate methods.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        self.on_any_event(event, name)
        {
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CLOSED: self.on_closed,
        }[event.event_type](event, name)
    
    def on_any_event(self, event, name):
        self.event_logger.write_analysis(event)
        # print(f'<WatchDog: {name}>')
    
    def on_closed(self, event, name):
        self.event_logger.log_warn(event, name)
    
    def on_created(self, event, name):
        self.event_logger.log_info(event, name)
    
    def on_deleted(self, event, name):
        self.event_logger.log_critical(event, name)
    
    def on_modified(self, event, name):
        if isdir(event.src_path): # avoid logging redundant modification of directories
            return
        self.event_logger.log_info(event, name)
    
    def on_moved(self, event, name):
        self.event_logger.log_file(event, name)
