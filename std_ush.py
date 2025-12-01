from circuit_sim import circuit_sim
import pandas as pd
import warnings, sys
from concurrent.futures import ThreadPoolExecutor
import os, threading, time
from tqdm import tqdm
import numpy as np
warnings.simplefilter('ignore')
# from test5 import change_timing, get_switch_timing, sim, check_timing, erf_inverse_search, calc_time_param

# 入力タイミングをずらす時間のおおよその範囲を記載したファイルを指定
time_file = "tmp_ush/hold_setup.csv"
lic = 74.4 * 2.4
bias_vol_v = 0.5 * 10**(-3)

# ジッタを付与しての実行回数の指定
# try_count = 10 # 13m, 60m
# try_count = 100 # 2h48m, 8h19m
# try_count = 250 # 5h33m
try_count = 1000 # 22h12m, 96h29m
# try_count = 5000 #

def run_simulation(i):
    time.sleep(i)
    ic = 5*(i+1) 
    
    if ic < 20:
        # search_range = range(-15, 16)
        search_range = np.arange(-15, 16, 0.5)
    elif ic < 50:
        # search_range = range(-10, 11)
        search_range = np.arange(-7, 8, 0.25)
    else:
        # search_range = range(-5, 6)
        search_range = np.arange(-5, 6, 0.2)
        # print(search_range)
    # sys.exit()
    
    sims = search_range.shape[0]
    bar = tqdm(total=sims*2, position=i, desc=f"Sim {i}", leave=True, ncols=80)
    # bar = tqdm(total=42, position=i, desc=f"Sim {i}", leave=True, ncols=80)

    sim_con = circuit_sim("dff_ush.cir")
    Icn, power = sim_con.new_make_dff2(ic, lic, bias_vol_v)
    sim_con.sim()
    df = pd.read_csv(time_file, names=["LIc","Ic","hold","setup"])
    obj_data = df[(df["LIc"] == lic) & (df["Ic"] == ic)]
    setup, hold = obj_data["setup"].iloc[0], obj_data["hold"].iloc[0]
    # print(setup, hold)

    hold_output_file = "timing_ush/hold_"+str(lic)+"_"+str(ic)+".csv"
    setup_output_file = "timing_ush/setup_"+str(lic)+"_"+str(ic)+".csv"

    # 入力タイミングがクロックの中央にある時の、出力タイミングを取得
    # この出力タイミングとの誤差が少ない時、そのクロックでスイッチしたと判定する
    # clock at 300ps
    sim_con.din_generator(350,100,1)
    sim_con.sim()
    dout_clock1 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

    # clock at 400ps
    sim_con.din_generator(450,100,1)
    sim_con.sim()
    dout_clock2 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

    # clock at 500ps
    sim_con.din_generator(550,100,1)
    sim_con.sim()
    dout_clock3 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]
        
    # print("dout_clock1",dout_clock1)
    # print("dout_clock2",dout_clock2)
    # print("dout_clock3",dout_clock3)

    # sim_con.add_jitter(["jtl_squid","jtl_base","X1_squid","X2_squid","X3_squid","X4_squid","X5_squid","X6_squid","X7_squid","DFF_"],"temp=4.2 neb=10000GHz" )
    sim_con.add_jitter(["X1_squid","X2_squid","X3_squid","X4_squid","X5_squid","X6_squid","X7_squid","DFF_"],"temp=4.2 neb=10000GHz" )

    sim_con.change_din("Vin1          31    0    PWL(0ps 0mV 450ps 0mV 451ps 0.517mV 452ps 0.517mV 453ps 0mV)")
    sim_con.sim()
    
    #holdタイム
    for diff_time in search_range:
        bar.update(1)
        
        # 入力タイミングをずらす
        din = hold + diff_time
        offset = din - 450
        din_time = 450 + offset

        tmp_sim = circuit_sim("dff_ush.cir")
        tmp_sim.netlist = sim_con.netlist

        not_clock1_switching_count = 0
        not_clock2_switching_count = 0
        not_clock3_switching_count = 0
        non_output_error = 0

        tmp_sim.change_timing(1,offset)
        for j in range(try_count):
            tmp_sim.sim()
            data_out_time = tmp_sim.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"])
            if len(data_out_time) >= 1:
                new_time = data_out_time.iloc[0,0]
            else:
                new_time = 10
                non_output_error += 1
            
            # print("count",j,"new_time:",new_time)

            # それぞれのクロックでスイッチしたかどうかを判定
            if tmp_sim.check_timing(new_time,dout_clock1,50e-12) == False:
                not_clock1_switching_count += 1
            if tmp_sim.check_timing(new_time,dout_clock2,50e-12) == False:
                not_clock2_switching_count += 1
            if tmp_sim.check_timing(new_time,dout_clock3,50e-12) == False:
                not_clock3_switching_count += 1

        clock1_in_time = 400
        clock2_in_time = 500
        clock3_in_time = 600

        pd.DataFrame([{'din_time':din_time,'non_output_error':non_output_error,'clock1_switching_probability':round(1-not_clock1_switching_count/try_count,4),'clock2_switching_probability':round(1-not_clock2_switching_count/try_count,4),'clock3_switching_probability':round(1-not_clock3_switching_count/try_count,4)}]).to_csv(hold_output_file,mode="a",header=False,index=False,float_format="%.4f")
    
    # setupタイム
    for diff_time in search_range:
        bar.update(1)
        
        # 入力タイミングをずらす
        din = setup + diff_time
        offset = din - 350
        din_time = 350 + offset

        tmp_sim = circuit_sim("dff_ush.cir")
        tmp_sim.netlist = sim_con.netlist

        not_clock1_switching_count = 0
        not_clock2_switching_count = 0
        not_clock3_switching_count = 0
        non_output_error = 0

        tmp_sim.change_timing(1,offset)
        for j in range(try_count):
            tmp_sim.sim()
            data_out_time = tmp_sim.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"])
            if len(data_out_time) >= 1:
                new_time = data_out_time.iloc[0,0]
            else:
                new_time = 10
                non_output_error += 1
            
            # print("count",j,"new_time:",new_time)
            
            # それぞれのクロックでスイッチしたかどうかを判定
            if tmp_sim.check_timing(new_time,dout_clock1,50e-12) == False:
                not_clock1_switching_count += 1
            if tmp_sim.check_timing(new_time,dout_clock2,50e-12) == False:
                not_clock2_switching_count += 1
            if tmp_sim.check_timing(new_time,dout_clock3,50e-12) == False:
                not_clock3_switching_count += 1

        clock1_in_time = 400
        clock2_in_time = 500
        clock3_in_time = 600

        pd.DataFrame([{'din_time':din_time,'non_output_error':non_output_error,'clock1_switching_probability':round(1-not_clock1_switching_count/try_count,4),'clock2_switching_probability':round(1-not_clock2_switching_count/try_count,4),'clock3_switching_probability':round(1-not_clock3_switching_count/try_count,4)}]).to_csv(setup_output_file,mode="a",header=False,index=False,float_format="%.4f")

    bar.close()
    
