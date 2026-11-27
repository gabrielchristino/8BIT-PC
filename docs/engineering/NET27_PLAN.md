# NET-27 — programa completo temporizado

Plano preparado após NET26 `f1c6c27d60d921286ed8729cd6f47e90e5948a3b`.
**Preparação de ensaio; nenhum resultado temporizado completo é declarado aqui.**

O executor foi verificado por cinco processos pequenos: conclusão normal,
limite de memória, saída, CPU e tempo de parede, além de detecção de processo
vivo/encerrado e boot diferente. Comando: `python3 tools/check_tracked_simulation.py`.
Evidências em `verification/net27/preparation/runner-check.json`; isso valida
o controle do processo, não o circuito. Estado é gravado por substituição atômica.

Executar `python3 tools/run_full_timed_program.py` no Ubuntu WSL. Usa Icarus,
CPU100kHz, mestre25,175MHz, startup10ms e atrasos digitais selecionados; SRAM
indefinida, sem seeds. Asserções originais de instruções/WAIT/COMMIT/memórias,
VRAM e comparação do quadro permanecem. Progresso adicional é somente leitura.

Limites por processo: compilador1GiB/120sCPU/180swall; simulação1GiB/20hCPU/
24hwall,8MiB por arquivo de saída e sem core dump. Trata-se de um ensaio
extenso, não de promessa de prazo. Falha, interrupção, limite ou ausência de
RESULT não são aprovação. Não usar CVC nos resultados de engenharia.

Em `verification/net27/full-timed/attempt-NNN` ficam PID/boot_id, comando,
estado, logs, snapshots dos modelos/bancada/imagens e referência do commit.
O progresso aparece em `simulation.stdout.log`; o PPM observado é preservado.
Reexecutar o comando identifica tentativa ainda viva e não a duplica. Processo
encerrado não tem estado HDL retomável: uma nova tentativa conserva a anterior.

Aceitar somente132.197 instruções,232.576 transações,32.771transaçõesVRAM,
76.800pixels com igualdade byte a byte do quadro, verificações originais
concluídas, sem aborts/erros e todas as fontes identificadas. O sucesso continua
limitado ao modelo digital/condições escolhidas; não libera fabricação.

Manter os arquivos de fonte listados congelados enquanto o processo estiver
ativo; trabalhos posteriores devem usar novas variantes. Orçamento temporal/
elétrico global, alimentação/consumo/POR, DAC/firmware, esquema/footprints/ERC,
PCB/DRC e protótipo continuam pendentes com critérios próprios.
