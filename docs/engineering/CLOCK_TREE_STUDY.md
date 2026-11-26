# Estudo de distribuição e reset local — ainda não implementado

26/11/2026. Base publicada NET24 `5a871ff3ddc58986ae1fb7998690bb9ec3711d5b`.
NET25 é experimento separado. Este documento não é circuito concluído.

## O que os ensaios já mostraram

A drenagem síncrona conserva pulsos durante os32 cortes selecionados com
políticas0/1. Entretanto, o padrão inicial binário4 produz pulso7,722ns no
monitor HC74 enquanto seu CLR está0. A rejeição estrita fica em
`verification/net25/development/strict-cold-clock` e não pode ser reclassificada
como aprovação. A projeção diagnóstica de partida apenas registra esses casos
como OPEN_RESET_CLOCK e exige reset conhecido; não fecha a restrição20ns.

Outro defeito, desta vez de recovery do vídeo ativo, ocorre com RAW baixo50ns
no offset39ns. SAFE retorna antes de PHASE_RUN cair e a AND local libera reset
assíncronamente perto de P3. `drain-startup.json` registra a falha em U36_1.

Uma hipótese apenas em HDL acrescentou um pacote AHC74: duas etapas de reset
local em P1, clear SAFE, primeiro D=1, segundo D=Qprimeiro, segundo Q=LOCAL_RESET_N.
Passaram156 cenários selecionados de partida, glitches e pausas alinhadas.
Eles ainda usam o diagnóstico OPEN_RESET_CLOCK na partida; não equivalem a
156 aprovações estritas de clock. A hipótese não tem esquema nativo próprio.

## Reset local para transformar em esquema

Manter warm AHC164 em quatro estágios, clear RC independente, serial SAFE e
Q3=PHASE_RUN; U9 serial NOR&PHASE_RUN e clearVDD. Repor U8 AHC74 para o reset
local, adicionar U37 AHC164 warm com desacoplamento C37. Alternativamente
conservar U8 warm e acrescentar outro AHC74, desde que a origem dos nomes seja
registrada. Vídeo passaria de36 para37CIs, sem mudança de CPU/ISA/SP/VGA.

Clock das duas etapas locais em P1 deixa aproximadamente dois períodos do
mestre antes de P3/captura e três antes do próximo P0 dos contadores. Não
usar Q0/Q3 do warm como AND local: a liberação pode coincidir com P3 quando se
variam CQ/gates. Não usar P3 ou CAPTURE_CLOCK para a nova dupla sem conferir
o pior recovery dos contadores P0; as janelas se aproximam demais.

Para compartilhar a nova dupla local e a dupla de armamento dos bancos,
uma AHC125 existente no reset pode receber P1 e dirigir os quatro CLK em um
mesmo PHASE1_CLOCK (40pF de entradas+10pF de trilha condicionais). Exportar
P1 do vídeo e PHASE1_CLOCK do reset. O P1 da AHC164 teria NOR, OR e a entrada
desse buffer: três cargas,40pF condicionais. Pinos/esquema/cargas precisam ser
checados; a hipótese HDL concluída usa P1 direto e não testa essa distribuição.

## Eliminar o pulso curto de partida por distribuição

**Alternativa menor para ensaiar primeiro:** o CLK de entrada do controlador
tem três entradas AHC125. Ligar essas três diretamente ao BACKEND, mantendo
o quarto consumidor como U8.A0 do reset(BACKEND_ROOT), daria quatro cargas,
50pF condicionais. Desabilitar o antigo canal U8.1 do reset que dirigia
ACCESS_CLK e fazer esse porto ser alias da rede BACKEND no adaptador/pinos.
Assim os HC74/HC377/HCT377 do controlador ficam após uma única porta.
**Atenção ao teclado:** sua U1 HC174 também recebe BUF_1_0, derivado do backend,
conforme JSON/pin9; IO_COMMIT autoriza os dados pelo mux, não é seu clock.
Portanto não basta corrigir só o controlador: o pulso frio7,722ns ainda
encontraria um receptor HC lento no teclado. Os156casos da hipótese direta
não instanciam teclado e não aprovam esse caminho.

Uma opção menor que Q/QB seria trocar essa U1 HC174 por AHC174, mesma pinagem/
função, família já usada no controlador NET19. Conferir datasheet e adaptar
modelo real de CQ/setup/hold/recovery/pulso, sem relaxar monitor do HC antigo.
Isso mantém41CIs do teclado, frequência/polaridade e seu caminho de clocks.
Demais receptores de backend são LV161A/AHC574/AHC74. Exigir5ns apenas após
confirmar por peça/condição; HC174 antigo tem20ns. O novo hold AHC174 precisa
ser conferido contra mux AHCT157/caminhos reais, inclusive min-delay e clock
comum dos registradores. Reverter só a peça deve reproduzir falha no monitor
HC174 estrito. Não tratar a troca como aprovada sem regressões de MMIO/scan,
CPU/WAIT/COMMIT, boot e pinagem/cargas. Nenhuma troca foi construída ainda.

