import threading

# heavily borrowed from: http://timka.org/tech/2008/12/17/singleton-in-python/

class SingletonType(type):
  def __new__(self, name, bases, namespace):
    namespace.setdefault('__lock__', threading.RLock())
    namespace.setdefault('__instance__', None)
    return super(SingletonType, self).__new__(self, name, bases, namespace)

  def __call__(self, *args, **kwargs):
    self.__lock__.acquire()
    try:
      if self.__instance__ is None:
        self.__instance__ = self.__new__(self, *args, **kwargs)
        self.__instance__.__init__(*args, **kwargs)
    finally:
      self.__lock__.release()
    return self.__instance__
