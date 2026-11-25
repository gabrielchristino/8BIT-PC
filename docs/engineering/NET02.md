# NET-02 — pilha simulada a partir do esquema

Desenvolvimento novo de 25/11/2026 sobre a RTL-01 do commit `6bbac525a4435f87566ccb723e733134e21d3e43`. O primeiro caminho físico de SP agora usa a mesma pinagem que o esquema KiCad: esquema nativo → XML exportado pelo KiCad → SystemVerilog conectado por pinos → CPU comandada pelas ROMs originais. **É um bloco parcial com simulação funcional; não é a placa completa liberada para fabricação.**

## Circuito e contrato

O banco contém dois SN74HC273 (16 bits de armazenamento), quatro SN74HC157 (retenção/atualização), quatro CD74HC283 (soma de 16 bits), um SN74HC04 (duas inversões e quatro entradas não usadas aterradas) e um SN74HC125 (quatro buffers de direção). Doze capacitores de 100 nF são propostas de desacoplamento. São 24 componentes e 220 pinos, incluindo cinco saídas NC.

O valor arquitetural de SP continua sendo 8000h quando vazio. Para produzir esse valor com o clear dos HC273, somente o bit 15 é armazenado invertido: `Q = SP XOR 8000h`. Isso é codificação interna, não outra convenção de pilha. Um inversor decodifica Q15 e outro codifica SUM15 antes de armazená-lo. Reset limpa os registradores e resulta em SP=8000h depois dos atrasos do clear/inversor. A verificação funcional de reset usa o modelo sem atrasos; o cenário temporal aguarda a propagação.

Os somadores recebem B=0001h para incremento e FFFFh para decremento, com carry inicial zero. Há um único somador compartilhado para SP+1 e SP−1; o sinal DOWN seleciona a operação. SP e SUM estão simultaneamente disponíveis. O circuito aritmético faz wrap; os guardas externos impedem que uma operação arquitetural inválida o utilize.

UPDATE=0 faz os multiplexadores realimentarem Q. UPDATE=1 seleciona a soma codificada para o próximo flanco positivo. Todos os registradores usam o mesmo clock, sem clock derivado ou chaveado. RESET_N é clear ativo baixo; sua remoção precisa respeitar a recuperação dos componentes.

A CPU adaptada conserva o controle e os guardas da RTL-01. Durante PUSH/CALL, seleciona SP−1 e retém o endereço no latch de barramento antes de WAIT. Somente depois da confirmação e do retorno de ACK ao repouso a microinstrução de decremento atualiza SP. POP/RET retêm SP para leitura e depois incrementam. O latch do endereço e a geração física de UPDATE/DOWN ainda são externos ao esquema parcial; na integração, são RTL. Não há compartilhamento deste somador com X.

## Uma ligação entre esquema e modelo

`tools/build_stack_bank.py` cria símbolos de pacote completos, com funções de pinos transcritas dos datasheets TI; não assume características de símbolos LS. O esquema é exportado com KiCad CLI 7.0.11. O conversor lê os nós `(referência,pino)` desse XML e os conecta a modelos funcionais dos CIs. Capacitores constam da netlist, mas não têm efeito na simulação digital.

O fluxo verifica correspondência entre os 220 pinos esperados e exportados, entradas flutuantes, alimentação incorreta, múltiplos drivers, nomes colidentes e componentes não suportados. Esses controles **não são ERC**. Não verificam todas as regras elétricas ou geometria de PCB.

`tools/make_stack_cpu.py` aplica transformações limitadas e verificadas à CPU RTL-01: substitui armazenamento e aritmética de SP pela netlist, sem modificar ROMs, ISA, flags ou handshake. As fixtures dos testes são adaptadas em `/tmp` para semear os dois registradores físicos; suas comparações são preservadas. Os arquivos RTL-01 e as fontes históricas permanecem intactos. As seeds não representam uma porta de carga que exista no circuito.

## Evidência e escopo dos testes

Os resultados exatos ficam em `verification/net02/results.json`:

