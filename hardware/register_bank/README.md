# Registradores e seleção de dados NET-06

Banco parcial: A/B/EA em HC273 com realimentação HC157, Z/C em HC74 e seleção interna de dados. São 40 CIs, sem aprovação de BOM/layout ou fabricação. O HDL deriva dos pinos do XML exportado pelo KiCad.

Construir com `tools/build_register_bank.py`, adaptar CPU com `tools/make_register_cpu.py` e testar com `tools/run_register_netlist.py`, no WSL Ubuntu. Evidências em `verification/net06`; escopo, comandos e limitações no [relatório NET-06](../../docs/engineering/NET06.md).
