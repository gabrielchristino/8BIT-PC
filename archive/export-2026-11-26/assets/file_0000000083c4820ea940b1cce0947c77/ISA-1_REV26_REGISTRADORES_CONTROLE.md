# ISA-1 — Revisão 2.6: registradores e interface ZIF
Data: 2026-11-23. **Status: proposta parcialmente verificada por lógica; não pronta para PCB.**

## Base e mudança
A Rev. 2.5 preferiu a interface dedicada do gravador de EEPROM. Nesta revisão selecionamos o **SN74HC377DW (SOIC-20)** para três registradores: endereço inferior (8 bits), endereço superior (7 bits úteis, oitavo reservado), e dado de escrita (8 bits). Seu `/CLKEN` permite captura síncrona sem multiplexadores de realimentação. **Não possui reset**: bloquear `/CE`, `/OE`, `/WE` e a direção do transceptor durante reset, e liberar somente após inicializar os três registradores. A ordem de inicialização é parte do protocolo. A condição de inicialização precisa ser registrada com reset real, não apenas assumida em software.

## Pinagem SN74HC377 (vista superior, SOIC-20)
| Pino | Função | Pino | Função |
|---:|---|---:|---|
|1|/CLKEN|20|VCC|
|2|Q0|19|Q7|
|3|D0|18|D7|
|4|D1|17|D6|
|5|Q1|16|Q6|
|6|Q2|15|Q5|
|7|D2|14|D5|
|8|D3|13|D4|
|9|Q3|12|Q4|
|10|GND|11|CLK|

**Conexão funcional provisória**: U_ADDR_LO.Q[7:0] -> EEPROM.A[7:0]; U_ADDR_HI.Q[6:0] -> EEPROM.A[14:8]; U_DATA.Q[7:0] -> entrada do driver de escrita, com saída em alta impedância quando inativa. Os D de cada registrador vêm de `CPU_DATA[7:0]`, e `/CLKEN` recebe seleção exclusiva por registrador. **A saída de dados não pode ligar diretamente ao barramento bidirecional da EEPROM**: o 74HC377 sempre dirige Q. Um 74HC245 ou buffer tri-state deve isolar a saída de U_DATA.

## SN74HC245 (SOIC-20), dados bidirecionais
Pino 1 DIR; 2..9 A0..A7; 10 GND; 11..18 B7..B0; 19 /OE; 20 VCC. A0..A7 são os bits 0..7 na ordem de pinos 2..9; B0..B7 são pinos 18..11. Para ler, direção EEPROM -> CPU e habilitação apenas quando a CPU não dirige o mesmo barramento; para escrever, direção CPU -> EEPROM e `/OE` da EEPROM inativo. **A topologia ainda precisa de escolha explícita**: o registrador U_DATA fornece a origem do lado A para escrita, mas a CPU também deve receber o retorno na leitura, sem que o U_DATA dispute o lado A. Isso pode requerer um buffer de leitura adicional ou multiplexação. Portanto **a contagem mínima de 4 CIs octais não é uma BOM fechada**.

## Supervisor de alimentação
**MCP130** (Microchip), saída RESET ativa em nível baixo, open drain com pull-up interno, tempo típico de reset ~350 ms, variantes com limiares diferentes. É um **candidato**, não componente aprovado: selecionar sufixo e encapsulamento SMD, verificar limiar mínimo/máximo contra tensão mínima de operação de todos os chips, tempo de queda e a proteção da EEPROM abaixo do limiar. O supervisor sozinho não garante `/WE` alto em toda rampa desde VCC=0: precisamos demonstrar topologia fail-safe e medir. Não atribuir pinagem antes de escolher variante.

## Intertravamento proposto
Estados: RESET -> IDLE -> SETUP -> READ -> TURN -> WRITE_SETUP -> WRITE_PULSE -> WRITE_HOLD -> VERIFY -> IDLE. READ e VERIFY habilitam somente a EEPROM como fonte; WRITE_SETUP/PULSE/HOLD habilitam somente o driver. TURN e RESET desabilitam ambos. `/WE` só pode ficar ativo em WRITE_PULSE com POWER_OK, INIT_DONE, WRITE_AUTH, SAVE_RANGE_OK ou modo explícito de programação de código. **Os sinais de seleção devem ser registrados e fisicamente intertravados**. Não usar simples AND de clocks. O pulso de escrita deve obedecer tWP, tAS, tAH, tDS, tDH e limites de EEPROM reais, ainda não calculados.

## Proteção de dados e formato
EEPROM 0000–003F cabeçalho, 0040–77FF código, 7800–7BFF SAVE A, 7C00–7FFF SAVE B. Para gravar programa novo em chip vazio, modo de gravação integral autorizado; durante jogo, somente SAVE. Duas cópias de SAVE com commit final e CRC. **Proteção por software não é proteção contra falha de firmware**. Para proteção física da região SAVE, estudar comparador de endereço e modo de programação bloqueado por comando ou chave física.

## Resultados reproduzíveis
`python isa1_rev26_interface_test.py`: verificou unicidade/cobertura dos 20 pinos de cada 74HC377 e 74HC245; 131072 combinações de carga/retenção de um registrador abstrato; 144 combinações estáticas de controle; teste negativo que detecta disputa forçada; integridade do mapa e páginas. **Os testes de registrador verificam apenas a equação de seleção**, não os tempos ou circuitos internos. Nenhum teste SPICE, nenhuma rampa real de VCC, nenhuma pinagem física da EEPROM neste script, nenhum protótipo. Resultado em `isa1_rev26_results.json`.

## Comparação provisória de CIs
- Dedicado: 3× HC377 + pelo menos 1× HC245, e provavelmente mais 1× buffer de leitura/mux, além de decodificação, FSM, supervisor e lógica de proteção.
- Mapeado: menos registradores dedicados possíveis, mas mais seleção de memória, arbitragem e risco de escrita. Ainda não há comparação quantitativa completa.

## Bloqueadores para revisão 2.7
1. Resolver a topologia completa do retorno EEPROM -> CPU sem disputa com U_DATA, com netlist pin-to-pin.
2. Selecionar supervisor SMD específico e comparar datasheet e limiar com VCC do sistema.
3. Dimensionar e testar bloqueio de escrita de hardware, inclusive reset e queda de alimentação.
4. Extrair limites de temporização (min/max) das variantes exatas e criar simulação temporal com injeção de skew.
5. Confirmar pinagem do ZIF e compatibilidade com encapsulamento PDIP-28 real da AT28C256.

## Fontes oficiais
- TI SN74HC377: https://www.ti.com/lit/ds/symlink/sn74hc377.pdf
- TI SN74HC245: https://www.ti.com/lit/ds/symlink/sn74hc245.pdf
- Microchip MCP130: https://www.microchip.com/en-us/product/MCP130
- Microchip AT28C256: https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C256-Industrial-Grade-256-Kbit-Paged-Parallel-EEPROM-Data-Sheet-DS20006386.pdf
