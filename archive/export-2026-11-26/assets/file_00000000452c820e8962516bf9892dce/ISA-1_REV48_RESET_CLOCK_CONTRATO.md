# ISA-1 — Revisão 4.8 — Reset, clock e proteção de escrita

## Fontes do projeto
Continuação direta da Rev. 4.7 (`ISA-1_REV47_STARTUP_RESET.md`). O PC candidato consiste em quatro SN74HC163D com /CLR **síncrono** e clock compartilhado; EA/RET candidatos usam 74HC377 sem reset.

## Decisão de arquitetura
1. Supervisor externo monitora VCC e gera `RESET_REQUEST_N`; saída de reset de variante específica **ainda não selecionada/validada**. Não atribuir pinagem ou limiar sem datasheet.
2. Clock primário permanece ativo durante reset, com integridade elétrica a comprovar. Não combinar clock com portas lógicas comuns para forçar bordas.
3. Reset deve ser assertado de forma assíncrona para inibir imediatamente FETCH e /WE; liberação deve ser sincronizada com clock por pelo menos dois estágios. O reset síncrono do PC deve permanecer ativo até ocorrer pelo menos uma borda válida.
4. Se nenhuma borda de clock ocorrer enquanto reset do PC está ativo, o PC **não está comprovadamente inicializado**. A liberação de FETCH deve depender de uma evidência registrada de borda válida sob reset; simplesmente contar bordas após power-good não basta se o oscilador ainda não era válido.
5. `SRAM_WE_N` e `EEPROM_WE_N` devem permanecer em nível inativo por circuito independente de software enquanto RESET_REQUEST estiver ativo, inclusive durante brownout. Isso requer análise elétrica das saídas no power-up e pull-ups adequados. A EEPROM precisa ainda de intertravamento para a região SAVE e comandos SDP conforme revisões anteriores.
6. Registrar `EA_VALID` e `RET_VALID` antes de usar saídas de 74HC377, pois não possuem reset.

## Proposta de blocos
- Supervisor 5 V com saída de reset apropriada: **pendente de seleção exata**.
- Oscilador de clock 5 V compatível com 74HC: **pendente de frequência, tolerância e datasheet**.
- Dois flip-flops sincronizadores para liberação (família 74HC74 é candidata); a implementação deverá garantir que reset assíncrono, sinais de enable e condições de power-down sejam compatíveis.
- Um bit `RESET_EDGE_SEEN`, registrado durante a manutenção de /CLR do PC, para impedir FETCH prematuro. A lógica exata ainda não foi sintetizada.
- Intertravamento de /WE: requer portas e polaridade definidas após seleção de SRAM, EEPROM e supervisor; não ligar diretamente sem verificar correntes e limiares.

## Teste executado
`python isa1_rev48_reset_model.py` → 851.973 assertivas aprovadas, cobrindo todos os 65.536 valores iniciais do PC, reset, liberação e bloqueio lógico de escrita. O teste **não simula portas reais**, nem os tempos de propagação, metastabilidade, falha de clock, brownout analógico ou rampa de VCC. O modelo zera PC na borda válida explicitamente e não constitui prova elétrica.

## Pendências bloqueantes
- Identificar part numbers completos do supervisor e oscilador, pinagem, reset threshold, startup, VCC mínimo e máximo.
- Desenhar netlist com os flip-flops de sincronização, prova de borda, clock, PC, SRAM e EEPROM.
- Calcular worst-case setup/hold e propagação da cadeia RCO em datasheets oficiais.
- Validar operação com clock ausente, intermitente e alimentação lenta; comportamento da memória durante VCC abaixo da especificação.
- Verificar via simulador digital de portas e, para rampa de alimentação, modelo elétrico apropriado.

## Status
**Rev 4.8: contrato e testes comportamentais concluídos; circuito elétrico não concluído, seleção de componentes pendente, não pronto para KiCad/PCB.**
