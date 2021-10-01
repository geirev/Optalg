# -*- coding: utf-8 -*-


'''
## one_step_rate_v1
    size == 1:
        return a1
    size == 2:
        b2 ~ bn - 1 = b1

    input = [a1, a2, a3, a4, a5], Nw = 8 

    --
        -> ary = [b1, b2, b3, b4]
        -> ary1 = [c1, c2, c3]
            yc = average( ary1 )

        ->
            a6 = a5 * (b5)
            a7 = a6 * (b6)
            a8 = a7 * (b7)

            b5 = b4 * yc
            b6 = b5 * yc
            b7 = b6 * yc

    return a8
    --

'''
def get_value(fargv, Nw):
    fargv = [float("%.6f" % it) for it in fargv]
    length = len(fargv)

    if length == 1:
        print("adjustvalue: ", fargv, " -> ", fargv[0])
        return fargv[0]

    divary_b, divary_c = [], []
    if length == 2:
        divary_b = [fargv[1] / fargv[0] for i in range(Nw - 1)]
    else:
        divary_b = [fargv[i] / fargv[i - 1] for i in range(1, length)]
        divary_c = [divary_b[i] / divary_b[i - 1] for i in range(1, len(divary_b))]
        average = sum(divary_c) / len(divary_c)
        for i in range(1, Nw - length + 1):
            divary_b.append(divary_b[-1] * average)
    
    foo = fargv[-1]
    for i in range(length - 1, Nw - 1):
        foo = foo * divary_b[i]
    foo = float("%.6f" % foo)

    print("adjustvalue: ", fargv, " -> ", foo)
    return foo
