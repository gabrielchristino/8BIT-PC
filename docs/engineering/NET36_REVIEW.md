# NET36 — auditoria do boot temporizado e revisão da reserva H/V

27/11/2026. Base `2a7fbab2a34c678e15bdde94d1073e52818125d4`.
**NET27 aceita no escopo digital NET26; NET30 ainda ativa na coleta.
Nenhum circuito novo adotado ou projeto liberado para fabricação.**

## Resultado das execuções completas

`tools/audit_full_timed_attempts.py` só lê as tentativas e regenera a referência
em diretório temporário Linux. Não inicia simulador, altera entradas ou retoma
processo. A primeira coleta e a coleta final permanecem separadas em
`verification/net36/full-timed-audit*.json`, com identidade, limites e hashes.

NET27 `attempt-001` terminou com saída zero em 56.155,678 s de parede,
sem timeout: 132.197 instruções, 232.576 transações, 32.771 transações VRAM,
258.492 verificações WAIT e 17.395 observações de pausa. Foram 337 escritas
RAM e 32.770 escritas VRAM válidas, zero abortos e FIXTURE_DEFAULTS=0.
O quadro PPM tem 230.415 bytes e 76.800 pixels, exatamente iguais à referência
regenerada, SHA256 `152c217f59e4a6f05b8c75f8c17e66c1b4e01b5369e37b913f034e97d6903665`.

A bancada compara cada retirada e transação, todos os 32.768 bytes de VRAM,
um sentinela RAM, pixels e geometria. Não há dump exaustivo final da RAM.
Há 49 conferências de runners/snapshots/fontes congeladas por tentativa e
49 fontes do relatório final NET27 resolvidas. As três imagens de entrada
(estados, barramento, ROM) de cada tentativa coincidem com a regeneração.
Seis negativos adulteram contagem, pixel, aborto, término, aprovação e timeout;
todos são rejeitados. Nada foi alterado nas evidências para esses negativos.

CPU nominal 100 kHz, master nominal 25,175 MHz (meio período19,860973 ns),
startup10 ms e atrasos digitais selecionados. A impressão `video_half=20` é
arredondada; o auditor confere o parâmetro fonte. RESET_BOUNDARY registra zero
eventos warm nesta execução, mantendo hipótese binária explícita e nenhuma
aprovação de metastabilidade/MTBF/PVT/POR analógico. NET27 usa NET26: não
transferir este sucesso à redistribuição de cargas NET30 nem às NET33–35.

NET30 permanece no mesmo boot WSL/PID1656, comando e cwd esperados. Limites
reais do processo conferidos:1GiB,72000sCPU,8MiB/arquivo,sem core; watchdog
do executor24h. As entradas congeladas conferem. Não há RESULT, relatório
final ou comparação final de imagem nessa coleta; não está aprovada.
O progresso exato e a data UTC estão nos checkpoints, não são conclusão.

## Descarga H/V: hipótese que precisa ser revista

LT3042 Rev.C p19 descreve recuperação de sobretensão; p22 descreve até15mA
de drenagem nessa função, além do caminho pelo SET. Bloqueio reverso de IN
não elimina descarga para terra. Cerca de4mA é típico, não máximo. A ativação
depende de OUTS/SET/VIN: a soma a seguir é estresse condicional, não simulação
do comportamento real nem prova de que todos os caminhos conduzem juntos.

O ledger parcial de resistores/carga, com3,6V e sem queda favorável no driver,
chega a5,714481mA em estado ativo. Somando15mA e o caminho resistivo SET,
o estresse parcial chega a20,817148mA, antes de ICC/DeltaICC, comutação,
fugas e transientes. Não é máximo global garantido. No proxy47uF/50mohm/
20,1us, sobra somente0,890826mV acima3V. O orçamento10mA NET35 permanece
uma hipótese não demonstrada; não declarar defeito físico por essa soma.

O novo cálculo racional reproduz exatamente3,006057740V da NET35 sob10mA.
Para os mesmos47uF/50mohm/20,1us, a fronteira matemática é22,682129mA
para alcançar3V, sem margem. O caso25mA já cai abaixo3V.
Uma **proposta de requisito**, ainda sem peça/BOM ou esquema novo, é
25mA totais,150uF efetivos mínimos,50mohm máximos e20,1us máximos:
resulta3,006234336V. Para margem5mV seriam necessários109,612385uF nesse
mesmo modelo.150uF é reserva adicional, não capacitância nominal adotada.

Foram classificadas120 combinações C/I/t/ESR e cinco proxies ngspice:
três acima3V e dois abaixo, incluindo negativo25mA/47uF. Todos coincidem
com a equação de carga dentro da tolerância numérica. Proxies não contêm
modelos vendor do regulador ou supervisor. O caso150uF/25mA/50us fica
acima3V, mas não atende margem5mV; não confundir critérios.

## Critérios para a próxima revisão

Qualificar o tempo SENSE→RESET com pullup4,7k e carga real (tabelaTPS3808
usa100k/50pF), NAND/buffer e rampa; não herdar20,1us como garantia.
Fechar corrente integrada de descarga e dinâmica SET/OUTS em falha de IN,
passivos reais/temperatura/bias/frequência/envelhecimento/ESR/ESL e estabilidade
com o bulk. Avaliar isolamento da reserva ou outra arquitetura se necessário.
Maior bulk não resolve a margem superior4,2198mV, retomada, overshoot,
curto/clamp abrupto, receptor/proteção, partida ou POR.

6SEPC220M foi descartado nesta pesquisa por indicação NRFND;6SVPC220M
permanece apenas pesquisa: valores nominais não qualificam os requisitos.
Novo download LT3042 terminou em timeout; registro emreferences/net36,
sem PDF inventado. Leitura web primária, revisão/páginas e fontes locais
reutilizadas estão identificadas. Falhas/limitações da NET35 preservadas.

## Reprodução e continuidade

```
timeout 120 python3 tools/audit_full_timed_attempts.py --output verification/net36/full-timed-audit-final.json
timeout 180 python3 tools/check_sync_hold_up_review.py
python3 tools/record_net36_results.py
```

Python3.12.3/ngspice42 no UbuntuWSL; proxies limitados a256MiB/10sCPU/
20swall/2MiB por arquivo, cinco execuções. Icarus12.0 é a ferramenta do
resultado NET27 já encerrado. Nenhuma nova execução CPU/quadro foi feita
pela NET36. Fontes hardware/sim/firmware earchive/revisions não mudaram.
NET30 continua candidato digital460CIs+dois osciladores; energia global,
RGB/SLEEP/proteção, timing/CDC/cargas, firmware, esquema unido/ERC,
footprints/PCB/DRC e protótipo continuam abertos.

A primeira chamada verify_archive falhou por um cachePython preexistente de
26/11 emrev983, ausente dos ZIPs/Git. Seus6.124bytes/metadados foram
preservados emdevelopment, e somente esse artefato gerado foi retirado da
extração. A repetição passou159arquivos/55entradas ZIP. Fontes originais
intactas; primeira falha e transformação emdevelopment/archive-first-failure.json
e cache-quarantine.json. verify_recovered não foi repetido nesta mudança:
a ausência histórica diagnostic.asm continua sendo falha conhecida.
