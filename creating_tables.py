import numpy as np
import pandas as pd

FILE_PATH = "./inputs/"
FILE_NAMES_UPSTAIRS = ["upstairs_with_barometer_1.xls", "upstairs_with_barometer_2.xls"]
FILE_NAME_DOWNSTAIRS = ["downstairs_with_barometer_1.xls", "downstairs_with_barometer_2.xls"]


def get_data_frames(file_names_list, accel_df=[], gyro_df=[], accel_linear_df=[]):
    for name in file_names_list:
        name = FILE_PATH + name
    accel_df.append(pd.read_excel(open(name, 'rb'), sheet_name="Accelerometer"))
    gyro_df.append(pd.read_excel(open(name, 'rb'), sheet_name="Gyroscope"))
    accel_linear_df.append(pd.read_excel(open(name, 'rb'), sheet_name="Linear Acceleration"))
    return [accel_df, gyro_df, accel_linear_df]


[df_upstairs_accel_list, df_upstairs_gyro_list, df_upstairs_accel_linear_list] = \
    get_data_frames(FILE_NAMES_UPSTAIRS)
df_upstairs_accel = pd.concat(df_upstairs_accel_list)
df_upstairs_gyro = pd.concat(df_upstairs_gyro_list)
df_upstairs_accel_linear = pd.concat(df_upstairs_accel_linear_list)
[df_downstairs_accel_list, df_downstairs_gyro_list, df_downstairs_accel_linear_list] = \
    get_data_frames(FILE_NAME_DOWNSTAIRS)
df_downstairs_accel = pd.concat(df_downstairs_accel_list)
df_downstairs_gyro = pd.concat(df_downstairs_gyro_list)
df_downstairs_accel_linear = pd.concat(df_downstairs_accel_linear_list)


# calculates given function from a triaxial table parameters: sourceDict: n x 3 dictionary of, for example,
# acceleration data - accel_x , accel_y and accel_z. data_name: 1st part of the resulting table name, for example -
# "accel". data_name: 2nd part of the resulting table name that will be calculated per axis and appended as headers
# for all 3 of them, for example - std startIndex: for calibration


def calculate_generic(fn_name, func, source_df, data_name, chunk_amount, start_index):
    calculation = fn_name.strip("get_")
    if len(source_df.columns) > 1:
        X = data_name + "-" + calculation + "()" + "-X"
        Y = data_name + "-" + calculation + "()" + "-Y"
        Z = data_name + "-" + calculation + "()" + "-Z"
        chunk_size = int(len(source_df.index) / chunk_amount)
        dict_temp = {X: [func(source_df.iloc[0:chunk_size, [0]]).item()],
                     Y: [func(source_df.iloc[0:chunk_size, [1]]).item()],
                     Z: [func(source_df.iloc[0:chunk_size, [2]]).item()]}
        for i in range(chunk_size + start_index, len(source_df.index) - 1, chunk_size):
            list_temp = [func(source_df.iloc[i:i + chunk_size, [0]]).item(),
                         func(source_df.iloc[i:i + chunk_size, [1]]).item(),
                         func(source_df.iloc[i:i + chunk_size, [2]]).item()]
            dict_temp[X].append(list_temp[0])
            dict_temp[Y].append(list_temp[1])
            dict_temp[Z].append(list_temp[2])
    else:
        X = data_name + "-" + calculation + "()"
        chunk_size = int(len(source_df.index) / chunk_amount)
        dict_temp = {X: [func(source_df.iloc[0:chunk_size, [0]]).item()]}
        for i in range(chunk_size + start_index, len(source_df.index) - 1, chunk_size):
            list_temp = [func(source_df.iloc[i:i + chunk_size, [0]]).item()]
            dict_temp[X].append(list_temp[0])

    data_frame = pd.DataFrame(data=dict_temp)
    return data_frame


def calculate_magnitude(source_df, data_name):
    calculation = 'Mag'
    header = data_name + calculation
    rows = np.sqrt(source_df.iloc[:, 0] ** 2 + source_df.iloc[:, 1] ** 2 + source_df.iloc[:, 2] ** 2).values.tolist()

    dict_temp = {header: rows}
    data_frame = pd.DataFrame(data=dict_temp)
    return data_frame


def get_mean(n): return n.mean()


def get_std(n): return n.std()


def get_mad(n): return (n - n.mean()).abs().mean()


def get_max(n): return n.max()


def get_min(n): return n.min()


def get_energy(n): return n.pow(2).sum() / len(n.index)


def get_iqr(n):
    q75, q25 = np.percentile(n.iloc[:, [0]], [75, 25])
    iqr = q75 - q25
    return iqr


functions = [get_mean, get_std, get_mad, get_max, get_min, get_energy, get_iqr]


class Measurement:
    def __init__(self, name, source):
        self.name = name
        self.source = source


acceleration = Measurement("tGravityAcc", df_upstairs_accel.iloc[:, [1, 2, 3]])
# to be separated into tBody and tLinear by a low pass Butterworth filter with a corner frequency of 0.3 Hz.
accelerationMag = Measurement("tGravityAccMag", calculate_magnitude(df_upstairs_accel, "tGravityAcc"))
gyroscope = Measurement("tBodyGyro", df_upstairs_gyro.iloc[:, [1, 2, 3]])
gyroscopeMag = Measurement("tBodyGyroMag", calculate_magnitude(df_upstairs_gyro, "tBodyGyro"))
accelerationLinear = Measurement("tBodyAcc", df_upstairs_accel_linear.iloc[:, [1, 2, 3]])
accelerationLinearMag = Measurement("tBodyAccMag", calculate_magnitude(df_upstairs_accel_linear, "tBodyAcc"))

measurementsUp = [accelerationLinear, acceleration, gyroscope, accelerationLinearMag, accelerationMag, gyroscopeMag]

tables = []
for measurement in measurementsUp:
    for function in functions:
        table = calculate_generic(function.__name__, function, measurement.source, measurement.name, 200, -4)
        tables.append(table)

tableUp = pd.concat(tables, axis=1)
label = ["WALKING_UPSTAIRS"] * len(tableUp.index)
tableUp["Activity"] = label

acceleration = Measurement("tGravityAcc", df_downstairs_accel.iloc[:, [1, 2, 3]])
# to be separated into tBody and tLinear by a low pass Butterworth filter with a corner frequency of 0.3 Hz.
accelerationMag = Measurement("tGravityAccMag", calculate_magnitude(df_downstairs_accel, "tGravityAcc"))
gyroscope = Measurement("tBodyGyro", df_downstairs_gyro.iloc[:, [1, 2, 3]])
gyroscopeMag = Measurement("tBodyGyroMag", calculate_magnitude(df_downstairs_gyro, "tBodyGyro"))
accelerationLinear = Measurement("tBodyAcc", df_downstairs_accel_linear.iloc[:, [1, 2, 3]])
accelerationLinearMag = Measurement("tBodyAccMag", calculate_magnitude(df_downstairs_accel_linear, "tBodyAcc"))

measurementsDown = [accelerationLinear, acceleration, gyroscope, accelerationLinearMag, accelerationMag, gyroscopeMag]

tables = []
for measurement in measurementsDown:
    for function in functions:
        table = calculate_generic(function.__name__, function, measurement.source, measurement.name, 200, -4)
        tables.append(table)

tableDown = pd.concat(tables, axis=1)
label = ["WALKING_DOWNSTAIRS"] * len(tableDown.index)
tableDown["Activity"] = label

fullTable = pd.concat([tableUp, tableDown])

fullTable.to_csv("./prepared_tables/fullTable.csv", index=False, mode='w+')
print(fullTable)

# %%
