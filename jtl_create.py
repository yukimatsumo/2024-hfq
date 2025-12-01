from circuit_sim import circuit_sim

# パラメータ設定
## ic: 臨界電流値(μA)
## lic: L*Ic積(pH*μA)
## bias_voltage: バイアス電圧(V)
ic = 74.4
lic = 74.4*2.4
bias_voltage = 0.5*10**(-3)

# JTLネットリストの作成
sim_con = circuit_sim("jtl_base.cir")
sim_con.new_make_jtl2(ic,lic,bias_voltage)

# シミュレーション実行
sim_con.sim()

# 作成したネットリストのファイル出力
netlist_file = "netlist_output.cir"
sim_con.output_netlist(netlist_file)

# シミュレーション結果のファイル出力、プロット
result_file = "result.csv"
sim_con.output_sim_result(result_file)
# sim_con.plot_output(result_file)
