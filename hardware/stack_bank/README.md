# Banco SP candidato NET-02

`stack_bank.kicad_sch` é o esquema nativo. `stack_bank_netlist.sv` é gerado a partir do XML realmente exportado pelo KiCad, não escrito como segunda representação independente. `package-functions.json` identifica a pinagem por função; `pinmap.csv` registra cada conexão.

Dois HC273, quatro HC157, quatro CD74HC283, HC04 e HC125, com doze desacoplamentos propostos. SP arquitetural vazio = 8000h; somente o armazenamento do bit 15 é invertido. UPDATE, DOWN, clock, clear, guardas e latch de barramento dependem de controle externo.

**Parcial, sem liberação para produção.** Ver [relatório NET-02](../../docs/engineering/NET02.md), saídas e limites em `verification/net02/`. Os modelos não conferem capacitâncias, níveis analógicos, footprints, PCB ou ERC/DRC.
