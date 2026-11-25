# NET-03 — transações e retenção de endereço/dados

Desenvolvimento novo de 25/11/2026 sobre o commit NET-02 `60c097c8d5fb6a8f282fa6429347431c9f313ac8`. O controle do barramento, seus registradores de payload e o MDR agora derivam do XML realmente exportado pelo KiCad. A CPU continua executando as ROMs originais e usando o banco SP da NET-02. **É um bloco parcial, ainda sem liberação de placa para fabricação.**

## Circuito e interface

O esquema contém 17 CIs e 17 capacitores de 100 nF propostos, com 304 pinos e 13 saídas NC:

| Quantidade | CI | Função |
|---|---|---|
| 1 | SN74HC174 | Seis bits de fase, com clear compartilhado |
| 1 | SN74HC74 | Dois estágios de amostragem de ACK |
| 5 | SN74HC377 | Endereço de 16 bits, dado de escrita, descritor de escrita e MDR |
| 2 | SN74HC125 | Distribuição de clock e de clear/qualificadores de segurança |
| 4 | SN74HC08 | Portas AND |
| 3 | SN74HC32 | Portas OR |
| 1 | SN74HC04 | Inversores |

Os sete bits não usados do descritor recebem zero e suas saídas são NC. Um HC74 com multiplexação de retenção exigiria outro pacote neste bloco isolado; a decisão privilegia armazenamento independente do modo de escrita, sem alegar BOM otimizada.

Entradas: CLK, RESET_N, POWER_GOOD, START, endereço/dado/modo da operação, ACK_RAW e dados de leitura. Saídas: READY, DONE, REQUEST, WRITE_ENABLE, endereço/dado retidos e leitura retida. O endereço/dado do HC377 não têm reset: antes da primeira captura podem ser desconhecidos, mas REQUEST/WRITE_ENABLE ficam inativos. Não tratar payload inválido como transação.

Todos os sinais externos devem cumprir níveis CMOS dos CIs HC. Dados ou ACK vindos de uma saída TTL não estão automaticamente compatíveis; o condicionamento HC/HCT da interface real de memória ainda será definido. POWER_GOOD é uma entrada lógica, não um supervisor analógico já projetado.

## Fases conectadas por portas e flip-flops

Não há `case` comportamental implementando a máquina de estados dentro do modelo gerado. Suas equações são portas reais conectadas aos seis D/Q do HC174:

| Fase | Ação |
|---|---|
| IDLE, todos os bits zero | Aceita START somente com ACK bruto e ambos os estágios baixos |
| P0 CAPTURE | Habilita a captura do endereço, dado e descritor no próximo flanco |
| P1 SETTLE | Aguarda um intervalo completo de clock após a captura |
| P2 ACTIVE | Mantém REQUEST e o payload retidos; aguarda ACK sincronizado |
| P3 DRAIN | REQUEST baixo; espera ACK sincronizado retornar a zero |
| P4 DONE | Pulso de conclusão; leitura já retida no MDR |
| P5 LOCK | Não rearma enquanto START ou qualquer estágio de ACK estiver alto |

O HC74 usa dois estágios de amostragem. O MDR captura os dados quando ACTIVE e ACK2 estão ativos, antes de o pedido ser retirado. O periférico deve conservar o dado até essa captura e cumprir o handshake de quatro fases, mantendo ACK até REQUEST baixar. Pulsos/glitches arbitrários de ACK não são um protocolo suportado.

O emissor conserva endereço/dado/modo até a captura. Depois disso pode alterá-los sem afetar a transação ativa. START mantido não repete a operação; ele deve cair para rearmar. READY é amostrado sincronamente, não usado como clock. A árvore combinacional de detecção de IDLE pode ter transientes entre flancos; os sinais de pedido/conclusão vêm de fases registradas e devem respeitar as condições temporais do bloco.

RESET_N/POWER_GOOD invalidam as fases e qualificam REQUEST, WRITE_ENABLE e DONE. Na simulação ideal, cancelamento ocorre após a propagação em deltas; com atrasos, há latência de propagação. Isso não demonstra ausência de pulsos durante uma rampa analógica de alimentação. A memória/periférico também deve receber reset/invalidação para cancelar trabalho antigo; não há rollback de uma escrita já completada.

Não foi acrescentada tolerância a upset ou a estados multiativos por falha física. A sequência normal, após reset válido e dentro da temporização, mantém a codificação de fases. Metastabilidade e MTBF não são simulados pelos flip-flops ideais.

## Integração com a CPU

`tools/make_transaction_cpu.py` deriva um adaptador novo da NET-02, mantendo os arquivos anteriores intactos. Substitui os registradores RTL de endereço/dado, o descritor, o MDR e a espera de transação pelo bloco da netlist. O núcleo mantém START até DONE; em seguida espera READY antes de avançar a microinstrução de memória. O dado já fica no MDR físico modelado, sem outro registrador RTL duplicado.

SP continua sendo atualizado pela microinstrução posterior à conclusão; WAIT não permite avançar PC/SP/flags. A captura de X, a ALU, os guardas de pilha, a ROM e o sequenciador de microinstruções continuam com os níveis de modelo anteriores. **A geração física dos sinais da ROM e de SP_UPDATE ainda não foi concluída.**

As fixtures preservam as comparações arquiteturais da RTL-01. Na bancada exaustiva de guardas, o evento observado passa de REQUEST imediato para `bus_start`, pois um pedido externo agora aparece somente depois das fases de captura/estabilização. O critério de rejeição continua sendo não iniciar acesso e conservar SP; as regressões completas conferem as transações externas subsequentes.

## Bancadas

