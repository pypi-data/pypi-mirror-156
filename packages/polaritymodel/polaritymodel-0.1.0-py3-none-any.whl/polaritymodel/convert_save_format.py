"""
This script should open a data file in the legacy format and save it in a forward-compatible format
"""
from .plot import plotcore as pc
import pickle as pkl

def convert(fname):
    data, kwargs, fname = pc.load(fname)
    try:
        df, lig, kwargs = pc.build_df(data, kwargs)
        fname_new = fname.replace('data','data_converted')
        mdict = {'df':df, 'lig':lig, 'kwargs':kwargs}
        with open(fname_new, 'wb') as fobj:
            pkl.dump(mdict, fobj)
        return
    except ValueError:
        pass


if __name__ == '__main__':
    fname = input('file name? (default: most recent) ') or 'most recent'
    convert(fname)