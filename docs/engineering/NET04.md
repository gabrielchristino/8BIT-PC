# NET-04 — sequenciador e palavra de controle registrados

25/11/2026. Desenvolvimento novo sobre NET-03 (`b5e46593fab55b8679254f9004e5711cd1ffa2c5`), preservando os arquivos anteriores. O esquema KiCad exportado fornece as conexões da simulação dos pacotes; o restante da CPU continua parcialmente RTL. Não é uma liberação para fabricação.

## Circuito e protocolo

O banco contém 34 CIs e 34 capacitores propostos de 100 nF: 68 componentes, 652 pinos, 24 pinos explicitamente não conectados. A verificação encontra no máximo quatro entradas digitais por sinal interno. O orçamento usa até 10 pF por entrada e 10 pF de interligação; não substitui cargas medidas, comprimento de trilhas, alimentação e temporização global.

Um HC161 mantém o microstep; HC74 mantêm FETCH/EXECUTE e dois tokens de endereço/palavra; HC377 captura IR; HC157 mascaram o opcode durante FETCH. Quatro EEPROMs de 8K×8 alimentam quatro HCT377 que retêm a palavra de controle de 32 bits. HC138/139 decodificam campos; HC08/32/04/86 e HC125 distribuem qualificadores e clocks. A0–A3 são step, A4–A11 opcode mascarado, A12 FETCH. São alcançáveis 4.096 posições de execução e 16 posições FETCH; os 4.080 endereços FETCH restantes estão mascarados. Todos os 8.192 valores das quatro lanes são comparados com o gerador original, sem reescrever os binários históricos.

O endereço avança na fase positiva e alterna ADDRESS_TOKEN. A palavra é capturada na fase oposta; WORD_TOKEN recebe o token do endereço. Tokens diferentes significam palavra pendente. CONTROL_READY requer igualdade e alimentação/reset digitalmente seguros. O estado inicial tem tokens opostos, forçando a primeira leitura. O enable dos HCT377 só permite captura pendente: durante WAIT, a palavra retida não acompanha nem mesmo alterações deliberadas das saídas brutas das ROMs. HALT impede avanço e atualização da pilha. END e despacho FETCH recarregam o contador com zero por LOAD síncrono, sem criar clock por portas.

SP_UPDATE e SP_DOWN agora vêm da decodificação deste banco. EXECUTE_PULSE e ADVANCE_REQ ainda são produzidos pelo controle RTL integrado. ALU, A/B/PC/EA/flags e parte do controle de execução permanecem RTL; o candidato X conserva sua máquina de carga anterior. Portanto, mapear este sequenciador não conclui o controle físico de toda a CPU.

## Escolha das EEPROMs e limites elétricos

O documento Microchip AT28C64B DS20006432A, também arquivado, garante VOH de apenas 2,0 V nas condições indicadas. Isso coincide com VIH mínimo de 2,0 V do HCT377 e deixa margem garantida nula. Essa combinação foi rejeitada para esta proposta.

A candidata usada no esquema é **AT28HC64B-120**, documento Microchip 0274L (2009), com acesso máximo de 120 ns e VOH mínimo 2,4 V a −400 µA, VOL máximo 0,4 V a 2,1 mA. Frente aos limites HCT de 2,0/0,8 V, a verificação parcial fornece 0,4 V de margem DC nas condições especificadas. HCT377 faz a ponte para lógica HC; uma verificação pontual a 4,5 V compara VOH 3,84 V com VIH HC de 3,15 V. Isso não fecha toda a faixa de alimentação, ruído, cargas, temperaturas e skew. O datasheet prevê até 40 mA ativos por EEPROM, totalizando 160 mA para as quatro antes dos demais circuitos: o orçamento USB-C continua pendente.

CE e OE estão em GND e WE em VCC; o modelo só lê. A pinagem é de 28 pinos SOIC/PDIP, não TSOP. As quatro ROMs de controle são independentes da EEPROM de programa de 32 KiB. Disponibilidade comercial, encapsulamento final e BOM de compra não estão aprovados. Os capacitores desenhados são propostas; não há layout validado.

Fontes primárias preservadas com hashes no manifesto:

