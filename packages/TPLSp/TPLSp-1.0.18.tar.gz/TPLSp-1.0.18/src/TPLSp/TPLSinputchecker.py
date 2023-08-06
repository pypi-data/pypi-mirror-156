import numpy as np
import math

def TPLSinputchecker(datainput, name, dattype = None, maxval = None, minval = None, variation = 0, integercheck = 0):
    inputtype = type(datainput)
    assert (inputtype==int or inputtype==float or inputtype==np.ndarray), name + " should be numeric int or float" # numeric check
    assert (not np.isnan(datainput).any()), "NaN found in " + name # nan check
    assert (np.isfinite(datainput).all()), "Non finite value found in " + name # inf check

    if dattype is not None:
        if dattype == 'scalar':
            assert (inputtype==int or inputtype==float), name + " should be a scalar of type int or float"
        elif dattype == 'mat':
            assert(datainput.ndim == 2), name + " should have 2 dimensions as a matrix"
            n,v = datainput.shape
            assert (v > 2), name + " should have at least 3 columns"
            assert (n > 2), name + " should have at least 3 observations"
        elif dattype == 'colvec': # a column vector with 2 dimensions
            datainput = np.atleast_2d(datainput)
            n,v = datainput.shape
            assert (n == 1 or v == 1), name + " should be a vector" # it's okay if the input is a scalar which is a special case of column vector
            if v > 1 : # shouldn't be a row vector
                datainput = datainput.T
        elif dattype == 'rowvec': # a row vector with 1 dimensions
            if inputtype != int and inputtype != float:
                datainput = np.reshape(datainput,datainput.size)
        else:
            raise Exception("Unexpected input type checking requested")

    if maxval is not None:
        assert( np.all(datainput <= maxval) ), name + " should be less than or equal to " + maxval

    if minval is not None:
        assert( np.all(datainput >= minval) ), name + " should be greater than or equal to " + minval

    if variation == 1:
        assert( np.all(np.std(datainput)!=0) ), "There is no variation in " + name

    if integercheck == 1 and inputtype==float:
        assert(math.floor(datainput)==math.ceil(datainput)), name + " should be integer"
    elif integercheck == 1 and inputtype==np.ndarray:
        datainput = datainput.flatten()
        for i in range(datainput.size):
            assert(math.floor(datainput[i])==math.ceil(datainput[i])), name + " should be integer"

    return datainput