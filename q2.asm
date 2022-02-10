.load 3 2
.store 3 2
.mult 2 6
.add 2 1
.div 0 6
LD  F1, 34(F0)
LD  F2, 45(F0)
ADDD F1, F1, 3
MULTD F2, F1, F2
SD F0, (F2)
ADDD F0, F0, 4
LD F1, 34(F0)
LD F2, 45(F0)
ADDD F1, F1, 3
MULTD F2, F1, F2
SD F0, (F2)