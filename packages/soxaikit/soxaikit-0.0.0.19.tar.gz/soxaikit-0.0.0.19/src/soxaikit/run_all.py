import os


from .io import load, save, combine

from .plot import plot_time_domain, plot_features, multipage_save

from .pre import smooth, get_acti, get_Spo2, get_wear, \
    average, accumulate, merge
from .fea import feature_from_ppg, feature_from_xyz

# from .sleep import get_sleep, print_sleep_info, plot_sleep_info
import sleep as slp
# process the raw data to be the ring's format
def run():
    combine("XYZ")
    combine("PPG")
    combine("T")
    data_ppg, keys_ppg = load("PPG")
    data_xyz, keys_xyz = load("XYZ")
    data_T, keys_T = load("T")
    features_ppg, keys_feature_ppg = feature_from_ppg(data_ppg)
    features_xyz, keys_feature_xyz = feature_from_xyz(data_xyz)

    features_ppg_1min = average(features_ppg, 60)
    print(f"features_ppg_1min : size ({len(features_ppg_1min)}, {len(features_ppg_1min[0])}), keys: {keys_feature_ppg}")

    features_xyz_1min = accumulate(features_xyz, 60)
    print(f"features_xyz_1min : size ({len(features_xyz_1min)}, {len(features_xyz_1min[0])}), keys: {keys_feature_xyz}")

    features_1min, keys_1min = merge(features_ppg_1min, keys_feature_ppg, features_xyz_1min, keys_feature_xyz)
    features_1min, keys_1min = merge(features_1min, keys_1min, data_T, keys_T)
    save(features_1min, keys_1min, "ring_features_1min", out_folder_name="ring")

    features_ring, key_ring = load("ring_features_1min", 'ring')

    wear = get_wear(features_ring[key_ring.index('T')])
    print(f"features ring : size ({len(features_ring)}, {len(features_ring[0])}), {key_ring}")
    spo2 = get_Spo2(features_ring[key_ring.index('r')], features_ring[key_ring.index('dc')])
    hr_mean, hr_max, hr_min = smooth(features_ring[key_ring.index('hr')], wear, 5)
    print(f"hr len {len(hr_mean)}, {len(hr_max)}, {len(hr_min)}")
    hrv_mean, hrv_max, hrv_min = smooth(features_ring[key_ring.index('hrv')], wear, 5)
    print(f"hrv len {len(hrv_mean)}, {len(hrv_max)}, {len(hrv_min)}")
    spo2_mean, spo2_max, spo2_min = smooth(spo2, wear, 5)
    print(f"spo2 len {len(spo2_mean)}, {len(spo2_max)}, {len(spo2_min)}")
    actigraph, sleep = get_acti(features_ring[key_ring.index('zc')])
    print(f"sleep len {len(sleep)}, {len(actigraph)}")

    features_processed = [features_ring[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, sleep, actigraph, features_ring[key_ring.index('T')], wear]
    key_processed = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T', 'wear']

    save(features_processed, key_processed, "features_pre_processed")

    wake_sleep_features, sleep_trip_index = slp.get_sleep(features_processed)
    features_final=[features_processed[0], hr_mean, hr_max, hr_min, hrv_mean, hrv_max, hrv_min, spo2_mean, spo2_max, spo2_min, wake_sleep_features, actigraph, features_ring[key_ring.index('T')], wear]
    key_final = ['time', 'hr_mean', 'hr_max', 'hr_min', 'hrv_mean', 'hrv_max', 'hrv_min', 'spo2_mean', 'spo2_max', 'spo2_min', 'sleep', 'actigraph', 'T', 'wear']

    slp.print_sleep_info(features_processed[0], wake_sleep_features, sleep_trip_index)
    print(f"sleep_trip_index: {sleep_trip_index}")

    slp.plot_sleep_info(features_processed[0], wake_sleep_features, sleep_trip_index)
    plot_time_domain(features_ring, key_ring, title='data from ring')
    plot_features(features_processed, key_processed, 'pre-processed')
    plot_features(features_final, key_final, 'final')

    save(features_final, key_final, "features_output")


    multipage_save(os.getcwd()+"/output/"+ f"{features_final[0][0].strftime('%Y%m%d')}" +"_all_results.pdf")
# plt.show()