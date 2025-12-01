.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)

** + -------------------- +
** |     HFQJTL           |
** + -------------------- +
.subckt jtl_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=0.8
R1 1 5 14.125ohm
B2 4 5 pjjmod area=0.8
R2 4 5 14.125ohm
.ends

.subckt jtl_base        1       5       100
L1 1 2 0.626pH
L2 2 3 2.63pH
L3 3 4 5.259pH
L4 4 5 1.999pH
X1      jtl_squid       3       0
X2      jtl_squid       4       0
R1 2 100 27.13ohm
.ends

.subckt jtl_base8       1       9       100
X1      jtl_base        1       2       100
X2      jtl_base        2       3       100
X3      jtl_base        3       4       100
X4      jtl_base        4       5       100
X5      jtl_base        5       6       100
X6      jtl_base        6       7       100
X7      jtl_base        7       8       100
X8      jtl_base        8       9       100
.ends
** + ---------------------------------- +

** + -------------------- +
** |     HFQDFF           |
** + -------------------- +
.subckt X1_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=0.8
R1 1 5 14.125ohm
B2 4 5 pjjmod area=0.8
R2 4 5 14.125ohm
.ends

.subckt X2_squid    2       5 
L0 2 3 0.00001pH
L1 3 1 0.919pH
L2 3 4 0.919pH
B1 1 5 jjmod area=1.0472700000000001
R1 1 5 10.79ohm
B2 4 5 pjjmod area=1.0472700000000001
R2 4 5 10.79ohm
.ends

.subckt X3_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.2255pH
L2 3 4 1.2255pH
B1 1 5 jjmod area=0.78545
R1 1 5 14.387ohm
B2 4 5 pjjmod area=0.78545
R2 4 5 14.387ohm
.ends

.subckt X4_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=0.8
R1 1 5 14.125ohm
B2 4 5 pjjmod area=0.8
R2 4 5 14.125ohm
.ends

.subckt X5_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=0.8
R1 1 5 14.125ohm
B2 4 5 pjjmod area=0.8
R2 4 5 14.125ohm
.ends

.subckt X6_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=2.0
R1 1 5 14.125ohm
B2 4 5 pjjmod area=2.0
R2 4 5 14.125ohm
.ends

.subckt X7_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.203pH
L2 3 4 1.203pH
B1 1 5 jjmod area=0.8
R1 1 5 14.125ohm
B2 4 5 pjjmod area=0.8
R2 4 5 14.125ohm
.ends


.subckt DFF_ 1 21 9 100
L1 1 2 0.626pH
R1 2 100 27.13ohm
L2 2 3 2.63pH
X1      X1_squid        3       0
L3 3 4 3.875pH
X2      X2_squid        4       0
L4 4 5 14.88pH
R2 5 100 23.68ohm
L5 5 6 2.862pH
L6 6 7 0.572pH
X3      X3_squid        7       0
L7 7 8 5.248pH
X4      X4_squid        8       0
L8 8 9 1.999pH

L21 21 22 0.626pH
R3 22 100 27.13ohm
L22 22 23 2.629pH
X5      X5_squid        23      0
L23 23 24 1.867pH
X6      X6_squid        24      25
L24 25 26 0.267pH
X7      X7_squid        26      27
L25 27 6 0.267pH
.ends
** + ---------------------------------- +

*** top cell: 
Vin1                        31      0       PWL(0ps 0mV 350ps 0mV 351ps 0.517mV 352ps 0.517mV 353ps 0mV)
* Vin1                        31      0       PWL(0ps 0mV)
R31                         31      32      1ohm temp=0
X31    jtl_base8            32      33      100
X32    jtl_base8            33      34      100
X33    jtl_base8            34      35      100
X34    jtl_base8            35      36      100

Vinclk                      51      0       PULSE(0mV 0.517mV 300ps 1ps 1ps 1ps 100ps)
* Vinclk                      51      0       PWL(0ps 0mV   300ps 0mV 301ps 0.517mV 302ps 0.517mV 303ps 0mV   400ps 0mV 401ps 0.517mV 402ps 0.517mV 403ps 0mV)
R51                         51      52      1ohm temp=0
X51    jtl_base8            52      53      100
X52    jtl_base8            53      54      100
X53    jtl_base8            54      55      100
X54    jtl_base8            55      56      100

X1      DFF_                 36      56      72      100

X71    jtl_base8            72      73      100
X72    jtl_base8            73      74      100
X73    jtl_base8            74      75      100
X74    jtl_base8            75      76      100
R72                         76      77 5.720722222222222ohm
L71                         77      0       2pH

Vb1                         100     0       pwl(0ps 0mV 100ps 0.5mV)

*** jsim input file ***
.tran 0.1ps 1100ps 0ps 0.1ps

.print phase  B1|X1|X5|X73
.print phase  B2|X1|X5|X73
.print phase  B1|X1|X5|X32
.print phase  B2|X1|X5|X32
.print phase  B1|X1|X5|X34
.print phase  B2|X1|X5|X34
.print phase  B1|X1|X1
.print phase  B2|X1|X1
.print phase  B1|X2|X1
.print phase  B2|X2|X1
.print phase  B1|X5|X1
.print phase  B2|X5|X1

.print phase  B1|X7|X1
.print phase  B2|X7|X1


.print devv R31
.print devv R51
.print devv  R72
*.print devv R10|X1
.end