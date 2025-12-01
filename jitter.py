import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

from circuit_sim import circuit_sim

lic = 3.5 * 60.8
ic_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
vb = 0.50e-3
ibf_list = [0.4, 0.5]
bc_list = [1, 2]
tot_combi = len(ic_list) * len(ibf_list) * len(bc_list)
indices = range(1, tot_combi + 1)

def calc_nominal_ic_uA(Ic_uA, L_pH):
    f_q = 2.06783385*(10**(-15))
    Ic_A = Ic_uA*10**(-6)
    L_H = L_pH*10**(-12)
    x = (L_H * Ic_A) / f_q
    result = (0.5263*x**6 -2.3279*x**5 + 3.4434*x**4 - 1.0023*x**3 - 2.5876*x**2 + 3.341*x)*Ic_A
    return result*10**6

def strParse(index, tot_combi):
    ibf_tag = 0 if index <= (tot_combi/2) else 1
    bc_tag = 0 if (index <= (tot_combi/4) or index > (tot_combi*3/4)) else 1
    ibf = ibf_list[ibf_tag]
    bc = bc_list[bc_tag]
    Ic = ic_list[(index % len(ic_list)) - 1]
    return ibf, bc, Ic

def run_simulation(i):
    ibf, bc, Ic = strParse(i, tot_combi)
    time.sleep(i*0.2)
    print(f"Start simulation {i} with Ic={Ic:.2f}uA, LIc={lic:.2f}uA*pH, Vb={vb*(10**3):.2f}mV, Ibfactor={ibf}, Betac={bc}")
    time.sleep(12)
    
    sim_con = circuit_sim("jtl_base.cir")
    sim_con.new_make_jtl2(Ic, lic, vb, ibf, bc)
    sim_con.sim()
    netlist_file = f"jitter/jitter_{i}.cir"
    sim_con.output_netlist(netlist_file)

    diff_file = f"jitter/diff_{i}.csv"
    open(diff_file, "w").close()
    sim_con.calc_jitter(
        ["P(B1|X1|X2|X2)", "P(B2|X1|X2|X2)"],
        ["P(B1|X2|X6|X7)", "P(B2|X2|X6|X7)"],
        # ["P(B1|X1|X1|X35)", "P(B2|X1|X1|X35)"],
        # ["P(B1|X2|X20|X35)", "P(B2|X2|X20|X35)"],
        40, diff_file,
        # try_count=1000, #1h28m
        # try_count=5000, #
        try_count=10000, #38h13m
        index=i
    )

    data = pd.read_csv(diff_file)
    data[0] = data[0].apply(lambda x: 0 if abs(x) <= 1e-20 else x)
    data.to_csv(diff_file, index=False, header=False)

if __name__ == "__main__":
    indices = range(1, tot_combi + 1)
    # max_workers = tot_combi
    max_workers = 20

    # indices = range(1, 10 + 1)
    # max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(run_simulation, indices)