# -*- coding: utf-8 -*-


'''
## one_step_rate 
    size == 1:
        return a1
    a1 is the root node
    input = [a1, a2, a3, a4, a5], Nw = 8

    --
    1. 
        -> ary = [b1, b2, b3, b4]
        -> yb = average( ary )
        -> 
            for (Nw - size)
                a6 = a5 * yb
                a7 = a6 * yb
                a8 = a7 * yb
    
    return a8
    --
'''
def get_value(fargv, Nw):
    fargv = [float("%.6f" % it) for it in fargv]
    length = len(fargv)
    if length == 1:
        print("adjustvalue: ", fargv, " -> ", fargv[0])
        return fargv[0]

    divary = [fargv[i] / fargv[i - 1] for i in range(1, length)]
    average = sum(divary) / len(divary)
    
    foo = fargv[-1] * (average ** (Nw - length))
    foo = float("%.6f" % foo)
    
    print("adjustvalue: ", fargv, " -> ", foo)
    return foo
