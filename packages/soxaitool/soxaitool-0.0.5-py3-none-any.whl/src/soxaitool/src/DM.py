from datetime import timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def score_model(features_final, key_final):
    daily_features_split_index = day_split(features_final[0])
    array_time = features_final[0]
    out=[]
    key_sleep=['total_sleep_time', 'REM_time', 'n1_time', 'n2_time', 'n3_time', 'sleep_score']
    key_act=['total_steps','total_calories', 'act_score']
    key_stress= ['stress_value', 'stress_score']
    for k in daily_features_split_index:
        s_index_start, s_index_end=k
        while s_index_start>0 and (array_time[s_index_start]+timedelta(hours=10)).date==array_time[k[0]]:
            s_index_start-=1
        while s_index_end<k[1] and (array_time[s_index_end]+timedelta(hours=10)).date==array_time[k[0]]:
            s_index_end+=1
        sleep_array = features_final[key_final.index('sleep')][s_index_start: s_index_end]
        sleep_info = [sleep_array.count(0), sleep_array.count(1), sleep_array.count(2), sleep_array.count(3)]
        total_sleep_time = sum(sleep_info)
        sleep_info.insert(0, total_sleep_time)
        sleep_score =100 if total_sleep_time>60*8 else 100*total_sleep_time/(60*8)
        sleep_info.append(sleep_score)

        stress_array=features_final[key_final.index('stress')][s_index_start: s_index_end]
        stress_score = sum(stress_array)
        stress_info = [sum(stress_array), stress_score]

        steps_array = features_final[key_final.index('steps')][s_index_start: s_index_end]
        act_array = features_final[key_final.index('actigraph')][s_index_start: s_index_end]
        total_steps = sum(steps_array)
        total_calories = sum(act_array)
        act_score = 100 if total_steps>10000 else total_steps/10000*100
        act_info = [total_steps, total_calories, act_score]

        out.append([array_time[k[0]], array_time[k[1]-1]]+ sleep_info + act_info + stress_info)
        print(f"\nday time: {array_time[k[0]]} to {array_time[k[1]-1]}" )
        print(f"sleep time: {array_time[s_index_start]} to {array_time[s_index_end-1]}")
        print(f"sleep info: {sleep_info}")
        print(f"act info: {act_info}")
    # print(out, key_sleep + key_act)
    return out, ['start_time','end_time']+ key_sleep + key_act + key_stress

        # sleep_info=[feature_sleep]
        # act_info=[]
        # sleep_day_split_index = day_split([k - timedelta(hours=10) for k in features_final[0]])


def day_split(array_time):
    out=[]
    start=0
    len_data = len(array_time)
    for i in range(1, len_data):
        if array_time[i-1].date() < array_time[i].date():
            out.append([start,i])
            start=i
    if len(out)==0:
        out.append([start, len_data])
    elif out[-1][1]!=len_data-1:
        out.append([start, len_data])
    return out


def get_daily_features(features_final, key_final):
    daily_features_split_index = day_split(features_final[0])
    return [[k1[k[0]:k[1]] for k1 in features_final] for k in daily_features_split_index], key_final



def process(features_ring, key_ring):
    wear = get_wear(features_ring[key_ring.index('T')])
    # print(f"features ring : size ({len(features_ring)}, {len(features_ring[0])}), {key_ring}")
    spo2 = get_Spo2(features_ring[key_ring.index('r')], features_ring[key_ring.index('dc')])
    hr_mean, hr_max, hr_min = smooth(features_ring[key_ring.index('hr')], wear, 5)
    hrv_mean, hrv_max, hrv_min = smooth(features_ring[key_ring.index('hrv')], wear, 5)
    spo2_mean, spo2_max, spo2_min = smooth(spo2, wear, 5)
    actigraph, sleep = get_acti(features_ring[key_ring.index('zc')])
    features_processed = [features_ring[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max,
                          spo2_min, sleep, actigraph,features_ring[key_ring.index('actI')], features_ring[key_ring.index('T')], wear]
    key_processed = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max',
                     'spo2_min', 'sleep', 'actigraph', 'actI', 'T', 'wear']
    # IO.save(features_processed, key_processed, "features_pre_processed")
    wake_sleep_features, sleep_trip_index = get_sleep(features_processed, key_processed)
    features_final = [features_processed[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max,
                      spo2_min, actigraph, wake_sleep_features, wake_sleep_features,  features_ring[key_ring.index('steps')], features_ring[key_ring.index('steps')], features_ring[key_ring.index('T')], wear]
    key_final = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max',
                 'spo2_min' ,'actigraph', 'sleep', 'stress', 'calorie', 'steps', 'T', 'wear']

    return features_final, key_final, sleep_trip_index

