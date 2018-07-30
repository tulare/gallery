# -*- encoding: utf-8 -*-

import abc

# --- INTERFACES -----------------------------------------------

class IObserver(metaclass=abc.ABCMeta) :

    @abc.abstractmethod
    def observe(self, *args, **kwargs) :
        pass

class IObservable(metaclass=abc.ABCMeta) :
    
    @abc.abstractmethod
    def addObserver(self, observer) :
        pass

    @abc.abstractmethod
    def removeObserver(self, observer) :
        pass

    @abc.abstractmethod
    def removeAllObservers(self) :
        pass

    @abc.abstractmethod
    def notify(self, *args, **kwargs) :
        pass

# --- IMPLEMENTATIONS -------------------------------------------

class Observable(IObservable) :

    def __init__(self) :
        self._observers = set()

    def addObserver(self, observer) :
        if not isinstance(observer, IObserver) :
            raise ValueError("{} : don't respect interface IObserver".format(observer))
        self._observers.add(observer)

    def removeObserver(self, observer) :
        self._observers.remove(observer)

    def removeAllObservers(self) :
        self._observers.clear()

    def notify(self, *args, **kwargs) :
        for observer in self._observers :
            observer.update(*args, **kwargs)
            
