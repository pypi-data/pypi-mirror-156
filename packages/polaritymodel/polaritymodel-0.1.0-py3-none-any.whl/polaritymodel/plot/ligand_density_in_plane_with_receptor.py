import os
from .plotcore import load, build_df, select

import pandas as pd
import numpy as np
import plotly.express as px

def good_basis(normal_vector):
    nv = normal_vector/np.linalg.norm(normal_vector)
    v2 = np.cross(nv, np.random.rand(3))
    v2 /= np.linalg.norm(v2)
    v3 = np.cross(normal_vector, v2)
    v3 /= np.linalg.norm(v3)
    V = np.array([v2, v3]).T
    return nv, V

def plot(df, normal_vector, offset, width):
    nv, V = good_basis(normal_vector)
    X_all = df[['x1','x2','x3']].values
    normal_values = X_all @ nv
    mask_left = (normal_values > offset - width)
    mask_right = (normal_values < offset + width)
    X_slice = X_all[mask_left * mask_right]
    data2d = X_slice @ V
    fig = px.density_heatmap(pd.DataFrame(data2d), x=0, y=1, nbinsx=100, nbinsy=100)
    return fig
    

def save(fig, fname, T_plot):
    fig.write_html(os.path.join('animations', os.path.basename(fname)).replace('.pkl',f'_ligand_heatmap_t-{T_plot}.html'), include_plotlyjs='directory',
                   full_html=False)
    return

if __name__ == '__main__':
    fname = input('Enter data filename (default: most recent): ') or 'most recent' # 'data/test1.pkl'
    T_plot = int(input('timestep to plot (default: final time): ') or -1)
    vector_input = input('normal vector? (default = [1,0,0]) ') or '1,0,0'
    offset = float(input('offset? (default: 0) ') or 0)
    width = float(input('width? (default: 3)') or 3)
    normal_vector = np.array(eval(vector_input), dtype = 'float')
    data, kwargs, fname = load(fname)
    _, df_lig, kwargs = build_df(data, kwargs)
    df = select(df_lig, T_plot)
    fig = plot(df, normal_vector, offset, width)
    save(fig, fname, T_plot)
