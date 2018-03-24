import numpy as np
import re
import pandas as pd
from loren_frank_data_processing.core import logger

def multiunit_to_spykshrk(mu_times, ntrode_keys):
    '''converting Eric DeNovellis dataframe format to spykshrk format

    Parameters
    ----------
    mu_times : ntrodes list of dataframe multiunit marks
    ntrode_keys : tuples

    Returns
    -------
    allmu : multiindex dataframe of ntrode marks in spykshrk format

    '''
    allmu = []
    for introde, ntrode_key in enumerate(ntrode_keys):
        # format time multiindex
        try:
            ntrode = ntrode_key[-1]
            testmu = mu_times[ntrode-1].astype('int16')
        except AttributeError:
            logger.warning('Failed to load mu from: {0}'.format(
                ntrode_key))
            continue

        testmu['time'] = np.round(testmu.index.total_seconds(), decimals=5)
        testmu.drop_duplicates(subset='time', inplace=True)
        testmu['timestamp'] = testmu.time.apply(lambda row: (row*1e5)).astype('uint64') #in ns
        testmu.set_index(['time', 'timestamp'], inplace=True)
        num_channels = testmu.shape[1]
        channel_names = ['c{chan:02d}'.format(chan=chan) for chan in range(0,num_channels)]
        testmu.columns = channel_names
        ### re-label channels to c00, c01, c02 .. cn
        # testmu.rename(columns=lambda x: 'c%02d' % (int(re.findall(r'\d+',x)[0])-1), inplace=True)

        # join ntrode info
        testmu['day'] = ntrode_key[1]
        testmu['epoch'] = ntrode_key[2]
        testmu['elec_grp_id'] = ntrode_key[3]
        testmu.set_index(['day', 'epoch', 'elec_grp_id'], append=True, inplace=True)
        testmu = testmu.reorder_levels(['day', 'epoch', 'elec_grp_id', 'timestamp', 'time'])
        allmu.append(testmu)
    spyk_marks_df = pd.concat(allmu)
    any_duplicates = spyk_marks_df[spyk_marks_df.index.duplicated(keep='first')].size
    if any_duplicates > 0:
        logger.warning('duplicates removed: {0}'.format(any_duplicates))
        spyk_marks_df = spyk_marks_df[~spyk_marks_df.index.duplicated(keep='first')]
    return spyk_marks_df

def linear_position_to_spykshrk(position_df,ntrode_key):
    '''converting Eric DeNovellis dataframe format to spykshrk format

    Parameters
    ----------
    position_df : dataframe
    ntrode_keys : tuples

    Returns
    -------
    tetpos : multiindex dataframe

    '''
    testpos = position_df[['linear_distance', 'speed', 'labeled_segments']]
    testpos.columns= ['linpos_flat', 'linvel_flat', 'seg_idx']
    testpos['time'] = testpos.index.total_seconds()
    testpos['timestamp'] = testpos.time.apply(lambda row: (row*1e5)).astype('uint64')
    testpos['day'] = ntrode_key[1]
    testpos['epoch'] = ntrode_key[2]
    testpos.set_index(['day', 'epoch', 'timestamp', 'time'], append=False, inplace=True)
    testpos = testpos.reorder_levels(['day', 'epoch', 'timestamp', 'time'])
    return testpos

def ripples_to_spykshrk(ripple_times, day, epoch):
    '''converting Eric DeNovellis dataframe format to spykshrk format

    Parameters
    ----------
    ripple_times : dataframe
    day, epoch : int

    Returns
    -------
    tetpos : multiindex dataframe

    '''
    ripple_times['starttime'] = ripple_times['start_time'].dt.total_seconds()
    ripple_times['endtime'] = ripple_times['end_time'].dt.total_seconds()
    ripple_times['time'] = ripple_times['starttime']
    ripple_times['event'] = ripple_times.index
    ripple_times['day'] = day
    ripple_times['epoch'] = epoch
    ripple_times['maxthresh'] = 4
    ripple_times = ripple_times.set_index(
        ['day', 'epoch', 'event', 'time'])[['starttime', 'endtime', 'maxthresh']]

    return ripple_times
