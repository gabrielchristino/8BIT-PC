# NET-05 — ALU de 8 bits derivada do esquema

25/11/2026. Desenvolvimento novo a partir de NET-04, commit `179b06ed6aa80ab1658022657638ef571888d6a7`. Originais recuperados e arquivos das etapas anteriores permanecem intactos. Esta etapa mapeia apenas a ALU combinacional, sem liberação para fabricação.

## Comportamento e circuito

Dois CD74HC283 em cascata compartilham soma e subtração. O segundo operando passa por XOR: subtração/comparação selecionam B invertido e carry-in igual a um. O carry de subtração significa **ausência de empréstimo**, como no modelo anterior. AND, OR e XOR são portas explícitas; deslocamentos são interligações e seleção. Dois HC138 decodificam os 16 códigos; portas mascaram e combinam os resultados. Não há barramento tri-state compartilhado na seleção de resultado.

| Campo ALU | Resultado | Carry de saída |
|---|---|---|
| 1 | A+B, módulo 256 | Transbordamento sem sinal |
| 2 e 8 | A−B, módulo 256 | A ≥ B |
| 3, 4, 5 | A AND B, A OR B, A XOR B | Carry anterior |
| 6 | A deslocado à esquerda, entrada zero | A7 |
| 7 | A deslocado à direita, entrada zero | A0 |
| 0 e 9–15 | Zero | Carry anterior |

O pino ZERO indica resultado zero, mas **não substitui o teste de flags da CPU**: ali Z depende do valor selecionado no barramento, que também pode vir de memória ou registradores. Os registradores de flags, A/B, PC/EA e parte do controle de execução continuam RTL. A ALU integra-se aos bancos SP, transações e microcódigo das etapas anteriores. Não se alteram ROMs, opcodes, política de pilha, X, VGA ou teclado.

## Esquema, pinagem e custo

O desenho nativo `hardware/alu_bank/alu_bank.kicad_sch` é exportado pelo KiCad; o XML fornece todas as conexões de `alu_bank_netlist.sv`. O conversor valida entradas conectadas, alimentação, drivers únicos, nomes e saídas. O mapa de pinos é comparado com o XML realmente exportado. A folha A1 foi renderizada e inspecionada; é um esquema parcial por pacotes completos com labels, não PCB.

| Candidato | Quantidade |
|---|---:|
| CD74HC283 | 2 |
| SN74HC138 | 2 |
| SN74HC08 | 15 |
| SN74HC32 | 15 |
| SN74HC86 | 4 |
| SN74HC04 | 2 |
| SN74HC125 | 9 |
| Capacitor proposto de 100 nF | 49 |

Total: 49 CIs, 98 componentes, 792 pinos e seis saídas explicitamente sem conexão. Nenhuma entrada digital fica aberta. A distribuição recursiva por HC125 mantém até quatro entradas digitais por net; a capacidade estimada é até 40 pF de entradas mais reserva de 10 pF de interligação. Carga externa e soma dos consumidores entre blocos ainda precisam de conferência global. Isso não é extração de PCB. Esta base prioriza equivalência verificável e não demonstra economia de componentes. Multiplexadores e redes alternativas de seleção podem reduzir custo, mas exigem nova comparação de BOM, fanout e caminhos antes de qualquer substituição.

