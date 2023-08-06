"""
This file is to plot the density of ligand in the case that the ligand is modeled by a PDE instead of particles
"""
import os
from .plotcore import load, build_df
import plotly.express as px


def plot(L, axis, index):
    fig = px.imshow(L.take(index, axis), animation_frame=0)
    return fig


def save(fig, fname):
    fig.write_html(os.path.join('animations',os.path.basename(fname)).replace('.pkl', f'_ligand_density_pde.html'),
                   include_plotlyjs='directory',
                   full_html=False)
    return

if __name__ == '__main__':
    fname = input('Enter data filename (default: most recent): ') or 'most recent' # 'data/test1.pkl'
    data, kwargs, fname = load(fname)
    df, L, kwargs = build_df(data, kwargs)
    axis = int(input('axis along which to slice? default 1') or 1)
    index = int(input('which slice to take? (default: halfway) ') or L.shape[-1]/2)
    fig = plot(L, axis, index)
    save(fig, fname)
