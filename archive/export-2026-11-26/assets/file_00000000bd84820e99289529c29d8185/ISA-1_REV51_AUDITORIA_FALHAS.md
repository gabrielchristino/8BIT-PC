# ISA-1 — Revisão 5.1 — Auditoria adversarial da netlist 5.0

## Evidência reproduzível
Executar `python isa1_rev51_safety_audit.py`. O programa lê a netlist real da revisão 5.0 e injeta sinais de controle não definidos. Contraexemplo: PC inicial 0000h, /LOAD=0, COUNT=0, valor de entrada BEEFh; na terceira borda após o reset, o PC vira BEEFh apesar de CPU_RUN=0. A netlist 5.0 NÃO garante a invariância PC=0000h até o início da execução.

## Correção obrigatória — contrato, ainda sem circuito físico
- `PC_LOAD_N_SAFE = PC_LOAD_N_REQ OR (NOT CPU_RUN)` (entrada /LOAD é ativa em zero).
- `PC_COUNT_SAFE = PC_COUNT_REQ AND CPU_RUN` (usar em ENP de todos os nibbles e ENT do nibble inferior, mantendo a cascata RCO nos demais ENT).
- Enquanto `CPU_RUN=0`, a lógica garante `PC_LOAD_N_SAFE=1` e `PC_COUNT_SAFE=0`.
- `CPU_RUN` é um sinal assíncrono relativo à lógica de comando se sua origem não for sincronizada; avaliar setup/hold, glitches e a propagação dos gates antes de conectar ao 74HC163. Não usar CPU_RUN como clock.
- O estado do PC é zerado pelas primeiras duas bordas com /CLR=0. Na terceira borda /CLR já é 1, mas /LOAD e COUNT estão inativos. A quarta borda só incrementa se a lógica de execução pedir.
- É necessário definir se a primeira micro-operação deve contar o PC; o teste 5.0 presume contagem automática, o que não é um contrato de busca de instruções completo.

## Resultados
O teste rev5.1 percorreu 65.536 valores iniciais × 2 valores de solicitação de carga × 2 valores de contagem × 4 bordas = 1.048.576 verificações do contrato corrigido, sem falhas. O teste negativo detectou a falha da Rev 5.0.

## Outras lacunas detectadas
A netlist rev5.0 não contém as redes de proteção de escrita SRAM_WE_N, EEPROM_WE_N, POWER_GOOD, OSC_VALID nem os sinais corrigidos PC_COUNT_SAFE e PC_LOAD_N_SAFE. Ela não contém supervisor, oscilador nem esquemático KiCad. Portanto não é apropriado fabricar PCB ou afirmar aprovação elétrica.

## Próximo gate
1. Escolher part numbers e consultar datasheets oficiais do supervisor e oscilador; verificar tensão, temporização e pinagem.
2. Materializar as portas de inibição /LOAD e COUNT em uma nova netlist, com pinagem e fanout.
3. Separar reset de inicialização de proteção imediata de /WE em brownout; garantir estados de saída de OE/WE durante subida/queda de VCC.
4. Produzir esquema KiCad nativo, com símbolos, alimentação, desacoplamento e footprints, e executar ERC com ferramenta instalada.
5. Simular temporização real com modelos apropriados; os testes Python NÃO são SPICE nem simulação digital com atrasos.

## Ferramentas disponíveis
Neste ambiente, `kicad-cli`, `iverilog` e `ngspice` não foram encontrados no PATH durante esta revisão. Não foi executado ERC nem simulação elétrica.
