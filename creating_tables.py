import numpy as np
import pandas as pd

file_path = "./inputs/"

# gathering upstairs data
file_names = ["upstairs_with_barometer_1.xls", "upstairs_with_barometer_2.xls"];
df_upstairs_accel_list = [];
df_upstairs_gyro_list = [];
df_upstairs_accel_linear_list = [];

for file_name in file_names:
    file_name = file_path + file_name;
    df_upstairs_accel_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Accelerometer"));
    df_upstairs_gyro_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Gyroscope"));
    df_upstairs_accel_linear_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Linear Acceleration"));

df_upstairs_accel = pd.concat(df_upstairs_accel_list);
df_upstairs_gyro = pd.concat(df_upstairs_gyro_list);
df_upstairs_accel_linear = pd.concat(df_upstairs_accel_linear_list);


# gathering downstairs data
file_names = ["downstairs_with_barometer_1.xls", "downstairs_with_barometer_2.xls"];
df_downstairs_accel_list = [];
df_downstairs_gyro_list = [];
df_downstairs_accel_linear_list = [];

for file_name in file_names:
    file_name = file_path + file_name;
    df_downstairs_accel_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Accelerometer"));
    df_downstairs_gyro_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Gyroscope"));
    df_downstairs_accel_linear_list.append(pd.read_excel(open(file_name, 'rb'), sheet_name="Linear Acceleration"));

df_downstairs_accel = pd.concat(df_downstairs_accel_list);
df_downstairs_gyro = pd.concat(df_downstairs_gyro_list);
df_downstairs_accel_linear = pd.concat(df_downstairs_accel_linear_list);

# calculates given function from a triaxial table
# parameters:
# sourceDict: n x 3 dictionary of, for example, acceleration data - accel_x , accel_y and accel_z.
# data_name: 1st part of the resulting table name, for example - "accel".
# data_name: 2nd part of the resulting table name that will be calculated per axis and appended as headers for all 3 of them, for example - std
# startIndex: for calibration
def calculateGeneric(funcName, func, source_df, data_name, chunkAmount, startIndex):
    calculation = funcName;
    if (len(source_df.columns) > 1):
        X = data_name + "-" + calculation + "()" + "-X";
        Y = data_name + "-" + calculation + "()" + "-Y";
        Z = data_name + "-" + calculation + "()" + "-Z";
        chunkSize = int(len(source_df.index) / chunkAmount);
        dict_temp = {X: [func(source_df.iloc[0:chunkSize, [0]]).item()],
                     Y: [func(source_df.iloc[0:chunkSize, [1]]).item()],
                     Z: [func(source_df.iloc[0:chunkSize, [2]]).item()]};
        for i in range(chunkSize + startIndex, len(source_df.index) - 1, chunkSize):
            list_temp = [func(source_df.iloc[i:i + chunkSize, [0]]).item(),
                         func(source_df.iloc[i:i + chunkSize, [1]]).item(),
                         func(source_df.iloc[i:i + chunkSize, [2]]).item()];
            dict_temp[X].append(list_temp[0]);
            dict_temp[Y].append(list_temp[1]);
            dict_temp[Z].append(list_temp[2]);
    else:
        X = data_name + "-" + calculation + "()";
        chunkSize = int(len(source_df.index) / chunkAmount);
        dict_temp = {X: [func(source_df.iloc[0:chunkSize, [0]]).item()]};
        for i in range(chunkSize + startIndex, len(source_df.index) - 1, chunkSize):
            list_temp = [func(source_df.iloc[i:i + chunkSize, [0]]).item()];
            dict_temp[X].append(list_temp[0]);

    data_frame = pd.DataFrame(data=dict_temp);
    return data_frame;


def calculateMag(source_df, data_name):
    calculation = 'Mag';
    header = data_name + calculation;
    rows = np.sqrt(source_df.iloc[:, 0] ** 2 + source_df.iloc[:, 1] ** 2 + source_df.iloc[:, 2] ** 2).values.tolist()

    dict_temp = {header: rows};
    data_frame = pd.DataFrame(data=dict_temp);
    return data_frame;


# wrappers to pass methods of generic objects:
def mean(n): return n.mean();
def std(n): return n.std();
def mad(n): return (n - n.mean()).abs().mean();
def min(n): return n.min();
def max(n): return n.max();

def energy(n): return n.pow(2).sum()/len(n.index);

def iqr(n): q75, q25 = np.percentile(n.iloc[:,[0]], [75 ,25]); iqr = q75 - q25; return iqr;


functions = [mean, std, mad, min, max, energy, iqr];


class Measurement:
    def __init__(self, name, source):
        self.name = name
        self.source = source


acceleration = Measurement("tGravityAcc", df_upstairs_accel.iloc[:, [1, 2, 3]]);   # to be separated into tBody and tLinear by a low pass Butterworth filter with a corner frequency of 0.3 Hz.
accelerationMag = Measurement("tGravityAccMag", calculateMag(df_upstairs_accel, "tGravityAcc"));
gyroscope = Measurement("tBodyGyro", df_upstairs_gyro.iloc[:, [1, 2, 3]]);
gyroscopeMag = Measurement("tBodyGyroMag", calculateMag(df_upstairs_gyro, "tBodyGyro"));
accelerationLinear = Measurement("tBodyAcc", df_upstairs_accel_linear.iloc[:, [1, 2, 3]]);
accelerationLinearMag = Measurement("tBodyAccMag", calculateMag(df_upstairs_accel_linear, "tBodyAcc"));

measurementsUp = [accelerationLinear,  acceleration,  gyroscope, accelerationLinearMag, accelerationMag,  gyroscopeMag]

tables = [];
for measurement in measurementsUp:
    for function in functions:
        table = calculateGeneric(function.__name__, function, measurement.source, measurement.name, 120, -4);
        tables.append(table);

        print(table);

tableUp = pd.concat(tables, axis=1)
label = ["WALKING_UPSTAIRS"] * len(tableUp.index);
tableUp["Activity"] = label;


acceleration = Measurement("tGravityAcc", df_downstairs_accel.iloc[:, [1, 2, 3]]);   # to be separated into tBody and tLinear by a low pass Butterworth filter with a corner frequency of 0.3 Hz.
accelerationMag = Measurement("tGravityAccMag", calculateMag(df_downstairs_accel, "tGravityAcc"));
gyroscope = Measurement("tBodyGyro", df_downstairs_gyro.iloc[:, [1, 2, 3]]);
gyroscopeMag = Measurement("tBodyGyroMag", calculateMag(df_downstairs_gyro, "tBodyGyro"));
accelerationLinear = Measurement("tBodyAcc", df_downstairs_accel_linear.iloc[:, [1, 2, 3]]);
accelerationLinearMag = Measurement("tBodyAccMag", calculateMag(df_downstairs_accel_linear, "tBodyAcc"));

measurementsDown = [accelerationLinear,  acceleration,  gyroscope, accelerationLinearMag, accelerationMag,  gyroscopeMag]

tables = [];
for measurement in measurementsDown:
    for function in functions:
        table = calculateGeneric(function.__name__, function, measurement.source, measurement.name, 120, -4);
        tables.append(table);

        print(table);

tableDown = pd.concat(tables, axis=1)
label = ["WALKING_DOWNSTAIRS"] * len(tableDown.index);
tableDown["Activity"] = label;

fullTable = pd.concat([tableUp, tableDown]);

fullTable.to_csv("./prepared_tables/fullTable.csv", index=False, mode='w+');
print(fullTable);


