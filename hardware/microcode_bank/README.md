# Banco de microcódigo NET-04

Esquema parcial nativo KiCad e simulação dos pacotes gerada do XML exportado, não um circuito completo liberado para fabricação. Base, construção, resultados e limites em [NET04.md](../../docs/engineering/NET04.md).

`tools/build_microcode_bank.py` gera os símbolos de pacote, esquema, mapa de pinos e exporta XML/PDF; converte as conexões em `microcode_bank_netlist.sv`. `design.json` e `package-functions.json` descrevem o banco. Evidências e hashes estão em `verification/net04/`. EEPROMs são candidatas AT28HC64B-120 em modo somente leitura; encapsulamentos/BOM/layout finais continuam pendentes.
