# ISA-1 — Revisão 5.9 — Arbitragem lógica do barramento

## Contexto
A revisão 5.8 detectava intencionalmente conflitos entre drivers. A 5.9 acrescenta um modelo separado de **propriedade exclusiva** do barramento de dados de 8 bits. A numeração 5.9 aqui cobre o ajuste de segurança antes da futura integração do vídeo.

## Decisão de arquitetura
- Propriedade do barramento: CPU, SRAM, EEPROM, I/O ou ninguém.
- Na troca entre dois proprietários ativos, inserir estado **Z** (*break-before-make*). Nenhum driver pode permanecer habilitado no intervalo.
- Desabilitar o barramento e a permissão de escrita em reset, CPU inativa, endereço inválido ou falta de `POWER_GOOD` (no **modelo lógico**).
- Decodificação de leitura/escrita mutuamente exclusiva, e no máximo um chip selecionado em cada transação.
- Não atribuir ainda endereços absolutos: a janela local SRAM 0000h–7FFFh não é o mapa global de 64 KiB.

## Verificação executada
`python3 isa1_rev59_bus_guard.py` produziu 210.744 verificações e zero falhas. O teste cobre 12 transições dirigidas entre os quatro proprietários, 100.000 estímulos pseudoaleatórios determinísticos, e casos negativos de protocolo. O CSV registra 80 ciclos de amostra. O programa é reexecutável.

## Limitações que impedem aprovação elétrica
1. O estado Z é abstrato. Não foram medidos os atrasos tDIS/tEN dos 74HC245/244, SRAM e EEPROM, nem calculada a margem de turnaround.
2. Não foi construída uma netlist de portas, um esquemático KiCad ou executado ERC.
3. O teste de escrita modela permissão para a CPU dirigir o barramento; não substitui as equações físicas /CS, /OE e /WE para cada memória.
4. `POWER_GOOD` não é garantia física de proteção em brownout. O supervisor e o bloqueio de /WE precisam de análise própria, inclusive abaixo da faixa operacional dos CIs.
5. A arbitragem de vídeo, clock, acesso a VRAM e sincronismo composto não estão modelados.
6. É preciso definir comportamento quando a requisição muda durante o estado Z, e especificar em qual borda do clock os controles são registrados.

## Próximos trabalhos
1. Congelar mapa de memória preliminar com janelas mutuamente exclusivas e decodificação comprovável.
2. Converter FSM em sinais de habilitação ativos-baixos e escolher componentes de lógica; calcular margens temporais com datasheets.
3. Integrar controlador de vídeo e, se necessário, VRAM dedicada para evitar que vídeo bloqueie a CPU.
4. Concluir o circuito de proteção de escrita da EEPROM e validar a alimentação USB-C/boost.

**Status:** testes lógicos aprovados no escopo. Não é comprovação elétrica ou autorização para fabricação.
