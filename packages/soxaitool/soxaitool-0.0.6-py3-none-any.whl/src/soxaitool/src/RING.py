
# Extract hr in each epoch
import numpy as np
from scipy.signal import butter, filtfilt


def cal_hr(led1, led2, f_s):
    nyq = 0.5 * f_s
    low = 0.4 / nyq
    high = 4 / nyq
    b, a = butter(2, [low, high], btype='band')
    led1_filt = filtfilt(b, a, led1)
    led2_filt = filtfilt(b, a, led2)
    diff = np.array(led1_filt[1::]) - np.array(led1_filt[0:-1])
    diff_min = min(diff)
    diff_max = max(diff)
    diff_threshold = 0.6
    peak_index = []
    for k in range(1, len(diff) - 1):
        if diff[k] < diff_min * diff_threshold and diff[k] < diff[k - 1] and diff[k] < diff[k + 1]:
            peak_index.append(k)
    bpm = []
    pi = []
    if len(peak_index) < 3:
        return 0, 0, 0
    else:
        for k in range(1, len(peak_index)):
            bpm.append(60 * f_s / (peak_index[k] - peak_index[k - 1]))
            pi.append(1/f_s*(peak_index[k] - peak_index[k - 1]))
        if len(bpm) >= 2:
            bpm_diff = np.array(bpm[1::]) - np.array(bpm[0:-1])
            hrv = [abs(pi[k]-pi[k-1]) for k in range(1,len(pi))]
            if max(abs(bpm_diff)) < 15:
                return sum(bpm) / len(bpm), np.mean(hrv)*1000, (np.std(led1)/np.mean(led1))/(np.std(led2)/np.mean(led2))
            else:
                return 0, 0, 0
        else:
            return 0, 0, 0


def feature_from_ppg(data_ppg, window_interval=4.8, fs_ppg=25):
    ppg_time = data_ppg[0]
    ppg_led1 = data_ppg[1]
    ppg_led2 = data_ppg[2]
    keys_out = ['time', 'hr', 'hrv', 'r', 'dc']
    array_time=[]
    array_hr=[]
    array_hrv=[]
    array_spo2=[]
    array_dc = []
    window = {'t': [], 'led1': [], 'led2': []}
    for k in range(len(ppg_time)):
        window['t'].append(ppg_time[k])
        window['led1'].append(ppg_led1[k])
        window['led2'].append(ppg_led2[k])
        if len(window['t']) >= window_interval * fs_ppg:
            hr, hrv, spo2 = cal_hr(window['led1'], window['led2'], fs_ppg)
            array_time.append(window['t'][0])
            array_hr.append(hr)
            array_hrv.append(hrv)
            array_spo2.append(spo2)
            array_dc.append(window['led1'][0])
            window['t'] = []
            window['led1'] = []
            window['led2'] = []
    return [array_time, array_hr, array_hrv, array_spo2, array_dc], keys_out

def cal_zc(x, y, z, f_s=26):
    nyq = 0.5 * f_s
    low = 1 / nyq
    high = 4 / nyq
    th=0.01
    b, a = butter(2, [low, high], btype='band')
    x_filt = filtfilt(b, a, x)
    y_filt = filtfilt(b, a, y)
    z_filt = filtfilt(b, a, z)
    zc_x, zc_y, zc_z=0, 0, 0
    for k in range(0,len(x)-1):
        if (x_filt[k]-th)*(x_filt[k+1]-th)<0:
            zc_x+=1
        if (y_filt[k] - th) * (y_filt[k + 1] - th) < 0:
            zc_y += 1
        if (z_filt[k] - th) * (z_filt[k + 1] - th) < 0:
            zc_z += 1
    return max(zc_x,zc_y,zc_z)

