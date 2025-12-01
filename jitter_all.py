import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

from circuit_sim import circuit_sim

lsq_list = [2.4, 3.0, 3.5, 5.29]
ic_list = [72.8, 65.4, 60.8, 50.0]
lic_list = [lsq * ic for lsq, ic in zip(lsq_list, ic_list)]
vb_list = [0.25e-3, 0.50e-3]
ibf_list = [0.4, 0.5]
bc_list = [1, 2]
tot_combi = len(lic_list) * len(vb_list) * len(ibf_list) * len(bc_list)
indices = range(1, tot_combi + 1)

def calc_nominal_ic_uA(Ic_uA, L_pH):
    f_q = 2.06783385*(10**(-15))
    Ic_A = Ic_uA*10**(-6)
    L_H = L_pH*10**(-12)
    x = (L_H * Ic_A) / f_q
    result = (0.5263*x**6 -2.3279*x**5 + 3.4434*x**4 - 1.0023*x**3 - 2.5876*x**2 + 3.341*x)*Ic_A
    return result*10**6

def sB2iD(s):
    result = 0
    length = len(s)
    for i in range(length):
        bit = int(s[length - 1 - i])
        result += bit * (2 ** i)
    return result

def strParse(index, tot_combi):
    offset = len(bin(tot_combi))
    str_bin = bin(index-1)[2:].zfill(offset-3)
    lic = lic_list[sB2iD(str_bin[0:2])]
    vb = vb_list[sB2iD(str_bin[2])]
    ibf = ibf_list[sB2iD(str_bin[3])]
    bc = bc_list[sB2iD(str_bin[4])]
    Ic = ic_list[sB2iD(str_bin[0:2])]
    Lsq = lsq_list[sB2iD(str_bin[0:2])]
    return lic, vb, ibf, bc, Ic, Lsq

def run_simulation(i):
    lic, vb, ibf, bc, Ic, Lsq = strParse(i, tot_combi)
    time.sleep(i*0.2)
    print(f"Start simulation {i} with Ic={Ic:.2f}uA, LIc={lic:.2f}uA*pH, Vb={vb*(10**3):.2f}mV, Ibfactor={ibf}, Betac={bc}")
    time.sleep(12)
    
    sim_con = circuit_sim("jtl_base.cir")
    sim_con.new_make_jtl2(Ic, lic, vb, ibf, bc)
    sim_con.sim()
    netlist_file = f"jitter_all/jitter_{i}.cir"
    sim_con.output_netlist(netlist_file)

    diff_file = f"jitter_all/diff_{i}.csv"
    # open(diff_file, "w").close()
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
    max_workers = tot_combi

    # indices = range(1, 10 + 1)
    # max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(run_simulation, indices)