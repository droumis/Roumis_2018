
#%%
import pandas as pd
import numpy as np
import scipy as sp
import json
import os
import functools
from IPython.display import display
import math

import sys
sys.path.insert(0, '/home/droumis/Src/loren_frank_data_processing/')
import loren_frank_data_processing as lfdp
# import replay_classification as replay
import ripple_detection as ripple


# from spykshrk.util import AttrDict
from spykshrk.franklab.data_containers import RippleTimes
import spykshrk.franklab.filterframework_util as ff_util
# from spykshrk.realtime.simulator import nspike_data
from spykshrk.franklab.pp_decoder.util import gaussian, normal2D, apply_no_anim_boundary, simplify_pos_pandas, \
                                                normal_pdf_int_lookup
from spykshrk.franklab.pp_decoder.pp_clusterless import OfflinePPDecoder, OfflinePPEncoder
from spykshrk.franklab.data_containers import EncodeSettings, DecodeSettings, SpikeObservation, \
                                                         LinearPosition, StimLockout, Posteriors, \
                                                         FlatLinearPosition, SpikeWaves, SpikeFeatures, \
                                                         pos_col_format, DayEpochTimeSeries
from spykshrk.franklab.pp_decoder.visualization import DecodeVisualizer
from spykshrk.franklab.pp_decoder.decode_error import LinearDecodeError
import spykshrk
import dask
import dask.dataframe as dd
import dask.array as da
import dask.diagnostics as diag

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patches
import holoviews as hv
from holoviews.operation.datashader import aggregate, shade, datashade, dynspread, regrid
from holoviews.operation import decimate

# %matplotlib inline
# %reload_ext autoreload
# %autoreload 2
# %load_ext Cython
# %matplotlib inline
# hv.notebook_extension('bokeh', 'matplotlib')      
# mpl.rcParams.update({'font.size': 14})
# hv.Store.renderers['bokeh'].webgl = True

# pd.set_option('display.precision', 4)
# pd.set_option('display.max_rows', 10)
# pd.set_option('display.max_columns', 15)


#%%
idx = pd.IndexSlice

dask.set_options(get=dask.threaded.get)

animal_id = 'JZ1'
day, epoch = [4, 2]
ripple_area = 'ca1'
mu_areas = ['ca1', 'mec']
animals = {
    'JZ1': lfdp.Animal(short_name='JZ1', directory='/home/droumis/Src/Roumis_2018/Raw-Data/JZ1')}
date = 20161117
areas = ['ca1']
mark_variables = ['channel_1_max', 'channel_2_max', 'channel_3_max',
                  'channel_4_max']
epoch_index = ('JZ1', 4, 2)
ntrode_key = ('JZ1', 4, 2, 16)

mu_filenames = lfdp.multiunit.get_multiunit_filename(ntrode_key, animals)
assert(mu_filenames is not None)

ntrode_df = lfdp.make_tetrode_dataframe(animals)
ntrode_keys = ntrode_df.xs(epoch_index, drop_level=False).index.values
ca1_ntrode_keys_df = ntrode_df.xs(epoch_index, drop_level=False).query('area == "ca1"')
ca1_ntrode_keys = ca1_ntrode_keys_df.index.values
mec_ntrode_keys_df = ntrode_df.xs(epoch_index, drop_level=False).query('area == "mec"')
mec_ntrode_keys = mec_ntrode_keys_df.index.values

