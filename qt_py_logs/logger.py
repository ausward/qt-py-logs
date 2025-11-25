import paho.mqtt.publish as publish
import inspect
import json
import time # Added import for time module
import threading


class QTlogger:
    """ Singleton MQTT Logger for publishing log messages to the specified MQTT broker and topic. """
    _instance = None
    topic: str 
    broker: str 
    port: int 
    source: str 
  
    def __new__(cls, *args, **kwargs):
        """ Implement singleton pattern for QTlogger. """
         # __new__ can accept args/kwargs but typically doesn't process them for singletons
        if cls._instance is None:
            cls._instance = super(QTlogger, cls).__new__(cls)
            cls._instance._initialized = False # Initialize flag for the new instance
        return cls._instance
    
    def __init__(self, topic:str = None, broker:str = None, port:int = None, source:str = None):
        """ Initialize the QTlogger instance.
        args:
            topic (str): MQTT topic to publish logs to.
            broker (str): MQTT broker address.
            port (int): MQTT broker port.
            source (str): Source identifier for the logger.
        """
        if not self._initialized:
            self.topic = topic
            self.broker = broker
            self.port = port
            self.source = source
            self._initialized = True # Set flag after initialization

    def _log(self, message: str):
        """ Internal method to publish log messages to the MQTT broker."""
        publish.single(self.topic, payload=message, hostname=self.broker, port=self.port)


    def log(self, level: str, message: str, Extra: dict = None):
        """ Log a message with a given severity level.
        args:
            level (str): Severity level of the log (e.g., 'INFO', 'ERROR').
            message (str): The log message.
            Extra (dict, optional): Additional contextual information to include in the log.
        """
        caller_frame = inspect.stack()
        caller_function = str(caller_frame[1].frame)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        if Extra:
            json_message = {
                "from": self.source,
                "payload": message,
                "level": level,
                "timestamp": current_time, 
                "caller": caller_function,
                "extra": json.dumps(Extra)
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
    """ Setup the QTlogger singleton instance.
    args:
        topic (str): MQTT topic to publish logs to.
        broker (str): MQTT broker address.
        port (int): MQTT broker port.
        source (str): Source identifier for the logger.
    returns:
        QTlogger: Configured singleton logger instance.
    """
    logger = QTlogger(topic, broker, port, source) # Create instance without arguments
    return logger



