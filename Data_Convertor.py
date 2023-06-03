import pandas as pd
import os

# Делаем вариант для чтения и работы.
os.chdir("data")
LoF = os.listdir()

for FileName in LoF:
    df = pd.read_csv(FileName, header=None)

    time_base = int(df.iloc[0][0][10:-2])
    time_base *= 10 ** (-6)
    data_points = int(df.iloc[5][0][12:])
    nbm_sqr = 16
    step = time_base * nbm_sqr / data_points

    amount_add_info = 6
    steps = [None, None, None, None, None, None ]
    for i in range(data_points):
        steps.append((i-1) * step)
    df["Steps"] = steps

    os.chdir("../r_data")
    df.to_csv("R_" + FileName, index = False, header=None)

    os.chdir("../w_data")
    df = df.drop(index=[0,1,2,3,4,5])
    df.loc[5] = ["y","x"]
    df = df.sort_index()
    df.to_csv("W_" + FileName, index = False, header=None)

    os.chdir("../data")

os.chdir("..")