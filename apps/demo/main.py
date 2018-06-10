import pandas as pd
from spykshrk.franklab.pp_decoder.visualization import DecodeVisualizer
from spykshrk.franklab.data_containers import LinearPosition, FlatLinearPosition, SpikeObservation,\
 EncodeSettings, DecodeSettings, Posteriors, pos_col_format, RippleTimes, UnitTime
import holoviews as hv
from bokeh.plotting import curdoc
import numpy as np
import json
# hv.extension('bokeh', logo=False)

values = np.arange(1840, 1940, 10)

posteriors = pd.read_hdf('/opt/vortex2/data1_backup/demetris/JZ1/crap/testing.h5', 'posteriors')
linpos = pd.read_hdf('/opt/vortex2/data1_backup/demetris/JZ1/crap/testing.h5', 'linpos')
ripples = pd.read_hdf('/opt/vortex2/data1_backup/demetris/JZ1/crap/testing.h5', 'ripples').set_index(['day', 'epoch', 'event'], append=True)

config_file = '/home/droumis/Src/spykshrk_realtime/config/droumis_test.json'
config = json.load(open(config_file, 'r'))
encode_settings = EncodeSettings(config)
decode_settings = DecodeSettings(config)

posteriors = Posteriors.create_default(posteriors, enc_settings=encode_settings, dec_settings=decode_settings)
linpos = FlatLinearPosition.create_default(linpos, sampling_rate=1e5, arm_coord=encode_settings.arm_coordinates)
ripples = RippleTimes.create_default(ripples, time_unit=UnitTime)

ca1_viz = DecodeVisualizer(posteriors, linpos=linpos, enc_settings=encode_settings, riptimes=ripples)

stream = hv.streams.RangeXY()
ca1_dmap = ca1_viz.plot_all_dynamic(stream=stream, plt_range=10, slide=10, values=values)
doc = hv.renderer('bokeh').server_doc(ca1_dmap)

# curdoc().add_root(ca1_dmap)