import liblip as ll
import sys
import math
import random

# Trace function
def trace( str):
    print( '######')
    print( "## ", str)
    print( '######')
    
# test function, here just a product of sin(2x)sin(2y),...
def fun2( dat, dim):
    s = 1.0
    for j in range( dim): s *= math.sin( 2 * dat[j])
    return s

# generate data randomly
def generate_random_data( dim, npts):
    x, XData, YData = ll.init( dim, npts)
    for i in range( npts):
        for j in range( dim):
            x[j] = random.random() * 3.0
            XData[i * dim + j] = x[j]
        YData[i] = fun2( x, dim)
    return x, XData, YData

###
# Initial test
###
trace( 'initial test: start')
dim = 3
npts = 1500
lip_const = 10.0
K2 = 100
        
print( "-- test procedural start --")        
x, XData, YData = generate_random_data( dim, npts)


ll.STCSetLipschitz( lip_const)
ll.STCBuildLipInterpolant( dim, npts, XData, YData)
    
err2 = 0
err = 0
for k in range( K2):
    for j in range( dim): x[j] = random.random() * 3.0 # randomly choose a test point
    w = ll.STCValue( x)
    w1 = fun2( x, dim) # the true function
    w = abs( w - w1) # compute the error
    if( err < w): err = w
    err2 += w * w    
err2 = math.sqrt( err2 / K2) # average error RMSE
print( "Interpolation max error: ",err)
print( "Average error: ", err2)

trace( 'initial test: end')

###
# example of usage of SLipInt class
###
trace( 'example of usage of SLipInt class: start')

dim=4        # the dimension and size of the data set
npts=1000
LipConst=4
x, XData, YData = generate_random_data( dim, npts)

for j in range( dim): x[j]=random.random() * 3.0 # some random x
# calculate the value
w = ll.LipIntValue( dim,npts,x,XData, YData,LipConst,1)
sys.exit()
# estimate Lipschitz constant
ll.LipIntComputeLipschitz(dim,npts,XData, YData)
# uses the computed Lipschitz constant
w = ll.LipIntValue(dim,npts,x,XData, YData)
# the same using local Lipschitz constants
ll.LipIntComputeLocalLipschitz(dim,npts,XData, YData)
# calculate the value
w = ll.LipIntValueLocal(dim,npts,x,XData, YData)
    
trace( 'example of usage of SLipInt class: end')

###
# example of usage of SLipInt class for monotone interpolation
###
trace( 'example of usage of SLipInt class for monotone interpolation: start')
trace( 'example of usage of SLipInt class for monotone interpolation: end')

###
# example of usage of SLipInt class with extra bounds
###
trace( 'example of usage of SLipInt class with extra bounds: start')
trace( 'example of usage of SLipInt class with extra bounds: end')

###
# example of usage of STCInterpolant class
###
trace( 'example of usage of STCInterpolant class: start')
trace( 'example of usage of STCInterpolant class: end')

###
# example using procedural interface
###
trace( 'example using procedural interface: start')
trace( 'example using procedural interface: end')

###
# example for smoothing
###
trace( 'example for smoothing: start')
trace( 'example for smoothing: end')

###
# example of usage of STCInterpolant class and smoothened data
###
trace( 'example of usage of STCInterpolant class and smoothened data: start')
trace( 'example of usage of STCInterpolant class and smoothened data: end')


# Test wrapper for:
#    double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)
# ll.LipIntValueAuto(Dim, Ndata, x, Xd, y, Index)


# Test wrapper for:
#    double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
# ll.LipIntValueLocal(Dim, Ndata, x, Xd, y)


# Test wrapper for:
#    double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
# ll.LipIntValueLocalCons(Dim, Ndata, Cons, x, Xd, y)


# Test wrapper for:
#    double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntComputeLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntComputeLocalLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
# ll.LipIntComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)
# ll.LipIntComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
# ll.LipIntSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)


# Test wrapper for:
#    double	LipIntGetLipConst() 
# ll.LipIntGetLipConst()


# Test wrapper for:
#    void		LipIntGetScaling(double *S) 
# ll.LipIntGetScaling(S)


# Test wrapper for:
#    int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
# ll.LipIntComputeScaling(Dim, Ndata, XData, YData)


# Test wrapper for:
#    void	ConvertXData(int *Dim, int* npts,  double* XData)
# ll.ConvertXData(Dim, npts, XData)


# Test wrapper for:
#    void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)
# ll.ConvertXDataAUX(Dim, npts, XData, auxdata)


# Test wrapper for:
#    int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
# ll.LipIntVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, eps)


# Test wrapper for:
#    int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntInfValue(Dim, Ndata, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)
# ll.LipIntInfValueAuto(Dim, Ndata, x, Xd, y, Index)


# Test wrapper for:
#    double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index)
# ll.LipIntInfValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntInfValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntInfValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
# ll.LipIntInfValueLocal(Dim, Ndata, x, Xd, y)


# Test wrapper for:
#    double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
# ll.LipIntInfValueLocalCons(Dim, Ndata, Cons, x, Xd, y)


# Test wrapper for:
#    double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntInfValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntInfValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntInfComputeLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntInfComputeLocalLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
# ll.LipIntInfComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)
# ll.LipIntInfComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
# ll.LipIntInfSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)


# Test wrapper for:
#    double	LipIntInfGetLipConst() 
# ll.LipIntInfGetLipConst()


# Test wrapper for:
#    void	LipIntInfGetScaling(double *S) 
# ll.LipIntInfGetScaling(S)


# Test wrapper for:
#    int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
# ll.LipIntInfComputeScaling(Dim, Ndata, XData, YData)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)
# ll.LipIntInfVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, ep)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntInfVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntInfVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)
# ll.LipIntInfSmoothLipschitzSimp(Dim, npts, XData, YData, TData, LC)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)
# ll.LipIntInfSmoothLipschitzSimpW(Dim, npts, XData, YData, TData, LC, W)


# Test wrapper for:
#    int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantExplicit(Dim, Ndata, x, y)


# Test wrapper for:
#    int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantColumn(Dim, Ndata, x, y)


# Test wrapper for:
#    int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantExplicitColumn(Dim, Ndata, x, y)


# Test wrapper for:
#    double	STCValueExplicit( double* x )
# ll.STCValueExplicit(x)


# Test wrapper for:
#    void	STCFreeMemory()
# ll.STCFreeMemory()


print( "-- test procedural end --")