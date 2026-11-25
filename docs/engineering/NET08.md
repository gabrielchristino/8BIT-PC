# NET-08 — execução, guardas de pilha e falhas

25/11/2026. Trabalho novo sobre NET-07 `50a923cd3d60bb4943030934140d8336be4ddf42`, mantendo as fontes anteriores. O esquema parcial contém dois HC174 para fases/flags e portas HC08/32/04 com buffers HC125: 51 CIs, 51 capacitores propostos, 102 componentes, 820 pinos e 13 saídas NC. O HDL vem dos pinos do XML KiCad. A folha A1 foi renderizada e inspecionada. Não há liberação para fabricação.

RESPONSE, DROP e X_LOAD são bits registrados; EXEC é implícito quando todos estão zero. RESPONSE mantém START até BUS_DONE, DROP aguarda BUS_READY e CONTROL_READY antes do avanço. X_LOAD mantém o pedido; X_COMPLETED retém uma conclusão ocorrida durante RUN pausado. STACK_CHECKED, HALTED, FAULT e RETIRED passam a registros físicos. O clock é positivo e distribuído, sem gated clock. A decodificação ADDR_N/MEM_N/X_N da NET-04 é reutilizada. SP_UPDATE continua qualificado pelo controle NET-04; endereço/payload ficam retidos pela NET-03 durante WAIT.

Os limites de SP são portas binárias explícitas, não comparações HDL: SP=0, SP>8000h, SP<4000h, SP≤4000h, SP<2, SP<4002h e SP>7FFEh. CALL/RET testam dois bytes antes do primeiro acesso quando STACK_CHECKED=0; os bytes seguintes usam os limites unitários. Isso preserva a política E04. Push inválido gera FAULT=1, pop inválido FAULT=2, HALT para opcode diferente de FFh gera FAULT=3. RETIRED dura um ciclo; em DROP pode ocorrer mesmo com RUN pausado, preservando a conclusão já aceita. Estado inválido por perturbação física/SEU não tem prova de recuperação automática.

Todos os sinais internos têm até quatro entradas digitais, com orçamento de 10 pF por entrada mais 10 pF de interligação. Cargas externas, ruído, reset analógico, mínimos/skew e temporização completa continuam pendentes. Capacitores são propostas, sem layout dimensionado. Não se alega otimização de BOM.

Na primeira integração, MEM_N_0 foi interpretado com polaridade incorreta. Como Y0 é ativo em nível baixo para mem=0, ele fica alto em operações de memória. O erro fez FETCH avançar antes da leitura. A correção foi feita somente na nova versão; `initial-integration-failure.json` e `memory-decode-trace-failure.json` preservam a falha e o rastreamento intermediários, com seus hashes próprios. Esses logs não são aprovação das fontes finais. Erros de montagem do gerador (nome de net passado como entrada e capacidade gráfica) também foram resolvidos antes da aceitação, sem alterar as bases históricas.

Reproduzir no WSL Ubuntu:

```text
python3 tools/build_execution_bank.py
python3 tools/make_execution_cpu.py
python3 tools/run_execution_unit.py
python3 tools/run_execution_netlist.py
python3 tools/record_net08_manifest.py
python3 tools/record_net08_manifest.py --check
```

`unit-results.json` e `results.json` registram comandos, versões/fontes/hashes, saídas e durações. A integração principal contém sete configurações completas; `--quick` não é aceitação. `--trace` é auxílio de diagnóstico e não foi usado para substituir resultados finais. Fixtures de pilha agora semeiam STACK_CHECKED em Q do HC174; as demais sementes físicas seguem as etapas anteriores. Sementes não são portas reais. Firmware de boot parte de reset normal.

- Banco isolado ideal e com atrasos: 1.048.576 casos de guardas por modo (todo SP, overlay, quatro operações, primeiro/segundo byte), 256 códigos em HALT e 18 verificações dirigidas de handshake/pausa/retorno de X. Não são todas as sequências possíveis de controle ou perturbações assíncronas.
- Duas falhas deliberadas no relatório isolado: D de RESPONSE preso em zero causa divergência; clear desconectado é rejeitado pelo conversor. Os dois testes devem falhar pelo motivo esperado.
- Integração: 6.886 casos das 26 instruções/13.406 transações por configuração de X; reset/alimentação digital/pausa/WAIT; 524.288 guardas; programa completo com 132.197 instruções, 232.576 transações e quadro de 76.800 pixels idêntico à referência nas duas configurações.

O cenário temporizado isolado usa intervalos de 1 µs; HC174 CQ/clear 40 ns, portas de duas entradas conservadoramente 31 ns, inversão 24 ns e buffers 36 ns. Os monitores reutilizados exigem dados/setup e clear/recovery 25 ns e clock/clear mínimos 20 ns, com exclusão inicial explícita do modelo. Esses são limites selecionados sob condições anteriores de HC, não simulação elétrica. A integração usa modelos funcionais sem atrasos; não certifica frequência da placa. Os datasheets TI HC174/08/32/04/125 já arquivados permanecem intactos e são identificados por URL/hash no manifesto.

X ainda possui alternativa procedural/HC191 de comparação nesta base; NET-09 é a etapa separada de X síncrono por pinos. Memória, arbitragem, vídeo/teclado, USB-C/reset/clock e a união elétrica/temporal de todos os blocos continuam necessários, seguidos de ERC, layout, DRC e protótipo. O diagnóstico histórico continua ausente. Nenhum resultado digital equivale a ensaio físico.
