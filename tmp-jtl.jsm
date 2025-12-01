.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)


** + -------------------- +
** |     HFQJTL           |
** + -------------------- +
.subckt jtl_squid   2       5 
L0 2 3 0.00001pH
L1 3 1 1.2pH
L2 3 4 1.2pH
B1 1 5 jjmod area=0.7440000000000001
B2 4 5 pjjmod area=0.7440000000000001
* R1 3 5 31.26ohm
* R1 1 5 39.418ohm
* R2 4 5 39.418ohm
.ends

.subckt jtl_base        1       5       100
L1 1 2 0.684pH
L2 2 3 2.874pH
L3 3 4 5.748pH
L4 4 5 2.186pH
X1      jtl_squid       3       0
X2      jtl_squid       4       0
R1 2 100 31.26ohm
* R1 2 100 50.014ohm
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

*** top cell: DCHFQ - HFQJTL

Vin1                    1       0       PULSE(0mV 0.517mV 350ps 1ps 1ps 1ps 25ps)
* Vin1                    1       0       PULSE(0mV 0.517mV 350ps 1ps 1ps 1ps 40ps)
* Vin1                    1       0       PWL(0ps 0mV   500ps 0mV 501ps 0.517mV 502ps 0.517mV 503ps 0mV  600ps 0mV 601ps 0.517mV 602ps 0.517mV 603ps 0mV)

R1                      1       11      1ohm temp=0
X1      jtl_base8       11      12      100        
X2      jtl_base8       12      13      100   
X3      jtl_base8       13      14      100   
X4      jtl_base8       14      15      100 

X35     jtl_base8       15      25      100

X5      jtl_base8       25      26      100        
X6      jtl_base8       26      27      100   
X7      jtl_base8       27      28      100   
X8      jtl_base8       28      76      100   
R72                     76      77      8.32ohm temp=0
L1                      77      0       2pH

Vb1                     100     0       pwl(0ps 0mV 100ps 0.5mV)
* Vb1                     100     0       pwl(0ps 0mV 100ps 1.0mV)

* .tran 0.1ps 1300ps 0ps 0.1ps
.tran 0.1ps 1300ps 300ps 0.1ps

.temp 4.2
.neb 10000GHz

.print phase  B1|X1|X1|X35
.print phase  B2|X1|X1|X35

.print phase B1|X1|X6|X2
.print phase B2|X1|X6|X2
.print phase B1|X1|X6|X7
.print phase B2|X1|X6|X7

* .print devv R1
.print devv B1|X1|X1|X35
.print devv B2|X1|X1|X35
.end