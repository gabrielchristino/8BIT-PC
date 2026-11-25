# ALU combinacional NET-05

Banco parcial de 8 bits, 49 CIs, com soma/subtração compartilhada, portas e distribuição de sinais. O HDL é gerado das conexões do XML exportado pelo KiCad. Construção: `python3 tools/build_alu_bank.py`; integração: `python3 tools/make_alu_cpu.py`; testes: `python3 tools/run_alu_netlist.py` no WSL Ubuntu.

Ver [relatório NET-05](../../docs/engineering/NET05.md) e `verification/net05/`. Não inclui os registradores de A/B/flags nem aprovação de fabricação. Pinagem/labels completos; footprints, ERC/DRC, elétrica e temporização global pendentes.
