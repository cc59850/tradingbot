import sys
sys.path.append("..")
import numpy as NP

def var(arr=None):
    result=NP.var(arr)
    return result

def mean(arr=None):
    result=NP.mean(arr,dtype=float)
    return result

def std_to_mean(arr=None):
    std=NP.std(arr)
    mean=NP.mean(arr,dtype=float)
    result=std/mean
    return result

def std(arr=None):
    return NP.std(arr)

