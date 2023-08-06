# Python wrapper for:
#    double	LipIntValue(int *Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index):
"""xxx

Args:
    dim (int): The number of dimensions

Returns:
    y (float): Initialized data
"""
    trace( "double	LipIntValue(int *Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValue( pDim, pNdata, px, pXd, py, pLipconst, pIndex)
    return yy


# Test wrapper for:
#    double	LipIntValue(int *Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index)


