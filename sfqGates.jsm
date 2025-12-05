.model jjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA)
.model pjjmod jj(Rtype=1, Vg=2.8mV, Cap=0.064pF, R0=100ohm, Rn=16ohm, Icrit=0.1mA, PHI=PI)

** + -------------------- +
** |     SFQ JTL          |
** + -------------------- +
** ADP2 2.5mV ijtl
.subckt ijtl            1       11
L1                      1       10      4.534pH
B1                      10      9       jjmod area=2.13
RS1                     10      9       5.31ohm
LP2                     9       0       0.198pH
L2                      10      11      1.976pH
.ends

** ADP2 2.5mV source
.subckt source          1
L1                      1       2       2.012pH fcheck
L2                      2       3       2.644pH fcheck
Rd                      3       0       4.02ohm
B1                      2       4       jjmod area=2.16
RS1                     2       4       5.2225ohm
LP1                     4       0       0.122pH fcheck
.ends

** ADP2 2.5mV sink
.subckt sink            1       100
LPIN                    1       2       0.317pH fcheck
L1                      2       3       2.272pH fcheck
L2                      3       4       4.776pH fcheck
R2                      4       0       4.08ohm
LPR1                    2       5       0.177pH fcheck
R1                      5       100     8.32ohm
B1                      3       9       jjmod area=2.17
RS1                     3       9       5.207ohm
LP1                     9       0       0.13pH fcheck
.ends

*** HSTP drv_jtl
.subckt drv_jtl     1     2     3
Rins       2     4  1.67ohm
R1         3     5  8.34ohm
L1         1     6  0.842pH fcheck
LPR1       5     6  3.585pH fcheck
LPOUT      7     4  0.959pH fcheck
L2         6     7  2.327pH fcheck
LP1        8     0  0.237pH fcheck
B1         7     8  jjmod area=2.37
RS1        7     8  7.06ohm *SHUNT=16.74
.ends

*** HSTP rec
.subckt rec     1     2     3
R1         3     5  22.92ohm
L1         1     6  0.723pH fcheck
LPR1       5     6  1.849pH fcheck
L2         7     9  5.333pH fcheck
L3         9     2  1.620pH fcheck
LP3        6     7  0.185pH fcheck
LP2        10    0  0.216pH fcheck
LP1        8     0  0.281pH fcheck
B2         9    10  jjmod area=2.13
RS2        9    10  7.04ohm *SHUNT=15.00
B1         7     8  jjmod area=1.39
RS1        7     8  12.03ohm *SHUNT=16.74
.ends

*** HSTP sll (PTL wire)
.subckt sll     1     2
C1         1     0  0.084pF
L1         1     2  1.142pH fcheck
.ends

*** hstp001 ptl sample
*** PORT    din  = 1
*** PORT    dout = 2
* XI0      drv_jtl   1      11    Vb
* XI1        rec     12     2     Vb
* XI4        sll     13     12
* XI3        sll     14     13
* XI2        sll     11     14

** ADP2 2.5mV (betac=2) delay: 3.6 ps
.subckt sfq_jtl         1       5       100
LPIN                    1       2       0.317pH fcheck
L1                      2       3       2.288pH fcheck
L2                      3       4       4.506pH fcheck
L3                      4       5       1.963pH fcheck
B1                      3       7       jjmod area=2.16
RS1                     3       7       5.225ohm
LP1                     7       0       0.096pH fcheck
B2                      4       8       jjmod area=2.16
RS2                     4       8       5.225ohm
LP2                     8       0       0.099pH fcheck
LPR1                    2       6       0.177pH fcheck
R1                      6       100     8.32ohm
.ends

* delay: 5.4 ps
.subckt sfq_3jtl        1       5       100
LPIN                    1       2       0.317pH fcheck
L1                      2       3       2.288pH fcheck
L2                      3       4       4.506pH fcheck
L3                      4       5       4.506pH fcheck
L4                      5       6       1.963pH fcheck
B1                      3       7       jjmod area=2.16
RS1                     3       7       5.225ohm
LP1                     7       0       0.096pH fcheck
B2                      4       8       jjmod area=2.16
RS2                     4       8       5.225ohm
LP2                     8       0       0.099pH fcheck
B3                      5       11      jjmod area=2.16
RS3                     5       11      5.225ohm
LP3                     11      0       0.099pH fcheck
LPR1                    2       9       0.177pH fcheck
R1                      9       100     8.32ohm
LPR2                    4       10      0.177pH fcheck
R2                      10      100     16.64ohm
.ends

.subckt balanced_jtl    1       5       100
LPIN                    1       2       0.317pH fcheck
L1                      2       3       2.288pH fcheck
L2                      3       4       4.506pH fcheck
L3                      4       5       2.963pH fcheck
B1                      3       7       jjmod area=2.16
RS1                     3       7       5.225ohm
LP1                     7       0       0.096pH fcheck
B2                      4       8       jjmod area=2.16
RS2                     4       8       5.225ohm
LP2                     8       0       0.099pH fcheck
* R1                      2       100     16.64ohm
* R2                      4       100     16.64ohm
R1                      2       100     8.32ohm
R2                      4       100     17.5ohm
.ends

* delay: 7.2 ps
.subckt sfq_jtl2        1       3       100
X1      sfq_jtl         1       2       100
X2      sfq_jtl         2       3       100
.ends

