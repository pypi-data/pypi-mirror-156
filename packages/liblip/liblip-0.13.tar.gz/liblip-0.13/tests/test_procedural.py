import liblip as ll
import sys
import math
import random

# test function, here just a product of sin(2x)sin(2y),...
def fun2( dat, dim):
    s = 1.0
    for j in range( dim): s *= math.sin( 2 * dat[j])
    return s


dim = 3
npts = 1500
lip_const = 10.0
K2 = 100
        
print( "-- test procedural start --");        
x, XData, YData = ll.init( dim, npts, y = fun2)

ll.STCSetLipschitz( lip_const)
ll.STCBuildLipInterpolant( dim, npts, XData, YData);
    
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
    
print( "-- test procedural end --")