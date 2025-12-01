from circuit_sim import circuit_sim
from get_round import get_round_time_params, try_one_time

sim_con = circuit_sim("dff_base.cir")
open("tmp/hold_setup.csv",mode="w").close()

# LIc積
lic = 192.5

# Icを刻んでループ
for i in range(1,1+1):
    ic = i*10
    one_time_file = "tmp/dff_"+str(lic)+"_" + str(ic) + ".csv"
    print("one_time_file:", one_time_file)
    hold_round, setup_round = get_round_time_params(one_time_file)
    
    output_file = "tmp/hold_setup.csv"
    with open(output_file, mode="a") as f:
        f.write("{0},{1},{2},{3}\n".format(lic,ic,hold_round,setup_round))