* delay: 3.6+4.3= 7.9 ps
.subckt sfq_spl_jtl     1       3       100
X1      sfq_spl         1       2       4      100
X2      sfq_jtl         2       3       100
X3      sink            4       100
.ends

* delay: 9.0 ps
.subckt sfq_3jtl_jtl    1       3       100
X1      sfq_3jtl        1       2       100
X2      sfq_jtl         2       3       100
.ends

* delay: 5.4+4.3= 9.7 ps
.subckt sfq_spl_3jtl    1       3       100
X1      sfq_spl         1       2       4      100
X2      sfq_3jtl        2       3       100
X3      sink            4       100
.ends

* delay: 10.8 ps
.subckt sfq_jtl3        1       4       100
X1      sfq_jtl         1       2       100
X2      sfq_jtl         2       3       100
X3      sfq_jtl         3       4       100
.ends

* delay: 7.2+4.3= 11.5 ps
.subckt sfq_spl_jtl2    1       3       100
X1      sfq_spl         1       2       4      100
X2      sfq_jtl2        2       3       100
X3      sink            4       100
.ends

* delay: 12.6 ps
.subckt sfq_3jtl_jtl2   1       3       100
X1      sfq_3jtl        1       2       100
X2      sfq_jtl2        2       3       100
.ends

* delay: 9.0+4.3= 13.3 ps
.subckt sfq_spl_3j_j    1       3       100
X1      sfq_spl         1       2       4      100
X2      sfq_3jtl_jtl    2       3       100
X3      sink            4       100
.ends

* delay: 14.4 ps
.subckt sfq_jtl4        1       5       100
X1      sfq_jtl         1       2       100
X2      sfq_jtl         2       3       100
X3      sfq_jtl         3       4       100
X4      sfq_jtl         4       5       100
.ends

* delay: 18.0 ps
.subckt sfq_jtl5        1       3       100
X1      sfq_jtl4        1       2       100
X2      sfq_jtl         2       3       100
.ends

* delay: 19.8 ps
.subckt sfq_3jtl_jtl4   1       3       100
X1      sfq_3jtl        1       2       100
X2      sfq_jtl4        2       3       100
.ends

* delay: 21.6 ps
.subckt sfq_jtl6       1       3       100
X1      sfq_jtl4        1       2       100
X2      sfq_jtl2        2       3       100
.ends

* delay: 23.4 ps
.subckt sfq_3jtl_jtl5   1       3       100
X1      sfq_3jtl        1       2       100
X2      sfq_jtl5        2       3       100
.ends

* delay: 25.2 ps
.subckt sfq_jtl7        1       3       100
X1      sfq_jtl4        1       2       100
X2      sfq_jtl3        2       3       100
.ends

* delay: 28.8 ps
.subckt sfq_jtl8        1       3       100
X1      sfq_jtl4        1       2       100
X2      sfq_jtl4        2       3       100
.ends

.subckt sfq_jtl9        1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl         2       3       100
.ends

.subckt sfq_jtl10       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl2        2       3       100
.ends

.subckt sfq_jtl11       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl3        2       3       100
.ends

.subckt sfq_jtl12       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl4        2       3       100
.ends

.subckt sfq_jtl13       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl5        2       3       100
.ends

.subckt sfq_jtl14       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl6        2       3       100
.ends

.subckt sfq_jtl15       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl7        2       3       100
.ends

.subckt sfq_jtl16       1       3       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
.ends

.subckt sfq_jtl17       1       4       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl         3       4       100
.ends

.subckt sfq_jtl18       1       4       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl2        3       4       100
.ends

.subckt sfq_jtl19       1       4       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl3        3       4       100
.ends

.subckt sfq_jtl20       1       4       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl4        3       4       100
.ends

.subckt sfq_jtl24       1       4       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl8        3       4       100
.ends

.subckt sfq_jtl28       1       5       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl8        3       4       100
X4      sfq_jtl4        4       5       100
.ends

.subckt sfq_jtl32       1       5       100
X1      sfq_jtl8        1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl8        3       4       100
X4      sfq_jtl8        4       5       100
.ends

.subckt sfq_jtl36       1       5       100
X1      sfq_jtl12       1       2       100
X2      sfq_jtl8        2       3       100
X3      sfq_jtl8        3       4       100
X4      sfq_jtl8        4       5       100
.ends

.subckt sfq_jtl40       1       5       100
X1      sfq_jtl12       1       2       100
X2      sfq_jtl12       2       3       100
X3      sfq_jtl8        3       4       100
X4      sfq_jtl8        4       5       100
.ends

.subckt sfq_jtl44       1       5       100
X1      sfq_jtl12       1       2       100
X2      sfq_jtl12       2       3       100
X3      sfq_jtl12       3       4       100
X4      sfq_jtl8        4       5       100
.ends

.subckt sfq_jtl48       1       5       100
X1      sfq_jtl12       1       2       100
X2      sfq_jtl12       2       3       100
X3      sfq_jtl12       3       4       100
X4      sfq_jtl12       4       5       100
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ SPL          |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** din (1), out1 (7), out2 (9), bias (100)
.subckt sfq_spl 1 7 9 100
LPIN                    1       2       0.38pH fcheck
L1                      2       3       2.215pH fcheck
L6                      3       4       0.504pH fcheck
L2                      4       6       4.707pH fcheck
L4                      6       7       1.708pH fcheck
L3                      4       8       4.857pH fcheck
L5                      8       9       1.682pH fcheck

