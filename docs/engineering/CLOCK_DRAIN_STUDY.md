# Estudo de parada do relógio — proposta não implementada

26/11/2026. Base publicada NET23 `c54226afed52e04c787b91c65dc29cfacf8f661e`.
Análise para ensaiar depois do agrupamento de pedidos NET24. Não é revisão
de circuito concluída nem aprovação de temporização/produção.

## Fatos conferidos

O backend **já tem duty de 50% em regime**: U25 canal0 faz OR(P1,P2) em G_2,
amostrado por U11_0, sem clear assíncrono. Não parte diretamente de P0.
`verification/net24/topology.json` confere esses pinos e os dois buffers de
distribuição no reset mais um buffer no controlador. Sob as hipóteses
selecionadas, a largura em regime tem limite aritmético de47,44ns, acima dos
20ns do HC74 a4,5V/−40…85°C. Isso não é limite durante reset nem inclui jitter
ou trilhas extraídas.

O ensaio `run_reset_pulse_probe.py` já reproduziu a pendência no modelo:
quatro offsets30/39/40/60ns, com perfil assimétrico de CQ/buffers, produzem
7,722ns e são rejeitados pelo monitor HC74 de20ns. Oito cenários de atraso
simétrico e o perfil assimétrico em regime passam. Outros atrasos do antecessor
continuam fixos; isso não é medida em placa nem fechamento de todo PVT.

Interpretação a investigar: o clear assíncrono do shift de fases pode encerrar
uma sequência entre as duas fases do OR. Uma alta de apenas um período do
mestre, após dispersão de CQ e de subida/descida em três buffers, poderia
violar o mínimo do controlador antes do reset atrasado dos bancos. Conferir
a projeção digital com monitores originais, distinguindo efeitos
reais do modelo e eventos CQ pendentes na modelagem de clear. Não declarar
uma falha física a partir dessa hipótese.

## Alternativa para avaliar nos ensaios seguintes

Preservar a frequência e o OR(P1,P2), mas drenar o token de fases por entrada
serial síncrona em vez de apagar U9 assíncronamente durante RAW. Há dois AND
livres em U24 canais2/3; não é necessário acrescentar pacote para eles.

Uma proposta mantém o total de CIs e troca U8 AHC74 por AHC164 de14pinos
(pinagem precisa ser refeita e conferida):

- U8 recebe SAFE na entrada serial e usa Q3 como PHASE_RUN, quatro estágios de
  sincronização internos e apenas um pino de clock. Não é um modelo analógico
  de metastabilidade; seria necessário marcar/calibrar só a fronteira de dados
  e a recuperação de clear, mantendo os outros requisitos do CI.
- Clear de U8 recebe **DELAY_CLEAR_N**, Schmitt do RC no reset, independente
  das bordas de backend. Não usar BANK_RESET_N: isso poderia impedir o backend
  de partir e criar dependência circular. Exportar e orçar a ligação real.
- U9 mantém CLR em VDD. Uma AND forma PHASE_SHIFT_IN = PHASE_SERIAL & PHASE_RUN.
  Outra forma LOCAL_RESET_N = SAFE & PHASE_RUN, conservando a asserção rápida
  de reset dos contadores/saídas sem apagar o token em trânsito.
- U8 CLR já estará baixo antes do clock numa partida válida. Ao ser liberado,
  quatro bordas de zero em U9 tornam todos os quatro bits conhecidos; na quinta,
  o NOR injeta o primeiro token. Três zeros bastariam para o NOR, mas quatro
  evitam liberar o clear local perto de um possível P3 inicial em uma partida
  binária arbitrária. Conferir recovery/removal de READY/contadores e todas as
  alternativas de potência, inclusive RAW liberado antes do oscilador começar.
- Durante falha com MASTER funcionando, o serial de U8 amostra SAFE baixo e
  PHASE_RUN cai em poucas bordas, muito antes da asserção RC mínima de1us.
  O clear atrasado de U8 então reafirma zero. Com MASTER parado, comprovar que
  sua retomada não cria pulso curto nem escrita antes de rearmar os bancos.
- Um token válido deve terminar P1/P2 antes da parada, deixando backend baixo.
  Glitches curtos de RAW, duas políticas binárias nas fronteiras e retomada
  antes de drenar completamente exigem ensaios explícitos.

Na partida física, U9 pode começar em qualquer padrão binário. Antes de a
sequência ficar conhecida, não permitir que duas bordas preliminares de
backend já liberem os bancos. Uma proposta complementar reaproveita OR livre
de U27 para BANK_ARM = CAPTURE_READY | BANK_SYNC1 e usa BANK_ARM em D0 de U3
do reset. Exportar BANK_SYNC1 para o vídeo e BANK_ARM para o reset, mantendo
o mesmo total de CIs. Isso exige pinos e novos limites explícitos, não apenas
um adaptador simbólico.

CAPTURE_READY só deve subir depois de um P3 válido e da liberação do clear
local. BANK_SYNC1 então mantém BANK_ARM alto mesmo se RAW derrubar READY;
assim o reset dos bancos continua atrasado até o RC, preservando WE antes de
clear. Não usar READY diretamente em clear de U3: isso poderia apagar bancos
antes da inibição física de WE. Confirmar o feedback, transições durante
partida interrompida e eventuais aperturas de dados/clear, sem desabilitar
monitores indiscriminadamente. A nova sequência não pode depender de SRAM
inicializada nem de um estado binário de potência escolhido sem registrar a
hipótese e ensaiar as alternativas.

O clock MASTER comum passaria de quatro para três pinos: U8 shift, U9 shift e
U11_0 backend. O novo PHASE_RUN teria dois consumidores; LOCAL_RESET_N da AND
alimentaria os quatro buffers existentes. São orçamentos a conferir por pinos,
não capacitâncias extraídas. Q3 de U8 e o gate serial precisam cumprir setup/
hold de U9 com extremos de CQ/gates e skew real.

## Critérios antes de adotar

Provar a necessidade e a solução nos pinos, sem relaxar guardas para aceitar
runt ativo. Distinguir pulsos durante inicialização com bancos resetados de
pulsos durante escrita ainda ativa. Preservar RAW rápido, payload retido até
WE alto, IRQ/MMIO/teclado, todas as26 instruções, SP/X/flags/VGA e COMMIT único.
Repetir partida/clock ausente/pausado, cortes nas fases e nos pinos SRAM,
quadros completos, CPU e boot integrado. Fontes/transformações/hashes, ERC,
novas hipóteses de fronteira e alternativas devem entrar em ADR antes de
promover a variante. POR/MTBF/PVT/forma elétrica continuam sujeitos a análise
e validação correspondentes.
