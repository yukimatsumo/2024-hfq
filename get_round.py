import pandas as pd
from scipy.special import erf
import numpy as np
from circuit_sim import circuit_sim
import warnings
import os 
# from test5 import change_timing, get_switch_timing, sim, check_timing, erf_inverse_search, calc_time_param


warnings.filterwarnings('ignore', category=FutureWarning)

def try_one_time(input_file, output_file):
    sim_con = circuit_sim(input_file)

    ### clock pulse time is 
    sim_con.din_generator(350,100,1)
    sim_con.sim()
    dout_clock1 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

    ### clock pulse time is 
    sim_con.din_generator(450,100,1)
    sim_con.sim()
    dout_clock2 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

    ### clock pulse time is 
    sim_con.din_generator(550,100,1)
    sim_con.sim()
    dout_clock3 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]
        
    print("dout_clock1",dout_clock1)
    print("dout_clock2",dout_clock2)
    print("dout_clock3",dout_clock3)

    ### the second input is 
    sim_con.din_generator(450,100,1)
    sim_con.sim()
        
    try_count = 1
    for i in range(-100,100):
        clock1_error_count = 0
        clock2_error_count = 0
        clock3_error_count = 0
        clock_in_time = 0

        non_output_error = 0
        data_out_time = 0
        new_sim_time = 450+i
        
        tmp_sim = sim_con
        tmp_sim.din_generator(new_sim_time,100,1)
        tmp_sim.sim()
        
        data_out_time = tmp_sim.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"])
        if (len(data_out_time) >= 1):
            ### check second switch timing
            new_time = data_out_time.iloc[0,0]
        else:
            new_time = 10
            non_output_error += 1

        print("new_time:",new_time)
        if tmp_sim.check_timing(new_time,dout_clock1,50e-12) == False:
                clock1_error_count += 1
        if tmp_sim.check_timing(new_time,dout_clock2,50e-12) == False:
                clock2_error_count += 1
        if tmp_sim.check_timing(new_time,dout_clock3,50e-12) == False:
                clock3_error_count += 1

        clock1_in_time = 400
        clock2_in_time = 500
        clock3_in_time = 600

        diff_time1 =  clock1_in_time - new_sim_time
        diff_time2 =  clock2_in_time - new_sim_time
        diff_time3 =  clock3_in_time - new_sim_time
        pd.DataFrame([{'time':new_sim_time,'non_output_error':non_output_error, 'diff_time1':diff_time1, 'diff_time2':diff_time2,'diff_time3':diff_time3, 'clock1_error_count':clock1_error_count,'clock2_error_count':clock2_error_count,'clock3_error_count':clock3_error_count}]).to_csv(output_file,mode="a",header=False,index=False)

def get_round_time_params(input_file):
    # CSVファイルを読み込み、1行目を無視する
    df = pd.read_csv(input_file, header=None, skiprows=1)

    target_column = df.iloc[:, 6]
    change_to_zero_indices = target_column[(target_column.diff() == -1)].index

    target_column = df.iloc[:, 6]
    print(target_column)
    change_to_one_indices = target_column[(target_column.diff() == 1)].index

    # それぞれの変化があった最初の行の最左の値（index 0の列）を取得
    first_change_to_zero = df.iloc[change_to_zero_indices[0], 0] if not change_to_zero_indices.empty else None
    first_change_to_one = df.iloc[change_to_one_indices[0], 0] if not change_to_one_indices.empty else None

    # 結果を表示
    print("1→0の最初の変化:", first_change_to_zero)
    print("0→1の最初の変化:", first_change_to_one)

    return first_change_to_zero, first_change_to_one

