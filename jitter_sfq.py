import pandas as pd
import multiprocessing
# from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import time

from circuit_sim import circuit_sim

ic_list = [2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100, 150, 213]
vb_list = [0.50e-3, 2.50e-3]
bc_list = [2]
tot_combi = len(ic_list) * len(vb_list) * len(bc_list)
indices = range(1, tot_combi + 1)

def strParse(index, tot_combi):
    vb_tag = 0 if index <= (tot_combi/2) else 1
    bc_tag = 0
    # bc_tag = 0 if (index <= (tot_combi/4) or index > (tot_combi*3/4)) else 1
    vb = vb_list[vb_tag]
    bc = bc_list[bc_tag]
    # Ic = ic_list[(index % len(ic_list)) - 1]
    Ic = ic_list[(index - 1) % len(ic_list)]
    return vb, bc, Ic

def run_simulation(i):
    vb, bc, Ic = strParse(i, tot_combi)
    Ic_scale = Ic / 213
    Vb_scale = vb / 2.50e-3
    time.sleep(i*0.2)
    print(f"Start simulation {i} with Ic={Ic:.2f}uA, Vb={vb*(10**3):.2f}mV, Betac={bc}")
    time.sleep(4)
    
    sim_con = circuit_sim("sfq-jtl-axsfq.jsm")
    sim_con.change_Ic_sfq(Ic_scale)
    sim_con.change_Vb_sfq(Vb_scale)
    sim_con.change_temp(0)
    sim_con.sim()
    netlist_file = f"jitter_sfq_lv/jitter_{i}.cir"
    sim_con.output_netlist(netlist_file)
    
    diff_file = f"jitter_sfq_lv/diff_{i}.csv"
    open(diff_file, "w").close()
    sim_con.calc_jitter_sfq(
        ["P(B1|X1|X32)"],
        ["P(B1|X1|X43)"],
        80, diff_file,
        # try_count=2000, # 6h52m
        try_count=5000, #
        index=i
    )

    data = pd.read_csv(diff_file)
    # data[0] = data[0].apply(lambda x: 0 if abs(x) <= 1e-20 else x)
    data.to_csv(diff_file, index=False, header=False)

if __name__ == "__main__":
    # run_simulation(10)

    indices = range(1, tot_combi + 1)
    max_workers = 20
    # max_workers = int(multiprocessing.cpu_count()/2)
    print(f"Using {max_workers} threads for simulation.")

    with ProcessPoolExecutor(max_workers=int(max_workers)) as executor:
    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(run_simulation, indices)