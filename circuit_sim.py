import pandas as pd
from subprocess import PIPE
import subprocess
import re
import math
import io
import json
import warnings
from tqdm import tqdm

class circuit_sim():
    def __init__(self, file):
        try:
            with open(file, 'r', encoding='utf-8') as file:
                self.netlist = file.read()
        except FileNotFoundError:
            print("ファイルが見つかりませんでした。")
        self.result = None
    
    def sim(self):
        result = subprocess.run(["josim-cli", "-i"], input=self.netlist, stdout=PIPE, stderr=PIPE, text=True)
        first_split = re.split(r'100%\s*Formatting\s*Output',result.stdout)
        if len(first_split) == 2:
            split_data = first_split[1]
        else:
            print(result.stdout)
            raise ValueError("\033[31m" + result.stderr + "\033[0m")
        self.result = pd.read_csv(io.StringIO(split_data),index_col=0,header=0, sep=r'\s+') if split_data is not None else None

    
    def change_timing(self, place:int, diff:int) -> str:
        net_lines = self.netlist.split("\n")
        index = 8*place - 3
    
        for l,line in enumerate(net_lines):
            if  "forPython" in line:
                change_line = net_lines[l+1].split()    
                for i in [index,index+2,index+4,index+6]:
                    new_time = str(int(re.sub(r"[^\d.]", "", change_line[i]))+diff) + "ps"
                    change_line[i] = new_time
                new_line = " ".join(change_line)
                net_lines[l+1] = new_line
                self.netlist = "\n".join(net_lines)
    
        return self.netlist
    
    def check_timing(self, time:float, compare_time:float, time_diff:float) -> bool:
        if abs(time - compare_time) > time_diff:
            return False
        return True
    
    def get_switch_timing(self, param:list[str]) -> pd.DataFrame:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning, message="The behavior of DataFrame concatenation.*")

            if self.result is None:
                self.sim()
            if len(param) != 2:
                raise ValueError("Decide two 0-junction to detect switch!!")
        
            p = math.pi
            p2 = math.pi * 2
            srs = pd.DataFrame()
            column_name = "+".join(param)
            try:
                srs[column_name] = self.result[param[0]] + self.result[param[1]]
            except KeyError as e:
                print(f"Error: The key '{e.args[0]}' does not exist in the DataFrame.")
                exit()
    
            
            res_df = pd.DataFrame([{'time':None, 'phase':None, 'element':None}])
            init_phase = srs[( srs.index > 200e-12 ) & ( srs.index < 300e-12 )][column_name].mean()   
            judge_phase = init_phase + p          
            srs = srs[srs.index > 300e-12]
            flag = 0
            
            for  i in range(len(srs)-1):
                if (((srs[column_name].iat[i]) - (flag*p2 + judge_phase)) * (srs[column_name].iat[i+1] - (flag*p2 + judge_phase)) )< 0:
                    flag = flag + 1
                    res_df = pd.concat([res_df, pd.DataFrame([{'time':srs.index[i], 'phase':flag, 'element':column_name}])], ignore_index=True)
                elif (srs[column_name].iat[i] - ((flag-1)*p2 + judge_phase)) * ((srs[column_name].iat[i+1]) - ((flag-1)*p2 + judge_phase)) < 0:
                    flag = flag - 1
                    res_df = pd.concat([res_df, pd.DataFrame([{'time':srs.index[i], 'phase':flag, 'element':column_name}])], ignore_index=True)

            return res_df[1:]
            
    def get_jj_jitter(self, jitter_start_factor, jitter_end_factor, try_count = 100) -> float:
        for i in range(try_count):
            self.sim()
            if self.result is not None:
                break

    def add_jitter(self, factors:list[str], add_string):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        pattern_R = re.compile(r"R\d+")
        pattern_B = re.compile(r"B\d+")
        for factor in factors:
            for index, line in enumerate(original_lines):
                if factor in line:
                    while not ".ends" in original_lines[index+1]:
                        if pattern_R.search(original_lines[index+1]) or pattern_B.search(original_lines[index+1]):
                            new_netlist[index+1] = original_lines[index+1] + " " + add_string
                        index += 1
                    break
        self.netlist = "\n".join(new_netlist)
        return new_netlist

    def change_indactance(self, factors:list[str], pH_values:list[str]):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        pattern = re.compile(r"L\d+")
        for factor in factors:
            for index, line in enumerate(original_lines):
                if factor in line:
                    inner_index = 0
                    while not ".ends" in original_lines[index+1]:
                        if pattern.search(original_lines[index+1]):
                            #new_netlist[index+1] = re.sub(r'\d+pH', '', original_lines[index+1]) + " " + pH_values[inner_index]

                            new_netlist[index+1] = " ".join(original_lines[index+1].split()[0:3]) + " " + pH_values[inner_index]
                            inner_index += 1
                            if inner_index == len(pH_values):
                                break
                        index += 1
                    break
        self.netlist = "\n".join(new_netlist)
        return new_netlist
    
    def change_resistor(self, factors:list[str], r_values:list[str]):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        pattern = re.compile(r"R\d+")
        for factor in factors:
            for index, line in enumerate(original_lines):
                if factor in line:
                    inner_index = 0
                    while not ".ends" in original_lines[index+1]:
                        if pattern.search(original_lines[index+1]):
                            #new_netlist[index+1] = re.sub(r'\d+ohm', '', original_lines[index+1]) + " " + r_values[inner_index]

                            new_netlist[index+1] = " ".join(original_lines[index+1].split()[0:3]) + " " + r_values[inner_index]
                            inner_index += 1
                            if inner_index == len(r_values):
                                break
                        index += 1
                    break
        self.netlist = "\n".join(new_netlist)
        return new_netlist

    

    def output_netlist(self, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(self.netlist)

    def output_sim_result(self, file_name):
        if self.result is None:
            self.sim()
        self.result.to_csv(file_name, sep=",")
    
    def calc_indactance_pH(self, Icn, L_squid):
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Icn)*(1/4)*f_q - L_squid
        return round(L_loop*10**12,4)

    def new_calc_indactance_pH(self, Icn, L_squid):
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Icn)*(1/4)*f_q - L_squid
        return round(L_loop*10**12,4)

    # L_squid_pH is not half of L_squid
    def calc_storage_loop_indactance_pH(self, Ic_uA, L_squid_1_pH, L_squid_2_pH):
        Ic = Ic_uA*10**(-6)
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Ic)*(3/4)*f_q - (L_squid_1_pH/4)*10**-12 - (L_squid_2_pH/4)*10**-12
        return L_loop*10**12
    
    def calc_propagate_loop_indactance_pH(self, Ic_uA, L_squid_1_pH, L_squid_2_pH):
        Ic = Ic_uA*10**(-6)
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Ic)*(1/4)*f_q - (L_squid_1_pH/4)*10**-12 - (L_squid_2_pH/4)*10**-12
        return L_loop*10**12
    
    def calc_clock_loop_indactance_pH(self, Ic_uA, L_squid_1_pH, L_squid_2_pH, L_squid_escape_pH, L_squid_phase_pH):
        Ic = Ic_uA*10**(-6)
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Ic)*(1/4)*f_q - (L_squid_1_pH/4)*10**-12 - (L_squid_2_pH/4)*10**-12 - (L_squid_escape_pH/2)*10**-12 - (L_squid_phase_pH/2)*10**-12
        return L_loop*10**12
    
    def calc_clock_loop_indactance_total(self, Ic_uA, L_squid_1_pH, L_squid_2_pH, L_squid_escape_pH, L_squid_phase_pH):
        Ic = Ic_uA*10**(-6)
        f_q = 2.06783385*(10**(-15))
        L_loop = (1/Ic)*(1/4)*f_q 
        return L_loop*10**12

    def calc_resistor(self, area, Icrit, betac=1):
        if betac == 1:
            Bc_const = 0.773*10**(-3)
        else:
            Bc_const = 1.13*10**(-3)
        R = Bc_const/(area*Icrit)
        return round(R,2)
    
    def new_calc_resistor(self, Ic_uA, betac=1):
        Ic_A = Ic_uA*10**(-6)
        if betac == 1:
            Bc_const = 0.773*10**(-3)
        else:
            Bc_const = 1.13*10**(-3)
        R = Bc_const/Ic_A
        return R

    # input Ic_A, L_squid_H
    def nominal_ic(self, L, Ic):
        x = (L*2 * Ic) / (2.07*10**(-15))
        result = (0.5263*x**6 -2.3279*x**5 + 3.4434*x**4 - 1.0023*x**3 - 2.5876*x**2 + 3.341*x)*Ic
        return result

    def new_nominal_ic_uA(self,Ic_uA,L_pH):
        f_q = 2.06783385*(10**(-15))
        Ic_A = Ic_uA*10**(-6)
        L_H = L_pH*10**(-12)
        x = (L_H * Ic_A) / f_q
        result = (0.5263*x**6 -2.3279*x**5 + 3.4434*x**4 - 1.0023*x**3 - 2.5876*x**2 + 3.341*x)*Ic_A
        return result*10**6
    
    
    def calc_bias_resistor(self, Icn, Vb, factor=0.4):
        # R = Vb/(Icn*0.4*2)
        R = Vb/(Icn*factor*2)
        return round(R,2)
    
    def new_calc_bias_resistor(self, Icn_uA_1,Icn_uA_2, Vb, factor=0.4):
        Icn_A_1 = Icn_uA_1*10**(-6)
        Icn_A_2 = Icn_uA_2*10**(-6)
        # R = Vb/((Icn_A_1 + Icn_A_2)*0.4)
        R = Vb/((Icn_A_1 + Icn_A_2)*factor)
        return round(R,2)
    
    def output_netlist(self, filename):
        with open(filename, 'w', encoding='utf-8', newline='\n') as f:
            f.write(self.netlist)   
    
    def change_Ic(self, factor:str, Ic_area_values:str):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if factor in line:
                while not ".ends" in original_lines[index+1]:
                    if "B1" in original_lines[index+1] or "B2" in original_lines[index+1]:
                        new_netlist[index+1] = " ".join(original_lines[index+1].split()[0:4]) + " area=" + Ic_area_values
                    index += 1
                break
        self.netlist = "\n".join(new_netlist)
        return new_netlist
    
    def change_netlist(self, Ic_area:float,Icrit:float, L_squid:float, bias_voltage:float):
        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid_test", str(Ic_area))
        Icn = self.nominal_ic(L_squid, Ic_area*Icrit)
        print("Icn:",Icn)
        L_loop = self.calc_indactance_pH(Ic_area*Icrit, L_squid)
        L_loop = round(L_loop,3)
        print("L_loop:",L_loop)
        self.change_indactance(["jtl_squid"],[str(L_squid*10**12)+"pH",str(L_squid*10**12)+"pH"])
        self.change_indactance(["jtl_base"],["1pH", str(L_loop/2-1)+"pH", str(L_loop)+"pH",str(L_loop/2)+"pH"])
        self.change_indactance(["jtl_base_test"],["1pH", str(L_loop/2-1)+"pH", str(L_loop)+"pH",str(L_loop/2)+"pH"])
        self.change_indactance(["DFF_"],["1pH", str(L_loop/2-1)+"pH", str(L_loop)+"pH","1pH",str(L_loop*3 - 2)+"pH","1pH",str(L_loop)+"pH",str(L_loop/2)+"pH","1pH",str(L_loop/2-1)+"pH","1pH","1pH"])

        new_resistor = self.calc_resistor(Ic_area, Icrit,2)
        print("new_resistor:",new_resistor)
        resistor_list = [str(new_resistor)+"ohm", str(new_resistor)+"ohm"]
        self.change_resistor(["jtl_squid"],resistor_list)
        self.change_resistor(["jtl_squid_test"],resistor_list)
        bias_R = self.calc_bias_resistor(Icn, bias_voltage)
        print("bias_R:",bias_R)
        self.change_resistor(["jtl_base"],[str(bias_R)+"ohm"])
        self.change_resistor(["jtl_base_test"],[str(bias_R)+"ohm"])
        return self.netlist
    
    def make_jtl(self, Ic_area:float, Icrit:float, bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 0.6/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid_test", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid_test"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid_test"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base","jtl_base_test"],[str(bias_R)+"ohm"])
        self.change_indactance(["jtl_base","jtl_base_test"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])

        print(self.netlist)

        self.param_dic = param_dic
        return self.netlist
    
    def make_jtl2(self, Ic_area:float, Icrit:float, bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 0.9/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid_test", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid_test"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid_test"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base","jtl_base_test"],[str(bias_R)+"ohm"])
        self.change_indactance(["jtl_base","jtl_base_test"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])

        print(self.netlist)

        self.param_dic = param_dic
        return self.netlist
    
    def make_jtl3(self, Ic_area:float, Icrit:float,  bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 1.2/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid_test", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid_test"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid_test"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base","jtl_base_test"],[str(bias_R)+"ohm"])
        self.change_indactance(["jtl_base","jtl_base_test"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])

        print(self.netlist)

        self.param_dic = param_dic
        return self.netlist
    
    def make_dff(self, Ic_area:float, Icrit:float, bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 0.6/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid2", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid2"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid2"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base"],[str(bias_R)+"ohm"])
        self.change_resistor(["DFF_"],[str(bias_R)+"ohm",str(bias_R)+"ohm",str(bias_R)+"ohm"])


        dff_squid_param = {}
        dff_squid_param["Ic_area"] = Ic_area*1.5
        dff_squid_param["L_squid_pH"] = round(0.6/dff_squid_param["Ic_area"],3)
        dff_squid_param["R_squid_O"] = self.calc_resistor(dff_squid_param["Ic_area"], Icrit,2)
        print("dff_squid_param:",dff_squid_param)

        self.change_Ic("dff_squid1", str(dff_squid_param["Ic_area"]))
        self.change_resistor(["dff_squid1"],[str(dff_squid_param["R_squid_O"])+"ohm", str(dff_squid_param["R_squid_O"])+"ohm"])
        self.change_indactance(["dff_squid1"],[str(dff_squid_param["L_squid_pH"])+"pH",str(dff_squid_param["L_squid_pH"])+"pH"])

        self.change_indactance(["jtl_base"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])


        DFF_inductances = {}
        DFF_inductances["L1"] = "1pH"
        DFF_inductances["L2"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L3"] = str(L_loop_pH)+"pH"
        DFF_inductances["L4"] = "1pH"
        DFF_inductances["L5"] = str(L_loop_pH*3 - 2)+"pH"
        DFF_inductances["L6"] = "1pH"
        DFF_inductances["L7"] = str(L_loop_pH)+"pH"
        DFF_inductances["L8"] = str(L_loop_pH/2)+"pH"
        DFF_inductances["L9"] = "1pH"
        DFF_inductances["L10"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L11"] = "1pH"
        DFF_inductances["L12"] = "1pH"
        DFF_inductances["L13"] = str(round(L_loop_pH - 3 - L_squid_pH*2 - 1.2,3))+"pH"
        print("DFF_inductances:",DFF_inductances)

        self.change_indactance(["DFF_"],[DFF_inductances["L1"],DFF_inductances["L2"],DFF_inductances["L3"],DFF_inductances["L4"],DFF_inductances["L5"],DFF_inductances["L6"],DFF_inductances["L7"],DFF_inductances["L8"],DFF_inductances["L9"],DFF_inductances["L10"],DFF_inductances["L11"],DFF_inductances["L12"],DFF_inductances["L13"]])


        #print(self.netlist)

        self.param_dic = param_dic

        
        return self.netlist
    
    def new_make_jtl(self, Ic_uA:float, LIc:float, bias_voltage:float):
        f_q = 2.06783385*(10**(-15))

        X1_Ic_uA = Ic_uA
        X1_Lsquid_pH = LIc/X1_Ic_uA

        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)
        print("L_propagete_loop_pH_1:",L_propagete_loop_pH_1)
        L1_pH = round(L_propagete_loop_pH_1 * (10/84),3)
        L2_pH = round(L_propagete_loop_pH_1 * (42/84),3)
        L3_pH = round(L_propagete_loop_pH_1 * (32/84),3)

        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,2),3)
        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage),3)


        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("jtl_squid_test", str(X1_Ic_uA/100))

        
        self.change_resistor(["jtl_squid","jtl_squid_test"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid_test"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        
        self.change_resistor(["jtl_base","jtl_base_test"],[str(R1)+"ohm"])
        self.change_indactance(["jtl_base","jtl_base_test"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L3_pH)+"pH"])



        #print(self.netlist)
        #print((bias_voltage**2/R1)*33+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2)
        #power = (bias_voltage**2/R1)*33+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2
        return 

    def new_make_jtl2(self, Ic_uA:float, LIc:float, bias_voltage:float=0.5*10**(-3), ibfactor:float=0.4, betac:float=2):
        f_q = 2.06783385*(10**(-15))

        X1_Ic_uA = Ic_uA
        X1_Lsquid_pH = LIc/X1_Ic_uA

        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)
        # print("L_propagete_loop_pH_1:",L_propagete_loop_pH_1)
        L1_pH = round(L_propagete_loop_pH_1 * (10/84),3)
        L2_pH = round(L_propagete_loop_pH_1 * (42/84),3)
        L3_pH = round(L_propagete_loop_pH_1 * (32/84),3)

        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,betac=betac),3)
        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage,ibfactor),3)


        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("jtl_squid_test", str(X1_Ic_uA/100))

        
        self.change_resistor(["jtl_squid","jtl_squid_test"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid_test"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        
        self.change_resistor(["jtl_base","jtl_base_test"],[str(R1)+"ohm"])
        self.change_indactance(["jtl_base","jtl_base_test"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L3_pH)+"pH"])

        self.change_bias_voltage(bias_voltage)
        #print(self.netlist)
        #print((bias_voltage**2/R1)*33+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2)
        #power = (bias_voltage**2/R1)*33+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2
        return 
    

    # Ic_uA : 50uA  LIc 50uA*2.4pH, not half of L_squid
    def new_make_dff(self, Ic_uA:float, LIc:float, bias_voltage:float):
        f_q = 2.06783385*(10**(-15))
        
        param_dic = {}
        
        if Ic_uA == 0:
            return None
        L_squid_pH = LIc/Ic_uA
        print(L_squid_pH)
        param_dic["L_squid_pH"] = L_squid_pH

        X1_Ic_uA = Ic_uA
        X2_Ic_uA = Ic_uA*72/55
        X3_Ic_uA = Ic_uA*54/55
        X4_Ic_uA = Ic_uA
        X5_Ic_uA = Ic_uA
        X6_Ic_uA = 200
        X7_Ic_uA = Ic_uA

        X1_Ic_uA = round(X1_Ic_uA,3)
        X2_Ic_uA = round(X2_Ic_uA,3)
        X3_Ic_uA = round(X3_Ic_uA,3)
        X4_Ic_uA = round(X4_Ic_uA,3)
        X5_Ic_uA = round(X5_Ic_uA,3)
        X6_Ic_uA = round(X6_Ic_uA,3)
        X7_Ic_uA = round(X7_Ic_uA,3)

        print(X2_Ic_uA)

        X1_Lsquid_pH = LIc/X1_Ic_uA
        X2_Lsquid_pH = LIc/X2_Ic_uA
        X3_Lsquid_pH = LIc/X3_Ic_uA
        X4_Lsquid_pH = LIc/X4_Ic_uA
        X5_Lsquid_pH = LIc/X5_Ic_uA
        X6_Lsquid_pH = LIc/X7_Ic_uA
        X7_Lsquid_pH = LIc/X7_Ic_uA

        X1_Lsquid_pH = round(X1_Lsquid_pH,3)
        X2_Lsquid_pH = round(X2_Lsquid_pH,3)
        X3_Lsquid_pH = round(X3_Lsquid_pH,3)
        X4_Lsquid_pH = round(X4_Lsquid_pH,3)
        X5_Lsquid_pH = round(X5_Lsquid_pH,3)
        X6_Lsquid_pH = round(X6_Lsquid_pH,3)
        X7_Lsquid_pH = round(X7_Lsquid_pH,3)

        print("X1_Lsquid_pH:",X1_Lsquid_pH)
        print("X2_Lsquid_pH:",X2_Lsquid_pH)
        print("X3_Lsquid_pH:",X3_Lsquid_pH)
        print("X4_Lsquid_pH:",X4_Lsquid_pH)
        print("X5_Lsquid_pH:",X5_Lsquid_pH)
        print("X6_Lsquid_pH:",X6_Lsquid_pH)
        print("X7_Lsquid_pH:",X7_Lsquid_pH)
        
        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)
        print("L_propagete_loop_pH_1:",L_propagete_loop_pH_1)

        print(self.calc_clock_loop_indactance_total(X6_Ic_uA, X5_Lsquid_pH, X4_Lsquid_pH, X6_Lsquid_pH, X7_Lsquid_pH))

        L1_pH = L_propagete_loop_pH_1 * (10/84)
        L2_pH = L_propagete_loop_pH_1 * (42/84)

        L1_pH = round(L1_pH,3)
        L2_pH = round(L2_pH,3)

        L_propagete_loop_pH_2 = self.calc_propagate_loop_indactance_pH(X2_Ic_uA, X1_Lsquid_pH, X2_Lsquid_pH)
        print("L_propagete_loop_pH_2:",L_propagete_loop_pH_2)
        L3_pH = L_propagete_loop_pH_2 
        L3_pH = round(L3_pH,3)

        L_storage_loop_pH = self.calc_storage_loop_indactance_pH(Ic_uA, X2_Lsquid_pH, X3_Lsquid_pH)
        print("L_storage_loop_pH:",L_storage_loop_pH)

        L4_pH = L_storage_loop_pH * (26/32)
        L5_pH = L_storage_loop_pH * (5/32)
        L6_pH = L_storage_loop_pH * (1/32)

        L4_pH = round(L4_pH,3)
        L5_pH = round(L5_pH,3)
        L6_pH = round(L6_pH,3)

        L_propagete_loop_pH_4 = self.calc_propagate_loop_indactance_pH(X4_Ic_uA, X3_Lsquid_pH, X4_Lsquid_pH)
        print("L_propagete_loop_pH_4:",L_propagete_loop_pH_4)

        L7_pH = L_propagete_loop_pH_4
        L8_pH = L_propagete_loop_pH_4*(32/84)
        L7_pH = round(L7_pH,3)
        L8_pH = round(L8_pH,3)

        L_propagete_loop_pH_5 = self.calc_propagate_loop_indactance_pH(X5_Ic_uA, X5_Lsquid_pH, X5_Lsquid_pH)
        print("L_propagete_loop_pH_5:",L_propagete_loop_pH_5)

        L9_pH = L_propagete_loop_pH_5 * (10/84)
        L10_pH = L_propagete_loop_pH_5 * (42/84)
        L9_pH = round(L9_pH,3)
        L10_pH = round(L10_pH,3)

        L_clock_loop_pH = self.calc_clock_loop_indactance_pH(X3_Ic_uA, X5_Lsquid_pH, X4_Lsquid_pH, X6_Lsquid_pH, X7_Lsquid_pH)
        print("L_clock_loop_pH:",L_clock_loop_pH)

        L_clock_loop_pH_remain = L_clock_loop_pH - L6_pH 
        L11_pH = L_clock_loop_pH_remain * (7/9)
        L12_pH = L_clock_loop_pH_remain * (1/9)
        L13_pH = L_clock_loop_pH_remain * (1/9)
        L11_pH = round(L11_pH,3)
        L12_pH = round(L12_pH,3)
        L13_pH = round(L13_pH,3)

        print("L1_pH:",L1_pH)
        print("L2_pH:",L2_pH)
        print("L3_pH:",L3_pH)
        print("L4_pH:",L4_pH)
        print("L5_pH:",L5_pH)
        print("L6_pH:",L6_pH)
        print("L7_pH:",L7_pH)
        print("L8_pH:",L8_pH)
        print("L9_pH:",L9_pH)
        print("L10_pH:",L10_pH)
        print("L11_pH:",L11_pH)
        print("L12_pH:",L12_pH)
        print("L13_pH:",L13_pH)

        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        X2_Icn_uA = round(self.new_nominal_ic_uA(X2_Ic_uA,X2_Lsquid_pH),3)
        X3_Icn_uA = round(self.new_nominal_ic_uA(X3_Ic_uA,X3_Lsquid_pH),3)
        X4_Icn_uA = round(self.new_nominal_ic_uA(X4_Ic_uA,X4_Lsquid_pH),3)
        X5_Icn_uA = round(self.new_nominal_ic_uA(X5_Ic_uA,X5_Lsquid_pH),3)
        print("X1_Icn_uA:",X1_Icn_uA)
        print("X2_Icn_uA:",X2_Icn_uA)
        print("X3_Icn_uA:",X3_Icn_uA)
        print("X4_Icn_uA:",X4_Icn_uA)
        print("X5_Icn_uA:",X5_Icn_uA)

        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage),3)
        R2 = round(self.new_calc_bias_resistor(X2_Icn_uA,X3_Icn_uA,bias_voltage),3)
        R3 = round(self.new_calc_bias_resistor(X5_Icn_uA,X5_Icn_uA,bias_voltage),3)
        print("R1:",R1)
        print("R2:",R2)
        print("R3:",R3)

        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,2),3)
        print("shunt_1:",shunt_1)
        shunt_2 = round(self.new_calc_resistor(X2_Ic_uA,2),3)
        shunt_3 = round(self.new_calc_resistor(X3_Ic_uA,2),3)
        shunt_4 = round(self.new_calc_resistor(X4_Ic_uA,2),3)
        shunt_5 = round(self.new_calc_resistor(X5_Ic_uA,2),3)
        shunt_6 = round(self.new_calc_resistor(X6_Ic_uA,2),3)
        
        print("shunt_2:",shunt_2)
        print("shunt_3:",shunt_3)
        print("shunt_4:",shunt_4)
        print("shunt_5:",shunt_5)
        print("shunt_6:",shunt_6)

        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("X1_squid", str(X1_Ic_uA/100))
        self.change_Ic("X2_squid", str(X2_Ic_uA/100))
        self.change_Ic("X3_squid", str(X3_Ic_uA/100))
        self.change_Ic("X4_squid", str(X4_Ic_uA/100))
        self.change_Ic("X5_squid", str(X5_Ic_uA/100))
        self.change_Ic("X6_squid", str(X6_Ic_uA/100))
        self.change_Ic("X7_squid", str(X7_Ic_uA/100))

        self.change_resistor(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_resistor(["X2_squid"],[str(shunt_2)+"ohm", str(shunt_2)+"ohm"])
        self.change_resistor(["X3_squid"],[str(shunt_3)+"ohm", str(shunt_3)+"ohm"])

        self.change_indactance(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X2_squid"],["0.00001pH",str(X2_Lsquid_pH/2)+"pH",str(X2_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X3_squid"],["0.00001pH",str(X3_Lsquid_pH/2)+"pH",str(X3_Lsquid_pH/2)+"pH"])
        
        self.change_indactance(["jtl_base"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L8_pH)+"pH"])
        self.change_resistor(["jtl_base"],[str(R1)+"ohm"])

        self.change_resistor(["DFF_"],[str(R1)+"ohm",str(R2)+"ohm",str(R3)+"ohm"])
        self.change_indactance(["DFF_"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L3_pH)+"pH",str(L4_pH)+"pH",str(L5_pH)+"pH",str(L6_pH)+"pH",str(L7_pH)+"pH",str(L8_pH)+"pH",str(L9_pH)+"pH",str(L10_pH)+"pH",str(L11_pH)+"pH",str(L12_pH)+"pH",str(L13_pH)+"pH"])

        #print(self.netlist)
        print((bias_voltage**2/R1)+(bias_voltage**2/R2)+(bias_voltage**2/R3))
        power = (bias_voltage**2/R1)+(bias_voltage**2/R2)+(bias_voltage**2/R3)
        return X1_Icn_uA, power
    
    def new_make_dff2(self, Ic_uA:float, LIc:float, bias_voltage:float=0.5*10**(-3), ibfactor:float=0.4, betac:float=2):
        f_q = 2.06783385*(10**(-15))
        
        param_dic = {}
        
        if Ic_uA == 0:
            return None
        L_squid_pH = LIc/Ic_uA
        param_dic["L_squid_pH"] = L_squid_pH

        X1_Ic_uA = Ic_uA
        X2_Ic_uA = Ic_uA*72/55
        X3_Ic_uA = Ic_uA*54/55
        X4_Ic_uA = Ic_uA
        X5_Ic_uA = Ic_uA
        X6_Ic_uA = 200
        X7_Ic_uA = Ic_uA

        X1_Ic_uA = round(X1_Ic_uA,3)
        X2_Ic_uA = round(X2_Ic_uA,3)
        X3_Ic_uA = round(X3_Ic_uA,3)
        X4_Ic_uA = round(X4_Ic_uA,3)
        X5_Ic_uA = round(X5_Ic_uA,3)
        X6_Ic_uA = round(X6_Ic_uA,3)
        X7_Ic_uA = round(X7_Ic_uA,3)


        X1_Lsquid_pH = LIc/X1_Ic_uA
        X2_Lsquid_pH = LIc/X2_Ic_uA
        X3_Lsquid_pH = LIc/X3_Ic_uA
        X4_Lsquid_pH = LIc/X4_Ic_uA
        X5_Lsquid_pH = LIc/X5_Ic_uA
        X6_Lsquid_pH = LIc/X7_Ic_uA
        X7_Lsquid_pH = LIc/X7_Ic_uA

        X1_Lsquid_pH = round(X1_Lsquid_pH,3)
        X2_Lsquid_pH = round(X2_Lsquid_pH,3)
        X3_Lsquid_pH = round(X3_Lsquid_pH,3)
        X4_Lsquid_pH = round(X4_Lsquid_pH,3)
        X5_Lsquid_pH = round(X5_Lsquid_pH,3)
        X6_Lsquid_pH = round(X6_Lsquid_pH,3)
        X7_Lsquid_pH = round(X7_Lsquid_pH,3)

        
        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)


        L1_pH = L_propagete_loop_pH_1 * (10/84)
        L2_pH = L_propagete_loop_pH_1 * (42/84)

        L1_pH = round(L1_pH,3)
        L2_pH = round(L2_pH,3)

        L_propagete_loop_pH_2 = self.calc_propagate_loop_indactance_pH(X2_Ic_uA, X1_Lsquid_pH, X2_Lsquid_pH)
        L3_pH = L_propagete_loop_pH_2 
        L3_pH = round(L3_pH,3)

        L_storage_loop_pH = self.calc_storage_loop_indactance_pH(Ic_uA, X2_Lsquid_pH, X3_Lsquid_pH)

        L4_pH = L_storage_loop_pH * (26/32)
        L5_pH = L_storage_loop_pH * (5/32)
        L6_pH = L_storage_loop_pH * (1/32)

        L4_pH = round(L4_pH,3)
        L5_pH = round(L5_pH,3)
        L6_pH = round(L6_pH,3)

        L_propagete_loop_pH_4 = self.calc_propagate_loop_indactance_pH(X4_Ic_uA, X3_Lsquid_pH, X4_Lsquid_pH)

        L7_pH = L_propagete_loop_pH_4
        L8_pH = L_propagete_loop_pH_4*(32/84)
        L7_pH = round(L7_pH,3)
        L8_pH = round(L8_pH,3)

        L_propagete_loop_pH_5 = self.calc_propagate_loop_indactance_pH(X5_Ic_uA, X5_Lsquid_pH, X5_Lsquid_pH)

        L9_pH = L_propagete_loop_pH_5 * (10/84)
        L10_pH = L_propagete_loop_pH_5 * (42/84)
        L9_pH = round(L9_pH,3)
        L10_pH = round(L10_pH,3)

        L_clock_loop_pH = self.calc_clock_loop_indactance_pH(X3_Ic_uA, X5_Lsquid_pH, X4_Lsquid_pH, X6_Lsquid_pH, X7_Lsquid_pH)

        L_clock_loop_pH_remain = L_clock_loop_pH - L6_pH 
        L11_pH = L_clock_loop_pH_remain * (7/9)
        L12_pH = L_clock_loop_pH_remain * (1/9)
        L13_pH = L_clock_loop_pH_remain * (1/9)
        L11_pH = round(L11_pH,3)
        L12_pH = round(L12_pH,3)
        L13_pH = round(L13_pH,3)


        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        X2_Icn_uA = round(self.new_nominal_ic_uA(X2_Ic_uA,X2_Lsquid_pH),3)
        X3_Icn_uA = round(self.new_nominal_ic_uA(X3_Ic_uA,X3_Lsquid_pH),3)
        X4_Icn_uA = round(self.new_nominal_ic_uA(X4_Ic_uA,X4_Lsquid_pH),3)
        X5_Icn_uA = round(self.new_nominal_ic_uA(X5_Ic_uA,X5_Lsquid_pH),3)



        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage,ibfactor),3)
        R2 = round(self.new_calc_bias_resistor(X2_Icn_uA,X3_Icn_uA,bias_voltage,ibfactor),3)
        R3 = round(self.new_calc_bias_resistor(X5_Icn_uA,X5_Icn_uA,bias_voltage,ibfactor),3)


        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,betac=betac),3)
        shunt_2 = round(self.new_calc_resistor(X2_Ic_uA,betac=betac),3)
        shunt_3 = round(self.new_calc_resistor(X3_Ic_uA,betac=betac),3)
        shunt_4 = round(self.new_calc_resistor(X4_Ic_uA,betac=betac),3)
        shunt_5 = round(self.new_calc_resistor(X5_Ic_uA,betac=betac),3)
        shunt_6 = round(self.new_calc_resistor(X6_Ic_uA,betac=betac),3)
        

        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("X1_squid", str(X1_Ic_uA/100))
        self.change_Ic("X2_squid", str(X2_Ic_uA/100))
        self.change_Ic("X3_squid", str(X3_Ic_uA/100))
        self.change_Ic("X4_squid", str(X4_Ic_uA/100))
        self.change_Ic("X5_squid", str(X5_Ic_uA/100))
        self.change_Ic("X6_squid", str(X6_Ic_uA/100))
        self.change_Ic("X7_squid", str(X7_Ic_uA/100))

        self.change_resistor(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_resistor(["X2_squid"],[str(shunt_2)+"ohm", str(shunt_2)+"ohm"])
        self.change_resistor(["X3_squid"],[str(shunt_3)+"ohm", str(shunt_3)+"ohm"])

        self.change_indactance(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X2_squid"],["0.00001pH",str(X2_Lsquid_pH/2)+"pH",str(X2_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X3_squid"],["0.00001pH",str(X3_Lsquid_pH/2)+"pH",str(X3_Lsquid_pH/2)+"pH"])
        
        self.change_indactance(["jtl_base"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L8_pH)+"pH"])
        self.change_resistor(["jtl_base"],[str(R1)+"ohm"])

        self.change_resistor(["DFF_"],[str(R1)+"ohm",str(R2)+"ohm",str(R3)+"ohm"])
        self.change_indactance(["DFF_"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L3_pH)+"pH",str(L4_pH)+"pH",str(L5_pH)+"pH",str(L6_pH)+"pH",str(L7_pH)+"pH",str(L8_pH)+"pH",str(L9_pH)+"pH",str(L10_pH)+"pH",str(L11_pH)+"pH",str(L12_pH)+"pH",str(L13_pH)+"pH"])

        #print(self.netlist)
        power = (bias_voltage**2/R1)+(bias_voltage**2/R2)+(bias_voltage**2/R3)
        return X1_Icn_uA, power
    
    def new_make_dff3(self, Ic_uA:float, LIc:float, bias_voltage:float=0.5*10**(-3), ibfactor:float=0.4, betac:float=2):
        f_q = 2.06783385*(10**(-15))
        
        param_dic = {}
        
        if Ic_uA == 0:
            return None
        L_squid_pH = LIc/Ic_uA
        param_dic["L_squid_pH"] = L_squid_pH

        X1_Ic_uA = Ic_uA
        X2_Ic_uA = Ic_uA*72/55
        X3_Ic_uA = Ic_uA*54/55
        X4_Ic_uA = Ic_uA
        X5_Ic_uA = Ic_uA
        X6_Ic_uA = 200
        X7_Ic_uA = Ic_uA

        X1_Ic_uA = round(X1_Ic_uA,3)
        X2_Ic_uA = round(X2_Ic_uA,3)
        X3_Ic_uA = round(X3_Ic_uA,3)
        X4_Ic_uA = round(X4_Ic_uA,3)
        X5_Ic_uA = round(X5_Ic_uA,3)
        X6_Ic_uA = round(X6_Ic_uA,3)
        X7_Ic_uA = round(X7_Ic_uA,3)


        X1_Lsquid_pH = LIc/X1_Ic_uA
        X2_Lsquid_pH = LIc/X2_Ic_uA
        X3_Lsquid_pH = LIc/X3_Ic_uA
        X4_Lsquid_pH = LIc/X4_Ic_uA
        X5_Lsquid_pH = LIc/X5_Ic_uA
        X6_Lsquid_pH = LIc/X7_Ic_uA
        X7_Lsquid_pH = LIc/X7_Ic_uA

        X1_Lsquid_pH = round(X1_Lsquid_pH,3)
        X2_Lsquid_pH = round(X2_Lsquid_pH,3)
        X3_Lsquid_pH = round(X3_Lsquid_pH,3)
        X4_Lsquid_pH = round(X4_Lsquid_pH,3)
        X5_Lsquid_pH = round(X5_Lsquid_pH,3)
        X6_Lsquid_pH = round(X6_Lsquid_pH,3)
        X7_Lsquid_pH = round(X7_Lsquid_pH,3)

        
        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)


        L1_pH = L_propagete_loop_pH_1 * (10/84)
        L2_pH = L_propagete_loop_pH_1 * (42/84)

        L1_pH = round(L1_pH,3)
        L2_pH = round(L2_pH,3)

        L_propagete_loop_pH_2 = self.calc_propagate_loop_indactance_pH(X2_Ic_uA, X1_Lsquid_pH, X2_Lsquid_pH)
        L3_pH = L_propagete_loop_pH_2 
        L3_pH = round(L3_pH,3)

        L_storage_loop_pH = self.calc_storage_loop_indactance_pH(Ic_uA, X2_Lsquid_pH, X3_Lsquid_pH)

        L4_pH = L_storage_loop_pH * (26/32)
        L5_pH = L_storage_loop_pH * (5/32)
        L6_pH = L_storage_loop_pH * (1/32)

        L4_pH = round(L4_pH,3)
        L5_pH = round(L5_pH,3)
        L6_pH = round(L6_pH,3)

        L_propagete_loop_pH_4 = self.calc_propagate_loop_indactance_pH(X4_Ic_uA, X3_Lsquid_pH, X4_Lsquid_pH)

        L7_pH = L_propagete_loop_pH_4
        L8_pH = L_propagete_loop_pH_4*(32/84)
        L7_pH = round(L7_pH,3)
        L8_pH = round(L8_pH,3)

        L_propagete_loop_pH_5 = self.calc_propagate_loop_indactance_pH(X5_Ic_uA, X5_Lsquid_pH, X5_Lsquid_pH)

        L9_pH = L_propagete_loop_pH_5 * (10/84)
        L10_pH = L_propagete_loop_pH_5 * (42/84)
        L9_pH = round(L9_pH,3)
        L10_pH = round(L10_pH,3)

        L_clock_loop_pH = self.calc_clock_loop_indactance_pH(X3_Ic_uA, X5_Lsquid_pH, X4_Lsquid_pH, X6_Lsquid_pH, X7_Lsquid_pH)

        L_clock_loop_pH_remain = L_clock_loop_pH - L6_pH 
        L11_pH = L_clock_loop_pH_remain * (7/9)
        L12_pH = L_clock_loop_pH_remain * (1/9)
        L13_pH = L_clock_loop_pH_remain * (1/9)
        L11_pH = round(L11_pH,3)
        L12_pH = round(L12_pH,3)
        L13_pH = round(L13_pH,3)


        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        X2_Icn_uA = round(self.new_nominal_ic_uA(X2_Ic_uA,X2_Lsquid_pH),3)
        X3_Icn_uA = round(self.new_nominal_ic_uA(X3_Ic_uA,X3_Lsquid_pH),3)
        X4_Icn_uA = round(self.new_nominal_ic_uA(X4_Ic_uA,X4_Lsquid_pH),3)
        X5_Icn_uA = round(self.new_nominal_ic_uA(X5_Ic_uA,X5_Lsquid_pH),3)



        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage),3)
        R2 = round(self.new_calc_bias_resistor(X2_Icn_uA,X3_Icn_uA,bias_voltage),3)
        R3 = round(self.new_calc_bias_resistor(X5_Icn_uA,X5_Icn_uA,bias_voltage),3)

        self.change_bias_voltage(bias_voltage)


        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,2),3)
        shunt_2 = round(self.new_calc_resistor(X2_Ic_uA,2),3)
        shunt_3 = round(self.new_calc_resistor(X3_Ic_uA,2),3)
        shunt_4 = round(self.new_calc_resistor(X4_Ic_uA,2),3)
        shunt_5 = round(self.new_calc_resistor(X5_Ic_uA,2),3)
        shunt_6 = round(self.new_calc_resistor(X6_Ic_uA,2),3)
        

        """
        修正必要




        """
        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("X1_squid", str(X1_Ic_uA/100))
        self.change_Ic("X2_squid", str(X2_Ic_uA/100))
        self.change_Ic("X3_squid", str(X3_Ic_uA/100))
        self.change_Ic("X4_squid", str(X4_Ic_uA/100))
        self.change_Ic("X5_squid", str(X5_Ic_uA/100))
        self.change_Ic("X6_squid", str(X6_Ic_uA/100))
        self.change_Ic("X7_squid", str(X7_Ic_uA/100))

        self.change_resistor(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_resistor(["X2_squid"],[str(shunt_2)+"ohm", str(shunt_2)+"ohm"])
        self.change_resistor(["X3_squid"],[str(shunt_3)+"ohm", str(shunt_3)+"ohm"])

        self.change_indactance(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X2_squid"],["0.00001pH",str(X2_Lsquid_pH/2)+"pH",str(X2_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X3_squid"],["0.00001pH",str(X3_Lsquid_pH/2)+"pH",str(X3_Lsquid_pH/2)+"pH"])
        
        self.change_indactance(["jtl_base"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L8_pH)+"pH"])
        self.change_resistor(["jtl_base"],[str(R1)+"ohm"])

        self.change_resistor(["DFF_"],[str(R1)+"ohm",str(R2)+"ohm",str(R3)+"ohm",str(R3)+"ohm"])
        self.change_indactance(["DFF_"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L3_pH)+"pH",str(L4_pH)+"pH",str(L5_pH)+"pH",str(L6_pH)+"pH",str(L7_pH)+"pH",str(L8_pH)+"pH",str(L9_pH)+"pH",str(L10_pH)+"pH",str(L11_pH)+"pH",str(L12_pH)+"pH",str(L13_pH)+"pH"])

        #print(self.netlist)
        power = (bias_voltage**2/R1)*33+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2
        return X1_Icn_uA, power
    
    def new_make_dff_power(self, Ic_uA:float, LIc:float, bias_voltage:float):
        f_q = 2.06783385*(10**(-15))
        
        param_dic = {}
        
        if Ic_uA == 0:
            return None
        L_squid_pH = LIc/Ic_uA
        param_dic["L_squid_pH"] = L_squid_pH

        X1_Ic_uA = Ic_uA
        X2_Ic_uA = Ic_uA*72/55
        X3_Ic_uA = Ic_uA*54/55
        X4_Ic_uA = Ic_uA
        X5_Ic_uA = Ic_uA
        X6_Ic_uA = 200
        X7_Ic_uA = Ic_uA

        X1_Ic_uA = round(X1_Ic_uA,3)
        X2_Ic_uA = round(X2_Ic_uA,3)
        X3_Ic_uA = round(X3_Ic_uA,3)
        X4_Ic_uA = round(X4_Ic_uA,3)
        X5_Ic_uA = round(X5_Ic_uA,3)
        X6_Ic_uA = round(X6_Ic_uA,3)
        X7_Ic_uA = round(X7_Ic_uA,3)


        X1_Lsquid_pH = LIc/X1_Ic_uA
        X2_Lsquid_pH = LIc/X2_Ic_uA
        X3_Lsquid_pH = LIc/X3_Ic_uA
        X4_Lsquid_pH = LIc/X4_Ic_uA
        X5_Lsquid_pH = LIc/X5_Ic_uA
        X6_Lsquid_pH = LIc/X7_Ic_uA
        X7_Lsquid_pH = LIc/X7_Ic_uA

        X1_Lsquid_pH = round(X1_Lsquid_pH,3)
        X2_Lsquid_pH = round(X2_Lsquid_pH,3)
        X3_Lsquid_pH = round(X3_Lsquid_pH,3)
        X4_Lsquid_pH = round(X4_Lsquid_pH,3)
        X5_Lsquid_pH = round(X5_Lsquid_pH,3)
        X6_Lsquid_pH = round(X6_Lsquid_pH,3)
        X7_Lsquid_pH = round(X7_Lsquid_pH,3)

        
        L_propagete_loop_pH_1 = self.calc_propagate_loop_indactance_pH(X1_Ic_uA, X1_Lsquid_pH, X1_Lsquid_pH)
        L_propagete_loop_pH_1 = round(L_propagete_loop_pH_1,3)


        L1_pH = L_propagete_loop_pH_1 * (10/84)
        L2_pH = L_propagete_loop_pH_1 * (42/84)

        L1_pH = round(L1_pH,3)
        L2_pH = round(L2_pH,3)

        L_propagete_loop_pH_2 = self.calc_propagate_loop_indactance_pH(X2_Ic_uA, X1_Lsquid_pH, X2_Lsquid_pH)
        L3_pH = L_propagete_loop_pH_2 
        L3_pH = round(L3_pH,3)

        L_storage_loop_pH = self.calc_storage_loop_indactance_pH(Ic_uA, X2_Lsquid_pH, X3_Lsquid_pH)

        L4_pH = L_storage_loop_pH * (26/32)
        L5_pH = L_storage_loop_pH * (5/32)
        L6_pH = L_storage_loop_pH * (1/32)

        L4_pH = round(L4_pH,3)
        L5_pH = round(L5_pH,3)
        L6_pH = round(L6_pH,3)

        L_propagete_loop_pH_4 = self.calc_propagate_loop_indactance_pH(X4_Ic_uA, X3_Lsquid_pH, X4_Lsquid_pH)

        L7_pH = L_propagete_loop_pH_4
        L8_pH = L_propagete_loop_pH_4*(32/84)
        L7_pH = round(L7_pH,3)
        L8_pH = round(L8_pH,3)

        L_propagete_loop_pH_5 = self.calc_propagate_loop_indactance_pH(X5_Ic_uA, X5_Lsquid_pH, X5_Lsquid_pH)

        L9_pH = L_propagete_loop_pH_5 * (10/84)
        L10_pH = L_propagete_loop_pH_5 * (42/84)
        L9_pH = round(L9_pH,3)
        L10_pH = round(L10_pH,3)

        L_clock_loop_pH = self.calc_clock_loop_indactance_pH(X3_Ic_uA, X5_Lsquid_pH, X4_Lsquid_pH, X6_Lsquid_pH, X7_Lsquid_pH)

        L_clock_loop_pH_remain = L_clock_loop_pH - L6_pH 
        L11_pH = L_clock_loop_pH_remain * (7/9)
        L12_pH = L_clock_loop_pH_remain * (1/9)
        L13_pH = L_clock_loop_pH_remain * (1/9)
        L11_pH = round(L11_pH,3)
        L12_pH = round(L12_pH,3)
        L13_pH = round(L13_pH,3)


        X1_Icn_uA = round(self.new_nominal_ic_uA(X1_Ic_uA,X1_Lsquid_pH),3)
        X2_Icn_uA = round(self.new_nominal_ic_uA(X2_Ic_uA,X2_Lsquid_pH),3)
        X3_Icn_uA = round(self.new_nominal_ic_uA(X3_Ic_uA,X3_Lsquid_pH),3)
        X4_Icn_uA = round(self.new_nominal_ic_uA(X4_Ic_uA,X4_Lsquid_pH),3)
        X5_Icn_uA = round(self.new_nominal_ic_uA(X5_Ic_uA,X5_Lsquid_pH),3)



        R1 = round(self.new_calc_bias_resistor(X1_Icn_uA,X1_Icn_uA,bias_voltage),3)
        R2 = round(self.new_calc_bias_resistor(X2_Icn_uA,X3_Icn_uA,bias_voltage),3)
        R3 = round(self.new_calc_bias_resistor(X5_Icn_uA,X5_Icn_uA,bias_voltage),3)

        self.change_bias_voltage(bias_voltage)


        shunt_1 = round(self.new_calc_resistor(X1_Ic_uA,2),3)
        shunt_2 = round(self.new_calc_resistor(X2_Ic_uA,2),3)
        shunt_3 = round(self.new_calc_resistor(X3_Ic_uA,2),3)
        shunt_4 = round(self.new_calc_resistor(X4_Ic_uA,2),3)
        shunt_5 = round(self.new_calc_resistor(X5_Ic_uA,2),3)
        shunt_6 = round(self.new_calc_resistor(X6_Ic_uA,2),3)
        

        """
        修正必要




        """
        R_end = 15.842*8.32/X1_Icn_uA

        self.change_end_resistor(R_end)


        self.change_Ic("jtl_squid", str(X1_Ic_uA/100))
        self.change_Ic("X1_squid", str(X1_Ic_uA/100))
        self.change_Ic("X2_squid", str(X2_Ic_uA/100))
        self.change_Ic("X3_squid", str(X3_Ic_uA/100))
        self.change_Ic("X4_squid", str(X4_Ic_uA/100))
        self.change_Ic("X5_squid", str(X5_Ic_uA/100))
        self.change_Ic("X6_squid", str(X6_Ic_uA/100))
        self.change_Ic("X7_squid", str(X7_Ic_uA/100))

        self.change_resistor(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],[str(shunt_1)+"ohm", str(shunt_1)+"ohm"])
        self.change_resistor(["X2_squid"],[str(shunt_2)+"ohm", str(shunt_2)+"ohm"])
        self.change_resistor(["X3_squid"],[str(shunt_3)+"ohm", str(shunt_3)+"ohm"])

        self.change_indactance(["jtl_squid","X1_squid","X4_squid","X5_squid","X6_squid","X7_squid"],["0.00001pH",str(X1_Lsquid_pH/2)+"pH",str(X1_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X2_squid"],["0.00001pH",str(X2_Lsquid_pH/2)+"pH",str(X2_Lsquid_pH/2)+"pH"])
        self.change_indactance(["X3_squid"],["0.00001pH",str(X3_Lsquid_pH/2)+"pH",str(X3_Lsquid_pH/2)+"pH"])
        
        self.change_indactance(["jtl_base"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L_propagete_loop_pH_1)+"pH",str(L8_pH)+"pH"])
        self.change_resistor(["jtl_base"],[str(R1)+"ohm"])

        self.change_resistor(["DFF_"],[str(R1)+"ohm",str(R2)+"ohm",str(R3)+"ohm",str(R3)+"ohm"])
        self.change_indactance(["DFF_"],[str(L1_pH)+"pH",str(L2_pH)+"pH",str(L3_pH)+"pH",str(L4_pH)+"pH",str(L5_pH)+"pH",str(L6_pH)+"pH",str(L7_pH)+"pH",str(L8_pH)+"pH",str(L9_pH)+"pH",str(L10_pH)+"pH",str(L11_pH)+"pH",str(L12_pH)+"pH",str(L13_pH)+"pH"])

        #print(self.netlist)
        power = (bias_voltage**2/R1)+(bias_voltage**2/R2)+(bias_voltage**2/R3)*2
        return X1_Icn_uA, power
    
    def make_dff2(self, Ic_area:float,Icrit:float, bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 0.9/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid2", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid2"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid2"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base"],[str(bias_R)+"ohm"])
        self.change_resistor(["DFF_"],[str(bias_R)+"ohm",str(bias_R)+"ohm",str(bias_R)+"ohm"])


        dff_squid_param = {}
        dff_squid_param["Ic_area"] = Ic_area*1.5
        dff_squid_param["L_squid_pH"] = round(0.9/dff_squid_param["Ic_area"],3)
        dff_squid_param["R_squid_O"] = self.calc_resistor(dff_squid_param["Ic_area"], Icrit,2)
        print("dff_squid_param:",dff_squid_param)

        self.change_Ic("dff_squid1", str(dff_squid_param["Ic_area"]))
        self.change_resistor(["dff_squid1"],[str(dff_squid_param["R_squid_O"])+"ohm", str(dff_squid_param["R_squid_O"])+"ohm"])
        self.change_indactance(["dff_squid1"],[str(dff_squid_param["L_squid_pH"])+"pH",str(dff_squid_param["L_squid_pH"])+"pH"])

        self.change_indactance(["jtl_base"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])


        DFF_inductances = {}
        DFF_inductances["L1"] = "1pH"
        DFF_inductances["L2"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L3"] = str(L_loop_pH)+"pH"
        DFF_inductances["L4"] = "1pH"
        DFF_inductances["L5"] = str(L_loop_pH*3 - 2)+"pH"
        DFF_inductances["L6"] = "1pH"
        DFF_inductances["L7"] = str(L_loop_pH)+"pH"
        DFF_inductances["L8"] = str(L_loop_pH/2)+"pH"
        DFF_inductances["L9"] = "1pH"
        DFF_inductances["L10"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L11"] = "1pH"
        DFF_inductances["L12"] = "1pH"
        DFF_inductances["L13"] = str(round(L_loop_pH - 3 - L_squid_pH*2 - 1.2,3))+"pH"
        print("DFF_inductances:",DFF_inductances)

        self.change_indactance(["DFF_"],[DFF_inductances["L1"],DFF_inductances["L2"],DFF_inductances["L3"],DFF_inductances["L4"],DFF_inductances["L5"],DFF_inductances["L6"],DFF_inductances["L7"],DFF_inductances["L8"],DFF_inductances["L9"],DFF_inductances["L10"],DFF_inductances["L11"],DFF_inductances["L12"],DFF_inductances["L13"]])


        #print(self.netlist)

        self.param_dic = param_dic

        
        return self.netlist
    
    def make_dff3(self, Ic_area:float,Icrit:float, bias_voltage:float):
        param_dic = {}
        param_dic["Ic_area"] = Ic_area
        param_dic["Icrit_mA"] = Icrit*10**3
        param_dic["bias_voltage_mV"] = bias_voltage*10**3
        Ic_uA = Ic_area*Icrit*10**6
        param_dic["Ic_uA"] = Ic_uA

        L_squid_pH = 1.2/Ic_area
        param_dic["L_squid_pH"] = L_squid_pH

        L_squid_H = L_squid_pH*10**(-12)
        param_dic["L_squid_H"] = L_squid_H

        Icn_A = self.nominal_ic(L_squid_H, Ic_area*Icrit)
        param_dic["Icn_A"] = Icn_A

        R_squid_O = self.calc_resistor(Ic_area, Icrit,2)
        param_dic["R_squid_O"] = R_squid_O

        Icn_uA = round(Icn_A*10**6,3)
        param_dic["Icn_uA"] = Icn_uA

        L_loop_pH = round(self.calc_indactance_pH(Ic_area*Icrit, L_squid_H),3)
        print("L_loop_pH:",L_loop_pH)
        param_dic["L_loop_pH"] = L_loop_pH

        bias_R = self.calc_bias_resistor(Icn_A, bias_voltage)
        param_dic["bias_R"] = bias_R
        print(param_dic)

        self.change_Ic("jtl_squid", str(Ic_area))
        self.change_Ic("jtl_squid2", str(Ic_area))

        self.change_resistor(["jtl_squid","jtl_squid2"],[str(R_squid_O)+"ohm", str(R_squid_O)+"ohm"])
        self.change_indactance(["jtl_squid","jtl_squid2"],[str(param_dic["L_squid_pH"])+"pH",str(param_dic["L_squid_pH"])+"pH"])

        self.change_resistor(["jtl_base"],[str(bias_R)+"ohm"])
        self.change_resistor(["DFF_"],[str(bias_R)+"ohm",str(bias_R)+"ohm",str(bias_R)+"ohm"])


        dff_squid_param = {}
        dff_squid_param["Ic_area"] = Ic_area*1.5
        dff_squid_param["L_squid_pH"] = round(1.2/dff_squid_param["Ic_area"],3)
        dff_squid_param["R_squid_O"] = self.calc_resistor(dff_squid_param["Ic_area"], Icrit,2)
        print("dff_squid_param:",dff_squid_param)

        self.change_Ic("dff_squid1", str(dff_squid_param["Ic_area"]))
        self.change_resistor(["dff_squid1"],[str(dff_squid_param["R_squid_O"])+"ohm", str(dff_squid_param["R_squid_O"])+"ohm"])
        self.change_indactance(["dff_squid1"],[str(dff_squid_param["L_squid_pH"])+"pH",str(dff_squid_param["L_squid_pH"])+"pH"])

        self.change_indactance(["jtl_base"],["1pH",str(L_loop_pH/2 - 1)+"pH",str(L_loop_pH)+"pH",str(L_loop_pH/2)+"pH"])


        DFF_inductances = {}
        DFF_inductances["L1"] = "1pH"
        DFF_inductances["L2"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L3"] = str(L_loop_pH)+"pH"
        DFF_inductances["L4"] = "1pH"
        DFF_inductances["L5"] = str(L_loop_pH*3 - 2)+"pH"
        DFF_inductances["L6"] = "1pH"
        DFF_inductances["L7"] = str(L_loop_pH)+"pH"
        DFF_inductances["L8"] = str(L_loop_pH/2)+"pH"
        DFF_inductances["L9"] = "1pH"
        DFF_inductances["L10"] = str(L_loop_pH/2-1)+"pH"
        DFF_inductances["L11"] = "1pH"
        DFF_inductances["L12"] = "1pH"
        DFF_inductances["L13"] = str(round(L_loop_pH - 3 - L_squid_pH*2 - 1.2,3))+"pH"
        print("DFF_inductances:",DFF_inductances)

        self.change_indactance(["DFF_"],[DFF_inductances["L1"],DFF_inductances["L2"],DFF_inductances["L3"],DFF_inductances["L4"],DFF_inductances["L5"],DFF_inductances["L6"],DFF_inductances["L7"],DFF_inductances["L8"],DFF_inductances["L9"],DFF_inductances["L10"],DFF_inductances["L11"],DFF_inductances["L12"],DFF_inductances["L13"]])

        self.param_dic = param_dic
        return self.netlist

    def calc_jitter(self, start, end, jj_count, file, try_count, index):
        self.sim()
        # print(self.get_switch_timing(start))
        # print(self.get_switch_timing(end))
        base_diff = self.get_switch_timing(end).iloc[0,0] - self.get_switch_timing(start).iloc[0,0]
        jitter_list = []
        self.add_jitter(["jtl_squid_test"],"temp=4.2 neb=10000GHz")
        self.add_jitter(["jtl_base_test"],"temp=4.2 neb=10000GHz")
        bar = tqdm(total=try_count, position=index, desc=f"Simulation {index:02}", leave=True, ncols=100)
        for _ in range(try_count):
            bar.update(1)
            self.sim()
            jitter_start = self.get_switch_timing(start).iloc[1,0]
            jitter_end = self.get_switch_timing(end).iloc[1,0]
            jitter_list.append((jitter_end-jitter_start)-base_diff)
            # jitter_list.append(((jitter_end-jitter_start)-base_diff)/jj_count)
            with open(file, 'a', encoding='utf-8', newline='\n') as f:
                f.write(str((jitter_end-jitter_start)-base_diff))
                # f.write(str(((jitter_end-jitter_start)-base_diff)/jj_count))
                f.write("\n")
        bar.close()
        return jitter_list

    def clock_cir_generator(self, interval, count):
        cir = "Vinclk            51    0    PWL(0ps 0mV  "
        for i in range(1,count+1):
            cir += str(i*interval) + "ps 0mV "
            cir += str(i*interval + 1) + "ps 0.517mV "
            cir += str(i*interval + 2) + "ps 0.517mV "
            cir += str(i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vinclk" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir
    
    def clock_cir_generator2(self,start, interval, count):
        cir = "Vinclk            51    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vinclk" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir
    
    def clock_cir_generator_jtl(self,start, interval, count):
        cir = "Vin1           1    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vin1" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir
    
    def clock_cir_generator_for_and(self,start, interval, count):
        cir = "Vinclk           41    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vinclk" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir
    
    def change_end_resistor(self, new_resistor):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        cir = "R72                         76      77" + " " + str(new_resistor) + "ohm"
        for index, line in enumerate(original_lines):
            if "R72" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
    
    def change_bias_resistor(self, percentage):
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            pattern = r"R\d+.*100.*"
            if re.search(pattern, line) and ".model" not in line:
                pre_resistor = float(line.split()[3][:-3])
                new_resistor = pre_resistor*percentage
                new_netlist[index] = ("  ").join(line.split()[0:3]) + " " + str(new_resistor) + "ohm"
        self.netlist = "\n".join(new_netlist)
    
    def din_generator(self,start, interval, count):
        cir = "Vin1          31    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vin1" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir

    def din_generator_Vin1(self,start, interval, count):
        cir = "Vin1          31    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vin1" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir

    def din_generator_Vin2(self,start, interval, count):
        cir = "Vin2          31    0    PWL(0ps 0mV  "
        for i in range(0,count):
            cir += str(start+i*interval) + "ps 0mV "
            cir += str(start+i*interval + 1) + "ps 0.517mV "
            cir += str(start+i*interval + 2) + "ps 0.517mV "
            cir += str(start+i*interval + 3) + "ps 0mV "
        cir += ")\n"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vin2" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir
    
    def change_bias_voltage_percentage(self,origin_voltage, percentage):
        cir = "Vb1                         100     0                       pwl(0ps 0mV 100ps "
        new_vol = origin_voltage*percentage
        cir += str(new_vol)+"mv)"
        print(cir)
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vb1" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir

    def change_bias_voltage(self, bias_voltage_v):
        cir = "Vb1                         100     0                       pwl(0ps 0mV 100ps "
        bias_voltage_mv = bias_voltage_v*10**3
        cir += str(bias_voltage_mv)+"mv)"
        original_lines = self.netlist.split("\n")
        new_netlist = original_lines
        for index, line in enumerate(original_lines):
            if "Vb1" in line:
                new_netlist[index] = cir
                break
        self.netlist = "\n".join(new_netlist)
        return cir

    def change_din(self, din_str):
        net_lines = self.netlist.split("\n")    
        for l,line in enumerate(net_lines):
            if  "Vin1" in line:
                net_lines[l] = din_str
                self.netlist = "\n".join(net_lines)
                break
        return self.netlist

    def change_din1(self, din_str):
        net_lines = self.netlist.split("\n")    
        for l,line in enumerate(net_lines):
            if  "Vin1" in line:
                net_lines[l] = din_str
                self.netlist = "\n".join(net_lines)
                break
        return self.netlist
    
    def change_din2(self, din_str):
        net_lines = self.netlist.split("\n")    
        for l,line in enumerate(net_lines):
            if  "Vin2" in line:
                net_lines[l] = din_str
                self.netlist = "\n".join(net_lines)
                break
        return self.netlist
    
    def change_output_range(self,end,interval):
        net_lines = self.netlist.split("\n")    
        for index, line in enumerate(net_lines):
            if ".tran" in line:
                new_netline = line.split()
                new_netline[1] = interval
                new_netline[2] = end
                new_netline[4] = interval
                net_lines[index] = " ".join(new_netline)
        self.netlist = "\n".join(net_lines)
        print(self.netlist)
        return self.netlist
    
    def change_timing(self, place:int, diff:int):
        net_lines = self.netlist.split("\n")
        index = 8*place - 3
    
        for l,line in enumerate(net_lines):
            if  "Vin1" in line:
                change_line = net_lines[l].split()    
                for i in [index,index+2,index+4,index+6]:
                    new_time = str(int(re.sub(r"[^\d.]", "", change_line[i]))+diff) + "ps"
                    change_line[i] = new_time
                new_line = " ".join(change_line)
                net_lines[l] = new_line
                self.netlist = "\n".join(net_lines)
                break
    
        return self.netlist
    
    def write_error(self):
        file_info_path = "error/error_info_index.json"
        with open(file_info_path, 'r', encoding='utf-8') as file:
            error_info = json.load(file)
        file_count = int(error_info["file_count"])
        self.output_netlist(f"error/error_{file_count}.cir")
        self.output_sim_result(f"error/error_{file_count}.csv")

        with open(file_info_path, 'w', encoding='utf-8') as file:
            error_info["file_count"] = file_count + 1
            json.dump(error_info, file, indent=4)
        
    
    
    def add_print_element(self, elements):
        net_lines = self.netlist.split("\n")
        length = len(net_lines) -1
        
        for index, e in enumerate(elements):
            match = re.search(r'^([VIP])\((.*?)\)', e)
            element_type = ""
            if match.group(1) == "V":
                element_type = "devv"
            elif match.group(1) == "I":
                element_type = "devi"
            elif match.group(1) == "P":
                element_type = "phase"

            new_element = f".print {element_type} {match.group(2)}"

            net_lines.insert(length-1+index, new_element)
            
        self.netlist = "\n".join(net_lines)
        
        return self.netlist
    
    def plot_output(self, file, title="HFQ-DFF"):
        command = [
            "python3", "../scripts/josim-plot.py", file,
            "-t", "stacked",
            "-c", "light",
            "-w", title,
            "-o", title+".png"
        ]

        # subprocess.run を使ってコマンドを実行
        subprocess.run(command)

    def dff_test1(self):
        self.clock_cir_generator2(500, 100,50)
        self.din_generator(650, 100,15)
        
        print(self.get_switch_timing(["P(B1|X7|X1)","P(B2|X7|X1)"]).shape[0])
        print(self.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).shape[0])
        escape_count = self.get_switch_timing(["P(B1|X7|X1)","P(B2|X7|X1)"]).shape[0] 
        output_count = self.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).shape[0]

        return escape_count, output_count
    
    def dff_test2(self):
        self.clock_cir_generator2(500, 100,20)
        self.din_generator(620, 100,8)
        
        print(self.get_switch_timing(["P(B1|X7|X1)","P(B2|X7|X1)"]).shape[0])
        print(self.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).shape[0])
        escape_count = self.get_switch_timing(["P(B1|X7|X1)","P(B2|X7|X1)"]).shape[0] 
        output_count = self.get_switch_timing(["P(B1|X1|X5|X73)","P(B2|X1|X5|X73)"]).shape[0]

        return escape_count, output_count
