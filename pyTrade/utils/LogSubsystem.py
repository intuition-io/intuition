# Logger class (obviously...)
import logging

#TODO: reimplement fatal function with (colors ?) exit
'''---------------------------------------------------------------------------------------
Logger class
---------------------------------------------------------------------------------------'''
class LogSubsystem(object):
  ''' Trade logging version '''
  def __init__(self, name='default', lvl_str='debug', file_channel=False):
    if lvl_str == "debug":
      lvl = logging.DEBUG
    elif lvl_str == "info":
      lvl = logging.INFO
    else:
      print '[DEBUG] __LogSubSystem__ : Unsupported mode, setting default logger level: debug'
      lvl = logging.DEBUG
    if name == '':
      self.logger = logging.getLogger()
    else:
      self.logger = logging.getLogger(name)
    self.logger.setLevel(lvl)
    self.setup(lvl)

  def setup(self, lvl = logging.DEBUG):
    self.formatter = logging.Formatter('[%(levelname)s] %(name)s :  %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    ch.setFormatter(self.formatter)
    self.logger.addHandler(ch)

    print('[DEBUG] __LogSubSystem__ : Logging initialized.')

  def addFileHandler(self, lvl = logging.DEBUG, file_store = 'pyTrade.log'):
    fh = logging.FileHandler(file_store)
    fh.setLevel(lvl)
    fh.setFormatter(self.formatter)
    self.logger.addHandler(fh)
    print('[DEBUG] __LogSubSystem__ : Logging file handler initialized.')

  def getLog(self):
    return self.logger


'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
  logSys = LogSubSystem(__name__, "debug")
  #logSys.addFileHandler()
  log = logSys.getLog()

  # 'application' code
  log.debug('SQLite fork wrapper test')
'''
