# NET-25 — drenagem experimental, falhas ainda abertas

26/11/2026. Base publicada `5a871ff3ddc58986ae1fb7998690bb9ec3711d5b`.
**Experimento não promovido e placa não liberada.**

As folhas separadas `hardware/phase_drain_video` e `hardware/phase_drain_reset`
partem dos JSON nativos anteriores. Vídeo72componentes/36CIs/590pinos/33NC;
reset26componentes/144pinos/7NC, sete CIs digitais, um supervisor e dois módulos
osciladores configurados. Nenhum código de compra de oscilador foi homologado.

Warm U8 muda para AHC164 de14pinos e quatro estágios/Q3. Recebe SAFE em série
e clearRC independente. U9 mantém clearVDD e recebe NOR&PHASE_RUN. LOCAL_RESET_N
é SAFE&PHASE_RUN. Porta OR livre forma BANK_ARM=READY|BANK_SYNC1; alimenta D0
do primeiro FF de armamento dos bancos. É sticky até clearRC, sem dependência
circular do reset dos bancos para o warm. Backend continua OR(P1,P2) registrado.
CPU/ISA/X/SP/flags/microcódigo e demais blocos permanecem iguais.

## Resultados separados por escopo

- KiCad10.0.8 exportou e conferiu todos os pinos sem divergência. ERC parcial:
  vídeo49 violações(2power+13input+34isolated); reset14(2+2+10). Sem waivers.
  PDFs/previews foram vistos. Não é ERC da placa global.
-16 contratos e cargas conjuntas conferidos: MASTER3CLK/40pF; clearRC3/40pF;
  BANK_SYNC1 duas/30pF; ARM uma/20pF; PHASE_RUN duas/30pF; LOCAL quatro/50pF.
  Ci10pF máximo a5V mais trilhas10pF é orçamento condicional, não extraçãoPCB.
- Modelo warm:18 calibrações, nove positivas e nove rejeições esperadas.
  Default estrito conserva setup4,5ns/hold0,5ns/recovery2,5ns/pulsos5ns/95MHz.
  Projeção marcada só no warm trata aberturas de dados/clear por duas escolhas
  binárias. Hold usa captura antiga. Isso não esgota resoluções analógicas,
  não simula metastabilidade nem garante duração/MTBF.
-32 cortes selecionados de pulso passaram com guardas originais: dois perfis,
  duas políticas e oito offsets, incluindo os quatro antes rejeitados.
  Phase/warm CLK são monitorados mesmo enquanto RAW baixo. Outros atrasos
  seguem fixos; não é todoPVT/skew/jitter/slew elétrico.
-6.886 casos de instruções ideais:13.406 transações,569.801 verificaçõesWAIT,
  zero falhas e nenhum abort de memória. Fixtures semeiam estado só nesse
  ensaio; não representam SRAM inicializada fisicamente.
- Quatro cortes de escrita da CPU(duas políticas/offsets0 e40ns) com scans de
  reinício completos passaram. SRAM conserva o mesmo epoch durante a falha,
  sem rollback/seed; WE físico inibido em84ns no cenário selecionado.

Os dois cenários temporizados concluíram1.062 instruções/1.821 transações
cada, sem falhas; atrasos padrão e antecipado do controlador. Setup observado
54,888/36,944/46,944ns no cenário padrão. As contagens warm de aberturas são
eventos da projeção binária, não aprovações analógicas.

O novo boot/quadro ideal concluiu132.197 instruções/232.576 transações e
76.800pixels idênticos à referência, SRAM inicialmente desconhecida e
FIXTURE_DEFAULTS=0. Períodos/startup são escalados explicitamente nessa
regressão lógica. Programa inteiro temporizado não foi executado.
Esses resultados pertencem à variante experimental, não à hipóteseP1.

## Falhas reproduzidas — não aprovações

