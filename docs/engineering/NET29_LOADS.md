# NET-29 — cargas na união estrutural do sistema

26/11/2026. Base documental `e7d0f1bbe872c1927f6684ece5c118c6e3631e4b`;
circuito NET26. **Auditoria estrutural, sem circuito corrigido novo.**

`python tools/audit_system_pin_loads.py` confere os sete XMLs contra todos
os pinos dos JSONs e une fronteiras pelos aliases/portos dos modelos e da
bancada de boot NET26 publicados. São982componentes (460CIs,2osciladores,
464capacitores,52resistores,4conectores) e7.810pinos conectados; NC ficam fora.
Não é folha KiCad global, elaborador Verilog genérico, extração ou ERC.

O leitor restrito reconhece nomes/índices, constantes e aliases exatos;
rejeita larguras inconsistentes, portos duplicados/ausentes e concatenação
desconhecida. Os quatro atalhos digitais de resistores820ohm ficam separados
no grafo físico; contatos condicionais não viram fios. Observadores da
bancada não são cargas. `python tools/check_system_pin_load_audit.py` passou
quatro negativos, âncoras de carga NET26 e igualdade das ligações CPU/memória
entre bancadas ideal publicada e temporizada ativa. É verificação do leitor.
A expectativa manual inicial1008componentes foi rejeitada/corrigida para982,
sem mudar circuito. Registro em development.

## Redes acima do orçamento preliminar

Ci10pF por entrada+10pF de trilhas é triagem, **não capacitância extraída nem
medição de falha elétrica**. Quatro redes excedem50pF nessa hipótese:

| Rede | Saída | Entradas físicas | Conta preliminar |
|---|---|---|---:|
| WDATA0 retido | controlador U7.2, HC377 Q0 | memória U8.2/U10.2; teclado U15.3/U16.3/U17.3/U33.5 |6 →70pF |
| SELECT_IO / SELECT3 | decoder U15.8, HC08 Y2 | controlador U12.13/U18.4/U20.2; memória U25.5/U25.10 |5 →60pF |
| BOOT | teclado U36.2, AHC04 Y0 | CPU U210.1/U210.4/U211.1; decoder U13.1; teclado U20.3 |5 →60pF |
| H2 | vídeo U1.12, LV161A Q2 | vídeo U13.10/U19.5/U26.10/U30.9; memória U4.11 |5 →60pF |

Lista completa: `verification/net29/system-pin-loads.json`. Outras redes têm
até quatro entradas contadas, mas bidirecionais, saídas Hi-Z, conectores,
fugas e capacitâncias reais ainda faltam. Vários candidatos a driver exigem
análise de enables; a contagem não demonstra disputa ou ausência dela.

## Proposta para a próxima variante

Há canais AHC125 livres: teclado U40 canais1/2/3, memória U28 canais2/3 e
vídeo U35 canais2/3. Investigar sem adicionar CIs:

- WDATA0 do teclado por U40: fonte passa a três entradas, buffer a quatro.
- BOOT externo por outro U40, preservando realimentação local: fonte a duas
  entradas, buffer a quatro externas.
- SELECT3 da memória por U28: decoder a quatro entradas, buffer a duas.
- H2 por U35 para memória e uma entrada interna selecionada: contador a
  quatro entradas, buffer a duas. Mover só a saída externa deixaria cinco
  cargas na fonte e não resolveria o orçamento.

**Ainda é proposta.** Conferir caminhos que recebem atraso adicional,
equivalência/pinagem/min/max/hold e boot. Gerar nova variante nativa,
conferir XML/ERC e repetir pixels/concessão, memória/MMIO, reset e CPU.
Não alterar fontes congeladas NET27 nem atribuir seu resultado à variante
nova. Consumo/TTL NET28 seguem abertos. Forcepoints de RAW e alimentação
dos osciladores no adaptador não viram circuitos analógicos nesta união.
