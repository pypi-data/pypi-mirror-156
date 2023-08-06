from matplotlib import pyplot as plt

from DataLoadSave import load_raw_data,combine, output_arrays_to_file

from feature_extract import feature_from_ppg, feature_from_xyz

from soxaiPlot import plot_time_domain

from PreProcessModel import pre_process_smooth, pre_process_average, pre_process_accumulate, merge_array

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
features_1min, keys_1min = merge_array(features_ppg_1min,keys_feature_ppg,features_xyz_1min,keys_feature_xyz)
features_1min, keys_1min = merge_array(features_1min,keys_1min,data_T,keys_T)

output_arrays_to_file(features_ppg_1min,keys_feature_ppg,"PPG_features_1min")
output_arrays_to_file(features_xyz_1min,keys_feature_xyz,"XYZ_features_1min")
output_arrays_to_file(features_1min,keys_1min, "all_features_1min")

plot_time_domain(features_ppg, keys_feature_ppg)
plot_time_domain(features_xyz, keys_feature_xyz)
plot_time_domain(features_ppg_1min, keys_feature_ppg)
plot_time_domain(features_1min, keys_1min)

plt.show()