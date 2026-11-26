# NET-19A — CPU, teclado e MMIO por pinos

26/11/2026. Base Git `9a21166ebdcd8d0dd118345e27b735ee75296984`.
Trabalho novo, separado das fontes recuperadas e de NET-14C/15/17/18.
**Integração digital; placa e alimentação global não liberadas.**

## Circuito e comportamento

A CPU global, decoder, SRAM/EEPROM/barramento e raster já existentes agora
usam os registradores, drivers, amostradores e contador de acomodação da folha
`keyboard_500`. Foram removidos do novo adaptador o armazenamento procedural
dos bancos/ROW e o cálculo procedural das colunas: a leitura vem dos pinos da
matriz ideal, dois estágios de amostragem e muxes físicos da NET-17.

O controlador espera KEY_READY para ler colunas. Não muda ISA, X, pilha, flags,
mapa, formato EEPROM, VGA ou efeito único de COMMIT. Mantém payload retido,
liberação do driver antes de devolver VRAM ao vídeo e os ACKs prolongados.

| Endereço | Função preservada |
|---|---|
| A000h | VB, dois bits |
| A001h | EB, um bit |
| A002h | BOOT_OFF, bit 0 retido; zero não religa overlay |
| A010h | ROW, dois bits; toda escrita reinicia a espera |
| A011h / A012h | Colunas baixa/alta, ativas em zero; leitura aguarda KEY_READY |

`hardware/system_access` é uma variante **de 31 CIs**, 62 componentes, 526 pinos
e nove NC. Apenas três pacotes de estado U1/U2/U3 mudam de HC174 para AHC174;
todos os pinos, passivos, conexões e lógica permanecem iguais. A conferência
compara o grafo inteiro e os textos das duas netlists, permitindo somente essas
substituições de classe e o nome/parâmetro do módulo. Não é economia fictícia de
componentes nem uma edição apenas do monitor temporal.

## Defeito temporal encontrado e candidato

A integração temporizada inicial rejeitou o controlador anterior: no caso 363
da bancada reduzida, LDA absoluta de VRAM em 8000h, a entrada de estado mudou
**18,944 ns** antes do relógio, contra os 25 ns usados para HC174. A nova condição
de acomodação do teclado acrescenta profundidade ao caminho de concessão; o
ensaio isolado com SLOT constante não expunha esse caminho.

