#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time as t

def controlTypes(*a_args, **a_kwargs):
    ''' Example:
    @controler_types(int, int)
    def fct(a, b): ...
    '''
    def decorator(fct):
        def controler(*args, **kwargs):
            if len(a_args) != len(args):
                raise TypeError("** function args different from args to check")

            for i, arg in enumerate(args):
                if a_args[i] is not type(args[i]):
                    raise TypeError("Bad type, Arg {0} not {1}".format(i, a_args[i]))
            
            for cle in kwargs:
                if cle not in a_kwargs:
                    raise TypeError("Type of arg {0} not in control list".format(repr(cle)))
                if a_kwargs[cle] is not type(kwargs[cle]):
                    raise TypeError("Bad type, Arg {0} not {1}".format(repr(cle), a_kwargs[cle]))
            return fct(*args, **kwargs)
        return control
    return decorator

#def singleton(defClass):
    #instances = {}
    #def get_instance():
        #if defClass not in instances:
            #instances[defClass] = defClass()
        #return instances[defClass]
    #return get_instance
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class should define at most one `__init__` function
    that takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        """
        Call method that raises an exception in order to prevent creation
        of multiple instances of the singleton. The `Instance` method should
        be used instead.

        """
        raise TypeError(
            'Singletons must be accessed through the `Instance` method.')


def limitPerf(limit):
    def decorator(fct):
        def timestamp(*args, **kwargs):
            start = t.time()
            result = fct(*args, **kwargs)
            elapse = t.time() - start
            if elapse > limit:
                print('! {0} took {1} to be executed'.format(fct.__name__, elapse))
            else:
                print('{0}@{1}: We\'re good'.format(fct.__name__, fct))
            return result, elapse
        return timestamp
    return decorator


def perf(fct):
    ''' Give a perf metric '''
    def metric(*args, **kwargs):
        start = t.time()
        result = fct(*args, **kwargs)
        elapse = t.time() - start
        print('{0} took {1} to be executed'.format(fct.__name__, elapse))
        return result, elapse
    return metric

def deprecated(fct):
    ''' raise an exception on decorated finctions '''
    def prevent(*args, **kwargs):
        raise RuntimeError('Function {0} deprecated, stopping.'.format(fct))
    return prevent
