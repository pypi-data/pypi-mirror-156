import io
from typing import Type
import picologging
import logging
import pytest

def test_logger_attributes():
    logger = picologging.Logger('test')
    assert logger.name == 'test'
    assert logger.level == logging.NOTSET
    assert logger.parent == None
    assert logger.propagate == True
    assert logger.handlers == []
    assert logger.disabled == False
    assert logger.propagate == True

level_names = [
    "debug",
    "info",
    "warning",
    "error",
    "critical"
]

levels = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
    logging.NOTSET,
]

@pytest.mark.parametrize("level", levels)
def test_logging_custom_level(level):
    logger = picologging.Logger('test', level)
    assert logger.level == level


def test_set_level():
    logger = picologging.Logger('test')
    logger.setLevel(logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_get_effective_level():
    logger = picologging.Logger('test')
    parent = picologging.Logger('parent', logging.DEBUG)
    logger.parent = parent
    assert logger.getEffectiveLevel() == logging.DEBUG
    assert logger.level == logging.NOTSET
    logger.setLevel(logging.WARNING)
    assert logger.getEffectiveLevel() == logging.WARNING


def test_dodgy_parents():
    logger = picologging.Logger('test')
    parent = "potato"
    logger.parent = parent
    with pytest.raises(AttributeError):
        logger.getEffectiveLevel()


def test_add_filter():
    logger = picologging.Logger('test')
    filter = logging.Filter("filter1")
    logger.addFilter(filter)
    assert logger.filters == [filter]
    filter2 = logging.Filter("filter2")
    logger.addFilter(filter2)
    assert logger.filters == [filter, filter2]


def test_remove_filter():
    logger = picologging.Logger('test')
    filter = logging.Filter("filter1")
    logger.addFilter(filter)
    assert logger.filters == [filter]
    logger.removeFilter(filter)
    assert logger.filters == []


def test_no_filter():
    logger = picologging.Logger('test')
    record = picologging.LogRecord('test', logging.INFO, 'test', 1, 'test', (), {})
    assert logger.filter(record) == True


def test_filter_record():
    logger = picologging.Logger('test')
    filter = logging.Filter("hello")
    logger.addFilter(filter)
    record = picologging.LogRecord('hello', logging.INFO, 'test', 1, 'test', (), {})
    record2 = picologging.LogRecord('goodbye', logging.INFO, 'test', 1, 'test', (), {})
    assert logger.filter(record) == True
    assert logger.filter(record2) == False
    logger.removeFilter(filter)
    assert logger.filter(record) == True
    assert logger.filter(record2) == True


def test_filter_callable():
    logger = picologging.Logger('test')
    def filter(record):
        return record.name == 'hello'
    logger.addFilter(filter)
    record = picologging.LogRecord('hello', logging.INFO, 'test', 1, 'test', (), {})
    assert logger.filter(record) == True
    record = picologging.LogRecord('goodbye', logging.INFO, 'test', 1, 'test', (), {})
    assert logger.filter(record) == False


def test_log_debug():
    logger = picologging.Logger('test', logging.DEBUG)
    stream = io.StringIO()
    handler = picologging.StreamHandler(stream)
    handler.setFormatter(picologging.Formatter('%(message)s'))
    logger.addHandler(handler)
    assert logger.debug("Hello World") == None
    result = stream.getvalue()
    assert result == "Hello World\n"

def test_log_debug_info_level_logger():
    logger = picologging.Logger('test', logging.INFO)
    stream = io.StringIO()
    logger.handlers.append(picologging.StreamHandler(stream))
    assert logger.debug("Hello World") == None
    result = stream.getvalue()
    assert result == ""

def test_log_debug_info_level_logger_logging_handler():
    logger = picologging.Logger('test', logging.INFO)
    stream = io.StringIO()
    logger.handlers.append(logging.StreamHandler(stream))
    assert logger.debug("Hello World") == None
    result = stream.getvalue()
    assert result == ""

@pytest.mark.parametrize("level", levels)
def test_log_log(level):
    logger = picologging.Logger('test', level)
    stream = io.StringIO()
    handler = picologging.StreamHandler(stream)
    handler.setFormatter(picologging.Formatter('%(message)s'))
    logger.addHandler(handler)
    assert logger.log(level, "Hello World") == None
    result = stream.getvalue()
    assert result == "Hello World\n"


def test_logger_with_explicit_level(capsys):
    logger = picologging.Logger("test", logging.DEBUG)
    tmp = io.StringIO()
    handler = picologging.StreamHandler(tmp)
    handler.setLevel(logging.DEBUG)
    formatter = picologging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.handlers.append(handler)
    logger.debug("There has been a picologging issue")
    result = tmp.getvalue()
    assert result == "test - DEBUG - There has been a picologging issue\n"
    cap = capsys.readouterr()
    assert cap.out == ""
    assert cap.err == ""

def test_exception_capture():
    logger = picologging.getLogger(__name__)
    tmp = io.StringIO()
    handler = picologging.StreamHandler(tmp)
    logger.addHandler(handler)
    try:
        1/0
    except ZeroDivisionError:
        logger.exception("bork")
    result = tmp.getvalue()
    assert "bork" in result
    assert "ZeroDivisionError: division by zero" in result

def test_getlogger_no_args():
    logger = logging.getLogger()
    assert logger.name == "root"
    assert logger.level == logging.WARNING
    assert logger.parent is None

    picologger = picologging.getLogger()
    assert picologger.name == "root"
    assert picologger.level == logging.WARNING
    assert picologger.parent is None

def test_logger_init_bad_args():
    with pytest.raises(TypeError):
        logger = picologging.Logger("goo", 10, dog=1)
    
    with pytest.raises(TypeError):
        logger = picologging.Logger(name="test", level="potato")

def test_logger_repr():
    logger = picologging.Logger("goo", picologging.DEBUG)
    assert repr(logger) == "<Logger 'goo' (10)>"

def test_set_level_bad_type():
    logger = picologging.Logger("goo", picologging.DEBUG)
    with pytest.raises(TypeError):
        logger.setLevel("potato")

def test_add_remove_handlers():
    logger = picologging.Logger("goo", picologging.DEBUG)
    assert logger.handlers == []
    test_handler = picologging.Handler()
    logger.addHandler(test_handler)
    # add it twice should have no effect
    logger.addHandler(test_handler)
    assert len(logger.handlers) == 1
    assert test_handler in logger.handlers
    logger.removeHandler(test_handler)
    assert test_handler not in logger.handlers
    assert logger.handlers == []


@pytest.mark.parametrize("level_config", levels)
def test_log_and_handle(level_config):
    logger = picologging.Logger("test", level=level_config)
    assert not logger.info("gello")
    assert not logger.debug("hello")
    assert not logger.warning("hello")
    assert not logger.error("hello")
    assert not logger.fatal("hello")
    assert not logger.critical("hello")
    assert not logger.log(level_config, "hello")

def test_log_bad_arguments():
    logger = picologging.Logger("test")
    with pytest.raises(TypeError):
        logger.log("potato", "message")
    
    with pytest.raises(TypeError):
        logger.log()