LPR1                    2       10      0.156pH fcheck
R1                      10      100     8.32ohm
B1                      3       11      jjmod area=2.15
RS1                     3       11      5.249ohm
LP1                     11      0       0.138pH fcheck

B2                      6       12      jjmod area=1.94
RS2                     6       12      5.818ohm
LP2                     12      0       0.127pH fcheck

B3                      8       13      jjmod area=1.94
RS3                     8       13      5.818ohm
LP3                     13      0       0.125pH fcheck
.ends

.subckt balanced_spl 1 7 9 100
LPIN                    1       2       0.38pH fcheck
L1                      2       3       2.215pH fcheck
L6                      3       4       0.504pH fcheck
L2                      4       6       4.707pH fcheck
L4                      6       7       1.708pH fcheck
L3                      4       8       4.857pH fcheck
L5                      8       9       1.682pH fcheck

LPR1                    2       10      0.156pH fcheck
R1                      10      100     8.32ohm
B1                      3       11      jjmod area=2.15
RS1                     3       11      5.249ohm
LP1                     11      0       0.138pH fcheck

B2                      6       12      jjmod area=1.94
RS2                     6       12      5.818ohm
LP2                     12      0       0.127pH fcheck

R2                      8       100     15.5ohm
B3                      8       13      jjmod area=1.94
RS3                     8       13      5.818ohm
LP3                     13      0       0.125pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ CBE          |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** din1 (1), din2 (10), out (20), bias (100)
.subckt sfq_cbe         1       10      20       100
LPIN1                   1       2       0.354pH fcheck
L8                      2       3       2.467pH fcheck
L1                      3       4       3.624pH fcheck
L5                      4       5       1.144pH fcheck
B3                      5       6       jjmod area=1.82
RS3                     5       6       6.201ohm
LPR2                    2       7       0.174pH fcheck 
R2                      7       100     8.34ohm
B6                      3       8       jjmod area=2.16
RS6                     3       8       5.225ohm
LP6                     8       0       0.109pH fcheck
B1                      4       9       jjmod area=2.16
RS1                     4       9       5.225ohm
LP1                     9       0       0.276pH fcheck

LPIN2                   10      11      0.403pH fcheck
L9                      11      12      2.488pH fcheck
L2                      12      13      3.619pH fcheck
L6                      13      14      1.154pH fcheck
B4                      14      6       jjmod area=1.82
RS4                     14      6       6.201ohm
LPR3                    11      15      0.187pH fcheck
R3                      15      100     8.34ohm
B7                      12      16      jjmod area=2.16
RS7                     12      16      5.225ohm
LP7                     16      0       0.12pH fcheck
B2                      13      17      jjmod area=2.16
RS2                     13      17      5.225ohm
LP2                     17      0       0.268pH fcheck

L7                      6       18      0.494pH fcheck
L3                      18      19      4.186pH fcheck
L4                      19      20      1.277pH fcheck
LPR1                    18      21      0.018pH fcheck
R1                      21      100     9.0ohm
B5                      19      22      jjmod area=2.70
RS5                     19      22      4.18ohm
LP5                     22      0       0.343pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ TFF          |
** + -------------------- +
** HSTP 2.5mV (betac=2)
** din (1), outA (10), outB (16), bias (100)
.subckt sfq_tff 1 10 16 100
LPIN                    1       2       0.476pH fcheck
LPR1                    2       31      0.363pH fcheck
R1                      31      100     8.33ohm
L1                      2       3       2.241pH fcheck
B1                      3       21      jjmod area=2.16
RS1                     3       21      5.225ohm
LP1                     21      0       0.304pH fcheck
L2                      3       4       1.069pH fcheck

L3                      4       5       1.867pH fcheck
B2                      5       6       jjmod area=2.2
RS2                     5       6       5.13ohm
B4                      6       24      jjmod area=1.082
RS4                     6       24      10.43ohm
LP4                     24      0       0.247pH fcheck
L12                     6       7       0.101pH fcheck
L7                      7       8       0.679pH fcheck
LPR2                    8       32      0.445pH fcheck
R2                      32      100     16.66ohm
L8                      8       9       2.392pH fcheck
B6                      9       27      jjmod area=2.16
RS6                     9       27      5.225ohm
LP6                     27      0       0.234pH fcheck
L10                     9       10      1.365pH fcheck

L5                      7       11      3.208pH fcheck
LP8                     11      28      0.294pH fcheck
RD                      28      0       2.0ohm
L6                      11      14      3.115pH fcheck 

L4                      4       12      1.911pH fcheck
B3                      12      13      jjmod area=1.3
RS3                     12      13      8.682ohm
B5                      13      25      jjmod area=1.96
RS5                     13      25      5.758ohm
LP5                     25      0       0.185pH fcheck
L13                     13      14      0.177pH fcheck
L9                      14      15      4.222pH fcheck
B7                      15      27      jjmod area=2.16
RS7                     15      27      5.225ohm
LP7                     27      0       0.174pH fcheck
L11                     15      16      2.09pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ RTFF         |
** + -------------------- +
** HSTP RTFFb03 2.5mV (betac=2)
** rst (1), din (8), outA (10), outB (16), bias (100)
.subckt sfq_rtff 1 8 17 24 100
LPIN1                   1       2       0.356pH fcheck
LPR1                    2       31      0.172pH fcheck
R1                      31      100     8.34ohm
L8                      2       3       2.527pH fcheck
B11                     3       32      jjmod area=2.16
RS11                    3       32      5.225ohm
LP11                    32      0       0.138pH fcheck
L4                      3       4       4.215pH fcheck
B8                      4       5       jjmod area=1.32
RS8                     4       5       8.56ohm
B9                      5       33      jjmod area=1.20
RS9                     5       33      9.416ohm
LP9                     33      0       1.022pH fcheck
B7                      5       6       jjmod area=1.10
RS7                     5       6       10.273ohm
LEX4                    6       19      1.693pH fcheck

