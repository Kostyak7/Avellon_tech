import pandas as pd
import os

df = pd.DataFrame(columns=["A","B","C","D"])
os.chdir("w_data")
file_list = os.listdir()

ind_a, ind_b, ind_c, ind_d = 0, 0, 0, 0
for file_name in file_list:
    data = pd.read_csv(file_name)
    max_amplitude = max([float(y) for y in data['y']])

    if file_name[10] == 'A':
        df.loc[ind_a, "A"] = max_amplitude
        ind_a += 1
    elif file_name[10] == 'B':
        df.loc[ind_b, "B"] = max_amplitude
        ind_b += 1
    elif file_name[10] == 'C':
        df.loc[ind_c, "C"] = max_amplitude
        ind_c += 1
    else:
        df.loc[ind_d, "D"] = max_amplitude
        ind_d += 1

os.chdir("..")
df.to_csv("wind_data.csv", index=False)