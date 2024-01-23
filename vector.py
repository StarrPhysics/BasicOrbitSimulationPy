import numpy

class Vector(numpy.ndarray):
    """
    Redefines the `numpy.array` class to make it easier to work with.
    All properties are inherited, but default data type is changed to `float64`.
    """
    def __new__(cls, object):
        obj = numpy.asarray(object, dtype=numpy.float64).view(cls)
        return obj

xhat    = Vector([1,0])
yhat    = Vector([0,1])
zeroVec = Vector([0,0])