LPIN2                   8       9       0.322pH fcheck
LPR2                    9       34      0.166pH fcheck
R2                      34      100     8.35ohm
L1                      9       10      1.945pH fcheck
B3                      10      35      jjmod area=2.04
RS3                     10      35      5.539ohm
LP3                     35      0       0.135pH fcheck
LEX2                    10      11      1.113pH fcheck
LEX1                    11      12      1.269pH fcheck
B2                      12      13      jjmod area=1.38
RS2                     12      13      8.188ohm
LX2                     13      14      0.824pH fcheck
LPR3                    14      36      0.008pH fcheck
R3                      36      100     11.94ohm
L10                     14      15      4.477pH fcheck
B12                     15      37      jjmod area=1.00
RS12                    15      37      11.3ohm
LP12                    37      0       0.166pH fcheck
L5                      15      16      5.091pH fcheck
B13                     16      38      jjmod area=2.00
RS13                    16      38      5.65ohm
LP13                    38      0       0.122pH fcheck
L9                      16      17      1.849pH fcheck

L2                      11      7       3.026pH fcheck
B5                      7       21      jjmod area=1.05
RS5                     7       21      10.762ohm

LX1                     13      18      1.284pH fcheck
B1                      18      39      jjmod area=1.00
RS1                     18      39      11.3ohm
LP1                     39      0       0.177pH fcheck
L3                      18      19      5.546pH fcheck
LEX3                    19      20      1.134pH fcheck
B6                      20      21      jjmod area=1.32
RS6                     20      21      8.56ohm
LX3                     21      22      1.004pH fcheck
B4                      22      40      jjmod area=1.00
RS4                     22      40      11.3ohm
LP4                     40      0       0.182pH fcheck
L6                      22      23      5.426pH fcheck
B10                     23      41      jjmod area=2.00
RS10                    23      41      5.65ohm
LP10                    41      0       0.125pH fcheck
L7                      23      24      2.09pH fcheck
.ends
** + ---------------------------------- +

*** rtffrh
.subckt rtffrh         18        130        131        99
***       din     dout1     reset
R1                99        25   8.34ohm *FIX
R3                99        37  28.20ohm
R2                99       109   8.34ohm *FIX
LP9              127         0   1.526pH fcheck *FIX
LP11              58         0   0.281pH fcheck
LP10               0       132   0.510pH fcheck
LP4                0       133   0.320pH fcheck
LP3                0       134   0.278pH fcheck
LPIN1            131        84   0.650pH fcheck
LPR1              84        25   5.923pH fcheck
L7                84        60   2.361pH fcheck *MIN=  2.000 *MAX=  2.500
L4               135        60   2.436pH fcheck
L6               105       130   1.737pH fcheck *MIN=  1.400 *MAX=  2.000
L5                81       105   5.366pH fcheck
LX2              136        81   1.953pH fcheck *MIN=  1.500 *MAX=  2.000
LEX4             114       137   1.594pH fcheck *FIX
L3               124       114   4.615pH fcheck
LEX3             138       114   1.183pH fcheck *FIX
LP1              139         0   0.367pH fcheck
LX1              140       124   1.342pH fcheck *FIX
LPR3              37       140   0.086pH fcheck
LEX1              95       141   1.355pH fcheck *FIX
LEX2              95       142   0.276pH fcheck
L2               143        95   2.345pH fcheck
LPR2             144       109   5.262pH fcheck
LPIN2             18       144   0.601pH fcheck
L1               144       143   2.220pH fcheck *MIN=  2.000 *MAX=  2.500
B11               60        58  jjmod area=2.07
*MIN=  1.960 *MAX=  2.160
RS11              60        58   5.45ohm *SHUNT=11.30
B8               135       145  jjmod area=1.21
RS8              135       145   9.34ohm *SHUNT=11.30
B9               145       127  jjmod area=1.04
RS9              145       127  10.87ohm *SHUNT=11.30
B10              105       132  jjmod area=2.02
*MIN=  1.960 *MAX=  2.160
RS10             105       132   5.61ohm *SHUNT=11.30
B3               143       134  jjmod area=2.02
*MIN=  1.960 *MAX=  2.160
RS3              143       134   5.61ohm *SHUNT=11.30
B7               137       145  jjmod area=1.00
RS7              137       145  11.30ohm *SHUNT=11.30
B5               142       136  jjmod area=1.08
RS5              142       136  10.44ohm *SHUNT=11.30
B1               124       139  jjmod area=1.00
RS1              124       139  11.30ohm *SHUNT=11.30
B6               138       136  jjmod area=1.39
RS6              138       136   8.12ohm *SHUNT=11.30
B2               141       140  jjmod area=1.08
RS2              141       140  10.44ohm *SHUNT=11.30
B4                81       133  jjmod area=1.00
RS4               81       133  11.30ohm *SHUNT=11.30
.ends

