from datetime import datetime
from itertools import izip
from logbook import FileHandler

from neuronquant.utils.dates import dateToEpoch


def setup_logger(test, path='test.log'):
    test.log_handler = FileHandler(path)
    #test.log_handler = logbook.TestHandler()
    test.log_handler.push_application()


def teardown_logger(test):
    test.log_handler.pop_application()
    test.log_handler.close()


def check_dict(test, a, b, label):
    test.assertTrue(isinstance(a, dict))
    test.assertTrue(isinstance(b, dict))
    for key in a.keys():
        # ignore the extra fields used by dictshield
        if key in ['progress']:
            continue

        test.assertTrue(key in a, "missing key at: " + label + "." + key)
        test.assertTrue(key in b, "missing key at: " + label + "." + key)
        a_val = a[key]
        b_val = b[key]
        check(test, a_val, b_val, label + "." + key)


def check_datetime(test, a, b, label):
    test.assertTrue(isinstance(a, datetime))
    test.assertTrue(isinstance(b, datetime))
    test.assertEqual(dateToEpoch(a), dateToEpoch(b), "mismatched dates " + label)


def check(test, a, b, label=None):
    """
    Check equality for arbitrarily nested dicts and lists that terminate
    in types that allow direct comparisons (string, ints, floats, datetimes)
    """
    if not label:
        label = '<root>'
    if isinstance(a, dict):
        check_dict(test, a, b, label)
    elif isinstance(a, datetime):
        check_datetime(test, a, b, label)
    else:
        test.assertEqual(a, b, "mismatch on path: " + label)
