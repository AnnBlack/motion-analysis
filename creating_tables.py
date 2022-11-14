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


# calculates mean from a triaxial table
# paramerets:
# sourceDict = n x 3 dictionary of, for example, accel_x , accel_y and accel_z.
# XYZname = name of the resulting table that will be appended as headers for all 3 axes, in
# case of the above example XYZname = "accel".
def createMeanDict(source_df, data_name, chunkAmount):
    calculation = "mean";
    X = data_name + "-" + calculation + "()" + "-X";
    Y = data_name + "-" + calculation + "()" + "-Y";
    Z = data_name + "-" + calculation + "()" + "-Z";
    chunkSize = int(len(source_df.index)/chunkAmount);
    dict_temp = {X: [source_df.iloc[0:chunkSize, [0]].mean().item()], Y: [source_df.iloc[0:chunkSize, [1]].mean().item()], Z: [source_df.iloc[0:chunkSize, [2]].mean().item()]};
    for i in range (chunkSize,len(source_df.index),chunkSize): # to-do: calibrate starting index for evening out the mean values (esp Z axis)
        list_temp = [source_df.iloc[i:i+chunkSize, [0]].mean().item(), source_df.iloc[i:i+chunkSize, [1]].mean().item(), source_df.iloc[i:i+chunkSize, [2]].mean().item()];
        dict_temp[X].append(list_temp[0]);
        dict_temp[Y].append(list_temp[1]);
        dict_temp[Z].append(list_temp[2]);

    data_frame = pd.DataFrame(data = dict_temp);
    return data_frame;


measurement_name_XYZ = "tBodyAcc";

source = df_upstairs_accel.iloc[:, [1, 2, 3]];
meanTable = createMeanDict(source, measurement_name_XYZ, 5);
meanTable.to_csv("./prepared_tables/mean.csv",index=False,mode='w+');
print(meanTable);
