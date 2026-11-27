# NET-30 — redistribuição com canais livres

26/11/2026. Base `b5a19c7ee72a9b8543060e77f9c26824daf271ca`.
Fechamento das regressões em27/11/2026: **candidato digital para continuidade**,
com resultados próprios abaixo. Não é temporização global, circuito analógico
ou placa liberada. O boot completo temporizado desta variante ainda é pendente.

## Circuito construído separadamente

- `hardware/load_distributed_keyboard`: U40 canal1 recebe WDATA0 retido e
  dirige U15.B0/U16.B0/U17.B0/U33.B1 por WDATA0_LOCAL; canal2 recebe BOOT
  e exporta BOOT_EXTERNAL. Realimentação local de BOOT permanece direta.
- `hardware/load_distributed_bus`: U28 canal2 recebe SELECT3 e dirige
  U25.B1/B2 por SELECT3_LOCAL.
- `hardware/load_distributed_video`: U35 canal2 recebe H2 e dirige o pino
  externo h[2] e U30.A3 por H2_EXTERNAL. Os outros três consumidores internos
  permanecem diretamente em H2. Isso preserva quatro cargas na fonte.

Todos são AHC125 já presentes, com OE em GND. Há15 mudanças de pinos:
oito no teclado, quatro na memória e três no vídeo. Não se acrescenta CI,
capacitor ou altera família/pinagem de pacote. A união mantém460CIs e dois
osciladores,982componentes; quatro saídas antes NC passam a conectadas,
elevando pinos conectados de7.810 para7.814. Todos os pinos XML foram
conferidos. A contagem conjunta ficou em até quatro entradas digitais por
saída, contra cinco/seis em quatro redes NET29. Isso não é extração de carga.

CPU/controlador/reset, ISA/X/pilha/flags/microcódigo e membranas permanecem
nos arquivos anteriores. Fontes NET27 ficam congeladas. Novos arquivos
`sim/net30` usam as mesmas fronteiras binárias explícitas de warm/reset;
não houve relaxamento de monitores para aceitar a mudança.

`tools/build_distributed_loads.py` reutiliza preparação em memória e emite
somente diretórios novos. Confere que as partes preparadas equivalem ao JSON
NET26 antes de mudar pinos. A primeira transformação do adaptador rejeitou
uma âncora ambígua antes de gerar; guarda corrigida com contexto completo,
sem alteração de hardware ancestral. Transformações e desenvolvimento ficam
preservados em verification/net30.

## Resultados das regressões

- Auditoria nativa/união: XMLs e15pinos alterados conferidos, nenhum CI novo,
  máximo de quatro entradas contadas. [Auditor](../../tools/audit_distributed_loads.py).
- 48 cortes SRAM em quatro cenários RC/política passaram: WE até94ns;
  dois negativos detectaram banco apagado cedo e endereço alterado sob WE.
- 6.886 vetores ideais/13.406transações/569.718 verificaçõesWAIT passaram.
- Quatro cortes de CPU nominais e scans após reinício passaram: WE até84ns,
  SRAM não semeada e epoch preservado, sem rollback.
- Dois cenários temporizados de1.062instruções/1.821transações passaram;
  setup observado54,888/16,944/26,944ns, sem aprovação de STA global.
- Mais quatro cortes CPU/scans com fontes em extremos opostos de50ppm
  passaram; oito cortes somando nominais/cantos, WE até84ns.
- Quatro cenários temporizados de quadros, duas políticas binárias por dois
  instantes de captura, passaram: dois quadros/210.000amostras por cenário,
  153.600pixels visíveis,25.200amostrasHSYNC,800VSYNC,2.014escritas e todas as
  32posições de concessão. VRAM/VB são seeds explícitos desse ensaio sem CPU.
  A primeira bancada de quadros aplicou só1us de reset frio e expirou:
  diagnóstico mostrou fases/armamento/banco indefinidos, sem SAFE. A RC
  exige asserção além de19us para essa inicialização. Fontes/logs preservados
  em development/frames-short-reset; nova tentativa começa RAW baixo por50us,
  sem mudar hardware, watchdog90ms ou monitores. Não é POR analógico aprovado.
- Boot/quadro ideal completo passou:132.197instruções,232.576transações,
  32.771transaçõesVRAM,76.800pixels idênticos por comparação byte a byte,
  5.355.850WAIT,46.465verificações de pausa,337escritasRAM/32.770VRAM,
  nenhum abort e FIXTURE_DEFAULTS=0/SRAM inicialmente desconhecida. A imagem
  foi inspecionada. Clocks/startup são escalados somente nesse ensaio ideal.
- Programa completo temporizado NET27 continua pertencendo à NET26,
  independentemente do resultado; não valida os quatro buffers novos.

`tools/run_distributed_load_job.py` cria registros por ensaio em
`verification/net30/jobs`, com fontes/hashes, comando e limites próprios:
1GiB por processo,3000sCPU/3600s de parede,8MiB por saída, sem core dump.
Vetores semeiam estado por contrato da bancada; boot completo não semeia
SRAM. O ensaio específico de quadros sem CPU semeia VRAM/VB explicitamente e
instancia os seis blocos do subsistema; o arquivo da CPU compilado é podado.

## Revisão nativa e limites

ERC parcial sem waivers: vídeo49(2power+13input+34isolated), teclado27
(2+12+13), memória172(2+88+82). Não é soma de erros de placa global e não
há ERC aprovado. PDFs/previews foram inspecionados. Depois de todos os jobs
NET30 terminarem, datas/títulos herdados foram corrigidos para27/11 e
NET-30V/K/B. Textos mudaram somente nesses campos; XMLs conservaram exatamente
componentes/valores/pinos/redes e modelosSV/JSONs não mudaram. Originais do
commit16a82e4 e cópias ficam preservados, com hashes antes/depois em
verification/net30/title-update-final. Relatórios de execução continuam
identificando os XMLs anteriores realmente usados, resolvidos nesse snapshot.
Uma primeira tentativa não produziu o JSON ERC do teclado; comando não foi
retido nessa etapa, portanto causa não foi inferida. Saídas parciais foram
preservadas/restauradas antes da nova rodada limitada a2GiB, com comandos
persistentes; ERC e grafos permaneceram iguais. Não foi falha da CPU.

Os buffers acrescentam atraso de dados e atividade/corrente dinâmica, mesmo
sem CIs extras. O modelo usa atraso selecionado10ns nesses canais; mínimos,
hold, assimetria, glitches/skew de decodificação, slew/jitter, capacitâncias
reais, alimentação/POR e MTBF continuam abertos. Ci10pF+10pF de trilhas é
orçamento de triagem, não garantia em todoVDD ou extração da placa.

O próximo programa completo temporizado usa tools/run_full_load_program.py,
com frequências nominais, startup10ms, progresso/snapshots e os mesmos limites
NET27. Preparação não é resultado. O ensaio antigo NET27 não valida os buffers
novos; mantê-lo identificado separadamente. Os156/128cenários específicos
NET26 não foram novamente executados como NET30 e não recebem nova contagem.
Produção exige timing/energia/DAC/firmware/união/ERC/footprints,PCB/DRC e
protótipo; nada disso é antecipado como aprovado aqui.
