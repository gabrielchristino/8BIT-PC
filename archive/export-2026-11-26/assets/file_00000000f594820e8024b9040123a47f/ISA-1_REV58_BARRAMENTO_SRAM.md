# ISA-1 — Revisão 5.8 — Bancada de barramento, SRAM e pilha

## Objetivo
Integrar em um modelo comportamental a SRAM de 32 KiB, um barramento de dados de 8 bits, permissões de escrita e sequências CALL/RET da revisão 5.7.

## Modelo implementado
- SRAM simulada como `bytearray(32768)` no intervalo local `0000h–7FFFh`. **O mapeamento global da CPU ainda não foi aprovado**; o endereço local não deve ser confundido com o mapa definitivo de 64 KiB.
- Operação de escrita exige um único driver externo de 8 bits, CPU pronta, alimentação válida e endereço válido.
- Leitura da SRAM não admite outro driver ativo no barramento.
- Leitura e escrita simultâneas são rejeitadas.
- `CALL` empilha byte alto e depois baixo, pré-decrementando SP; `RET` lê baixo e depois alto, pós-incrementando SP. Essa convenção continua *proposta*, sujeita à reconciliação com ISA/microcódigo.
- Na bancada, `POWER_GOOD`, `CPU_RUN` e `ADDR_VALID` são sinais abstratos. Não representam um circuito de proteção eletricamente validado.

## Resultado reproduzível
Executar `python3 isa1_rev58_bus_bench.py` no diretório. Resultado: **35.087 verificações, 0 falhas**. Inclui 8 combinações de bloqueio, leitura/escrita de todos os 256 bytes em seis endereços de fronteira, seis casos negativos de protocolo, 200 sequências de 32 CALLs/32 RETs e bloqueio de escrita após parada da CPU.

Artefatos: `isa1_rev58_bus_bench.py`, `isa1_rev58_results.json`, `isa1_rev58_trace.csv`.

## Pontos descobertos e riscos abertos
1. **Mapeamento da SRAM:** 32 KiB não podem ser acessados indiscriminadamente no mesmo espaço que ROM, EEPROM, I/O e vídeo. Precisamos fechar a decodificação e as janelas antes de atribuir pinos /CS, /OE e /WE.
2. **Conflito físico:** a checagem de drivers no Python presume comutação instantânea. Em hardware, atrasos de desabilitação e habilitação podem criar contenção transitória. Exigir ciclos de liberação/turnaround e análise temporal por datasheet.
3. **Escrita em brownout:** `POWER_GOOD` lógico não prova inibição de /WE durante queda de alimentação. A proteção deve ser analisada eletricamente.
4. **Vídeo:** a arbitragem de memória de vídeo, concorrência com CPU e temporização de sincronismo não estão implementadas.
5. **Pilha:** a bancada testa pilhas que permanecem em SRAM. Falta tratar overflow, proteção de limites e chamadas/retornos durante interrupções.
6. **Microcódigo:** os passos de CALL/RET não estão ligados a um conjunto definitivo de sinais físicos nem reconciliados com a codificação de instruções.
7. **Reset:** ainda falta demonstrar que os enables reais dos buffers não dirigem barramento indevidamente antes de CPU_RUN.

## Próxima etapa — 5.9
Definir a arquitetura de vídeo composto colorido e seu acesso à memória, com cronograma de ciclos e prioridades CPU/vídeo. Antes de aprovar esquemático, integrar a decodificação SRAM/ROM/I/O, os buffers tri-state e os sinais de controle reais.

**Status:** aprovação comportamental restrita. Não equivale a ERC, simulação elétrica, validação de frequência ou autorização para fabricar PCB.