def feature_from_xyz(data, fs_xyz=26, window_interval=160 / 26):
    xyz_time=data[0]
    x=data[1]
    y=data[2]
    z=data[3]
    array_time = []
    array_zc = []
    keys=['time', 'zc']
    window = {'t': [], 'x': [], 'y': [], 'z': []}
    for k in range(len(xyz_time)):
        window['t'].append(xyz_time[k])
        window['x'].append(x[k])
        window['y'].append(y[k])
        window['z'].append(z[k])
        if len(window['t']) >= window_interval * fs_xyz:
            zc = cal_zc(window['x'], window['y'], window['z'], fs_xyz)
            array_time.append(window['t'][0])
            array_zc.append(zc)
            # print(f"HR: {HR}, HRv: {HRv}")
            window['t'] = []
            window['x'] = []
            window['y'] = []
            window['z'] = []
    return [array_time, array_zc], keys

def average(array_input, window_interval=60):
    # array_input is a 2D list
    array_time = array_input[0]
    num_features = len(array_input) - 1
    len_feature = len(array_time)
    array_out = []
    [array_out.append([]) for i in range(1 + num_features)]

    window_t = []
    window_data = [0] * num_features
    t_start = array_time[0]
    k = 0
    while k < len_feature:
        t_start = array_time[k]
        t_current = array_time[k]
        j = k
        while (t_current - t_start).total_seconds() <= window_interval and j < len_feature:
            t_current = array_time[j]
            if array_input[1][j] > 0:
                window_t.append(array_time[j])
                for i in range(num_features):
                    window_data[i] += array_input[i + 1][j]
            j += 1
        # print(f"k to j: {k}->{j}")
        k = j

        if len(window_t) > 0:
            array_out[0].append(t_current)
            for i in range(num_features):
                array_out[i + 1].append(window_data[i] / len(window_t))
        else:
            array_out[0].append(t_current)
            for i in range(num_features):
                array_out[i + 1].append(0)
            # dic2['hrv'].append(sum(window['hrv']) / len(window['hrv']))
        window_t = []
        window_data = [0] * num_features
    return array_out


def accumulate(array_input, window_interval=60):
    # array_input is a 2D list
    array_time = array_input[0]
    num_features = len(array_input) - 1
    len_feature = len(array_time)
    array_out = []
    [array_out.append([]) for i in range(1 + num_features)]

    window_t = []
    window_data = [0] * num_features
    t_start = array_time[0]
    k = 0
    while k < len_feature:
        t_start = array_time[k]
        t_current = array_time[k]
        j = k
        while (t_current - t_start).total_seconds() <= window_interval and j < len_feature:
            t_current = array_time[j]
            window_t.append(array_time[j])
            for i in range(num_features):
                window_data[i] += array_input[i + 1][j]
            j += 1
        # print(f"k to j: {k}->{j}")
        k = j

        array_out[0].append(t_current)
        for i in range(num_features):
            array_out[i + 1].append(window_data[i])

        window_t = []
        window_data = [0] * num_features
    return array_out

def merge(array0_input, array0_keys, array1_input, array1_keys):
    # merge array1 to array0
    array0=array0_input.copy()
    array1=array1_input.copy()
    num_old_item = len(array0)
    num_new_item = len(array1) - 1
    array0_time = array0[0]
    array1_time = array1[0]
    array1_start_index = 0
    array1_end_index = len(array1_time)
    for j in range(num_new_item):
        array0.append([])

    for k in range(len(array0_time)):
        i_found = 0
        if (array1_time[array1_start_index] >= array0_time[k]):
            for j in range(num_new_item):
                array0[num_old_item + j].append(array1[j + 1][array1_start_index])
        else:
            for i in range(array1_start_index, array1_end_index - 1):
                if array1_time[i] <= array0_time[k] and array1_time[i + 1] >= array0_time[k]:
                    for j in range(num_new_item):
                        array0[num_old_item + j].append(array1[j + 1][i])
                    array1_start_index = i
                    i_found = 1
                    break
            if i_found == 0:
                for j in range(num_new_item):
                    array0[num_old_item + j].append(array1[j + 1][array1_end_index - 1])

    return array0, array0_keys + array1_keys[1::]
