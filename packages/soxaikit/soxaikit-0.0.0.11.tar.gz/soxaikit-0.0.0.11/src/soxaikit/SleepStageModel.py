from sklearn.cluster import KMeans


def print_sleep_info(array_time, wake_sleep_features, sleep_trip_index):
    for i, sleep_index in enumerate(sleep_trip_index):
        print(f"trip: {i}, from {array_time[sleep_index[0]]} to {array_time[sleep_index[-1]]}")
        print(f" len_index: {len(sleep_index)}, len_feature: {len(wake_sleep_features)}")
        print(f"Efficiency: {len(sleep_index) / (sleep_index[-1] - sleep_index[0] + 1)}")


def sleep_stage_cal(array_time, features_input, latency, n):
    # features is a 2D array, features[0] is "sleep stage" feature
    wake_sleep_features = features_input[0]
    HR_features = features_input[1]
    HRv_features = features_input[2]
    temperature_features = features_input[3]

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

            stages_classified = sleep_KMean(sleep_features, n)
            for n in range(len(stages_classified)):
                wake_sleep_features[sleep_index[k]] = stages_classified[k]
            sleep_trip_index.append((sleep_index[0], sleep_index[-1], len(sleep_index)))
            sleep_features = []
            sleep_index = []
        state_last = state_start
    if len(sleep_features) > 0:
        stages_classified = sleep_KMean(sleep_features, n)
        for k in range(len(stages_classified)):
            sleep_features[sleep_index[k]] = stages_classified[k]
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
    print(label_class)
    print(f"{[k[0] for k in label_class]} : {[k[1] for k in label_class]}")
    y_out = [new_label.index(k) for k in y]
    return y_out
