.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)

.param Jc=0.100m
.param IcScale=2/213
.param VbScale=0.50m/2.5m

.param Phi0=2.067833848E-15
.param Vbase=2.5m
.param IbFactor=0.7

.param IcRs=1.13m
.param Vb=Vbase*VbScale

.param interval=50p
* .param interval=100p
* .param interval=2*Phi0/Vb

** parameters for the itl **
.param ijtl_ic1=IcScale*213u
.param ijtl_b1=ijtl_ic1/Jc
.param ijtl_rs1=IcRs/ijtl_ic1
.param ijtl_l1=4.534p/IcScale
.param ijtl_l2=1.976p/IcScale
.param ijtl_lp1=0.198p/IcScale
** + ---------------------------------- +

** parameters for the sink **
.param sink_ic1=IcScale*217u
.param sink_b1=sink_ic1/Jc
.param sink_rs1=IcRs/sink_ic1
.param sink_lpin=0.317p/IcScale
.param sink_l1=2.272p/IcScale
.param sink_l2=4.776p/IcScale
.param sink_lp1=0.13p/IcScale
.param sink_lpr1=0.177p/IcScale
.param sink_r2=4.08/IcScale
.param sink_rb1=(8.32)/IcScale
* .param sink_rb1=(8.32*VbScale)/IcScale
** + ---------------------------------- +

** parameters for the jtl **
.param jtl_ic1=IcScale*216u
.param jtl_b1=jtl_ic1/Jc
.param jtl_rs1=IcRs/jtl_ic1
.param jtl_ic2=IcScale*216u
.param jtl_b2=jtl_ic2/Jc
.param jtl_rs2=IcRs/jtl_ic2
.param jtl_lpin=0.317p/IcScale
.param jtl_l1=2.288p/IcScale
.param jtl_l2=4.506p/IcScale
.param jtl_l3=1.963p/IcScale
.param jtl_lp1=0.096p/IcScale
.param jtl_lp2=0.099p/IcScale
.param jtl_lpr1=0.177p/IcScale
.param jtl_rb1=(8.32)/IcScale
.param test_rb1=(8.32*VbScale)/IcScale
** + ---------------------------------- +

.subckt ijtl            1       11
L1                      1       10      ijtl_l1 fcheck
B1                      10      9       jjmod area=ijtl_b1 temp=0
RS1                     10      9       ijtl_rs1 temp=0
LP2                     9       0       ijtl_lp1 fcheck
L2                      10      11      ijtl_l2 fcheck
.ends

.subckt sink            1       100
LPIN                    1       2       sink_lpin fcheck
L1                      2       3       sink_l1 fcheck
L2                      3       4       sink_l2 fcheck
R2                      4       0       sink_r2 temp=0
LPR1                    2       5       sink_lpr1 fcheck
* R1                      5       100     sink_rb1
R1                      100     5       sink_rb1 temp=0
B1                      3       9       jjmod area=sink_b1 temp=0
RS1                     3       9       sink_rs1 temp=0
LP1                     9       0       sink_lp1 fcheck
.ends

.subckt sfq_jtl         1       5       100
LPIN                    1       2       jtl_lpin fcheck
L1                      2       3       jtl_l1 fcheck
L2                      3       4       jtl_l2 fcheck
L3                      4       5       jtl_l3 fcheck
B1                      3       7       jjmod area=jtl_b1 temp=0
RS1                     3       7       jtl_rs1 temp=0
LP1                     7       0       jtl_lp1 fcheck
B2                      4       8       jjmod area=jtl_b2 temp=0
RS2                     4       8       jtl_rs2 temp=0
LP2                     8       0       jtl_lp2 fcheck
LPR1                    2       6       jtl_lpr1 fcheck
R1                      6       100     jtl_rb1 temp=0
.ends

.subckt test_jtl        1       5       100
LPIN                    1       2       jtl_lpin fcheck
L1                      2       3       jtl_l1 fcheck
L2                      3       4       jtl_l2 fcheck
L3                      4       5       jtl_l3 fcheck
B1                      3       7       jjmod area=jtl_b1
RS1                     3       7       jtl_rs1
LP1                     7       0       jtl_lp1 fcheck
B2                      4       8       jjmod area=jtl_b2
RS2                     4       8       jtl_rs2
LP2                     8       0       jtl_lp2 fcheck
LPR1                    2       6       jtl_lpr1 fcheck
R1                      6       100     test_rb1
.ends

.subckt sfq_jtl8        1       9       100
X1      sfq_jtl         1       2       100
X2      sfq_jtl         2       3       100
X3      sfq_jtl         3       4       100
X4      sfq_jtl         4       5       100
X5      sfq_jtl         5       6       100
X6      sfq_jtl         6       7       100
X7      sfq_jtl         7       8       100
X8      sfq_jtl         8       9       100
.ends

.subckt test_jtl8       1       9       100
X1      test_jtl        1       2       100
X2      test_jtl        2       3       100
X3      test_jtl        3       4       100
X4      test_jtl        4       5       100
X5      test_jtl        5       6       100
X6      test_jtl        6       7       100
X7      test_jtl        7       8       100
X8      test_jtl        8       9       100
.ends

*** top cell:

* Vin                         31      0       PULSE(0mV 1.035mV 400ps 1ps 1ps 1ps interval)
Vin                         31      0       PWL(0ps 0mV   300ps 0mV 301ps 1.035mV 302ps 1.035mV 303ps 0mV)

X30    ijtl                 31      32
X31    sfq_jtl8             32      33      100
X32    sfq_jtl8             33      34      100
X33    sfq_jtl8             34      35      100
X34    sfq_jtl8             35      11      100

X11    test_jtl8            11      12      200
X12    test_jtl8            12      13      200
X13    test_jtl8            13      14      200
X14    test_jtl8            14      15      200
X15    test_jtl8            15      16      200

X41    sfq_jtl8             16      42      100
X42    sfq_jtl8             42      43      100
X43    sfq_jtl8             43      44      100
X44    sfq_jtl8             44      45      100
X45    sink                 45      100

Vb1                         100     0       pwl(0ps 0mV 200ps Vbase)
Vb2                         200     0       pwl(0ps 0mV 200ps Vb)

*** jsim input file ***
.tran 0.01ps 900ps 0ps 0.01ps
* .tran 0.1ps 1300ps 300ps 0.1ps

.temp 4.2
.neb 10000GHz

.print phase  B1|X1|X32
.print phase  B1|X1|X43

.print phase  B2|X8|X34
.print phase  B1|X1|X41

.print divv   B1|X1|X32
.print divv   B1|X1|X43

.print divv   B2|X8|X34
.print divv   B1|X1|X41

* .print divi   B1|X1|X13

.end