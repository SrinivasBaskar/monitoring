'''
Created on Jan 27, 2016
@author: souvik
'''

import logging
from logging.handlers import TimedRotatingFileHandler
from abc import ABCMeta
from AbstractMetrics import AbstractMetrics, AbstractMetricsFactory
import threading

class ThreadLocalMetrics(AbstractMetrics):
    ''' Number of files to retain in the log folder
    '''

    __threadLocal = threading.local()

    def __init__(self, logger):
        '''
        Constructor
        '''
        super(ThreadLocalMetrics, self).__init__()
        ThreadLocalMetrics.__threadLocal.metrics = self
        self.__logger = logger

    @staticmethod
    def get():
        return ThreadLocalMetrics.__threadLocal.metrics

    def _initialize_metrics(self):
        pass

    def _flush_metrics(self):
        ''' This just prints out the Metric object
        '''
        self.__logger.info(self.__str__())

    def __str(self):
        return super(self).__str__()

    def close(self):
        super(ThreadLocalMetrics, self).close()
        ThreadLocalMetrics.__threadLocal.__dict__.clear()



class Singleton(type):
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance

class ThreadLocalMetricsFactory(AbstractMetricsFactory):
    ''' Factory method to create Thread Local Metrics
    Example Usage:
    metricsFactory = ThreadLocalMetricsFactory("/tmp/service_log").with_marketplace_id("IDC1").with_program_name("CinderAPI")
    metrics =  metricsFactory.create_metrics();
    '''
    __metaclass__ = Singleton

    def __init__(self, service_log_path, propagate_to_application_logs = True):
        super(ThreadLocalMetricsFactory, self).__init__()
        # This is done so that metrics flowing in cinder do not break.  To be removed soon.
        service_log_path = service_log_path.replace("service_log", "service.log")
        self.__logger = self.create_timed_rotating_log(service_log_path, propagate_to_application_logs)
    '''
    This method creates a thread local metrics
    '''
    def create_metrics(self):
        metrics = ThreadLocalMetrics(self.__logger)
        self._add_metric_attributes(metrics)
        return metrics

    #The default path is given to ensure backward compatibility to cinder. To be removed soon.
    def create_timed_rotating_log(self, path = "/var/log/cinder/service.log", propagate_to_application_logs = True):
        ''' This method describes the logging type of service logs
        '''
        logger = logging.getLogger("service.log")
        logger.propagate = propagate_to_application_logs
        # Uncomment this after thorough validation in Production, that all metrics are in service
        # logs. This will remove the service logs from cinder API.

        handler = logging.handlers.WatchedFileHandler(path)

        # Cinder itself uses watched file handler. LogRotation is handled externally using logrotate.d

        logger.addHandler(handler)
        return logger
