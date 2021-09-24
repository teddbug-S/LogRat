import json
from datetime import datetime
from functools import partial


class LogRatEventLogger:
    """
    LogRatEventLogger is a logger tailored to log filesystem changes especially.
    The default logger of the LogRatObserver class, provides logging in 
    the ff levels 'warn', 'error', 'critical', 'debug', 'info'.
    Writes logs to it's log_file attribute and makes analysis in the 
    analysis_file, the analysis file simply sorts the filesystem event type
    and adds the paths from which that specific event was triggered to it's list
    of non-duplicated paths for easier programmatic access to monitoring your
    directories. The make_analysis method can be overriden to suit the
    way you want your analysis to be made.


    Args:
        log_file: the file to log to
        analysis_file: a json file to make analysis to.
    """
    
    def __init__(self, log_file, analysis_file):
        self.log_file = log_file
        self.analysis_file = analysis_file
        for level in ['info', 'warn', 'critical', 'debug', 'error']:
            setattr(self, f'log_{level}', partial(self.write_log, level=level)) 
            # set log functions for each level 
    

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
        
    def make_analysis(self, event, initials=None) -> dict:
        """
        Makes analysis as an event is triggered.
        
        Args:
            event: the event tirggered
            initials: a list of initial paths that event type was holding in it's analysis
            file.
        
        Returns: A dictionary updating the event type's list of paths.
        """
        data = dict()
        if initials:
            new_paths = set(initials) # remove duplicates from initials
            new_paths.add(event.src_path) # add new path
            data[event.event_type] = list(new_paths) # convert back to list ans set
        else:
            data.setdefault(event.event_type, []).append(event.src_path)
        return data

    def write_analysis(self, event) -> None: 
        """ Writes analysed event triggers to aa json file categorized the paths
        using the event_type. """
        analysis = self.make_analysis(event) # get analysis from make_analysis
        try:
            with open(self.analysis_file) as analysis_file_r: # read initial data
                initial_data = json.load(analysis_file_r) 
                analysis = self.make_analysis(event, initials=initial_data.get(event.event_type, None))
                initial_data |= analysis # merge new analysis with initial data
        except (FileNotFoundError, json.JSONDecodeError):
            initial_data = analysis # set initial data to analysis if file not found
        finally:
            with open(self.analysis_file, 'w') as analysis_file_w:
                json.dump(initial_data, analysis_file_w, sort_keys=True, indent=4)
