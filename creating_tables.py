import pandas as pd
import xlrd
import matplotlib as mpl
import matplotlib.pyplot as plt

file_name = "./inputs/upstairs_with_barometer_1.xls";

df_upstairs_accel = pd.read_excel(open(file_name, 'rb'), sheet_name="Accelerometer");


# file_name = "./inputs/downstairs_with_barometer_1.xls";
# df_downstairs_accel = pd.read_excel(file_name, sheet_name="Accelerometer");


# #to access the entire data frame
# print(df_upstairs_accel);
#
# #to access the second column:
# print(df_upstairs_accel.get("Acceleration x (m/s^2)"));
#
# #print mean, std, min, max, etc:
# print(df_upstairs_accel.iloc[:, [1, 2, 3]].describe());
#
# #check for null entries:
# print(df_upstairs_accel.iloc[:, [1, 2, 3]].info());
#
# #visualize the datasets
# df_upstairs_accel.plot(x="Time (s)", y= [1, 2, 3]);
# plt.show();
#
# df_downstairs_accel.plot(x="Time (s)", y= [1, 2, 3]);
# plt.show();


def calculateMean(source_df, data_name, chunkAmount):
    calculation = "mean";
    X = data_name + "-" + calculation + "()" + "-X";
    Y = data_name + "-" + calculation + "()" + "-Y";
    Z = data_name + "-" + calculation + "()" + "-Z";
    chunkSize = int(len(source_df.index) / chunkAmount);
    dict_temp = {X: [source_df.iloc[0:chunkSize, [0]].mean().item()],
                 Y: [source_df.iloc[0:chunkSize, [1]].mean().item()],
                 Z: [source_df.iloc[0:chunkSize, [2]].mean().item()]};
    for i in range(chunkSize + 4, len(source_df.index),
                   chunkSize):  # to-do: calibrate starting index for evening out the mean values (esp Z axis)
        list_temp = [source_df.iloc[i:i + chunkSize, [0]].mean().item(),
                     source_df.iloc[i:i + chunkSize, [1]].mean().item(),
                     source_df.iloc[i:i + chunkSize, [2]].mean().item()];
        dict_temp[X].append(list_temp[0]);
        dict_temp[Y].append(list_temp[1]);
        dict_temp[Z].append(list_temp[2]);

    data_frame = pd.DataFrame(data=dict_temp);
    return data_frame;


# calculates given function from a triaxial table
# parameters:
# sourceDict: n x 3 dictionary of, for example, acceleration data - accel_x , accel_y and accel_z.
# data_name: 1st part of the resulting table name, for example - "accel".
# data_name: 2nd part of the resulting table name that will be calculated per axis and appended as headers for all 3 of them, for example - std
# startIndex: for calibration
def calculateGeneric(funcName, func, source_df, data_name, chunkAmount, startIndex):
    calculation = funcName;
    X = data_name + "-" + calculation + "()" + "-X";
    Y = data_name + "-" + calculation + "()" + "-Y";
    Z = data_name + "-" + calculation + "()" + "-Z";
    chunkSize = int(len(source_df.index) / chunkAmount);
    dict_temp = {X: [func(source_df.iloc[0:chunkSize, [0]]).item()], Y: [func(source_df.iloc[0:chunkSize, [1]]).item()],
                 Z: [func(source_df.iloc[0:chunkSize, [2]]).item()]};
    for i in range(chunkSize + startIndex, len(source_df.index)-1, chunkSize):
        list_temp = [func(source_df.iloc[i:i + chunkSize, [0]]).item(),
                     func(source_df.iloc[i:i + chunkSize, [1]]).item(),
                     func(source_df.iloc[i:i + chunkSize, [2]]).item()];
        dict_temp[X].append(list_temp[0]);
        dict_temp[Y].append(list_temp[1]);
        dict_temp[Z].append(list_temp[2]);

    data_frame = pd.DataFrame(data=dict_temp);
    return data_frame;


# wrappers to pass methods of generic objects:
def mean(n): return n.mean();
def std(n): return n.std();
#mad
def min(n): return n.min();
def max(n): return n.max();


measurement_name_XYZ = "tBodyAcc";
source = df_upstairs_accel.iloc[:, [1, 2, 3]];

meanTable = calculateGeneric('mean', mean, source, measurement_name_XYZ, 5, 4);
meanTable.to_csv("./prepared_tables/mean.csv", index=False, mode='w+');
print(meanTable);

stdTable = calculateGeneric('std', std, source, measurement_name_XYZ, 5, 0);
stdTable.to_csv("./prepared_tables/std.csv", index=False, mode='w+');
print(stdTable);

minTable = calculateGeneric('min', min, source, measurement_name_XYZ, 5, 0);
minTable.to_csv("./prepared_tables/std.csv", index=False, mode='w+');
print(minTable);

maxTable = calculateGeneric('max', max, source, measurement_name_XYZ, 5, 0);
maxTable.to_csv("./prepared_tables/std.csv", index=False, mode='w+');
print(maxTable);
