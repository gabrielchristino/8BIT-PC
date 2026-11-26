# ISA-1 — Revisão 3.4 — Escolha preliminar de CIs da CPU

**Estado:** seleção de arquitetura e famílias lógicas; NÃO é BOM final, esquemático, netlist, nem aprovação de fabricação.

## Base inspecionada
- `ISA-1_REV33_MICROOPERACOES.md`
- `isa1_rev33_microcode.json`: 19 instruções, 101 etapas simbólicas
- `ISA-1_REV31_CPU_CONTRATO_E_REGRESSAO.md`: diferenças ainda abertas entre ISA pretendida e emulador

## Topologia preferida
CPU síncrona de 8 bits, endereçamento de 16 bits, registradores dedicados, barramento interno de dados de 8 bits, barramento de endereço gerado por MAR de 16 bits, ALU combinacional de 8 bits, microsequenciador registrado e ROM de microcódigo. A CPU não será implementada por microcontrolador ou microprocessador comercial.

## Seleção preliminar
| Bloco | Família/CI candidato | Razão | Bloqueio antes de BOM |
|---|---|---|---|
| Registradores comuns | SN74HC377 (8-bit, clock enable) | carga seletiva sem mux de realimentação | não possui reset nem OE; usar isolamento e inicialização |
| Registradores resetáveis | SN74HC273 (8-bit, clear) | estado inicial conhecido | carga condicional requer mux/controle de clock correto; não fazer gating combinacional de clock |
| Multiplexação | SN74HC157 (4 canais 2:1) | escolha de fontes | contabilizar todos os muxes e cargas |
| Buffer tri-state unidirecional | SN74HC244 | controle explícito de direção fixa | sinais OE registrados ou temporalmente protegidos |
| Transceptor | SN74HC245 | bidirecional onde necessário | direção e OE com turnaround |
| Somador ALU | SN74HC283 (4-bit) ×2 por somador 8-bit | soma em cascata | ripple carry, tempo de propagação e flags |
| XOR | SN74HC86 | XOR e inversão condicional de B para SUB | carry-in e carry-out devem ser tratados |
| AND/OR | SN74HC08 / SN74HC32 | operações booleanas | seleção do resultado da ALU |
| Decode | SN74HC138, SN74HC00 | decodificação de destinos e sinais | glitches e qualificação por microestado |
| Flag flip-flop | SN74HC74 (candidato) | flags Z/C com captura explícita | lógica de Z e clock enable |
| ROM de microcódigo | EEPROM paralela a selecionar | controle sem processador | largura, profundidade, acesso, programação e pinagem |
| Clock e reset | oscilador + supervisor a selecionar | partida e frequência determinísticas | thresholds, rampas e brown-out |

**Compatibilidade elétrica:** HC e HCT não são intercambiáveis sem avaliar níveis de entrada, alimentação, fanout e família de saída. Preferir uma alimentação lógica coerente; não congelar a tensão antes da análise de vídeo e memórias.

## Alocação de registradores — estimativa conservadora, NÃO quantidade final de chips
PC 16, SP 16, MAR 16, EA 16, RETADDR 16, A 8, B 8, IR 8, TMP 8, TPH 8, MDR 8: total 16 bytes de estado de registradores propostos, **16 posições de CIs octais se todos forem físicos e independentes**. Alguns temporários podem ser eliminados depois de comprovar que o microcódigo e o datapath permitem compartilhamento. O registrador X 16-bit da ISA 3.1 ainda não está representado na tabela rev33 e precisará de 2 posições adicionais se a ISA expandida for aprovada.

## Caminhos críticos e decisões pendentes
1. PC/SP incrementam/decrementam: somadores dedicados vs ALU compartilhada; contar ciclos adicionais antes de escolher.
2. CALL/RET: EA ou registrador de destino precisa permanecer estável enquanto MAR aponta para a pilha; não assumir que RETADDR físico é necessário sem mapear o fluxo.
3. Memória: separar preparação de endereço, ativação de /OE, captura, desativação, preparação de dados, pulso de /WE e hold.
4. Barramento: nenhuma saída 74HC377 pode ser ligada diretamente a um barramento com outros drivers; usar mux ou buffer tri-state.
5. Microsequenciador: definir IR + passo + flags -> palavra de controle, largura da ROM e estado de reset; não conectar ROM assíncrona diretamente a /WE sem registro/qualificação.
6. Falta fechar instruções 32,33,34,35,36,42,54 e I/O antes de congelar opcodes.
7. Memórias SRAM/ROM, vídeo composto colorido, teclado e ZIF precisam de projetos completos, com pinagem oficial e temporização.
8. Testes Python atuais são verificações de estrutura, não simulação de componentes, nem ERC/DRC.

## Critério para revisão 3.5
Produzir tabela por microestado com sinais explícitos (fontes, destinos, enables, ALU op, endereço, RD, WR, turnaround), gerar detector de conflito de drivers e estimar largura/profundidade de ROM. Somente após isso desenhar esquemático pin-to-pin.

## Reprodução
`python3 isa1_rev34_ci_audit.py` gera `isa1_rev34_results.json` a partir da tabela rev33. O script confere quantidade de instruções, etapas e presença de CALL, RET e EA; **não verifica equivalência funcional ou eletricidade**.
