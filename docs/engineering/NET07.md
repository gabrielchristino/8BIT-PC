# NET-07 — PC e seleção de endereços

25/11/2026, desenvolvimento novo sobre NET-06 `d876dc6499c49b937c2dfd318abe605eea0497e3`. Fontes anteriores e ROMs permanecem intactas. Não é liberação de fabricação.

Dois SN74HC273 mantêm PC. Quatro CD74HC283 em cascata calculam PC+1, incluindo FFFFh→0000h. HC157 selecionam incremento/EA e retenção/carga; portas usam o PC_N já decodificado na NET-04 e Z anterior à borda. Modo PC=1 incrementa, 2 salta para EA, 3 salta quando Z, 4 quando não Z; demais códigos retêm. EXEC_ENABLE qualificado, reset e POWER_GOOD digitais bloqueiam carga indevida. Não há clock gated. A árvore de endereço seleciona zero/PC/EA/X/SP/SP±1/zero/zero, preservando as convenções anteriores. A transação NET-03 captura esse endereço antes de REQUEST/WAIT; a seleção combinacional não substitui esse armazenamento.

O banco tem 45 CIs (2 HC273, 4 HC283, 32 HC157, 3 HC125, 2 HC08, 1 HC32 e 1 HC04), mais 45 capacitores propostos de 100 nF: 90 componentes, 804 pinos e 10 saídas NC. Até quatro entradas digitais por net interna, com orçamento de 10 pF por entrada mais 10 pF de interligação. Cargas entre blocos, layout e orçamento global continuam pendentes; não há alegação de otimização/BOM final.

Esquema nativo, mapa de pinos e XML em `hardware/address_bank` e `verification/net07`; o HDL deriva dos nós de pinos exportados pelo KiCad. A folha A1 foi renderizada e inspecionada. Os checks verificam pinos/alimentação/drivers/fanout, não ERC. Datasheets TI existentes são reutilizados sem alterar bytes: HC273/283/157/125/08/32/04, com URLs e hashes no manifesto.

Reproduzir no WSL Ubuntu, na raiz:

```text
python3 tools/build_address_bank.py
python3 tools/make_address_cpu.py
python3 tools/run_address_netlist.py
python3 tools/record_net07_manifest.py
python3 tools/record_net07_manifest.py --check
```

O relatório `results.json` registra versões, comandos, saídas, duração e fontes. As fixtures temporárias semeiam PC nos Q dos dois HC273; não são portas físicas. Outros adaptadores de fixture são os das etapas anteriores. O programa de boot usa reset e memória, sem sementes arquiteturais.

- Ideal e com atrasos selecionados: 65.536 PC × 8 modos × 2 Z × 2 enables = 2.097.152 casos por modo. EA varia com padrão XOR; isso não exaure todos os pares PC/EA, mas exercita todos os bits e valores de PC. Seleção de endereços: 65.536 padrões × 8 origens = 524.288 casos por modo, com fontes diferenciadas e teste dos códigos inativos. Clear e alimentação digital insegura também são conferidos.
- Integração nas duas configurações de X: 6.886 casos de instruções/13.406 transações por configuração, segurança digital, 524.288 guardas, boot com 132.197 instruções/232.576 transações e quadro de 76.800 pixels idêntico à referência. Ambas as comparações de quadro são verdadeiras.
- Falhas deliberadas: carry-in do primeiro somador preso em zero é detectado; clear do registrador aberto é rejeitado pelo conversor.

O cenário isolado usa intervalos de 1 µs, CQ/clear HC273 40 ns, soma 58 ns/carry 49 ns, mux 38 ns, buffer 36 ns, inversor 24 ns e portas 31 ns conservadores. São atrasos constantes selecionados, sob as condições documentadas anteriormente para HC a 4,5 V, −40..85 °C e até 50 pF. Monitores HC273 exigem setup/recovery 25 ns, clock/clear mínimos 20 ns e hold de dados zero, com exclusão inicial conforme o modelo. A integração usa modelos funcionais sem atrasos. Isso não fecha mínimos/skew, reset analógico, carga real, clock ou frequência máxima da placa.

Controle de execução/guardas/fault e parte do X ainda eram RTL nesta base; NET-08 é trabalho separado para removê-los. Memórias, periféricos, USB-C/reset, circuito completo, ERC/DRC, PCB e protótipo continuam necessários. `diagnostic.asm` histórico continua ausente; não se promove o diagnóstico novo a arquivo recuperado. Manifestos anteriores são auditados em seus respectivos commits, sem reescrever hashes antigos.
