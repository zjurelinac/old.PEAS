                       	ORG 0
00000000  00 00 81 07  	MOVE 10000, SP
00000004  01 00 00 24  	ADD R0, 1, R0
00000008  14 00 80 00      MOVE ADDR, R1
0000000C  14 00 80 B0      LOAD R1, (ADDR)
00000010  00 00 00 F8  	HALT
                       
00000014  01 00 00 00  ADDR DW 
