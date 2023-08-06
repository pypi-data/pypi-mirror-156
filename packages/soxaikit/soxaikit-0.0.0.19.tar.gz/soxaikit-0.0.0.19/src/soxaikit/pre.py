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

def spo2_r(r):
    SPO2 = -3.0 * r + 110
    if SPO2 > 100:
        SPO2 = 100
    return r

def get_Spo2(array_r, array_dc):
    return [spo2_r(k) for k in array_r]

def get_wear(array_T):
    return [k>30 for k in array_T]

# a = [1, 2, 3, 4, 3, 0, 0, 0, 0, 2, 1]
# output = pre_process_smooth(a, 3, True, True, True)
# print(a)
# print(output)
#
# a = [1, 2, 2, 2, 2, 50, 50, 10, 0, 2, 1]
# output = pre_process_actigraph(a)
# print(a)
# print(output)