# this is for pre_process of the HR, HRv, SPO2, actIntensity, temperature
def smooth(array_input, wear, window_num, output_mean: bool = True, output_max: bool = True,
           output_min: bool = True):
    array_output_mean = []
    array_output_max = []
    array_output_min = []


    num_data = len(array_input)
    for k in range(window_num - 1, num_data):
        window_data = [array_input[i] if wear[i] else 0 for i in range(k - window_num + 1, k + 1)]
        num_none_zero = sum(i > 0 for i in window_data)
        if num_none_zero > 0 :
            if output_mean:
                array_output_mean.append(sum(window_data) / num_none_zero)
            if output_max:
                array_output_max.append(max(window_data))
            if output_min:
                array_output_min.append(min(window_data))
        else:
            if output_mean:
                array_output_mean.append(0)
            if output_max:
                array_output_max.append(0)
            if output_min:
                array_output_min.append(0)
    if num_data > window_num:
        if output_mean:
            array_output_mean = [array_output_mean[0]] * (window_num-1) + array_output_mean
        if output_max:
            array_output_max = [array_output_max[0]] * (window_num-1) + array_output_max
        if output_min:
            array_output_min = [array_output_min[0]] * (window_num-1) + array_output_min

    return array_output_mean, array_output_max, array_output_min


# this is for pre_process of ZC value, to get the sleep/wake classification
def get_acti(array_input):
    num_data = len(array_input)
    actigraph = []
    sleep_stage = []
    for k in range(4, num_data - 2):
        d_value = 0.00001 * (
                404 * array_input[k - 4] + 598 * array_input[k - 3] + 326 * array_input[k - 2] + 441 * array_input[
            k - 1] + 1408 * array_input[k] + 508 * array_input[k + 1] + 350 * array_input[k + 2])
        actigraph.append(d_value)
        sleep_stage.append(-1 if d_value > 1 else 0)
    first, last = sleep_stage[0], sleep_stage[-1]
    sleep_stage = [first] * 4 + sleep_stage
    sleep_stage += [last] * 2

    first, last = actigraph[0], actigraph[-1]
    actigraph = [first] * 4 + actigraph
    actigraph += [last] * 2
    return actigraph, sleep_stage




def spo2_r(r):
    SPO2 = -3.0 * r + 110
    if SPO2 > 100:
        SPO2 = 100
    return r

def get_Spo2(array_r, array_dc):
    return [spo2_r(k) for k in array_r]

def get_wear(array_T):
    return [1 if k>30 else 0 for k in array_T]


def sleep_trip_analysis(array_time, array_sleep, sleep_trip_index):
    out=[]
    for i, k in enumerate(sleep_trip_index):
        start_i=k[0]
        start_t=array_time[start_i]
        end_i=k[1]
        end_t=array_time[end_i]
        valid=k[2]
        sleep = array_sleep[start_i:end_i+1]
        total_time=end_i-start_i+1
        efficiency=valid/total_time
        wake_time=sleep.count(-1)
        wake_per=wake_time/total_time
        rem_time=sleep.count(0)
        rem_per=rem_time/total_time
        n1_time=sleep.count(1)
        n1_per=n1_time/total_time
        n2_time=sleep.count(2)
        n2_per=n2_time/total_time
        n3_time=sleep.count(3)
        n3_per=n3_time/total_time
        out.append([start_i, end_i, start_t, end_t, total_time, total_time-wake_time, rem_time, n1_time, n2_time, n3_time, efficiency,wake_per, rem_per, n1_per, n2_per, n3_per])
    keys=["start_index", "end_index", "start_datetime",  "end_datetime", "total_time(min)", "sleep_time(min)", "rem_time(min)", "n1_time(min)", "n2_time(min)", "n3_time(min)", "efficiency", "wake_per", "rem_per",
     "n1_per", "n2_per", "n3_per"]
    return out, keys

def print_sleep_info(array_time, wake_sleep_features, sleep_trip_index):
    for i, sleep_index in enumerate(sleep_trip_index):
        print(f"trip: {i}, from {array_time[sleep_index[0]]} to {array_time[sleep_index[1]]}")
        print(f"Efficiency: {sleep_index[2] / (sleep_index[1] - sleep_index[0] + 1)}")