O candidato [SN74AHC174, TI SCLS425H](https://www.ti.com/lit/ds/symlink/sn74ahc174.pdf)
mantém a pinagem. Nos limites selecionados de 4,5–5,5 V, −40 a 85 °C e CL de
50 pF: setup 4,5 ns, hold 0,5 ns, recovery 2,5 ns, pulso mínimo de 5 ns, CLK→Q
máximo 10,5 ns e clear máximo 11 ns. O cenário antecipado usa CLK→Q de 1 ns.
São limites de um candidato, não homologação de BOM ou varredura de todos os
mínimos/máximos independentes, skew, transições e cargas reais.

Dois cenários temporizados de 1.062 instruções passaram. O menor setup observado
foi 54,888 / 18,944 / 28,944 ns em U1/U2/U3: margem mínima selecionada **14,444 ns**
contra 4,5 ns. Reverter os três pacotes para os modelos HC174 do grafo anterior
reproduz a rejeição por setup. Não se reduziu o requisito do componente antigo.
Dois testes de atraso e cinco violações propositais calibram os novos monitores.

Ci máximo de 10 pF e ICC estático máximo de 40 uA por pacote têm condições de
datasheet; ICC pressupõe entradas nos trilhos e saída sem carga. Não fecham o
consumo dinâmico nem o orçamento da placa. A união candidata continua em 456 CIs,
agora 30 famílias, incluindo a folha de reset ainda não integrada.

## Evidências concluídas

| Bancada | Resultado no escopo executado |
|---|---|
| Instruções ideal | 6.886 casos, 13.406 transações; arquitetura comparada à referência |
| Instruções com atrasos | 1.062 casos / 1.821 transações em cada um dos cenários de CQ selecionados |
| Boot/programa/quadro ideal completo | 132.197 instruções retiradas, 232.576 transações, 76.800 pixels; PPM completo idêntico |
| Reset/PG digital ideal | 4.562 cortes, todos os 26 índices; oito abortos RAM e sete VRAM registrados, sem rollback prometido |
| Reset/PG com atrasos | 1.692 cortes em sete lotes completos, índices 0–25 sem omissões; contrato de reset global anterior |
| Varredura com firmware na CPU e atrasos | Cinco quadros estáticos em cada configuração binária 0/1 de reset; 40 leituras, 20 escritas ROW concluídas por execução e uma escrita da tentativa abortada |
| Pausa/reset durante varredura | Relógio da CPU parado sem bloquear raster/ACK; leitura pendente cancelada e programa reiniciado |
| Negativos | Liberação antecipada das colunas, atualização de registro sem COMMIT amostrado e retorno aos HC174 são rejeitados |
| ERC parcial | 135 violações: duas de alimentação, 45 entradas e 88 etiquetas isoladas; retorno nativo 5, sem exceções |

O programa completo desabilita FIXTURE_DEFAULTS: **SRAM começa desconhecida**.
O loader escreve a aplicação em RAM e o diagnóstico preenche VRAM por transações
reais. CPU/MMIO não são semeados nesse programa. A imagem de referência PNG é
retida somente após a comparação byte a byte do PPM capturado.

Os lotes de segurança temporizados têm relatório separado em
`verification/net19a/timed-safety-batches.json`. Exigir sete lotes completos,
índices cobertos exatamente 0–25, saída zero e RESULT; um processo parcial ou
interrompido não aprova cobertura. O texto legado `opcodes=26` é o tamanho do
array, não a quantidade efetivamente exercitada em cada lote.

Os 1.692 cortes temporizados diferem dos 1.700 da etapa anterior porque o laço
calcula o fim dos cortes a partir da latência efetiva de cada instrução nessa
fixture. Não foram removidos índices, tipos de falha ou posições entre zero e
baseline+2; sete intervalos e contagens estão registrados separadamente.

## Verificador de COMMIT e preparação das bancadas

O monitor antigo conferia o nível de IO_COMMIT no instante posterior em que
BOOT/VB/ROW mudavam. O traço do caso de vetor 3.663 mostrou `captured_commit=1` na
borda do registrador e `io_commit_now=0` quando a saída foi observada: a captura
era válida. O monitor novo confere a autorização amostrada no **CLK real de U1**
e verifica as mudanças do registrador; um defeito que força NEXT_0 durante
operação sem escrita é rejeitado. Comparação de estados/transações e estabilidade
da CPU em WAIT continuam ativas. Não se removeu a propriedade de efeito único.

As bancadas de vetores semeiam estado para isolar instruções, como seus
antecessores. Os bits MMIO são semeados fora da borda do backend, com ACTIVE=0,
**antes** da mudança de geração da memória. Depois retorna-se à borda negativa
da CPU. Uma tentativa que introduziu tempo entre geração e preenchimento dos
arrays capturou o padrão 71h no lugar do primeiro opcode; a falha é preservada.
Geração e preenchimento continuam atômicos no mesmo ciclo delta da fixture.

Na varredura temporizada, o snapshot do payload ocorre após os 500 ns de
propagação de lançamento já usados pelo predecessor; a captura inicial em 1 ps
era cedo demais. Após essa acomodação, WAIT é verificado sem permitir mudanças.
Fontes, hashes, traços e falhas estão em `verification/net19a/development`.
Os runners iniciais `run_keyboard_cpu.py` e `run_system_cpu.py` conservam a
bancada de vetores antiga; usar **run_system_vectors.py** para aceitação das
instruções. `run_system_cpu.py --bench program` usa o programa completo, que não
contém aquele monitor de vetores.

## Firmware e limites

`firmware/net19a/keyboard_scan.asm` é diagnóstico **novo**, montado em C040h.
Varre quatro linhas, lê oito bytes e escreve RAM 6000h–6007h, com 26 instruções
incluindo o salto de boot. A imagem EEPROM de 32 KiB fica no relatório da
varredura; não é o `diagnostic.asm` histórico ausente.

Esse firmware é leitura bruta: debounce, política conservadora de até duas
teclas, CANCEL/ALL_UP e fila continuam contrato host da NET-17. O trio em L da
bancada testa fechamento **digital ideal**, sem aprovar tensão de todos os
fantasmas a 500 ohm ou ampliar o reconhecimento simultâneo. Contatos, isolação,
capacitâncias e bounce das unidades permanecem não medidos.

Clocks são estímulos: ideal escalado; temporizado com mestre de 25,175 MHz e CPU
de 100 kHz. O raster e os dois FFs U41 mantêm as fronteiras binárias de reset
documentadas, sem MTBF aprovado. Os demais monitores não foram desativados.
As duas configurações da varredura não constituem uma cobertura exaustiva das
aberturas assíncronas; os 90 eventos por estágio nos vetores temporizados
pertencem à configuração de resolução tardia documentada nesses relatórios.

**NET-18 ainda não fornece os domínios desta integração.** Reset/PG aqui seguem
o estímulo global anterior. Não extrapolar os cortes digitais para brownout,
partida fria ou ordem física WE/bancos sob mínimos/carga/skew. Distribuição de
clock e fanout entre folhas, temporização global, fonte, DAC, união de esquema,
footprints, ERC/DRC e protótipo continuam critérios de produção.

## Reproduzir no Ubuntu WSL

```text
python3 tools/build_system_access.py
python3 tools/make_system_cpu.py
python3 tools/prepare_system_vectors.py
python3 tools/check_system_access.py
python3 tools/check_ahc174_limits.py
python3 tools/run_system_vectors.py
python3 tools/run_system_vectors.py --timed --quick
python3 tools/run_system_vectors.py --timed --early --quick
python3 tools/run_system_vectors.py --bench safety
python3 tools/run_system_safety_batches.py
python3 tools/run_system_vectors.py --quick --negative-bank
python3 tools/run_system_vectors.py --timed --quick --legacy-state
python3 tools/run_system_cpu.py --bench program
python3 tools/run_system_scan.py --timed
python3 tools/run_system_scan_policy0.py --timed
python3 tools/run_system_scan.py --negative
python3 tools/check_system_access_erc.py
python3 tools/record_net19_manifest.py --check
```

ERC retorna 5 pelas pendências reais. Negativos só aprovam sua **rejeição
específica**, não qualquer erro de compilação/timeout. Não regenerar fontes
enquanto uma execução que as usa estiver em andamento.

`environment.json` complementa os relatórios com versões e os quatro inputs de
ROM, conferidos contra o commit base. Essa metadata foi coletada depois dos
ensaios, como indicado no arquivo; CPU/lotes também registraram Icarus ao iniciar.
