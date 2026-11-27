# Testes, pendências e revisões do ISA-1

Atualizado em27/11/2026, após as regressões próprias da NET30.
**Placa não liberada para fabricação.** Esta lista mostra o estado corrente;
relatórios NET e versões Git preservam os estados anteriores. Não somar
ensaios sobrepostos nem transferir aprovação entre variantes diferentes.

## Folha experimental NET32

Tres DACs em folha KiCad separada: 24 componentes,126pinos,15NC conferidos.
Passaram1024codigos por canal,oito negativos de XML,12288avaliacoes
condicionais e tres varreduras de carga com corrente ideal. Sem modelo
analogico vendor, sem integracao ao raster NET30. RSET de diagnostico nao
atende ao branco final; ganho/calibracao,protecao,partida/niveis,H/V e cargas
continuam abertos. ERC65itens sem aprovacao e footprints nao atribuidos.
[Detalhes e limites NET32](NET32_DAC_LEAF.md). A contagem candidata NET30
continua460CIs; dois boots completos temporizados seguem pendentes.

## Estudo VGA NET31

Contrato candidato e proposta funcional separados: 256 cores, 16 cantos
condicionais e quadro sintetico de 76.800 pixels; quatro negativos de
guardas rejeitados. Nao ha circuito DAC nativo ou BOM adotada. Ganho,
compliance sem monitor, protecao, alimentacao/niveis, driver H/V,
calibracao/temperatura e integracao permanecem abertos. Ver
[NET31_DAC.md](NET31_DAC.md). Nao acrescentar esses numeros aos ensaios
nativos NET30 ou considerar os dois boots temporizados completos aprovados.

## Circuito candidato corrente

A [NET30](NET30.md) é o candidato digital para os próximos blocos: usa quatro
canais livres, passou vetores ideal/dois temporizados,48cortes SRAM, oito
cortes CPU, quatro cenários de quadros temporizados e boot ideal completo.
Programa completo temporizado próprio, cargas/timing global e placa continuam
pendentes. NET27 em execução usa o circuito anterior NET26.

CPU `cpu_global`, decoder `memory_decode`, controlador `common_request`,
barramento `load_distributed_bus`, vídeo `load_distributed_video`, teclado
`load_distributed_keyboard` e reset `local_phase_reset`: **460 CIs, dois módulos
ACH e 464 capacitores**, ainda em folhas separadas. Fonte, USB-C, isolação e
DAC não integram essa contagem.

NET25 permanece experimento não promovido. NET26 corrigiu as rejeições de
pulso frio/recovery nos cenários documentados. Elas não continuam como
defeitos demonstrados do circuito NET26; temporização global continua aberta.

## Evidências concluídas, com escopo

| Item | Evidência aceita | Limite da conclusão |
|---|---|---|
| CPU/ISA/WAIT/COMMIT | NET30: 6.886 casos ideais/13.406 transações; dois cenários temporizados de1.062casos/1.821transações | Vetores semeiam estado; não são boot completo ou todo PVT |
| Boot e quadro | NET30 ideal:132.197instruções/232.576transações/32.771VRAM/76.800pixels idênticos; quatro cenários adicionais de dois quadros temporizados cada | Boot sem seed de SRAM e com clocks escalados; ensaio de quadros sem CPU semeia VRAM/VB |
| Reset/clocks locais | NET26 histórico:156cenários/128combinações/três negativos; NET30 tem cortes e partidas dos ensaios próprios | Não recontar matriz NET26 como NET30; jitter/trilhas/slew/MTBF globais abertos |
| Cortes de escrita | NET30:48cortes SRAM, WE até94ns; oito cortes CPU/scans, WE até84ns | Cenários específicos, sem rollback; byte interrompido pode ficar desconhecido |
| Pilha/flags/X/microcódigo | SP vazio8000h, push emSP−1 e atualização após COMMIT; ROMs preservadas | Contagens antigas não são novas execuções NET26 |
| Memória/VGA/teclado por pinos | Esquemas KiCad e projeções por pinos nas regressões correspondentes | Modelo digital difere de simulação elétrica e ensaio físico |
| Executor longo | NET27: cinco testes reais de limites de processo e identificação vivo/encerrado | Verifica executor, não circuito; boot completo temporizado sem resultado final aceito |
| Consumo documental | NET28: 34 famílias/configurações, parcelas/condições dos PDFs e hashes | Soma de referências não é máximo da placa; orçamento aberto |