if __name__ == "__main__":
    for i in range(1, 19 + 1):
        open(f"timing_ush/hold_"+str(lic)+"_"+str(5*(i+1))+".csv", "w").close()
        open(f"timing_ush/setup_"+str(lic)+"_"+str(5*(i+1))+".csv", "w").close()
    
    max_workers = 19
    indices = range(1, 19 + 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(run_simulation, indices))

    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # executor.map(run_simulation, indices)

# for ic in range(10,110,10):

#     Icn, power = sim_con.new_make_dff2(ic,lic,0.5*10**(-3))
#     sim_con.sim()
#     df = pd.read_csv(time_file, names=["LIc","Ic","hold","setup"])
#     obj_data = df[(df["LIc"] == lic) & (df["Ic"] == ic)]
#     setup, hold = obj_data["setup"].iloc[0], obj_data["hold"].iloc[0]
#     print(setup, hold)

#     hold_output_file = "timing_ush/hold_"+str(lic)+"_"+str(ic)+".csv"
#     setup_output_file = "timing_ush/setup_"+str(lic)+"_"+str(ic)+".csv"

#     # 入力タイミングがクロックの中央にある時の、出力タイミングを取得
#     # この出力タイミングとの誤差が少ない時、そのクロックでスイッチしたと判定する
#     # clock at 300ps
#     sim_con.din_generator(250,100,1)
#     sim_con.sim()
#     dout_clock1 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

#     # clock at 400ps
#     sim_con.din_generator(350,100,1)
#     sim_con.sim()
#     dout_clock2 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]

