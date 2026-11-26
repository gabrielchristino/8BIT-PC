# ISA-1 — Revisão 5.3 — Auditoria independente da netlist 5.2

## Escopo e evidência
Reabertos `ISA-1_REV52_CORRECAO_PC_PINOS_TESTES.md`, `ISA-1_REV49_VALIDACAO_RESET_CLOCK.md` e `isa1_rev52_corrected_nets.json`. Foi executado `isa1_rev53_audit.py`, que usa tabelas explícitas de direção e alimentação dos pinos para os 13 CIs 74HC presentes. Esta verificação é **estática**, não um ERC do KiCad, não uma simulação SPICE e não uma medição.

## Resultados
- 13 circuitos integrados e 198 pinos mapeados.
- Zero pinos não atribuídos, duplicados, alimentados em rede incompatível ou redes com dois drivers lógicos (conforme tabelas do script).
- **37 redes sem driver interno**: 32 bits EA_Q/RET_Q, `PC_SEL_RET`, `SUP_RESET_N`, `SYS_CLK`, `PC_COUNT_REQ`, `PC_LOAD_N_REQ`. São interfaces pendentes, **não** 37 falhas comprovadas: podem receber drivers externos no esquemático completo.
- **17 redes com saída sem receptor na netlist parcial**: majoritariamente saídas PC_Q e RCO de monitoração. Precisam de destino ou documentação de ponto de teste; não significam necessariamente defeito.
- A rede de alimentação da Rev 5.2 chama-se `VCC_5V`, não `VCC`; o auditor aceita ambos como alias de 5 V. **Não foi conferido o comportamento elétrico da alimentação.**

## Riscos ainda abertos (bloqueiam aprovação de PCB)
1. O supervisor TPS3808G50DBVR é apenas candidato: pinos, variante exata, limiar, temporização, pull-up e comportamento de saída em alimentação baixa ainda não foram integrados.
2. O oscilador não está definido: frequência, tensão, duty cycle, tempo de partida, distribuição e margem temporal desconhecidos.
3. `SUP_RESET_N` assíncrono pode ser desassertado próximo da borda do clock; verificar recuperação/remoção dos 74HC74 e estratégia de sincronização.
4. Bloqueio de escrita em SRAM e EEPROM durante power-up/power-down e brownout **não está implementado**.
5. O HC163 usa reset síncrono: o PC não fica necessariamente em zero sem borda válida; manter sequenciamento e controle de cargas até o início efetivo do clock.
6. 32 sinais EA/RET são apenas rótulos: registradores, drivers, clocks e habilitações ainda não foram desenhados.
7. Necessário consultar os datasheets oficiais da variante escolhida antes de fixar símbolos/footprints e fazer cálculo de atraso da cascata RCO.
8. Desacoplamento por CI, pull-ups, estados de entradas e comportamento sob VCC abaixo da faixa válida ainda não foram definidos.

## Próximo marco concreto
Montar um **esquemático KiCad mínimo** de supervisor + sequenciador + PC, com os drivers das entradas explicitados, inserir alimentação e capacitores de desacoplamento, executar `kicad-cli sch erc` e publicar os resultados. Só então passar à validação temporal e de brownout em simulador/ bancada.

## Reproduzir
`python isa1_rev53_audit.py` na pasta do projeto. Saída `isa1_rev53_results.json`.
