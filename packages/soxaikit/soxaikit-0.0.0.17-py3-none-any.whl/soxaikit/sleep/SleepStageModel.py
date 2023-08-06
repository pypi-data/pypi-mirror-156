import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


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


def sleep_stage_cal(features_input, latency=5, n_class=4):
    # features is a 2D array, features[0] is "sleep stage" feature
    wake_sleep_features = features_input[10]
    HR_features = features_input[1]
    HRv_features = features_input[4]
    temperature_features = features_input[12]

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
            sleep_trip_index.append((sleep_index[0], sleep_index[-1], len(sleep_index)))
            sleep_features = []
            sleep_index = []
        state_last = state_start
    if len(sleep_features) > n_class:
        stages_classified = sleep_KMean(sleep_features, n_class)
        for n in range(len(stages_classified)):
            wake_sleep_features[sleep_index[n]] = stages_classified[n]
        sleep_trip_index.append((sleep_index[0], sleep_index[-1], len(sleep_index)))
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
