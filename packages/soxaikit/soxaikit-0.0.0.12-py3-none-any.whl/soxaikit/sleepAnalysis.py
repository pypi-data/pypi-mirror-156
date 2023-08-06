import os

from matplotlib import pyplot as plt

from DataLoadSave import load_raw_data,combine, output_arrays_to_file

from feature_extract import feature_from_ppg, feature_from_xyz

from soxaiPlot import plot_time_domain, plot_time_domain_single_figure, plot_time_domain_single_figure_combine, multipage_save

from PreProcessModel import pre_process_smooth, pre_process_average, pre_process_accumulate, pre_process_actigraph, merge_array

from SleepStageModel import sleep_stage_cal

# process the raw data to be the ring's format
# combine("XYZ")
# combine("PPG")
# combine("T")
data_ppg, keys_ppg = load_raw_data("PPG")
data_xyz, keys_xyz = load_raw_data("XYZ")
data_T, keys_T = load_raw_data("T")
features_ppg, keys_feature_ppg = feature_from_ppg(data_ppg)
features_xyz, keys_feature_xyz = feature_from_xyz(data_xyz)
output_arrays_to_file(features_ppg,keys_feature_ppg,"PPG_features")
features_ppg_1min = pre_process_average(features_ppg, 60)
features_xyz_1min = pre_process_accumulate(features_xyz, 60)
print(f"features_ppg_1min len {len(features_ppg_1min[0])}")
features_1min, keys_1min = merge_array(features_ppg_1min,keys_feature_ppg,features_xyz_1min,keys_feature_xyz)
features_1min, keys_1min = merge_array(features_1min,keys_1min,data_T,keys_T)
print(f"features_1min len {len(features_1min)}, {keys_1min}")

hr_mean, hr_max, hr_min = pre_process_smooth(features_1min[1],5)
print(f"hr len {len(hr_mean)}, {len(hr_max)}, {len(hr_min)}")
hrv_mean, hrv_max, hrv_min = pre_process_smooth(features_1min[2],5)
print(f"hrv len {len(hrv_mean)}, {len(hrv_max)}, {len(hrv_min)}")
spo2_mean, spo2_max, spo2_min = pre_process_smooth(features_1min[3],5)
print(f"spo2 len {len(spo2_mean)}, {len(spo2_max)}, {len(spo2_min)}")
actigraph, sleep = pre_process_actigraph(features_1min[4])
plt.figure()
plt.plot(sleep)
plt.show()
print(f"sleep len {len(sleep)}, {len(actigraph)}")

features_1min_processed = [features_1min[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, sleep, actigraph, features_1min[5] ]
key_processed = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T']
wake_sleep_features, sleep_trip_index = sleep_stage_cal(features_1min_processed)
features_final=[features_1min[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, wake_sleep_features, actigraph, features_1min[5] ]
key_final = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T']


output_arrays_to_file(features_ppg_1min,keys_feature_ppg,"PPG_features_1min")
output_arrays_to_file(features_xyz_1min,keys_feature_xyz,"XYZ_features_1min")
output_arrays_to_file(features_1min,keys_1min, "all_features_1min")
output_arrays_to_file(features_1min_processed, key_processed, "all_features_1min_processed")




plot_time_domain(data_ppg, keys_ppg)
plot_time_domain_single_figure_combine(data_xyz,keys_xyz)
plot_time_domain_single_figure_combine(data_T,keys_T)
plot_time_domain(features_ppg, keys_feature_ppg)
plot_time_domain(features_xyz, keys_feature_xyz)
plot_time_domain(features_ppg_1min, keys_feature_ppg)
plot_time_domain(features_1min, keys_1min)
# plot_time_domain_single_figure(features_1min_processed, key_processed)
plot_time_domain_single_figure_combine([features_1min_processed[0]] + features_1min_processed[1:4], [key_processed[0]] + key_processed[1:4])
plot_time_domain_single_figure_combine([features_1min_processed[0]] + features_1min_processed[4:7], [key_processed[0]]+ key_processed[4:7])
plot_time_domain_single_figure_combine([features_1min_processed[0]] + features_1min_processed[7:10], [key_processed[0]] + key_processed[7:10])

plot_time_domain([features_1min_processed[0], features_1min_processed[10]],['time', 'sleep'])
multipage_save(os.getcwd()+"/output/All_results.pdf")
plt.show()