import numpy as np
import pandas as pd



def morans_i(xy:np.ndarray, z:np.ndarray, d:list[float])->np.ndarray:
    import scipy.spatial.distance
    distances = scipy.spatial.distance.cdist(xy, xy)
    z_bar = np.mean(z)
    _z = (z-z_bar).reshape(-1,1)
    s_z2 = np.sum(np.power(z-z_bar,2))
    N = z.shape[0]

    ret = dict()
    for _d in d:
        w = (distances < _d).astype(int)
        W = np.sum(w)

        I = (N/(W*s_z2)) * (_z.T@w@_z)
        ret[_d] = [I[0,0]]
    ret = pd.DataFrame.from_dict(ret, orient='index', columns=['morans_i'])
    ret.index.name = 'd'
    return ret
