""" Python wrapper for liblip for multivariate scattered data interpolation. 

Simplifies the usage of liblip by handling all Numpy and CFFI calls
The Lipschitz interpolant possesses a number of desirable features, such
 as continuous dependence on the data, preservation of Lipschitz properties 
 and of the range of the data, uniform approximation and best error bounds. 
 On the practical side, construction and evaluation of the interpolant is 
 com- putationally stable. There is no accumulation of errors with the size 
 of the data set and dimension.
In addition to the Lipschitz constant, the user can provide information about 
other properties of f, such as monotonicity with respect to any subset of variables, 
upper and lower bounds (not necessarily constant bounds). If the data are given with errors, 
then it can be smoothened to satisfy the required properties. The Lipschitz constant, 
if unknown, can be estimated from the data using sample splitting and cross-validation techniques. 
The library also provides methods for approximation of locally Lipschitz functions.<br>

This file can also be imported as a module and contains the following
functions:
    * init - initializes package data
    * free - frees package data  
    * STCSetLipschitz
    * STCBuildLipInterpolant
    * STCValue
"""
import numpy as np
import random
import math
from  _liblip import ffi, lib as fm

###
# Helper functions
###

# global variable to support trace-info while testing
isTest = True

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

# Trace function
def trace( str):
    if isTest == True: print( "-- ", str, " --")
    
# use numpy to create an intc array with n zeros and cast to CFFI 
def create_intc_zeros_as_CFFI_int( n):
    x = np.zeros( n, np.intc)
    px = ffi.cast( "int *", x.ctypes.data)
    return x, px

# use numpy to create an float array with n zeros and cast to CFFI 
def create_float_zeros_as_CFFI_double( n):
    x = np.zeros( n, float)
    px = ffi.cast( "double *", x.ctypes.data)
    return x, px

def convert_py_float_to_cffi( x):
    if isinstance( x, np.ndarray) == True:
        px = x
    else:
        px = np.array( x)
        if px.dtype != "float64": px = px.astype( float)
    pxcffi = ffi.cast( "double *", px.ctypes.data)
    return px, pxcffi


def convert_py_int_to_cffi( x):
    x = np.intc( x)
    px = np.array( x)
    pxcffi = ffi.cast( "int *", px.ctypes.data)
    return px, pxcffi


###
# The python minimum wrapper 
###


def init( dim, npts, y =  None):
    """Initializes the package data

    Args:
        dim (int): The number of dimensions
        npts (int): The number of points per dimension
        y (target function: Function to initialize YData. (default is NaN)

    Returns:
        x, XData, YData (float arrays): Initialized data
    """
    trace( "py_init")        
    x = x = np.zeros( dim + 1, float)
    XData = np.zeros( dim * npts, float) 
    YData = np.zeros( npts, float)

    # generate data randomly
    for i in range( npts):
        for j in range( dim):
            x[j] = random.random() * 3.0
            XData[i * dim + j] = x[j]
        if y == y: YData[i] = y( x, dim) # initialise y if target function != NaN 

    return x, XData, YData

def free():
    """Frees the package data

    Args:
        no arguments
    Returns:
        0: no error 
    """
    return 0   

# Python wrapper for:
#    void STCSetLipschitz(double* x)
def STCSetLipschitz( lip_const):
    """Supplies the Lipschitz constant

    Args:
        lip_cost (float): Lipschitz constant

    Returns:
        no return value
    """
    trace( "void STCSetLipschitz(double* x)")
    plip_constnp, plip_const = convert_py_float_to_cffi( lip_const)
    fm.STCSetLipschitz( plip_const)    


# Python wrapper for:
#    int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolant( Dim, Ndata, x, y):
    """Builds Lipschitz interpolant using the simplicial distance for 
    subsequent fast evaluation. 

    Args:
    Dim (int): dimension of the data set 
    Ndata (int): the size of the data set
    x (float array): abscissae of the data, stored rowwise
    y (float array): values to be interpolated
    Returns:
        Lipschitz interpolant
    """
    trace( "int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)

    return fm.STCBuildLipInterpolant( pDim, pNdata, px, py)


# Python wrapper for:
#    double STCValue( double* x );
def STCValue( x):
    """Computes the value of the interpolant at any given point x, using fast method.
    Must be called after STCBuildLipInterpolant() procedure.

    Args:
        x (float array): point

    Returns:
        (foat): interpolant
    """
    trace( "double STCValue( double* x );")
    pxnp, px = convert_py_float_to_cffi( x)
    
    return fm.STCValue( px)



