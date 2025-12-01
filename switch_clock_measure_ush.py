from circuit_sim import circuit_sim
from get_round import get_round_time_params, try_one_time

sim_con = circuit_sim("dff_ush.cir")
open("tmp_ush/hold_setup.csv",mode="w").close()

# LIc積
lic = 74.4 * 2.4

# Icを刻んでループ
for i in range(1,11):
    ic = i*10
    sim_con.new_make_dff(ic,lic,0.5*10**(-3))

    sim_con.sim()
    netlist_file = "tmp_ush/dff_"+str(lic)+"_"+str(ic)+".jsm"
    sim_con.output_netlist(netlist_file)

    #one_time_file = "tmp/dff_192.5_" + str(1c) + ".csv"
    one_time_file = "tmp_ush/dff_"+str(lic)+"_" + str(ic) + ".csv"
    open(one_time_file,mode="w").close()
    # print("one_time_file:", one_time_file)
    try_one_time(netlist_file, one_time_file)
    hold_round, setup_round = get_round_time_params(one_time_file)
    
    output_file = "tmp_ush/hold_setup.csv"
    with open(output_file, mode="a") as f:
        f.write("{0},{1},{2},{3}\n".format(lic,ic,hold_round,setup_round))