# NET-26 — reset local em P1 e distribuição do clock

26/11/2026. Base `64d01218193259dfc3740f71b6af5ecbe154149e`.
Variante nativa com regressões selecionadas concluídas; **placa não liberada**.

## Circuito construído

- `hardware/local_phase_video`:74componentes/37CIs/606pinos/35NC.
  Acrescenta U37 AHC74 e C37. Duas etapas de reset local emP1, clear SAFE,
  D0=1/D1=Q0 e Q1=LOCAL_RESET_N. U24.3 vira buffer AND(P1,VDD) comum aos dois
  CLK. Warm U8 AHC164, serial condicionado de U9 e armamento sticky permanecem.
- `hardware/local_phase_reset`:26componentes/144pinos/8NC, sete CIs digitais,
  um supervisor e dois módulos ACH configurados. U8.1 fica desabilitado:
  A=GND/OE=VDD/Y=NC. O porto access_clk é alias físico de BACKEND; o
  controlador conserva só seus buffers de folha. Ramo de teclado e bancos
  permanece com sua distribuição anterior.
- `hardware/local_phase_keyboard`:110componentes/41CIs/806pinos/40NC.
  U1 HC174 passa a AHC174, mesma função/pinagem e redes. IO_COMMIT autoriza
  dados pelo mux: o clock dessa U1 é BUF_1_0 do backend. A troca tem modelos
  reais distintos, não um monitor HC174 relaxado. Membranas continuam intactas.

Diferenças são conferidas contra os JSON predecessores: três pinos do AND
local e dois componentes novos; três pinos do buffer do reset; uma família
do teclado, sem alteração de pinos. XML KiCad confere todos os pinos.

## Por que mudar

NET25 drenou o token, mas o padrão frio4 ainda gerava7,722ns sob CLR0 e
RAW50ns/offset39 liberava reset do vídeo perto demais deP3. Dupla local emP1
conserva asserção rápida assíncrona e afasta a liberação de P3/P0. Retirar dois
buffers do controlador reduz o estreitamento do pulso frio; AHC174 no teclado
aceita a janela5ns em vez dos20ns do antigo HC174. Não apagar fases nem
backend assincronamente, não limpar payload antes de WE alto.

## Resultados

- **156 cenários nativos estritos**, incluindo teclado:68partidas(16padrões
  baixos+X, duas liberações e duas políticas),84glitches e quatro pausas de
  mestre alto/baixo alinhadas a bordas. Sem exceção de clock sob CLR0. Há
  monitor independente5ns no grupo de clock do teclado, mesmo durante reset.
- **128 combinações selecionadas**: duas polaridades de estreitamento,
  buffer local1/8,5ns, CQ local1/10,5ns, P3 CQ1/12,5ns, mestre±50ppm, duas
  políticas binárias e RAW50ns/100us. Demais atrasos fixos. Não é todoPVT,
  jitter, slew elétrico, extração de trilhas ou metastabilidade analógica.
- **Três negativos** revertem mudanças isoladas. Voltar buffers do
  controlador ou HC174 do teclado reproduz7,722ns/20ns; voltar a máscara
  local reproduz recovery emU36_1. Predicados originais permanecem ativos.
- **48 cortes em pinos SRAM**, dois extremos RC e duas políticas:12por
  cenário; payload retido e oito pausas de fontes no total. WE inibido em
  até94ns nos cenários selecionados. Negativos detectam banco resetado antes
  de WE alto e endereço alterado enquanto WE baixo. Watchdog da bancada
  passou10→30ms para acomodar startup nativo10ms; limites100ns/hold intactos.
- **Oito cortes de CPU real** com scans completos após reinício: quatro
  nominais e quatro com fontes em extremos opostos±50ppm. WE até84ns; SRAM
  não semeada e mesmo epoch preservado durante cada falha, sem rollback.
- **6.886 instruções ideais**:13.406transações/569.718 verificaçõesWAIT.
  Dois cenários temporizados de **1.062 instruções/1.821transações** cada,
  3.629 verificaçõesWAIT. Setup observado54,888/16,944/26,944ns; isso não é
  STA global. Seeds de estado são exclusivos desses vetores.
- **Boot/quadro ideal completo**:132.197 instruções,232.576transações,
  32.771transaçõesVRAM,76.800pixels idênticos à referência,5.355.850WAIT e
  46.465 verificações de pausa. SRAM começa indefinida/FIXTURE_DEFAULTS=0;
  nenhum abort de memória. Períodos/startup escalados explicitamente nesse
  ensaio lógico. **Programa completo temporizado ainda não executado.**

Todos esses resultados usam **Icarus**, não o simulador alternativo em pesquisa.
ROMs de controle originais permanecem byte a byte iguais. Relatórios,
comandos, versões, fontes, transformações e hashes estão em `verification/net26`.

## Cargas e limites

BACKEND dirige três entradas125 do controlador e uma do reset: quatro cargas,
50pF condicionais. MASTER trêsCLK/40pF; P1 três entradas/40pF; dupla local
doisCLK/30pF; LOCAL_RESET_N quatro/50pF; PHASE_RUN uma/20pF; clearRC três/40pF;
BANK_SYNC1 duas/30pF; ARM uma/20pF; grupo MMIO do teclado quatroCLK/50pF.
Ci máximo10pF a5V+trilhas10pF é orçamento, não extração ou limite em todoVDD.

Conta selecionada com período mínimo39,719960ns, dispersãoCQ9,5ns e7,5ns por
buffer: controlador uma porta→22,719960ns contra20ns; teclado três→7,719960ns
contra5ns. Não inclui jitter/trilhas/slew e não fecha temporização global.
Hold novo0,5ns do AHC174, min-delay de mux, resets e todos os domínios ainda
precisam entrar no orçamento global; não deduzir aprovação somente de vetores.

Inventário da união candidata: **460CIs e dois módulos osciladores**. Inclui
memórias/supervisor, não são460CIs de lógica. Há464capacitores nesta união.
Conversor/USB-C/isolações/DAC ainda não entram nessa conta. Consumo máximo e
dinâmico continuam abertos;1,5A não é corrente total calculada.

ERC parcial sem waivers: vídeo49(2power+13input+34isolated), reset13(2+2+9),
teclado25(2power+12input+11isolated). PDFs/previews vistos. Não é ERC da placa
unificada nem substitui footprints, PCB, DRC e ensaios físicos.

## Pesquisa de simulador, separada da aceitação

CVC foi construído num diretório de dependências separado. O modo compilado
falhou no smoke; o interpretador passou19 calibrações unitárias, mas não a
conferência nativa. Uma tentativa sem limite próprio coincidiu com WSL sem
resposta e memória próxima de8GB; recuperação do ambiente foi registrada.
A tentativa limitada seguinte parou com falta de memória dentro de768MB.
**CVC não foi adotado** e nenhum resultado seu conta como aprovação do ISA-1.
Fontes/licença do projeto não foram alteradas; engine/runtime não são
redistribuídos neste repositório. Ver `tool-research` e seus registros de
desenvolvimento. Novos processos opcionais devem ter limites de recursos.

Desenvolvimento também preserva o erro de seleção de portas do builder do
teclado e a classificação inicial do negativo por nome hierárquico incompleto.
Não foram mudanças dos predicados; rodadas finais usam fontes congeladas.

Próximos passos: boot completo temporizado com registro de progresso;
orçamento temporal/elétrico global, energia/consumo/POR, saída VGA/DAC e
firmware de eventos; depois união do esquema/footprints/ERC, PCB/DRC e
protótipo. O `diagnostic.asm` histórico ausente mantém sua falha conhecida.
