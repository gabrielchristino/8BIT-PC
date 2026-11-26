# Evidências intermediárias — não aprovações

Os caminhos em JSON identificam os nomes usados naquele momento; seus hashes
não devem ser comparados aos arquivos finais e chamados de falha histórica.
O manifesto NET25 preserva os bytes destes registros. Nenhum resultado aqui
substitui as rodadas finais ou a rejeição explícita de uma hipótese.

- `initial-gated-checks`:32casos com checks de phase/warm condicionados a RAW;
  guardas depois ficaram sempre ativos, e a rodada final foi repetida.
  A cópia do vídeo identifica os pinos e monitores daquela execução.
- `calibration-clear-stimulus`: bancada inicial não produzia uma borda real
  de clear. Esperava Q conhecido sem esse estímulo e falhou. Correção somente
  no testbench(clear inicialmente1 e pulso explícito); modelo não mudou.
- `old-recovery-counter`: compilação ainda usava U8_0/U8_1 do antigo AHC74.
  Primeira adaptação buscou expressão somada inexistente; o segundo resultado
  falho e seu runner estão em `retry`. A correção final usa contadores reais
  U8.recovery_events e U8.setup_events, com rótulos correspondentes.
- `pre-adapter-metadata`: a primeira CPU executou corretamente, mas o script
  de preparação listado como fonte foi ajustado durante o trabalho para os
  contadores dos outros ensaios. Não se troca o hash retroativamente. O
  preparo final foi executado com as fontes congeladas e a CPU foi repetida;
  só o relatório da raiz é regressão final. O preparo original está em
  `old-recovery-counter/prepare_phase_drain_system.py`.
- `short-initial-raw`: pulso de partida12ns não atende hipótese inicial do
  RC/supervisor; watchdog não é aprovação de POR. Não foi corrigido circuito
  para prometer partida com esse pulso. Cenários seguintes usam60us/12ms.
- `strict-cold-clock`: rejeição verdadeira do monitor original7,722ns/20ns,
  CLR0. Não há correção nessa variante. A projeção diagnóstica posterior só
  permite examinar contenção sob reset conhecido e mantém esse clock aberto.
- `hypothesis-power-fixture`: semente de estadoP1 em0,001ns antecedeu a
  qualificação de SAFE e foi monitorada como operação válida. Na hipótese
  posterior, checks da nova dupla usam o mesmo qualificador RAW/power do
  vídeo. Demais predicados e fronteiras binárias são explícitos; resultado
  não vira aprovação de VDD inválido/POR.

`drain-startup.json`, na raiz, **continua falhando** no primeiro recovery
de RAW50ns/offset39. Os relatórios das hipóteses apenasHDL pertencem a circuitos
simulados distintos, sem esquema próprio; não corrigem retroativamente essa
folha nem os registros originais.