1. Estado inicial binário4: guardas HC74 rejeitam pulso7,722ns/20ns enquanto
   CLR0 conhecido. Resultado estrito em `development/strict-cold-clock`.
   `package_models_cold_diagnostic.sv` apenas permite observar contenção sob
   reset conhecido e registra cada OPEN_RESET_CLOCK. Preserva fatal se CLR
   alto/indefinido, demais predicados intactos. Essa projeção NÃO fecha a
   restrição física de clock frio e não é usada nos32 cortes estritos/CPU.
2. RAW baixo50ns no offset39ns: a varredura estendida rejeita recovery em
   U36_1. SAFE retorna antes de PHASE_RUN cair, liberando reset local perto de
   P3. O coletor para na primeira falha;54casos concluídos não são156casos
   aprovados. Registro final `drain-startup.json` tem uma falha explícita.
3. Um estímulo inicial RAW baixo só12ns não partiu, pois não fornece asserção
   válida para RC/supervisor. Resultado/watchdog e estímulo preservados em
   `development/short-initial-raw`. Partidas funcionais seguintes usam60us ou
   12ms de RAW baixo. Não há aprovação de POR para pulsos arbitrários.

## Hipótese seguinte, apenas em HDL

`local-sync-hypothesis.json` acrescenta duas etapas AHC74 emP1 para reset local,
clear SAFE, D0=1/D1=Q0 e Q1=LOCAL_RESET_N. Passaram156 cenários funcionais:
68partidas(16padrões baixos+X, duas liberações, duas políticas),84glitches
(sete offsets/seis larguras/duas políticas) e quatro pausas de MASTER alto/
baixo alinhadas a bordas. Usa a mesma projeção de clock frio sob CLR0 e deixa
esse requisito aberto. **Não há esquema nativo dessa hipótese.** Um pacote
adicional aumentaria vídeo para37CIs; não é a contagem da NET25 construída.

Uma segunda hipótese apenasHDL combina a dupla local emP1 após uma AND8,5ns
e o controlador ligado diretamente ao backend, conservando apenas seus
buffers de folha. Passaram os mesmos156 cenários com o monitor de clock
**estrito original**, sem exceção sob CLR0. Dois negativos reintroduzem uma
mudança por vez e reproduzem o pulso7,722ns ou recovery de U36_1. Isso ainda
não é variante nativa nem teste de teclado/SRAM/CPU integrado. O teclado não
está nessa sonda: U1HC174 também recebe backend e exige tratamento próprio.
Ver `direct-backend-hypothesis.json` e `direct-backend-negative.json`.

A próxima etapa deve construir a liberação local e investigar distribuição
de clock com Q/QB e uma porta por ramo. Ver [estudo não implementado](CLOCK_TREE_STUDY.md).
Não relaxar monitores para aceitar clock ativo curto. Repetir partidas/glitches,
pausas/reset/SRAM/CPU/teclado, quadros e programa, com fontes congeladas.

## Origem e limitações de ensaio

`build_phase_drain.py` lê JSON/definições sem modificar predecessores. Os
adaptadores distinguem netlist nativa estrita, projeção warm e sondas de atrasos.
Desenvolvimento preserva: calibração sem pulso explícito de clear corrigida
no estímulo; duas falhas de compilação por nomes antigos de contadores U8_0/1;
primeira rodada com metadados do adaptador alterados durante execução(rodada
final repetida com fontes congeladas); checks de clock inicialmente ligados a
RAW, depois mantidos sempre ativos no warm/phase; partida curta e clock frio;
hipótese com checks indevidos durante seed antes da qualificação de potência.
Esses registros não entram como aprovações da variante final.

Fontes, comandos, ferramentas, hashes e saídas estão em `verification/net25`.
O consumo do novo shift não é fechado; CPD típico não é limite de corrente.
Supervisão/VDDinválido/POR, cargas/trilhas/jitter/MTBF/PVT, programa completo
temporizado, energia/USB-C/consumo, DAC/firmware, união/ERC/footprints/PCB/DRC
e protótipo continuam com seus critérios próprios. `diagnostic.asm` histórico
permanece ausente e sua falha conhecida não foi suprimida.
