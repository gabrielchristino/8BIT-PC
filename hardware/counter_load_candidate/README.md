# Banco X candidato — esquema parcial

`counter_load_bank.kicad_sch` contém quatro SN74HC191, quatro SN74HC157, dois SN74HC377 e dez capacitores de desacoplamento propostos. Os pinos foram mapeados aos datasheets TI; a exportação KiCad é comparada automaticamente com `pinmap.csv`.

As entradas do controle, habilitações, clock e EA são interfaces externas. Não há ainda portas de encadeamento, sequenciador físico, conectores, footprints ou PCB completos. **Não fabricar a partir deste arquivo.**

Ver `docs/engineering/REV9842.md` para resultados, contrato de carga, limitações e próximos passos. Os símbolos gráficos vêm das bibliotecas KiCad 7.0.11, com pinagem conferida e valores HC; créditos e licença originais do pacote constam em `references/KICAD_SYMBOLS_COPYRIGHT.txt`.