** + -------------------- +
** |     SFQ DFF          |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (21), din (1), out (9), bias (100)
.subckt sfq_dff 1 21 9 100
LPIN                    21      2       0.328pH fcheck
L7                      2       3       2.756pH fcheck
L5                      3       4       4.508pH fcheck
L2                      4       5       1.508pH fcheck
L3                      5       6       6.373pH fcheck
L9                      6       7       0.042pH fcheck
L4                      7       8       4.641pH fcheck
L8                      8       9       2.405pH fcheck
LPR2                    2       10      0.156pH fcheck
R2                      10      100     8.32ohm
B2                      3       11      jjmod area=2.16
RS2                     3       11      5.225ohm
LP2                     11      0       0.094pH fcheck
B3                      4       12      jjmod area=2.34
RS3                     4       12      4.829ohm
LP3                     12      0       0.104pH fcheck
LPR1                    5       13      0.104pH fcheck
R1                      13      100     21.44ohm
B4                      7       14      jjmod area=1.69
RS4                     7       14      6.686ohm
LP4                     14      0       0.276pH fcheck
B6                      8       15      jjmod area=2.25
RS6                     8       15      5.022ohm
LP6                     15      0       0.127pH fcheck

LPCLK                   1       22      0.361pH fcheck
L6                      22      23      2.535pH fcheck
L1                      23      24      3.302pH fcheck
B1                      24      6       jjmod area=1.63
RS1                     24      6       6.933ohm
LPR3                    22      25      0.159pH fcheck
R3                      25      100     8.32ohm
B5                      23      26      jjmod area=2.16
RS5                     23      26      5.225ohm
LP5                     26      0       0.096pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ RDFF         |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (1), din (21), rst (31), out (12), bias (100)
.subckt sfq_rdff 1 21 31 12 100
LPCLK                   1       2       0.372pH fcheck
L4                      2       3       2.597pH fcheck
L6                      3       4       2.842pH fcheck
B5                      4       5       jjmod area=1.84
RS5                     4       5       6.1336ohm
LPR2                    2       6       0.244pH fcheck
R2                      6       100     8.33ohm
B3                      3       7       jjmod area=2.16
RS3                     3       7       5.225ohm
LP3                     7       0       0.13pH fcheck

L10                     5       10      0.023pH fcheck
L11                     10      11      4.581pH fcheck
L12                     11      12      2.226pH fcheck
B10                     10      13      jjmod area=1.10
RS10                    10      13      10.26ohm
LP10                    13      0       0.198pH fcheck
B11                     11      14      jjmod area=2.16
RS11                    11      14      5.225ohm
LP11                    14      0       0.117pH fcheck

LPDIN                   21      22      0.288pH fcheck
L1                      22      23      2.662pH fcheck
L2                      23      24      4.242pH fcheck
L3                      24      25      3.154pH fcheck
B7                      25      26      jjmod area=1.56
RS7                     25      26      7.2345ohm
L8                      26      5       1.854pH fcheck
LPR1                    22      29      0.229pH fcheck
R1                      29      100     8.33ohm
B1                      23      27      jjmod area=2.16
RS1                     23      27      5.225ohm
LP1                     27      0       0.101pH fcheck
B2                      24      28      jjmod area=1.26
RS2                     24      28      8.957ohm
LP2                     28      0       0.148pH fcheck

LPRESET                 31      32      0.45pH fcheck
L5                      32      33      2.738pH fcheck
L7                      33      34      2.746pH fcheck
B6                      34      35      jjmod area=1.84
RS6                     34      35      6.1336ohm
L9                      35      36      1.966pH fcheck
B8                      36      25      jjmod area=1.56
RS8                     36      25      7.2345ohm
LPR3                    32      39      0.218pH fcheck
R3                      39      100     8.33ohm
B4                      33      37      jjmod area=2.16
RS4                     33      37      5.225ohm
LP4                     37      0       0.127pH fcheck
B9                      35      38      jjmod area=1.70
RS9                     35      38      6.6387ohm                      
LP9                     38      0       0.156pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ NDRO         |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (1), rst (16), din (24), dout (8), bias (100)
.subckt sfq_ndro 1 16 24 8 100
LPCLK                   1       2       0.216pH fcheck
L1                      2       3       2.148pH fcheck
B2                      3       4       jjmod area=1.62
RS2                     3       4       6.967ohm
L2                      4       5       2.967pH fcheck
L13                     5       6       0.918pH fcheck
L11                     6       7       5.338pH fcheck
L12                     7       8       2.062pH fcheck

LPR1                    2       9       0.198pH fcheck
RB1                     9       100     8.34ohm
B1                      3       10      jjmod area=2.10
RS1                     3       10      5.374ohm
LP1                     10      0       0.164pH fcheck
B10                     6       11      jjmod area=1.75
RS10                    6       11      6.45ohm
LP10                    11      0       0.164pH fcheck
B11                     7       12      jjmod area=2.03
RS11                    7       12      5.56ohm
LP11                    12      0       0.12pH fcheck

LPRST                   16      17      0.216pH fcheck
L3                      17      18      2.551pH fcheck
L4                      18      19      3.003pH fcheck
B4                      19      20      jjmod area=2.25
RS4                     19      20      5.016ohm
L8                      20      30      3.021pH fcheck

LPR2                    17      21      0.198pH fcheck
RB2                     21      100     8.34ohm
B3                      18      22      jjmod area=2.18
RS3                     18      22      5.177ohm
LP3                     22      0       0.148pH fcheck
B5                      20      23      jjmod area=2.72
RS5                     20      23      4.15ohm
LP5                     23      0       0.159pH fcheck

