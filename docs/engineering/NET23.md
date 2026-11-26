# NET-23 — Osciladores candidatos no esquema

26/11/2026. Base publicada `cbb38703c34cf119612f39ecb0255940e670f974` (NET22).
Variante separada; validação digital selecionada concluída. Não há placa
liberada nem oscilador/BOM homologado.

## Configuração construída

Dois módulos [Abracon ACH](https://abracon.com/Oscillators/ACH.pdf) candidatos,
25,175 MHz para vídeo e 100 kHz para CPU,
alimentados pelo trilho interno proposto de 5,392 V, dentro de 4,5–5,5 V.
Pinagem de quatro pinos: 1 enable/NC, 4 GND, 5 saída, 8 VDD. Configuração
proposta L/C/T/A, faixa −40…85 °C, ±50 ppm inicial/temperatura e duty
47,5/52,5%. Enable fica em VDD, sem gate assíncrono pelo reset. Código completo
de compra e garantia específica de jitter/partida sob rampa continuam abertos.

Usar **carga padrão de 15 pF**, evitando atribuir os tempos da tabela padrão
automaticamente à opção de 50 pF. O clock de vídeo recebe uma única entrada
AHC125 de U34; seu orçamento passa a exigir até 5 pF de trilha/pads além dos
10 pF máximos de Ci na condição de 5 V. São limites para o futuro layout,
não capacitâncias medidas ou extraídas.

O clock da CPU alimentava duas entradas de U7, excedendo 15 pF já nos CIs.
Reutilizar os dois inversores Schmitt livres de U2 (canais4/5): uma entrada
recebe CPU_OSC e a dupla não inversora CPU_CLK alimenta os dois ramos de U7.
O canal0 de U1 permanece desabilitado. Mesmo número de CIs de lógica,
mais dois módulos osciladores e seus capacitores.

A tentativa intermediária usava U1 AHC125. A conferência do
[AHC125](https://www.ti.com/lit/ds/symlink/sn74ahc125.pdf) identificou limite de
entrada de **20 ns/V em 5 V ±0,5 V**, não 100 ns/V (esse valor é de 3,3 V).
O ACH de 100 kHz lista Tr/Tf máximo de 40 ns, sem definir aqui sua forma de
onda. Isso não demonstra por si só o slew local. Escolher as duas portas
[Schmitt AHC14](https://www.ti.com/lit/ds/symlink/sn74ahc14.pdf) evita depender
de uma hipótese de transição linear para essa recepção. Não se afirma que
uma unidade com AHC125 tenha falhado fisicamente.

`hardware/clocked_reset`: **26 componentes, oito CIs (sete de lógica e um
supervisor), dois módulos
osciladores, 144 pinos e sete NC**. O XML KiCad confere todos os pinos/valores;
os valores identificam configurações candidatas, sem inventar códigos de compra.
CPU_OSC e MASTER ficam com 15 pF previstos; CPU_CLK, após Schmitt, com 30 pF.
Há dois negativos de contrato: bypass do receptor da CPU e enable no RAW.
Nenhum capacitor de trilha foi extraído. A união candidata tem 459 CIs mais
dois módulos osciladores, antes dos demais circuitos ausentes.
Os 75 mA máximos listados para os dois intervalos de frequência dos ACH
precisam caber no futuro orçamento global; 1,5 A de NET21 é hipótese de carga,
não consumo previamente calculado ao qual se possa somar ou subtrair sem análise.

Alternativas: [LVC2G125](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf)
tem Ci=3,5 pF **típico em 3,3 V**, não máximo garantido em 5 V. PDF primário
e extração foram preservados em `references/net23`/`verification/net23/research`.
Sua entrada a 5 V também tem limite de transição próprio; não promover esse
buffer a solução validada apenas por seu atraso menor.
Dois osciladores em 3,3 V exigiriam regulação e
tradução, com nova análise de distorção dos pulsos. Nenhuma dessas alternativas
foi homologada ou implementada por haver apenas um PDF disponível.

## Evidências concluídas

| Bancada | Resultado observado na variante Schmitt |
|---|---|
| Fonte/reset/raster | Seis cenários: quatro cruzando políticas binárias0/1, reset antes/depois da partida, duty47,5/52,5% e frequência inicial/temperatura±50ppm; cada um tem duas partidas e três cortes RAW. Dois casos com fonte da CPU ou MASTER ausente mantêm acesso inibido |
| Modelo de oscilador | Dois positivos com48 bordas cada verificam interrupção durante startup e nova partida; três parâmetros inválidos rejeitados. Enable fica alto, como no circuito |
| CPU real nominal | Quatro escritas interrompidas e quatro scans reiniciados, duas por política, sem semear SRAM/sem rollback, WE até84ns |
| CPU com frequências opostas | Mais quatro cortes/scans reiniciados: CPU−50/Master+50ppm e CPU+50/Master−50ppm, políticas0/1; WE até84ns. Não é varredura contínua de fase/jitter |
| Pinos SRAM e clock ausente | Escrita/leitura normal e um corte ativo do mestre de teste, WE84ns; duas ausências de clock bloqueiam WE mesmo com pedido artificial. Forçar SAFE_MEMORY alto deve cair no monitor independente |
| Vetores ideais | 6.886 casos/13.406 transações, 570.876 verificações WAIT; clocks e startup escalados explicitamente para essa bancada |
| Vetores temporizados | Dois cenários, CQ normal/antecipado do estado do controlador, cada um com1.062 casos/1.821 transações/3.645 verificações WAIT; setup observado54,888/36,944/46,944ns e74 eventos na fronteira binária de cada estágio do raster; sem falhas |

O modelo de oscilador inicia desconhecido e só gera pulsos depois da janela
de startup configurada. Power_valid é uma condição de alimentação qualificada
do modelo, separada do RAW do supervisor. Não é modelo analógico da fonte,
do cristal ou dos transistores. Enable desabilitado não é caracterizado como
um modelo completo de Hi-Z: o circuito o mantém em VDD e a calibração também.
Não há jitter, aging nem dispersão por alimentação/carga garantidos nesse modelo.

`sim/net23/isa1_clocked_memory.sv` remove os dois clocks externos da interface
da memória e usa as saídas das fontes nativas; a CPU recebe cpu_core_clk e
cpu_reset_n. Permanecem as 26 instruções, X/SP/flags/VGA, payload estável em
WAIT e COMMIT único. As ROMs são idênticas à base. As bancadas de instruções
usam seeds de fixture após readiness e fora da borda do backend; os scans
da CPU real não semeiam SRAM. Não houve novo boot/quadro completo nesta etapa;
a execução de 132.197 instruções/76.800 pixels permanece evidência NET22.

ERC parcial: **12 violações**, duas de alimentação, uma de entrada e nove
rótulos isolados; saída nativa5/host1, sem exceções. PDF/preview gerados e
inspecionados. União global e apresentação final da placa continuam necessárias.

## Proveniência e desenvolvimento

A configuração intermediária com AHC125, seus resultados e grafos estão em
`verification/net23/development/pre-cpu-schmitt`, com30 arquivos copiados e
conferidos por hash. Eles não são aprovação da variante Schmitt. Os testes
relevantes foram repetidos depois do rebuild final, com fontes congeladas.

Erros de desenvolvimento preservados: valor do oscilador omitido pelo emitter
e contagem incorreta de uma substituição; amostragem do contador de bordas na
mesma região do simulador; negativo cujo REQ não chegou a armar o controlador;
rename da instância ideal sem parâmetros. As correções mantêm comparações
XML,48 bordas mínimas e monitores dos pinos. O negativo de clock ausente agora
espera reset dos bancos e20 ciclos de backend com REQ baixo antes de pedir
escrita; o bypass de SAFE é detectado. A correção ideal usa runner separado,
preservando os inputs da execução temporizada que já estava em andamento.

Fontes, transformações, comandos/saídas, versões e SHA-256 estão nos relatórios
e arquivos `*-origin.json`. Nenhum original em archive/revisions foi alterado.
`annotate_clock_counts.py` corrige somente a classificação de oito CIs em
sete digitais e um supervisor; preserva o relatório original do builder.
Não altera circuito, pinos ou resultados e não representa uma nova simulação.
Supervisor analógico continua um forcepoint qualificado; não declarar POR
real, MTBF, jitter ou funcionamento com VDD inválido aprovados.

Reprodução sequencial no WSL: builder `build_clocked_reset.py`, anotador
`annotate_clock_counts.py`, adaptadores `prepare_clocked_cpu.py`,
`prepare_clocked_vectors.py` e `prepare_clocked_ideal.py`; depois as bancadas
`run_clock_sources.py`, `check_clock_model.py`, `run_clocked_memory_start.py`,
`run_clocked_cpu_fault.py`, `run_clocked_cpu_corners.py`,
`run_clocked_vectors_ideal.py` e `run_clocked_vectors.py --timed --quick`
(também com `--early`). Use `check_clock_source_loads.py`,
`check_clocked_reset_erc.py`, `record_clocked_environment.py` e o manifesto
para conferir os demais registros. O ERC continua retornando violações.

Continuam necessários: circuitos e análise global, fonte/USB-C/consumo/POR,
DAC, firmware de eventos, união/ERC, footprints/BOM/PCB/DRC e protótipo físico.
Analisar também a distorção de duração de pulso ao atravessar vários buffers
do backend. Os atrasos simétricos dos testes não fecham automaticamente esse
caminho global. A falta histórica de diagnostic.asm permanece registrada.
