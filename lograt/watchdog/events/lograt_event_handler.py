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


from os.path import isdir

from watchdog.events import (EVENT_TYPE_CLOSED, EVENT_TYPE_CREATED,
                             EVENT_TYPE_DELETED, EVENT_TYPE_MODIFIED,
                             EVENT_TYPE_MOVED, FileSystemEventHandler)

from ..event_loggers import WatchDogEventLogger


class LogRatHandler(FileSystemEventHandler):
    """
    LogRatHandler, subclasses watchdog.events.FileSystemEventHandler
    to dispatch the name of the specific thread triggering the event
    so that we can identify each thread when monitoring multiple directories.
    """

    def __init__(self, log_dir='logs', log_file='fsevents_analysis.log', analysis_file='fsevents_log.json'):
        super().__init__()
        self.event_logger = WatchDogEventLogger(log_dir=log_dir, log_file=log_file, analysis_file=analysis_file)

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
        print(f'<WatchDog: {name}>')

    def on_closed(self, event, name):
        self.event_logger.log_warn(event, name)

    def on_created(self, event, name):
        self.event_logger.log_info(event, name)

    def on_deleted(self, event, name):
        self.event_logger.log_warn(event, name)

    def on_modified(self, event, name):
        if isdir(event.src_path):  # avoid logging redundant modification of directories
            return
        self.event_logger.log_info(event, name)

    def on_moved(self, event, name):
        self.event_logger.log_file(event, name)
