                       LED_ADDR    EQU     0FFF80000
                       SW_ADDR     EQU     0FFF81000
                       
                                   ORG 0
00000000  11 00 00 04              MOVE 011, R0
00000004  AA 00 00 05              MOVE 0AA, R2
00000008  00 00 08 B8              STORE R0, (LED_ADDR)
0000000C  11 00 00 24              ADD R0, 11, R0
00000010  00 00 08 B8              STORE R0, (LED_ADDR)
00000014  11 00 00 24              ADD R0, 11, R0
00000018  00 30 00 B9              STORE R2, (3000)
0000001C  00 00 08 B8              STORE R0, (LED_ADDR)
00000020  11 00 00 24              ADD R0, 11, R0
00000024  00 30 80 B0              LOAD R1, (3000)
00000028  00 00 08 B8              STORE R0, (LED_ADDR)
0000002C  00 00 88 B8              STORE R1, (LED_ADDR)
00000030  00 00 00 F8              HALT