Para a dupla local, U24.3 fica livre quando deixa de fazer SAFE&PHASE_RUN.
Usar essa AND como buffer P1&VDD para os dois CLK do novo U37 AHC74, mantendo
U8 warm AHC164 e adicionando C37. P1 passaria a três entradas(NOR/OR/buffer),
40pF; o buffer da dupla teria dois CLK/30pF. Bancos podem continuar no clock
anterior: seus AHC74 têm requisito5ns e duas portas após backend. Não mover
seu domínio se essa alternativa menor satisfizer todas as verificações.

`run_direct_backend_hypothesis.py` está ensaiando essa conexão somente em HDL,
com todos os guardas originais e sem a exceção diagnóstica CLR0. Não há esquema
desse ajuste e não atribuir à NET25 os resultados futuros dessa hipótese.

Alternativa mais ampla, somente se necessária pelas cargas/temporização:
investigar uma única etapa de buffer após cada saída do FF de backend,
em vez das três atuais. Não basta ligar seis entradas na mesma saída:
o controlador tem três entradas125 e o teclado outras três.

O backend U11 tem QB0 físico atualmente livre. Uma proposta aproveita Q para
as três entradas de clock do controlador, e QB para três **inversores** do
teclado. A inversão restaura o mesmo sentido das bordas; não clockar o teclado
na borda oposta inadvertidamente. Cada saída do FF teria três cargas40pF,
incluindo orçamento de10pF de trilha. Q/QB devem ter CQ e polaridades próprios
no modelo; não supor QB sem atraso como prova temporal.

O teclado U39 AHC125 atual tem três canais de CLK e um de G_13. É possível
avaliar a troca para AHC04: três inversores de clock, mais **dois** inversores
para preservar a polaridade do quarto canal G_13→BUF_1_3, e um canal livre.
Isso conserva41CIs no teclado, mas aumenta o atraso daquele sinal em uma
porta; precisa regressões de scan/acomodação/RC e novo esquema/pinagem.
Não tratar uma troca de família ou inversão apenas em HDL como BOM validada.

Os buffers de clock intermediários do reset podem ficar desabilitados e seus
CLK de acesso/teclado virar aliases físicos das redes Q/QB para os respectivos
blocos. O canal que recebe P1 alimentaria a dupla de bancos e a dupla local.
O D0 dos bancos continua BANK_ARM=READY|BANK_SYNC1, preservando armamento
sticky/clear atrasado e a independência do warm. A dupla de bancos amostraria
P1, não backend; READY em P3 tem dois períodos até a próxima borda P1. Conferir
setup/hold e recuperação por pinos, inclusive partida interrompida.

Conta inicial a verificar em datasheets: um pulso de um período do mestre
39,72ns menos dispersão9,5ns de CQ e7,5ns de **uma** porta daria22,72ns,
maior que20ns mas com apenas2,72ns para jitter/trilhas. Os números das portas
precisam confirmação por peça/carga/temperatura; isso não é STA nem garantia
global. Preservar o ensaio que reintroduz três buffers e reproduz7,722ns.

Essa alternativa acrescentaria somente o pacote da dupla local (+1CI no
sistema), não osciladores/reguladores novos. Consumo máximo/dinâmico permanece
aberto; não atribuir uma corrente máxima a partir de CPD típico.

## Próximas verificações

Construir variante nativa separada, conferir XML/pinos/ERC/cargas conjuntas e
orçamento de pulsos/setup/hold/recovery. Repetir os156 cenários **com monitores
estritos originais**, varrer bordas rise/fall/Q/QB/clock compartilhado e manter
negativos. Depois integrar pinos SRAM, cortes da CPU, vetores ideais e
temporizados, teclado/scan, quadros e boot. Não promover NET25 porque testes
nominais passam: glitches e clock frio ainda têm falhas abertas.

Pesquisa de alternativa rápida: Nexperia74AHC/AHCT377 existe em datasheet,
mas várias versões constam EndOfLife no catálogo consultado. Não foi adotada:
[datasheet primário](https://assets.nexperia.com/documents/data-sheet/74AHC_AHCT377.pdf),
[catálogo do fabricante](https://www.nexperia.com/products/analog-logic-ics/logic/flip-flops-latches-registers-counters-dividers).
Latch LVC1G373 também foi somente pesquisa, sem implementação/BOM:
[fabricante](https://www.ti.com/product/SN74LVC1G373).