- [TI HC161](https://www.ti.com/lit/ds/symlink/sn74hc161.pdf), [HCT377](https://www.ti.com/lit/ds/symlink/sn74hct377.pdf), [HC138](https://www.ti.com/lit/ds/symlink/sn74hc138.pdf), [HC139](https://www.ti.com/lit/ds/symlink/sn74hc139.pdf), [HC86](https://www.ti.com/lit/ds/symlink/sn74hc86.pdf).
- [Microchip AT28HC64B, 0274L](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0274.pdf).
- [Microchip AT28C64B, DS20006432A — candidata rejeitada](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64K-%288Kx8%29-Industrial-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-20006432A.pdf).

## Iterações e correção de integração

Na primeira regressão rápida, o teste DEX 550 encontrou 0001h em vez de FFFFh para X inicialmente zero. O adaptador anterior amostrava direção na borda negativa global, antes da nova captura da palavra de controle. A versão nova `sim/net04/counter_word_candidate.sv` utiliza diretamente a direção já retida na palavra. A base anterior permanece intacta; `tools/make_microcode_cpu.py` registra as duas transformações e seus hashes. A CPU usa a mesma fase positiva distribuída do sequenciador para evitar uma corrida de ordem de eventos na simulação.

## Reprodução e resultados

Na raiz do projeto, Ubuntu WSL:

```text
python3 tools/build_microcode_bank.py
python3 tools/make_microcode_cpu.py
python3 tools/run_microcode_netlist.py
python3 tools/run_microcode_timing_checks.py
python3 tools/record_net04_manifest.py
python3 tools/record_net04_manifest.py --check
python3 scripts/verify_archive.py
```

Os logs em `verification/net04/results.json` são a evidência da rodada completa; `--quick` não é aceitação. Fontes, comandos, versões, saídas, duração e comparações de quadro são registrados. As adaptações de fixtures são novas, não alterações dos originais: sementes de SP seguem NET-03; guardas semeiam IR/step/FETCH físicos e aguardam captura com RUN pausado antes do acesso. O monitor observa START porque REQUEST tem latência. A bancada isolada também usa sementes internas, que não representam interfaces físicas existentes.

- Banco isolado ideal e com atrasos selecionados: 834 palavras executadas, 1.668 verificações de retenção, 4.112 endereços alcançáveis, 6.068 verificações de decodificação e 231 bloqueios HALT, sem falhas.
- CPU: 6.886 casos das 26 instruções, em cada configuração de X; 13.406 transações por configuração. Reset, alimentação digital, pausa e WAIT têm regressões separadas.
- Guardas: 524.288 combinações de SP/overlay/operação, sem falhas.
- Programa completo: boot, 132.197 instruções, 232.576 transações, 32.771 eventos VRAM e 76.800 pixels comparados com a referência, nas duas configurações de X. Consultar as saídas completas e `frame_matches_reference`.
- Falhas intencionais: enable de uma lane preso ativo deve denunciar vazamento da ROM durante WAIT; WE sem conexão deve ser rejeitado pelo conversor.
- Seis ensaios negativos dos monitores temporais devem falhar pelo motivo esperado: setup HC161 de 43 ns, recovery de clear de 31 ns; setup HCT377 de dados/enable de 15 ns, hold de dados 3 ns e enable 5 ns. Saída não zero nesses casos é rejeição esperada, registrada separadamente.

O cenário temporizado usa meias fases de 500 ns e margens de assentamento; o atraso das EEPROMs é 120 ns, HC138/139 são conservadoramente 45 ns. Não é certificação de frequência máxima da CPU. Somente limites selecionados têm monitores, com exclusão explícita dos primeiros 5 µs. Mínimos, skew, largura de pulso em todos os nós, metastabilidade, distribuição real e fechamento global permanecem pendentes.

## Pendências preservadas

Faltam esquema completo e controle físico restante, interface elétrica das memórias e periféricos, reset/brownout e RUN condicionados, orçamento de energia, fanout real, temporização completa, ERC/DRC, footprints, PCB e protótipo. Corrupção das ROMs não tem detecção por hardware. O modelo digital de alimentação não representa rampas analógicas. Não foi executada simulação elétrica completa. KiCad CLI 7 exporta os desenhos/netlists, mas esta verificação de pinos não é ERC. A ausência histórica de `diagnostic.asm` continua falha conhecida; o firmware novo não a resolve.

Os manifestos anteriores são auditados nos seus próprios commits, porque incluem documentos gerais que evoluem. Originais em `archive/`, `revisions/` e fontes de etapas anteriores não são corrigidos ou substituídos nesta etapa.
