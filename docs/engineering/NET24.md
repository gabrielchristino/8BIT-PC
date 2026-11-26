# NET-24 — Relógio comum do sincronizador de pedidos

26/11/2026. Base `c54226afed52e04c787b91c65dc29cfacf8f661e` (NET23).
**Regressões funcionais aprovadas no escopo descrito; falha de largura de
pulso durante reset ainda aberta. Placa não liberada.**

## Mudança nativa e razão

O primeiro estágio do sincronizador HC74 recebia BUF_3_3; o segundo, BUF_3_4.
Com buffers distintos, relógios próximos não garantem a separação temporal
entre os dois estágios. A folha `hardware/common_request` muda somente U4
pinos3/11 para BUF_4_1, compartilhado com o MDR. Não muda dados, resets, portas
lógicas, estados, memória, CPU ou componentes.

São **62 componentes, 31 CIs, 526 pinos e nove NC**. XML KiCad confere todos
os pinos/valores. O comparador `topology.json` demonstra exatamente essas duas
diferenças. Os três grupos de clock passam a três pinos cada: estados,
payload e sincronizador/MDR. Orçamento de40pF por grupo (10pF/entrada na
condição selecionada mais10pF de trilhas), abaixo de50pF. Não é extração de PCB
ou qualificação de skew entre pinos físicos.

[HC74 SCLS094F](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), tabela74,
4,5V/−40…85°C: setup25ns, hold0ns, recovery6ns, pulso mínimo20ns e CLK–Q
máximo44ns. O datasheet não dá CLK–Q mínimo. O ensaio usa6ns como valor
ilustrativo não excluído pelo limite máximo, sem afirmar que seja típico,
garantido ou medido numa unidade.

Na projeção do circuito antigo, primeiro clock1ns/segundo8,5ns e primeiro
CQ6ns geram rejeição do monitor de setup do segundo estágio. Cinco cenários
de comparação passam. Na nova projeção,32 combinações de três buffers1/8,5ns
e primeiroCQ0/1/6/44ns passam. A reversão de um único clock volta a provocar
a mesma rejeição. O primeiro REQ foi mantido estável antes da amostragem;
esse ensaio não depende de provocar metastabilidade no primeiro estágio.
Seu comportamento analógico continua sem modelo e MTBF permanece aberto.

## Integração executada

`sim/net24/isa1_memory_common_request.sv` usa a variante nativa no lugar de
system_access. Clock/reset/osciladores NET23, raster NET22, memórias e teclado
continuam os mesmos. As ROMs não mudaram. Os testes mantêm os monitores
downstream, payload em WAIT, COMMIT único, 26 instruções, X/SP/flags e VGA.

| Bancada | Resultado |
|---|---|
| Instruções ideais | 6.886 casos,13.406 transações,570.876 verificações WAIT |
| Instruções temporizadas | Dois cenários de1.062 casos/1.821 transações/3.645 WAIT cada, CQ normal/antecipado do estado; setup observado54,888/36,944/46,944ns |
| Escrita real da CPU interrompida | Quatro cortes nominais e quatro com frequências opostas±50ppm; oito scans reiniciados, sem semear SRAM/rollback, WE até84ns |
| Boot/quadro ideal completo | 132.197 instruções,232.576 transações,32.771 transações VRAM,76.800 pixels,5.385.810 verificações WAIT e46.465 de pausa. SRAM inicialmente desconhecida e PPM idêntico à referência |

Boot levou1.035,231s de execução. O limite de tempo do processo foi elevado
para1.800s antes de iniciar, sem alterar deadline simulado ou asserções.
Períodos/startup dos modelos de oscilador são explicitamente escalados no
modo ideal. Não é execução física a essa frequência e o programa/quadro
completo temporizado ainda não foi executado.

ERC parcial: **135 violações**, duas de alimentação,45 de entradas e88 de
rótulos isolados; saída nativa5/host1, sem exceções. PDF/preview gerados.
Não somar ERC de folhas parciais como se fosse uma placa global revisada.

## Rejeição de pulso preservada, ainda sem correção

O backend **já é50% em regime**: G_2 = P1 OR P2, registrado por U11_0 com
clear permanentemente alto. A conta selecionada, sem jitter/skew de PCB,
dá47,44ns mínimos em regime após CQ e três buffers; não cobre reset.

`run_reset_pulse_probe.py` usa cópias das três netlists nativas. O perfil
assimétrico escolhe CLK–Q do backend10,5ns na subida/1ns na descida e buffers
de clock8,5ns/1ns em três níveis. Outros atrasos permanecem fixos conforme os
modelos anteriores; não é todo PVT. O código do monitor mantém exatamente a
mesma condição e acrescenta apenas o valor medido/estado de clear à mensagem.

Oito cenários simétricos passam. Do perfil assimétrico, o cenário em regime
e três offsets passam; **quatro resets em offsets30/39/40/60ns após a queda
do backend são rejeitados: pulso de7,722ns, requisito20ns** no HC74 do
controlador. São falhas de restrição observadas em simulação, não medições de
silício nem resultados aprovados. O relatório preserva exit1, mensagem e
escopo em `investigations`; `failures: []` do coletor significa somente que
todos os ensaios foram registrados/classificados, não que esses quatro
circuitos tenham passado.

O agrupamento de pedidos elimina a dependência selecionada entre seus dois
buffers, mas **não corrige essa rejeição durante reset**. Antes de qualificar
a placa, investigar o apagamento assíncrono do token de fases e a duração de
pulso em todos os consumidores, inclusive antes do clear atrasado dos bancos.
O [estudo de drenagem](CLOCK_DRAIN_STUDY.md) propõe uma alternativa com portas
livres e quatro estágios internos, ainda não implementada/aprovada nesta etapa.
Não enfraquecer a guarda para aceitar um pulso curto ativo.

## Origem, reprodução e limites

Builder deriva dos JSONs versionados de system_access, sem executar o
builder antigo para reescrevê-los. Projeções/fixtures e comandos/saídas/hash
estão em `verification/net24`; o primeiro coletor ERC procurava a biblioteca
errada, e sua fonte/saída nativa foram preservadas em development antes da
correção. A biblioteca real é access_packages.kicad_sym; erros/severidades
do ERC não foram alterados.

Reproduzir sequencialmente no WSL: `build_common_request.py`,
`run_request_skew_probe.py`, `run_common_request_probe.py`,
`check_common_request_topology.py`, `prepare_common_request_checks.py`,
`run_common_request_vectors.py` (também `--timed --quick` e `--early`),
`run_common_request_cpu_fault.py`, `run_common_request_cpu_corners.py`,
`run_common_request_program.py` e `run_reset_pulse_probe.py`. ERC, referências,
ambiente e manifesto têm ferramentas separadas. Não reconstruir entradas
enquanto uma bancada as estiver usando.

Continuam abertos: rejeição de pulso de reset, primeiro estágio/MTBF, demais
mínimos/máximos/skew/jitter/slew/cargas, osciladores/BOM completos,
fonte/consumo/USB-C/POR, DAC, firmware de eventos, união/ERC/footprints/PCB/DRC
e protótipo físico. diagnostic.asm original segue ausente; nenhuma bancada
histórica teve sua falha transformada em aprovação.
