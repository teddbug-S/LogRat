<<<<<<< HEAD
# LogRat

### A basic logging and file monitoring system built together.

Monitor filesystem changes in multiple paths and watch live logs, also have full control over
the threads or processes watching for changes. LogRat logs all changes to `fsevents_log.log`
file in a directory called logs in your current path by default, also in that directory
there is a file named `fsevents_analysis.json`. This file contains all the changed paths
grouped based on the type of event which occurred in json format, for easier access to 
these change logs in case you would like to know what changed and use that path in someway.

# Usage:
1. **Setting Up A LogRatObserver**
   1. You need to make an instance of `LogRatObsever` class, you can name the instance `observer_api` not to get you confused.
   2. Call the `create_observer` method of the instance and pass in the path you want to 
   monitor. Also, it takes an optional argument `name` which you can set if you want to give your observer a name.
   The default name is the last directory or file name in your path, finally is returns an observer object.
   3. Pass in the observer object you got from step ii. to the `start_observer` method of the observer class to start the observer.
   
**It's done, your observer is watching for changes.**

2. **Setting Up an Observer For Multiple Paths**
    1. Make an instance of `LogRatObserver` class, you can name it `observer_api`.
    2. Call it's `create_observers` method and pass in the list of paths you want to monitor,
       this returns a set of observers.
    3. Pass the observers to the `start_observers` method. Apart from the observers, it takes an 
       optional `start_method` argument which specifies the concurrency interface to use in starting the 
       observers. It can be any attribute of the `StartMethods` class. The default is `StartMethods.THREAD` which means using threads. Returns an iterable of
       the threads or processes.

**And again, your paths are being monitored.**

# Why LogRat?
LogRat seems to do what exactly the what `watchdog` but just added some few other touches
like taking care of multiple paths observing. LogRat is useful when you want to 
keep track of files third party programs create on your machine.
=======
# LogRat 
## A good monitor for changes in filesystems.
>>>>>>> e252378b209444afcc7237c322faf577181efe66
