import pandas as pd
import numpy as np
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "LOCATION_CLUSTER_ID"]


def get_location_cluster_minute(ind_cluster_label_table_path, date):
    df_cluster = pd.read_csv(ind_cluster_label_table_path)
    df_cluster_day = df_cluster[df_cluster.Time.str.contains(date)]
    df_cluster_day.reset_index(inplace=True, drop=True)

    if df_cluster_day.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    tz_list = []
    for time_str in df_cluster_day["Time"]:

        hour_min_second = time_str.split(".")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        tz_list.append(time_str.split(" ")[2])

    df_cluster_day.loc[:, "Hour"] = hour_list
    df_cluster_day.loc[:, "Minute"] = minute_list
    df_cluster_day.loc[:, "Date"] = ymd_list

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]

    df_cluster_day = df_cluster_day[df_cluster_day.Date == YMD]
    df_cluster_day.reset_index(inplace=True, drop=True)

    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for min in range(60):
            hour_min = str(hour) + "_" + str(min)

            df_cluster_hour = df_cluster_day[df_cluster_day.Hour == hour]
            df_cluster_min = df_cluster_hour[df_cluster_hour.Minute == min]
            if len(df_cluster_min) > 0:
                hour_min_dict[hour_min] = dict()
                hour_min_dict[hour_min]["LOCATION_CLUSTER_ID"] = list(df_cluster_min["Cluster_ID"])
            else:
                hour_min_dict[hour_min] = {"LOCATION_CLUSTER_ID": NAN}

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1], hour_min_dict[hour_min]["LOCATION_CLUSTER_ID"]]
        rows.append(row)

    df_minute = pd.DataFrame(rows, columns=colnames)

    return df_minute


if __name__ == "__main__":
    df_cluster_day = pd.read_csv(
        r"D:\data\TIME\intermediate_sample\idealistsustainerexpansive@timestudy_com\2021-11-07\watch_accelerometer_swan_clean_2021-11-07.csv")
    date = ""
    df_minute = get_location_cluster_minute(df_cluster_day, date)
    print(df_minute)
    df_minute.to_csv(r"C:\Users\Jixin\Downloads\swan_minute.csv")
