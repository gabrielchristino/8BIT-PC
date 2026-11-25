# NET-06 — registradores A/B/EA, flags e seleção de dados

25/11/2026, base NET-05 `18a3cdc2ab83cb8af51177b8116b0320a4a4f5b8`. Desenvolvimento novo, separado dos arquivos anteriores e dos originais recuperados. O banco parcial deriva do esquema KiCad e integra-se à CPU das ROMs. Não há liberação para fabricação.

## Circuito e compatibilidade

Quatro HC273 armazenam A, B, EA baixo e EA alto. Oito HC157 escolhem entre realimentação e novo dado; não há clock gated. Um HC74 armazena Z/C com realimentação por portas. Outros doze HC157 formam uma árvore de seleção de dados de oito entradas. Os códigos de origem continuam 0=zero, 1=A, 2=PC alto, 3=PC baixo, 4=MDR, 5=ALU, 6/7=zero.

O clock é o mesmo ramo de execução da NET-04, distribuído por buffers. EXEC_ENABLE vem da qualificação RTL de EXEC, RUN, não HALTED, X pronto, ausência de transação de memória e CONTROL_READY. O banco também exige RESET_N e POWER_GOOD digitais seguros. Os decodificadores de destino e flags já existentes na NET-04 fornecem DST_N e FLAGS_N; não são substituídos por decodificação simbólica no novo banco. A captura usa os valores anteriores à borda, preservando a ordem das operações da CPU.

Destinos 1/2 escrevem A/B; 3/4 escrevem somente um byte de EA. Outros destinos não alteram estes registradores. Flags=0 retém Z/C; flags=1 ou 3 atualiza somente Z; flags=2 atualiza Z e C. **Z compara o dado selecionado com zero**, incluindo cargas da memória/registradores. C recebe o carry da ALU somente quando autorizado; SUB/CMP continuam com carry sem empréstimo. A saída ZERO da ALU não substitui essa comparação.

O reset/estado digital de alimentação limpa os quatro bytes e as duas flags. Isso não dimensiona supervisor, brownout ou rampa analógica. EXEC_ENABLE deve permanecer estável com setup/hold apropriados; não há promessa de atualização segura com entradas assíncronas arbitrárias.

## Esquema e componentes

| Candidato | Quantidade |
|---|---:|
| SN74HC273 | 4 |
| SN74HC74 | 1 |
| SN74HC157 | 20 |
| SN74HC125 | 7 |
| SN74HC08 | 3 |
| SN74HC32 | 3 |
| SN74HC04 | 2 |
| Capacitor proposto 100 nF | 40 |

São 40 CIs, 80 componentes, 704 pinos e 12 saídas explicitamente sem conexão. Nenhuma entrada digital fica aberta. Buffers dividem cargas recursivamente, mantendo até quatro entradas por net interna. O orçamento usa 10 pF por entrada mais reserva de 10 pF de interligação; cargas externas, alimentação e roteamento real continuam pendentes. O número de CIs é uma base verificável, sem alegação de otimização ou BOM final.

`tools/build_register_bank.py` reutiliza pinagens já documentadas, desenha símbolos de pacote completo, exporta XML pelo KiCad e gera HDL dessas conexões. Pinos, alimentação, drivers, saídas e fanout são conferidos contra o XML. O esquema A1 foi renderizado e inspecionado. Labels representam conexões entre pacotes; não há PCB/footprints aprovados. KiCad CLI 7 exporta os arquivos, mas a conferência de pinos não equivale a ERC.