LPDIN                   24      25      0.237pH fcheck
L5                      25      26      2.223pH fcheck
L6                      26      27      3.96pH fcheck
B7                      27      28      jjmod area=2.03
RS7                     27      28      5.56ohm
L14                     28      29      0.85pH fcheck
L7                      29      30      3.598pH fcheck
B9                      30      31      jjmod area=1.00
RS9                     30      31      11.286ohm
L9                      31      32      0.497pH fcheck
L10                     32      5       0.45pH fcheck

LPR3                    25      34      0.2pH fcheck
RB3                     34      100     8.34ohm
B6                      26      35      jjmod area=2.17
RS6                     26      35      5.201ohm
LP6                     35      0       0.127pH fcheck
B8                      28      36      jjmod area=1.32
RS8                     28      36      8.55ohm
LP8                     36      0       0.172pH fcheck
LPR4                    29      37      0.434pH fcheck
RB4                     37      100     24ohm
LPR5                    32      38      0.07pH fcheck
RB5                     38      100     22.98ohm
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ AND          |
** + -------------------- +
** 2.5mV (betac=2)
** clk (1), din1 (11), din2 (21), out (35), bias (100)
.subckt sfq_and 1 11 21 35 100
LPCLK                   1       2       0.237pH fcheck
LPR5                    2       74      0.198pH fcheck
RB5                     74      100     8.32ohm
L9                      2       3       2.14pH fcheck
L10                     3       4       5.255pH fcheck
LPR6                    4       73      0.198pH fcheck
RB6                     73      100     23.2ohm
L11                     4       5       0.803pH fcheck
L12                     5       6       0.65pH fcheck
L13                     6       7       3.429pH fcheck
B7                      7       8       jjmod area=1.0
RS7                     7       8       11.3ohm
L14                     6       9       3.476pH fcheck
B8                      9       10      jjmod area=1.0
RS8                     9       10      11.3ohm
B5                      3       72      jjmod area=2.16
RS5                     3       72      5.225ohm
LP5                     72      0       0.083pH fcheck
B6                      5       71      jjmod area=1.4
RS6                     5       71      8.06ohm
LP6                     71      0       0.177pH fcheck

LPA                     11      12      0.192pH fcheck
LPR1                    12      95      0.231pH fcheck
RB1                     95      100     8.32ohm
L1                      12      13      2.239pH fcheck
L3                      13      14      4.766pH fcheck
L5                      14      15      2.077pH fcheck
LPR3                    15      94      0.179pH fcheck
RB3                     94      100     22.0ohm
L7                      15      8       9.428pH fcheck
L15                     8       16      0.512pH fcheck
L17                     16      17      2.592pH fcheck
B11                     17      31      jjmod area=1.3
RS11                    17      31      8.68ohm
B1                      13      93      jjmod area=2.16
RS1                     13      93      5.225ohm
LP1                     93      0       0.117pH fcheck
B3                      14      92      jjmod area=1.75
RS3                     14      92      6.45ohm
LP3                     92      0       0.148pH fcheck
B9                      16      91      jjmod area=1.2
RS9                     16      91      9.40ohm
LP9                     91      0       0.216pH fcheck

LPB                     21      22      0.195pH fcheck
LPR2                    22      85      0.229pH fcheck
RB2                     85      100     8.32ohm
L2                      22      23      2.244pH fcheck
L4                      23      24      4.787pH fcheck
L6                      24      25      2.083pH fcheck
LPR4                    25      84      0.179pH fcheck
RB4                     84      100     22.0ohm
L8                      25      10      9.399pH fcheck
L16                     10      26      0.473pH fcheck
L18                     26      27      2.608pH fcheck
B12                     27      31      jjmod area=1.3
RS12                    27      31      8.68ohm
B2                      23      83      jjmod area=2.16
RS2                     23      83      5.225ohm
LP2                     83      0       0.117pH fcheck
B4                      24      82      jjmod area=1.75
RS4                     24      82      6.45ohm
LP4                     82      0       0.148pH fcheck
B10                     26      81      jjmod area=1.2
RS10                    26      81      9.40ohm
LP10                    81      0       0.237pH fcheck

L19                     31      32      0.803pH fcheck
L20                     32      33      0.793pH fcheck
LPR7                    33      63      0.159pH fcheck
RB7                     63      100     28.96ohm
L21                     33      34      4.134pH fcheck
L22                     34      35      1.971pH fcheck
B13                     32      62      jjmod area=1.78
RS13                    32      62      6.34ohm
LP13                    62      0       0.294pH fcheck
B14                     34      61      jjmod area=2.16
RS14                    34      61      5.225ohm
LP14                    61      0       0.133pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ OR           |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (1), din1 (7), din2 (16), out (34), bias (100)
.subckt sfq_or 1 7 16 34 100
LPCLK                   1       2       0.265pH fchec
LPR5                    2       5       0.208pH fcheck
RB5                     5       100     8.34ohm
L16                     2       3       2.449pH fcheck
L17                     3       4       2.301pH fcheck
B12                     4       21      jjmod area=1.5
RS12                    4       21      7.524ohm
B11                     3       6       jjmod area=2.16
RS11                    3       6       5.225ohm
LP11                    6       0       0.172pH fcheck

