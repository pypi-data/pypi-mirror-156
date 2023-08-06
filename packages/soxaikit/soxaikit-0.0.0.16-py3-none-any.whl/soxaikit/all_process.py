import os

from IO.DataLoadSave import load_raw_data, output_arrays_to_file, combine

from plot.soxaiPlot import plot_time_domain, plot_features, multipage_save

from process.PreProcessModel import pre_process_smooth, pre_process_actigraph, getSpo2, pre_process_get_wear, \
    pre_process_average, pre_process_accumulate, merge_array
from process.feature_extract import feature_from_ppg, feature_from_xyz

from sleep.SleepStageModel import sleep_stage_cal, print_sleep_info, plot_sleep_info

# process the raw data to be the ring's format
def run_all():
    combine("XYZ")
    combine("PPG")
    combine("T")
    data_ppg, keys_ppg = load_raw_data("PPG")
    data_xyz, keys_xyz = load_raw_data("XYZ")
    data_T, keys_T = load_raw_data("T")
    features_ppg, keys_feature_ppg = feature_from_ppg(data_ppg)
    features_xyz, keys_feature_xyz = feature_from_xyz(data_xyz)

    features_ppg_1min = pre_process_average(features_ppg, 60)
    print(f"features_ppg_1min : size ({len(features_ppg_1min)}, {len(features_ppg_1min[0])}), keys: {keys_feature_ppg}")

    features_xyz_1min = pre_process_accumulate(features_xyz, 60)
    print(f"features_xyz_1min : size ({len(features_xyz_1min)}, {len(features_xyz_1min[0])}), keys: {keys_feature_xyz}")

    features_1min, keys_1min = merge_array(features_ppg_1min,keys_feature_ppg,features_xyz_1min,keys_feature_xyz)
    features_1min, keys_1min = merge_array(features_1min,keys_1min,data_T,keys_T)
    output_arrays_to_file(features_1min,keys_1min,"ring_features_1min", out_folder_name="ring")

    features_ring, key_ring = load_raw_data("ring_features_1min", 'ring')

    wear = pre_process_get_wear(features_ring[key_ring.index('T')])
    print(f"features ring : size ({len(features_ring)}, {len(features_ring[0])}), {key_ring}")
    spo2 = getSpo2(features_ring[key_ring.index('r')], features_ring[key_ring.index('dc')])
    hr_mean, hr_max, hr_min = pre_process_smooth(features_ring[key_ring.index('hr')], wear ,5)
    print(f"hr len {len(hr_mean)}, {len(hr_max)}, {len(hr_min)}")
    hrv_mean, hrv_max, hrv_min = pre_process_smooth(features_ring[key_ring.index('hrv')], wear,5)
    print(f"hrv len {len(hrv_mean)}, {len(hrv_max)}, {len(hrv_min)}")
    spo2_mean, spo2_max, spo2_min = pre_process_smooth(spo2,wear, 5)
    print(f"spo2 len {len(spo2_mean)}, {len(spo2_max)}, {len(spo2_min)}")
    actigraph, sleep = pre_process_actigraph(features_ring[key_ring.index('zc')])
    print(f"sleep len {len(sleep)}, {len(actigraph)}")

    features_processed = [features_ring[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, sleep, actigraph, features_ring[key_ring.index('T')], wear]
    key_processed = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T', 'wear']

    output_arrays_to_file(features_processed, key_processed, "features_pre_processed")

    wake_sleep_features, sleep_trip_index = sleep_stage_cal(features_processed)
    features_final=[features_processed[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, wake_sleep_features, actigraph, features_ring[key_ring.index('T')], wear]
    key_final = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T', 'wear']

    print_sleep_info(features_processed[0], wake_sleep_features, sleep_trip_index)
    print(f"sleep_trip_index: {sleep_trip_index}")

    plot_sleep_info(features_processed[0], wake_sleep_features, sleep_trip_index)
    plot_time_domain(features_ring, key_ring, title='data from ring')
    plot_features(features_processed, key_processed, 'pre-processed')
    plot_features(features_final, key_final, 'final')

    output_arrays_to_file(features_final, key_final, "features_output")


    multipage_save(os.getcwd()+"/output/"+ f"{features_final[0][0].strftime('%Y%m%d')}" +"_all_results.pdf")
# plt.show()