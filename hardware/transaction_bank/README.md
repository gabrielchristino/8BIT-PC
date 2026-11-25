# Transações e payload NET-03

`transaction_bank.kicad_sch` é o esquema nativo; `transaction_bank_netlist.sv` deriva do XML exportado pelo KiCad. A máquina de estados é conectada por portas e um HC174, com ACK em dois HC74 e payload/MDR em cinco HC377. Dois HC125 distribuem clock e clear/qualificadores.

START/READY/DONE são uma interface síncrona. REQUEST/ACK usam quatro fases. Endereço/dado/modo ficam retidos, e START mantido não repete. Após reset, o payload sem clear é inválido até a primeira captura. As portas exigem níveis CMOS; adaptação TTL/CMOS e supervisão analógica não estão fechadas.

**Parcial, sem liberação para fabricação.** Ver [NET03.md](../../docs/engineering/NET03.md) e `verification/net03/`. Não interpretar comparação de pinagem ou orçamento de capacitância como ERC/DRC ou temporização global aprovada.
