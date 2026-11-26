# ISA-1 — Revisão 4.7 — Contrato de reset e partida

## Base conferida
Revisões 4.5 e 4.6: PC com quatro SN74HC163D; /CLR síncrono no pino 1, CLK comum no pino 2; /LOAD no pino 9. A Rev 4.6 **não** estabeleceu valores elétricos de temporização. O 74HC157 seleciona EA/RET para carga paralela do PC.

## Decisão de arquitetura
1. Alimentação abaixo do limiar ou botão RESET: supervisor mantém `RESET_REQUEST` ativo.
2. Oscilador de clock deve continuar funcionando enquanto RESET_REQUEST está ativo, ou o sequenciador deve gerar uma borda limpa e válida; não fazer clock gating combinacional.
3. Durante RESET_REQUEST, controlar `/CLR` dos 74HC163 em nível ativo, e garantir ao menos uma borda de subida válida de CLK; demais registradores sem reset não são presumidos inicializados.
4. Somente após a borda de reset comprovada e após a estabilização de controles, habilitar o FETCH da CPU. O reset do PC tem prioridade sobre /LOAD e COUNT.
5. Manter `/WE` de SRAM e EEPROM inativos durante power-up, brownout e reset; projetar **intertravamento elétrico independente de firmware** para EEPROM. O supervisor precisa de variante exata e comprovação de níveis em rampas de alimentação.
6. Em brownout, bloquear escrita imediatamente; o modelo funcional não prova proteção durante transientes de VCC.

## Proposta de máquina de estados (abstrata)
`POWER_UNSTABLE → RESET_HELD → RESET_EDGE_SEEN → RELEASE_WAIT → FETCH`.
Transições devem ser sincronizadas com o clock; `RESET_EDGE_SEEN` deve ser registrado. `RELEASE_WAIT` é barreira de segurança, não um atraso temporal já dimensionado.

## EA e RET: especificação de interface, não circuito pronto
- `EA[15:0]` deve permanecer estável antes da borda de `PC_LOAD` durante JMP/CALL.
- `RET[15:0]` deve ser reconstruído dos dois bytes lidos da SRAM antes de carregar PC em RET; exigir retenção independente de MAR e do barramento de memória.
- Escolha candidata: quatro octais 74HC377 para dois pares EA e RET (dois CIs por par), **sem reset próprio**, com carga sincronizada e inibição de uso antes da inicialização; os sinais de carga e caminhos de dados ainda precisam de esquema.
- Não confundir pinos de enable de 74HC377 com saídas tri-state: suas saídas dirigem continuamente.

## Teste reproduzível
`python isa1_rev47_startup.py` cobre 327.680 afirmações abstratas em todos os 65.536 estados iniciais de PC; testa reset, liberação, carga, incremento e prioridade de reset. Um teste negativo detecta liberação sem borda de reset. **A implementação Python impõe diretamente PC=0 ao chamar tick(reset)**; isso é uma abstração do contrato, NÃO uma simulação fiel do 74HC163 e não demonstra que a placa terá uma borda real durante o reset.

## Pendências bloqueantes para KiCad e PCB
- Escolher supervisor com referência exata, pinagem, limiares, histerese, saída e comportamento em power-down documentados.
- Definir oscilador e circuito de reset síncrono com prova de borda válida, sem glitches e sem metastabilidade na liberação.
- Fechar clock, setup/hold, skew, RCO e carga paralela com limites de datasheet na faixa de VCC e temperatura.
- Integrar reset e escrita segura em SRAM/EEPROM; validar comportamento durante quedas de tensão.
- Fechar registradores EA/RET, decodificação de escrita, microcódigo e barramento físico.

## Status
Contrato comportamental testado; **não é esquemático elétrico, não há simulação de portas, não há validação física e não está pronto para fabricar**.
