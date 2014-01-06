# -*- coding: utf-8 -*-
# vim:fenc=utf-8


import os


DEFAULT_CONFIG = {'algorithm': {}, 'manager': {}}
MODULES_PATH = os.environ.get('MODULES_PATH', 'insights')

LOG_FORMAT = (u'{record.extra["ip"]} [{record.time:%m-%d %H:%M}]'
              '{record.level_name}::{record.channel} - {record.message}')

DEFAULT_LOG_DESTINATION = os.path.expanduser('~/.intuition/logs')
LOG_DESTINATION = DEFAULT_LOG_DESTINATION \
    if os.path.exists(DEFAULT_LOG_DESTINATION) else '/tmp'
DEFAULT_FILE_LOG = 'intuition.log'