LPIN1                   7       8       0.289pH fcheck
LPR2                    8       13      0.205pH fcheck
RB2                     13      100     8.34ohm
L8                      8       9       2.499pH fcheck
L1                      9       10      3.614pH fcheck
L5                      10      11      1.745pH fcheck
B3                      11      12      jjmod area=1.63
RS3                     11      12      6.924ohm
B6                      9       14      jjmod area=2.16
RS6                     9       14      5.225ohm
LP6                     14      0       0.101pH fcheck
B1                      10      15      jjmod area=2.47
RS1                     10      15      4.569ohm
LP1                     15      0       0.14pH fcheck

LPIN2                   16      17      0.289pH fcheck
LPR3                    17      22      0.205pH fcheck
RB3                     22      100     8.34ohm
L9                      17      18      2.499pH fcheck
L2                      18      19      3.614pH fcheck
L6                      19      20      1.745pH fcheck
B4                      20      12      jjmod area=1.63
RS4                     20      12      6.924ohm
B7                      18      23      jjmod area=2.16
RS7                     18      23      5.225ohm
LP7                     23      0       0.101pH fcheck
B2                      19      24      jjmod area=2.47
RS2                     19      24      4.569ohm
LP2                     24      0       0.138pH fcheck

L7                      12      25      0.45pH fcheck
LPR1                    25      29      0.036pH fcheck
RB1                     29      100     10.83ohm
L10                     25      26      5.13pH fcheck
B5                      26      27      jjmod area=1.72
RS5                     26      27      6.562ohm
L11                     27      28      1.57pH fcheck
LPR4                    28      30      0.211pH fcheck
RB4                     30      100     32.3ohm
L12                     28      21      9.532pH fcheck
B8                      27      31      jjmod area=1.38
RS8                     27      31      8.178ohm
LP8                     31      0       0.122pH fcheck

L13                     21      32      0.226pH fcheck
L14                     32      33      4.664pH fcheck
L15                     33      34      2.246pH fcheck
B9                      32      35      jjmod area=1.32
RS9                     32      35      8.55ohm
LP9                     35      0       0.216pH fcheck
B10                     33      36      jjmod area=2.16
RS10                    33      36      5.225ohm
LP10                    36      0       0.133pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ XOR          |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (1), din1 (7), din2 (18), out (33), bias (100)
.subckt sfq_xor 1 7 18 33 100
** clock
LPCLK                   1       2       0.328pH fchec
LPR5                    2       5       0.211pH fcheck
RB5                     5       100     8.32ohm
L11                     2       3       2.545pH fcheck
B9                      3       4       jjmod area=1.69
RS9                     3       4       6.678ohm
L10                     4       30      3.791pH fcheck
B10                     3       6       jjmod area=2.17
RS10                    3       6       5.201ohm
LP10                    6       0       0.148pH fcheck

** dinA
LPA                     7       8       0.322pH fcheck
LPR1                    8       14      0.169pH fcheck
RB1                     14      100     8.32ohm
L1                      8       9       2.608pH fcheck
L2                      9       10      4.051pH fcheck
B3                      10      11      jjmod area=1.69
RS3                     10      11      6.678ohm
L3                      11      12      1.097pH fcheck
LPR3                    12      15      0.338pH fcheck
RB3                     15      100     29.6ohm
L7                      12      13      2.613pH fcheck
B1                      9       16      jjmod area=2.18
RS1                     9       16      5.177ohm
LP1                     16      0       0.122pH fcheck
B2                      10      17      jjmod area=1.89
RS2                     10      17      5.971ohm
LP2                     17      0       0.148pH fcheck

** dinB
LPB                     18      19      0.325pH fcheck
LPR2                    19      25      0.169pH fcheck
RB2                     25      100     8.32ohm
L4                      19      20      2.603pH fcheck
L5                      20      21      4.15pH fcheck
B6                      21      22      jjmod area=1.69
RS6                     21      22      6.678ohm
L6                      22      23      1.092pH fcheck
LPR4                    23      26      0.338pH fcheck
RB4                     26      100     29.6ohm
L8                      23      13      2.608pH fcheck
B4                      20      27      jjmod area=2.18
RS4                     20      27      5.177ohm
LP4                     27      0       0.117pH fcheck
B5                      21      28      jjmod area=1.89
RS5                     21      28      5.971ohm
LP5                     28      0       0.143pH fcheck

