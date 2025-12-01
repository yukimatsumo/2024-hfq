.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)

** + -------------------- +
** |     HFQJTL           |
** + -------------------- +
.subckt jtl_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=0.7
B2 4 5 pjjmod area=0.7
.ends

.subckt jtl_base        1       5       100
L1 1 2 0.727pH
L2 2 3 3.055pH
L3 3 4 6.11pH
L4 4 5 2.323pH
X1      jtl_squid       3       0
X2      jtl_squid       4       0
R1 2 100 33.22ohm
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
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=0.7
B2 4 5 pjjmod area=0.7
.ends

.subckt X2_squid    2       5 
L0 2 3 0.00001pH
L1 3 1 0.9745pH
L2 3 4 0.9745pH
B1 1 5 jjmod area=0.91636
B2 4 5 pjjmod area=0.91636
.ends

.subckt X3_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.299pH
L2 3 4 1.299pH
B1 1 5 jjmod area=0.68727
B2 4 5 pjjmod area=0.68727
.ends

.subckt X4_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=0.7
B2 4 5 pjjmod area=0.7
.ends

.subckt X5_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=0.7
B2 4 5 pjjmod area=0.7
.ends

.subckt X6_squid  2       5 
L0 2 3 0.00001pH
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=2.0
B2 4 5 pjjmod area=2.0
.ends

.subckt X7_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.2755pH
L2 3 4 1.2755pH
B1 1 5 jjmod area=0.7
B2 4 5 pjjmod area=0.7
.ends


.subckt DFF_ 1 21 9 100
L1 1 2 0.727pH
R1 2 100 33.22ohm
L2 2 3 3.055pH
X1      X1_squid        3       0
L3 3 4 4.516pH
X2      X2_squid        4       0
L4 4 5 17.078pH
R2 5 100 29.0ohm
L5 5 6 3.284pH
L6 6 7 0.657pH
X3      X3_squid        7       0
L7 7 8 6.098pH
X4      X4_squid        8       0
L8 8 9 2.323pH

L21 21 22 0.727pH
R3 22 100 33.22ohm
L22 22 23 3.055pH
X5      X5_squid        23      0
L23 23 24 2.363pH
X6      X6_squid        24      25
L24 25 26 0.338pH
X7      X7_squid        26      27
L25 27 6 0.338pH
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
R72                         76      77 7.006083027693617ohm
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