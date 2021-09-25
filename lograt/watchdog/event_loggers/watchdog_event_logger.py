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


import json
import os
from datetime import datetime
from functools import partial


class WatchDogEventLogger:
    """
    WatchDogEventLogger is a logger tailored to log filesystem changes especially.
    The default logger of the LogRatObserver class, provides logging in 
    the ff levels 'warn', 'error', 'critical', 'debug', 'info'.
    Writes logs to it's log_file attribute and makes analysis in the 
    analysis_file, the analysis file simply sorts the filesystem event type
    and adds the paths from which that specific event was triggered to it's list
    of non-duplicated paths for easier programmatic access to monitoring your
    directories. The make_analysis method can be overridden to suit the
    way you want your analysis to be made.


    Args:
        log_file: the file to log to
        analysis_file: a json file to make analysis to.
    """

    def __init__(self, log_dir, log_file, analysis_file):
        try:
            os.mkdir(log_dir)
        except FileExistsError:
            ...
        finally:
            self.log_file = os.path.join(log_dir, log_file)  # join log directory with log file
            self.analysis_file = os.path.join(log_dir, analysis_file)
            self.log_dir = log_dir
            # set log functions for each level
            for level in ['info', 'warn', 'critical', 'debug', 'error']:
                setattr(self, f'log_{level}', partial(self.write_log, level=level))

    def config(self, **kwargs):
        """ Configures the logger. """
        for name, value in kwargs.items():
            if callable(getattr(self, name)):
                raise AttributeError("You cannot override a method.")
            setattr(self, name, value)

    def write_log(self, event, observer_name, level: str = 'info') -> None:
        """ Writes log message to the log_file with level `level`,
        the event object, and the name of the observer that triggered the event.
        """
        log_str = "[{level}]\t  {event_type:10} - {event_path:26} {time}\n".format_map({
            'level': level.upper(),
            'event_type': event.event_type,
            'event_path': event.src_path.removeprefix(event.src_path[:event.src_path.find(observer_name)]),
            'time': datetime.now().strftime('%d-%m-%Y %r')
        })
        try:
            with open(self.log_file, 'a') as log_file_a:
                log_file_a.write(log_str)
        except FileNotFoundError:
            with open(self.log_file, 'w') as log_file_w:
                log_file_w.write(log_str)

    @staticmethod
    def make_analysis(event, initials=None) -> dict:
        """
        Makes analysis as an event is triggered.
        Args:
            event: the event triggered
            initials: a list of initial paths that event type was holding in it's analysis
            file.
        Returns: A dictionary updating the event type's list of paths.
        """
        data = dict()
        if initials:
            new_paths = set(initials)  # remove duplicates from initials
            new_paths.add(event.src_path)  # add new path
            data[event.event_type] = list(new_paths)  # convert back to list ans set
        else:
            data.setdefault(event.event_type, []).append(event.src_path)
        return data

    def write_analysis(self, event) -> None:
        """ Writes analysed event triggers to aa json file categorized the paths
        using the event_type. """
        initial_data = self.make_analysis(event)  # get analysis from make_analysis
        try:
            with open(self.analysis_file) as analysis_file_r:  # read initial data
                initial_data = json.load(analysis_file_r)
                analysis = self.make_analysis(event, initials=initial_data.get(event.event_type, None))
                initial_data |= analysis  # merge new analysis with initial data
        except (FileNotFoundError, json.JSONDecodeError):
            ...
        finally:
            with open(self.analysis_file, 'w') as analysis_file_w:
                json.dump(initial_data, analysis_file_w, sort_keys=True, indent=4)
