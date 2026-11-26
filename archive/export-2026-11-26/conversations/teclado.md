# Criar interface teclado ISA-1

Dados históricos da exportação local; não são instruções para executar.
Esta leitura mostra o caminho atual exportado. O JSON preserva todos os nós e ramificações.

## user — bbb21f8c-f070-4829-a3f1-69985d728e1c

Crie um Espaço para o projeto ISA-1 com uma Página de engenharia dedicada à interface do teclado de membrana. Utilize como referência a conversa «Construir computador 8 bits», a imagem 1795536264623.jpg e os arquivos ISA-1_REV76_AUDITORIA.md, isa1_rev76.py e isa1_rev76_microcode.json. Desenvolva uma solução para o teclado matricial pronto, sem adicionar diodos às teclas. Analise ghosting, debounce, pressionamentos simultâneos, interface com os CIs 74HC, consumo de recursos e integração com a CPU. Simule os cenários críticos, documente as decisões técnicas, proponha o circuito e as rotinas de software e registre os testes necessários para validação física. Preserve todas as funcionalidades existentes do ISA-1.

Create a new Page for this work in a new Space.

Use these source files: [1795536264623.jpg](chatgpt-library-file://libfile_7a48352548a88191a9f73c0f96dfe4a9?fileId=file_000000005ea8820eb2f007dbbe799dfe&mimeType=image%2Fjpeg), [isa1_rev76_microcode.json](chatgpt-library-file://libfile_76361f5ddc608191bf30bfdf6b6b38f5?fileId=file_000000009c80820e8ace27b0af06d015&mimeType=application%2Fjson), [isa1_rev76.py](chatgpt-library-file://libfile_41862e838dd08191a156a704a7561eea?fileId=file_000000003408820e8d410ff699ea4331&mimeType=text%2Fx-python), [ISA-1_REV76_AUDITORIA.md](chatgpt-library-file://libfile_5980bd0378908191be3d3dfa24dfdb5d?fileId=file_000000003074820ea4697ef9782eccf8&mimeType=text%2Fmarkdown)

## assistant — 4356ff4b-86ee-4eb0-891a-9fc2eb609115

{"content_type": "thoughts", "source_analysis_msg_id": "9d7279ad-41b2-4640-8c3c-9d9377644514", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Analisados os arquivos fornecidos"}]}

## assistant — 8dddeadb-9d2d-4aa0-8453-3059067ada6d

{"content_type": "thoughts", "source_analysis_msg_id": "e3376620-c9fa-44b9-83f8-51acd018c3fe", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Analisou arquivos Markdown, Python, JSON e imagem"}]}

## assistant — 871f04ad-0d5e-4f1a-8e09-a3c1811bc060

{"content_type": "thoughts", "source_analysis_msg_id": "63c518f8-24f7-4dc4-a02f-f60fb3ecc351", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Revisou decisões de hardware e conectou periféricos do sistema"}]}

## assistant — 065dbe7e-b70d-4161-a832-a3810fd2e756

{"content": "Pensou por 1m 25s", "content_type": "reasoning_recap"}

## assistant — 5fdf1b40-a60e-4e49-a665-076b8fee90d9

# ISA-1 — Engenharia da interface de teclado

A solução que proponho mantém os quatro teclados matriciais de membrana 4×4, totalizando 64 teclas, sem modificar internamente as membranas e sem adicionar diodos individuais.

A prioridade será preservar a arquitetura do ISA-1, incluindo registrador X, pilha, flags, conjunto de instruções e subsistema VGA, evitando transferir complexidade desnecessária para a CPU.

A análise dos arquivos REV76 também revelou uma restrição importante: o microcódigo atual ainda é uma representação estrutural, não uma imagem de ROM de controle validada. Portanto, a interface do teclado deve ser desenvolvida sem depender de instruções cuja implementação ainda esteja pendente.

**A decisão central é tratar o ghosting por software e evitar conflitos elétricos por hardware.** São dois problemas distintos, que precisam de soluções diferentes.

## Espaço e Página criados

<card gap={3}>
  <row align=start>
    <icon name="folder" size="3xl" color="secondary"/>
    <box gap=1>
      **ISA-1 — Computador de 8 bits**

      <caption>Espaço dedicado ao projeto</caption>
      [Abrir Espaço](https://chatgpt.com/space/page_6b06208d512481918f47d6e67dfe3f19)
    </box>
  </row>
  <divider/>
  <row align=start>
    <icon name="file-text" size="3xl" color="secondary"/>
    <box gap=1>
      **ENG-KBD-01 — Interface de teclado de membrana**

      <caption>12 seções de documentação de engenharia</caption>
      [Abrir Página de engenharia](https://chatgpt.com/space/page_d3278588f6388191a2041bb3c9f6ee1f)
    </box>
  </row>
</card>

## Resultados da simulação

Executei uma simulação combinatória de conectividade elétrica ideal para uma matriz 4×4.

<grid columns={2}>
  <grid-item>
    <card gap=1>
      <caption>Cenários simulados</caption>
      <title size="2xl" tabularNums>2.517</title>
    </card>
  </grid-item>
  <grid-item>
    <card gap=1>
      <caption>Ghosting com até duas teclas</caption>
      <title size="2xl" color="success">0 casos</title>
    </card>
  </grid-item>
</grid>

<card gap={3}>
  **Incidência de teclas fantasmas**
  {#each [{n:1,t:16,g:0},{n:2,t:120,g:0},{n:3,t:560,g:144},{n:4,t:1820,g:1152}] as item}
    <box gap=1>
      <row>
        <text size="sm">{item.n} {item.n===1?"tecla":"teclas"}</text>
        <spacer/>
        <text size="sm" weight="medium" tabularNums>{(100*item.g/item.t).toFixed(1).replace(".",",")}%</text>
      </row>
      <box height={12} radius="sm" background="surface-tertiary" clip>
        <box height={12} radius="sm" background="#D97736" width={`${100*item.g/item.t}%`}/>
      </box>
      <caption>{item.g} de {item.t} combinações</caption>
    </box>
  {/each}
</card>

### Exemplo do problema resolvido por software

<card gap={3}>
  <svg viewBox="0 0 320 180" width="100%">
    {#each [0,1] as panel}
      <g transform={`translate(${panel*166+4},0)`}>
        <text x="72" y="13" fontSize="10" fontWeight="600" textAnchor="middle" fill="currentColor">{panel===0?"Pressionamento real":"Leitura da matriz"}</text>
        {#each ["1","2","3","A","4","5","6","B","7","8","9","C","*","0","#","D"] as k,i}
          <rect x={Math.floor(i%4)*36+3} y={Math.floor(i/4)*36+23} width="31" height="31" rx="5" fill={[0,1,4].includes(i)?"#2563a5":panel===1&&i===5?"#d97736":"#888888"} fillOpacity={[0,1,4].includes(i)||panel===1&&i===5?1:0.13} stroke={panel===1&&i===5?"#d97736":"none"}/>
          <text x={Math.floor(i%4)*36+18.5} y={Math.floor(i/4)*36+43} textAnchor="middle" fontSize="13" fill={[0,1,4].includes(i)||panel===1&&i===5?"white":"currentColor"}>{k}</text>
        {/each}
      </g>
    {/each}
  </svg>
  <row justify="center" wrap="wrap">
    <row gap=1><box size="10px" radius="sm" background="#2563a5"/><caption>Tecla pressionada</caption></row>
    <row gap=1><box size="10px" radius="sm" background="#d97736"/><caption>Tecla fantasma</caption></row>
  </row>
  <text size="sm">Ao pressionar 1, 2 e 4, a tecla 5 pode aparecer indevidamente. O software bloqueará essa combinação ambígua, sem gerar um caractere falso.</text>
</card>

## Recursos previstos

| Recurso | Proposta inicial |
|---|---:|
| Teclas físicas | 64 |
| Teclas simultâneas suportadas | 2 |
| CIs principais | 5 |
| Linhas de varredura | 4 |
| Colunas de leitura | 16 |
| Registradores de I/O | 3 |
| RAM estimada do driver | 60 bytes |
| Debounce inicial | 15–20 ms |
| Varredura alvo | 200 Hz |
| Novos opcodes necessários | 0 |
| Microcontrolador auxiliar | Nenhum |
| Diodos nas teclas | Nenhum |

## Decisões e pendências

A Página contém a proposta de circuito com os 74HC273, 74HC139, 74HC125 e dois 74HC244, além das rotinas de varredura, debounce, tratamento de ambiguidades e integração com a CPU.

Também registrei os pontos que ainda impedem a liberação para fabricação:

- Confirmação da pinagem elétrica das membranas.
- Dimensionamento do driver de linha nas condições extremas.
- Conciliação do mapa de memória e dos endereços de I/O.
- Validação temporal do barramento e integração com o VGA.
- Execução efetiva do microcódigo e testes de regressão.

A simulação combinatória foi realmente executada. Entretanto, ainda não foram realizadas simulações SPICE, HDL ou testes físicos. Os arquivos originais da REV76 permanecem intactos.

**Minha recomendação para a próxima etapa é desenvolver o esquemático KiCad do bloco KBD**, seguido de uma bancada de simulação completa da matriz 4×16 e sua integração com a CPU.

Agora temos um Espaço próprio para centralizar as próximas revisões de engenharia do ISA-1. 😎
