# NET-30 — redistribuição com canais livres

26/11/2026. Base `b5a19c7ee72a9b8543060e77f9c26824daf271ca`.
**Variante nativa em validação; ainda não substitui o candidato NET26.**

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

## Checkpoint de testes

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
- Quadros temporizados e boot ideal completo continuam em validação.
  A primeira bancada de quadros aplicou só1us de reset frio e expirou:
  diagnóstico mostrou fases/armamento/banco indefinidos, sem SAFE. A RC
  exige asserção além de19us para essa inicialização. Fontes/logs preservados
  em development/frames-short-reset; nova tentativa começa RAW baixo por50us,
  sem mudar hardware, watchdog90ms ou monitores. Não é POR analógico aprovado.
  Só relatórios finais completos permitem aceitar esses itens.
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
há ERC aprovado. PDFs/previews foram inspecionados. Rótulos de revisão/data
nos quadros de título de vídeo/teclado ainda herdaram NET26/25-11; os nomes
dos arquivos, JSONs e hashes identificam esta variante NET30. Corrigir esses
metadados depois das fontes congeladas, sem regenerar modelos no meio dos
ensaios. Memória tem marcador NET-30B. Nenhum arquivo é pacote de fabricação.

Os buffers acrescentam atraso de dados e atividade/corrente dinâmica, mesmo
sem CIs extras. O modelo usa atraso selecionado10ns nesses canais; mínimos,
hold, assimetria, glitches/skew de decodificação, slew/jitter, capacitâncias
reais, alimentação/POR e MTBF continuam abertos. Ci10pF+10pF de trilhas é
orçamento de triagem, não garantia em todoVDD ou extração da placa.

Para promover o candidato: terminar/verificar as regressões próprias,
conferir fontes congeladas e preservar todos os resultados negativos e
limites. Produção também exige energia/DAC/firmware/união/ERC/footprints,
PCB/DRC e protótipo; nada disso é antecipado como aprovado aqui.