Os símbolos e pinagens reutilizam as definições documentadas das etapas anteriores; as fontes TI originais já arquivadas não foram baixadas novamente ou alteradas. Fontes primárias: [CD74HC283](https://www.ti.com/lit/ds/symlink/cd74hc283.pdf), [HC08](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf), [HC32](https://www.ti.com/lit/ds/symlink/sn74hc32.pdf), [HC86](https://www.ti.com/lit/ds/symlink/sn74hc86.pdf), [HC04](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf), [HC125](https://www.ti.com/lit/ds/symlink/sn74hc125.pdf), [HC138](https://www.ti.com/lit/ds/symlink/sn74hc138.pdf). Hashes dos PDFs estão no manifesto desta etapa. Encapsulamentos, footprints, disponibilidade, BOM final e dimensionamento de desacoplamento não estão aprovados.

## Atrasos e cobertura

O cenário selecionado usa lógica HC a 4,5 V, faixa −40 a 85 °C e carga de até 50 pF, com entradas dentro dos requisitos dos fabricantes. Os limites usados são 58 ns para soma, 49 ns para carry, 45 ns para decodificação, 36 ns para buffers, 24 ns para inversão e 31 ns conservadores para todas as portas de duas entradas. São modelos funcionais com atrasos constantes, não modelos elétricos dos fabricantes.

`tools/analyze_alu_paths.py` percorre os arcos combinacionais da netlist exportada. Para somadores/decodificadores assume conservadoramente dependência de todas as entradas do pacote. Detecta ciclos, drivers ausentes/duplicados e produz caminhos por saída. Os 204 arcos resultam em limite de 515 ns até a última saída; a bancada espera 1.000 ns antes de cada comparação. Esse limite só vale para os arcos/atrasos selecionados: não inclui registradores anteriores/posteriores, roteamento real, skew, mínimos, ruído, transientes ou formas de onda. Não autoriza frequência máxima da CPU ou largura de ciclo físico.

## Reprodução e evidências

Na raiz, Ubuntu WSL:

```text
python3 tools/build_alu_bank.py
python3 tools/make_alu_cpu.py
python3 tools/analyze_alu_paths.py
python3 tools/run_alu_netlist.py
python3 tools/record_net05_manifest.py
python3 tools/record_net05_manifest.py --check
python3 scripts/verify_archive.py
```

`verification/net05/results.json` registra comandos, versões efetivas, hashes das fontes, saídas e durações. `--quick` não é aceitação. Binários, ROMs convertidas e fixtures ficam em diretório temporário Linux. As quatro lanes originais são comparadas com o gerador antes da execução. A CPU nova deriva da NET-04 por substituição da expressão ALU pela instância da netlist; o adaptador registra origem e hashes. Fixtures de guardas seguem a transformação já documentada em NET-04, sem editar as bancadas anteriores.

Critérios da rodada completa:

- ALU ideal e com atrasos: cada uma percorre 16 operações × 256 valores A × 256 valores B × dois estados de carry, total de 2.097.152 casos, verificando resultado, carry e ZERO.
- Regressão das 26 instruções: 6.886 casos e 13.406 transações em cada configuração de X, contra a referência arquitetural; segurança inclui reset/alimentação digital, pausa e WAIT.
- Guardas de pilha: 524.288 combinações, preservando convenção SP=8000h vazio e política de dois bytes CALL/RET.
- Programa completo nas duas configurações: 132.197 instruções, 232.576 transações, 32.771 eventos VRAM e quadro de 76.800 pixels comparado com a referência. O campo `frame_matches_reference` precisa ser verdadeiro em ambos os ensaios.
- Falhas intencionais: carry-in do primeiro somador preso em zero deve produzir divergência na bancada; entrada A0 do somador desconectada deve ser rejeitada pelo conversor. Não são falhas ocultadas da rodada normal.

Durante o preparo, a primeira rodada foi interrompida para ajustar a distribuição visual dos pacotes na folha; o circuito lógico não mudou. A rodada de aceitação foi reiniciada com os hashes definitivos do esquema e ferramentas. Não houve divergência funcional registrada nesta etapa antes dessa interrupção. Logs de aceitação completos são os do relatório final, não a rodada interrompida.

## Limites e continuidade

A integração da CPU usa modelos funcionais sem atrasos; somente o bloco isolado recebe o cenário temporizado. Não existe aprovação temporal global. Os estados digitais de reset/alimentação não modelam rampas analógicas. ALU é combinacional e pode apresentar transientes entre entradas: enables e captura reais precisarão respeitar assentamento/setup/hold. KiCad CLI 7 exporta esquema/netlist, mas os checks de pinos não substituem ERC. Faltam registradores e seleção de dados/endereços físicos restantes, reset/brownout e RUN condicionados, integração elétrica de memória/VGA/teclado, alimentação, ERC/DRC, PCB, ensaio e protótipo.

A ausência histórica de `diagnostic.asm` continua falha conhecida da bancada recuperada. O diagnóstico novo não recupera esse arquivo. Manifestos antigos são auditados nos próprios commits; nenhum hash histórico é reescrito para acompanhar os documentos gerais atuais.