- Banco de SP: todos os 65.536 valores e ambas as direções, 131.072 atualizações, 131.072 verificações de retenção e 512 resets, por cenário ideal/temporal. Os cenários usam as mesmas entradas.
- CPU: 6.886 casos por configuração de X, com transações e estado comparados à referência da RTL-01, incluindo a extensão de segurança da ADR E04.
- Reset/energia: cortes digitais nas 26 instruções, sem novas escritas ou retomadas após invalidação; efeitos anteriores já confirmados não são desfeitos.
- Guardas: 524.288 valores/combinações no primeiro microcomando de CALL/RET/PUSH/POP, incluindo boot ativo/inativo.
- Programa completo: boot EEPROM → RAM, 26 opcodes, 132.197 instruções, 232.576 transações e quadro VGA conferido, por configuração de X. A CPU com SP da netlist é comparada a cada instrução/transação.
- Testes negativos: ligação errada de B0 deve falhar na aritmética; D0 aberto deve ser rejeitado pelo conversor; violações de setup, recuperação e pulsos devem ser rejeitadas pelo monitor HC273. Falhas esperadas são classificadas separadamente, sem tornar um defeito real em aprovação.

## Temporização e carga

O cenário temporal **do banco isolado** usa 4,5 V, carga de saída de 50 pF e os limites aplicáveis a −40…85 °C. Parâmetros em ns: HC273 CLK/CLR→Q=40, HC157→Y=38, HC04→Y=24, HC125→Y=36, HC283→SUM=58 e →COUT=49. SUM usa um envelope comum conservador, abrangendo os caminhos de carry. Isso não modela a implementação interna do adder.

O monitor HC273 exige setup de dados e recuperação de clear de 25 ns, pulso de clear e cada nível do clock de pelo menos 20 ns. O datasheet especifica hold de dados igual a zero nessa condição. A bancada usa níveis de clock de pelo menos 500 ns e intervalos de estabilização definidos. Seu resultado não estabelece a frequência física da CPU: as regressões integradas continuam usando modelos sem atrasos e clocks ideais.

DOWN inicialmente alimentava 15 entradas de somadores. O candidato final usa quatro buffers, um por nibble, com três ou quatro cargas por saída. Reservando 10 pF por entrada e até 10 pF de trilha, o alvo é até 50 pF por saída; essa reserva ainda precisa ser verificada no layout. DOWN passa a carregar quatro entradas de buffer. UPDATE carrega quatro seletores, CLK e RESET_N dois HC273 cada. O orçamento global de clock/reset, o slew e os drivers externos permanecem pendentes.

Os modelos de atraso são envelopes selecionados com clock sem skew; não cobrem todos os cantos nem alimentação analógica. Ainda faltam análise global de clock/controle, capacitâncias reais, distribuição de alimentação, impedâncias, remoção de reset, ruído e compatibilidade com as saídas TTL das memórias quando aplicável. Não há SPICE de placa, footprints conferidos, PCB, ERC ou DRC aprovados.

## Reprodução no Ubuntu WSL

```text
python3 tools/build_stack_bank.py
python3 tools/make_stack_cpu.py
python3 tools/run_stack_netlist.py
python3 tools/record_net02_manifest.py --check
```

Executar na raiz `C:/Users/gabri/projetos/isa1`, montada em `/mnt/c/Users/gabri/projetos/isa1`. O build requer KiCad CLI e os testes Icarus Verilog. `--quick` omite os programas completos e reduz casos por opcode; esse modo é apenas preparação, nunca aprovação da etapa inteira.

## Fontes primárias

- TI [SN74HC273, SCLS136F](https://www.ti.com/lit/ds/symlink/sn74hc273.pdf), pinagem p. 3, requisitos p. 7, atrasos p. 8.
- TI [CD74HC283, SCHS176E](https://www.ti.com/lit/ds/symlink/cd74hc283.pdf), pinagem p. 3, atrasos p. 6.
- TI [SN74HC04, SCLS078H](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf), pinagem p. 3, atrasos p. 6.
- TI [SN74HC125, SCLS104F](https://www.ti.com/lit/ds/symlink/sn74hc125.pdf), pinagem p. 3, capacitância/atrasos p. 6.
- TI [SN74HC157, SCLS113F](https://www.ti.com/lit/ds/symlink/sn74hc157.pdf), já arquivado na etapa anterior.

Datasheets completos estão em `references/ti`, com hashes no manifesto NET-02. O HC283 escolhido para este candidato é **CD74HC283 da TI**; o nome genérico histórico HC283 não foi transformado num código SN74 inexistente. Nenhuma escolha final de encapsulamento/BOM comercial ou alteração da licença do projeto foi feita.

Próximo bloco: controle físico de transações/UPDATE, retenção de endereço e geração/registro dos sinais de ROM, preservando a mesma estratégia de esquema → netlist → regressão. A emulação de SP agora deriva do esquema desse banco; o restante da CPU ainda não.