O handshake acrescenta ciclos; a comparação é de instruções e transações, não de contagem de ciclos idêntica à versão anterior.

`verification/net03/results.json` registra as fontes/hashes, comandos, versões, saídas e configurações:

- Varredura de 65.536 endereços, uma operação por endereço, alternando leitura/escrita, com padrões de dados e esperas variáveis. As fontes são invertidas depois da captura para detectar acompanhamento indevido durante WAIT. Há 294.912 verificações do payload retido e 196.608 verificações de START mantido, por cenário ideal/temporal. Não é o produto exaustivo de todos os dados, tipos e atrasos.
- 84 cortes de reset/energia e ACK antigo em pontos da sequência, por cenário. O bloco não pode concluir nem emitir nova transação a partir do ACK antigo após reset.
- Varredura adicional de seis posições digitais de ACK, antes/no/depois do flanco, para leitura e escrita: 12 casos por cenário, registrados em `ack-phase.json`. Eles permitem a diferença de latência da amostragem; não simulam metastabilidade.
- 6.886 casos de instruções por configuração de X, incluindo os 26 opcodes válidos e os 230 inválidos, contra a referência da RTL-01 com ADR E04.
- Cortes de reset/energia nas 26 instruções integradas; os números efetivos aumentam porque o handshake agora tem mais ciclos. Resultados exatos no JSON.
- 524.288 casos dos limites de SP/boot/CALL/RET/PUSH/POP no primeiro microcomando de pilha.
- Boot EEPROM → RAM, 132.197 instruções e 232.576 transações, por configuração de X; cada instrução/transação e o quadro VGA posterior são comparados à referência. Clocks diferentes permanecem unidades digitais de simulação.
- Falhas intencionais: enable do endereço preso ativo, entrada do primeiro ACK aberta, setup do estado, hold de dados e setup/hold de enable do HC377. Devem falhar com mensagens específicas; não são falhas reais convertidas em aprovação.

Os cenários/configurações repetem entradas; não somar seus números como amostras independentes. O modo `--quick` reduz a varredura e omite os programas completos, sendo apenas preparação.

## Temporização e cargas

O cenário temporal é **somente do bloco isolado**, a 4,5 V e com envelopes de saída para 50 pF, aplicáveis às colunas de −40…85 °C. Atrasos usados em ns: HC174 CLK/CLR→Q 40, HC74 CLK→Q 44 e CLR→Q 58, HC377 CLK→Q 40, HC08/32 25, HC04 24 e HC125 36. QN não é usado e seu atraso não é validado.

Monitores verificam setup de 25 ns do estado, recuperação de clear de 25 ns, pulsos de clock/clear do HC174 de 20 ns; no segundo HC74, recuperação de 6 ns e clear de 25 ns. No HC377, verificam setup de dado/enable de 25 ns e hold de 5 ns. O primeiro estágio assíncrono de ACK não recebe uma falsa exigência de setup síncrono; o monitor não modela sua metastabilidade. A inicialização dos monitores ocorre após o período inicial de 5 µs. Os testes negativos exercitam suas rejeições.

A bancada usa níveis de clock de 500 ns no cenário temporal. Os quatro ramos de clock têm o mesmo atraso selecionado; não há varredura independente de mínimos/máximos ou skew. Portanto, aprovação nesse cenário **não fecha hold nem garante frequência da placa inteira**. As regressões de CPU usam os modelos sem atrasos.

`fanout.json` contabiliza no máximo quatro entradas por sinal interno. A hipótese é até 10 pF por entrada e 10 pF de reserva de trilha, dentro de 50 pF por saída. Clock e segurança são distribuídos por quatro canais cada. Isso é orçamento: trilhas, saídas do barramento e cargas externas ainda precisam ser conferidas no layout. O arquivo não mede a capacitância de um barramento de memória real.

## Reprodução e limites

```text
python3 tools/build_transaction_bank.py
python3 tools/make_transaction_cpu.py
python3 tools/run_transaction_netlist.py
python3 tools/run_ack_phase.py
python3 tools/record_net03_manifest.py --check
```

Rodar no Ubuntu WSL a partir de `/mnt/c/Users/gabri/projetos/isa1`. KiCad CLI 7 exporta o esquema, XML e PDF; Icarus executa a netlist. Compilações e fixtures ficam em `/tmp`. Conferência de pinos/drivers e orçamento de carga não são ERC. Não há SPICE do circuito completo, footprints escolhidos, PCB, DRC ou ensaio físico aprovados.

Os próximos blocos são o sequenciador de microcódigo, a retenção/decodificação dos sinais das ROMs e a geração física de SP_UPDATE. A interface de memória, condicionamento TTL/CMOS, reset/supervisão USB-C, VGA e teclado físicos continuam na lista de produção.

## Fontes

Datasheets TI completos e seus avisos são preservados em `references/ti`, com hashes no manifesto:

- [SN74HC174, SCLS119E](https://www.ti.com/lit/ds/symlink/sn74hc174.pdf), pinagem p. 3 e requisitos/atrasos pp. 5–6.
- [SN74HC74, SCLS094F](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), pinagem p. 3, requisitos/atrasos pp. 7–8.
- [SN74HC08, SCLS081J](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf), pinagem e tabela de atrasos.
- [SN74HC32, SCLS200F](https://www.ti.com/lit/ds/symlink/sn74hc32.pdf), pinagem e tabela de atrasos.
- [SN74HC377, SCLS307D](https://www.ti.com/lit/ds/symlink/sn74hc377.pdf), pinagem p. 3, requisitos p. 5 e atrasos p. 6.
- [SN74HC04](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf) e [SN74HC125](https://www.ti.com/lit/ds/symlink/sn74hc125.pdf), já usados na NET-02.