Evidências: [NET26](NET26.md), [plano NET27](NET27_PLAN.md) e
[consumo NET28](NET28_POWER.md). A execução NET27 grava estado em
`verification/net27/full-timed/attempt-NNN/run-state.json` e progresso em
`simulation.stdout.log`. Exigir relatório final íntegro, contagens, asserções,
quadro idêntico e `simulation_passed=true`. Processo vivo ou compilação zero
não bastam. Interrupção exige nova tentativa; não há checkpoint HDL.

## Trabalho restante

| Prioridade | Estado atual | Critério de fechamento |
|---|---|---|
| 1. Boot inteiro temporizado | NET27 usa NET26; runner NET30 próprio preparado, sem resultado final |132.197instruções, transações/quadro completos, sem erros/aborts e fontes verificadas no circuito atual |
| 2. Temporização global | Rejeições locais selecionadas corrigidas; pulsos22,72/7,72ns condicionais | Todos os caminhos min/max, muxes, setup/hold/recovery, skew/jitter, cargas extraídas, slew, PVT e CDC/MTBF |
| 3. Energia/consumo/POR | Ordem WE/bancos digital, TPS3808/Schmitt; trilho proposto5,392V com margens pequenas; ledger NET28 | Fonte/proteção reais, consumo por estado, partida/inrush, reverso, regulação/transientes/POR e térmica |
| 4. USB-C | Requisito5V, entrada ainda não fechada | CC/corrente anunciada, proteção/quedas e carga controlada da reserva; não presumir1,5A disponível |
| 5. VGA analógico | Raster/dados digitais disponíveis; DAC/conector pendentes | RGB em75ohm, níveis/correntes, sincronismos/latência, proteção, simulação e medidas |
| 6. Firmware de teclado | Raw scan na CPU; debounce/fila/cancelamento no host | Implementar na CPU; até duas teclas estáticas e ambiguidades conservadoras, sem diodos/NKRO |
| 7. Elétrica global | NET30 redistribui quatro redes NET29; união até quatro entradas contadas, não extração | Qualificar Ci/cargas reais, TTL/CMOS/Delta-ICC, memória/Hi-Z, ruído/overshoot, retorno e temperatura |
| 8. União/ERC | Folhas separadas; ERC parcial vídeo49/reset13/teclado27/memória172/controlador135, sem waivers | Unir pinos/alimentações/portas, resolver erros e justificar exceções; não somar ERCs parciais |
| 9. BOM/footprints | Famílias candidatas, código completo ACH aberto | Códigos reais, pinagens/encapsulamentos/faixas/cargas/consumo e footprints |
| 10. Firmware de produto | Diagnóstico novo e imagem EEPROM disponíveis | Boot/monitor definitivo, gravação e diagnóstico de bancada/produção |
| 11. PCB/DRC | Layout não concluído | Mecânica, desacoplamento, retorno, clock/memória/VGA, posicionamento/roteamento e DRC revisados |
| 12. Fabricação | Não liberada | Revisão de esquema/BOM/layout, Gerbers, furos e posições coerentes |
| 13. Protótipo | Nenhuma placa ensaiada | Boot/RAM/VRAM/VGA/membranas, consumo/energia/reset, margens/repetibilidade medidos; corrigir e repetir |

CVC não foi adotado; erros/testes unitários são pesquisa, não aprovação do
circuito. Fronteiras binárias de warm/reset não garantem duração analógica de
metastabilidade. SPICE de reserva/teclado é condicional; o modelo oficial
TPS63070 ainda não concluiu. 1,5A é hipótese de hold-up, não consumo calculado.

## Lacunas históricas e dados físicos

- `diagnostic.asm` original continua ausente; `verify_recovered.py` mantém a
  falha conhecida. Diagnóstico novo não substitui esse original.
- REV33/REV76 foram recuperadas e reproduzidas em26/11. Permanecem33 conteúdos
  sem bytes e72 IDs de origem ausentes. Ver [lacunas](../LACUNAS.md).
- Imagens são referência de pinagem das membranas; resistência/capacitância e
  bounce das quatro unidades não foram medidos. O usuário ainda não consegue
  medir; avançar com envelopes condicionais sem repetir a solicitação.

Critérios físicos: [PRODUCTION_GATES](PRODUCTION_GATES.md). Registrar comandos,
versões, entradas/hashes, falhas e limites. Congelar fontes de ensaios ativos;
trabalho independente usa variantes novas.
