"""
QTlogger: A singleton MQTT logger for publishing log messages. 
Allows configuration of MQTT broker, topic, and source identifier.
Supports logging messages with severity levels and additional context.

Meant to be used with QTlogs https://github.com/ausward/QTLogs
"""

import inspect
import json
import time # Added import for time module
import threading
from paho.mqtt import publish



class QTlogger:
    """ Singleton MQTT Logger for publishing log messages 
    to the specified MQTT broker and topic.
    """
    _instance = None
    topic: str
    broker: str
    port: int
    source: str

    def __new__(cls, *args, **kwargs):
        """ Implement singleton pattern for QTlogger. """
        if cls._instance is None:
            cls._instance = super(QTlogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, topic: str = None, broker: str = None, port: int = None, source: str = None):
        """
        Initialize or update the QTlogger's configuration.

        If configuration values are provided, the logger instance is updated.
        If no arguments are given, the existing configuration is maintained.

        Args:
            topic (str): MQTT topic to publish logs to.
            broker (str): MQTT broker address.
            port (int): MQTT broker port.
            source (str): Source identifier for the logger.
        """
        if topic is not None:
            self.topic = topic
            self.broker = broker
            self.port = port
            self.source = source

    def _log(self, message: str):
        """ Internal method to publish log messages to the MQTT broker."""
        # Check if logger is configured before attempting to publish
        if not all(hasattr(self, attr) for attr in ['topic', 'broker', 'port']):
            print("Error: Logger not configured. Please call SetupLogger first.")
            return
        publish.single(self.topic, payload=message, hostname=self.broker, port=self.port)

    def __print__(self):
        """ Print the current configuration of the logger. """
        if not all(hasattr(self, attr)
                for attr in ['topic', 'broker', 'port', 'source']):
            return "MQTT Logger is not configured."
        return f"MQTT Logger Configuration:\n\
        Topic: {self.topic}\n Broker: {self.broker}\n\
        Port: {self.port}\n Source: {self.source}"

    def log(self, level: str, message: str, extra_data: dict = None):
        """ Log a message with a given severity level.
        Args:
            level (str): Severity level of the log (e.g., 'INFO', 'ERROR').
            message (str): The log message.
            extra_data (dict, optional): Additional contextual information to include in the log.
        """
        caller_frame = inspect.stack()
        caller_function = str(caller_frame[1].frame)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if extra_data:
            json_message = {
                "from": self.source,
                "payload": message,
                "level": level,
                "timestamp": current_time,
                "caller": caller_function,
                "extra": json.dumps(extra_data)
            }
        else:
            json_message = {
                "from": self.source,
                "payload": message,
                "level": level,
                "timestamp": current_time,
                "caller": caller_function
            }
        threading.Thread(target=self._log, args=(json.dumps(json_message),)).start()


def SetupLogger(topic:str, broker:str, port:int, source:str) -> QTlogger:
    """
    Configure and retrieve the QTlogger singleton instance.

    This function can be called multiple times to re-configure the logger.

    Args:
        topic (str): MQTT topic to publish logs to.
        broker (str): MQTT broker address.
        port (int): MQTT broker port.
        source (str): Source identifier for the logger.

    Returns:
        QTlogger: The configured singleton logger instance.
    """
    logger = QTlogger(topic, broker, port, source)
    return logger
