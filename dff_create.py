from circuit_sim import circuit_sim

# パラメータ設定
## ic: 臨界電流値(μA)
## lic: L*Ic積(pH*μA)
## bias_voltage: バイアス電圧(V)
ic = 60.8
lic = 60.8*3.5  
bias_voltage = 0.5*10**(-3)
betac = 2
ibfactor = 0.5

# DFFネットリストの作成
sim_con = circuit_sim("dff_base.cir")
# sim_con.new_make_dff2(ic,lic,bias_voltage, ibfactor=ibfactor, betac=betac)
sim_con.new_make_dff3(ic,lic,bias_voltage, ibfactor=ibfactor, betac=betac)
# シミュレーション実行
sim_con.sim()

# 作成したネットリストのファイル出力
netlist_file = "netlist_output.cir"
sim_con.output_netlist(netlist_file)

# シミュレーション結果のファイル出力、プロット
result_file = "result.csv"
sim_con.output_sim_result(result_file)
# sim_con.plot_output(result_file)
