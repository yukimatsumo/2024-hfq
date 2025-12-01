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

lsq_list = [2.4, 3.0, 3.5, 5.29]
ic_list = [72.8, 65.4, 60.8, 50.0]
lic_list = [lsq * ic for lsq, ic in zip(lsq_list, ic_list)]
vb_list = [0.25e-3, 0.5e-3]
ibf_list = [0.4, 0.5]
bc_list = [1, 2]
tot_combi = len(lic_list) * len(vb_list) * len(ibf_list) * len(bc_list)
indices = range(1, tot_combi + 1)
for i in indices:
    lic, vb, ibf, bc, Ic, Lsq = strParse(i, tot_combi)
    Icn = calc_nominal_ic_uA(Ic, Lsq)
    print(f"lic : {lic:.2f}, vb : {vb*1e3:.2f}, ibf : {ibf}, bc : {bc}, Ic: {Ic}, Lsq: {Lsq:.2f}, Icn: {Icn:.3f}")