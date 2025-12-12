import pandas as pd
import multiprocessing
# from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import time

from circuit_sim import circuit_sim

ic_list = [20, 50, 100, 213]
vb_list = [0.50e-3, 2.50e-3]
bc_list = [2]
jj_count_list = [16, 32, 48, 64, 80]
tot_combi = len(ic_list) * len(vb_list) * len(bc_list) * len(jj_count_list)
indices = range(1, tot_combi + 1)

def strParse(index, tot_combi):
    ic_tag = (index - 1) % len(ic_list)
    vb_tag = ((index - 1) // len(ic_list)) % len(vb_list)
    bc_tag = ((index - 1) // (len(ic_list) * len(vb_list))) % len(bc_list)
    jjc_tag = ((index - 1) // (len(ic_list) * len(vb_list) * len(bc_list))) % len(jj_count_list)
    Ic = ic_list[ic_tag]
    vb = vb_list[vb_tag]
    bc = bc_list[bc_tag]
    jj_count = jj_count_list[jjc_tag]
    return vb, bc, Ic, jj_count

def run_simulation(i):
    vb, bc, Ic, jj_count = strParse(i, tot_combi)
    Ic_scale = Ic / 213
    Vb_scale = vb / 2.50e-3
    time.sleep(i*0.2)
    # print(f"Start simulation {i} with Ic={Ic:.2f}uA, Vb={vb*(10**3):.2f}mV, Betac={bc}, JJ count={jj_count}")
    # time.sleep(4)

    target = "sfq-jtl-axsfq"
    sorce_netlist = target + "-" + str(jj_count) + ".jsm"
    des_dir = "jitter_sfq_" + str(jj_count)

    sim_con = circuit_sim(sorce_netlist)
    sim_con.change_Ic_sfq(Ic_scale)
    sim_con.change_Vb_sfq(Vb_scale)
    sim_con.change_temp(0)
    sim_con.sim()
    index = i % 8
    netlist_file = f"{des_dir}/jitter_{index}.cir"
    sim_con.output_netlist(netlist_file)
    
    diff_file = f"{des_dir}/diff_{index}.csv"
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

    indices = range(1, tot_combi + 1)
    
    for i in indices:
        vb, bc, Ic, jj_count = strParse(i, tot_combi)
        print(f"Sim {i}/{tot_combi}: Ic={Ic:.2f}uA, Vb={vb*(10**3):.2f}mV, Betac={bc}, JJ count={jj_count}")
    
    max_workers = 20
    # max_workers = int(multiprocessing.cpu_count()/2)
    print(f"Using {max_workers} threads for simulation.")

    with ProcessPoolExecutor(max_workers=int(max_workers)) as executor:
    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(run_simulation, indices)
        executor.shutdown(wait=True)