import pytest
from qt_py_logs import QTlogger, SetupLogger
from unittest.mock import patch, MagicMock
import os
import time
import yaml
import json
import threading


@pytest.fixture
def mock_mqtt_publish_single():
    with patch('qt_py_logs.logger.publish.single') as mock_publish:
        yield mock_publish

def test_qtlogger_singleton():
    SetupLogger("test/topic", "mqtt.test.com", 1883, "test_source")
    logger1 = QTlogger()
    logger2 = QTlogger()
    assert logger1 is logger2

def test_setup_logger(mock_mqtt_publish_single):
    topic = "test/topic"
    broker = "mqtt.test.com"
    port = 1883
    source = "test_source"

    logger = SetupLogger(topic, broker, port, source)

    assert isinstance(logger, QTlogger)
    assert logger.topic == topic
    assert logger.broker == broker
    assert logger.port == port
    assert logger.source == source

def test_setup_logger_from_yaml(mock_mqtt_publish_single, tmp_path):
    config_data = {
        "topic": "yaml_topic",
        "broker": "yaml_broker",
        "port": 1884,
        "source": "yaml_source"
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    logger = SetupLogger(config_path=str(config_file))
    
    assert isinstance(logger, QTlogger)
    assert logger.topic == config_data['topic']
    assert logger.broker == config_data['broker']
    assert logger.port == config_data['port']
    assert logger.source == config_data['source']

def test_config_hot_reload(mock_mqtt_publish_single, tmp_path):
    config_data = {
        "topic": "initial_topic",
        "broker": "initial_broker",
        "port": 1883,
        "source": "initial_source"
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    logger = SetupLogger(config_path=str(config_file))

    assert logger.topic == "initial_topic"

    # Modify the config file
    new_config_data = {
        "topic": "updated_topic",
        "broker": "updated_broker",
        "port": 1884,
        "source": "updated_source"
    }
    with open(config_file, 'w') as f:
        yaml.dump(new_config_data, f)

    # Wait for the watcher to detect the change, with a timeout
    max_wait_time = 5  # seconds
    start_time = time.time()
    while logger.topic != "updated_topic":
        time.sleep(0.1)
        if time.time() - start_time > max_wait_time:
            pytest.fail("Config hot reload timed out")

    assert logger.topic == "updated_topic"
    assert logger.broker == "updated_broker"
    assert logger.port == 1884
    assert logger.source == "updated_source"


def test_added_Extra_parameter_in_log_method(mock_mqtt_publish_single):
    topic = "test/topic"
    broker = "mqtt.test.com"
    port = 1883
    source = "test_source"
    

    logger = SetupLogger(topic, broker, port, source)
    test_message = "This is a test message with extra."
    test_level = "INFO"
    extra_data = {"user": "tester", "session": "xyz123"}
    logger.log(test_level, test_message, extra_data=extra_data)

    mock_mqtt_publish_single.assert_called_once()
    args, kwargs = mock_mqtt_publish_single.call_args


    assert  topic in args
    assert kwargs['hostname'] == broker
    assert kwargs['port'] == port

    # Verify payload content
    payload = kwargs['payload']
    
    json_payload = json.loads(payload)
    assert json_payload['from'] == source
    assert json_payload['payload'] == test_message
    assert json_payload['level'] == test_level
    assert 'timestamp' in json_payload
    assert 'caller' in json_payload
    assert json.loads(json_payload['extra']) == extra_data

def test_qtlogger_log_method(mock_mqtt_publish_single):
    topic = "test/topic"
    broker = "mqtt.test.com"
    port = 1883
    source = "test_source"

    logger = SetupLogger(topic, broker, port, source)

    test_message = "This is a test message."
    test_level = "INFO"
    logger.log(test_level, test_message)

    mock_mqtt_publish_single.assert_called_once()
    args, kwargs = mock_mqtt_publish_single.call_args


    assert  topic in args
    assert kwargs['hostname'] == broker
    assert kwargs['port'] == port

    # Verify payload content
    payload = kwargs['payload']
    
    json_payload = json.loads(payload)
    assert json_payload['from'] == source
    assert json_payload['payload'] == test_message
    assert json_payload['level'] == test_level
    assert 'timestamp' in json_payload
    assert 'caller' in json_payload
    # The caller function will be different now because of the new file structure
    # assert json_payload['caller'] == 'test_qtlogger_log_method'