#     # clock at 500ps
#     sim_con.din_generator(450,100,1)
#     sim_con.sim()
#     dout_clock3 = sim_con.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).iloc[0,0]
        
#     print("dout_clock1",dout_clock1)
#     print("dout_clock2",dout_clock2)
#     print("dout_clock3",dout_clock3)

#     sim_con.add_jitter(["jtl_squid","jtl_base","X1_squid","X2_squid","X3_squid","X4_squid","X5_squid","X6_squid","X7_squid","DFF_"],"temp=4.2 neb=10000GHz" )

#     sim_con.change_din("Vin1          31    0    PWL(0ps 0mV 350ps 0mV 351ps 0.517mV 352ps 0.517mV 353ps 0mV)")
#     sim_con.sim()

#     #holdタイム
#     for diff_time in range(-10,11):

#         # 入力タイミングをずらす
#         din = hold + diff_time
#         offset = din - 350
#         din_time = 350 + offset

#         tmp_sim = circuit_sim("dff_base.cir")
#         tmp_sim.netlist = sim_con.netlist

#         not_clock1_switching_count = 0
#         not_clock2_switching_count = 0
#         not_clock3_switching_count = 0
#         non_output_error = 0

#         tmp_sim.change_timing(1,offset)
#         for j in range(try_count):
#             tmp_sim.sim()
#             data_out_time = tmp_sim.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"])
#             if len(data_out_time) >= 1:
#                 new_time = data_out_time.iloc[0,0]
#             else:
#                 new_time = 10
#                 non_output_error += 1
            
#             print("count",j,"new_time:",new_time)

#             # それぞれのクロックでスイッチしたかどうかを判定
#             if tmp_sim.check_timing(new_time,dout_clock1,50e-12) == False:
#                 not_clock1_switching_count += 1
#             if tmp_sim.check_timing(new_time,dout_clock2,50e-12) == False:
#                 not_clock2_switching_count += 1
#             if tmp_sim.check_timing(new_time,dout_clock3,50e-12) == False:
#                 not_clock3_switching_count += 1

#         clock1_in_time = 300
#         clock2_in_time = 400
#         clock3_in_time = 500

#         pd.DataFrame([{'din_time':din_time,'non_output_error':non_output_error,'clock1_switching_probability':round(1-not_clock1_switching_count/try_count,2),'clock2_switching_probability':round(1-not_clock2_switching_count/try_count,2),'clock3_switching_probability':round(1-not_clock3_switching_count/try_count,2)}]).to_csv(hold_output_file,mode="a",header=False,index=False)
    
#     # setupタイム
#     for diff_time in range(-10,11):
#         # 入力タイミングをずらす
#         din = setup + diff_time
#         offset = din - 350
#         din_time = 350 + offset

#         tmp_sim = circuit_sim("dff_base.cir")
#         tmp_sim.netlist = sim_con.netlist

#         not_clock1_switching_count = 0
#         not_clock2_switching_count = 0
#         not_clock3_switching_count = 0
#         non_output_error = 0

#         tmp_sim.change_timing(1,offset)
#         for j in range(try_count):
#             tmp_sim.sim()
#             data_out_time = tmp_sim.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"])
#             if len(data_out_time) >= 1:
#                 new_time = data_out_time.iloc[0,0]
#             else:
#                 new_time = 10
#                 non_output_error += 1
            
#             print("count",j,"new_time:",new_time)
            
#             # それぞれのクロックでスイッチしたかどうかを判定
#             if tmp_sim.check_timing(new_time,dout_clock1,50e-12) == False:
#                 not_clock1_switching_count += 1
#             if tmp_sim.check_timing(new_time,dout_clock2,50e-12) == False:
#                 not_clock2_switching_count += 1
#             if tmp_sim.check_timing(new_time,dout_clock3,50e-12) == False:
#                 not_clock3_switching_count += 1

#         clock1_in_time = 300
#         clock2_in_time = 400
#         clock3_in_time = 500

#         pd.DataFrame([{'din_time':din_time,'non_output_error':non_output_error,'clock1_switching_probability':round(1-not_clock1_switching_count/try_count,2),'clock2_switching_probability':round(1-not_clock2_switching_count/try_count,2),'clock3_switching_probability':round(1-not_clock3_switching_count/try_count,2)}]).to_csv(setup_output_file,mode="a",header=False,index=False)
    
    