def plot_sleep_info(array_time, wake_sleep_features, sleep_trip_index):
    sleep_total_time=0
    string=f'Sleep info: {array_time[0].strftime("%Y/%m/%d/, %H:%M:%S")} to {array_time[1].strftime("%Y/%m/%d/, %H:%M:%S")}'
    for i, sleep_index in enumerate(sleep_trip_index):
        string+=f'\n\ntrip: {i}, \ntime: {array_time[sleep_index[0]].strftime("%Y/%m/%d/, %H:%M:%S")} to {array_time[sleep_index[1]].strftime("%Y/%m/%d/, %H:%M:%S")}'
        string += f"\nSleep time: {(array_time[sleep_index[1]]-array_time[sleep_index[0]]).total_seconds() / 3600 :.0f} hours :{((array_time[sleep_index[1]]-array_time[sleep_index[0]]).total_seconds() % 3600)/60 :.0f} min"
        string+=f"\nEfficiency: {100 * sleep_index[2] / (sleep_index[1] - sleep_index[0] + 1):.2f} %"
        string+=f"\n"
    fig, ax = plt.subplots(1, 1, tight_layout=True)
    ax.set_title(string, loc='left')
    ax.set_axis_off()


def get_sleep(features_input, keys_input, latency=5, n_class=4):
    # features is a 2D array, features[0] is "sleep stage" feature
    wake_sleep_features = features_input[keys_input.index('sleep')]
    HR_features = features_input[keys_input.index('hr_mean')]
    HRv_features = features_input[keys_input.index('hrv_mean')]
    temperature_features = features_input[keys_input.index('T')]

    num_one_feature = len(features_input[0])
    sleep_trip_index = []
    sleep_features = []
    sleep_index = []
    state_start, state_last = False, False

    wake_count = [0, 0]  # wake_count[0] for sleep count, wake_count[1] for awake count
    wake_current, wake_last = 0, wake_sleep_features[0]
    for k in range(1, num_one_feature):
        wake_current = wake_sleep_features[k]
        if wake_current == 0:
            if wake_current == wake_last:
                wake_count[0] += 1
            else:
                wake_count = [0, 0]

        if wake_current == -1:
            if wake_current == wake_last:
                wake_count[1] += 1
            else:
                wake_count = [0, 0]

        wake_last = wake_current
        if wake_count[0] > latency:
            state_start = True
        elif wake_count[1] > latency:
            state_start = False

        if state_start:
            if not state_last:
                sleep_features += [[HR_features[i], HRv_features[i], temperature_features[i]] for i in
                                   range(k - latency, k)]
                sleep_index += (list(range(k - latency, k)))
            if wake_sleep_features[k] == 0:
                sleep_features.append([HR_features[k], HRv_features[k], temperature_features[k]])
                sleep_index.append(k)
        if (not state_start) and state_last:
            sleep_features = sleep_features[0:-latency]
            sleep_index = sleep_index[0:-latency]

            stages_classified = sleep_KMean(sleep_features, n_class)
            for n in range(len(stages_classified)):
                wake_sleep_features[sleep_index[n]] = stages_classified[n]
            sleep_trip_index.append([sleep_index[0], sleep_index[-1], len(sleep_index)])
            sleep_features = []
            sleep_index = []
        state_last = state_start
    if len(sleep_features) > n_class:
        stages_classified = sleep_KMean(sleep_features, n_class)
        for n in range(len(stages_classified)):
            wake_sleep_features[sleep_index[n]] = stages_classified[n]
        sleep_trip_index.append([sleep_index[0], sleep_index[-1], len(sleep_index)])
    return wake_sleep_features, sleep_trip_index


def sleep_KMean(sleep_features, n):
    clustering = KMeans(n_clusters=n, random_state=20)
    clustering.fit(sleep_features)
    y = clustering.predict(sleep_features)
    hrv_mean = [0] * n
    hrv_mean_n = [0] * n
    for k in range(len(y)):
        hrv_mean[y[k]] += sleep_features[k][1]
        hrv_mean_n[y[k]] += 1
    for i in range(n):
        hrv_mean[i] = hrv_mean[i] / hrv_mean_n[i] if hrv_mean_n[i] > 0 else 0
    label_class = sorted(enumerate(hrv_mean), key=lambda i: i[1], reverse=False)
    new_label = [k[0] for k in label_class]
    y_out = [new_label.index(k) for k in y]
    return y_out