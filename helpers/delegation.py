# -*- encoding: utf-8 -*-

# https://programmingideaswithjake.wordpress.com/2015/05/23/python-decorator-for-simplifying-delegate-pattern/

# http://python-dependency-injector.ets-labs.org/introduction/index.html
# https://www.martinfowler.com/articles/injection.html


class SimpleProperty :

    def __get__(self, instance, owner) :
        if instance is None :
            return self
        else :
            return instance.__value

    def __set__(self, instance, value) :
        instance.__value = value

class DelegatedAttribute : 

    def __init__(self, delegate_name, attr_name) :
        self.attr_name = attr_name
        self.delegate_name = delegate_name

    def __get__(self, instance, owner) :
        if instance is None:
            return self
        else:
            # return instance.delegate.attr
            return getattr(self.delegate(instance),  self.attr_name)

    def __set__(self, instance, value) :
        # instance.delegate.attr = value
        setattr(self.delegate(instance), self.attr_name, value)

    def __delete__(self, instance) :
        delattr(self.delegate(instance), self.attr_name)

    def delegate(self, instance) :
        return getattr(instance, self.delegate_name)

    def __str__(self) :
        return ""


def delegate_as(delegate_cls, to='delegate', include=frozenset(), ignore=frozenset()) :
    # turn include and ignore into sets, if they aren't already
    if not isinstance(include, set):
        include = set(include)
    if not isinstance(ignore, set):
        ignore = set(ignore)
    delegate_attrs = set(delegate_cls.__dict__.keys())
    attributes = include | delegate_attrs - ignore

    def inner(cls):
        # create property for storing the delegate
        setattr(cls, to, SimpleProperty())
        # don't bother adding attributes that the class already has
        attrs = attributes - set(cls.__dict__.keys())
        # set all the attributes
        for attr in attrs:
            setattr(cls, attr, DelegatedAttribute(to, attr))
        return cls
    return inner
