import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from concurrent.futures import ThreadPoolExecutor
import threading, time

from circuit_sim import circuit_sim

lic_list = [2.4*74.4, 3.5*60.8]
vb_list = [0.5*10**(-3), 0.25*10**(-3)]
ibf_list = [0.4, 0.5]
bc_list = [1, 2]

def run_simulation(i):
    index = bin(i-1)[2:].zfill(4)
    lic = lic_list[int(index[0])]
    vb = vb_list[int(index[1])]
    ibf = ibf_list[int(index[2])]
    bc = bc_list[int(index[3])]
    Ic = 60.8 if lic == 3.5*60.8 else 74.4
    time.sleep(i*0.2)
    print(f"Start simulation {i} with Ic={Ic}uA, LIc={lic}uA*pH, Vb={vb*(10**3)}mV, Ibfactor={ibf}, Betac={bc}")
    time.sleep(6)
    
    sim_con = circuit_sim("jtl_base.cir")
    sim_con.new_make_jtl2(Ic, lic, vb, ibf, bc)
    sim_con.sim()
    netlist_file = f"jitter_hstp/jitter_{i}.cir"
    sim_con.output_netlist(netlist_file)

    diff_file = f"jitter_hstp/diff_{i}.csv"
    # open(diff_file, "w").close()
    sim_con.calc_jitter(
        ["P(B1|X1|X2|X2)", "P(B2|X1|X2|X2)"],
        ["P(B1|X2|X6|X7)", "P(B2|X2|X6|X7)"],
        # ["P(B1|X1|X1|X35)", "P(B2|X1|X1|X35)"],
        # ["P(B1|X2|X20|X35)", "P(B2|X2|X20|X35)"],
        40, diff_file,
        # try_count=1000, #1h28m
        try_count=5000, #
        # try_count=10000, #14h40m
        index=i
    )

    data = pd.read_csv(diff_file)
    data[0] = data[0].apply(lambda x: 0 if abs(x) <= 1e-20 else x)
    data.to_csv(diff_file, index=False, header=False)

if __name__ == "__main__":
    indices = range(1, 16 + 1)
    max_workers = 16
    for i in indices:
        # open(f"jitter_hstp/diff_{i}.csv", "w").close()
        pass

    # indices = range(1, 10 + 1)
    # max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(run_simulation, indices)