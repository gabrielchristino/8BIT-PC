# ISA-1 — Revisão 3.0: interface ZIF e auditoria de proprietários dos barramentos
Data: 2026-11-23. **Estado: subsistema lógico candidato; não é esquemático completo nem hardware estável.**

## Base da revisão
Partimos das Rev. 2.4, 2.6, 2.8 e 2.9. Corrigimos a interpretação da Rev. 2.7: dois 74HC244 unidirecionais NÃO eliminam, por si só, a necessidade de controlar quem dirige o barramento da CPU. O buffer de leitura deve ser desabilitado enquanto qualquer fonte da CPU estiver dirigindo CPU_DATA. O buffer de escrita deve receber o valor de um registrador dedicado, nunca diretamente de CPU_DATA durante gravação.

## Topologia de sinais candidata (não netlist física fechada)
- U1 SN74HC377, endereço baixo: CPU_DATA[0..7] -> U1.D[0..7]; U1.Q[0..7] -> ZIF.A[0..7].
- U2 SN74HC377, endereço alto: CPU_DATA[0..6] -> U2.D[0..6]; U2.Q[0..6] -> ZIF.A[8..14]. O bit D7/Q7 fica reservado e NÃO deve flutuar em D7 (amarrar a nível definido).
- U3 SN74HC377, dado: CPU_DATA[0..7] -> U3.D[0..7]; U3.Q[0..7] -> U4.A[0..7].
- U4 SN74HC244, buffer escrita: U4.Y[0..7] -> ZIF.IO[0..7]; ambas /OE do CI sob controle WRITE_DRIVER_ENABLE_N.
- U5 SN74HC244, buffer leitura: ZIF.IO[0..7] -> U5.A[0..7]; U5.Y[0..7] -> CPU_DATA[0..7]; ambas /OE sob READ_DRIVER_ENABLE_N, com exclusão física de qualquer driver de CPU_DATA.
- ZIF para AT28C256 PDIP-28: pinos 1=A14, 2=A12, 3=A7, 4=A6, 5=A5, 6=A4, 7=A3, 8=A2, 9=A1, 10=A0, 11=IO0, 12=IO1, 13=IO2, 14=GND, 15=IO3, 16=IO4, 17=IO5, 18=IO6, 19=IO7, 20=/CE, 21=A10, 22=/OE, 23=A11, 24=A9, 25=A8, 26=A13, 27=/WE, 28=VCC.
- Os três 377 têm clock comum, com /CLKEN individual; somente são carregados em bordas válidas. Não há reset nos 377: o circuito de controle deve bloquear todas as saídas perigosas até registrar INIT_DONE.
- U4 e U5 são chips octais inteiros; os dois grupos de /OE de cada um precisam de tratamento consistente. Capacitores de desacoplamento por CI e aterramento correto são obrigatórios, valores ainda a dimensionar.

## Controle e restrições
- READ: /CE=0, /OE=0, /WE=1, U4 desligado, U5 ligado somente se barramento CPU livre.
- WRITE: /CE=0, /OE=1, /WE=0, U4 ligado, U5 desligado.
- TURN/IDLE/RESET: /CE=/OE=/WE=1, U4/U5 desligados.
- IMPORTANTE: o modelo lógico da Rev. 3.0 usa a entrada `cpu_driver_en` como uma informação perfeita. Falta construir o circuito real que garanta essa exclusão. Ainda falta construir o gerador de pulso de escrita com temporização de datasheet, supervisor e decodificação de autorização.
- Segurança de SAVE: as exceções SDP 5555/2AAA exigem sequenciador registrado. O bloqueio de endereços de código **não está implementado fisicamente**. A escrita integral de um chip vazio deve requerer modo PROGRAM autorizado.
- Regras de conexão: troca de EEPROM apenas desligado; pino 1 e orientação ZIF verificados; entradas não usadas não podem flutuar; evitar conexão direta de saídas dos 377 ao barramento bidirecional.

## Mapa de mídia consolidado (Rev. 2.5)
- 0000–003F: cabeçalho (64 bytes)
- 0040–77FF: programa e recursos (30.656 bytes)
- 7800–7BFF: SAVE A (1.024 bytes)
- 7C00–7FFF: SAVE B (1.024 bytes)
Todos os limites são múltiplos de 64 bytes.

## Resultados reproduzíveis
Executar `python isa1_rev30_bus_audit.py`: 640 combinações de controle, 68 entradas de tabelas de pinos, dois testes negativos de contenção, cobertura de 32.768 bytes. **Somente modelo estático de software**, sem análise temporal, sem biblioteca de símbolos CAD, sem simulação SPICE e sem medições.

## Bloqueadores para circuito completo
1. Congelar a ISA, microarquitetura, diagrama de clock, CPU/ALU/PC/SP/flags, firmware ROM e mapa de I/O.
2. Projetar o sequenciador real da interface (74HC/HCT, sinais registrados, reset e supervisor com variante específica), com circuito de exclusão de barramento e proteção física da escrita.
3. Orçamento worst-case de temporização com variantes e cargas verificadas; simulação temporal com atraso assimétrico e rampa de alimentação.
4. Vídeo RCA colorido: escolher encoder, padrão de vídeo, gerador de sincronismo, clock e VRAM; validar na tela real.
5. Teclado 4×16: pinagem, varredura, anti-ghosting e firmware.
6. Esquemático CAD, ERC, PCB, DRC, BOM, protótipo, osciloscópio e testes de regressão. **Não fabricar ainda.**

## Fontes de pinagem a conferir antes de esquemático
- TI SN74HC377: https://www.ti.com/lit/ds/symlink/sn74hc377.pdf
- TI SN74HC244: https://www.ti.com/lit/ds/symlink/sn74hc244.pdf
- Microchip AT28C256: https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C256-Industrial-Grade-256-Kbit-Paged-Parallel-EEPROM-Data-Sheet-DS20006386.pdf

**Não confundir esta descrição de sinais com netlist pino a pino completa de todos os componentes.**
