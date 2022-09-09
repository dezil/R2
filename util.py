def scale(val, src, dst):
    return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]
