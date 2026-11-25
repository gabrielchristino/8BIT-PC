# NET-10 — CPU unificada a partir dos pinos

25/11/2026, base NET-09 `5020e30394303971c4c0c1852a81d635365b4fee`. Trabalho novo em `hardware/cpu_global`; oito bancos anteriores preservados. A CPU principal usa X síncrono. A variante HC191 permanece nos snapshots anteriores, sem integrar esta árvore de fabricação candidata.

O esquema hierárquico reúne SP, transações, microcódigo, ALU, registradores, PC/endereço, execução e X. SAFE_CORE é a saída da porta física de execução, eliminando a expressão de reset do adaptador. Uma biblioteca local acompanha o projeto. O XML realmente exportado pelo KiCad é comparado pino a pino e convertido em modelo de portas, muxes, somadores, memórias de controle e flip-flops. Alias de observação não representam componentes nem cargas adicionais.

A união revelou cargas que não apareciam nas verificações isoladas: relógios, reset, alimentação válida, SP, B e sinais de controle. Foram acrescentados 17 HC125 e seus capacitores propostos. Resultado: 283 CIs, 283 capacitores, 566 componentes, 4.892 pinos e 150 NC. Cada sinal interno atende até quatro entradas após distribuição. Isso é contagem de entradas do grafo da CPU; não inclui trilhas, conectores, pontas de prova nem cargas dos periféricos futuros. Não comprova capacitância, integridade do sinal ou skew.

Reproduzir no Ubuntu WSL, a partir da raiz:

```text
python3 tools/build_cpu_global.py
python3 tools/convert_cpu_global.py
python3 tools/check_cpu_global_negative.py
python3 tools/run_cpu_global.py
python3 tools/run_cpu_global.py --timed
python3 tools/check_cpu_global_erc.py
python3 tools/record_net10_manifest.py
python3 tools/record_net10_manifest.py --check
```

O comando ERC retorna **5** enquanto houver violações; esse retorno não é aprovação. KiCad 10.0.8 foi instalado separadamente do KiCad 7.0.11. Procedência em `KICAD_ENVIRONMENT.md`.

Cada modo da regressão final cobre 6.886 casos das 26 instruções, 13.406 transações e 524.288 casos de guardas da pilha. O programa compara cada instrução e transação com a referência arquitetural: 132.197 instruções, 232.576 transações, 32.771 acessos de VRAM e quadro de 76.800 pixels. Os JSONs finais são a evidência de aprovação ou falha; não interpretar a existência de um relatório parcial como aprovação. Os negativos desconectam o clock do SP e ligam sua saída à alimentação, exigindo rejeição do conversor.

As duas regressões finais passaram, incluindo o programa e o quadro idêntico à referência. Segurança/reset: 3.780 casos no ideal e 3.602 com atrasos. A bancada escolhe os cortes pelo número de ciclos até RETIRED medido em cada cenário; a diferença não representa casos retirados para obter aprovação. O programa temporizado executou 5.314.951 verificações de WAIT e 46.105 ciclos de pausa. As dez folhas do PDF foram renderizadas e inspecionadas; isso complementa, sem substituir, a conferência de pinos/ERC.

No modo com atrasos, o relógio da CPU tem período de 10 µs e o estímulo de vídeo, 14 µs. Estes valores permitem exercitar a propagação selecionada da CPU; não são uma implementação do relógio VGA. O periférico `isa1_memory` continua um modelo comportamental. Os atrasos são limites selecionados das etapas anteriores, com monitores em parte dos registradores; faltam mínimos/máximos correlacionados, todos os caminhos, skew, capacitâncias e cantos elétricos. Não há frequência máxima certificada.

Reset/POWER_GOOD têm uma janela de resposta digital de 1 µs na bancada temporizada. A contagem de efeitos começa antes da afirmação de reset, para não ocultar escritas nessa janela. Isso não autoriza o circuito físico a escrever com alimentação insegura: o supervisor e a reserva de energia ainda precisam garantir que o bloqueio termine antes de a alimentação sair da faixa válida.

Falhas intermediárias preservadas: amostragem de reset antes da propagação; alias IR ausente na bancada de programa; parâmetros de clock não substituídos por causa de declaração conjunta; mensagem de negativo mais específica que a esperada. Cada arquivo identifica suas próprias fontes. Não são aceitação final nem defeitos silenciosamente removidos dos relatórios históricos.

ERC inicial: 1.244 violações. Correções de grade, biblioteca local e saídas internas NC reduziram para **56 violações atuais**: 40 etiquetas isoladas, 14 entradas externas sem driver e duas alimentações sem fonte. Não foram inseridas exceções para produzir zero. A CPU isolada ainda não contém os circuitos que encerram essas interfaces. O esquema/PDF são revisáveis; a placa completa continua bloqueada até memória, vídeo, teclado, alimentação, relógios, temporização, footprints, ERC/DRC e ensaios correspondentes.