B7                      13      29      jjmod area=1.96
RS7                     13      29      5.758ohm
L9                      29      30      1.443pH fcheck
L12                     30      31      0.117pH fcheck
L13                     31      32      4.995pH fcheck
L14                     32      33      2.215pH fcheck
B8                      31      35      jjmod area=1.63
RS8                     31      35      6.924ohm
LP8                     35      0       0.12pH fcheck
B11                     32      36      jjmod area=2.18
RS11                    32      36      5.177ohm
LP11                    36      0       0.138pH fcheck
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ NOT          |
** + -------------------- +
** HSTP 2.5mV (betac=2)
** din (25), dout (26), clk (1), bias (34)
.subckt sfq_not   25 26 1 34
***         a         c       clk
Rd                27         0   3.51ohm *FIX
R4                34         9   8.32ohm *FIX
R1                34        30  26.40ohm
R7                34        32  29.44ohm
R2                34        11  37.04ohm
R3                34        35   8.32ohm *FIX
LP10              36         0   0.263pH fcheck
LP9               37         0   0.218pH fcheck
LP6               38         0   0.244pH fcheck
L10               24        39   5.340pH fcheck
L15               39        26   1.854pH fcheck *FIX
L19               40        27   2.571pH fcheck *FIX
L16               41        42   2.847pH fcheck *FIX
LPR4               9        41   3.591pH fcheck
L17               43        44   0.135pH fcheck
LP7               45         0   0.195pH fcheck
L12               20        19   1.773pH fcheck *MIN=  0.500
L2                21        46   1.256pH fcheck *MIN=  0.900
L14               42        20   3.575pH fcheck
LPR1              30        21   0.278pH fcheck
LP8               47         0   0.221pH fcheck
L6                48        49   3.975pH fcheck
LP4                6         0   0.312pH fcheck
L5                44        48   4.501pH fcheck
L1                44        21   0.884pH fcheck *MIN=  0.800
LP11              50         0   0.216pH fcheck
L11               19        51   2.389pH fcheck
L8                52        51   1.180pH fcheck *MIN=  0.800
L3                49        53   2.883pH fcheck
LPR2              11        53   0.270pH fcheck
LP5               54         0   0.276pH fcheck
L4                53        55   2.400pH fcheck
L7                56        57   1.141pH fcheck *MIN=  0.800
L9                57        24   0.231pH fcheck
LPR7              32        19   0.341pH fcheck
L18               51        40   0.361pH fcheck
LPA               25        41   0.842pH fcheck
L13               58        43   2.348pH fcheck *FIX
LPR3              35        58   3.172pH fcheck
LPCLK              1        58   0.832pH fcheck
B10               40        36  jjmod area=2.37
RS10              40        36   4.76ohm *SHUNT=11.30
B6                24        38  jjmod area=1.17
RS6               24        38   9.69ohm *SHUNT=11.30
B9                39        37  jjmod area=2.13
*FIX
RS9               39        37   5.30ohm *SHUNT=11.30
B7                43        45  jjmod area=2.13
*FIX
RS7               43        45   5.30ohm *SHUNT=11.30
B8                20        47  jjmod area=1.90
RS8               20        47   5.93ohm *SHUNT=11.30
B4                48         6  jjmod area=1.21
RS4               48         6   9.34ohm *SHUNT=11.30
B11               42        50  jjmod area=2.13
*FIX
RS11              42        50   5.30ohm *SHUNT=11.30
B3                52        55  jjmod area=1.44
RS3               52        55   7.85ohm *SHUNT=11.30
B1                57        46  jjmod area=1.69
RS1               57        46   6.69ohm *SHUNT=11.30
B5                49        54  jjmod area=1.04
RS5               49        54  10.87ohm *SHUNT=11.30
B2                56        55  jjmod area=1.39
RS2               56        55   8.12ohm *SHUNT=11.30
.ends
** + ---------------------------------- +

** + -------------------- +
** |     SFQ T1           |
** + -------------------- +
** ADP2 2.5mV (betac=2)
** clk (1), din (16), sum (8), carry (24), bias (100)
.subckt sfq_t1 1 16 8 24 100
LPIN1                   1       2       0.166pH fcheck
L8                      2       3       2.278pH fcheck
L4                      3       4       2.369pH fcheck
B8                      4       5       jjmod area=1.68
RS8                     4       5       6.718ohm
LX3                     5       6       1.027pH fcheck
L5                      6       7       5.447pH fcheck
L9                      7       8       2.033pH fcheck
LPR1                    2       9       0.239pH fcheck
RB1                     9       100     8.35ohm
B11                     3       10      jjmod area=2.1
RS11                    3       10      5.374ohm
LP11                    10      0       0.164pH fcheck
B9                      6       11      jjmod area=1.0
RS9                     6       11      11.29ohm
LP9                     11      0       0.164pH fcheck
B12                     7       12      jjmod area=2.0
RS12                    7       12      5.643ohm
LP12                    12      0       0.12pH fcheck

B7                      5       13      jjmod area=1.0
RS7                     5       13      11.29ohm
LEX4                    13      14      1.027pH fcheck
LEX3                    14      15      1.336pH fcheck
B6                      15      21      jjmod area=1.43
RS6                     15      21      7.893ohm
L3                      29      14      5.359pH fcheck
* L3                      14      29      5.359pH fcheck
LX1                     29      30      1.37pH fcheck
B2                      30      31      jjmod area=1.05
RS2                     30      31      10.75ohm
LEX1                    31      19      1.264pH fcheck
B1                      29      32      jjmod area=1.21                                                
RS1                     29      32      9.328ohm
LP1                     32      0       0.151pH fcheck
LPR3                    30      33      0.229pH fcheck
RB3                     33      100     17.93ohm

LPIN2                   16      17      0.208pH fcheck
L1                      17      18      2.015pH fcheck
L2                      18      19      2.09pH fcheck
LEX2                    19      20      1.027pH fcheck
B5                      20      21      jjmod area=1.21
RS5                     20      21      9.328ohm
LX2                     21      22      1.261pH fcheck
L6                      22      23      4.654pH fcheck
L7                      23      24      2.07pH fcheck
LPR2                    17      25      0.218pH fcheck
RB2                     25      100     8.35ohm
B3                      18      26      jjmod area=2.1
RS3                     18      26      5.374ohm
LP3                     26      0       0.159pH fcheck
B4                      22      27      jjmod area=1.05
RS4                     22      27      10.75ohm
LP4                     27      0       0.151pH fcheck
B10                     23      28      jjmod area=2.0
RS10                    23      28      5.643ohm
LP10                    28      0       0.112pH fcheck
.ends
** + ---------------------------------- +