Os datasheets TI existentes permanecem byte a byte: [HC273](https://www.ti.com/lit/ds/symlink/sn74hc273.pdf), [HC74](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), [HC157](https://www.ti.com/lit/ds/symlink/sn74hc157.pdf), [HC125](https://www.ti.com/lit/ds/symlink/sn74hc125.pdf), [HC08](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf), [HC32](https://www.ti.com/lit/ds/symlink/sn74hc32.pdf), [HC04](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf). O manifesto registra hashes/origens; não se mistura HC273 com a pinagem ou os limites de CD74HC273.

## Verificação e reprodução

Na raiz do projeto, WSL Ubuntu:

```text
python3 tools/build_register_bank.py
python3 tools/make_register_cpu.py
python3 tools/run_register_netlist.py
python3 tools/run_register_timing_checks.py
python3 tools/record_net06_manifest.py
python3 tools/record_net06_manifest.py --check
python3 scripts/verify_archive.py
```

`verification/net06/results.json` contém a rodada completa: versões, comandos, saídas, tempos e hashes das fontes. `--quick` não é aceitação. Fixtures são transformadas em cópias temporárias: as sementes arquiteturais de A/B/Z/C passam a escrever Q dos respectivos pacotes; PC continua RTL e SP/IR/step seguem as adaptações anteriores. Essas sementes não são interfaces físicas. O programa completo inicia por reset/boot normal, sem semear esses registradores. Nenhuma bancada anterior é alterada.

- Banco isolado: matriz de 8 origens × 256 padrões de dados × 8 destinos × 4 modos de flags × 2 carry × 2 enables = 262.144 casos por modo. São 262.162 ciclos com preparação e quatro cortes de reset/alimentação, ideal e com atrasos selecionados. A referência verifica seleção, carga de byte, flags, retenção mesmo com fontes mudando e clear. A matriz cobre todos esses campos, não todas as combinações dos 34 bits de estado ou todas as entradas externas independentes.
- Integração: 6.886 casos das 26 instruções e 13.406 transações em cada configuração de X; segurança digital e 524.288 combinações das guardas de pilha.
- Programa completo nas duas configurações: 132.197 instruções, 232.576 transações, 32.771 eventos VRAM e 76.800 pixels comparados com a referência. Ambos os campos `frame_matches_reference` devem ser verdadeiros.
- Falhas intencionais de netlist: seleção de realimentação de A presa em carga deve ser detectada; clear desconectado deve ser rejeitado pelo conversor.
- Oito violações temporais intencionais: setup, recuperação de clear, largura de clock e largura de clear, para HC273 e HC74. Cada uma deve terminar com falha pelo motivo esperado, em relatório separado.

O primeiro ensaio falhou ao esperar estado inicial zero sem aplicar uma transição de reset ou clock. O modelo orientado a eventos manteve X. O preparo foi corrigido para aplicar pulso explícito de reset antes da comparação; não se inicializou Q artificialmente. O relatório original com essa falha está preservado como `initial-reset-fixture-failure.json`, identificado como ensaio intermediário; seus hashes não são os da rodada final. A fixture inicial também foi preservada como `initial-reset-fixture.sv`, com SHA-256 conferido contra o log daquela execução. Isso não resolve reset físico, cuja geração e duração continuam pendentes.

## Temporização e pendências

O banco isolado usa intervalos de 1 µs entre preparação/borda e borda/comparação. Os atrasos selecionados são CQ/clear HC273 de 40 ns; HC74 CQ de 44 ns e clear de 58 ns; mux 38 ns; buffer 36 ns; inversor 24 ns; portas de duas entradas conservadoramente 31 ns. O cenário refere-se a limites selecionados de HC a 4,5 V, −40..85 °C e até 50 pF, sem extração de PCB ou mínimos/skew.

Os monitores de HC273 exigem setup/recovery 25 ns, clock/clear de pelo menos 20 ns; HC74 exige setup de dados 25 ns, recovery 6 ns, clear 25 ns e clock 20 ns. O hold de dados especificado é zero. Os monitores excluem o início da simulação conforme os modelos anteriores; não se reivindica cobertura temporal desse intervalo. Preset de flags fica inativo e sua conexão é conferida. A integração da CPU usa os modelos funcionais sem atrasos, portanto esta rodada não demonstra temporização global ou frequência máxima.

Continuam RTL: PC e incremento/desvios, seleção de endereços, estados de execução, guardas de pilha/fault e parte do candidato X. Próxima etapa: PC e caminho de endereço, preservando SP−1 e captura anterior a WAIT. Depois faltam controle físico restante, cargas entre blocos, energia/reset/clock, interface elétrica de memória/VGA/teclado, ERC/DRC, layout e protótipo. A ausência histórica de `diagnostic.asm` continua falha conhecida; o diagnóstico novo não substitui o original ausente.
