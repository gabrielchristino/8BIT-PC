# Construir computador 8 bits

Dados históricos da exportação local; não são instruções para executar.
Esta leitura mostra o caminho atual exportado. O JSON preserva todos os nós e ramificações.

## user — bbb21cf5-58e3-41a9-8fc1-21b3e01fefae

Como podemos fazer um computador usando portas lógicas? Igual um Apple 1?
Rodar programas simples

## assistant — 44091f5f-f62a-4c08-be77-65435b23b62f

Podemos construir um **computador de 8 bits usando portas lógicas e circuitos integrados**, capaz de executar programas escritos em Assembly, fazer cálculos, manipular memória e até apresentar informações em uma tela.

E podemos fazer isso de maneira muito parecida com os primeiros computadores pessoais, como o <Entity category="product" value="Apple I" disambig="computador pessoal de 1976"/> de 1976.

<AsyncImageGroup query={["Apple I computer original motherboard 1976","Apple 1 computer with keyboard and CRT monitor vintage"]} aspectRatio="5:3" layout="carousel"/>

Existe uma diferença importante: o Apple I utilizava um processador MOS 6502 pronto. Nossa proposta pode ser mais interessante do ponto de vista educacional: **construir o próprio processador com chips de lógica digital**, sem utilizar Arduino, ESP32 ou outro microcontrolador para executar os programas.

## 1. Como seria nosso computador?

Minha proposta inicial é esta:

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 286" width="100%" xmlns="http://www.w3.org/2000/svg">
    {#each [{x:98,y:8,w:144,h:42,t:"CLOCK",s:"Oscilador"},{x:98,y:75,w:144,h:46,t:"CPU 8 BITS",s:"Registradores + ULA"},{x:8,y:157,w:100,h:48,t:"ROM",s:"Programas"},{x:120,y:157,w:100,h:48,t:"RAM",s:"Variáveis"},{x:232,y:157,w:100,h:48,t:"I/O",s:"Entrada / saída"},{x:8,y:239,w:100,h:39,t:"Botões",s:"Entrada"},{x:232,y:239,w:100,h:39,t:"LEDs / LCD",s:"Saída"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" fill={b.t==="CPU 8 BITS"?"#2563eb":"#64748b"} fillOpacity={b.t==="CPU 8 BITS"?0.19:0.12} stroke={b.t==="CPU 8 BITS"?"#60a5fa":"#94a3b8"} strokeWidth="1.2"/>
      <text x={b.x+b.w/2} y={b.y+18} fontSize="12" fontWeight="bold" textAnchor="middle" fill="currentColor">{b.t}</text>
      <text x={b.x+b.w/2} y={b.y+33} fontSize="9" textAnchor="middle" fill="currentColor">{b.s}</text>
    {/each}
    <g stroke="#94a3b8" strokeWidth="1.5" fill="none">
      <path d="M170 50 V75"/>
      <path d="M170 121 V140 H58 V157 M170 140 V157 M170 140 H282 V157"/>
      <path d="M282 205 V222 H58 V239 M282 222 V239"/>
    </g>
    <rect x="108" y="127" width="124" height="22" rx="4" fill="#64748b" fillOpacity=".15"/>
    <text x="170" y="141" fontSize="10" textAnchor="middle" fill="currentColor">Barramentos</text>
  </svg>
  <caption textAlign="center">Arquitetura conceitual simplificada. Os barramentos de dados, endereços e controle interligam os componentes.</caption>
</box>

| Componente | Função |
|---|---|
| CPU de 8 bits | Executa instruções |
| ULA | Soma, subtrai e faz operações lógicas |
| Registradores | Guardam valores temporários |
| ROM/EEPROM | Armazena programas |
| RAM | Guarda dados durante a execução |
| Clock | Sincroniza o computador |
| Entrada/saída | Botões, teclado, LEDs ou monitor |

## 2. Quais chips usaríamos?

Podemos utilizar a família **74HC**, composta por circuitos lógicos relativamente simples.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="74HC00 DIP14 logic IC chip white background" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **74HC00 — Portas NAND**

      Combinando portas NAND, conseguimos construir outras funções lógicas e circuitos mais complexos.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="74HC283 DIP integrated circuit chip" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **74HC283 — Somador de 4 bits**

      Dois chips permitem realizar somas de 8 bits, formando parte da ULA.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="74HC173 DIP16 integrated circuit" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **74HC173 — Registrador de 4 bits**

      Dois chips armazenam um número de 8 bits.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="AT28C64B EEPROM DIP28 integrated circuit" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **AT28C64B — EEPROM de 8 KB**

      Armazena o programa mesmo depois de desligarmos o computador.
    </box>
  </row>
</box>

Também precisaríamos de contadores, multiplexadores, buffers, memória RAM e circuitos para gerar sinais de controle.

## 3. Como a CPU executaria programas?

Podemos criar um conjunto próprio de instruções, inspirado nos processadores clássicos.

Por exemplo:

| Instrução | Operação |
|---|---|
| `LDI 5` | Carrega o número 5 |
| `STA 0x80` | Salva na memória |
| `LDA 0x80` | Lê da memória |
| `ADD 3` | Soma 3 |
| `SUB 1` | Subtrai 1 |
| `JMP 0x00` | Salta para um endereço |
| `JZ 0x20` | Salta se o resultado for zero |
| `OUT` | Envia um valor à saída |
| `HLT` | Para o processador |

Essas instruções seriam codificadas em bytes na memória. O circuito de controle as decodificaria e acionaria os registradores, a ULA e os barramentos.

### Exemplo de programa real

Um programa que soma 5 + 3 e mostra o resultado nos LEDs:

<CodeBlock language="asm" editable>
LDI 5
ADD 3
OUT
HLT
</CodeBlock>

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium" size="xs" color="secondary">Saída de 8 bits — resultado decimal 8</text>
  <row justify="center" gap={2}>
    {#each [0,0,0,0,1,0,0,0] as bit,i}
      <col align="center" gap={1}>
        <box background={bit?"#22c55e":"surface-tertiary"} border={{size:1,color:bit?"#16a34a":"default"}} radius="full" size="25px" align="center" justify="center">
          {#if bit}<box background="#dcfce7" radius="full" size="9px"/>{/if}
        </box>
        <text size="3xs" color="tertiary">{7-i}</text>
      </col>
    {/each}
  </row>
  <text textAlign="center" color="secondary" size="sm">00001000₂ = 8₁₀</text>
</box>

## 4. Podemos simular nossa CPU agora

Este exemplo representa uma pequena CPU de 8 bits, com acumulador e quatro instruções. É uma simulação didática da execução, não um circuito eletrônico completo.

{@body const prog=[["LDI",5],["ADD",3],["OUT",null],["HLT",null]]}
{@body const [step,setStep]=DIL.useState(0)}
{@body const vals=[0,5,8,8,8]}
<box border radius="xl" padding={3} gap={3}>
  <row justify="between" align="center">
    <box gap="2px">
      <text color="secondary" size="xs">Acumulador A</text>
      <title size="2xl" color="default" tabularNums>{vals[step]}</title>
    </box>
    <box gap="2px" align="end">
      <text color="secondary" size="xs">Contador de programa</text>
      <title size="xl" tabularNums>{step}</title>
    </box>
  </row>
  <row gap={1}>
    {#each Array.from({length:8},(_,i)=>(vals[step]>>(7-i))&1) as bit,i}
      <box flex="1" padding={{y:2}} align="center" radius="sm" background={bit?"#166534":"surface-secondary"}>
        <text color={bit?"#ffffff":"default"} weight="medium" tabularNums>{bit}</text>
      </box>
    {/each}
  </row>
  <box background="surface-secondary" radius="md" padding={2} gap={1}>
    {#each prog as p,i}
      <row key={i} justify="between" padding={2} background={step===i?"rgba(59,130,246,0.15)":undefined} radius="sm">
        <text color="secondary" size="xs" tabularNums>{String(i).padStart(2,"0")}</text>
        <text weight={step===i?"semibold":"normal"}>{p[0]} {p[1]??""}</text>
        {#if step===i}<icon name="arrow-left" color="info"/>{:else}<box width="16px"/>{/if}
      </row>
    {/each}
  </box>
  <row justify="between" align="center">
    <box gap={1}>
      <text color="secondary" size="xs">Porta de saída</text>
      <text weight="medium">{step>=3?"8 (00001000)":"Aguardando OUT"}</text>
    </box>
    <badge color={step===4?"success":"secondary"}>{step===4?"Parado":"Pronto"}</badge>
  </row>
  <row gap={2}>
    <button block color="primary" disabled={step===4} onClick={()=>setStep(s=>Math.min(4,s+1))}><icon name="step-forward"/> Executar instrução</button>
    <button color="secondary" variant="outline" onClick={()=>setStep(0)}><icon name="rotate-ccw"/> Reiniciar</button>
  </row>
</box>

## 5. Como construir fisicamente?

Eu dividiria o projeto em quatro etapas.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="8 bit breadboard computer 74HC logic chips LEDs wires homemade CPU" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Etapa 1 — CPU mínima**

      Montar clock, registradores, somador, barramento e contador de programa. Executar operações manualmente, passo a passo.
    </box>
  </row>
  <row align="start" gap={3}>
    <AsyncImage query="homemade 8 bit breadboard computer EEPROM RAM circuit wiring" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Etapa 2 — Computador programável**

      Adicionar memória, decodificação de instruções e controle automático. Rodar programas sem precisar manipular os sinais manualmente.
    </box>
  </row>
  <row align="start" gap={3}>
    <AsyncImage query="retro homebrew computer breadboard 16x2 LCD display keyboard" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Etapa 3 — Interface**

      Adicionar teclado e display LCD. Criar um monitor simples para inspecionar memória e executar programas.
    </box>
  </row>
  <row align="start" gap={3}>
    <AsyncImage query="homebrew retro 8 bit computer custom printed circuit board through hole chips" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Etapa 4 — Computador definitivo**

      Transferir os circuitos para uma placa PCB, adicionar conectores e construir um gabinete no estilo dos computadores dos anos 1970.
    </box>
  </row>
</box>

## 6. Qual arquitetura escolher?

Existem três caminhos interessantes:

{@body const [arch,setArch]=DIL.useState("custom")}
<box gap={2}>
  {#each [{id:"minimal",name:"CPU didática de 4 bits",desc:"Menos componentes, ótima para entender cada porta lógica. Programas muito limitados."},{id:"custom",name:"CPU própria de 8 bits",desc:"Equilíbrio entre aprendizado e capacidade. Podemos projetar nosso próprio Assembly e rodar programas simples."},{id:"6502",name:"Computador com processador 6502",desc:"Mais próximo do Apple I original. Permite usar um processador pronto e desenvolver um sistema mais sofisticado."}] as a}
    <pressable onClick={()=>setArch(a.id)} border={{size:1,color:arch===a.id?"#3b82f6":"default"}} background={arch===a.id?"rgba(59,130,246,0.07)":undefined} padding={3} radius="lg" direction="row" gap={3} align="start">
      <icon name={arch===a.id?"circle-check":"circle"} color={arch===a.id?"info":"tertiary"} size="lg"/>
      <box flex="1" gap={1}>
        <text weight="medium">{a.name}</text>
        <text color="secondary" size="sm">{a.desc}</text>
      </box>
    </pressable>
  {/each}
  <button block onClick={()=>GenUI.issueNewTurn(({minimal:"Vamos projetar uma CPU didática de 4 bits usando portas lógicas. Defina arquitetura, componentes e esquema inicial.",custom:"Vamos projetar nossa CPU própria de 8 bits usando chips 74HC, sem microcontrolador. Comece pela arquitetura detalhada, conjunto de instruções, registradores, barramentos e esquema elétrico do primeiro módulo.",6502:"Vamos construir um computador estilo Apple I usando processador 6502. Defina componentes, mapa de memória e circuito inicial."})[arch])}>Desenvolver esta arquitetura <icon name="arrow-right"/></button>
</box>

**Eu escolheria a CPU própria de 8 bits.** Ela nos permitiria entender de verdade como um processador funciona, desde os sinais elétricos até a execução de Assembly.

E há uma decisão importante: podemos usar chips de portas lógicas, registradores e somadores prontos, ou construir até o somador e os registradores a partir de portas básicas. A segunda opção exige muito mais componentes.

Para começar, proponho projetar o **primeiro módulo físico: clock + registrador de 8 bits + somador + LEDs**, com esquema elétrico, lista de componentes e ligações pino a pino. Depois evoluímos esse circuito até ele executar programas sozinho.

## user — bbb21076-48ce-46d4-9482-e59c80719ee6

Como seria possível já conectar a uma TV analógica, de tubo? 

## assistant — ae691870-a622-4ffb-93f3-2893f143053f

Sim! E podemos fazer nosso computador de 8 bits **gerar vídeo diretamente para uma TV de tubo (CRT)**, como faziam os computadores domésticos dos anos 1970 e 1980.

O interessante é que podemos construir o circuito de vídeo também com portas lógicas, contadores e memórias, sem precisar de Arduino ou ESP32.

## 1. Como conectar à TV?

Existem três possibilidades:

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="CRT television rear yellow white red RCA composite video inputs" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Vídeo composto (RCA amarelo)**

      É minha primeira escolha. Um circuito gera os sinais de sincronismo e imagem, enviados pelo cabo amarelo à TV.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="vintage CRT television RF antenna coaxial input back panel" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Entrada de antena (RF)**

      Podemos usar um modulador RF externo, que converte nosso vídeo composto para um canal de televisão analógica.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="CRT television RGB SCART connector rear" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **RGB**

      Permite gerar imagens coloridas de boa qualidade, mas exige que a televisão tenha uma entrada RGB compatível. Não é comum em muitas TVs brasileiras.
    </box>
  </row>
</box>

## 2. Como gerar vídeo usando portas lógicas?

Podemos construir um controlador de vídeo independente da CPU.

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 285" width="100%">
    {#each [{x:10,y:10,w:145,h:45,a:"CPU 8 bits",b:"Executa programas"},{x:185,y:10,w:145,h:45,a:"RAM de vídeo",b:"Caracteres da tela"},{x:100,y:91,w:140,h:45,a:"Contadores",b:"Horizontal / vertical"},{x:10,y:175,w:145,h:45,a:"Gerador de pixels",b:"ROM de caracteres"},{x:185,y:175,w:145,h:45,a:"Sincronismo",b:"HSYNC + VSYNC"}] as n}
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx="6" stroke="#64748b" fill="#64748b" fillOpacity=".1"/>
      <text x={n.x+n.w/2} y={n.y+19} textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">{n.a}</text>
      <text x={n.x+n.w/2} y={n.y+34} textAnchor="middle" fontSize="9" fill="currentColor">{n.b}</text>
    {/each}
    <g fill="none" stroke="#94a3b8" strokeWidth="1.6">
      <path d="M155 32 H185"/>
      <path d="M257 55 V73 H170 V91"/>
      <path d="M170 136 V155 H82 V175"/>
      <path d="M170 155 H257 V175"/>
      <path d="M82 220 V241 H170"/>
      <path d="M257 220 V241 H170"/>
      <path d="M170 241 V255"/>
    </g>
    <rect x="105" y="255" width="130" height="28" rx="6" stroke="#22c55e" fill="#22c55e" fillOpacity=".12"/>
    <text x="170" y="273" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">Saída RCA → TV</text>
  </svg>
</box>

O circuito precisa fazer três coisas:

1. **Gerar sincronismo horizontal e vertical:** informa à TV onde começa cada linha e cada quadro.
2. **Ler a memória de vídeo:** descobre qual caractere ou pixel deve aparecer.
3. **Produzir o sinal elétrico:** combina a imagem com o sincronismo em um sinal de vídeo composto.

Para uma primeira versão, podemos gerar vídeo monocromático, sem a complexidade da codificação de cores PAL-M ou NTSC.

## 3. Como ficaria a imagem?

Uma primeira versão poderia oferecer uma tela de texto de 32 colunas por 24 linhas.

<box background="#16191d" theme="dark" radius="xl" padding={3} gap={2}>
  <box background="#252b29" border={{size:3,color:"#444c4b"}} radius="lg" padding={3}>
    <box background="#07150d" radius="lg" padding={3} gap={1}>
      <svg viewBox="0 0 320 224" width="100%">
        <defs>
          <pattern id="scancrt" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 3 H320" stroke="#000" strokeOpacity=".28"/></pattern>
        </defs>
        <rect width="320" height="224" fill="#07150d"/>
        {#each ["*** COMPUTADOR 8 BITS ***","","MEMORIA:  2048 BYTES","CPU:      8 BITS","VIDEO:    MONOCROMATICO","","PRONTO.","","10 PRINT \"OLA MUNDO!\"","20 GOTO 10","","> RUN","","OLA MUNDO!","OLA MUNDO!","OLA MUNDO!","","> _"] as line,i}
          <text x="12" y={15+i*11.5} fill="#7dfba0" fontSize="10.5" fontFamily="monospace" xmlSpace="preserve">{line}</text>
        {/each}
        <rect width="320" height="224" fill="url(#scancrt)"/>
      </svg>
    </box>
  </box>
  <caption color="secondary" textAlign="center">Simulação ilustrativa de uma tela de texto em uma TV CRT. O interpretador BASIC seria uma etapa posterior.</caption>
</box>

## 4. Quais componentes precisaríamos?

Para um gerador de vídeo monocromático, poderíamos utilizar:

| Componente | Função |
|---|---|
| 74HC161 / 74HC163 | Contadores de vídeo |
| 74HC00 / 74HC08 | Lógica de sincronismo |
| 74HC157 | Seleção de sinais e dados |
| 74HC166 | Deslocamento serial dos pixels |
| EEPROM | Fonte dos caracteres |
| SRAM | Memória de vídeo |
| Oscilador | Referência de tempo |
| Resistores | Níveis elétricos de vídeo |

Um detalhe importante: **a CPU não precisa desenhar cada pixel em tempo real**. O controlador de vídeo pode fazer isso sozinho, enquanto a CPU apenas escreve caracteres na memória.

Assim, poderíamos rodar programas e atualizar a tela simultaneamente. Precisaríamos, porém, definir como CPU e vídeo compartilham o acesso à memória.

## 5. Qual padrão de vídeo utilizar?

No Brasil, muitas TVs analógicas de tubo utilizavam PAL-M, mas algumas aceitam NTSC e outros padrões.

Para vídeo monocromático, podemos começar com um sinal composto de aproximadamente 1 Vpp em 75 Ω, com temporização compatível com o sistema de 525 linhas e aproximadamente 60 campos por segundo. O circuito precisa gerar os intervalos de sincronismo e apagamento corretamente.

A ligação deve ser feita somente pela entrada externa de vídeo, sem abrir ou modificar os circuitos internos da TV, que podem conter tensões perigosas mesmo desligada.

---

**Minha proposta:** construir nosso computador com uma saída RCA amarela integrada à placa, desde a primeira versão. Assim, teremos um computador de 8 bits com CPU própria, teclado e uma tela real de televisão.

Antes de desenharmos o circuito eletrônico, preciso saber uma coisa:

**Sua TV de tubo tem entrada RCA amarela (áudio/vídeo) ou somente entrada de antena?**

Isso determina se podemos ligar nosso circuito diretamente à TV ou se precisaremos de um modulador RF.

## user — bbb21823-b4c5-4114-82e4-841a0745655d

Não tenho tv de tubo
Teria de comprar uma
Ou teria alguma alternativa? 


## assistant — dc049660-1f50-4d74-a8e2-4cbddc88a88d

{"content_type": "thoughts", "source_analysis_msg_id": "0d06ed39-70a7-4cd9-a1f7-3c642297fad4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 6 sites"}]}

## assistant — 056913f9-5db5-4055-a6d8-912c0a22b98b

{"content": "Pensou por 11s", "content_type": "reasoning_recap"}

## assistant — 5192eb11-f042-490c-b950-d81026396830

Não precisamos comprar uma TV de tubo para começar! Existem alternativas muito interessantes para nosso computador de 8 bits, e algumas são até melhores para desenvolver e testar os circuitos.

O mais importante é separar duas coisas: **o circuito que gera o vídeo** e **a tela que mostra a imagem**.

Podemos construir nosso próprio gerador de vídeo com portas lógicas e escolher diferentes tipos de tela.

## 1. Alternativas para nosso computador

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="small 5 inch LCD monitor composite AV RCA input retro computer" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **1. Mini monitor LCD com entrada AV**

      <badge color="success">Minha preferência</badge>

      Aceita vídeo composto, como uma TV antiga. Podemos usar exatamente o mesmo circuito que usaríamos com uma TV de tubo.

      <text color="secondary" size="sm">Vantagem: mantém o projeto retrô e permite conectar uma TV CRT futuramente.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="20x4 character LCD green display HD44780 electronics" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **2. Display LCD de caracteres (20×4)**

      Podemos controlar diretamente pelo barramento da CPU usando circuitos de entrada e saída.

      <text color="secondary" size="sm">Vantagem: implementação mais simples. Desvantagem: apenas quatro linhas de texto, sem vídeo convencional.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro computer VGA monitor displaying green text terminal" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **3. Monitor VGA**

      Podemos construir um controlador VGA com contadores, portas lógicas e memória de vídeo.

      <text color="secondary" size="sm">Vantagem: imagem nítida, conexão direta a monitores VGA. Exige temporização mais rápida.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro 8 bit computer composite video HDMI converter modern monitor" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **4. Monitor ou TV moderna com HDMI**

      Nosso computador gera vídeo composto, e um conversor AV-para-HDMI transforma o sinal para uma tela moderna.

      <text color="secondary" size="sm">Vantagem: podemos usar uma tela que já temos. O conversor faz o trabalho de adaptação.</text>
    </box>
  </row>
</box>

## 2. Algumas opções que encontrei

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage ref="turn656833product0" maxWidth="116px" aspectRatio="1:1"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn656833product0" value={turn656833product0.title}/>**

      <title size="lg" color="default">{turn656833product0.displayed_price}</title>
      <text color="secondary" size="xs">{turn656833product0.merchant}</text>
      Boa candidata para um computador compacto. Confirmar entrada CVBS/RCA e alimentação antes de comprar.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn656833product31" maxWidth="116px" aspectRatio="1:1"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn656833product31" value={turn656833product31.title}/>**

      <title size="lg">{turn656833product31.displayed_price}</title>
      <text color="secondary" size="xs">{turn656833product31.merchant}</text>
      Para aproveitar uma TV ou monitor HDMI existente. Precisa aceitar entrada AV e produzir saída HDMI.
    </box>
  </row>
</box>

Atenção à direção do conversor: precisamos de **AV → HDMI**, não HDMI → AV. Muitos anúncios misturam essas descrições.

## 3. O que eu faria no nosso projeto

Manteria uma saída de vídeo composto monocromático, gerada inteiramente por lógica digital, e começaria usando um monitor LCD pequeno com entrada AV.

Isso permite evoluir posteriormente para gráficos, jogos simples e até uma interface de texto semelhante à do Apple I, sem trocar o circuito de vídeo.

**Uma pergunta para definirmos o hardware:** você prefere que nosso computador tenha uma telinha própria de 5 polegadas, formando uma máquina compacta, ou que seja conectado a um monitor grande que você já possui?

## user — bbb2118f-51a0-4fc0-8577-b3a6b5d58114

Usar uma tela dessas de câmera de ré eh uma opção interessante

## assistant — 8ad624cc-8259-4bd3-b747-1e70bb75e3ee

{"content_type": "thoughts", "source_analysis_msg_id": "77df53aa-671a-4e70-b666-06b6c8b1019c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — 1f657044-7b70-41e9-aed2-5102952eb07d

{"content": "Pensou por 17s", "content_type": "reasoning_recap"}

## assistant — 9cf7b766-8046-451c-bc6a-49e7082469b3

Sim! Uma **tela de câmera de ré automotiva** pode ser uma excelente escolha para nosso computador de 8 bits feito com portas lógicas.

Ela tem uma vantagem enorme: muitos desses monitores já aceitam vídeo composto (CVBS), exatamente o tipo de sinal que podemos gerar com circuitos digitais simples.

<grid columns={2} gap={3}>
  <grid-item>
    <AsyncImage query="4.3 inch automotive rear view camera LCD monitor standalone black screen RCA composite" aspectRatio="5:4"/>
    <text weight="medium" size="sm">Monitor de 4,3 polegadas</text>
    <text color="secondary" size="xs">Compacto e fácil de integrar a um gabinete</text>
  </grid-item>
  <grid-item>
    <AsyncImage query="5 inch car rear view camera LCD monitor AV RCA composite video" aspectRatio="5:4"/>
    <text weight="medium" size="sm">Monitor de 5 polegadas</text>
    <text color="secondary" size="xs">Mais confortável para visualizar textos</text>
  </grid-item>
</grid>

## Como conectaríamos?

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 150" width="100%">
    <rect x="5" y="26" width="95" height="75" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="52" y="49" fontSize="12" fontWeight="600" textAnchor="middle" fill="currentColor">CPU 8 bits</text>
    <text x="52" y="65" fontSize="10" textAnchor="middle" fill="currentColor">Portas lógicas</text>
    <text x="52" y="80" fontSize="9" textAnchor="middle" fill="currentColor">RAM + ROM</text>
    <rect x="120" y="26" width="99" height="75" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="169" y="48" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">Vídeo</text>
    <text x="169" y="63" fontSize="10" textAnchor="middle" fill="currentColor">Contadores</text>
    <text x="169" y="77" fontSize="10" textAnchor="middle" fill="currentColor">+ lógica</text>
    <rect x="242" y="14" width="93" height="100" rx="7" fill="#343c45" stroke="#94a3b8"/>
    <rect x="250" y="23" width="77" height="74" rx="3" fill="#0b1b12"/>
    {#each ["8-BIT READY","> HELLO","OK","_"] as line,i}
      <text x="255" y={39+i*15} fontFamily="monospace" fontSize="9" fill="#83ef9c">{line}</text>
    {/each}
    <path d="M100 63 H120 M219 63 H242" stroke="#94a3b8" strokeWidth="2"/>
    <text x="231" y="52" fontSize="8" fill="currentColor" textAnchor="middle">AV</text>
    <text x="170" y="130" textAnchor="middle" fontSize="10" fill="currentColor">Saída composta monocromática → RCA amarelo</text>
  </svg>
</box>

Para funcionar, precisamos verificar três características do monitor:

- **Entrada AV/CVBS:** normalmente um conector RCA amarelo.
- **Alimentação:** muitos modelos automotivos usam 12 V; nosso computador provavelmente usará 5 V, então podemos ter duas tensões na mesma fonte.
- **Compatibilidade de vídeo:** preferencialmente NTSC ou PAL-M. Alguns monitores automotivos aceitam NTSC e PAL-B/G, mas não necessariamente PAL-M.

Para nossa primeira versão, eu faria uma tela monocromática com caracteres de 8×8 pixels. Uma resolução lógica de 256×192 permitiria organizar 32 colunas por 24 linhas de texto. A geração do sinal composto exigiria adaptar essa área ativa à temporização de vídeo escolhida.

## 6. Um modelo concreto para considerar

Encontrei um monitor automotivo de 4,3 polegadas da WMIX com duas entradas AV (RCA), compatibilidade PAL/NTSC e preço anunciado de aproximadamente R$ 66. É uma opção interessante para testar nosso projeto, embora seja necessário confirmar a tensão de alimentação com o vendedor, pois o anúncio apresenta informações inconsistentes. <Cite ref="turn267889search0"/>

<Link url="https://www.mercadolivre.com.br/tela-automotiva-43-monitor-veicular-lcd-entrada-av-12v24v-compativel-com-camera-de-re-instalacao-simples-wmix-eletronicos/p/MLB64345157" title="Ver monitor de 4,3 polegadas no Mercado Livre"/>

Eu começaria pelo **circuito gerador de vídeo**, antes mesmo de construir a CPU inteira. Nossa primeira experiência seria mostrar uma imagem fixa, depois caracteres e, finalmente, texto enviado pelo processador.

Assim, quando a CPU estiver pronta, já teremos uma tela funcionando para testar nossos programas.

## user — bbb21e41-f806-4ebb-8586-49432799a160

Ok
Já temos um rascunho
Agora precisamos entender o tamanho do projeto
Quantos CIs? 
Materiais
Cabos
Conectores
Teclado? Mouse? Entendo que não podemos usar um USB de alto dpi

## assistant — 66ee254e-530f-4a05-994e-a553d1454af9

{"content_type": "thoughts", "source_analysis_msg_id": "1567e288-aded-438a-a3aa-b19338133139", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 10 sites"}]}

## assistant — 0286f6cc-7fee-4e32-9668-b6b445de7e2e

{"content": "Pensou por 17s", "content_type": "reasoning_recap"}

## assistant — bf7e4b46-2509-4e73-b345-8cec4a898406

Agora chegamos à parte mais importante: transformar nossa ideia em um **projeto eletrônico viável**, com quantidade de componentes, dimensões, alimentação, conectores e possibilidades de expansão.

Minha proposta é construir um computador de 8 bits inspirado no Apple I, mas com **processador próprio feito de CIs lógicos da família 74HC**, sem utilizar microcontrolador como CPU.

Vamos dimensioná-lo pensando em um computador de verdade, capaz de executar programas, receber comandos pelo teclado e exibir texto e gráficos simples na tela de câmera de ré.

## 1. Especificações que proponho

<box border radius="xl" padding={3} gap={3}>
  <row align="center" justify="between">
    <box gap={1}>
      <text color="secondary" weight="medium" size="xs">Projeto provisório</text>
      <title size="xl">Computador TTL-8</title>
      <text color="secondary" size="sm">Arquitetura de 8 bits com vídeo composto</text>
    </box>
    <icon name="cpu" size="3xl" color="secondary"/>
  </row>
  <divider color="subtle"/>
  <grid columns={2} gap={3}>
    {#each [{l:"Processador",v:"8 bits"},{l:"Clock inicial",v:"1 MHz"},{l:"RAM",v:"32 KB"},{l:"ROM",v:"8–16 KB"},{l:"Vídeo",v:"Monocromático"},{l:"Tela",v:"LCD AV 4,3–5″"},{l:"Teclado",v:"PS/2"},{l:"Expansão",v:"GPIO / serial"}] as a}
      <grid-item>
        <text color="secondary" size="xs">{a.l}</text>
        <text weight="medium">{a.v}</text>
      </grid-item>
    {/each}
  </grid>
</box>

O clock de 1 MHz é uma meta, não uma velocidade garantida. A frequência máxima dependerá do caminho crítico dos circuitos, da organização dos barramentos e da qualidade da montagem.

## 2. Quantos circuitos integrados?

<text color="secondary" size="sm">Estimativa preliminar para uma arquitetura com registradores de 8 bits, ULA, controle microprogramado e controlador de vídeo independente.</text>

| Subsistema | Quantidade estimada |
|---|---:|
| Registradores e barramentos da CPU | 12–18 CIs |
| ULA e flags | 8–12 CIs |
| Contador de programa e endereçamento | 6–10 CIs |
| Controle e decodificação | 8–14 CIs |
| RAM, ROM e lógica de seleção | 4–7 CIs |
| Vídeo composto e caracteres | 16–25 CIs |
| Interface de teclado PS/2 | 5–9 CIs |
| Clock, reset e interfaces | 4–7 CIs |
| **Total estimado** | **63–102 CIs** |

<box gap={1}>
  <row align="baseline" justify="between">
    <title size="2xl" color="default">~80 CIs</title>
    <text color="secondary" size="sm">Referência para planejamento</text>
  </row>
  <box background="surface-tertiary" radius="full" height="12px" clip>
    <row height="100%" gap="2px">
      {#each [{n:15,c:"#64748b"},{n:10,c:"#3b82f6"},{n:8,c:"#8b5cf6"},{n:11,c:"#14b8a6"},{n:6,c:"#f59e0b"},{n:20,c:"#22c55e"},{n:7,c:"#ec4899"},{n:5,c:"#a3a3a3"}] as a}
        <box flex={a.n} background={a.c}/>
      {/each}
    </row>
  </box>
  <caption>Distribuição ilustrativa de 82 CIs. O número definitivo depende do esquema elétrico.</caption>
</box>

É um projeto relativamente grande. Entretanto, esses 80 CIs não precisam ser montados de uma vez. Podemos dividir tudo em placas independentes e testáveis.

## 3. Teclado: podemos usar um teclado de PC?

Sim. E não precisamos construir um teclado do zero.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="classic beige PS2 keyboard mini DIN connector" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Teclado PS/2 — recomendado**

      Usa apenas duas linhas de comunicação, Clock e Data, além da alimentação. Podemos construir um receptor usando registradores de deslocamento e lógica digital.

      O protocolo transmite quadros de 11 bits, incluindo dados, paridade e bits de início/fim. <Cite refs={["turn653266search25","turn653266search26"]}/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro computer custom mechanical keyboard matrix PCB switches" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **Teclado matricial próprio**

      Podemos montar 40 a 60 teclas e criar um circuito de varredura com contadores e multiplexadores.

      É mais trabalho mecânico, mas combina muito com a ideia de construir um computador totalmente nosso.
    </box>
  </row>
</box>

Eu escolheria PS/2 para a primeira versão. Uma observação: um teclado USB com adaptador passivo para PS/2 só funciona se o próprio teclado suportar esse protocolo.

## 4. E o mouse?

Você está certo em desconfiar de um mouse USB moderno, mas **o problema não é o DPI**.

DPI representa a resolução do sensor do mouse. O que dificulta a conexão é o protocolo USB, que exige um controlador host, enumeração e comunicação relativamente complexa.

Temos três alternativas:

| Mouse | Viabilidade |
|---|---|
| PS/2 | Boa, usando interface digital própria |
| Serial RS-232 antigo | Boa, com UART e adaptação elétrica |
| USB moderno | Complexa sem controlador USB host dedicado |

Um mouse PS/2 é especialmente interessante porque utiliza uma interface elétrica semelhante à do teclado, mas precisamos implementar seus comandos de inicialização e interpretar os pacotes de movimento.

Para nossa primeira versão, eu deixaria o mouse como expansão. Um computador com interface de texto não precisa dele. Posteriormente, podemos criar um cursor gráfico e um pequeno sistema de janelas.

## 5. Materiais, conectores e cabos

Aqui está uma lista preliminar, sem ainda fixar a quantidade exata de cada modelo de CI.

| Material | Quantidade inicial |
|---|---:|
| CIs lógicos 74HC/74HCT | 70–100 unidades |
| SRAM 32 KB | 1 unidade |
| EEPROM 8–16 KB | 1–3 unidades |
| Soquetes DIP | 1 por CI DIP |
| Capacitores cerâmicos 100 nF | 100–120 unidades |
| Capacitores eletrolíticos | 10–15 unidades |
| Resistores diversos | 100–200 unidades |
| LEDs indicadores | 16–24 unidades |
| Osciladores e componentes de clock | 2–4 conjuntos |
| Botões reset/step | 2–4 unidades |
| Protoboards grandes | 6–10 unidades, provisoriamente |
| Fios jumper | 300–500 unidades |
| Conector RCA fêmea | 1 unidade |
| Conector PS/2 Mini-DIN | 1–2 unidades |
| Conector de alimentação | 1 unidade |
| Conectores de expansão | 2–4 conjuntos |
| Monitor AV automotivo | 1 unidade |
| Teclado PS/2 | 1 unidade |

Para as memórias, o total considera chips de dados e possíveis EEPROMs de microcódigo ou fonte de caracteres. A organização definitiva ainda precisa ser escolhida.

### Alimentação

Eu usaria uma fonte externa certificada de 12 V, com conversão DC-DC para 5 V na placa. O monitor automotivo receberia 12 V somente se suas especificações confirmassem essa tensão.

A fonte de 5 V deve ser dimensionada a partir do consumo real dos componentes, com margem e proteção contra curto-circuito.

Cada CI precisará de desacoplamento próximo aos pinos de alimentação. Com dezenas de chips e sinais de vídeo relativamente rápidos, uma PCB será muito mais confiável que uma montagem definitiva em protoboards.

## 6. Qual seria o tamanho físico?

<text color="secondary" size="sm">Estimativa de espaço, não desenho de fabricação.</text>

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 220" width="100%">
    <rect x="15" y="8" width="310" height="184" rx="8" fill="#166534" fillOpacity=".2" stroke="#16a34a" strokeWidth="2"/>
    {#each [{x:26,y:20,w:142,h:88,t:"CPU"},{x:176,y:20,w:138,h:88,t:"VÍDEO"},{x:26,y:117,w:90,h:62,t:"MEMÓRIA"},{x:123,y:117,w:98,h:62,t:"CONTROLE"},{x:228,y:117,w:86,h:62,t:"I/O"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="4" stroke="#86efac" strokeDasharray="3 3" fill="#14532d" fillOpacity=".3"/>
      <text x={b.x+b.w/2} y={b.y+14} fill="currentColor" textAnchor="middle" fontSize="9" fontWeight="600">{b.t}</text>
      {#each Array.from({length:b.t==="CPU"?15:b.t==="VÍDEO"?18:6},(_,i)=>i) as i}
        <rect x={b.x+8+(i%5)*((b.w-16)/5)} y={b.y+23+Math.floor(i/5)*15} width={(b.w-24)/5} height="10" rx="1" fill="#1f2937" stroke="#94a3b8" strokeWidth=".5"/>
      {/each}
    {/each}
    <text x="170" y="210" textAnchor="middle" fontSize="11" fill="currentColor">PCB conceitual: aproximadamente 30 × 20 cm</text>
  </svg>
</box>

Uma placa de aproximadamente **30 × 20 cm** é um ponto de partida plausível para estudar o layout, mas pode precisar crescer ou ser dividida em módulos. O espaço depende principalmente dos encapsulamentos DIP, dos conectores e do roteamento.

## 7. Como dividiria a construção

Não compraria os 80 CIs de uma vez. Primeiro fecharia o projeto lógico, depois montaria cada módulo.

<box gap={2}>
  {#each [{n:"01",t:"Clock e registradores",d:"Executar ciclos manualmente e observar os bits em LEDs."},{n:"02",t:"ULA e CPU",d:"Implementar instruções, saltos, registradores e controle."},{n:"03",t:"Memória e programas",d:"Executar código armazenado na EEPROM, usando RAM para variáveis."},{n:"04",t:"Vídeo composto",d:"Gerar sincronismo e caracteres para a tela automotiva."},{n:"05",t:"Teclado PS/2",d:"Receber teclas, interpretar códigos e criar um terminal."},{n:"06",t:"Sistema e expansão",d:"Monitor de máquina, editor simples, jogos e interface para mouse."}] as s}
    <row align="start" gap={3}>
      <box background="surface-secondary" radius="md" padding={2}>
        <text weight="semibold" tabularNums>{s.n}</text>
      </box>
      <box flex="1" gap={1}>
        <text weight="medium">{s.t}</text>
        <text color="secondary" size="sm">{s.d}</text>
      </box>
    </row>
  {/each}
</box>

## 8. Uma decisão importante antes de comprar

Precisamos definir o quanto queremos construir literalmente com portas lógicas.

{@body const [nivel,setNivel]=DIL.useState("equilibrado")}
<box gap={2}>
  {#each [{id:"purista",title:"Totalmente discreto",desc:"Construir registradores, somadores e controle usando portas lógicas básicas. Muito mais chips, fios e espaço."},{id:"equilibrado",title:"Lógica 74HC com CIs funcionais",desc:"Construir nossa própria CPU usando somadores, registradores, contadores, portas e memórias prontas. Sem processador comercial."},{id:"hibrido",title:"CPU própria com periféricos dedicados",desc:"CPU construída com lógica 74HC, mas teclado e vídeo podem utilizar controladores especializados para reduzir a complexidade."}] as o}
    <pressable onClick={()=>setNivel(o.id)} border={{size:1,color:nivel===o.id?"#3b82f6":"default"}} radius="lg" padding={3} direction="row" align="start" gap={3} background={nivel===o.id?"rgba(59,130,246,0.06)":undefined}>
      <icon name={nivel===o.id?"circle-check":"circle"} color={nivel===o.id?"info":"tertiary"} size="lg"/>
      <box flex="1" gap={1}>
        <text weight="medium">{o.title}</text>
        <text color="secondary" size="sm">{o.desc}</text>
      </box>
    </pressable>
  {/each}
  <button block onClick={()=>GenUI.issueNewTurn(({purista:"Quero construir o computador de 8 bits de forma purista, usando portas lógicas básicas até para registradores e ULA. Dimensione a arquitetura e faça uma lista de materiais detalhada.",equilibrado:"Vamos adotar CPU própria com lógica 74HC e CIs funcionais. Defina arquitetura completa, mapa de memória, barramentos, vídeo composto e lista exata de CIs por módulo antes das compras.",hibrido:"Quero CPU própria com lógica 74HC, mas aceito controladores dedicados para periféricos. Otimize a arquitetura para reduzir CIs, mantendo CPU de 8 bits construída por nós."})[nivel])}>Definir arquitetura <icon name="arrow-right"/></button>
</box>

Minha escolha é a **segunda opção**. Preserva o desafio de construir um processador real, mas evita multiplicar desnecessariamente os componentes.

O próximo passo seria desenhar a arquitetura elétrica completa, especialmente os barramentos, o mapa de memória e a comunicação entre CPU e vídeo. Só depois disso conseguiremos transformar a estimativa de aproximadamente 80 CIs em uma lista de materiais confiável, com modelos e quantidades exatas.

## user — bbb2191d-a7ea-4d8f-b316-4870909d27f4

Vamos adotar CPU própria com lógica 74HC e CIs funcionais. Defina arquitetura completa, mapa de memória, barramentos, vídeo composto e lista exata de CIs por módulo antes das compras.

## assistant — 9cfc6c0a-5190-46cf-93c8-7c7a2b9c7541

{"content": "Pensou por 36s", "content_type": "reasoning_recap"}

## assistant — 21cd3622-d6e1-4c9a-b7e1-2e21e3b3894a

# Projeto TTL-8 — Arquitetura de hardware v0.1

Vamos estabelecer uma arquitetura concreta para nosso computador de 8 bits, construído com circuitos integrados 74HC, sem microcontrolador e com saída de vídeo composto para um monitor de câmera de ré.

A prioridade será que o computador consiga **buscar instruções na memória, executar programas sozinho, utilizar RAM, receber comandos do teclado e escrever na tela**.

Uma distinção importante: podemos definir agora uma lista fechada de componentes para a arquitetura proposta, mas ela será uma **BOM de engenharia v0.1**, não uma lista de compras validada. As quantidades finais dependem da simulação dos circuitos, das temporizações e da revisão do esquema elétrico.

## 1. Especificação do computador

<box border radius="xl" padding={3} gap={2}>
  <row align="center" justify="between">
    <box gap={1}>
      <text color="secondary" weight="medium" size="xs">TTL-8 / REV 0.1</text>
      <title size="xl">Computador de 8 bits</title>
      <text color="secondary" size="sm">CPU própria • lógica 74HC • arquitetura Von Neumann modificada</text>
    </box>
    <icon name="cpu" size="3xl" color="secondary"/>
  </row>
  <divider color="subtle"/>
  <grid columns={2} gap={3}>
    {#each [{k:"Dados",v:"8 bits"},{k:"Endereçamento",v:"16 bits"},{k:"Espaço de memória",v:"64 KiB"},{k:"Clock CPU",v:"1 MHz (meta)"},{k:"RAM principal",v:"32 KiB"},{k:"ROM",v:"16 KiB"},{k:"VRAM",v:"2 KiB"},{k:"Vídeo",v:"CVBS monocromático"},{k:"Texto",v:"32 × 24"},{k:"Teclado",v:"PS/2"},{k:"Mouse",v:"PS/2 futuro"},{k:"Alimentação lógica",v:"5 V"}] as a}
      <grid-item>
        <text color="secondary" size="xs">{a.k}</text>
        <text weight="medium">{a.v}</text>
      </grid-item>
    {/each}
  </grid>
</box>

A CPU terá acumulador, registradores auxiliares, contador de programa, ponteiro de pilha, flags e uma ULA de 8 bits.

A tela terá seu próprio circuito de temporização, de forma que o processador não precise produzir os pixels por software.

## 2. Diagrama geral da arquitetura

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 325" width="100%">
    <g fontSize="11" fill="currentColor" textAnchor="middle">
      <rect x="97" y="8" width="146" height="45" rx="6" fill="#2563eb" fillOpacity=".16" stroke="#60a5fa"/>
      <text x="170" y="27" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="42" fontSize="9">ULA • registradores • controle</text>
      <path d="M170 53 V80" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="12" y="80" width="316" height="31" rx="5" fill="#64748b" fillOpacity=".14" stroke="#94a3b8"/>
      <text x="170" y="99">Barramentos: dados / endereços / controle</text>
      {#each [{x:8,t:"ROM",s:"16 KiB"},{x:91,t:"RAM",s:"32 KiB"},{x:174,t:"VRAM",s:"2 KiB"},{x:257,t:"I/O",s:"PS/2"}] as b}
        <path d={`M${b.x+37} 111 V136`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={b.x} y="136" width="75" height="48" rx="5" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
        <text x={b.x+37} y="154" fontWeight="600">{b.t}</text>
        <text x={b.x+37} y="169" fontSize="10">{b.s}</text>
      {/each}
      <path d="M211 184 V209 H170 V224" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="91" y="224" width="158" height="42" rx="5" fill="#16a34a" fillOpacity=".12" stroke="#4ade80"/>
      <text x="170" y="241" fontWeight="600">Controlador de vídeo</text>
      <text x="170" y="255" fontSize="9">Contadores + ROM de fonte</text>
      <path d="M170 266 V281" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="101" y="281" width="138" height="36" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="170" y="296" fontWeight="600">Saída RCA / CVBS</text>
      <text x="170" y="309" fontSize="9">Monitor automotivo</text>
    </g>
  </svg>
  <caption>Diagrama funcional. O acesso simultâneo da CPU e do controlador de vídeo à VRAM será resolvido por arbitragem de barramento.</caption>
</box>

A arquitetura utiliza uma memória principal compartilhada entre instruções e dados, mas mantém uma região de vídeo com acesso especial. Isso facilita a programação sem obrigar a CPU a interromper constantemente a execução para atualizar a imagem.

## 3. Barramentos

| Barramento | Largura | Finalidade |
|---|---:|---|
| D0–D7 | 8 bits | Dados e instruções |
| A0–A15 | 16 bits | Endereços |
| RD# | 1 bit | Leitura |
| WR# | 1 bit | Escrita |
| MEMREQ# | 1 bit | Acesso à memória |
| IOREQ# | 1 bit | Acesso a periféricos |
| RESET# | 1 bit | Reinicialização |
| CLK | 1 bit | Clock |
| WAIT | 1 bit | Suspensão de ciclos |
| IRQ | 1 bit | Interrupção futura |

O símbolo `#` indica um sinal ativo em nível baixo.

Os barramentos não serão conectados indiscriminadamente. Precisaremos de buffers tri-state e regras para impedir que dois circuitos tentem dirigir os mesmos fios simultaneamente.

Para reduzir complexidade, proponho inicialmente uma CPU com ciclos de memória síncronos e controle microprogramado. A CPU poderá usar vários ciclos de clock para executar uma única instrução.

## 4. Mapa de memória de 64 KiB

Este será o mapa de endereços visto pelo processador.

| Endereços | Tamanho | Uso |
|---|---:|---|
| `0000–3FFF` | 16 KiB | ROM do sistema |
| `4000–BFFF` | 32 KiB | RAM principal |
| `C000–C7FF` | 2 KiB | RAM de vídeo |
| `C800–DFFF` | 6 KiB | Reservado para expansão |
| `E000–E0FF` | 256 B | Periféricos |
| `E100–FFFF` | 7.75 KiB | Reservado |

<box gap={2}>
  <text weight="medium" size="sm">Distribuição do espaço de endereçamento</text>
  <box border radius="lg" padding={2} gap="3px">
    {#each [{name:"ROM",size:"16 KiB",pct:25,c:"#3b82f6"},{name:"RAM",size:"32 KiB",pct:50,c:"#16a34a"},{name:"VRAM",size:"2 KiB",pct:3.125,c:"#eab308"},{name:"Expansão",size:"6 KiB",pct:9.375,c:"#8b5cf6"},{name:"I/O",size:"256 B",pct:.390625,c:"#f97316"},{name:"Reservado",size:"7.75 KiB",pct:12.109375,c:"#64748b"}] as m}
      <row align="center" gap={2}>
        <text size="xs" width="70px">{m.name}</text>
        <box flex="1" background="surface-tertiary" height="13px" radius="2xs" clip>
          <box background={m.c} height="100%" width={`${m.pct}%`}/>
        </box>
        <text size="xs" color="secondary" width="49px" textAlign="end">{m.size}</text>
      </row>
    {/each}
  </box>
</box>

### Registradores de entrada e saída

Vamos usar periféricos mapeados em memória, evitando a necessidade de instruções especiais `IN` e `OUT`.

| Endereço | Registrador |
|---|---|
| `E000` | Dados do teclado PS/2 |
| `E001` | Estado do teclado |
| `E002` | Controle do teclado |
| `E010` | Saída de 8 LEDs |
| `E011` | Entrada de 8 bits |
| `E020` | Controle de vídeo |
| `E021` | Estado do vídeo |
| `E030` | Temporizador |
| `E031` | Controle do temporizador |

Os endereços são uma proposta de interface. Alguns registradores, como o controle de vídeo, serão inicialmente reservados e poderão não ter circuitos implementados na primeira revisão.

## 5. CPU: organização interna

Proponho os seguintes registradores:

| Registrador | Bits | Função |
|---|---:|---|
| A | 8 | Acumulador |
| B | 8 | Segundo operando da ULA |
| X | 8 | Índice |
| PC | 16 | Contador de programa |
| SP | 16 | Ponteiro de pilha |
| MAR | 16 | Endereço de memória |
| MDR | 8 | Dados de memória |
| IR | 8 | Instrução atual |
| FLAGS | 4 | Zero, Carry, Negativo, Overflow |

A ULA terá as operações de soma, subtração, AND, OR, XOR, deslocamento e comparação.

Para simplificar a primeira CPU, algumas operações serão realizadas em múltiplos ciclos. Não precisamos construir um circuito independente para cada instrução.

### Formato das instruções

A CPU terá instruções de comprimento variável:

- 1 byte: operações sem operandos.
- 2 bytes: opcode + valor de 8 bits.
- 3 bytes: opcode + endereço de 16 bits, em ordem little-endian.

Uma primeira tabela de instruções:

| Opcode | Assembly | Bytes |
|---|---|---:|
| `00` | NOP | 1 |
| `10` | LDI valor | 2 |
| `11` | LDA endereço | 3 |
| `12` | STA endereço | 3 |
| `20` | ADD valor | 2 |
| `21` | SUB valor | 2 |
| `22` | AND valor | 2 |
| `23` | OR valor | 2 |
| `24` | XOR valor | 2 |
| `30` | JMP endereço | 3 |
| `31` | JZ endereço | 3 |
| `32` | JNZ endereço | 3 |
| `40` | TAX | 1 |
| `41` | TXA | 1 |
| `FF` | HLT | 1 |

Esses códigos ainda são uma especificação de ISA: o microcódigo precisará ser escrito para implementá-los. A pilha, chamadas de subrotina e interrupções serão uma expansão posterior.

## 6. Vídeo composto: projeto concreto

Para nosso monitor automotivo, escolho inicialmente um sinal **monocromático compatível com temporização de 525 linhas/59,94 campos**, usando clock de referência de aproximadamente 14,31818 MHz.

Isso permite usar um clock de pixel de aproximadamente 7,15909 MHz, obtido por divisão por dois.

<box border radius="lg" padding={3} gap={2}>
  <title size="md">Pipeline de vídeo</title>
  <box background="surface-secondary" padding={2} radius="md" align="center">
    **Oscilador 14,31818 MHz**
  </box>
  <row justify="center">
    <icon name="arrow-down" color="secondary"/>
  </row>
  <grid columns={2} gap={2}>
    <grid-item>
      <box border padding={2} radius="md" align="center" gap={1}>
        **Contadores H/V**
        <text color="secondary" size="xs" textAlign="center">Posição e sincronismo</text>
      </box>
    </grid-item>
    <grid-item>
      <box border padding={2} radius="md" align="center" gap={1}>
        **Endereço VRAM**
        <text color="secondary" size="xs" textAlign="center">Caractere e linha</text>
      </box>
    </grid-item>
  </grid>
  <row justify="center">
    <icon name="arrow-down" color="secondary"/>
  </row>
  <box border padding={2} radius="md" align="center">
    **ROM de fonte → registrador de deslocamento**
  </box>
  <row justify="center">
    <icon name="arrow-down" color="secondary"/>
  </row>
  <box background="surface-secondary" padding={2} radius="md" align="center">
    **Mistura de luminância e sincronismo → RCA**
  </box>
</box>

### Resolução de texto

Vamos utilizar 32 colunas × 24 linhas, com caracteres de 8 × 8 pixels. Isso representa uma imagem lógica de 256 × 192 pixels.

A VRAM precisa de apenas 768 bytes para guardar os códigos dos caracteres. Os 2 KiB reservados permitem expansão.

O gerador de vídeo lerá a VRAM, consultará uma ROM contendo os desenhos dos caracteres e enviará os pixels serialmente.

**Ponto crítico:** a SRAM de vídeo não possui duas portas independentes. Portanto, proponho um esquema de arbitragem: o controlador de vídeo terá prioridade durante as leituras de caracteres, e a CPU poderá escrever nos intervalos disponíveis, recebendo `WAIT` quando necessário.

Também precisaremos de uma pequena etapa analógica para garantir os níveis de sincronismo, preto e branco sobre carga de 75 Ω. Não é seguro presumir que uma saída 74HC ligada diretamente ao RCA produza um sinal correto.

Para a primeira revisão, adotaremos temporização progressiva experimental próxima de 240p, que costuma funcionar em monitores CVBS compatíveis, mas não é garantida em todos os monitores automotivos. A compatibilidade será um teste obrigatório antes de finalizar a placa.

## 7. Lista de CIs por módulo — BOM v0.1

Para tornar a lista concreta, vou escolher uma implementação baseada em microcódigo, registradores de 8 bits, SRAM assíncrona e lógica de seleção 74HC.

As quantidades abaixo representam uma **alocação inicial de projeto**, com referências específicas. Ainda não representam um circuito verificado pino a pino.

### Módulo A — CPU, ULA e barramentos

| CI | Quantidade | Função |
|---|---:|---|
| 74HC574 | 6 | Registradores de 8 bits |
| 74HC173 | 2 | Registradores auxiliares de 4 bits |
| 74HC283 | 2 | Somador de 8 bits |
| 74HC86 | 2 | XOR e inversão condicional |
| 74HC08 | 2 | Operações AND |
| 74HC32 | 2 | Operações OR |
| 74HC157 | 4 | Multiplexadores |
| 74HC245 | 3 | Buffers de barramento |
| 74HC161 | 4 | Contadores de PC/SP |
| 74HC00 | 3 | Lógica auxiliar |
| 74HC04 | 1 | Inversores |
| 74HC138 | 2 | Decodificação |
| **Subtotal** | **33** | |

A quantidade de registradores 74HC574 cobre parte dos registradores de dados; o PC e o SP utilizam contadores dedicados. O MAR de 16 bits e os caminhos de escrita ainda precisam ser verificados contra o diagrama de ciclos, pois a simples soma dos chips não garante que todos os registradores tenham caminhos independentes.

### Módulo B — Controle microprogramado

| CI | Quantidade | Função |
|---|---:|---|
| AT28C64B | 3 | ROMs de microcódigo |
| 74HC161 | 1 | Contador de microetapas |
| 74HC273 | 1 | Registro de controle |
| 74HC157 | 2 | Seleção de próximo estado |
| 74HC138 | 2 | Decodificação |
| 74HC00 | 2 | Lógica de controle |
| 74HC74 | 2 | Flip-flops de estado |
| **Subtotal** | **13** | |

Três EEPROMs de 8 bits oferecem 24 sinais de microcontrole. Precisaremos definir quais sinais são diretos, quais são codificados e como o endereço do microcódigo combina opcode, microetapa e flags.

Essa é uma das partes que mais provavelmente exigirá ajustes na contagem de CIs.

### Módulo C — Memória principal

| CI | Quantidade | Função |
|---|---:|---|
| AT28C256 | 1 | ROM física de 32 KiB, usando janela de 16 KiB |
| 62256 SRAM | 1 | RAM de 32 KiB |
| 74HC138 | 1 | Seleção de regiões |
| 74HC00 | 1 | Habilitação e escrita |
| 74HC245 | 1 | Isolamento de barramento |
| **Subtotal** | **5** | |

A EEPROM AT28C256 tem capacidade maior que a região ROM definida. Podemos usar apenas metade dela inicialmente, deixando o restante para futuras configurações de banco.

### Módulo D — Controlador de vídeo

| CI | Quantidade | Função |
|---|---:|---|
| 6116 SRAM | 1 | VRAM de 2 KiB |
| AT28C64B | 1 | ROM de caracteres |
| 74HC4040 | 2 | Contadores horizontal e vertical |
| 74HC161 | 3 | Contadores auxiliares |
| 74HC166 | 1 | Serialização de pixels |
| 74HC157 | 4 | Seleção de endereços |
| 74HC153 | 2 | Seleção de sinais |
| 74HC85 | 3 | Comparação de contadores |
| 74HC00 | 3 | Lógica de sincronismo |
| 74HC08 | 2 | Máscaras e habilitação |
| 74HC74 | 2 | Sincronização |
| 74HC245 | 1 | Isolamento |
| **Subtotal** | **25** | |

Este é o módulo mais sujeito a revisão. Precisamos comprovar que a leitura da VRAM, o acesso à fonte e o carregamento do registrador de pixels cabem nos ciclos disponíveis.

Também faltam nessa tabela o oscilador e os componentes analógicos de saída, que entram no módulo de clock e interfaces.

### Módulo E — Teclado PS/2 e entrada/saída

| CI | Quantidade | Função |
|---|---:|---|
| 74HC165 | 2 | Captura serial |
| 74HC393 | 1 | Contagem de bits |
| 74HC74 | 2 | Sincronização e estado |
| 74HC00 | 2 | Controle |
| 74HC244 | 1 | Buffer de leitura |
| 74HC574 | 1 | Saída para LEDs |
| 74HC138 | 1 | Decodificação |
| **Subtotal** | **10** | |

A interface PS/2 será inicialmente somente de recepção, com o teclado interpretado por software. Para suportar comandos enviados ao teclado e maior compatibilidade, precisaremos expandir a interface.

### Módulo F — Clock, reset e suporte

| CI | Quantidade | Função |
|---|---:|---|
| 74HC14 | 2 | Condicionamento e reset |
| 74HC74 | 1 | Divisão e controle de clock |
| 74HC00 | 1 | Lógica de habilitação |
| 74HC123 | 1 | Temporização auxiliar |
| 74HC245 | 1 | Buffer auxiliar |
| **Subtotal** | **6** | |

Além desses chips, teremos osciladores, reguladores, transistores, resistores, capacitores e conectores.

### Consolidado

| Módulo | CIs |
|---|---:|
| CPU e ULA | 33 |
| Controle | 13 |
| Memória | 5 |
| Vídeo | 25 |
| Teclado e I/O | 10 |
| Clock e suporte | 6 |
| **Total preliminar** | **92 CIs** |

Esse total não inclui osciladores encapsulados, reguladores ou eventuais circuitos adicionais que a validação exigir.

**Portanto, 92 é nossa contagem de referência para a revisão 0.1, não uma quantidade exata já comprovada.**

## 8. Materiais complementares

Além dos CIs, a montagem precisará destes componentes:

| Material | Quantidade planejada |
|---|---:|
| Soquetes DIP compatíveis | 92 |
| Capacitores cerâmicos 100 nF | 110 |
| Capacitores de filtragem 10–100 µF | 15 |
| Resistores diversos | 150 |
| LEDs de diagnóstico | 24 |
| Botões de pressão | 4 |
| Oscilador 14,31818 MHz | 1 |
| Oscilador de CPU de 1 MHz | 1 |
| Conector RCA fêmea | 1 |
| Conector PS/2 Mini-DIN 6 | 1 |
| Conector DC de alimentação | 1 |
| Conectores de expansão | 4 conjuntos |
| Fonte externa 12 V | 1 |
| Conversor DC-DC 12 V → 5 V | 1 |
| Monitor automotivo CVBS | 1 |
| Teclado PS/2 | 1 |

A fonte e o conversor precisam ser escolhidos após calcularmos a corrente máxima. Também adicionaremos proteção de entrada, pontos de teste e planos de terra.

### Organização física

Eu dividiria a placa em quatro módulos interligados:

<grid columns={2} gap={2}>
  {#each [{n:"Placa 1",t:"CPU + ULA",s:"33 CIs"},{n:"Placa 2",t:"Controle + ROM/RAM",s:"18 CIs"},{n:"Placa 3",t:"Vídeo CVBS",s:"25 CIs"},{n:"Placa 4",t:"Teclado + suporte",s:"16 CIs"}] as p}
    <grid-item>
      <box border radius="lg" padding={3} gap={1}>
        <text color="secondary" size="xs">{p.n}</text>
        <text weight="medium">{p.t}</text>
        <title size="lg" tabularNums>{p.s}</title>
      </box>
    </grid-item>
  {/each}
</grid>

Os cabos entre placas não devem transportar indiscriminadamente todos os sinais de alta frequência. Principalmente no módulo de vídeo, será importante manter os sinais rápidos próximos e usar uma interconexão curta com aterramento adequado.

## 9. O que ainda precisamos validar

Antes de comprar os componentes, existem cinco pontos de engenharia que considero obrigatórios:

- **CPU:** desenhar todos os caminhos entre registradores, ULA, PC, MAR e barramentos, confirmando que nenhuma instrução exige uma conexão inexistente.
- **Microcódigo:** definir os sinais de controle e verificar se as três EEPROMs conseguem implementar a sequência completa de instruções.
- **Vídeo:** calcular as temporizações horizontais e verticais, os endereços de caracteres e o tempo disponível para cada acesso à VRAM.
- **Arbitragem:** garantir que CPU e vídeo não disputem a memória e que o sinal `WAIT` não interrompa operações em estados inválidos.
- **Elétrica:** confirmar tensões, fan-out, atrasos de propagação, níveis CVBS e consumo total.

A contagem atual de 92 CIs pode aumentar ou diminuir depois dessas verificações. Não recomendo fazer uma compra grande com base somente nesta revisão.

## 10. Próximo passo: transformar a arquitetura em circuito

Agora já temos uma especificação de máquina, um mapa de memória, uma proposta de conjunto de instruções, uma estrutura de vídeo e uma BOM preliminar.

O próximo passo mais útil é **fechar o esquema elétrico da CPU antes de avançar para o vídeo**.

Eu começaria por um circuito completo contendo registradores A e B, ULA de 8 bits, flags, barramento interno e sinais de controle. Desenharíamos as ligações pino a pino e simularíamos operações como `LDI`, `ADD` e `SUB`.

Quando esse primeiro módulo estiver validado, poderemos congelar sua lista exata de componentes e seguir para o contador de programa, a memória e o microcódigo.

Assim, construiremos um computador próprio de verdade, mas com cada parte testada antes de gastar dinheiro com a placa definitiva.

## user — bbb21755-eb62-48ab-9dc7-12198ebdc7d1

Ok
Li tudo e estou gostando do caminho que estamos seguindo
Vejo que a lista de itens é grande
Será um projeto complexo 
Temos que ver, não se vale a pena, pois é ganho de um conhecimento que eu particularmente gosto
Mas precisamos de algo que seja viável
E eu possa ir fazendo tranquilo aí longo de dias
Temos que validar tudo certinho e até ver alternativas
Sei que um Apple 1 não foi feito assim, até já vi projetos com processadores desses antigos, nas eles são caros e difíceis de achar
Um CI desse 74x eh fácil e barato
Mas será um projeto grande

## assistant — 56c96e2f-011a-4ba0-9463-9e7a5cf6e0e2

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — 24763e6b-d1f1-494f-8851-59785dee38c2

Concordo com a direção que você está propondo. E acho que chegamos a uma decisão importante para o projeto: **não precisamos construir o computador mais completo possível. Precisamos construir um computador que seja possível terminar, entender e melhorar ao longo do tempo.**

O objetivo não é apenas ter uma máquina funcionando. É entender como ela funciona, desde as portas lógicas até o programa aparecendo na tela.

E existe uma diferença enorme entre um projeto de 90 CIs e um de 30 ou 40 CIs. Não apenas pelo preço dos componentes, mas pela quantidade de conexões, pontos de falha, consumo, espaço e dificuldade de manutenção.

Eu não abandonaria a ideia de uma CPU própria. Mas revisaria a arquitetura antes de comprar qualquer coisa.

## 1. Podemos reduzir bastante a complexidade

Nossa primeira arquitetura tinha aproximadamente 92 CIs. Ela incluía uma CPU relativamente completa, memória, vídeo, teclado e várias possibilidades de expansão.

Mas podemos pensar em três versões:

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3} width="76px" align="center" gap={1}>
      <title size="xl" tabularNums>15–25</title>
      <text color="secondary" size="3xs">CIs</text>
    </box>
    <box flex="1" gap={1}>
      **Computador mínimo**

      CPU de 8 bits com instruções simples, pouca RAM e LEDs como saída. Sem teclado ou vídeo inicialmente.

      Ótimo para aprender, mas ainda distante de um computador pessoal.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3} width="76px" align="center" gap={1}>
      <title size="xl" tabularNums>30–50</title>
      <text color="secondary" size="3xs">CIs</text>
    </box>
    <box flex="1" gap={1}>
      **Computador compacto de 8 bits**

      CPU própria, RAM, ROM, programas e entrada/saída. Vídeo e teclado adicionados de forma modular ou com circuitos especializados.

      É o caminho que eu investigaria primeiro.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3} width="76px" align="center" gap={1}>
      <title size="xl" tabularNums>70–100+</title>
      <text color="secondary" size="3xs">CIs</text>
    </box>
    <box flex="1" gap={1}>
      **Computador completo em lógica discreta**

      CPU, controlador de vídeo e interfaces construídos majoritariamente com chips 74HC.

      É fascinante, mas exige muito mais tempo para montagem e depuração.
    </box>
  </row>
</box>

Essas faixas são metas de complexidade, não contagens validadas. Para saber se conseguimos realmente ficar abaixo de 50 CIs, precisamos redesenhar e simular a arquitetura.

## 2. Uma alternativa que considero especialmente interessante

Em vez de construir uma CPU relativamente sofisticada, podemos criar uma **CPU de 8 bits minimalista**, com poucas instruções, mas suficiente para executar programas reais.

Por exemplo, usar uma arquitetura com:

- Um acumulador de 8 bits.
- Uma ULA compartilhada para soma, subtração e lógica.
- Um contador de programa de 16 bits.
- Um registrador de endereço.
- Controle microprogramado simples.
- RAM e EEPROM externas.

Podemos até considerar uma arquitetura de instruções acumuladoras, como a dos computadores educacionais clássicos, ou uma CPU de instruções extremamente reduzidas.

O interessante é que uma CPU com poucas instruções ainda pode executar programas complexos, desde que possua operações de memória, aritmética e desvios condicionais.

Não precisamos implementar 30 instruções para ter um computador útil.

## 3. Também podemos simplificar a tela

Aqui está uma das maiores oportunidades de redução.

Na arquitetura anterior, tínhamos reservado 25 CIs somente para vídeo.

Mas existem alternativas:

| Solução | Vantagem | Desvantagem |
|---|---|---|
| Vídeo composto feito com 74HC | Aprendizado completo | Muitos circuitos e temporização exigente |
| Controlador de vídeo dedicado | Menos componentes externos | Disponibilidade e compatibilidade |
| LCD de caracteres | Muito simples | Não gera imagem para TV |
| Módulo de vídeo independente | Permite evoluir separadamente | Precisa de interface bem definida |

Minha preferência seria **manter a CPU totalmente construída por nós e tratar o vídeo como um módulo independente**.

Assim, podemos começar com LEDs, depois colocar um LCD de caracteres e, finalmente, adicionar nosso gerador de vídeo composto.

Nenhuma dessas etapas exige jogar fora o trabalho anterior.

## 4. Como tornar o desenvolvimento tranquilo

Eu criaria pequenos módulos com objetivos bem definidos.

<box gap={3}>
  {#each [{n:"1",t:"Clock e registrador",d:"Montar um circuito que armazena e mostra 8 bits em LEDs.",result:"Primeiro circuito funcionando"},{n:"2",t:"ULA de 8 bits",d:"Adicionar operações matemáticas e lógicas, controladas por chaves.",result:"Primeira calculadora binária"},{n:"3",t:"Controle e contador de programa",d:"Fazer o circuito buscar e executar instruções automaticamente.",result:"Primeira CPU funcional"},{n:"4",t:"RAM e EEPROM",d:"Executar programas armazenados e manipular variáveis.",result:"Computador programável"},{n:"5",t:"Teclado e vídeo",d:"Adicionar entrada de comandos e saída para o monitor.",result:"Computador pessoal de 8 bits"}] as a}
    <row align="start" gap={3}>
      <box background="surface-secondary" radius="lg" size="38px" align="center" justify="center">
        <text weight="semibold">{a.n}</text>
      </box>
      <box flex="1" gap={1}>
        <text weight="medium">{a.t}</text>
        <text color="secondary" size="sm">{a.d}</text>
        <row align="center" gap={1}>
          <icon name="check-circle-2" color="success" size="xs"/>
          <text size="xs" color="secondary">{a.result}</text>
        </row>
      </box>
    </row>
  {/each}
</box>

Cada etapa deve ter seu próprio esquema elétrico, lista de materiais, procedimento de teste e critérios objetivos de funcionamento.

Isso é especialmente importante porque você quer desenvolver o projeto ao longo de vários dias, sem precisar deixar uma montagem enorme e frágil ocupando a bancada.

## 5. O que eu mudaria na nossa estratégia

Acredito que devemos estabelecer algumas regras:

**Regra 1 — Nada de comprar 90 CIs antecipadamente.** Primeiro simulamos a CPU e verificamos quais componentes são realmente necessários.

**Regra 2 — Evitar componentes raros.** Dar preferência a chips 74HC comuns, SRAM e EEPROM ainda encontradas no mercado. Também precisamos verificar a disponibilidade de cada componente específico, porque nem todo 74HC é igualmente fácil de comprar.

**Regra 3 — Cada módulo precisa funcionar isoladamente.** Isso facilita muito identificar problemas.

**Regra 4 — Não exigir 1 MHz logo no início.** Um clock manual ou de poucos hertz permite acompanhar as operações pelos LEDs. A velocidade aumenta depois que o circuito estiver estável.

**Regra 5 — Projetar para manutenção.** Usar soquetes, conectores identificados, pontos de teste e documentação.

## 6. Minha proposta para a próxima revisão

Em vez de continuar desenvolvendo a arquitetura de 92 CIs, eu faria um estudo comparativo de duas CPUs:

<box border radius="xl" padding={3} gap={3}>
  <box gap={1}>
    <text weight="medium">Arquitetura A — CPU acumuladora de 8 bits</text>
    <text color="secondary" size="sm">Mais tradicional, fácil de entender e programar em Assembly. Provavelmente exigirá mais registradores e lógica de controle.</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    <text weight="medium">Arquitetura B — CPU minimalista de 8 bits</text>
    <text color="secondary" size="sm">Menos instruções e circuitos, potencialmente muito mais compacta. Em contrapartida, alguns programas exigirão mais instruções e memória.</text>
  </box>
</box>

Compararíamos as duas usando os mesmos programas de teste: somar números, executar um laço, manipular RAM e escrever caracteres em uma porta de saída.

A vencedora não seria necessariamente a que tem menos CIs, mas a que oferece o melhor equilíbrio entre simplicidade, capacidade e facilidade de montagem.

**Eu manteria nossa meta de construir uma CPU própria de 8 bits com chips 74HC, mas tentaria reduzir o computador básico para algo na faixa de 20 a 35 CIs**, sem contar inicialmente o módulo de vídeo. É uma meta a verificar, não uma promessa.

Acho que essa é a melhor próxima etapa: antes de desenhar placas ou comprar componentes, comparar essas duas arquiteturas em nível de registradores, barramentos e microoperações, e descobrir qual realmente conseguimos construir com menos complexidade.

## user — bbb216f0-b12e-4fa8-95ab-e01ecf819494

Eu quero realmente um PC 
Com teclado
E um vídeo de verdade, mesmo sendo monocromático
A ideia de acender led ou um desses LCD verde já fiz de outros jeitos
A ideia de um PC "completo" e do zero me é mais prazeroso de fazer


## assistant — 56cb68d5-10b8-42c6-9479-f044c454e57a

Agora ficou claro o que queremos construir: **um computador pessoal de verdade, com CPU própria, teclado, memória, vídeo e capacidade de executar programas.** Não apenas uma CPU didática com LEDs.

E acho perfeitamente possível manter esse objetivo sem transformar o projeto em algo inviável.

<AsyncImageGroup query={["homebrew 8 bit computer custom PCB keyboard small CRT monitor retro","1970s homebrew computer terminal green monochrome screen keyboard circuit board"]} aspectRatio="5:3"/>

## O computador que vamos construir

Eu manteria estes requisitos como definitivos:

| Componente | Nossa escolha |
|---|---|
| CPU | 8 bits, construída com lógica 74HC |
| Memória | RAM + ROM/EEPROM |
| Vídeo | Composto monocromático real |
| Monitor | Tela automotiva de câmera de ré |
| Teclado | PS/2, com interface própria |
| Programação | Assembly próprio |
| Sistema | Monitor de máquina em ROM |
| Expansão | Barramento para periféricos |
| Mouse | Opcional, posteriormente |
| Microcontrolador | Nenhum na operação do computador |

O computador deverá ligar, inicializar e mostrar um prompt na tela. Você poderá digitar comandos, examinar a memória, carregar programas e executá-los.

Por exemplo, nossa meta seria algo assim:

<box background="#151a17" theme="dark" radius="xl" padding={3} gap={2}>
  <box border={{size:3,color:"#525a55"}} radius="lg" padding={3} background="#06120a">
    <svg viewBox="0 0 320 194" width="100%">
      <defs>
        <pattern id="scanpc" width="3" height="3" patternUnits="userSpaceOnUse">
          <path d="M0 2.5 H320" stroke="#000" strokeOpacity=".3"/>
        </pattern>
      </defs>
      <rect width="320" height="194" fill="#06120a"/>
      {#each ["TTL-8 PERSONAL COMPUTER","8-BIT HOME COMPUTER","ROM MONITOR V1.0","","32768 BYTES RAM","VIDEO 32 X 24","KEYBOARD READY","","> HELP","DUMP  EDIT  RUN  LOAD","SAVE  RESET  INFO","","> DUMP 4000","4000: 10 05 20 03 12 10 E0 FF","","> RUN 4000","PROGRAM FINISHED","","> _"] as line,i}
        <text x="10" y={12+i*9.6} fill="#8affab" fontSize="9.5" fontFamily="monospace" xmlSpace="preserve">{line}</text>
      {/each}
      <rect width="320" height="194" fill="url(#scanpc)"/>
    </svg>
  </box>
  <caption color="secondary" textAlign="center">Conceito da interface de inicialização do nosso computador.</caption>
</box>

## Onde devemos economizar complexidade?

Não na funcionalidade do computador. Devemos economizar **na arquitetura eletrônica**.

Existem três decisões que podem fazer uma grande diferença.

### 1. CPU simples, mas completa

Uma CPU acumuladora de 8 bits, com endereçamento de 16 bits, instruções de carga, armazenamento, aritmética, comparação e saltos condicionais.

Não precisamos de uma CPU rápida ou sofisticada. Precisamos que ela seja capaz de executar programas gerais, incluindo um monitor de máquina e rotinas de teclado e vídeo.

### 2. Vídeo independente da CPU

Este é provavelmente o ponto mais importante.

A CPU escreverá caracteres na memória de vídeo. Um circuito independente, também construído com lógica digital, transformará esses caracteres em um sinal de vídeo composto.

Isso permite uma tela real, com texto atualizado enquanto o computador executa programas.

Podemos simplificar o gerador usando vídeo monocromático e uma fonte fixa de caracteres. Não precisamos implementar cores, sprites ou gráficos avançados na primeira versão.

### 3. Teclado PS/2

O teclado PS/2 evita construir uma matriz de dezenas de teclas e sua estrutura mecânica.

Nossa placa receberá os códigos das teclas, e o firmware em ROM converterá esses códigos em caracteres.

Não há necessidade de um controlador USB complexo.

## Uma arquitetura que considero promissora

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 265" width="100%">
    <g fill="currentColor" textAnchor="middle">
      <rect x="91" y="8" width="158" height="49" rx="6" stroke="#60a5fa" fill="#3b82f6" fillOpacity=".13"/>
      <text x="170" y="27" fontSize="13" fontWeight="600">CPU 8 bits</text>
      <text x="170" y="43" fontSize="10">74HC + microcódigo</text>
      <path d="M170 57 V80" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="13" y="80" width="314" height="30" rx="5" fill="#64748b" fillOpacity=".15" stroke="#94a3b8"/>
      <text x="170" y="99" fontSize="11">Barramento de 8 bits / endereços de 16 bits</text>
      {#each [{x:8,t:"ROM",s:"Sistema"},{x:91,t:"RAM",s:"Programas"},{x:174,t:"VRAM",s:"Tela"},{x:257,t:"PS/2",s:"Teclado"}] as a}
        <path d={`M${a.x+37} 110 V130`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={a.x} y="130" width="75" height="44" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+37} y="148" fontSize="11" fontWeight="600">{a.t}</text>
        <text x={a.x+37} y="163" fontSize="9">{a.s}</text>
      {/each}
      <path d="M211 174 V195" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="141" y="195" width="140" height="35" rx="5" fill="#16a34a" fillOpacity=".12" stroke="#4ade80"/>
      <text x="211" y="216" fontSize="11" fontWeight="600">Gerador CVBS</text>
      <path d="M211 230 V245" stroke="#94a3b8" strokeWidth="1.5"/>
      <text x="211" y="259" fontSize="10">Monitor automotivo</text>
    </g>
  </svg>
</box>

Eu investigaria uma CPU com **controle microprogramado e poucos registradores**, usando chips 74HC para a lógica e EEPROMs para o microcódigo.

Isso continua sendo uma CPU construída por nós: somos nós que definimos as instruções, os registradores, os sinais de controle e a arquitetura. As EEPROMs apenas armazenam a lógica de sequenciamento.

## Como eu organizaria o projeto

Em vez de tratar a máquina como uma montagem gigantesca, dividiria em três placas:

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3}>
      <icon name="cpu" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Placa principal — CPU, RAM e ROM**

      O computador propriamente dito. Responsável por executar programas, administrar memória e controlar periféricos.
    </box>
  </row>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3}>
      <icon name="monitor" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Placa de vídeo — CVBS monocromático**

      Gera a imagem para o monitor de câmera de ré. Podemos desenvolvê-la e testá-la independentemente da CPU.
    </box>
  </row>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={3}>
      <icon name="keyboard" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **Placa de entrada/saída — teclado e expansão**

      Recebe o teclado PS/2 e disponibiliza conexões para periféricos futuros.
    </box>
  </row>
</box>

Isso permite trabalhar tranquilamente ao longo de dias ou meses, sem perder a visão do computador completo.

## Minha proposta de compromisso

Não vamos reduzir nosso computador a uma experiência com LEDs. Vamos manter o objetivo de uma máquina completa, mas simplificar o que acontece *dentro* dela.

Também não precisamos construir todas as placas simultaneamente. Podemos começar pelo vídeo, que já produzirá uma imagem real no monitor, enquanto desenvolvemos a CPU em paralelo na simulação.

**O próximo passo que eu faria é uma revisão arquitetural focada em redução de CIs**, comparando diferentes formas de construir a CPU e o controlador de vídeo, sem retirar teclado, RAM, ROM ou saída CVBS.

Quero chegar a um esquema no qual possamos dizer exatamente: estes são os componentes, estas são as conexões, estes são os testes e este é o computador que construiremos.

## user — bbb21dfc-d166-4866-87ec-60cf225a3fb8

Até sobre o teclado, não sei como está pra achar um PS2, temos alguma alternativa? Não me importo de chavear 8 chaves e apertar um botão pra "enviar"
Como seria uma maneira simples? 
Mas vamos tentar ter um teclado 

## assistant — 5e5b5745-849f-4314-9a94-f8539c7e972d

{"content_type": "thoughts", "source_analysis_msg_id": "8096c7d3-44f9-43e1-aec5-79467035ee89", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 8 sites"}]}

## assistant — 5a84d53a-1957-4601-a833-e724ba2f104b

{"content": "Pensou por 12s", "content_type": "reasoning_recap"}

## assistant — 0f8966dd-ff04-42e3-b92b-dac53040897c

A ideia das **8 chaves e um botão de enviar é excelente** para nosso computador. Na verdade, ela resolve um problema importante: como controlar e programar a máquina antes mesmo de termos um teclado funcionando.

Mas eu faria algo ainda melhor: **nosso computador teria dois métodos de entrada**, e ambos poderiam continuar existindo na versão definitiva.

1. **Painel de 8 chaves:** permite inserir qualquer byte, diretamente em binário, e controlar o computador mesmo sem teclado.
2. **Teclado convencional:** permite escrever comandos, programas e textos normalmente.

Isso combina muito com os primeiros microcomputadores, que frequentemente tinham painéis de controle para examinar e modificar a memória.

## 1. O painel de 8 chaves

<box border radius="xl" padding={3} gap={3}>
  <text weight="medium">Simulação do painel de entrada</text>
  {@body const [bits,setBits]=DIL.useState([0,1,0,0,0,0,0,1])}
  {@body const [sent,setSent]=DIL.useState(null)}
  {@body const val=bits.reduce((a,b)=>a*2+b,0)}
  <row gap={1}>
    {#each bits as b,i}
      <box flex="1" gap={2} align="center">
        <text color="secondary" size="2xs">D{7-i}</text>
        <pressable onClick={()=>setBits(old=>old.map((v,j)=>j===i?1-v:v))} background={b?"#166534":"surface-tertiary"} border={{size:1,color:b?"#22c55e":"default"}} radius="md" width="100%" height="57px" align="center" justify="center">
          <icon name={b?"toggle-right":"toggle-left"} color={b?"#ffffff":"secondary"} size="xl"/>
        </pressable>
        <text weight="medium" tabularNums>{b}</text>
      </box>
    {/each}
  </row>
  <grid columns={3} gap={2}>
    <grid-item>
      <box background="surface-secondary" padding={2} radius="md" gap={1}>
        <text color="secondary" size="2xs">Binário</text>
        <text weight="medium" tabularNums>{bits.join("")}</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface-secondary" padding={2} radius="md" gap={1}>
        <text color="secondary" size="2xs">Hexadecimal</text>
        <text weight="medium" tabularNums>{val.toString(16).toUpperCase().padStart(2,"0")}</text>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface-secondary" padding={2} radius="md" gap={1}>
        <text color="secondary" size="2xs">Decimal</text>
        <text weight="medium" tabularNums>{val}</text>
      </box>
    </grid-item>
  </grid>
  <button block onClick={()=>setSent(val)}><icon name="send"/> Enviar byte</button>
  {#if sent!==null}
    <row align="center" gap={2}>
      <icon name="check-circle" color="success"/>
      <text size="sm">Byte enviado ao registrador: 0x{sent.toString(16).toUpperCase().padStart(2,"0")}</text>
    </row>
  {/if}
  <caption>Experimente mudar as chaves e pressionar Enviar. No hardware, um registrador capturaria o byte.</caption>
</box>

### Como implementar fisicamente?

Para um painel mínimo:

| Componente | Quantidade |
|---|---:|
| Chaves liga/desliga SPDT | 8 |
| Botão de envio | 1 |
| 74HC574, registrador de 8 bits | 1 |
| 74HC14, inversores Schmitt | 1 |
| Resistores de pull-up/pull-down | Conforme ligação |
| Capacitores de desacoplamento | 2 |

O 74HC574 armazenaria os oito bits quando o botão fosse pressionado. O 74HC14 ajudaria a eliminar o efeito de *bounce* do botão, usando uma rede de debounce apropriada.

Precisaríamos ainda de um sinal `DATA_READY` e de uma forma de a CPU reconhecer a leitura. Isso pode ser feito por polling, sem interrupções.

O painel também poderia ser usado para carregar programas diretamente na RAM, caso implementemos um modo de depósito de memória.

## 2. Ainda conseguimos comprar teclado PS/2?

Sim! Pesquisei opções no Brasil e encontrei teclados PS/2 novos e usados. Não precisamos desistir dessa interface.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage ref="turn162190product6" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn162190product6" value={turn162190product6.title}/>**
      <title size="lg">{turn162190product6.displayed_price}</title>
      <text color="secondary" size="xs">{turn162190product6.merchant}</text>
      Uma opção econômica para verificar antes de comprar.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn162190product30" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn162190product30" value={turn162190product30.title}/>**
      <title size="lg">{turn162190product30.displayed_price}</title>
      <text color="secondary" size="xs">{turn162190product30.merchant}</text>
      Modelo ABNT2, com conector PS/2.
    </box>
  </row>
</box>

Também encontrei um teclado Genius PS/2 ABNT2 anunciado por R$ 44 na Atera. <Cite ref="turn162190search7"/> Os valores e estoques podem mudar.

## 3. Outra possibilidade: teclado matricial próprio

Podemos construir um teclado com, por exemplo, 48 teclas organizadas em 6 linhas × 8 colunas.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Exemplo de disposição de teclas</text>
  <grid columns={10} gap="3px">
    {#each ["1","2","3","4","5","6","7","8","9","0","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","↵","⇧","Z","X","C","V","B","N","M","⌫","↑","CTRL","ALT","←","↓","→","SPACE","SPACE","SPACE",".","/"] as key,i}
      <grid-item>
        <box border radius="2xs" background="surface-secondary" minHeight="25px" align="center" justify="center">
          <text size="3xs" weight="medium">{key}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Layout apenas ilustrativo; poderíamos desenhar uma matriz física própria com a quantidade de teclas desejada.</caption>
</box>

O circuito usaria um contador e um decodificador para selecionar as linhas, enquanto buffers leriam as colunas. O software converteria a posição pressionada em caracteres.

Isso elimina a dependência de um teclado PS/2, mas aumenta bastante o trabalho mecânico e a necessidade de tratar teclas simultâneas e debounce.

Uma alternativa intermediária seria começar com um teclado hexadecimal de 16 teclas, que também pode ser usado para inserir programas.

<row gap={3} align="start">
  <AsyncImage ref="turn162190product7" aspectRatio="1:1" maxWidth="104px"/>
  <box flex="1" gap={1}>
    **<Entity ref="turn162190product7" value={turn162190product7.title}/>**
    <title size="lg">{turn162190product7.displayed_price}</title>
    <text color="secondary" size="xs">{turn162190product7.merchant}</text>
    Seria uma opção compacta para comandos e entrada hexadecimal.
  </box>
</row>

## 4. Como eu deixaria nosso computador

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 240" width="100%">
    <g fill="currentColor" textAnchor="middle">
      <rect x="104" y="7" width="132" height="40" rx="6" stroke="#60a5fa" fill="#3b82f6" fillOpacity=".12"/>
      <text x="170" y="24" fontSize="12" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="37" fontSize="9">Barramento de dados</text>
      <path d="M170 47 V73 H75 V92 M170 73 H265 V92" fill="none" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="8" y="92" width="134" height="51" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="75" y="112" fontSize="11" fontWeight="600">Entrada manual</text>
      <text x="75" y="127" fontSize="9">8 chaves + ENTER</text>
      <rect x="198" y="92" width="134" height="51" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="265" y="112" fontSize="11" fontWeight="600">Teclado PS/2</text>
      <text x="265" y="127" fontSize="9">Clock + Data</text>
      <path d="M170 47 V174" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="4 3"/>
      <rect x="96" y="174" width="148" height="49" rx="6" stroke="#4ade80" fill="#16a34a" fillOpacity=".1"/>
      <text x="170" y="192" fontSize="11" fontWeight="600">Vídeo composto</text>
      <text x="170" y="207" fontSize="9">Monitor de câmera de ré</text>
    </g>
  </svg>
  <caption textAlign="center">Dois métodos de entrada independentes, uma CPU e um sistema de vídeo real.</caption>
</box>

Minha escolha seria manter **as 8 chaves como painel de manutenção e programação**, e adotar o **PS/2 como teclado principal**. Assim não dependemos do teclado para testar ou recuperar o computador, mas continuamos tendo uma experiência completa de PC.

O próximo detalhe que vale fechar é o painel frontal: além das oito chaves, eu colocaria botões `DEPOSIT`, `EXAMINE`, `RUN` e `RESET`. Com eles, poderíamos inserir bytes na RAM, consultar endereços e iniciar programas — sem precisar que o monitor de sistema esteja funcionando ainda.

## user — bbb21117-f83e-42d6-94d6-2630039f3ec5

Pensando aqui, lembro de já abrir teclados antigos e ele ter na membrana várias linhas saindo e chegando a uma placa
Meio que eh a ligação das 8 entradas dessas Chaves certo? 

## assistant — b6ea454e-104a-4d93-ad90-b1b74ebe61a8

**Exatamente!** Você está lembrando de uma **matriz de teclado**, e ela pode ser uma ótima solução para nosso computador de 8 bits.

A ideia é muito parecida com as oito chaves que discutimos, mas existe uma diferença: em vez de cada tecla ter seu próprio fio, várias teclas compartilham linhas e colunas.

## Como funciona a membrana de um teclado?

<AsyncImageGroup query={["computer keyboard membrane circuit transparent sheets row column traces","old computer keyboard membrane ribbon cable connector PCB controller"]} aspectRatio="5:3"/>

Aquelas trilhas que você viu na membrana formam uma matriz elétrica. Quando pressionamos uma tecla, ela conecta uma linha a uma coluna.

Por exemplo, podemos ter um teclado de 64 teclas usando apenas **16 fios: 8 linhas e 8 colunas**.

## Veja como funcionaria

Nesta simulação, selecione uma tecla. O circuito identifica a linha e a coluna conectadas.

{@body const keys=[["1","2","3","4"],["Q","W","E","R"],["A","S","D","F"],["Z","X","C","V"]]}
{@body const [selected,setSelected]=DIL.useState([1,2])}
<box border radius="xl" padding={3} gap={3}>
  <text weight="medium">Matriz simplificada de 4 × 4</text>
  <grid columns={5} gap="5px">
    <grid-item><box/></grid-item>
    {#each [0,1,2,3] as c}
      <grid-item><text color={selected[1]===c?"success":"secondary"} size="xs" textAlign="center">C{c}</text></grid-item>
    {/each}
    {#each keys as row,r}
      <grid-item>
        <box height="42px" justify="center"><text size="xs" color={selected[0]===r?"success":"secondary"}>L{r}</text></box>
      </grid-item>
      {#each row as key,c}
        <grid-item>
          <pressable onClick={()=>setSelected([r,c])} height="42px" align="center" justify="center" radius="md" background={selected[0]===r&&selected[1]===c?"#166534":"surface-secondary"} border={{size:1,color:selected[0]===r&&selected[1]===c?"#22c55e":"default"}}>
            <text color={selected[0]===r&&selected[1]===c?"#ffffff":"default"} weight="medium">{key}</text>
          </pressable>
        </grid-item>
      {/each}
    {/each}
  </grid>
  <box background="surface-secondary" padding={3} radius="lg" gap={1}>
    <text color="secondary" size="xs">Conexão detectada</text>
    <row align="center" justify="between">
      <title size="lg">Linha {selected[0]} + Coluna {selected[1]}</title>
      <badge color="success">Tecla {keys[selected[0]][selected[1]]}</badge>
    </row>
  </box>
</box>

## Como nosso computador leria isso?

Poderíamos usar uma matriz de 8 × 8 teclas, conectada a circuitos 74HC.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 215" width="100%">
    <g fill="currentColor" textAnchor="middle">
      <rect x="9" y="13" width="142" height="63" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="80" y="35" fontSize="12" fontWeight="600">Matriz 8 × 8</text>
      <text x="80" y="51" fontSize="10">64 teclas</text>
      <text x="80" y="65" fontSize="9">8 linhas + 8 colunas</text>
      <rect x="189" y="13" width="142" height="63" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="260" y="35" fontSize="12" fontWeight="600">74HC138</text>
      <text x="260" y="51" fontSize="10">Seleciona uma linha</text>
      <path d="M189 44 H151" stroke="#94a3b8" strokeWidth="2"/>
      <text x="170" y="34" fontSize="9">8</text>
      <path d="M80 76 V108" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="9" y="108" width="142" height="53" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="80" y="129" fontSize="12" fontWeight="600">74HC244</text>
      <text x="80" y="145" fontSize="10">Lê as 8 colunas</text>
      <path d="M80 161 V183 H170" fill="none" stroke="#94a3b8" strokeWidth="2"/>
      <path d="M260 76 V183 H170" fill="none" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="170" y="167" width="160" height="40" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="250" y="184" fontSize="12" fontWeight="600">CPU TTL-8</text>
      <text x="250" y="198" fontSize="9">Varredura por software</text>
    </g>
  </svg>
</box>

A CPU selecionaria uma linha por vez e leria as oito colunas. Repetindo isso rapidamente, identificaria qual tecla está pressionada.

Para uma matriz simples, com resistores de pull-up e varredura feita por software, podemos começar com apenas alguns CIs. Precisamos cuidar do debounce e do efeito *ghosting* quando várias teclas são pressionadas simultaneamente.

## E podemos reaproveitar um teclado antigo!

Essa é a parte interessante: **não precisamos necessariamente comprar um teclado PS/2**.

Podemos pegar um teclado USB antigo, abrir e aproveitar apenas a membrana, as teclas e a estrutura mecânica. A pequena placa controladora USB original seria desconectada, e as trilhas da membrana seriam ligadas diretamente ao nosso circuito de leitura.

Há um detalhe: as membranas comerciais não seguem necessariamente uma matriz regular de 8 × 8. Precisaríamos mapear as trilhas com um multímetro, descobrir quais pares correspondem a cada tecla e adaptar nosso circuito à quantidade real de linhas e colunas.

Isso poderia deixar o computador ainda mais interessante: **CPU própria, controlador de teclado próprio e vídeo próprio**, tudo integrado.

Minha sugestão é investigar essa alternativa antes de escolher PS/2. Se você tiver algum teclado USB antigo ou quebrado, podemos aproveitar sua mecânica e mapear a membrana, sem precisar implementar USB.

## user — bbb211cc-70cf-4b4e-b7d9-82c35ecffa2c

Vamos seguir pensando então
Vídeo já temos bem direcionado como vamos fazer
Cpu ram ROM também
Teclado, vc citou também o de membrana matricial, será que teria um teclado assim, só que mais completo? 

## assistant — 460e082b-5ab8-4412-b80f-df8e7be16885

{"content_type": "thoughts", "source_analysis_msg_id": "93ed3fe4-ae42-4a9f-8dbd-6f3acb8f4ced", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 15 sites"}]}

## assistant — 0908c364-f470-4c8c-9539-b34d64eef910

{"content": "Pensou por 12s", "content_type": "reasoning_recap"}

## assistant — 5441e492-f6d6-4b8d-af10-fe8603029689

Sim! E acho que encontramos uma alternativa muito interessante para nosso computador: **um teclado completo, com 60 a 105 teclas, mas que funcione como uma matriz elétrica simples**, sem USB, PS/2 ou microcontrolador.

O que estamos procurando é essencialmente um **teclado matricial passivo**: teclas, contatos e trilhas elétricas, deixando toda a inteligência de leitura para nosso computador TTL-8.

Existem três caminhos que vale investigar.

## 1. Teclado de membrana completo, reaproveitado

<AsyncImageGroup query={["full size computer keyboard membrane circuit sheets disassembled","computer keyboard rubber dome membrane layers ribbon connector"]} aspectRatio="5:3"/>

É provavelmente a solução mais econômica.

Podemos usar um teclado convencional de 104 teclas, retirar a pequena placa controladora USB e conectar as trilhas da membrana diretamente à nossa placa de entrada.

**Vantagens:** teclado completo, teclas confortáveis, estrutura pronta e nenhum protocolo USB para implementar.

O cuidado é que um teclado de 104 teclas não necessariamente tem uma matriz de 8 × 13. O fabricante pode distribuir as teclas de maneira irregular para reduzir a quantidade de trilhas.

Precisaríamos descobrir o mapeamento elétrico, mas isso é perfeitamente possível com um multímetro.

## 2. Teclado de notebook: outra alternativa

<AsyncImageGroup query={["laptop keyboard removed flat ribbon cable connector underside","laptop keyboard standalone replacement keyboard flat ribbon cable"]} aspectRatio="5:3"/>

Um teclado de notebook pode ser ainda mais interessante, principalmente se quisermos montar o TTL-8 em um gabinete compacto.

Muitos desses teclados são matrizes passivas e possuem um cabo flat que leva as linhas e colunas diretamente ao conector. Há projetos documentados que reaproveitam essas matrizes com controladores próprios. <Cite refs={["turn561578search7","turn561578search10"]}/>

A desvantagem é que o cabo flat costuma exigir um conector FPC específico, e o mapeamento pode ser trabalhoso.

## 3. Teclado mecânico com matriz própria

<AsyncImageGroup query={["DIY mechanical keyboard PCB exposed switch matrix diodes","handwired mechanical keyboard matrix switches wires"]} aspectRatio="5:3"/>

Aqui teríamos liberdade total para criar o teclado do nosso computador.

Podemos projetar uma matriz de 8 linhas × 10 colunas, comportando até 80 teclas. Cada tecla teria um switch mecânico e, preferencialmente, um diodo para evitar teclas fantasmas quando várias forem pressionadas. <Cite ref="turn561578youtube12"/>

É uma solução excelente, mas custa mais e exige construir a parte mecânica.

## 4. O que encontrei disponível

A pesquisa mostrou teclados matriciais prontos de 16 e 20 teclas, mas não encontrei uma opção convincente de teclado QWERTY completo, passivo, já com todas as linhas e colunas expostas.

Por exemplo:

<row align="start" gap={3}>
  <AsyncImage ref="turn561578product12" aspectRatio="1:1" maxWidth="112px"/>
  <box flex="1" gap={1}>
    **<Entity ref="turn561578product12" value={turn561578product12.title}/>**

    <text weight="medium">{turn561578product12.displayed_price}</text>
    <text color="secondary" size="xs">{turn561578product12.merchant}</text>
    É uma matriz passiva de 20 teclas, mas pequena demais para ser nosso teclado principal.
  </box>
</row>

## 5. Como eu integraria um teclado completo ao TTL-8

Usando como exemplo uma matriz de 8 × 16, que comporta até 128 posições:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 206" width="100%">
    {#each [{x:83,y:8,w:164,h:38,t:"Teclado matricial",s:"Até 128 posições"},{x:12,y:79,w:142,h:46,t:"74HC154",s:"Seleciona 1 de 16 colunas"},{x:177,y:79,w:142,h:46,t:"74HC244",s:"Lê 8 linhas"},{x:83,y:160,w:164,h:38,t:"CPU TTL-8",s:"Varredura por software"}] as a}
      <rect x={a.x} y={a.y} width={a.w} height={a.h} rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={a.x+a.w/2} y={a.y+16} fontSize="12" fontWeight="600" textAnchor="middle" fill="currentColor">{a.t}</text>
      <text x={a.x+a.w/2} y={a.y+30} fontSize="9" textAnchor="middle" fill="currentColor">{a.s}</text>
    {/each}
    <g stroke="#94a3b8" strokeWidth="1.6" fill="none">
      <path d="M115 46 V62 H83 V79 M215 46 V62 H248 V79"/>
      <path d="M83 125 V142 H130 V160 M248 125 V142 H200 V160"/>
    </g>
  </svg>
  <caption>Exemplo lógico. Precisaremos de sinais de seleção, resistores de polarização e isolamento adequado para a matriz.</caption>
</box>

Com essa organização, podemos implementar o controlador básico com poucos CIs, e o firmware em ROM cuidaria de Shift, Ctrl, repetição de teclas e conversão para ASCII.

Para um teclado reaproveitado, a quantidade de linhas e colunas poderá ser diferente.

## Minha escolha para o nosso projeto

Eu colocaria as opções nesta ordem:

1. **Reaproveitar um teclado USB de membrana completo**, removendo seu controlador e mapeando a matriz.
2. Usar um teclado de notebook, se quisermos um gabinete compacto.
3. Construir um teclado mecânico próprio, caso desejemos personalizar toda a aparência do computador.

A primeira opção oferece o melhor equilíbrio entre custo, trabalho e funcionalidade. Inclusive, há um projeto documentado de reaproveitamento de uma matriz de teclado IBM com 16 colunas e 8 linhas, exatamente uma configuração que podemos adaptar. <Cite ref="turn561578search3"/>

**Minha sugestão é adotarmos oficialmente uma interface de teclado matricial no TTL-8**, com o número de linhas e colunas configurável dentro dos limites do hardware. Assim, não ficamos presos a PS/2 nem USB e podemos escolher a parte mecânica depois.

O próximo passo seria selecionar um teclado de membrana barato e fácil de desmontar, preferencialmente ABNT2, e verificar se conseguimos acessar sua matriz sem danificá-la.

## user — bbb21abe-8677-4954-a3da-7b70b44fb2da

Quais alternativas mais temos? 

## assistant — b16a770b-d528-4d28-930c-74f523381800

{"content_type": "thoughts", "source_analysis_msg_id": "bc998c70-dd3e-4740-aec3-9439ab7392d0", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — 792ec010-1831-460a-b2b7-a15b1b645cd4

{"content": "Pensou por 7s", "content_type": "reasoning_recap"}

## assistant — a11a8e6f-c708-4040-9c30-0eab3576fbff

Temos várias alternativas! E pensando no nosso TTL-8, eu ampliaria a pesquisa para além dos teclados convencionais.

O que queremos é um **teclado completo, confortável para digitar programas e que não exija implementar USB**. Preferencialmente, algo que possamos conectar diretamente aos CIs 74HC.

Há opções interessantes que ainda não exploramos, incluindo teclados industriais, teclados de computadores antigos e até interfaces seriais muito simples.

## 1. As alternativas de teclado

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="vintage DIN 5 pin AT computer keyboard beige" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **Teclado AT com conector DIN de 5 pinos**

      Usado em PCs antigos. Seu protocolo é muito próximo do PS/2, permitindo aproveitar praticamente o mesmo circuito de recepção.

      É interessante, mas a disponibilidade pode ser pior que a de teclados PS/2.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="laptop replacement keyboard flat ribbon cable detached" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **Teclado de notebook com cabo flat**

      Muitos modelos expõem diretamente a matriz de teclas. São compactos, relativamente finos e podem ser montados no próprio gabinete do TTL-8.

      Precisaremos identificar o conector FPC e mapear as trilhas.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="industrial metal matrix keyboard keypad qwerty panel mount" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **Teclado industrial matricial**

      Alguns modelos disponibilizam linhas e colunas diretamente, sem controlador. São robustos e podem ser fixados em um painel.

      A dificuldade é encontrar modelos QWERTY completos por um preço razoável.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro computer rubber key keyboard ZX Spectrum style keyboard" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **Teclado de computador retrô ou réplica**

      Matrizes inspiradas em computadores como o ZX Spectrum ou Commodore 64 podem ser lidas por lógica digital simples.

      O problema é que muitas peças originais se tornaram itens de coleção, com preços elevados.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="custom 60 percent mechanical keyboard PCB switches without microcontroller" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **PCB de teclado mecânico sem controlador**

      Podemos comprar uma placa de matriz de teclas e utilizar somente os contatos, ignorando ou removendo o controlador, desde que as trilhas estejam acessíveis.

      É uma solução elegante para um gabinete definitivo.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="old electronic typewriter keyboard internal keyboard matrix" aspectRatio="5:4" maxWidth="124px"/>
    <box flex="1" gap={1}>
      **Teclado de máquina de escrever eletrônica**

      Alguns modelos possuem teclados matriciais completos, que podem ser reaproveitados.

      Exige investigar o circuito de cada máquina, mas pode render um teclado com uma aparência muito interessante.
    </box>
  </row>
</box>

## 2. Comparando as alternativas

| Solução | Complexidade eletrônica | Trabalho de adaptação | Teclado completo |
|---|---|---|---|
| Membrana USB reaproveitada | Baixa | Médio | Sim |
| Teclado de notebook | Baixa | Médio/alto | Sim |
| Teclado AT ou PS/2 | Média | Baixo | Sim |
| Teclado industrial passivo | Baixa | Baixo/médio | Depende |
| Teclado mecânico próprio | Baixa na interface | Alto na montagem | Sim |
| Máquina de escrever eletrônica | Variável | Alto | Geralmente |
| Teclado USB com controlador host | Alta | Alto | Sim |

A interface AT/PS/2 é bem documentada, com linhas Clock e Data e comunicação serial síncrona. Isso significa que não precisamos de um processador dedicado para receber as teclas; podemos implementar a recepção com lógica 74HC e interpretar os códigos na nossa CPU. <Cite refs={["turn857143search0","turn857143search1"]}/>

## 3. Existe ainda uma opção que não consideramos

Podemos usar **um teclado matricial de 60%**, com aproximadamente 61 teclas, construído a partir de uma placa de teclado mecânico sem controlador integrado.

Um teclado de 60% tem letras, números, modificadores e teclas de programação, mas ocupa muito menos espaço que um teclado completo.

<AsyncImage query="60 percent mechanical keyboard bare PCB with switches and keycaps compact keyboard" aspectRatio="16:9"/>

O TTL-8 poderia ler a matriz usando um 74HC154 para selecionar até 16 linhas e um 74HC244 para ler até oito colunas, além de lógica de controle e resistores. A varredura seria feita pelo software em ROM. Essa abordagem é consistente com o funcionamento tradicional de matrizes de teclado. <Cite ref="turn857143search26"/>

## 4. O que considero mais interessante para nós

Eu reduziria a escolha a duas soluções:

**Opção A — Reaproveitar um teclado USB de membrana ABNT2.** É a mais econômica e aproveita toda a estrutura de um teclado comum. Precisamos apenas mapear a matriz e construir o circuito de leitura.

**Opção B — Teclado mecânico compacto com matriz própria.** É mais caro, mas podemos definir o formato, as teclas e a aparência. Seria excelente para integrar o teclado ao gabinete do computador.

E manteria as oito chaves binárias como um painel auxiliar para diagnóstico e recuperação, não como teclado principal.

Uma terceira possibilidade seria projetar uma **interface de teclado universal por matriz**, capaz de aceitar diferentes teclados passivos mediante configuração das linhas e colunas. Assim poderíamos escolher a parte física mais tarde, sem redesenhar a CPU.

Minha sugestão para a próxima etapa é comparar uma matriz de teclado de notebook com uma membrana ABNT2 convencional, estimando os conectores e CIs necessários para cada uma. Isso nos ajudará a escolher o teclado que oferece mais funcionalidade com menos trabalho.

## user — bbb212ad-4a76-45bf-9508-e0c378e1e053

Voltando um ponto
Com base na nossa lista de Ci, qual eh o custo deles? Só pra ter uma ideia 

## assistant — cd809ff3-ec1d-46c1-99ba-cde9ab36c513

{"content_type": "thoughts", "source_analysis_msg_id": "c5bbd81c-3f85-4e96-954d-041f297f4a03", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 11 sites"}]}

## assistant — 5908f391-f26c-4d1a-a6c6-4af8b5a894ca

{"content": "Pensou por 9s", "content_type": "reasoning_recap"}

## assistant — d35e1bf9-8fc5-4793-8e2d-dd4e63ee82fd

Fiz uma pesquisa de preços em lojas brasileiras, usando como referência nossa lista preliminar de **92 circuitos integrados** para o TTL-8, incluindo CPU, RAM, ROM, vídeo composto e entrada/saída.

A boa notícia é que os CIs 74HC são relativamente baratos. O que pesa mais são as memórias EEPROM, algumas SRAMs e a quantidade de componentes.

<box gap={1}>
  <text color="secondary" weight="medium" size="xs">Estimativa para os circuitos integrados</text>
  <title size="2xl" color="default">R$ 450–750</title>
  <text color="secondary" size="xs">Orçamento preliminar, sem frete, placas, conectores, monitor ou ferramentas.</text>
</box>

## Preços encontrados

| Componente | Preço de referência |
|---|---:|
| 74HC00 — portas NAND | R$ 2–4 |
| 74HC08 — portas AND | R$ 3–5 |
| 74HC157 — multiplexador | R$ 2–4 |
| 74HC161 — contador | R$ 2–5 |
| 74HC245 — transceptor | R$ 4–6 |
| 74HC574 — registrador | R$ 3–8 |
| 74HC4040 — contador | R$ 1–3 |
| AT28C64B — EEPROM 8 KB | R$ 24–75 |
| AT28C256 — EEPROM 32 KB | R$ 15–35 |
| SRAM 62256 — 32 KB | R$ 7–45 |

Essas faixas vêm de anúncios de lojas como Eletrodex, Copel, Mult Comercial, Achei Componentes e outras. Os preços variam bastante conforme fabricante, encapsulamento e estoque. <Cite refs={["turn432191search8","turn432191search2","turn432191search12","turn432191search6","turn432191search9","turn432191search10"]}/>

Um exemplo interessante: encontrei o 74HC574 por R$ 3,30 na Copel e o 74HC161 por R$ 4,84 na Ca And Ma. Já a EEPROM AT28C64B apareceu por R$ 24 na Mult Comercial e por mais de R$ 70 em outra loja. <Cite refs={["turn432191search2","turn432191search1","turn432191search12","turn432191search5"]}/>

## Quanto custaria cada módulo?

Usando a distribuição de CIs que havíamos proposto:

| Módulo | Quantidade de CIs | Estimativa |
|---|---:|---:|
| CPU e ALU | 33 | R$ 100–170 |
| Microcódigo e controle | 13 | R$ 110–270 |
| RAM, ROM e decodificação | 5 | R$ 35–90 |
| Vídeo composto | 25 | R$ 110–190 |
| Teclado e entrada/saída | 10 | R$ 30–55 |
| Clock, reset e suporte | 6 | R$ 20–40 |
| **Total** | **92** | **R$ 405–805** |

São estimativas de planejamento, não cotações fechadas para cada item.

## E o computador montado?

Além dos CIs, precisaríamos de soquetes, capacitores, resistores, conectores, placas, alimentação e monitor.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Orçamento aproximado do projeto completo</text>
  {@body const costs=[{name:"Circuitos integrados",low:450,high:750},{name:"Soquetes, passivos e conectores",low:120,high:250},{name:"Placas e interligações",low:150,high:400},{name:"Fonte e reguladores",low:40,high:100},{name:"Monitor AV",low:100,high:200}]}
  <box gap={2}>
    {#each costs as c}
      <box gap={1}>
        <row justify="between" align="center">
          <text size="sm">{c.name}</text>
          <text size="xs" color="secondary" tabularNums>R$ {c.low}–{c.high}</text>
        </row>
        <box background="surface-tertiary" height="9px" radius="full" clip>
          <box background="#64748b" width={`${c.high/750*100}%`} height="100%" radius="full"/>
        </box>
      </box>
    {/each}
  </box>
  <divider/>
  <row justify="between" align="center">
    **Total estimado**
    <title size="xl" tabularNums>R$ 860–1.700</title>
  </row>
  <caption>Não inclui ferramentas, gravador de EEPROM, fretes ou possíveis retrabalhos.</caption>
</box>

## O que eu mudaria antes de comprar?

O custo não me parece proibitivo para um projeto construído aos poucos. Mas existe um detalhe importante: **a lista de 92 CIs ainda não foi validada eletricamente**.

Podemos provavelmente reduzir a quantidade de chips, especialmente na CPU e no controlador de vídeo, sem abrir mão do computador completo. Porém, não seria correto prometer uma redução específica antes de fechar os esquemas.

Eu trabalharia com **R$ 1.200 como referência inicial de orçamento**, sabendo que o custo final pode ficar acima ou abaixo disso.

E tem um ponto que vale investigar: as EEPROMs de microcódigo representam uma parcela significativa do custo. Uma arquitetura com menos sinais de controle ou memórias alternativas pode economizar mais do que trocar dezenas de portas lógicas baratas.

**Minha conclusão:** o projeto parece financeiramente viável, mas vale investir tempo na simplificação e simulação antes das compras. Isso deve nos poupar tanto dinheiro quanto retrabalho.

## user — bbb21c3f-eb4b-4075-a53c-d466e86a31d2

Legal, deu pra ter uma ideia boa😎
Seguindo então, o teclado
Não vejo necessidade de um teclado 100%
Letras, números, algumas teclas especiais

## assistant — 2fddf2ff-4e09-49f7-8f97-5b8b687edb12

😎 Então podemos fazer um teclado compacto, pensado especificamente para o nosso TTL-8, sem desperdiçar teclas nem complicar a eletrônica.

Eu escolheria algo próximo de um **teclado de 60%**, mas com um layout próprio. Não precisamos de teclado numérico separado, F1–F12 ou um bloco dedicado de navegação.

## Proposta: teclado TTL-8 de 56 teclas

{@body const rows=[["1","2","3","4","5","6","7","8","9","0","-","=","⌫"],["Q","W","E","R","T","Y","U","I","O","P","[","]"],["A","S","D","F","G","H","J","K","L",";", "'", "↵"],["⇧","Z","X","C","V","B","N","M",",",".","/","⇧"],["CTRL","ALT","ESC","SPACE","SPACE","SPACE","←","↓","↑","→"]]}
<box border radius="xl" padding={3} gap={2}>
  <row align="center" justify="between">
    <text weight="medium">Conceito de layout compacto</text>
    <badge>QWERTY</badge>
  </row>
  <box background="#252b34" theme="dark" padding={2} radius="lg" gap="5px">
    {#each rows as r,i}
      <row gap="3px" justify="center">
        {#each r as k,j}
          <box flex={k==="SPACE"?1.2:1} minWidth="0" height="32px" background="#e0e3e7" border={{size:1,color:"#a8afb8"}} radius="3px" align="center" justify="center">
            <text color="#202630" size="3xs" weight="medium">{k}</text>
          </box>
        {/each}
      </row>
    {/each}
  </box>
  <caption>Esboço funcional, não o desenho mecânico final. As três posições SPACE representam uma única barra de espaço.</caption>
</box>

Essa distribuição tem aproximadamente 52 teclas físicas. Podemos ajustar as teclas especiais conforme o sistema operacional que desenvolvermos.

## O que precisamos preservar?

- **Letras A–Z e números 0–9:** indispensáveis para escrever programas e comandos.
- **Enter, Backspace, Espaço e Shift:** essenciais para digitação.
- **Ctrl, Esc e Alt:** úteis para comandos e atalhos.
- **Pontuação:** `, . / ; ' [ ] - =`, importante para programação.
- **Setas:** convenientes para navegar no editor e no monitor de máquina.

Eu incluiria também uma tecla **Fn**, para acessar funções secundárias sem adicionar muitas teclas físicas.

## E a eletrônica fica simples

Uma matriz de **8 linhas × 8 colunas** oferece 64 posições, suficientes para esse teclado.

Poderíamos usar:

| Componente | Função |
|---|---|
| 74HC138 | Selecionar uma das 8 linhas |
| 74HC244 | Ler as 8 colunas |
| Resistores | Polarização das entradas |
| Diodos por tecla | Evitar ghosting em combinações |
| CPU TTL-8 | Fazer a varredura e interpretar as teclas |

O software na ROM faria o tratamento de Shift, Ctrl, Fn, debounce e repetição.

**Minha preferência seria uma matriz passiva de 8 × 8**, porque é simples, expansível e não exige controlador externo.

E temos uma decisão interessante para o próximo passo: **queremos reaproveitar a mecânica de um teclado existente ou construir o teclado do TTL-8 com switches individuais?**

A primeira opção tende a ser mais barata. A segunda nos dá liberdade para criar um computador com identidade visual própria.

## user — bbb21281-300f-4870-ba00-d5b81bccdf2b

Da uma procurada em teclado de matriz 8x8

## assistant — 02f4f82c-dfa6-41b0-8efb-5ad269e99da0

{"content_type": "thoughts", "source_analysis_msg_id": "9258d7d2-32a5-4cc3-9b42-553f001c2b9c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 16 sites"}]}

## assistant — 02aea3f4-422f-49c0-b532-a6402bb0c9f3

{"content": "Pensou por 7s", "content_type": "reasoning_recap"}

## assistant — 2bb29a1f-83f0-45d8-af03-4c283c05b90a

Pesquisei teclados matriciais **8×8, com 64 teclas**, pensando especificamente no nosso TTL-8.

Encontrei uma placa que realmente corresponde ao que procuramos: **64 posições de teclas e acesso direto às 8 linhas e 8 colunas, sem precisar de USB ou PS/2**.

Mas há uma ressalva: não encontrei ainda um teclado QWERTY completo, pronto para digitar, com essa interface passiva à venda no Brasil.

## As opções mais interessantes

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="Code Mercenaries 8x8 Keymatrix PCB 96x96 keypad" aspectRatio="1:1" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **1. <Link url="https://shop.codemercs.com/en/8x8-keymatrix.html" title="Code Mercenaries — 8×8 Keymatrix"/>**
      <title size="lg">€ 8,98</title>
      <badge color="success">Matriz 8×8 real</badge>
      Placa de 96 × 96 mm, com 64 posições para botões tácteis de 5 mm e dois conectores de 8 pinos. É vendida como PCB, sem as teclas montadas. <Cite ref="turn687258search0"/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Tipro MID KM064A 64 key programmable keyboard module" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **2. <Link url="https://www.posplaza.com.au/tipro-mid-km064a-range-programmable-keyboard.html" title="Tipro MID KM064A"/>**
      <title size="lg">A$ 159</title>
      Teclado industrial de 64 teclas, com matriz 8×8. Há versões de módulo sem controlador, mas é preciso confirmar como acessar eletricamente a matriz. É caro e voltado a aplicações comerciais. <Cite ref="turn687258search11"/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Forlinx 8x8 matrix keypad board 64 tactile buttons blue PCB" aspectRatio="1:1" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **3. <Link url="https://www.tradeindia.com/products/8-8-matrix-board-1406220.html" title="Forlinx — 8×8 Matrix Board"/>**
      <text color="secondary" size="xs">Preço sob consulta</text>
      Placa com 64 botões tácteis e cabo de 20 pinos. Mede aproximadamente 85,5 × 86 mm. É mais voltada a desenvolvimento eletrônico do que a digitação. <Cite ref="turn687258search12"/>
    </box>
  </row>
</box>

## E no Brasil?

Os resultados nacionais ficaram concentrados em teclados matriciais menores:

<row align="start" gap={3}>
  <AsyncImage ref="turn687258product16" aspectRatio="1:1" maxWidth="112px"/>
  <box flex="1" gap={1}>
    **<Entity ref="turn687258product16" value={turn687258product16.title}/>**
    <title size="lg">{turn687258product16.displayed_price}</title>
    <text color="secondary" size="xs">{turn687258product16.merchant}</text>
    É 4×4, com apenas 16 teclas, portanto não atende ao nosso teclado principal.
  </box>
</row>

A Usinainfo também anuncia matrizes de 4×5, com 20 teclas, mas não encontrei uma 8×8 completa no catálogo consultado. <Cite ref="turn687258search10"/>

## Uma observação importante para o TTL-8

**Uma matriz elétrica 8×8 não precisa ter as teclas organizadas fisicamente em oito linhas e oito colunas.**

Podemos construir um teclado QWERTY convencional, com linhas físicas desencontradas, e conectar suas 55–60 teclas a uma matriz elétrica 8×8.

Isso significa que temos liberdade para criar um teclado confortável, e não aquele quadrado de 64 botões pequenos.

Também encontrei um <Link url="https://cdck-file-uploads-europe1.s3.dualstack.eu-west-1.amazonaws.com/arduino/original/3X/1/7/1798cb7cdc683a2322baa5bfea0a803849654082.pdf" title="esquema eletrônico de um teclado 8×8"/> que utiliza registradores 74HC595 e 74HC165. É uma boa referência para nossa interface de teclado, embora não seja um projeto pronto para o TTL-8. <Cite ref="turn687258search25"/>

## O que eu escolheria?

| Opção | Serve ao TTL-8? | Minha avaliação |
|---|---|---|
| Code Mercenaries 8×8 | Sim | Boa para experimentar |
| Tipro 64 teclas | Potencialmente | Cara para nosso objetivo |
| Forlinx 8×8 | Sim, após verificar pinagem | Pouco confortável |
| Teclado compacto com matriz própria | Sim | Melhor para o computador definitivo |

Eu não compraria ainda nenhuma dessas placas. **A opção mais promissora continua sendo reaproveitar a mecânica de um teclado compacto ou construir nossa própria matriz 8×8**, porque teremos teclas de tamanho normal, custo controlável e integração direta com os 74HC.

A pesquisa confirmou que a matriz 8×8 é perfeitamente viável; o desafio maior não é a eletrônica, mas encontrar uma montagem física confortável e barata.

## user — bbb21cc0-36ad-42e1-a9aa-27fa34db35e7

Pesquisando de tudo um pouco aqui
Achei esse https://meli.la/13eCwrC

## assistant — 4645f77f-8d51-4668-a72d-3e69ba5e32c5

{"content_type": "thoughts", "source_analysis_msg_id": "6ee1ba6b-b3da-406f-b912-b6fd857a5240", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 1 site"}]}

## assistant — d210c79b-d3b2-43e5-9507-3bbf7a1aef6e

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — d9f8de5e-9ab8-466d-b544-9626a021b146

Boa! 😎 Vamos investigar esse também para ver se serve ao nosso TTL-8.

Tentei abrir o anúncio do Mercado Livre:

<Link url="https://meli.la/13eCwrC" title="Ver anúncio que você encontrou"/>

Mas o Mercado Livre bloqueou o acesso pelo link encurtado, e não consegui identificar o produto com segurança.

**Consegue me mandar um print do anúncio**, mostrando a foto, o nome e o preço?

Quero avaliar principalmente três coisas:

- **Interface elétrica:** se podemos acessar diretamente a matriz de teclas, sem USB ou microcontrolador.
- **Quantidade de teclas:** se atende às nossas necessidades de letras, números e comandos.
- **Adaptação:** quantos CIs 74HC seriam necessários para integrá-lo ao computador.

Se for um teclado que já tenha uma matriz passiva acessível, pode ser exatamente o que estamos procurando!

## user — bbb21868-75e4-41a1-bee5-b79da04e3548

{"asset_pointer": "sediment://file_000000007c28820ea9441d32d66a0b1d", "content_type": "image_asset_pointer", "fovea": null, "height": 1536, "metadata": {"asset_pointer_link": null, "container_pixel_height": null, "container_pixel_width": null, "dalle": null, "emu_omit_glimpse_image": null, "emu_patches_override": null, "generation": null, "gizmo": null, "is_no_auth_placeholder": null, "lpe_delta_encoding_channel": null, "lpe_keep_patch_ijhw": null, "sanitized": true, "segmentation": null, "watermarked_asset_pointer": null}, "mime_type": "image/jpeg", "size_bytes": 112872, "width": 1536}
https://www.mercadolivre.com.br/up/MLBU3131549911?matt_tool=38524122&pdp_filters=item_id%3AMLB5358484964&ua=vYRdfZlzD7BEn2ddN-hKOnivae9XwVOzIZ1jBje1WbHD4IY
Eh um tenso upson sem fio até, parece ser infravermelho


## assistant — 2c6acb06-983c-4519-893b-84659cb8dc80

{"content_type": "thoughts", "source_analysis_msg_id": "73c2136c-d2c9-48ba-a72f-8b378ddc2027", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 12 sites"}]}

## assistant — f9028f1c-852b-4cea-8b22-b3b183938227

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 9999a914-5cac-4f91-a036-255fe0069107

Esse é um achado interessante! 😎

Pela foto, parece ser um **teclado UPSON para multimídia**, acompanhado de mouse, manual e um pequeno receptor. O manual parece indicar o modelo **F-21**, mas precisamos confirmar.

O detalhe mais interessante para o nosso TTL-8 é justamente ele ser sem fio.

Se realmente usar infravermelho, poderíamos tentar aproveitar o teclado inteiro, incluindo sua eletrônica original, e construir apenas um receptor compatível com nossa CPU de 8 bits.

Isso evitaria desmontar a membrana e mapear dezenas de teclas.

**Mas há uma diferença importante:** infravermelho não significa necessariamente protocolo simples. O teclado pode transmitir códigos proprietários, e precisaríamos descobrir como eles são codificados.

## O que a pesquisa revelou

Encontrei anúncios de teclados antigos Upson sem fio, inclusive um modelo **UP6872**, descrito como teclado de membrana ABNT2. <Cite ref="turn241350search5"/>

Porém, não consegui confirmar que o modelo da sua foto utiliza infravermelho. Ele também pode funcionar por radiofrequência (RF).

Essa distinção muda bastante o projeto:

| Característica | Infravermelho (IR) | Radiofrequência (RF) |
|---|---|---|
| Receptor | Sensor IR, possivelmente simples | Receptor RF compatível |
| Decodificação com 74HC | Possível, dependendo do protocolo | Geralmente mais trabalhosa |
| Precisa apontar para o receptor | Normalmente sim | Não |
| Integração com TTL-8 | Promissora | Depende do receptor original |

## Como poderíamos aproveitá-lo

Vejo três caminhos:

1. **Manter a comunicação sem fio original**, descobrindo o protocolo e construindo a interface com o TTL-8.
2. **Aproveitar o receptor original**, identificando os sinais elétricos que ele entrega ao computador. Se sua saída for PS/2, por exemplo, seria especialmente conveniente.
3. **Desativar a parte sem fio e aproveitar a matriz interna**, transformando o teclado em um periférico com fio.

O terceiro caminho é o mais previsível. O primeiro seria o mais divertido do ponto de vista de engenharia reversa.

### Minha avaliação

<badge color="warning">Vale investigar antes de comprar</badge>

O teclado é interessante, principalmente por ser antigo e possivelmente ter uma eletrônica mais acessível do que a de um teclado moderno. Mas não devemos presumir que o protocolo seja simples apenas pela idade.

**Tem um detalhe que eu gostaria muito de verificar: a conexão do receptor.**

Na foto aparece um pequeno dispositivo perto do manual. Se você conseguir uma imagem mais próxima desse receptor, ou uma foto da parte traseira da embalagem mostrando o modelo e as conexões, poderemos determinar melhor se estamos diante de um teclado IR, RF ou de uma interface PS/2 sem fio.

Se o receptor entregar PS/2, podemos ter encontrado uma solução muito conveniente: **um teclado sem fio completo para nosso computador feito com lógica 74HC.**

## user — bbb21c61-4fa4-48d3-8cc7-b0deb4bcd738

Ahh não eh um mouse, eh o receptor, interessante

## assistant — 7cdeba3f-4315-4977-b191-27e1529e07f4

Ahhh, isso muda bastante! 😎

Se aquele dispositivo é o **receptor do teclado**, temos uma possibilidade ainda mais interessante para o nosso TTL-8: aproveitar o conjunto sem fio original.

O receptor provavelmente já faz a parte mais complicada: receber os sinais do teclado e convertê-los em informações que um computador consiga interpretar.

Agora precisamos descobrir **qual é a saída desse receptor**.

- **PS/2:** excelente! Podemos implementar a leitura com poucos CIs 74HC.
- **Serial:** também seria interessante, dependendo do protocolo.
- **USB:** mais complicado, pois nosso computador precisaria atuar como host USB.
- **Conector proprietário:** precisaríamos investigar a pinagem.

E, como você observou, ele pode ser infravermelho, mas ainda não temos confirmação.

**Uma coisa me chamou a atenção:** na imagem, o receptor parece ter uma abertura escura na frente, compatível com uma janela para infravermelho, embora isso não seja prova.

Consegue ver no anúncio se há uma foto do **cabo ou conector que sai do receptor**?

Essa informação pode ser decisiva. Se for PS/2, esse teclado antigo pode acabar sendo uma das soluções mais interessantes que encontramos até agora!

## user — bbb21f0e-fd4a-449d-9b52-5e12703e9467

Eh PS2 mesmo
Mas vamos ver outros, estou pensando em seguir pelo PS2
Pois não vamos construir uma tela por exemplo
Pq vamos gastar com o teclado

## assistant — 17a0dd4d-7493-4d4f-98c2-8783cc3a3a25

{"content_type": "thoughts", "source_analysis_msg_id": "9df987bf-1cc3-4a09-8b50-a3098e3adc42", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 7 sites"}]}

## assistant — b441de89-f5fa-466f-91c9-1580f9d5f692

{"content": "Pensou por 7s", "content_type": "reasoning_recap"}

## assistant — ef3c7953-aa9a-4ba8-a0eb-e7f2367df7c0

Concordo! 😎 Acho que chegamos a uma decisão importante para o TTL-8: **usar componentes prontos onde isso não compromete a essência de construir nosso próprio computador.**

Estamos comprando um monitor pronto, não construindo o tubo de imagem. Podemos seguir exatamente a mesma lógica com o teclado.

A parte que realmente queremos desenvolver é a CPU, os barramentos, a memória, o controlador de vídeo e a interface eletrônica com os periféricos.

E o PS/2 combina muito bem com isso, porque é um protocolo relativamente simples, com apenas duas linhas de comunicação: `CLOCK` e `DATA`.

## O que eu procuraria

Não precisamos de um teclado antigo, raro ou colecionável. Procuraria um modelo comum, com fio, preferencialmente ABNT2, que seja barato e fácil de substituir.

Também podemos considerar aquele UPSON sem fio que você encontrou: se o receptor realmente tem saída PS/2, o nosso computador não precisa saber que existe uma conexão sem fio entre ele e o teclado.

Para a CPU, os dois seriam teclados PS/2.

## Encontrei opções PS/2 bem baratas no Brasil

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="teclado Multi TC298 PS2 preto compacto" aspectRatio="1:1" maxWidth="116px"/>
    <box flex="1" gap={1}>
      **<Link url="https://www.pichau.com.br/teclado-compacto-multi-ps2-preto-tc298" title="Multi TC298 — compacto PS/2"/>**
      <title size="lg">R$ 29,99</title>
      ABNT2, com fio, anunciado como compacto. Mede aproximadamente 41 cm de largura. <Cite ref="turn843005search0"/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="teclado K-Mex KB-2428P PS2 preto" aspectRatio="1:1" maxWidth="116px"/>
    <box flex="1" gap={1}>
      **<Link url="https://www.atera.com.br/produto/kb-2428p/Teclado%2Bslim%2BK-Mex%2BKB-2428P%2BABNT2%2BPS2%2B107%2Bteclas" title="K-Mex KB-2428P — PS/2"/>**
      <title size="lg">R$ 27,00</title>
      ABNT2, 107 teclas, perfil baixo. Uma das opções mais econômicas que encontrei. <Cite ref="turn843005search4"/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="teclado Multilaser TC047 PS2 slim preto" aspectRatio="1:1" maxWidth="116px"/>
    <box flex="1" gap={1}>
      **<Link url="https://www.atera.com.br/produto/tc047/Teclado%2Bslim%2BMultilaser%2BTC047-%2Bsilencioso-%2BABNT2%2BPS-2" title="Multilaser TC047 — PS/2"/>**
      <title size="lg">R$ 28,00</title>
      ABNT2, 109 teclas, perfil baixo. <Cite ref="turn843005search6"/>
    </box>
  </row>
</box>

Os preços são os anunciados nas páginas consultadas, antes do frete, e não garantem estoque no momento da compra.

O curioso é que **um teclado PS/2 completo pode custar menos de R$ 30**, enquanto construir um teclado mecânico próprio provavelmente sairia bem mais caro.

## O circuito que teremos de construir

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 105" width="100%">
    {#each [{x:4,w:89,t:"Teclado",s:"PS/2"},{x:120,w:90,t:"Interface",s:"74HC"},{x:237,w:89,t:"CPU",s:"TTL-8"}] as a}
      <rect x={a.x} y="22" width={a.w} height="55" rx="6" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
      <text x={a.x+a.w/2} y="44" fontSize="12" fontWeight="600" fill="currentColor" textAnchor="middle">{a.t}</text>
      <text x={a.x+a.w/2} y="61" fontSize="11" fill="currentColor" textAnchor="middle">{a.s}</text>
    {/each}
    <path d="M93 49 H120 M210 49 H237" stroke="#94a3b8" strokeWidth="2"/>
    <text x="106" y="37" fontSize="8" fill="currentColor" textAnchor="middle">2 fios</text>
    <text x="224" y="37" fontSize="8" fill="currentColor" textAnchor="middle">8 bits</text>
    <text x="165" y="96" fontSize="9" fill="currentColor" textAnchor="middle">Recepção serial + registrador de dados</text>
  </svg>
</box>

Nossa interface PS/2 poderá receber os códigos de teclas usando registradores de deslocamento, lógica de sincronização e um registrador de dados acessível pela CPU. O firmware interpretará os códigos e os converterá em caracteres.

Precisaremos também tratar a comunicação bidirecional, ou definir inicialmente um subconjunto compatível do protocolo, incluindo a inicialização do teclado. A quantidade exata de CIs depende do esquema final.

**Eu adotaria PS/2 como interface oficial do TTL-8.** Isso nos dá liberdade para trocar de teclado sem modificar o computador, inclusive usar aquele UPSON sem fio com receptor PS/2.

E manteria o painel de oito chaves como uma expansão opcional, para programação e diagnóstico. Assim, o projeto continua sendo um PC completo, mas concentramos nosso tempo e dinheiro na eletrônica que realmente queremos desenvolver.

## user — bbb218fd-73d3-47c4-b6de-f524c33588c3

Não consegui abrir o link da pichau

## assistant — 4aae0c79-db4b-4c9f-8d4a-7478bf0a576f

{"content_type": "thoughts", "source_analysis_msg_id": "b56dbbc5-4884-43c8-988d-f10720afd4d6", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 11 sites"}]}

## assistant — 07cc13ac-2902-4d56-bcfa-57189c56a6de

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — d2a26548-23c1-4e3b-8c7e-b62d4a83aeeb

Conferi novamente! O link da Pichau ainda aparece na pesquisa, mas pode estar indisponível para acesso pelo aplicativo.

O teclado é o **Multi TC298, PS/2, ABNT2**, anunciado por R$ 29,99 na Pichau. <Cite ref="turn486042search0"/>

<row align="start" gap={3}>
  <AsyncImage query="teclado Multi Multilaser TC298 PS2 preto ABNT2" aspectRatio="5:4" maxWidth="130px"/>
  <box flex="1" gap={2}>
    **Multi TC298 — PS/2**

    <text color="secondary" size="sm">41 cm de largura, cabo de 1,3 m, teclado de membrana.</text>
    <text weight="medium">Links para tentar:</text>
    <Link url="https://www.pichau.com.br/teclado-compacto-multi-ps2-preto-tc298" title="Pichau — anúncio original"/>
    <Link url="https://acess.inf.br/teclado-mult-ps2-tc298-pre-multilaser-012396/p" title="Acess Informática — R$ 39,00, anunciado em estoque"/>
  </box>
</row>

A Acess Informática é uma alternativa interessante porque a página consultada indica estoque. <Cite ref="turn486042search6"/>

Uma observação: apesar de ser chamado de *compacto*, ele tem 41 cm de largura. Para nosso TTL-8, ainda vale procurar um PS/2 menor, sem teclado numérico.

## user — bbb2142f-0a03-4779-bd7b-8270cf0d7af2

Essa acess é confiável? 

## assistant — 1f570d59-8b05-4946-8cce-81cc659611d9

{"content_type": "thoughts", "source_analysis_msg_id": "6fd4f769-90aa-44ea-8393-77206b32235a", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 7 sites"}]}

## assistant — e3f3374c-8ade-4268-9440-18c09648fc97

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 2181a846-00ff-4d7f-9b78-26b02cea2e26

Pesquisei a **Acess Informática (acess.inf.br)** e encontrei alguns sinais positivos. Porém, ainda não tenho evidências suficientes para garantir que a experiência de compra seja confiável.

## O que consegui verificar

| Critério | Resultado |
|---|---|
| Empresa identificada | <icon name="check-circle" color="success" inline/> Sim |
| CNPJ divulgado | 08.665.985/0001-86 |
| Razão social | Majolo Informática Total Ltda. |
| Endereço físico | <icon name="check-circle" color="success" inline/> Divulgado em Arroio do Meio, RS |
| Telefone comercial | <icon name="check-circle" color="success" inline/> (51) 3716-1354 |
| Histórico declarado | Atua desde 2006 |
| Avaliações independentes | <icon name="alert-circle" color="secondary" inline/> Não consegui confirmar reputação suficiente |

Os dados cadastrais e de contato aparecem no próprio site da empresa. A informação sobre atuação desde 2006 também é declarada pela loja, não uma comprovação independente. <Cite refs={["turn860194search0","turn860194search1"]}/>

Não encontrei uma avaliação consistente no Reclame Aqui que pudesse atribuir com segurança a esse mesmo CNPJ.

## Minha avaliação

<badge color="warning">Confiabilidade ainda não confirmada</badge>

**A loja apresenta sinais de ser um estabelecimento real**, mas isso não comprova que entregará corretamente uma compra online.

Para comprar nosso teclado PS/2, de aproximadamente R$ 39, eu tomaria três cuidados:

- Confirmaria o CNPJ no site da Receita Federal.
- Perguntaria pelo WhatsApp se o teclado está realmente disponível.
- Preferiria pagar com cartão de crédito, evitando Pix antecipado para uma loja ainda não verificada.

**Eu não descartaria a Acess**, mas também não a colocaria no mesmo nível de confiança de uma loja com muitas avaliações verificadas.

Como o teclado é barato, minha preferência seria encontrar o mesmo modelo em um vendedor bem avaliado do Mercado Livre, mesmo que custasse R$ 10 ou R$ 15 a mais.

## user — bbb219ae-795c-4e31-a926-46db61e62ada

Pensando aqui
Daria pra usar algum conversor USB pra PS2? 

## assistant — 93cffd2b-2f94-4856-a3e7-84674b00f846

{"content_type": "thoughts", "source_analysis_msg_id": "925b4cb0-c658-41b4-a0b9-ffd87243b232", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 10 sites"}]}

## assistant — fbb7374a-83af-4a21-a93b-cbc9a25347dd

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — b4f8ce74-b333-40a8-951c-fd3b6265659a

**Sim! 😎 E isso pode facilitar bastante a escolha do teclado para nosso TTL-8.**

Mas existe uma pegadinha importante: há dois tipos de conversores USB para PS/2, e apenas um deles permite utilizar um teclado USB comum.

## 1. Adaptador passivo — geralmente não serve

<AsyncImage query="green purple USB female to PS2 male passive keyboard mouse adapter" aspectRatio="5:3" maxWidth="280px"/>

É aquele adaptador pequeno, geralmente verde ou roxo, que custa poucos reais.

Ele **não converte o protocolo USB em PS/2**. Apenas conecta os pinos de maneira diferente.

Funciona somente com teclados que já possuem suporte interno aos dois protocolos, chamados de dispositivos *dual-mode*.

Um teclado USB moderno, que não tenha esse suporte, não funcionará com esse adaptador.

## 2. Conversor ativo — esse pode funcionar!

<AsyncImage query="active USB keyboard to PS2 converter USB female PS2 male electronic converter keyboard" aspectRatio="5:3" maxWidth="280px"/>

Esse tipo possui um circuito eletrônico que:

1. Atua como host USB para reconhecer o teclado.
2. Recebe os códigos das teclas pelo protocolo USB HID.
3. Converte esses códigos em eventos PS/2.
4. Envia os dados ao nosso computador através de Clock e Data.

Nesse caso, o TTL-8 continuaria tendo apenas uma interface PS/2, mas poderíamos conectar um teclado USB convencional.

O conversor precisaria ser especificamente **USB teclado → PS/2 computador**, não o contrário.

## 3. Encontrei conversores ativos de verdade

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="Black Box KVUSB-PS2 USB keyboard to PS2 computer converter" aspectRatio="5:4" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Link url="https://www.blackbox.com/en-us/store/product/detail/USB-Keyboard-to-PS-2-Computer-Converter/KVUSB-PS2" title="Black Box KVUSB-PS2"/>**

      Produto comercial que permite usar teclados e mouses USB em computadores com portas PS/2. <Cite ref="turn669729search1"/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="HIDman USB keyboard PS2 retro computer converter board" aspectRatio="5:4" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Link url="https://github.com/rasteri/HIDman" title="HIDman — projeto aberto"/>**

      Conversor USB HID para PS/2 baseado no CH559, com esquemas e arquivos de placa disponíveis. <Cite ref="turn669729search3"/>
    </box>
  </row>
</box>

O problema é que esses conversores ativos podem custar mais que um teclado PS/2 simples, além de nem sempre serem fáceis de encontrar no Brasil.

## O que eu faria no TTL-8

Manteria a interface PS/2 como padrão, mas deixaria aberta a possibilidade de usar um conversor ativo futuramente.

Assim, teríamos:

<box border radius="lg" padding={3} gap={1}>
  <svg viewBox="0 0 330 100" width="100%">
    {#each [{x:3,t:"Teclado USB"},{x:116,t:"Conversor ativo"},{x:229,t:"TTL-8 / PS/2"}] as a}
      <rect x={a.x} y="27" width="98" height="42" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={a.x+49} y="52" textAnchor="middle" fontSize="10.5" fill="currentColor">{a.t}</text>
    {/each}
    <path d="M101 48 H116 M214 48 H229" stroke="#94a3b8" strokeWidth="2"/>
    <text x="108" y="19" fontSize="9" textAnchor="middle" fill="currentColor">USB</text>
    <text x="222" y="19" fontSize="9" textAnchor="middle" fill="currentColor">PS/2</text>
  </svg>
</box>

**Minha recomendação:** para a primeira versão, comprar um teclado PS/2 barato continua sendo a opção mais simples e econômica.

Mas se você já tiver um teclado USB compacto de que goste, um conversor ativo é tecnicamente viável — e não exige modificar nossa CPU.

Só não compraria aqueles adaptadores passivos de R$ 5 achando que vão converter qualquer teclado USB.

## user — bbb21127-cc9f-4192-a9d4-a456767f94b6

Qual o trabalho de pegar 4 desses teclados de membranas 4x4 16 teclas, E formar um com 64 teclas? Vi isso já

## assistant — 9836baa1-b325-4923-b442-45a2e1006416

{"content_type": "thoughts", "source_analysis_msg_id": "d7cacfb3-ac75-4ad5-9568-a9fd0aff54aa", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 13 sites"}]}

## assistant — 564ff82b-086d-478d-8223-cc112405cc69

{"content": "Pensou por 4s", "content_type": "reasoning_recap"}

## assistant — 52672a07-f41d-4ccb-bf64-6a73f2cfa468

**Dá para fazer, sim! 😎 E para o nosso TTL-8, essa pode ser uma das soluções mais simples e econômicas.**

Quatro teclados matriciais de membrana 4×4 nos dariam **64 teclas físicas**, suficientes para letras, números, pontuação e comandos.

O melhor é que podemos fazer isso sem microcontrolador, usando a própria CPU TTL-8 para ler as teclas.

Mas existe um detalhe interessante: **não precisamos de 32 fios nem de quatro controladores independentes.** Podemos interligar as quatro membranas e formar uma única matriz lógica de 8×8.

## Como ficaria a montagem

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">Quatro módulos 4×4 formando 64 teclas</text>
  <grid columns={2} gap={2}>
    {#each [{name:"Módulo A",keys:["1","2","3","4","5","6","7","8","9","0","-","=","Q","W","E","R"]},{name:"Módulo B",keys:["T","Y","U","I","O","P","[","]","A","S","D","F","G","H","J","K"]},{name:"Módulo C",keys:["L",";", "'", "↵","Z","X","C","V","B","N","M",",",".","/","⌫","ESC"]},{name:"Módulo D",keys:["SHIFT","CTRL","ALT","FN","←","↓","↑","→","F1","F2","F3","F4","SPACE","SPACE","SPACE","SPACE"]}] as m}
      <grid-item>
        <box border radius="lg" padding={2} gap={2}>
          <text color="secondary" size="xs" weight="medium">{m.name}</text>
          <grid columns={4} gap="3px">
            {#each m.keys as k}
              <grid-item>
                <box background="surface-secondary" border radius="xs" height="30px" align="center" justify="center">
                  <text size="3xs" weight="medium">{k}</text>
                </box>
              </grid-item>
            {/each}
          </grid>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Distribuição ilustrativa. Na montagem real, as quatro membranas teriam formato quadrado, não o formato tradicional de um teclado QWERTY.</caption>
</box>

Essa é a principal desvantagem: o teclado seria funcional, mas a disposição das letras não seria tão confortável quanto a de um teclado convencional.

## Como unir eletricamente os quatro módulos

Imagine os módulos dispostos assim:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 205" width="100%">
    {#each [{x:18,y:20,n:"A",rows:"R0–R3",cols:"C0–C3"},{x:172,y:20,n:"B",rows:"R0–R3",cols:"C4–C7"},{x:18,y:112,n:"C",rows:"R4–R7",cols:"C0–C3"},{x:172,y:112,n:"D",rows:"R4–R7",cols:"C4–C7"}] as m}
      <rect x={m.x} y={m.y} width="130" height="70" rx="6" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
      <text x={m.x+65} y={m.y+19} fontSize="12" fontWeight="600" textAnchor="middle" fill="currentColor">Módulo {m.n}</text>
      <text x={m.x+65} y={m.y+38} fontSize="10" textAnchor="middle" fill="currentColor">{m.rows}</text>
      <text x={m.x+65} y={m.y+54} fontSize="10" textAnchor="middle" fill="currentColor">{m.cols}</text>
    {/each}
    <g stroke="#94a3b8" strokeWidth="2" fill="none">
      <path d="M148 55 H172 M148 147 H172"/>
      <path d="M83 90 V112 M237 90 V112"/>
    </g>
    <text x="160" y="201" fontSize="11" textAnchor="middle" fill="currentColor">Resultado: matriz lógica de 8 × 8</text>
  </svg>
</box>

As conexões seriam:

| Módulos | Conexões compartilhadas |
|---|---|
| A e B | Mesmas quatro linhas |
| C e D | Outras quatro linhas |
| A e C | Mesmas quatro colunas |
| B e D | Outras quatro colunas |

Assim, os 32 terminais originais passam a formar **16 sinais únicos: oito linhas e oito colunas**.

A CPU selecionaria uma linha de cada vez e leria as oito colunas. Esse é o funcionamento normal de um teclado matricial. <Cite refs={["turn850544search0","turn850544search12"]}/>

## O que precisaríamos construir?

| Item | Quantidade |
|---|---:|
| Membranas 4×4 | 4 |
| Conectores para os cabos de 8 vias | 4 |
| 74HC138 para seleção de linhas | 1 |
| 74HC244 para leitura de colunas | 1 |
| Lógica adicional para seleção e controle | Conforme o barramento |
| Resistores de pull-up | 8 |
| Placa para interligação | 1 |

A interface é simples, mas há um detalhe importante: essas membranas normalmente não têm diodos individuais. Portanto, **Shift + letra pode funcionar, mas determinadas combinações de três ou mais teclas podem produzir teclas fantasmas**. <Cite ref="turn850544search6"/>

Para digitação normal, podemos tratar isso parcialmente no software. Para eliminar o problema eletricamente, precisaríamos de diodos por tecla, o que não é fácil de adicionar dentro de membranas prontas.

## Quanto trabalho daria?

Eu classificaria assim:

- **Eletrônica:** fácil a moderada. É basicamente interligação, seleção de linhas e leitura de colunas.
- **Firmware:** moderado. Precisamos implementar varredura, debounce, Shift e conversão para ASCII.
- **Montagem física:** moderada. Precisamos fixar os quatro módulos numa base e criar legendas para as teclas.
- **Conforto:** inferior ao de um teclado convencional, principalmente pela disposição quadrada.

**Minha avaliação:** é uma solução totalmente viável para o TTL-8, e podemos desenvolvê-la como um módulo independente da CPU.

Mas há uma escolha que eu faria antes de comprar: quatro membranas 4×4 são ótimas para um teclado de comandos, enquanto um teclado PS/2 pronto provavelmente será mais confortável para escrever programas longos.

Se a intenção é ter um computador com uma aparência própria, os quatro módulos podem ficar muito interessantes — especialmente com uma placa frontal personalizada, legendas e uma organização de teclas pensada especificamente para nosso sistema.

## user — bbb21769-48d6-45eb-bd9f-579456397a43

Podemos colocar tudo lado a lado
4 linhas por 16 colunas
E outro ponto
São mais ou menos Chips se comparado com um PS2? 
E o nosso código? Como fica? 

## assistant — fc5f3c4e-9a91-44f0-842a-6c2647e8ee05

{"content_type": "thoughts", "source_analysis_msg_id": "50945c45-d15b-4e00-b0e1-980ae296c47f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — a8b8996c-6fa6-442d-9db8-ab880fa08628

{"content": "Pensou por 7s", "content_type": "reasoning_recap"}

## assistant — 19b5e668-5c16-4800-a2dd-01bac7b85b7a

**Sim! E colocar os quatro teclados 4×4 lado a lado é até mais interessante para o nosso TTL-8.** 😎

Teríamos um teclado de **4 linhas × 16 colunas = 64 teclas**, sem precisar transformar a ligação elétrica em 8×8.

A grande vantagem é que podemos usar as 64 posições para letras, números e comandos, com um controlador relativamente simples.

## 1. Como ficaria o teclado

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">Quatro membranas 4×4 lado a lado</text>
  <box background="surface-secondary" padding={2} radius="lg" gap="4px">
    {#each [["1","2","3","4","5","6","7","8","9","0","-","=","[","]","/","⌫"],["Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H"],["J","K","L","Z","X","C","V","B","N","M",",",".",";", "'", "\\","↵"],["ESC","CTRL","SHIFT","ALT","FN","TAB","SPACE","←","↓","↑","→","HOME","END","DEL","F1","F2"]] as r}
      <row gap="3px">
        {#each r as k,i}
          <box flex="1" minWidth="0" height="32px" background={Math.floor(i/4)%2===0?"#dbe5ee":"#c3d3e1"} radius="3px" align="center" justify="center">
            <text color="#17212b" size="3xs" weight="medium">{k}</text>
          </box>
        {/each}
      </row>
    {/each}
  </box>
  <caption>Esboço de 64 posições. Cada grupo de quatro colunas corresponde a uma membrana; as teclas físicas continuam sendo quadradas.</caption>
</box>

Ele ficaria comprido e baixo, quase como um teclado de terminal industrial. Para programar, talvez seja menos confortável que um teclado QWERTY convencional, mas funcionaria.

## 2. Como ligar eletricamente

Cada membrana possui quatro linhas e quatro colunas. Ligamos as quatro linhas equivalentes dos quatro módulos em paralelo e mantemos as 16 colunas separadas.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 177" width="100%">
    {#each [0,1,2,3] as i}
      <rect x={6+i*84} y="10" width="76" height="62" rx="5" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
      <text x={44+i*84} y="29" textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">4×4</text>
      <text x={44+i*84} y="44" textAnchor="middle" fontSize="9" fill="currentColor">Módulo {i+1}</text>
      <text x={44+i*84} y="58" textAnchor="middle" fontSize="9" fill="currentColor">C{i*4}–C{i*4+3}</text>
      <path d={`M${44+i*84} 72 V104`} stroke="#94a3b8" strokeWidth="1.5"/>
    {/each}
    <path d="M44 104 H296" stroke="#94a3b8" strokeWidth="2" strokeDasharray="4 3"/>
    <text x="170" y="119" textAnchor="middle" fontSize="9" fill="currentColor">4 linhas compartilhadas • 16 colunas independentes</text>
    <rect x="69" y="135" width="202" height="33" rx="5" stroke="#60a5fa" fill="#3b82f6" fillOpacity=".1"/>
    <text x="170" y="156" textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">Interface de teclado TTL-8</text>
  </svg>
</box>

Isso resulta em **20 sinais de matriz**, em vez dos 16 sinais de uma matriz 8×8. Não é um problema: podemos organizar a leitura de modo a economizar CIs.

## 3. Quantos CIs: matriz 4×16 versus PS/2?

Aqui temos uma surpresa: **a matriz pode usar menos CIs que uma interface PS/2 completa**, principalmente porque a CPU pode fazer a varredura diretamente.

Eu compararia duas implementações:

| Solução | CIs estimados | Complexidade do firmware |
|---|---:|---|
| PS/2 com recepção por hardware | 3–6 | Média |
| Matriz 4×16 com leitura paralela | 4–5 | Baixa |
| Matriz 4×16 com multiplexação | 3–4 | Baixa/média |

Esses números são metas de arquitetura, não uma lista validada de montagem. Não incluem a decodificação de endereços que poderemos compartilhar com o restante do computador.

### Minha proposta para a matriz 4×16

Podemos usar:

- **1× 74HC139:** seleciona uma das quatro linhas.
- **2× 74HC244:** permitem ler as 16 colunas, em dois grupos de oito.
- **1× 74HC574:** armazena o número da linha selecionada, com bits não utilizados disponíveis.
- Resistores de pull-up para as 16 colunas.

O 74HC139 possui dois decodificadores 2→4; um deles basta para as quatro linhas. Os 74HC244 podem compartilhar o barramento de dados, desde que somente um seja habilitado por vez.

O 74HC574 pode até ser substituído por um registrador de saída que já exista no nosso módulo de entrada/saída.

**Total: quatro CIs dedicados, potencialmente três se reaproveitarmos um registrador existente.**

Essa opção é atraente porque é simples de entender, testar e consertar.

## 4. E o código? Fica mais simples que PS/2?

Sim, especialmente na camada de comunicação.

Com PS/2, precisamos receber uma sequência serial, verificar o enquadramento, distinguir pressionamento e soltura, e interpretar os *scan codes*.

Na matriz, a CPU simplesmente seleciona uma linha e lê as colunas.

Por exemplo, poderíamos reservar dois endereços de entrada/saída:

| Endereço | Função |
|---|---|
| `E040` | Escrever o número da linha (0–3) |
| `E041` | Ler as colunas 0–7 |
| `E042` | Ler as colunas 8–15 |

O código de varredura, em pseudocódigo próximo de C, seria:

```c
uint16_t ler_linha(uint8_t linha)
{
    uint8_t baixo, alto;

    escrever_io(0xE040, linha);

    // Pequeno tempo para estabilizar os sinais.
    baixo = ler_io(0xE041);
    alto  = ler_io(0xE042);

    // Coluna pressionada = 0 (pull-up).
    return ~((uint16_t)alto << 8 | baixo);
}

void varrer_teclado(void)
{
    for (uint8_t linha = 0; linha < 4; linha++) {
        uint16_t teclas = ler_linha(linha);

        for (uint8_t coluna = 0; coluna < 16; coluna++) {
            if (teclas & (1u << coluna)) {
                registrar_tecla(linha, coluna);
            }
        }
    }
}
```

Esse exemplo mostra apenas a detecção básica. O firmware real precisará comparar o estado atual com o anterior, fazer debounce e gerar eventos de pressionamento e soltura. Caso contrário, uma tecla mantida pressionada seria registrada repetidamente.

### Como transformar isso em letras?

Criamos uma tabela na ROM:

```c
const char mapa[4][16] = {
    {'1','2','3','4','5','6','7','8',
     '9','0','-','=','[',']','/','\b'},

    {'q','w','e','r','t','y','u','i',
     'o','p','a','s','d','f','g','h'},

    {'j','k','l','z','x','c','v','b',
     'n','m',',','.',';','\'','\\','\n'},

    {0,0,0,0,0,'\t',' ',0,
     0,0,0,0,0,0,0,0}
};
```

As posições especiais receberiam códigos próprios, e o Shift escolheria letras maiúsculas ou símbolos alternativos.

No computador definitivo, isso seria implementado no nosso Assembly de 8 bits, não em C. A rotina poderia ser chamada periodicamente pelo monitor de sistema.

## 5. Uma diferença importante: teclas simultâneas

Os teclados matriciais 4×4 de membrana geralmente não têm diodos individuais.

Isso significa que combinações como `SHIFT + A` podem ser detectadas normalmente, mas algumas combinações com três ou mais teclas podem gerar *ghosting*.

Podemos implementar uma política simples: detectar combinações ambíguas e ignorá-las, preservando o funcionamento básico. Isso não resolve todas as limitações de uma matriz sem diodos, mas evita interpretar algumas teclas fantasmas.

## Minha escolha para o TTL-8

Eu estou inclinado a preferir a **matriz 4×16**, por três motivos: não depende de protocolo externo, tem um circuito fácil de depurar e nos permite personalizar o teclado.

Mas existe um ponto que vale considerar antes de decidir: quatro membranas 4×4 lado a lado criam um teclado muito comprido e com apenas quatro fileiras. É funcional, porém diferente de um teclado tradicional.

**Se a estética e o conforto desse formato te agradarem, eu escolheria a matriz 4×16.** A quantidade de CIs fica praticamente empatada com PS/2, e o software de leitura é mais simples.

<text color="secondary" size="sm">Referência técnica: famílias 74HC139, 74HC244 e multiplexadores 74HC153, cuja configuração é documentada pelos fabricantes. <Cite refs={["turn994166search0","turn994166search1"]}/></text>

## user — bbb217b8-be6d-4701-a3d2-77f5c4c8cc92

Meu teclado do dia a dia já não eh convencional kkk
Eh um ajazz aks068
Então vamos de 4 matrizes

## assistant — 8d9a61c8-3660-4458-8cab-58f5a395d387

Hahaha, então você já está acostumado com teclados fora do padrão! 😂😎

**Fechado! O TTL-8 terá um teclado próprio de 64 teclas, construído com quatro matrizes de membrana 4×4.**

E gostei dessa decisão porque estamos criando um computador com personalidade, não simplesmente reproduzindo um PC convencional.

## Nossa configuração definida

<box border radius="xl" padding={3} gap={2}>
  <row align="center" justify="between">
    **TTL-8 — Teclado Rev. 1**
    <badge color="success">Definido</badge>
  </row>
  <grid columns={4} gap="5px">
    {#each [0,1,2,3] as m}
      <grid-item>
        <box background="surface-secondary" padding={1} radius="md" gap="4px">
          {#each [0,1,2,3] as r}
            <row gap="3px">
              {#each [0,1,2,3] as c}
                <box flex="1" height="26px" background="#64748b" radius="2xs" align="center" justify="center">
                  <text color="#ffffff" size="3xs">{m*4+c+1+r*16}</text>
                </box>
              {/each}
            </row>
          {/each}
        </box>
      </grid-item>
    {/each}
  </grid>
  <grid columns={3} gap={2}>
    {#each [{v:"64",l:"Teclas"},{v:"4 × 16",l:"Matriz lógica"},{v:"4",l:"CIs previstos"}] as s}
      <grid-item>
        <box align="center" gap={1}>
          <title size="lg">{s.v}</title>
          <text color="secondary" size="2xs">{s.l}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Os quatro CIs são uma previsão para a interface básica, ainda sujeita à validação do esquema elétrico.</caption>
</box>

## Como vamos construir

- **4× membranas matriciais 4×4**, lado a lado.
- **1× 74HC139**, para selecionar uma das quatro linhas.
- **2× 74HC244**, para ler as 16 colunas.
- **1× 74HC574**, para armazenar a linha selecionada.
- **16 resistores de pull-up**, além dos componentes de suporte.
- **Firmware na ROM**, para interpretar as 64 posições.

Uma vantagem importante: a CPU poderá identificar teclas pressionadas e soltas, permitindo implementar Shift, Ctrl, combinações e repetição de caracteres.

Como as membranas não costumam ter diodos individuais, precisaremos tratar combinações ambíguas de teclas no firmware.

## Uma ideia para o nosso computador

Eu aproveitaria a liberdade do teclado para criar algumas funções específicas do TTL-8.

Por exemplo, poderíamos reservar teclas para `RUN`, `BREAK`, `RESET` por comando, `HEX` e `MEM`, facilitando o uso do monitor de máquina.

Isso daria uma identidade própria ao computador, lembrando os micros de 8 bits, mas com nossas escolhas.

**Agora temos três grandes partes encaminhadas:** CPU/memória, vídeo composto monocromático e teclado matricial de 64 teclas.

O próximo passo que considero ideal é definir o **layout definitivo das 64 teclas**. Assim, já podemos criar a tabela de caracteres na ROM e fechar o circuito de leitura antes de comprar as membranas.

## user — bbb21771-b23a-45dc-9d99-029c4acd775f

Ahh outra coisa, não vejo necessidade de 3 teclas ao mesmo tempo, vc vê? 

## assistant — cbc31a85-3a8a-49b3-ae0c-4b5d780a39b9

Concordo! 😎 **Para o nosso TTL-8, não vejo necessidade de reconhecer três teclas simultâneas.**

Estamos construindo um computador de 8 bits para digitar comandos, escrever programas e navegar por menus, não um teclado para jogos competitivos.

O que precisamos é:

- **Uma tecla:** digitação normal.
- **Duas teclas:** `SHIFT + letra`, `CTRL + letra` ou `FN + tecla`.
- **Três ou mais:** podemos simplesmente não oferecer suporte.

## Isso simplifica nosso teclado?

Sim, principalmente o firmware. E permite usar as quatro membranas 4×4 sem adicionar diodos individuais.

Mas existe um detalhe elétrico importante: **uma matriz sem diodos pode produzir teclas fantasmas quando três teclas formam três cantos de um retângulo**.

Por isso, não basta dizer ao software para aceitar no máximo duas teclas. Ele precisa detectar estados ambíguos e ignorá-los, evitando registrar uma tecla inexistente.

Com apenas uma ou duas teclas pressionadas, esse problema não ocorre numa matriz passiva convencional.

## Como eu implementaria

| Situação | Comportamento |
|---|---|
| `A` | Digita `a` |
| `SHIFT + A` | Digita `A` |
| `CTRL + C` | Executa a função associada |
| `FN + 1` | Executa função especial |
| `SHIFT + CTRL + A` | Não suportado |
| Três teclas comuns | Ignora a combinação ambígua |

E podemos simplificar ainda mais o firmware: em vez de rastrear muitas teclas simultâneas, mantemos apenas o estado de uma tecla modificadora e uma tecla principal, com debounce e detecção de pressionamento/soltura.

**Minha recomendação é fechar o teclado com suporte a duas teclas simultâneas, sem diodos por tecla.**

Isso atende muito bem ao nosso projeto, mantém o custo baixo e não prejudica a digitação normal. Só precisaremos organizar o layout para que nenhuma função essencial dependa de três teclas.

## user — bbb214ee-14bb-4c05-b731-29fe935991fa

Vamos seguir assim
Sobre o layout o que você recomenda? 

## assistant — ccf3c045-bcc5-43f2-aef3-50405da1bb1e

Eu recomendo um **QWERTY compacto de 64 teclas, com algumas funções inspiradas nos computadores de 8 bits**. 😎

Como teremos quatro membranas 4×4 lado a lado, nosso teclado será comprido e baixo. Eu aproveitaria isso para organizar as letras de forma familiar, deixando a última linha para comandos e navegação.

## Minha proposta: TTL-8 Keyboard Rev. 1

<box border radius="xl" padding={3} gap={2}>
  <row justify="between" align="center">
    <text weight="medium">Layout proposto — 4 × 16</text>
    <badge>64 teclas</badge>
  </row>
  <box background="#252b34" theme="dark" padding={2} radius="lg" gap="4px">
    {#each [
      ["ESC","1","2","3","4","5","6","7","8","9","0","-","=","/","DEL","⌫"],
      ["TAB","Q","W","E","R","T","Y","U","I","O","P","[","]","\\","↑","↵"],
      ["CTRL","A","S","D","F","G","H","J","K","L",";", "'",",",".","←","→"],
      ["SHIFT","Z","X","C","V","B","N","M","SPACE","FN","ALT","RUN","MEM","HEX","↓","BREAK"]
    ] as r}
      <row gap="3px">
        {#each r as k,i}
          <box flex="1" minWidth="0" height="35px" align="center" justify="center" radius="3px" background={["RUN","MEM","HEX","BREAK"].includes(k)?"#476a58":["SHIFT","CTRL","FN","ALT"].includes(k)?"#a4b7c8":"#dce3ea"}>
            <text color={["RUN","MEM","HEX","BREAK"].includes(k)?"#ffffff":"#202630"} size="3xs" weight="medium">{k}</text>
          </box>
        {/each}
      </row>
    {/each}
  </box>
  <caption>Esquema de posições, não escala física. Cada tecla ocupa uma posição da matriz; a tecla SPACE teria o mesmo tamanho das demais.</caption>
</box>

## Por que eu escolheria esse layout?

Ele preserva as letras em uma disposição próxima do QWERTY, mas aproveita a quarta linha para funções próprias do nosso computador.

| Tecla | Função proposta |
|---|---|
| `RUN` | Executar programa |
| `MEM` | Examinar ou editar memória |
| `HEX` | Alternar entrada hexadecimal |
| `BREAK` | Solicitar interrupção do programa |
| `FN` | Acessar símbolos ou funções secundárias |
| `SHIFT` | Maiúsculas e símbolos |
| `CTRL` | Comandos especiais |

Essas funções seriam interpretadas pelo monitor em ROM. `BREAK`, por exemplo, precisará de uma rotina de verificação periódica ou de um mecanismo de interrupção para conseguir parar um programa em execução.

## Dois detalhes que eu ajustaria

**1. A barra de espaço.** Como as membranas 4×4 têm botões iguais, inicialmente usaríamos uma tecla `SPACE` comum. Poderíamos fabricar uma capa maior depois, mas isso exigiria uma solução mecânica que pressione apenas um contato.

**2. A posição das teclas.** Esse desenho mantém QWERTY por familiaridade, mas as letras ficam distribuídas de forma diferente de um teclado convencional. Podemos melhorar o alinhamento quando soubermos as dimensões exatas das membranas.

## E quanto ao português?

Eu não tentaria reproduzir todo o ABNT2 fisicamente. Usaria uma combinação de `FN` com outras teclas para gerar `Ç`, acentos e símbolos adicionais.

Isso preserva posições para comandos importantes e simplifica a primeira versão do firmware.

**Minha recomendação é começar com esse layout e fazer um protótipo em papel, no tamanho real das quatro membranas.** Antes de definir as legendas, poderemos testar se as posições de Enter, Backspace, Shift e Space são confortáveis.

Uma pergunta que influencia bastante o desenho final: **você prefere que o teclado seja otimizado para digitar textos normalmente ou principalmente para escrever Assembly e comandos do TTL-8?** Eu tenderia à segunda opção, mantendo o QWERTY para não dificultar a digitação.

## user — bbb21524-b0eb-475e-9e47-4e749a365425

Vamos seguir assim, não me preocupo com ç ou acentos aos

## assistant — ae58323d-e7ef-4786-ba56-0245aa222b25

Perfeito! 😎 Então vamos manter o teclado **QWERTY simplificado, sem Ç e sem acentos**, priorizando Assembly, comandos e programação.

Isso também simplifica nosso firmware: inicialmente podemos trabalhar apenas com caracteres ASCII.

### Teclado TTL-8 — Rev. 1

Ficam definidas estas características:

- **64 teclas**, em quatro membranas 4×4 lado a lado.
- **Matriz elétrica 4×16**, lida diretamente pela CPU.
- **Duas teclas simultâneas**, suficientes para Shift, Ctrl e Fn.
- **Sem diodos individuais**, com tratamento de combinações ambíguas.
- **Layout QWERTY**, com teclas especiais `RUN`, `MEM`, `HEX` e `BREAK`.
- **Sem necessidade de caracteres acentuados** na primeira versão.

Uma vantagem adicional é que podemos reservar apenas os caracteres necessários na ROM de vídeo. Não precisamos armazenar uma fonte completa com caracteres internacionais.

**Eu manteria a fonte ASCII básica de 96 caracteres imprimíveis**, incluindo letras, números, pontuação e símbolos de programação. Com caracteres de 8×8 pixels, isso ocupa somente **768 bytes** na ROM de caracteres.

Assim, nosso teclado já está suficientemente definido para avançarmos ao esquema eletrônico. A próxima etapa será desenhar a ligação das quatro membranas ao 74HC139 e aos dois 74HC244, incluindo a seleção dos endereços de entrada/saída.

Depois disso, podemos começar a fechar o circuito do TTL-8 módulo por módulo, com componentes e conexões verificáveis antes das compras.

## user — bbb21db6-d4b9-4846-964c-d8628fb87ca5

Pode seguir com o planejamento

## assistant — 3575a393-f951-43e1-bc68-d297c5ee168a

Vamos avançar para o **planejamento técnico do TTL-8, revisão 0.2**. 😎

Agora que decidimos usar quatro teclados matriciais 4×4, podemos fechar uma proposta concreta para a interface e definir como ela vai conversar com nossa CPU.

Minha intenção é que cada módulo tenha um circuito compreensível, possa ser testado separadamente e não precise ser redesenhado quando conectarmos tudo.

## 1. Arquitetura geral do computador

Vamos manter o objetivo original: um computador de 8 bits com CPU construída em lógica 74HC, memória RAM, ROM, vídeo composto monocromático e teclado próprio.

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 285" width="100%">
    <g fill="currentColor" textAnchor="middle">
      <rect x="96" y="8" width="148" height="48" rx="6" fill="#2563eb" fillOpacity=".14" stroke="#60a5fa"/>
      <text x="170" y="27" fontSize="13" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="43" fontSize="10">74HC + microcódigo</text>
      <path d="M170 56 V82" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="9" y="82" width="322" height="32" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="102" fontSize="11">Barramentos: 8 bits dados / 16 bits endereço</text>
      {#each [{x:9,t:"ROM",s:"Firmware"},{x:92,t:"RAM",s:"Programas"},{x:175,t:"VRAM",s:"Texto"},{x:258,t:"I/O",s:"Teclado"}] as a}
        <path d={`M${a.x+36} 114 V133`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={a.x} y="133" width="73" height="45" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+36} y="150" fontSize="11" fontWeight="600">{a.t}</text>
        <text x={a.x+36} y="165" fontSize="9">{a.s}</text>
      {/each}
      <path d="M211 178 V199 M294 178 V199" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="143" y="199" width="136" height="42" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="211" y="215" fontSize="11" fontWeight="600">Gerador CVBS</text>
      <text x="211" y="230" fontSize="9">Vídeo monocromático</text>
      <rect x="284" y="199" width="47" height="42" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="307" y="215" fontSize="9" fontWeight="600">4×4</text>
      <text x="307" y="230" fontSize="9">× 4</text>
      <path d="M211 241 V259" stroke="#94a3b8" strokeWidth="1.5"/>
      <text x="211" y="274" fontSize="10">Monitor com entrada AV</text>
    </g>
  </svg>
</box>

## 2. Circuito do teclado — proposta Rev. 0.2

Para a primeira versão, manteremos a leitura por varredura, controlada pelo software.

A organização será:

- As quatro linhas correspondentes de cada membrana serão interligadas, formando `R0–R3`.
- As quatro colunas de cada membrana permanecerão independentes, formando `C0–C15`.
- O circuito selecionará uma linha de cada vez.
- A CPU lerá as 16 colunas em duas operações de 8 bits.

### Componentes previstos

| Componente | Qtde. | Função |
|---|---:|---|
| 74HC139 | 1 | Decodificar a linha selecionada |
| 74HC244 | 2 | Ler os dois grupos de oito colunas |
| 74HC574 | 1 | Armazenar o índice da linha |
| Resistores de 10 kΩ | 16 | Pull-up das colunas |
| Capacitores de 100 nF | 4 | Desacoplamento |
| Conectores de 8 vias | 4 | Ligação das membranas |

Esses quatro CIs são suficientes como proposta funcional para a interface de matriz, **desde que o barramento principal forneça a seleção e os sinais de leitura/escrita necessários**.

O esquema definitivo ainda precisa detalhar os sinais de habilitação dos 74HC244, o clock de escrita do 74HC574 e o isolamento entre as saídas do 74HC139 e a matriz.

### Ligação das membranas

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 220" width="100%">
    {#each [0,1,2,3] as m}
      <rect x={5+m*84} y="8" width="78" height="61" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={44+m*84} y="27" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">M{m+1}</text>
      <text x={44+m*84} y="42" fontSize="9" textAnchor="middle" fill="currentColor">R0–R3</text>
      <text x={44+m*84} y="56" fontSize="9" textAnchor="middle" fill="currentColor">C{m*4}–C{m*4+3}</text>
      <path d={`M${44+m*84} 69 V94`} stroke="#94a3b8" strokeWidth="1.5"/>
    {/each}
    <path d="M44 94 H296" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="4 3"/>
    <text x="170" y="110" textAnchor="middle" fontSize="9" fill="currentColor">4 linhas compartilhadas / 16 colunas separadas</text>
    <path d="M170 116 V129" stroke="#94a3b8" strokeWidth="1.5"/>
    <rect x="76" y="129" width="188" height="39" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="170" y="145" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">74HC139 + 2×74HC244</text>
    <text x="170" y="159" fontSize="9" textAnchor="middle" fill="currentColor">Seleção e leitura das teclas</text>
    <path d="M170 168 V183" stroke="#94a3b8" strokeWidth="1.5"/>
    <rect x="112" y="183" width="116" height="30" rx="5" fill="#2563eb" fillOpacity=".12" stroke="#60a5fa"/>
    <text x="170" y="202" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">CPU TTL-8</text>
  </svg>
</box>

## 3. Mapa de memória e registradores

Manteremos, por enquanto, o mapa geral definido anteriormente:

| Endereço | Uso | Capacidade |
|---|---|---:|
| `0000–3FFF` | ROM do sistema | 16 KB |
| `4000–BFFF` | RAM | 32 KB |
| `C000–C7FF` | Memória de vídeo | 2 KB |
| `C800–DFFF` | Reservado | 6 KB |
| `E000–E0FF` | Entrada/saída | 256 bytes |
| `E100–FFFF` | Reservado | 7,75 KB |

Para o teclado, reservaremos três registradores:

| Endereço | Acesso | Função |
|---|---|---|
| `E040` | Escrita | Selecionar linha 0–3 |
| `E041` | Leitura | Colunas 0–7 |
| `E042` | Leitura | Colunas 8–15 |

O valor gravado em `E040` será armazenado no 74HC574, e seus dois bits menos significativos selecionarão uma das quatro linhas pelo 74HC139.

Cada 74HC244 entregará oito sinais ao barramento de dados. Apenas o buffer correspondente ao endereço lido poderá habilitar suas saídas, evitando conflito elétrico.

## 4. Como a leitura funciona

A lógica será:

1. A CPU grava `0` em `E040`, selecionando a primeira linha.
2. Lê `E041` e `E042`, obtendo o estado das 16 colunas.
3. Repete o procedimento para as linhas 1, 2 e 3.
4. Compara os estados com a varredura anterior.
5. Quando identifica uma tecla nova, consulta a tabela de caracteres na ROM.

Uma varredura completa exige **quatro escritas e oito leituras** de registradores.

Como nossa CPU será relativamente lenta, isso ainda é perfeitamente administrável para um teclado humano.

## 5. O firmware

O firmware terá três camadas:

**Camada elétrica:** seleciona linhas e lê colunas.

**Camada de eventos:** identifica teclas pressionadas e soltas, aplica debounce e acompanha modificadores.

**Camada de caracteres:** converte posições físicas em ASCII ou comandos especiais.

Por exemplo, se a tecla `A` corresponder à linha 2, coluna 1, o firmware poderá gerar `0x61` (`a`) ou `0x41` (`A`) quando Shift estiver pressionado.

As teclas `RUN`, `MEM`, `HEX` e `BREAK` serão códigos internos, não caracteres ASCII comuns.

Para simplificar, limitaremos a interpretação a duas teclas simultâneas. Também teremos de reconhecer estados ambíguos da matriz sem diodos e evitar gerar eventos falsos.

## 6. Uma observação sobre a CPU

Nosso projeto ainda tem um ponto de atenção: **o circuito da CPU com 92 CIs totais foi apenas estimado, não validado**.

Por isso, eu não começaria comprando toda a lista.

Primeiro devemos confirmar que a CPU consegue realizar as operações necessárias para o teclado, o vídeo e o monitor de sistema. Isso inclui instruções de leitura, escrita, operações lógicas, saltos e manipulação de endereços.

Também precisamos verificar o acesso da CPU à memória de vídeo enquanto o controlador CVBS está lendo caracteres.

## 7. Sequência de desenvolvimento

<list marker="number" connector="solid" gap={2}>
  <list-item>
    **Fechar a interface de teclado**

    Elaborar o esquema elétrico com pinagem, endereços, sinais de controle e conexões das quatro membranas.
  </list-item>
  <list-item>
    **Validar a arquitetura mínima da CPU**

    Definir registradores, ALU, conjunto de instruções e microoperações, verificando se conseguimos executar o firmware.
  </list-item>
  <list-item>
    **Simular CPU, RAM e ROM**

    Executar pequenos programas na simulação, incluindo leitura dos registradores de teclado.
  </list-item>
  <list-item>
    **Projetar o gerador de vídeo composto**

    Definir temporização, fonte de caracteres, VRAM e circuito de saída analógica.
  </list-item>
  <list-item>
    **Integrar os módulos**

    Inicializar o computador, exibir o prompt e receber caracteres do teclado.
  </list-item>
  <list-item>
    **Construir as placas físicas**

    Comprar os componentes por etapa, testar cada módulo e só então realizar a integração completa.
  </list-item>
</list>

## Próxima entrega técnica

Eu começaria pelo **esquema elétrico completo da interface de teclado**, porque já temos os requisitos fechados e podemos verificar esse circuito sem depender da CPU definitiva.

Nesse esquema, quero especificar cada pino dos quatro CIs, os resistores, os conectores, os sinais do barramento e a sequência de leitura. Também verificaremos se é possível eliminar algum CI compartilhando recursos da placa principal.

Depois, partiremos para a CPU, que é a parte mais importante e merece uma revisão rigorosa antes das compras.

Assim, avançamos para um computador real sem transformar as estimativas preliminares em componentes comprados por engano.

## user — bbb21be3-0450-4150-b984-be34e764bd02

Perfeito, vamos seguir

## assistant — 1c308710-61fb-4633-b279-a7e85df3b80e

Então vamos começar a transformar o TTL-8 em um projeto eletrônico de verdade! 😎

Nossa primeira entrega será o **circuito da interface de teclado Rev. 0.3**, com quatro membranas 4×4, formando 64 teclas em uma matriz de 4 linhas × 16 colunas.

Vou separar o que já podemos definir eletricamente do que ainda depende do barramento da CPU.

## 1. Circuito proposto

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 278" width="100%">
    <g fill="currentColor" textAnchor="middle">
      {#each [0,1,2,3] as m}
        <rect x={5+m*84} y="9" width="78" height="52" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={44+m*84} y="28" fontSize="11" fontWeight="600">M{m+1}</text>
        <text x={44+m*84} y="43" fontSize="9">4×4</text>
        <path d={`M${44+m*84} 61 V84`} stroke="#94a3b8" strokeWidth="1.5"/>
      {/each}
      <rect x="6" y="84" width="328" height="30" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="170" y="103" fontSize="11">4 linhas compartilhadas + 16 colunas</text>
      <path d="M75 114 V138 M265 114 V138" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="8" y="138" width="134" height="46" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="75" y="156" fontSize="11" fontWeight="600">74HC139</text>
      <text x="75" y="171" fontSize="9">Seleção de linha</text>
      <rect x="198" y="138" width="134" height="46" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="265" y="156" fontSize="11" fontWeight="600">2 × 74HC244</text>
      <text x="265" y="171" fontSize="9">Leitura das colunas</text>
      <path d="M75 184 V204 H170 M265 184 V204 H170" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="101" y="219" width="138" height="44" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="237" fontSize="11" fontWeight="600">74HC574</text>
      <text x="170" y="251" fontSize="9">Registrador de linha</text>
      <path d="M170 204 V219" stroke="#94a3b8" strokeWidth="1.5"/>
    </g>
  </svg>
  <caption>Diagrama funcional da interface. As ligações individuais e os sinais de seleção são detalhados abaixo.</caption>
</box>

## 2. Componentes e ligações

| Referência | Componente | Função |
|---|---|---|
| U1 | 74HC574 | Armazenar seleção da linha |
| U2 | 74HC139 | Ativar uma das quatro linhas |
| U3 | 74HC244 | Ler colunas C0–C7 |
| U4 | 74HC244 | Ler colunas C8–C15 |
| R1–R16 | 10 kΩ | Pull-up das colunas |
| C1–C4 | 100 nF | Desacoplamento |
| J1–J4 | Conector de 8 vias | Membranas 4×4 |

A alimentação lógica será de **5 V**, compartilhada com a CPU.

### Conexões principais

**U1 — 74HC574**

- Entradas D0–D7 conectadas ao barramento de dados.
- Saídas Q0 e Q1 conectadas às entradas de seleção A e B do 74HC139.
- Clock acionado somente em uma escrita válida no endereço `E040`.
- Saídas permanentemente habilitadas.
- Bits Q2–Q7 reservados, sem conexão na primeira versão.

**U2 — 74HC139**

- A e B recebem Q0 e Q1 de U1.
- Um dos dois decodificadores é utilizado.
- As quatro saídas ativas em nível baixo são conectadas às linhas R0–R3.
- A entrada de habilitação desse decodificador permanece ativa durante a operação normal.

**U3 e U4 — 74HC244**

- U3 recebe C0–C7.
- U4 recebe C8–C15.
- As saídas dos dois CIs compartilham D0–D7.
- Somente um CI pode habilitar suas saídas durante uma leitura válida.

**R1–R16**

Cada coluna recebe um resistor de 10 kΩ conectado ao +5 V. Sem tecla pressionada, a coluna permanece em nível lógico alto.

Quando uma tecla conecta a coluna à linha selecionada, o 74HC244 lê nível baixo.

Uma precaução importante: o 74HC139 mantém as linhas não selecionadas em nível alto. Com duas teclas pressionadas em linhas diferentes, isso pode criar um caminho de corrente entre saídas do decodificador.

**Portanto, não vamos ligar as saídas do 74HC139 diretamente às linhas da matriz na versão física.** Precisamos de acionamento que coloque as linhas não selecionadas em alta impedância, ou de uma solução equivalente com isolamento. Esse ajuste será obrigatório no esquema elétrico final.

## 3. Uma melhoria para reduzir componentes

Existe uma alternativa interessante: substituir o acionamento direto das linhas por um **74HC125**, com quatro buffers de três estados.

Cada saída selecionada poderia levar uma linha ao nível baixo, enquanto as demais permaneceriam em alta impedância.

Isso exige definir corretamente os sinais de habilitação dos buffers e manter as entradas de dados em nível baixo.

Com isso, o circuito ficaria:

| CI | Quantidade |
|---|---:|
| 74HC574 | 1 |
| 74HC139 | 1 |
| 74HC125 | 1 |
| 74HC244 | 2 |
| **Total** | **5** |

O quinto CI evita depender de uma ligação eletricamente inadequada.

Também podemos estudar uma solução com saídas de coletor aberto, que talvez permita simplificar a interface.

## 4. Mapa de registradores

Mantemos os endereços planejados:

| Endereço | Operação |
|---|---|
| `E040` | Selecionar linha |
| `E041` | Ler colunas 0–7 |
| `E042` | Ler colunas 8–15 |

A CPU fará uma escrita e duas leituras por linha.

Os registradores serão acessados pelo mesmo barramento utilizado pela RAM e pela ROM, mas com decodificação própria.

## 5. Como vamos testar

Antes de conectar a CPU, faremos três testes elétricos.

<list marker="number" connector="solid" gap={2}>
  <list-item>
    **Seleção de linhas**

    Aplicar manualmente os valores 0–3 no registrador e verificar que somente uma linha fica ativa.
  </list-item>
  <list-item>
    **Leitura das colunas**

    Pressionar teclas de diferentes módulos e verificar os oito bits recebidos em cada buffer.
  </list-item>
  <list-item>
    **Teclas simultâneas**

    Testar duas teclas em linhas e colunas diferentes, verificando que não há conflitos elétricos nem teclas fantasmas.
  </list-item>
</list>

## 6. O que ainda falta fechar

Antes de transformar isso em um esquema para montagem, precisamos definir três detalhes:

- A lógica exata de decodificação de `E040–E042`, incluindo leitura e escrita.
- O acionamento seguro das quatro linhas da matriz.
- O circuito de reset para iniciar o registrador de seleção em um estado conhecido.

O 74HC574 não possui entrada de reset dedicada, então podemos inicializá-lo por software antes da primeira leitura ou escolher outro registrador com reset.

**Minha recomendação é considerar esta Rev. 0.3 como a arquitetura funcional, não ainda como um esquema pronto para soldar.**

O próximo passo será fechar essas três questões e produzir a pinagem completa, sem ambiguidades, para que possamos simular e depois montar o módulo de teclado com segurança.

## user — bbb21e1a-330c-48f1-b0a8-be0ea7402836

Pode seguir

## assistant — c56eefcf-aac8-4747-bada-4a013a9ef1df

Vamos fechar a **interface de teclado TTL-8 Rev. 0.4**, corrigindo os problemas elétricos identificados na revisão anterior.

Nesta etapa, nosso objetivo é ter um circuito com componentes definidos, conexões verificáveis e comportamento previsível. Ainda não vamos depender de uma CPU pronta para testar o teclado.

## 1. Decisão: usar 74HC139 + 74HC125

Vamos manter os quatro teclados 4×4 e usar um 74HC125 para isolar eletricamente as linhas.

O funcionamento será:

- O 74HC139 seleciona uma das quatro linhas.
- O 74HC125 mantém a linha selecionada em nível baixo.
- As outras três linhas ficam em alta impedância.
- As 16 colunas possuem resistores pull-up.
- Dois 74HC244 entregam os estados das colunas ao barramento de dados.

Isso permite reconhecer até duas teclas simultâneas sem curto-circuitar saídas lógicas.

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 285" width="100%">
    <g fill="currentColor" textAnchor="middle">
      <rect x="91" y="8" width="158" height="40" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="24" fontSize="12" fontWeight="600">74HC574</text>
      <text x="170" y="38" fontSize="9">Seleção de linha</text>
      <path d="M170 48 V66" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="91" y="66" width="158" height="40" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="82" fontSize="12" fontWeight="600">74HC139</text>
      <text x="170" y="96" fontSize="9">Decodificador 2 → 4</text>
      <path d="M170 106 V124" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="91" y="124" width="158" height="40" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="170" y="140" fontSize="12" fontWeight="600">74HC125</text>
      <text x="170" y="154" fontSize="9">4 linhas em três estados</text>
      <path d="M170 164 V183" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="8" y="183" width="324" height="38" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="199" fontSize="11" fontWeight="600">4 membranas 4×4</text>
      <text x="170" y="212" fontSize="9">Matriz 4×16 + pull-ups</text>
      <path d="M170 221 V239" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="91" y="239" width="158" height="38" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="254" fontSize="11" fontWeight="600">2 × 74HC244</text>
      <text x="170" y="268" fontSize="9">Leitura das 16 colunas</text>
    </g>
  </svg>
</box>

## 2. Pinagem do circuito

### U1 — 74HC574

| Pino | Ligação |
|---|---|
| 1 — `/OE` | GND |
| 2 — D0 | Barramento D0 |
| 3 — D1 | Barramento D1 |
| 4–9 — D2–D7 | Barramento D2–D7 |
| 11 — CLK | Pulso de escrita em `E040` |
| 12–19 — Q7–Q0 | Q0 e Q1 usados para seleção |
| 10 — GND | GND |
| 20 — VCC | +5 V |

A saída Q0 irá para a entrada A do 74HC139; Q1 irá para B.

Como o 74HC574 não tem reset dedicado, seu estado após energização é indefinido. Isso não danifica a matriz, mas precisamos inicializá-lo antes de ler o teclado.

### U2 — 74HC139

Usaremos metade do CI:

| Pino | Ligação |
|---|---|
| 1 — `/1G` | GND |
| 2 — 1A | U1.Q0 |
| 3 — 1B | U1.Q1 |
| 4 — `/1Y0` | Habilitação do buffer R0 |
| 5 — `/1Y1` | Habilitação do buffer R1 |
| 6 — `/1Y2` | Habilitação do buffer R2 |
| 7 — `/1Y3` | Habilitação do buffer R3 |
| 8 — GND | GND |
| 16 — VCC | +5 V |

A metade não utilizada terá suas entradas presas em níveis lógicos definidos e sua habilitação desativada.

### U3 — 74HC125

| Buffer | Entrada A | Habilitação `/OE` | Saída Y |
|---|---|---|---|
| 1 | GND | `/1Y0` | R0 |
| 2 | GND | `/1Y1` | R1 |
| 3 | GND | `/1Y2` | R2 |
| 4 | GND | `/1Y3` | R3 |

Assim, somente o buffer selecionado conduz nível baixo. Os demais ficam desconectados eletricamente.

Essa é a principal correção em relação à Rev. 0.3.

### U4 e U5 — 74HC244

Cada CI receberá oito colunas.

| CI | Entradas | Saídas |
|---|---|---|
| U4 | C0–C7 | D0–D7 |
| U5 | C8–C15 | D0–D7 |

Os dois grupos de quatro buffers de cada 74HC244 precisam ter suas entradas de habilitação conectadas ao mesmo sinal de seleção do respectivo CI.

- U4 habilitado exclusivamente na leitura de `E041`.
- U5 habilitado exclusivamente na leitura de `E042`.
- Em qualquer outro acesso, ambos ficam em alta impedância.

**Atenção:** os sinais de habilitação deverão ser combinados com a decodificação de endereço e o sinal de leitura da CPU. Não basta conectar diretamente o endereço aos pinos `/OE`.

## 3. Decodificação dos endereços

Vamos definir três sinais ativos em nível baixo:

| Sinal | Condição |
|---|---|
| `/KBD_ROW_WR` | Escrita válida em `E040` |
| `/KBD_LOW_RD` | Leitura válida em `E041` |
| `/KBD_HIGH_RD` | Leitura válida em `E042` |

Esses sinais virão do módulo geral de decodificação de endereços do TTL-8.

Há um detalhe importante no clock do 74HC574: ele captura dados na borda de subida. Portanto, não podemos simplesmente ligar um sinal de escrita ativo em nível baixo sem verificar o momento em que os dados estão estáveis.

A solução definitiva deverá garantir os tempos de setup e hold em relação à borda de captura. Podemos usar a fase apropriada do clock da CPU ou um pulso de escrita gerado pela lógica de controle.

## 4. Resistores e alimentação

Cada coluna terá um resistor de 10 kΩ para +5 V.

Quando nenhuma tecla estiver pressionada:

\[
C_n=1
\]

Quando uma tecla conecta a coluna à linha ativa:

\[
C_n=0
\]

Os valores lidos são, portanto, ativos em nível baixo.

Para o firmware, podemos inverter os bits e trabalhar com `1 = tecla pressionada`.

Cada CI terá um capacitor cerâmico de 100 nF próximo aos pinos de alimentação. Também recomendo um capacitor de reserva de 10 µF na entrada de alimentação da placa.

## 5. Comportamento com duas teclas

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Exemplo de varredura</text>
  <grid columns={4} gap={2}>
    {#each [{n:"R0",v:"C3",s:"Pressionada"},{n:"R1",v:"—",s:"Livre"},{n:"R2",v:"C7",s:"Pressionada"},{n:"R3",v:"—",s:"Livre"}] as a}
      <grid-item>
        <box background="surface-secondary" radius="md" padding={2} align="center" gap={1}>
          <text weight="medium">{a.n}</text>
          <text color={a.v==="—"?"tertiary":"default"} weight="medium">{a.v}</text>
          <caption>{a.s}</caption>
        </box>
      </grid-item>
    {/each}
  </grid>
  <text size="sm">A CPU identifica as posições R0/C3 e R2/C7 durante a varredura completa. Como somente duas teclas estão pressionadas, não há formação de um retângulo de três contatos capaz de produzir uma tecla fantasma.</text>
</box>

Para três ou mais teclas, o firmware pode rejeitar estados ambíguos. Entretanto, como não existem diodos individuais, ele não consegue distinguir todos os padrões reais de contatos de padrões produzidos por ghosting. Isso é uma limitação aceita do nosso projeto.

## 6. Revisão da lista de componentes

<box border radius="lg" padding={3} gap={2}>
  <row justify="between" align="center">
    <text color="secondary" weight="medium">Interface de teclado Rev. 0.4</text>
    <badge color="success">Arquitetura definida</badge>
  </row>
  <title size="2xl" color="default" tabularNums>5 CIs</title>
  <text color="secondary" size="sm">74HC574 ×1, 74HC139 ×1, 74HC125 ×1 e 74HC244 ×2.</text>
  <divider/>
  <text size="sm">Além disso: 16 resistores de 10 kΩ, 5 capacitores de 100 nF, 1 capacitor de 10 µF, conectores e as quatro membranas.</text>
</box>

Essa contagem não inclui a decodificação de endereços compartilhada com a placa principal nem eventuais componentes adicionais exigidos pela implementação física.

## 7. O que considero fechado

Já podemos considerar definidas a topologia 4×16, a leitura em dois bytes, a seleção de uma linha por vez e o isolamento por três estados.

Ainda precisamos validar a pinagem completa dos buffers, os tempos dos sinais de controle e a integração com o barramento. Essas verificações são necessárias antes de fabricar uma PCB.

**A próxima etapa é projetar a CPU mínima do TTL-8**, começando pelos registradores e pelo barramento interno. Com isso, conseguiremos definir os sinais de leitura/escrita que faltam e construir uma simulação integrada de CPU, ROM, RAM e teclado.

A partir daí, teremos condições de executar nosso primeiro programa real em Assembly: inicializar o teclado, detectar uma tecla e armazenar seu código ASCII na RAM.

## user — bbb21134-43b9-4566-a3d1-dceaf6bf61c4

Pode seguir com o projeto

## assistant — 06c69670-21db-4ca2-b5c5-8c556b26d845

Vamos avançar para o coração do nosso computador: **a CPU TTL-8**.

Até agora definimos o teclado de 64 teclas, o mapa preliminar de memória e a proposta de vídeo composto monocromático. Agora precisamos projetar o processador que vai controlar tudo isso.

Quero manter uma regra durante o desenvolvimento: **cada circuito precisa ter uma função definida, sinais elétricos coerentes e um teste de validação antes de comprarmos os componentes.**

# TTL-8 — CPU Rev. 0.1

## 1. Arquitetura proposta

Minha recomendação é uma CPU de 8 bits, com arquitetura de acumulador, microprogramada e barramento de endereços de 16 bits.

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 345" width="100%">
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <rect x="91" y="8" width="158" height="36" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="30" fontWeight="600">Unidade de controle</text>
      <path d="M170 44 V65" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="7" y="65" width="326" height="34" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="86" fontWeight="600">Barramento interno de 8 bits</text>
      {#each [{x:7,t:"A",s:"8 bits"},{x:91,t:"B",s:"8 bits"},{x:175,t:"ALU",s:"8 bits"},{x:259,t:"FLAGS",s:"Z, C"}] as a}
        <path d={`M${a.x+37} 99 V120`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={a.x} y="120" width="74" height="49" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+37} y="140" fontWeight="600">{a.t}</text>
        <text x={a.x+37} y="155" fontSize="9">{a.s}</text>
      {/each}
      <path d="M170 169 V190" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="92" y="190" width="156" height="35" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="212" fontWeight="600">PC + MAR (16 bits)</text>
      <path d="M170 225 V244" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="7" y="244" width="326" height="34" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="265" fontWeight="600">Barramento de endereços de 16 bits</text>
      <path d="M170 278 V295" stroke="#94a3b8" strokeWidth="1.5"/>
      {#each [{x:7,t:"ROM"},{x:91,t:"RAM"},{x:175,t:"VRAM"},{x:259,t:"I/O"}] as a}
        <rect x={a.x} y="295" width="74" height="38" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".1"/>
        <text x={a.x+37} y="318" fontWeight="600">{a.t}</text>
      {/each}
    </g>
  </svg>
  <caption>Diagrama conceitual, não um esquema elétrico. Os caminhos de dados, multiplexadores e sinais de controle ainda serão detalhados.</caption>
</box>

A CPU não utilizará Arduino, ESP32 ou outro microcontrolador para executar instruções. Seu processamento será realizado pelos circuitos lógicos.

## 2. Registradores

Proponho começar com os seguintes registradores:

| Registrador | Largura | Função |
|---|---:|---|
| A | 8 bits | Acumulador principal |
| B | 8 bits | Segundo operando da ALU |
| PC | 16 bits | Endereço da próxima instrução |
| MAR | 16 bits | Endereço de acesso à memória |
| MDR | 8 bits | Dados lidos ou escritos |
| IR | 8 bits | Instrução atual |
| FLAGS | 2 bits | Zero e Carry |

O registrador X, que apareceu nas primeiras estimativas, ficará fora da CPU mínima. Poderemos acrescentá-lo posteriormente se os programas demonstrarem necessidade.

Isso reduz os caminhos de dados e simplifica o controle.

## 3. Unidade lógica e aritmética

A ALU realizará inicialmente seis operações:

| Operação | Resultado |
|---|---|
| ADD | A + B |
| SUB | A − B |
| AND | A AND B |
| OR | A OR B |
| XOR | A XOR B |
| NOT | NOT A |

Para construir essa unidade, podemos combinar dois 74HC283 com portas lógicas e multiplexadores 74HC157.

A subtração pode compartilhar o somador usando complemento de dois:

\[
A-B=A+\overline{B}+1
\]

Isso evita construir um circuito subtrator independente.

As flags terão dois significados principais: `Z` indica resultado zero e `C` indica transporte na soma. Para subtração, precisaremos definir explicitamente se `C` significa empréstimo ou ausência de empréstimo.

## 4. Primeiro conjunto de instruções

Em vez de criar dezenas de instruções, vamos começar com um conjunto pequeno, mas suficiente para executar programas.

| Instrução | Bytes | Função |
|---|---:|---|
| NOP | 1 | Não faz operação |
| LDA #n | 2 | Carrega valor imediato em A |
| LDB #n | 2 | Carrega valor imediato em B |
| LDA addr | 3 | Lê memória para A |
| STA addr | 3 | Grava A na memória |
| ADD | 1 | A = A + B |
| SUB | 1 | A = A − B |
| AND | 1 | A = A AND B |
| OR | 1 | A = A OR B |
| XOR | 1 | A = A XOR B |
| JMP addr | 3 | Salto absoluto |
| JZ addr | 3 | Salta se Z = 1 |
| JNZ addr | 3 | Salta se Z = 0 |

Também recomendo incluir `CMP` e uma instrução de parada ou espera antes de fechar o conjunto definitivo.

Essas instruções são uma **proposta de ISA**, ainda sem opcodes atribuídos. Precisaremos verificar se cada uma pode ser implementada com os registradores e sinais de controle escolhidos.

## 5. Como a CPU executará uma instrução

Vamos usar microcódigo armazenado em EEPROM.

Por exemplo, para executar:

```asm
LDA #42
```

A CPU deverá:

1. Colocar o PC no barramento de endereços.
2. Ler o opcode da ROM para o IR.
3. Incrementar o PC.
4. Ler o byte imediato `42`.
5. Armazenar esse byte no registrador A.
6. Incrementar o PC e iniciar a próxima instrução.

Essas ações ocorrerão em diferentes microetapas.

A EEPROM de controle determinará quais registradores recebem dados, qual fonte dirige o barramento e quando a memória deve ser acessada.

Precisamos projetar essa sequência respeitando os tempos de propagação dos CIs e impedindo que dois componentes dirijam o mesmo barramento simultaneamente.

## 6. Clock

Minha proposta é começar com um clock manual ou muito lento durante os testes e depois aumentar gradualmente.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Metas de frequência</text>
  <grid columns={3} gap={2}>
    {#each [{v:"1 Hz",s:"Depuração"},{v:"10 kHz",s:"Primeiros testes"},{v:"1 MHz",s:"Meta futura"}] as a}
      <grid-item>
        <box background="surface-secondary" radius="md" padding={2} gap={1} align="center">
          <title size="lg" color="default" tabularNums>{a.v}</title>
          <caption>{a.s}</caption>
        </box>
      </grid-item>
    {/each}
  </grid>
</box>

O valor de 1 MHz é uma meta, não uma frequência garantida. A velocidade real dependerá do caminho crítico entre os registradores, a EEPROM de microcódigo, a lógica de controle e a memória.

## 7. Primeiro programa de teste

Antes de integrar teclado e vídeo, quero que a CPU consiga executar um programa muito simples:

```asm
        LDA #10
        LDB #20
        ADD
        STA $4000

LOOP:   JMP LOOP
```

O resultado esperado é:

<box border radius="lg" padding={3} gap={2}>
  <row justify="between" align="center">
    <text color="secondary">Memória RAM — endereço $4000</text>
    <badge color="success">Resultado esperado</badge>
  </row>
  <row align="baseline" gap={2}>
    <title size="2xl" color="default" tabularNums>0x1E</title>
    <text color="secondary">= 30 decimal</text>
  </row>
  <text size="sm">Se a RAM receber esse valor, teremos validado a busca de instruções, carga de registradores, operação aritmética, escrita em memória e salto.</text>
</box>

Esse programa será nosso primeiro marco funcional.

## 8. Próximas etapas de engenharia

<list marker="number" connector="solid" gap={2}>
  <list-item>
    **Definir os caminhos de dados da CPU**

    Especificar como PC, MAR, MDR, A, B, IR e ALU compartilham os barramentos.
  </list-item>
  <list-item>
    **Atribuir os opcodes**

    Criar uma tabela binária fixa para as instruções.
  </list-item>
  <list-item>
    **Definir os sinais de controle**

    Estabelecer habilitação de registradores, fontes do barramento, operações da ALU e comandos de memória.
  </list-item>
  <list-item>
    **Construir o microcódigo**

    Descrever cada microetapa de cada instrução e calcular a capacidade necessária das EEPROMs.
  </list-item>
  <list-item>
    **Simular a execução**

    Verificar o programa de soma, os saltos e o comportamento do barramento antes da montagem.
  </list-item>
</list>

## Decisão importante

**Eu manteria a CPU sem pilha e sem interrupções nesta primeira revisão.** Isso simplifica bastante o hardware inicial, embora limite chamadas de sub-rotina, tratamento de eventos e programas mais complexos.

O teclado poderá ser consultado por polling. Para o `BREAK` interromper programas, inicialmente dependeremos de verificações feitas pelo software.

Depois de validar a CPU mínima, podemos avaliar a inclusão de pilha e instruções `CALL`/`RET`, que seriam muito úteis para o monitor em ROM.

O próximo trabalho será definir o **datapath completo**, com todos os sinais de entrada e saída dos registradores e uma primeira estimativa de CIs baseada nos circuitos efetivamente necessários — em vez de confiar na antiga estimativa de aproximadamente 92 chips.

Assim começaremos a sair da arquitetura conceitual e entrar no projeto lógico verificável do nosso TTL-8.

## user — bbb21afb-e6bb-4173-81ee-1e0ca966c3d7

Perfeito, com esse hardware, seria possível fazer upgrades de software e quem sabe um dia, até fazer um desenho na tela? 

## assistant — 378651b2-fe1f-4885-b020-480451c76fbf

**Sim! E essa é uma das partes mais interessantes do nosso TTL-8!** 😁

Com a arquitetura que estamos projetando, poderemos atualizar o sistema operacional, desenvolver novos programas e, futuramente, até criar desenhos e jogos na tela.

Mas existe uma decisão de hardware que eu gostaria de tomar **agora**, justamente para não limitar essas possibilidades no futuro.

## 1. Nosso TTL-8 poderá receber atualizações de software?

Sim. Teremos duas formas principais:

- **Atualização da ROM:** gravar uma nova versão do firmware em EEPROM, adicionando comandos, funções e melhorias ao sistema.
- **Programas na RAM:** carregar e executar programas sem modificar o firmware original.

Isso significa que poderemos começar com um monitor simples:

<box background="#101510" theme="dark" radius="lg" padding={3} gap={1}>
  <row justify="between" align="center">
    <text color="#78f78b" weight="medium" size="xs">TTL-8 COMPUTER</text>
    <text color="#78f78b" size="2xs">MONOCHROME</text>
  </row>
  <divider color="#315b37"/>
  <box padding={2} gap={1}>
    <text color="#8dff9b" preserveWhitespace size="sm">TTL-8 MONITOR V1.0</text>
    <text color="#8dff9b" preserveWhitespace size="sm">32768 BYTES RAM</text>
    <text color="#8dff9b" preserveWhitespace size="sm">READY.</text>
    <text color="#8dff9b" preserveWhitespace size="sm">{"> HELP"}</text>
    <text color="#8dff9b" preserveWhitespace size="sm">MEM  RUN  LOAD  DUMP</text>
    <text color="#8dff9b" preserveWhitespace size="sm">{"> _"}</text>
  </box>
</box>

E depois evoluir para um interpretador BASIC, editor de texto, assembler ou outros programas.

A EEPROM poderá ser regravada, embora inicialmente isso possa exigir um gravador externo. Atualização diretamente pelo próprio TTL-8 seria uma funcionalidade posterior, dependente de circuitos e rotinas apropriados.

## 2. E desenhar na tela?

Aqui temos duas possibilidades.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="retro 8 bit monochrome ASCII text mode pixel art computer screen green phosphor block characters" aspectRatio="4:3" maxWidth="152px"/>
    <box flex="1" gap={1}>
      **Modo texto — já previsto**

      Com nossa resolução de 32×24 caracteres, podemos montar desenhos usando caracteres ASCII ou caracteres gráficos personalizados.

      É possível fazer menus, molduras, mapas e jogos simples.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro monochrome green phosphor 8 bit computer pixel art landscape mountain sun tree simple bitmap graphics" aspectRatio="4:3" maxWidth="152px"/>
    <box flex="1" gap={1}>
      **Modo gráfico — evolução desejada**

      Cada pixel pode ser controlado individualmente. Poderemos desenhar linhas, círculos, sprites, paisagens e jogos com gráficos reais.
    </box>
  </row>
</box>

O detalhe é que **o modo gráfico exige um controlador de vídeo preparado para isso**. Não basta atualizar o firmware de um circuito que só sabe buscar caracteres.

## 3. Minha proposta: preparar o hardware para gráficos desde o início

Nossa memória de vídeo planejada é de 2 KB.

Com um bit por pixel, ela permite algumas resoluções interessantes:

| Resolução | Memória necessária | Cabe em 2 KB? |
|---|---:|---|
| 128×96 | 1.536 bytes | Sim |
| 128×128 | 2.048 bytes | Sim |
| 160×100 | 2.000 bytes | Sim |
| 256×192 | 6.144 bytes | Não |

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Comparação de memória gráfica</text>
  {#each [{name:"128×96",v:1536},{name:"128×128",v:2048},{name:"160×100",v:2000},{name:"256×192",v:6144}] as d}
    <box gap={1}>
      <row justify="between">
        <text size="sm">{d.name}</text>
        <text color="secondary" size="xs" tabularNums>{d.v.toLocaleString("pt-BR")} bytes</text>
      </row>
      <box background="surface-tertiary" height="9px" radius="full" clip>
        <box background={d.v<=2048?"#16a34a":"#d97706"} width={`${Math.min(100,d.v/2048*100)}%`} height="100%" radius="full"/>
      </box>
    </box>
  {/each}
  <caption>Referência: 2.048 bytes disponíveis. A barra laranja ultrapassa a capacidade, sendo exibida no limite da escala.</caption>
</box>

Eu escolheria **128×96 pixels monocromáticos** como nosso primeiro modo gráfico.

Essa resolução tem algumas vantagens: usa apenas 1,5 KB, deixa 512 bytes livres na VRAM e permite endereçamento relativamente simples.

## 4. Como seria desenhar um pixel?

Com 128 pixels por linha, cada linha ocupa 16 bytes.

O endereço de um pixel seria:

\[
\text{endereço}=C000+(y\times16)+\lfloor x/8\rfloor
\]

O bit correspondente seria:

\[
\text{bit}=7-(x\bmod8)
\]

Para acender um pixel, o software lê o byte, ativa o bit correspondente e grava o resultado novamente.

Por exemplo, um programa futuro poderia oferecer comandos como:

```asm
; Exemplo conceitual de API grafica
; Ainda nao e Assembly executavel da CPU

PSET  40, 20
LINE  10, 10, 100, 70
RECT  20, 20, 50, 30
CIRCLE 64, 48, 15
```

Esses comandos seriam implementados em software, utilizando as instruções reais da nossa CPU.

## 5. A mudança de hardware que eu faria agora

Eu projetaria o módulo de vídeo com dois modos selecionáveis:

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    **Controlador de vídeo TTL-8**
    <badge>Proposta Rev. 0.2</badge>
  </row>
  <svg viewBox="0 0 330 182" width="100%">
    <g textAnchor="middle" fill="currentColor" fontSize="11">
      <rect x="5" y="8" width="100" height="37" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="55" y="30">VRAM 2 KB</text>
      <path d="M105 26 H134" stroke="#94a3b8" strokeWidth="1.5"/>
      <path d="M134 26 V69 M134 26 V117" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="151" y="51" width="169" height="38" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="235" y="67" fontWeight="600">Modo texto</text>
      <text x="235" y="81" fontSize="9">32×24 caracteres</text>
      <rect x="151" y="99" width="169" height="38" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="235" y="115" fontWeight="600">Modo gráfico</text>
      <text x="235" y="129" fontSize="9">128×96 pixels</text>
      <path d="M320 70 H325 V151 H235 M320 118 H325" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="151" y="151" width="169" height="27" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="235" y="169">Saída CVBS</text>
    </g>
  </svg>
  <caption>Dois caminhos de interpretação da VRAM compartilhando a geração de sincronismo e a saída de vídeo.</caption>
</box>

O modo texto continuará sendo o padrão ao ligar o computador. Um registrador de controle, por exemplo `E020`, poderia selecionar o modo gráfico.

**Importante:** os dois modos não estarão automaticamente disponíveis apenas por reservar esse registrador. Precisaremos construir os caminhos de leitura da VRAM, a seleção entre eles e a temporização apropriada. Isso aumenta a complexidade e o número de CIs do módulo de vídeo.

## 6. E poderíamos criar jogos?

Sim! Alguns exemplos realistas:

- Pong, com duas raquetes e uma bola.
- Snake, movimentando uma cobrinha pelo cenário.
- Um editor de desenhos com o teclado.
- Jogos de labirinto e pequenas aventuras.
- Um ambiente gráfico simples, com janelas desenhadas em software.

O desempenho dependerá da frequência efetiva da CPU, das instruções disponíveis e da quantidade de memória que conseguirmos atualizar por quadro. Não devemos prometer animação fluida antes de medir isso.

## Minha recomendação para o projeto

Eu faria uma pequena mudança no planejamento:

**Manteria a CPU de 8 bits e a VRAM de 2 KB, mas incluiria o modo gráfico de 128×96 como requisito de projeto desde agora.**

Não precisamos construir os dois modos imediatamente. Podemos primeiro colocar o modo texto funcionando e depois adicionar o circuito gráfico, desde que a placa seja projetada com os sinais e a expansão necessários.

Isso preserva o espírito do TTL-8: começar com um computador simples, funcional e construído por nós, mas que possa crescer ao longo dos anos.

E tem algo ainda mais interessante: com um pequeno editor gráfico na ROM ou na RAM, poderemos um dia ligar nosso computador, digitar `DRAW` e **desenhar diretamente na tela usando o teclado que construímos**.

## user — bbb2154d-acc1-4d77-8430-953074fb8f08

Podemos já seguir com essa evolução, como fica o Hardware? Aumenta muito? 

## assistant — ec4140b5-3785-480f-b86b-b09f71ca4d07

**Podemos, sim! E eu recomendo incluir o modo gráfico agora, antes de fecharmos o circuito de vídeo.** 😁

A boa notícia é que não precisamos modificar a CPU, aumentar o barramento de dados ou abandonar nossa proposta de usar componentes 74HC.

O aumento ficará concentrado na placa de vídeo.

Minha sugestão é projetar o TTL-8 com **dois modos nativos: texto 32×24 e gráficos monocromáticos 128×96**.

## 1. Como ficará o hardware

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">TTL-8 — arquitetura com vídeo gráfico</text>
  <svg viewBox="0 0 340 330" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="95" y="6" width="150" height="39" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="22" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="36" fontSize="9">8 bits / 16 bits endereço</text>
      <path d="M170 45 V65" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="8" y="65" width="324" height="30" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="170" y="84">Barramento principal</text>
      <path d="M51 95 V112 M170 95 V112 M289 95 V112" stroke="#94a3b8" strokeWidth="1.5"/>
      {#each [{x:8,t:"ROM",s:"16 KB"},{x:127,t:"RAM",s:"32 KB"},{x:246,t:"I/O",s:"Teclado"}] as a}
        <rect x={a.x} y="112" width="86" height="42" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+43} y="129" fontWeight="600">{a.t}</text>
        <text x={a.x+43} y="144" fontSize="9">{a.s}</text>
      {/each}
      <path d="M170 154 V172" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="8" y="172" width="324" height="145" rx="7" stroke="#4ade80" strokeWidth="1.5" fill="#16a34a" fillOpacity=".05"/>
      <text x="170" y="190" fontWeight="600">Módulo de vídeo TTL-8</text>
      <rect x="23" y="202" width="113" height="37" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="79" y="218">VRAM 2 KB</text>
      <text x="79" y="230" fontSize="9">6116 SRAM</text>
      <rect x="204" y="202" width="113" height="37" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="260" y="218">Temporização</text>
      <text x="260" y="230" fontSize="9">HSync / VSync</text>
      <path d="M79 239 V255 H170 M260 239 V255 H170" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="57" y="262" width="105" height="28" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="109" y="280">Texto 32×24</text>
      <rect x="178" y="262" width="105" height="28" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="230" y="280">Gráfico 128×96</text>
      <path d="M170 290 V300" stroke="#94a3b8" strokeWidth="1.5"/>
      <text x="170" y="311" fontSize="10">Seletor de modo → CVBS</text>
    </g>
  </svg>
  <caption>Arquitetura funcional. Os caminhos de endereçamento da VRAM e de geração dos pixels ainda precisam de detalhamento elétrico.</caption>
</box>

A principal diferença é que a placa de vídeo passará a interpretar os bytes da VRAM de duas maneiras.

No modo texto, cada byte representa um caractere. No modo gráfico, cada bit representa um pixel.

## 2. Quanto aumenta o número de componentes?

A estimativa inicial do módulo de vídeo era de aproximadamente 25 CIs, mas ainda não tínhamos validado seu circuito completo.

Para acrescentar o modo gráfico, eu reservaria inicialmente:

| Circuito adicional | CIs estimados |
|---|---:|
| Seleção entre endereçamento texto/gráfico | 2–3 |
| Contadores/divisores e controle de linhas gráficas | 2–3 |
| Seleção de bits e caminho gráfico | 1–2 |
| Registrador de modo e lógica de controle | 1–2 |
| **Total adicional estimado** | **6–10** |

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">Estimativa de complexidade da placa de vídeo</text>
  <row align="baseline" justify="between">
    <box gap={1}>
      <title size="xl" color="default" tabularNums>~25</title>
      <caption>Vídeo somente texto</caption>
    </box>
    <icon name="arrow-right" color="tertiary" size="lg"/>
    <box gap={1}>
      <title size="xl" color="default" tabularNums>~31–35</title>
      <caption>Texto + gráficos</caption>
    </box>
  </row>
  <box background="surface-tertiary" height="12px" radius="full" clip>
    <row height="100%" gap="0">
      <box background="#64748b" width="71%" height="100%"/>
      <box background="#16a34a" flex="1" height="100%"/>
    </row>
  </box>
  <caption>Estimativa de planejamento, não uma contagem verificada por esquema. A implementação real pode exigir mais ou menos componentes.</caption>
</box>

Portanto, **não parece um aumento absurdo**, especialmente porque a CPU, a ROM principal e o teclado permanecem iguais.

Mas há uma ressalva: se tentássemos adicionar gráficos depois de fabricar uma placa exclusivamente textual, poderíamos precisar redesenhar boa parte do controlador de vídeo. Por isso vale decidir agora.

## 3. Como funcionará o modo gráfico

Vamos usar a mesma SRAM 6116 de 2 KB.

<grid columns={2} gap={3}>
  <grid-item>
    <box border radius="lg" padding={2} gap={2}>
      <text weight="medium" size="sm">Modo texto</text>
      <box background="#101510" theme="dark" aspectRatio="4/3" radius="md" padding={2} gap={1}>
        <text color="#8dff9b" size="2xs" preserveWhitespace>TTL-8 READY</text>
        <text color="#8dff9b" size="2xs" preserveWhitespace>{"> HELP"}</text>
        <text color="#8dff9b" size="2xs" preserveWhitespace>RUN MEM DUMP</text>
        <text color="#8dff9b" size="2xs" preserveWhitespace>{"> _"}</text>
      </box>
      <caption>32×24 caracteres, 768 bytes de tela</caption>
    </box>
  </grid-item>
  <grid-item>
    <box border radius="lg" padding={2} gap={2}>
      <text weight="medium" size="sm">Modo gráfico</text>
      <box background="#101510" theme="dark" aspectRatio="4/3" radius="md" padding={2}>
        <svg viewBox="0 0 128 96" width="100%" height="100%">
          <rect width="128" height="96" fill="#101510"/>
          <circle cx="95" cy="21" r="12" fill="none" stroke="#8dff9b" strokeWidth="1.5"/>
          <path d="M0 69 L29 35 L48 53 L76 19 L128 68 M0 80 L35 59 L64 78 L98 48 L128 74" stroke="#8dff9b" strokeWidth="1.5" fill="none"/>
          <path d="M14 80 V59 M7 67 L14 52 L21 67 M14 67 L6 73 M14 67 L23 73" stroke="#8dff9b" strokeWidth="1.5" fill="none"/>
          <path d="M0 87 H128" stroke="#8dff9b" strokeWidth="1"/>
        </svg>
      </box>
      <caption>128×96 pixels, 1.536 bytes de tela</caption>
    </box>
  </grid-item>
</grid>

O modo gráfico terá 16 bytes por linha, porque:

\[
128 \div 8 = 16
\]

E 96 linhas:

\[
16 \times 96 = 1536\text{ bytes}
\]

Assim, o framebuffer cabe inteiramente nos 2.048 bytes disponíveis.

## 4. A principal dificuldade: o acesso à VRAM

Aqui está o ponto mais importante do hardware.

O controlador de vídeo precisa ler a SRAM continuamente para produzir a imagem, enquanto a CPU precisa escrever nela para atualizar a tela.

Como a 6116 possui uma única porta de acesso, teremos que compartilhar seu uso.

Eu proponho **arbitragem por ciclos**, na qual o vídeo tem prioridade durante a leitura dos pixels e a CPU espera quando necessário.

Isso exige:

- Multiplexação dos endereços da VRAM.
- Controle dos sinais `/OE`, `/WE` e `/CS`.
- Isolamento correto do barramento de dados.
- Um sinal `WAIT` ou mecanismo equivalente para suspender a CPU.
- Temporização que garanta acesso à memória sem corromper a imagem.

Esse circuito é necessário mesmo no modo texto. O modo gráfico torna sua validação ainda mais importante.

## 5. Uma decisão sobre a resolução

Eu manteria 128×96 pixels, mas com uma característica interessante: **cada linha gráfica poderá ser repetida verticalmente**.

Isso ajuda a encaixar a imagem na região ativa do sinal composto.

Também podemos duplicar pixels horizontalmente, produzindo uma imagem com proporções mais agradáveis no monitor.

O hardware precisará definir exatamente como os 128 pixels serão distribuídos dentro de cada linha de vídeo e quantas linhas físicas representarão cada linha lógica.

Ainda não devemos fixar o clock de pixels antes de calcular a temporização completa do CVBS.

## 6. Atualizações futuras de software

Com o modo gráfico no hardware, poderemos adicionar funções progressivamente, sem trocar a CPU.

<list marker="number" connector="solid" gap={2}>
  <list-item>
    **Firmware 1.0 — Monitor**

    Prompt, leitura do teclado, comandos de memória e execução de programas.
  </list-item>
  <list-item>
    **Firmware 1.1 — Ferramentas**

    Editor hexadecimal, pequenos utilitários e carregamento de programas.
  </list-item>
  <list-item>
    **Firmware 1.2 — Biblioteca gráfica**

    Rotinas `PSET`, `LINE`, `RECT`, `CLEAR` e desenho de caracteres.
  </list-item>
  <list-item>
    **Firmware 2.0 — Ambiente gráfico**

    Editor de desenhos, menus gráficos e pequenos jogos.
  </list-item>
</list>

Essas versões são metas de desenvolvimento, não funcionalidades já implementadas.

## 7. O que eu mudaria no planejamento do TTL-8

| Módulo | Decisão |
|---|---|
| CPU | Mantemos 8 bits, 16 bits de endereço |
| ROM | Mantemos 16 KB |
| RAM | Mantemos 32 KB |
| Teclado | Mantemos 4 matrizes 4×4 |
| VRAM | Mantemos 2 KB |
| Vídeo | Dois modos: texto e gráfico |
| Saída | CVBS monocromático |
| Expansão | Reservar sinais para upgrades |

O único módulo que precisará ser ampliado substancialmente é o controlador de vídeo.

**Minha recomendação é aprovar essa evolução como requisito definitivo do TTL-8.** O próximo trabalho de engenharia deve ser calcular a temporização do vídeo composto e definir o circuito de acesso à VRAM antes de escolher os CIs exatos.

Assim poderemos construir uma placa que já nasce preparada para mostrar nosso primeiro desenho, sem precisar substituir o computador inteiro no futuro.

## user — bbb21b2b-a1e2-4145-ba68-6987054b371c

Teria algum outro jeito de termos um modo gráfico? 

## assistant — 427d9b2f-454d-4d76-bc85-85157076e598

Sim! 😁 E existem alternativas que podem ser **mais simples e econômicas** do que construir dois circuitos de vídeo completos, um para texto e outro para gráficos.

Pensando no nosso TTL-8, eu estudaria principalmente quatro arquiteturas.

## 1. Quatro maneiras de implementar gráficos

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="green monochrome retro 1980s computer screen ASCII art mountain landscape using block characters" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **A. Caracteres gráficos programáveis**

      Mantemos o controlador de texto 32×24, mas permitimos redefinir o desenho dos caracteres.

      Podemos criar blocos, linhas, sprites e pequenos desenhos usando a grade de caracteres.

      <text color="success" weight="medium" size="xs">Pouca lógica adicional</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="monochrome green retro pixel art simple drawing on black CRT computer screen 128x96" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **B. Framebuffer único com texto desenhado por software**

      Eliminamos o modo texto em hardware. A VRAM passa a armazenar pixels, e o próprio firmware desenha as letras na tela.

      Teríamos gráficos reais e texto, usando um único circuito de vídeo.

      <text color="success" weight="medium" size="xs">Minha opção preferida</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro monochrome computer tile based pixel game screen simple 8x8 sprites black green" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **C. Vídeo baseado em tiles**

      A tela é formada por pequenos blocos gráficos de 8×8 pixels, selecionados por índices em memória.

      É parecido com a abordagem usada em vários computadores e consoles antigos.

      <text color="secondary" weight="medium" size="xs">Bom para jogos e mapas</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="vintage 8 bit monochrome vector graphics wireframe geometric drawing green CRT screen" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **D. Coprocessador gráfico dedicado**

      Construímos um segundo circuito que recebe comandos da CPU para desenhar pixels, linhas e formas.

      É expansível, mas exige uma lógica de controle consideravelmente maior.

      <text color="secondary" weight="medium" size="xs">Mais complexo</text>
    </box>
  </row>
</box>

## 2. Comparação para o TTL-8

| Arquitetura | Gráficos livres | Complexidade | Memória |
|---|---|---|---|
| Caracteres programáveis | Limitados à grade | Baixa a média | Tela + padrões |
| Framebuffer único | Sim | Média | 1.536 B em 128×96 |
| Tiles | Limitados à grade | Média | Tela + padrões |
| Coprocessador | Sim | Alta | Depende do projeto |

A diferença mais importante é que **não precisamos de dois modos de vídeo para ter texto e gráficos**.

Podemos ter apenas um modo gráfico e deixar o software desenhar as letras.

## 3. Como funcionaria minha opção preferida?

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">TTL-8 — vídeo com framebuffer único</text>
  <svg viewBox="0 0 340 216" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="90" y="5" width="160" height="38" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="21" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="34" fontSize="9">Desenha letras e pixels</text>
      <path d="M170 43 V65" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="90" y="65" width="160" height="38" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="81" fontWeight="600">VRAM — 2 KB</text>
      <text x="170" y="94" fontSize="9">128×96 pixels, 1 bit/pixel</text>
      <path d="M170 103 V126" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="90" y="126" width="160" height="38" rx="6" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="170" y="142" fontWeight="600">Gerador de vídeo</text>
      <text x="170" y="155" fontSize="9">Contadores + shift register</text>
      <path d="M170 164 V184" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="90" y="184" width="160" height="27" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="202" fontWeight="600">Monitor CVBS</text>
    </g>
  </svg>
</box>

O gerador de vídeo não precisa saber o que é uma letra, um círculo ou uma linha.

Ele simplesmente lê os bytes da VRAM e transforma seus bits em pixels.

A CPU decide o conteúdo da imagem.

### Exemplo: desenhar a letra A

<row align="center" gap={4}>
  <box background="#101510" theme="dark" padding={3} radius="lg">
    <svg viewBox="0 0 96 96" width="132px" height="132px">
      {#each ["00111100","01100110","11000011","11000011","11111111","11000011","11000011","00000000"] as line,y}
        {#each line.split("") as bit,x}
          <rect x={x*12+0.6} y={y*12+0.6} width="10.8" height="10.8" rx="0.6" fill={bit==="1"?"#8dff9b":"#1c3321"}/>
        {/each}
      {/each}
    </svg>
  </box>
  <box flex="1" gap={2}>
    **Fonte 8×8**

    Cada caractere ocupa 8 bytes na memória de vídeo.

    O firmware copia o desenho da letra, armazenado na ROM, para a posição desejada na tela.
  </box>
</row>

Isso simplifica o hardware, mas transfere trabalho para a CPU.

## 4. Qual é a desvantagem?

A principal desvantagem é o desempenho.

No modo texto original, escrever uma letra exigiria basicamente gravar um byte na VRAM.

No framebuffer, desenhar uma letra 8×8 alinhada exige escrever oito bytes, além de buscar os dados da fonte e calcular os endereços.

Para um terminal de 32×24 caracteres, também teríamos uma diferença importante: uma tela de 128×96 pixels comporta apenas **16×12 caracteres de 8×8**.

Ou seja, perderíamos metade das colunas e das linhas do terminal planejado.

Para preservar 32×24 caracteres com fonte 8×8, precisaríamos de 256×192 pixels, consumindo 6 KB de framebuffer monocromático.

## 5. Uma alternativa que considero ainda mais interessante

Podemos manter o framebuffer único, mas aumentar a VRAM de 2 KB para **8 KB**, usando uma SRAM 6264.

Assim teríamos espaço para uma resolução de 256×192 pixels.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Comparação das duas configurações</text>
  <grid columns={2} gap={3}>
    <grid-item>
      <box background="surface-secondary" radius="lg" padding={3} gap={1}>
        <text color="secondary" weight="medium" size="xs">Configuração econômica</text>
        <title size="xl" color="default">128×96</title>
        <text size="sm">2 KB VRAM</text>
        <caption>Texto de 16×12 com fonte 8×8</caption>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface-secondary" radius="lg" padding={3} gap={1}>
        <text color="secondary" weight="medium" size="xs">Configuração expandida</text>
        <title size="xl" color="default">256×192</title>
        <text size="sm">8 KB VRAM</text>
        <caption>Texto de 32×24 com fonte 8×8</caption>
      </box>
    </grid-item>
  </grid>
</box>

A SRAM maior não exige necessariamente muito mais lógica, mas o controlador precisará de mais bits de endereço, maior taxa de leitura e temporização adequada.

Também teremos que revisar o mapa de memória: em vez de `C000–C7FF`, a VRAM poderia ocupar `C000–DFFF`, exatamente 8 KB.

## 6. Minha recomendação

Eu escolheria **framebuffer único, 8 KB de VRAM e resolução lógica de 256×192 monocromática**.

Por quê?

- Teremos texto 32×24, como planejado originalmente.
- Poderemos desenhar pixels em qualquer posição.
- Não precisaremos de uma ROM de caracteres no circuito de vídeo.
- Não precisaremos de um seletor físico entre modo texto e modo gráfico.
- Poderemos desenvolver fontes, desenhos e jogos inteiramente em software.
- A CPU continuará sendo nosso processador 8 bits construído com lógica 74HC.

Mas há uma condição: **precisamos validar a largura de banda e a arbitragem da VRAM antes de adotar essa resolução como definitiva**. Aumentar a memória é simples; produzir os pixels na velocidade correta é o verdadeiro desafio.

Também precisamos considerar que desenhar um quadro inteiro de 6 KB pode ser lento numa CPU microprogramada de aproximadamente 1 MHz.

Ainda assim, acredito que essa arquitetura é mais elegante e expansível para o TTL-8 do que manter dois geradores de vídeo separados.

**Eu seguiria com essa evolução: um único modo gráfico, 256×192, 8 KB de VRAM e texto renderizado por software.** Assim o computador já nasce capaz de desenhar, sem precisarmos acrescentar um segundo modo de vídeo posteriormente.

## user — bbb21214-f9f2-4969-a76a-a1a1308d84e9

Isso eh interessante, de ter só um modo
Faz assim
Revisa toda nossa arquitetura, levando em conta os pontos que você trouxe

## assistant — 00a4e104-8f19-415e-a733-891163de7c9c

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 7551458e-8e55-44e2-96af-0dce61c09442

# TTL-8 — Revisão geral da arquitetura Rev. 0.5

Vou revisar nosso computador como um sistema completo, considerando tudo o que definimos até agora: CPU construída com lógica 74HC, memória, teclado matricial de 64 teclas, vídeo composto e, principalmente, a nova decisão de usar **um único modo gráfico com texto desenhado por software**.

Minha conclusão inicial é que essa mudança faz sentido. Ela simplifica a organização lógica do vídeo, elimina a necessidade de manter dois modos de exibição e deixa o TTL-8 mais flexível para futuras atualizações.

Mas a revisão também revela alguns pontos que precisamos corrigir antes de comprar componentes: a organização dos registradores da CPU, a capacidade real da ROM, a arbitragem da memória de vídeo e a forma como vamos gerar o sinal composto.

## 1. Arquitetura geral revisada

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">TTL-8 — organização proposta</text>
  <svg viewBox="0 0 340 360" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="90" y="7" width="160" height="43" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="24" fontWeight="600">CPU TTL-8</text>
      <text x="170" y="39" fontSize="9">8 bits · Microprogramada</text>
      <path d="M170 50 V71" stroke="#94a3b8" strokeWidth="2"/>
      <rect x="7" y="71" width="326" height="31" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="91">Dados D0–D7 · Endereços A0–A15</text>
      {#each [{x:7,t:"ROM",s:"16 KB"},{x:91,t:"RAM",s:"32 KB"},{x:175,t:"VRAM",s:"8 KB"},{x:259,t:"I/O",s:"256 B"}] as a}
        <path d={`M${a.x+37} 102 V122`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={a.x} y="122" width="74" height="46" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+37} y="140" fontWeight="600">{a.t}</text>
        <text x={a.x+37} y="156" fontSize="9">{a.s}</text>
      {/each}
      <path d="M212 168 V187 M296 168 V187" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="143" y="187" width="138" height="43" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="212" y="204" fontWeight="600">Controlador gráfico</text>
      <text x="212" y="218" fontSize="9">256×192 · 1 bpp</text>
      <rect x="286" y="187" width="47" height="43" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="309" y="204" fontSize="9">4×</text>
      <text x="309" y="217" fontSize="9">4×4</text>
      <path d="M212 230 V252" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="143" y="252" width="138" height="42" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="212" y="268" fontWeight="600">Codificador CVBS</text>
      <text x="212" y="282" fontSize="9">Sincronismo + vídeo</text>
      <path d="M212 294 V316" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="143" y="316" width="138" height="35" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="212" y="337">Monitor AV monocromático</text>
    </g>
  </svg>
  <caption>Arquitetura funcional revisada. A CPU acessa a VRAM pelo barramento principal, enquanto o controlador gráfico precisa de acesso próprio para produzir a imagem.</caption>
</box>

## 2. Especificações principais

| Subsistema | Revisão proposta |
|---|---|
| Processador | CPU própria de 8 bits, lógica 74HC |
| Endereçamento | 16 bits, até 64 KB |
| Frequência | Meta inicial de até 1 MHz, sujeita a testes |
| Firmware | EEPROM regravável |
| RAM principal | 32 KB |
| Memória de vídeo | 8 KB SRAM |
| Vídeo | 256×192 pixels, monocromático |
| Texto | 32×24 caracteres de 8×8, via software |
| Saída de vídeo | Composto CVBS para monitor AV |
| Teclado | Quatro matrizes passivas 4×4 |
| Entrada simultânea | Até duas teclas |
| Expansão | Barramento e endereços reservados |

A proposta mantém o computador inteiramente programável, sem exigir um microcontrolador para executar as instruções ou desenhar os pixels.

## 3. Memória: a nova organização funciona?

Sim. A mudança para 8 KB de VRAM cabe no espaço de endereçamento de 64 KB.

Minha proposta é manter o mapa simples, sem bancos de memória nesta primeira versão.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Mapa de memória de 64 KB</text>
  <box direction="row" height="38px" radius="md" clip gap="2px">
    <box background="#3b82f6" width="25%" align="center" justify="center"><text color="#ffffff" size="2xs" weight="medium">ROM</text></box>
    <box background="#16a34a" width="50%" align="center" justify="center"><text color="#ffffff" size="2xs" weight="medium">RAM</text></box>
    <box background="#a855f7" width="12.5%" align="center" justify="center"><text color="#ffffff" size="2xs" weight="medium">VRAM</text></box>
    <box background="#d97706" flex="1" align="center" justify="center"><text color="#ffffff" size="2xs" weight="medium">I/O</text></box>
  </box>
  <table>
    <table-row><table-cell><text color="secondary" size="xs">0000–3FFF</text></table-cell><table-cell>ROM</table-cell><table-cell align="end">16 KB</table-cell></table-row>
    <table-row><table-cell><text color="secondary" size="xs">4000–BFFF</text></table-cell><table-cell>RAM</table-cell><table-cell align="end">32 KB</table-cell></table-row>
    <table-row><table-cell><text color="secondary" size="xs">C000–DFFF</text></table-cell><table-cell>VRAM</table-cell><table-cell align="end">8 KB</table-cell></table-row>
    <table-row><table-cell><text color="secondary" size="xs">E000–E0FF</text></table-cell><table-cell>Registradores I/O</table-cell><table-cell align="end">256 B</table-cell></table-row>
    <table-row><table-cell><text color="secondary" size="xs">E100–FFFF</text></table-cell><table-cell>Expansão futura</table-cell><table-cell align="end">7.75 KB</table-cell></table-row>
  </table>
  <caption>Os registradores de I/O ocupam 256 endereços; o restante da região superior permanece reservado.</caption>
</box>

### Componentes de memória

| Memória | Componente proposto | Observação |
|---|---|---|
| ROM principal | AT28C256 | 32 KB físicos; utilizar 16 KB inicialmente |
| RAM principal | 62256 | 32 KB |
| VRAM | 6264 | 8 KB |
| Microcódigo | EEPROMs separadas | Capacidade a calcular |
| Fonte 8×8 | Dados na ROM principal | Não precisa de ROM exclusiva no vídeo |

A AT28C256 tem capacidade física de 32 KB. Precisaremos fixar adequadamente seu pino de endereço adicional para expor somente 16 KB no mapa inicial.

A fonte de 96 caracteres de 8×8 ocupará 768 bytes na ROM. A CPU lerá esses padrões para desenhar letras no framebuffer.

**Correção importante:** os 8 KB da VRAM não estarão totalmente livres. A tela 256×192 consome 6.144 bytes, sobrando 2.048 bytes. Esses bytes restantes podem servir como área auxiliar, mas não formam um segundo framebuffer completo.

---

## 4. Vídeo: a revisão mais importante

A mudança para framebuffer único simplifica o caminho dos dados, mas não elimina a complexidade de gerar um sinal de vídeo composto válido.

O controlador gráfico precisa executar três tarefas independentes:

1. Gerar sincronismo horizontal e vertical.
2. Buscar bytes da VRAM nos instantes corretos.
3. Converter os bits em níveis de luminância para o monitor.

### Arquitetura do controlador

<box border radius="xl" padding={3} gap={2}>
  <svg viewBox="0 0 340 240" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="8" y="8" width="150" height="40" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="83" y="24" fontWeight="600">Clock de vídeo</text>
      <text x="83" y="38" fontSize="9">Oscilador independente</text>
      <rect x="182" y="8" width="150" height="40" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="257" y="24" fontWeight="600">Contadores H / V</text>
      <text x="257" y="38" fontSize="9">Posição do feixe</text>
      <path d="M158 28 H182 M257 48 V71" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="182" y="71" width="150" height="40" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="257" y="87" fontWeight="600">Endereço de vídeo</text>
      <text x="257" y="101" fontSize="9">Linha × 32 + coluna</text>
      <path d="M257 111 V130" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="90" y="130" width="242" height="37" rx="5" stroke="#a78bfa" fill="#a855f7" fillOpacity=".1"/>
      <text x="211" y="145" fontWeight="600">VRAM + arbitragem</text>
      <text x="211" y="159" fontSize="9">Compartilhada com a CPU</text>
      <path d="M211 167 V182" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="90" y="182" width="242" height="40" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="211" y="198" fontWeight="600">74HC166 + saída CVBS</text>
      <text x="211" y="212" fontSize="9">Serialização de pixels e níveis de vídeo</text>
      <rect x="8" y="130" width="69" height="37" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="42" y="146" fontWeight="600">CPU</text>
      <text x="42" y="159" fontSize="9">WAIT</text>
      <path d="M77 149 H90" stroke="#94a3b8" strokeWidth="1.5"/>
    </g>
  </svg>
</box>

### A frequência de pixels

Uma linha de vídeo NTSC tem aproximadamente 63,56 µs, mas parte desse tempo é consumida pelo sincronismo e pelos intervalos de apagamento.

Para distribuir 256 pixels em uma região ativa de aproximadamente 47,7 µs, precisaríamos de:

\[
f_{\text{pixel}} \approx \frac{256}{47,7\ \mu s}
\approx 5,37\text{ MHz}
\]

Isso é uma referência de cálculo, não um clock definitivo.

Podemos escolher um oscilador de frequência conveniente e ajustar a largura da imagem e as margens, desde que o monitor aceite a temporização produzida.

**Uma correção em relação à proposta anterior:** não podemos simplesmente duplicar as 192 linhas verticalmente num sinal NTSC convencional. Isso exigiria 384 linhas de imagem, mais do que cabe em um campo típico de aproximadamente 240 linhas úteis. Para 256×192, cada linha lógica deverá ocupar aproximadamente uma linha ativa de vídeo, com margens verticais.

### O problema da memória compartilhada

Este será provavelmente o circuito mais delicado da placa de vídeo.

Eu proponho aproveitar os intervalos entre buscas de bytes para permitir acessos da CPU à VRAM.

Por exemplo, o controlador pode carregar oito pixels em um registrador de deslocamento e, enquanto esses pixels são transmitidos, disponibilizar a SRAM para uma operação da CPU.

Mas isso só funciona se conseguirmos garantir os tempos de acesso e de comutação dos barramentos.

Nossa CPU precisará ter uma entrada `WAIT` para aguardar quando a VRAM estiver ocupada.

A prioridade será:

**Vídeo primeiro, CPU depois.**

Isso evita que um programa que esteja desenhando na tela desorganize o sincronismo ou produza pixels incorretos.

Ainda precisamos simular os ciclos para decidir se a arbitragem será por fases fixas, por intervalos de apagamento ou por uma combinação das duas.

---

## 5. CPU: precisamos melhorar a arquitetura antes de congelá-la

A CPU mínima proposta anteriormente consegue executar uma soma e gravar o resultado na RAM. Mas isso não significa que ela já tenha as instruções necessárias para um sistema gráfico utilizável.

Identifiquei três limitações importantes.

### A. Precisamos manipular endereços calculados

Para desenhar um pixel em 256×192, o software precisa calcular:

\[
\text{endereço}=C000+(y\times32)+\lfloor x/8\rfloor
\]

Sem registradores de índice ou instruções adequadas, esse cálculo será trabalhoso.

**Recomendo recuperar um registrador de índice de 16 bits**, que chamaremos de `X`, ou uma solução equivalente para endereçamento indireto.

### B. Precisamos manipular bits

Para acender ou apagar um pixel sem alterar seus vizinhos, a CPU precisa ler um byte, modificar um bit e gravá-lo novamente.

Nossas instruções AND, OR e XOR ajudam bastante, mas também serão úteis operações de deslocamento.

### C. Precisamos de sub-rotinas

Um sistema gráfico usará frequentemente funções como desenhar caractere, linha, pixel e limpar tela.

Sem `CALL` e `RET`, teríamos que repetir muito código ou implementar mecanismos complicados de retorno.

Por isso, **eu revisaria a decisão anterior de excluir pilha e chamadas de sub-rotina**.

## 6. CPU revisada — proposta Rev. 0.2

| Recurso | Decisão |
|---|---|
| A | Acumulador de 8 bits |
| B | Segundo operando de 8 bits |
| X | Índice de 16 bits |
| PC | Contador de programa de 16 bits |
| SP | Ponteiro de pilha de 16 bits |
| MAR | Endereço de memória de 16 bits |
| MDR | Dados de memória de 8 bits |
| IR | Instrução de 8 bits |
| Flags | Zero e Carry inicialmente |
| WAIT | Entrada para suspensão da CPU |

Não significa que precisaremos construir todos esses registradores de maneira independente. Durante o desenho do datapath, podemos compartilhar funções e eliminar redundâncias.

O conjunto de instruções também deverá incluir, além das operações já previstas, recursos equivalentes a:

| Instrução | Necessidade |
|---|---|
| `LDX` | Carregar endereço no índice |
| `LDA [X]` | Ler endereço apontado por X |
| `STA [X]` | Escrever no endereço apontado por X |
| `INX` | Avançar para o próximo byte |
| `SHL` / `SHR` | Deslocar bits |
| `CMP` | Comparar valores |
| `CALL` / `RET` | Executar sub-rotinas |
| `PUSH` / `POP` | Manipular pilha |

Esses nomes são provisórios. Ainda precisamos definir seus opcodes, formatos e microoperações.

A inclusão de X e SP aumenta o hardware, mas pode reduzir bastante a complexidade do software.

---

## 7. Teclado: manteremos a arquitetura, com alguns ajustes

A decisão de usar quatro membranas 4×4 continua adequada.

Não vejo motivo para trocar esse subsistema.

| Característica | Configuração |
|---|---|
| Teclas | 64 |
| Matriz | 4×16 |
| Simultâneas | Até duas |
| Diodos individuais | Não |
| Seleção de linhas | 74HC139 + 74HC125 |
| Leitura | 2×74HC244 |
| Registrador de linha | 74HC574 |

O 74HC125 permanece importante porque deixa as linhas não selecionadas em alta impedância, evitando conflitos elétricos.

O firmware fará varredura, debounce e conversão para ASCII.

Uma melhoria que recomendo é acrescentar uma forma de reinicialização do teclado. Podemos manter o 74HC574, desde que o firmware selecione uma linha antes da primeira leitura. Se quisermos um estado inicial garantido por hardware, poderemos substituí-lo por um registrador com reset.

Também precisamos confirmar a pinagem real das membranas: nem todos os modelos possuem os contatos organizados na mesma ordem.

## 8. Registradores de entrada e saída

O mapa de I/O precisa contemplar o vídeo e o teclado, além de reservar espaço para expansões.

| Endereço | Operação | Função |
|---|---|---|
| `E020` | Leitura | Estado do vídeo |
| `E021` | Leitura | Posição vertical ou indicador de quadro |
| `E040` | Escrita | Seleção de linha do teclado |
| `E041` | Leitura | Colunas 0–7 |
| `E042` | Leitura | Colunas 8–15 |
| `E050` | Escrita | Saída de diagnóstico |
| `E060–E06F` | Reservado | Temporizador futuro |

O vídeo não precisará de um registrador para selecionar texto ou gráficos, porque agora teremos apenas um formato de framebuffer.

Entretanto, um indicador de quadro ou de intervalo vertical será útil para sincronizar atualizações da imagem.

A saída de diagnóstico poderá ser um registrador simples conectado a LEDs, utilizados apenas durante a construção e depuração, não como interface principal do computador.

---

## 9. Atualizações de software: como preservar essa possibilidade

A CPU deverá iniciar sempre em um endereço conhecido, idealmente `0000`, onde ficará o código de inicialização.

A ROM principal poderá conter:

- Rotinas de inicialização e diagnóstico.
- Driver de teclado.
- Rotinas de acesso à memória de vídeo.
- Fonte de caracteres 8×8.
- Monitor de comandos.
- Biblioteca gráfica básica.
- Rotinas de carregamento e execução de programas.

Mas existe uma limitação que precisamos reconhecer: **16 KB de ROM podem se tornar apertados** conforme adicionarmos funções gráficas, editor e interpretador.

Por isso, eu manteria o componente físico AT28C256, de 32 KB, mas começaria utilizando apenas 16 KB.

No futuro, poderemos considerar remapear parte do espaço de endereços ou usar bancos de ROM, sem substituir necessariamente o chip.

Também recomendo reservar uma tabela de chamadas do sistema em endereços fixos. Assim, programas desenvolvidos para o TTL-8 poderão utilizar funções do firmware mesmo depois de atualizações, desde que preservemos a compatibilidade.

## 10. Precisamos revisar também a parte elétrica

Até agora falamos principalmente da arquitetura lógica. Para transformar isso em placas reais, há outras questões essenciais.

| Item | Requisito de projeto |
|---|---|
| Alimentação | 5 V regulados |
| Desacoplamento | 100 nF por CI, próximos à alimentação |
| Reset | Inicialização confiável da CPU e dos controladores |
| Clock | Distribuição adequada, sem pulsos espúrios |
| Barramentos | Apenas um componente dirigindo cada linha por vez |
| Temporização | Verificar setup, hold e propagação |
| Vídeo | Níveis de sincronismo e luminância adequados para 75 Ω |
| Conectores | Barramento modular com terra e alimentação suficientes |
| Expansão | Sinais reservados e documentação de pinagem |

O sinal composto merece atenção especial. Não podemos simplesmente conectar uma saída 74HC diretamente ao conector RCA e presumir que os níveis estarão corretos.

Precisaremos de um circuito de saída que produza os níveis de sincronismo, preto e branco adequados, considerando a terminação de 75 Ω do monitor.

Outro ponto: embora o projeto se chame TTL-8, estamos utilizando principalmente a família **74HC, que é CMOS**, não TTL clássica. O nome pode permanecer, mas os níveis lógicos, correntes e tempos devem seguir as especificações dos componentes reais.

---

## 11. O que acontece com nossa estimativa de 92 CIs?

A estimativa antiga já não serve como referência confiável.

Temos mudanças em direções diferentes:

| Mudança | Efeito provável |
|---|---|
| Eliminar gerador de caracteres em hardware | Reduz componentes de vídeo |
| Eliminar seletor texto/gráfico | Reduz componentes |
| Aumentar VRAM para 8 KB | Aumenta endereçamento necessário |
| Adicionar X de 16 bits | Aumenta lógica da CPU |
| Adicionar SP e chamadas | Aumenta registradores e controle |
| Implementar WAIT | Acrescenta controle de barramento |
| Melhorar decodificação e reset | Pode acrescentar componentes |

Portanto, não seria correto afirmar que continuaremos com 92 CIs ou que o número aumentará apenas seis ou dez unidades.

**Precisamos calcular a nova quantidade a partir dos esquemas elétricos.** O aumento pode ser compensado parcialmente pela simplificação do vídeo, mas ainda não sabemos em quanto.

Também não considero adequado estimar um orçamento definitivo antes dessa contagem.

---

## 12. Plano de construção revisado

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="cpu" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 1 — CPU e microcódigo**

      Fechar datapath, opcodes, registradores, pilha, microinstruções e sinais de controle. Simular programas básicos.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="memory-stick" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 2 — ROM, RAM e barramento**

      Executar programas reais, testar escrita/leitura e validar a inicialização.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="monitor" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 3 — Controlador gráfico**

      Simular sincronismo, endereçamento da VRAM, serialização dos pixels e arbitragem com a CPU.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="keyboard" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 4 — Teclado**

      Montar e testar a interface 4×16, integrando-a ao barramento.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="terminal" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 5 — Firmware e monitor**

      Exibir texto, receber comandos, editar memória e executar programas.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="pencil-ruler" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Fase 6 — Biblioteca gráfica**

      Implementar pixels, linhas, retângulos, caracteres e um primeiro editor de desenhos.
    </box>
  </row>
</box>

## 13. Minha avaliação final da revisão

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">Estado dos subsistemas</text>
  {#each [
    {n:"Arquitetura de memória",s:"Coerente, falta decodificação elétrica",v:0.75},
    {n:"Teclado 4×16",s:"Topologia definida, falta esquema final",v:0.75},
    {n:"CPU",s:"Registradores e ISA ainda em projeto",v:0.35},
    {n:"Vídeo 256×192",s:"Conceito definido, temporização não validada",v:0.3},
    {n:"Firmware",s:"Requisitos definidos, implementação pendente",v:0.2}
  ] as a}
    <box gap={1}>
      <row justify="between" align="center">
        <text weight="medium" size="sm">{a.n}</text>
        <text color="secondary" size="xs">{Math.round(a.v*100)}%</text>
      </row>
      <box background="surface-tertiary" height="6px" radius="full" clip>
        <box background="#64748b" width={`${a.v*100}%`} height="100%" radius="full"/>
      </box>
      <caption>{a.s}</caption>
    </box>
  {/each}
  <caption>Percentuais ilustrativos de maturidade do projeto, não métricas de testes concluídos.</caption>
</box>

**Eu aprovaria a arquitetura Rev. 0.5 como nossa nova referência de projeto**, com uma ressalva: a resolução 256×192 permanece uma meta de engenharia até validarmos o vídeo composto e a velocidade de acesso à SRAM.

As principais decisões ficam assim:

- CPU própria de 8 bits com endereçamento de 16 bits.
- Registrador X e suporte a pilha para facilitar programas maiores.
- 32 KB de RAM e 8 KB de VRAM.
- Um único framebuffer monocromático.
- Texto e gráficos desenhados por software.
- Teclado de 64 teclas, sem diodos individuais.
- Firmware regravável e possibilidade de expansão.

### Próxima etapa recomendada

Agora eu começaria pelo **projeto detalhado do datapath da CPU**.

Precisamos definir exatamente como os registradores, a ALU e os barramentos se conectam, quais componentes 74HC serão utilizados e como cada instrução será executada.

Essa etapa determinará a quantidade real de CIs da CPU e, principalmente, se conseguiremos executar nosso futuro firmware gráfico com um desempenho aceitável.

O objetivo continua sendo construir um computador completo e funcional, mas agora com uma arquitetura mais coerente para evoluir de um simples prompt até um editor gráfico e pequenos jogos.

## user — bbb21eeb-b36a-4d0e-ac03-be7b35a6eec7

Estou gostando
Pode revisar tudo, simular e entender o que vamos precisar
Seja crítico
Precisamos de uma lista e desenho 100% funcional, pois não teremos espaço pra erro 

## assistant — 2a003a42-bc57-492f-93eb-a07f118a930c

{"content_type": "thoughts", "source_analysis_msg_id": "28f9f8f3-8f70-4122-93d4-2cdaf4ecf701", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou a arquitetura preliminar e a simulação comportamental"}]}

## assistant — 07e5e231-df9a-43e4-880c-6a5bec514995

{"content": "Pensou por 21s", "content_type": "reasoning_recap"}

## assistant — 23b67a51-d3c1-4285-8e1f-5b9f76b74fb2

# TTL-8 — Auditoria técnica e validação do projeto

Concordo com a exigência. A partir de agora, vamos tratar o TTL-8 como um projeto de engenharia eletrônica, não apenas como uma ideia de computador.

Isso muda nossa metodologia: **não vamos comprar componentes nem fabricar placas com base em estimativas, diagramas conceituais ou circuitos que ainda não foram simulados.**

Também preciso ser rigoroso em um ponto: não seria correto prometer um desenho 100% funcional neste momento. Ainda não temos esquemas elétricos completos, microcódigo, temporizações verificadas nem modelos de todos os componentes. Podemos trabalhar para atingir esse nível de confiança, mas ele precisará ser demonstrado por testes.

## 1. Primeiros problemas que encontrei na arquitetura

| Área | Problema | Correção proposta |
|---|---|---|
| CPU | A ISA ainda não está fechada e pode não conseguir executar todo o firmware previsto | Definir instruções e microoperações antes dos CIs |
| Microcódigo | Não calculamos a quantidade de sinais de controle nem a capacidade das EEPROMs | Projetar o formato das microinstruções |
| Vídeo | A arbitragem da VRAM ainda não foi demonstrada | Simular os ciclos de leitura e escrita |
| Clock | 1 MHz é uma meta sem análise de temporização | Calcular o caminho crítico |
| Teclado | Faltam decodificação completa e reset definido | Fechar o circuito e testar combinações |
| ROM | O mapa reserva 16 KB, mas o chip escolhido possui 32 KB | Definir mapeamento e possibilidade de expansão |
| Firmware | Não sabemos se o conjunto de instruções será eficiente para gráficos | Criar um emulador da CPU antes de construir |

Há ainda uma questão especialmente importante: **o vídeo não pode depender da CPU para gerar cada pixel em tempo real**. O controlador de vídeo deve funcionar autonomamente, enquanto a CPU modifica a memória de imagem.

Isso já estava implícito na arquitetura, mas agora passa a ser um requisito obrigatório.

## 2. Primeira verificação executada

Fiz uma verificação computacional de dois pontos que podemos testar independentemente do circuito físico: o endereçamento do framebuffer e o comportamento lógico da matriz de teclado.

<box border radius="lg" padding={3} gap={3}>
  <row align="center" justify="between">
    **Resultados dos testes**
    <badge color="success">Testes lógicos passaram</badge>
  </row>
  <grid columns={2} gap={3}>
    <grid-item>
      <box gap={1}>
        <text color="secondary" size="xs">Endereços de vídeo</text>
        <title size="xl" color="default" tabularNums>6.144</title>
        <caption>Bytes distintos endereçados</caption>
      </box>
    </grid-item>
    <grid-item>
      <box gap={1}>
        <text color="secondary" size="xs">Combinações de 2 teclas</text>
        <title size="xl" color="default" tabularNums>2.016</title>
        <caption>Sem teclas fantasmas no modelo</caption>
      </box>
    </grid-item>
  </grid>
  <divider/>
  <text weight="medium" size="sm">Memória de vídeo</text>
  <table>
    <table-row><table-cell>Primeiro byte da imagem</table-cell><table-cell>`C000`</table-cell></table-row>
    <table-row><table-cell>Último byte da imagem</table-cell><table-cell>`D7FF`</table-cell></table-row>
    <table-row><table-cell>Área auxiliar restante</table-cell><table-cell>`D800–DFFF`</table-cell></table-row>
  </table>
  <text size="sm">O cálculo de endereço cobre exatamente os 6.144 bytes da imagem, sem ultrapassar a VRAM de 8 KB.</text>
</box>

Para o teclado, modelei as conexões elétricas como uma rede de linhas e colunas, com apenas a linha selecionada conduzindo nível baixo e as demais em alta impedância.

O resultado foi:

- Todas as 2.016 combinações possíveis de duas teclas foram reconhecidas sem teclas adicionais.
- Três teclas formando três cantos de um retângulo produziram uma quarta tecla fantasma, como esperado.

**Limite desses testes:** eles validam a lógica abstrata, não a eletrônica. Ainda não verificam atrasos de propagação, ruído, bouncing, correntes, pinagem ou temporização real.

## 3. Uma descoberta importante sobre o desempenho gráfico

Nossa tela 256×192 ocupa 6.144 bytes.

Se quiséssemos reescrever toda a tela 60 vezes por segundo:

\[
6144\times60=368.640\text{ bytes/s}
\]

Isso seria muito exigente para uma CPU microprogramada funcionando a aproximadamente 1 MHz.

E cada byte atualizado pode exigir várias microinstruções.

Portanto, precisamos distinguir duas coisas:

**Atualização do monitor:** o controlador de vídeo pode transmitir a imagem continuamente, independentemente da CPU.

**Atualização do conteúdo:** a CPU modifica somente os bytes necessários, na velocidade que conseguir.

Isso é perfeitamente aceitável para um terminal, editor gráfico e muitos jogos simples.

Não precisamos redesenhar a tela inteira a cada quadro.

Eu manteria a resolução 256×192, mas não estabeleceria 60 FPS como requisito de animação.

## 4. Uma melhoria que precisamos estudar: o clock da CPU

O vídeo precisará de um clock independente, provavelmente na faixa de alguns megahertz.

A CPU terá outro domínio de temporização, mais lento.

Isso exige cuidado ao conectar os dois módulos.

Minha recomendação é que o controlador de vídeo tenha prioridade absoluta sobre a VRAM e que o acesso da CPU seja controlado por uma interface de requisição e confirmação.

Não podemos simplesmente usar um sinal `WAIT` assíncrono sem especificar quando ele pode interromper e liberar a CPU.

O circuito deverá garantir que:

- Nenhuma escrita seja interrompida no meio.
- Nenhum registrador capture dados inválidos.
- A SRAM não receba dois endereços simultaneamente.
- Os pixels sejam carregados nos instantes corretos.
- A CPU só continue quando seu acesso estiver concluído.

Essa será uma das partes mais importantes da simulação digital.

## 5. Arquitetura que recomendo manter

<box border radius="xl" padding={3} gap={2}>
  <text weight="medium">TTL-8 — arquitetura de referência para validação</text>
  <svg viewBox="0 0 340 338" width="100%">
    <g textAnchor="middle" fill="currentColor" fontSize="11">
      <rect x="92" y="6" width="156" height="40" rx="5" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="170" y="22" fontWeight="600">CPU 8 bits</text>
      <text x="170" y="36" fontSize="9">ALU · PC · X · SP · Controle</text>
      <path d="M170 46 V67" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="7" y="67" width="326" height="31" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="170" y="86">Barramento de dados e endereços</text>
      {#each [{x:7,t:"ROM",s:"16 KB"},{x:91,t:"RAM",s:"32 KB"},{x:175,t:"VRAM",s:"8 KB"},{x:259,t:"I/O",s:"Teclado"}] as a}
        <path d={`M${a.x+37} 98 V117`} stroke="#94a3b8" strokeWidth="1.5"/>
        <rect x={a.x} y="117" width="74" height="43" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
        <text x={a.x+37} y="135" fontWeight="600">{a.t}</text>
        <text x={a.x+37} y="149" fontSize="9">{a.s}</text>
      {/each}
      <path d="M212 160 V184" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="125" y="184" width="174" height="41" rx="5" stroke="#a78bfa" fill="#a855f7" fillOpacity=".1"/>
      <text x="212" y="200" fontWeight="600">Arbitragem VRAM</text>
      <text x="212" y="214" fontSize="9">Requisição · Confirmação</text>
      <path d="M212 225 V245" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="125" y="245" width="174" height="40" rx="5" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="212" y="261" fontWeight="600">Gerador de vídeo</text>
      <text x="212" y="275" fontSize="9">256×192 · 1 bit por pixel</text>
      <path d="M212 285 V305" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="125" y="305" width="174" height="28" rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x="212" y="323">Saída CVBS · Monitor</text>
    </g>
  </svg>
  <caption>Diagrama de blocos para orientar os esquemas. Não representa conexões pino a pino nem um circuito pronto para montagem.</caption>
</box>

Há uma correção que quero introduzir: a interface entre CPU e vídeo deverá ter um protocolo de acesso claramente definido. Isso é mais importante do que decidir agora qual CI fará a arbitragem.

## 6. Lista preliminar de componentes

Esta é uma **lista de referência para engenharia**, não uma lista autorizada para compra.

| Subsistema | Componentes candidatos | Situação |
|---|---|---|
| CPU | 74HC574, 74HC173, 74HC245, 74HC157, 74HC283 e lógica auxiliar | Quantidades pendentes |
| Microcódigo | AT28C64B ou EEPROM equivalente | Largura e capacidade pendentes |
| ROM principal | AT28C256 ×1 | Candidato definido |
| RAM | SRAM 62256 ×1 | Candidato definido |
| VRAM | SRAM 6264 ×1 | Candidato definido |
| Teclado | 74HC574 ×1, 74HC139 ×1, 74HC125 ×1, 74HC244 ×2 | Topologia definida |
| Vídeo | Contadores 74HC, 74HC166, multiplexadores e lógica de sincronismo | Esquema pendente |
| Clock | Osciladores, divisores e circuitos de controle | Frequências pendentes |
| Alimentação | Regulador/fonte 5 V, desacoplamento e proteção | Dimensionamento pendente |

Também precisamos especificar os tempos de acesso das memórias, não apenas suas capacidades. Dois chips com o mesmo código básico podem ter velocidades diferentes.

E há outro problema a corrigir: a pinagem do 74HC574 apresentada numa revisão anterior não deve ser utilizada para montagem. Ela continha uma associação incorreta entre pinos e sinais. A pinagem de todos os componentes deverá ser conferida nos respectivos datasheets e registrada no esquema definitivo.

## 7. Como vamos obter um projeto realmente verificável

Quero estabelecer uma sequência de validação com critérios objetivos.

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="file-code" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 1 — Especificação executável da CPU**

      Definir a ISA e criar um emulador que execute exatamente seus opcodes. Testar aritmética, endereçamento, saltos, pilha e chamadas de sub-rotina.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="workflow" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 2 — Circuito lógico da CPU**

      Projetar registradores, ALU, multiplexadores e controle. Comparar a execução do circuito com o emulador, instrução por instrução.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="monitor" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 3 — Simulação do vídeo**

      Validar contadores, sincronismo, geração de endereços, leitura de pixels e disputa pela VRAM. A parte analógica da saída CVBS precisará de análise própria.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="keyboard" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 4 — Simulação do teclado**

      Testar seleção de linhas, buffers, sinais de leitura/escrita, inicialização e combinações de teclas.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="circuit-board" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 5 — Esquemático e PCB**

      Produzir os arquivos de engenharia, conferir pinagem e footprints, executar ERC/DRC, revisar alimentação, conectores e temporização.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="42px" align="center" justify="center"><icon name="check-check" size="lg"/></box>
    <box flex="1" gap={1}>
      **Etapa 6 — Protótipo físico**

      Testar cada placa isoladamente e depois o sistema integrado. Somente após os testes físicos poderemos considerar a revisão validada para reprodução.
    </box>
  </row>
</box>

## 8. Critérios de aprovação antes da compra

Não considero o projeto pronto enquanto não tivermos:

- Esquema elétrico completo com referência de cada pino.
- Lista de materiais com quantidades exatas, encapsulamentos e alternativas compatíveis.
- Microcódigo e firmware de teste executáveis.
- Simulação digital cobrindo todos os opcodes e operações críticas.
- Análise de temporização com margens adequadas.
- Verificação elétrica da saída de vídeo e compatibilidade com o monitor escolhido.
- Arquivos de PCB e relatórios de verificação.
- Plano de testes físicos com resultados esperados e critérios de aprovação.

Mesmo com isso, nenhuma simulação garante ausência absoluta de erros. A meta realista é eliminar os problemas conhecidos antes da fabricação e validar os riscos restantes em protótipos controlados.

---

## 9. Minha principal recomendação técnica

**Não começaria pelo desenho da placa. Começaria pelo emulador da CPU e pela definição definitiva da ISA.**

O motivo é simples: todo o restante depende de conseguirmos executar programas corretamente.

Se descobrirmos depois que falta uma instrução essencial, poderemos ter que alterar registradores, controle, microcódigo e até conexões físicas.

Em paralelo, devemos validar o controlador de vídeo, porque ele representa o segundo maior risco do projeto.

Quero que nossa próxima revisão produza três resultados concretos: **uma ISA executável, um datapath detalhado e uma primeira lista de sinais de controle**. Só depois calcularemos a quantidade de EEPROMs e de circuitos 74HC.

Dessa forma, não estaremos simplesmente escolhendo componentes que parecem suficientes. Estaremos demonstrando, progressivamente, por que cada componente é necessário.

**Estado atual: arquitetura conceitual consistente, dois testes lógicos preliminares aprovados, mas hardware ainda não validado para fabricação.** Esse é o ponto de partida correto para buscar um TTL-8 realmente funcional.

## user — bbb21747-07e8-4173-8024-7b6c966a0fc7

Não vejo necessidade de uma tela atualizando 60 vezes por segundo 
24 eh o minino pra um humano entender movimento? Por mim pode ser
Vc falou do nome kkkk vamos mudar, quero chamar de ISA 1, nome da minha filha (Isabel) e vi que tem coisas da CPU com Isa kkk

## assistant — e2bffc1c-4c5b-4f42-a7e5-88f16b60fe62

**ISA-1!** 😄 Gostei da escolha! Uma homenagem à Isabel e, ao mesmo tempo, uma coincidência perfeita com o mundo dos processadores.

Em arquitetura de computadores, **ISA** significa *Instruction Set Architecture*, ou arquitetura do conjunto de instruções. É justamente uma das partes que estamos desenvolvendo para nossa CPU!

Então teremos:

**ISA-1 — Isabel's 8-bit Computer**

Um computador de 8 bits, construído com lógica 74HC, microcódigo em EEPROM e vídeo monocromático. O nome combina com a história do projeto.

## Sobre os 24 FPS: você está no caminho certo, mas existe um detalhe importante

**24 quadros por segundo podem ser suficientes para perceber movimento**, especialmente em animações simples. Não existe um limite universal de 24 FPS para a visão humana: a fluidez percebida depende do movimento, da iluminação e de outros fatores.

Mas precisamos separar duas frequências diferentes:

| Conceito | O que significa | Nossa escolha |
|---|---|---|
| Frequência do sinal de vídeo | Quantas vezes o monitor recebe a imagem | ~60 campos/s no padrão NTSC |
| Taxa de animação | Quantas vezes o programa altera o desenho | Até 24 FPS como meta |

Nosso monitor RCA precisa receber sincronismo de vídeo continuamente. Se enviarmos apenas 24 quadros de sinal composto por segundo, um monitor convencional poderá perder o sincronismo ou não mostrar imagem.

**A solução é manter o controlador de vídeo funcionando continuamente e deixar a CPU atualizar os desenhos em uma velocidade menor.**

Por exemplo:

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Exemplo: animação a 24 FPS em uma saída de 60 Hz</text>
  <svg viewBox="0 0 340 116" width="100%">
    <g fontSize="10" fill="currentColor">
      <text x="5" y="15">Saída</text>
      <text x="5" y="74">Animação</text>
    </g>
    {#each Array.from({length:12},(_,i)=>i) as i}
      <rect x={65+i*22} y="27" width="19" height="25" rx="3" fill="#64748b" fillOpacity=".18" stroke="#94a3b8"/>
      <text x={74.5+i*22} y="43" fontSize="9" fill="currentColor" textAnchor="middle">{i+1}</text>
      <rect x={65+i*22} y="83" width="19" height="23" rx="3" fill={["#16a34a","#16a34a","#2563eb","#2563eb","#2563eb"][i%5]} fillOpacity=".8"/>
      <text x={74.5+i*22} y="98" fontSize="9" fill="white" textAnchor="middle">{Math.floor(i*2/5)+1}</text>
    {/each}
  </svg>
  <caption>Ilustração de repetição de imagens: a saída continua transmitindo, mesmo quando o conteúdo do framebuffer não muda. A cadência real dependerá do temporizador e da sincronização.</caption>
</box>

E temos outra vantagem: para exibir um terminal de comandos, a tela pode permanecer praticamente estática. A CPU só precisa desenhar novamente quando algo mudar.

## O que muda na arquitetura do ISA-1?

Praticamente nada no hardware por causa dessa decisão.

| Característica | ISA-1 |
|---|---|
| CPU | 8 bits, construída com 74HC |
| ROM | EEPROM regravável |
| RAM | 32 KB |
| VRAM | 8 KB |
| Resolução | 256×192 monocromática |
| Texto | 32×24 caracteres via software |
| Vídeo composto | Sincronismo contínuo |
| Animação | Meta de até 24 FPS, quando viável |
| Teclado | 64 teclas, quatro matrizes 4×4 |

A única ressalva é que **24 FPS de animação de tela inteira ainda podem ser exigentes** para nossa CPU.

Uma imagem ocupa 6.144 bytes. A 24 FPS, seriam 147.456 bytes escritos por segundo, sem contar as instruções para calcular e desenhar os pixels. Não vamos exigir isso do processador.

Em vez disso, os programas poderão atualizar pequenas regiões da imagem, aproveitando o framebuffer persistente.

Eu também incluiria no ISA-1 um temporizador simples ou contador de quadros para ajudar os jogos a controlar a velocidade das animações.

E agora temos uma distinção divertida que usaremos na documentação:

- **ISA-1** é o nome do computador, em homenagem à Isabel.
- **ISA da CPU** é o conjunto de instruções que vamos projetar.

O nome do projeto fica **ISA-1**, e nossa próxima tarefa continua sendo validar a CPU e o controlador gráfico antes de fechar os esquemas e a lista de componentes. <MemoryCite />

## user — bbb21c51-590e-4484-b369-1510992de6a7

Ahh entendi
Vc não falava de 60fps
Faz assim
Decide o que for melhor

## assistant — a917a713-6173-47b0-a0ff-34591d72a250

Fechado! 😁 Vou assumir as decisões técnicas do **ISA-1**, priorizando confiabilidade, simplicidade e custo, sem comprometer nossas possibilidades de expansão.

### Minha decisão para o vídeo

**Manteremos a saída de vídeo composta convencional, com sincronismo contínuo, e deixaremos a CPU atualizar a imagem conforme necessário.**

Não vamos impor uma meta fixa de 24 ou 60 FPS aos programas.

Isso significa que:

- O monitor receberá o sinal continuamente, independentemente do que a CPU estiver fazendo.
- A imagem permanecerá na VRAM até que algum programa a modifique.
- Texto, menus e desenhos estáticos não exigirão redesenho constante.
- Jogos atualizarão somente as regiões necessárias.
- Poderemos adicionar sincronização com o vídeo para reduzir artefatos visuais.

### Configuração escolhida

| Componente | Decisão |
|---|---|
| Computador | **ISA-1** |
| CPU | 8 bits, lógica 74HC |
| Endereçamento | 16 bits |
| Clock da CPU | Inicialmente lento; meta de 1 MHz após validação |
| RAM | 32 KB |
| ROM | EEPROM de 32 KB, com 16 KB inicialmente mapeados |
| VRAM | 8 KB |
| Resolução gráfica | 256×192, monocromática |
| Texto | 32×24 caracteres, desenhados por software |
| Vídeo | CVBS com controlador independente |
| Teclado | 64 teclas, matriz 4×16 |
| Software | Firmware atualizável e programas executados na RAM |

### Uma correção importante que vou incorporar

Na revisão detalhada, precisamos resolver o mapeamento físico da RAM 62256.

Nossa região `4000–BFFF` tem 32 KB, mas não corresponde diretamente aos endereços internos consecutivos da SRAM. Se conectarmos os 15 bits inferiores do barramento sem tradução, parte da RAM ficará espelhada.

Vou exigir uma decodificação que transforme corretamente os endereços da CPU nos endereços físicos da memória, sem sobreposição.

Também manterei como requisitos obrigatórios o controle seguro de acesso à VRAM, a verificação dos tempos de propagação e a validação de cada instrução da CPU.

### O princípio que vamos seguir

**Não vamos adicionar hardware apenas porque seria interessante. Cada componente precisará ter uma função necessária e verificável.**

Se uma função puder ser realizada em software sem prejudicar significativamente o funcionamento, preferiremos software.

E não vamos considerar um circuito pronto para fabricação enquanto não tivermos esquemas completos, pinagens verificadas, simulações e um plano de testes físicos.

Nossa arquitetura de referência passa a ser a **ISA-1 Rev. 0.6**.

A próxima prioridade técnica será fechar o datapath e o microcódigo da CPU, em paralelo com a validação da temporização do vídeo. Essas duas partes determinarão se todo o restante do computador será viável com os componentes escolhidos.

Quero que o ISA-1 seja um computador que possamos realmente montar, ligar e usar — não apenas um projeto bonito no papel.

## user — bbb21ab2-d298-4421-a033-4caa42003eb7

Pode seguir com as revisões
E se necessário, emule a construção do hardware e do software 

## assistant — 2d43d97b-0459-4906-8334-a55988284026

{"content_type": "thoughts", "source_analysis_msg_id": "6fb6054e-298c-441d-aa39-2e9b6aa3ef28", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementado e testado emulador ISA-1 com memória"}]}

## assistant — 01803880-edd4-4fd8-a8fa-1ec3a721e2d6

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 4bff056b-a1a3-425a-a44d-623f3eb6b718

# ISA-1 — Revisão técnica Rev. 0.7

Vamos avançar com **testes executáveis**, não apenas com novos diagramas.

Nesta revisão, vou trabalhar em três níveis: verificar se a arquitetura é coerente, emular o comportamento do processador e da memória e identificar o que ainda exige simulação elétrica antes da fabricação.

A prioridade é encontrar erros enquanto ainda podemos mudar o projeto sem custo.

## 1. Uma correção importante: a RAM

O mapa de memória que escolhemos continua interessante, mas existe um problema real na ligação da SRAM 62256.

Nossa RAM ocupa `4000–BFFF`, ou 32 KB. Se conectarmos diretamente os bits A0–A14 da CPU à SRAM, teremos espelhamento: endereços diferentes acessarão as mesmas posições físicas.

A solução é traduzir o bit de endereço mais alto da SRAM:

\[
A14_{\mathrm{RAM}}=A15_{\mathrm{CPU}}
\]

Essa relação funciona **dentro da região selecionada `4000–BFFF`**, porque os dois blocos de 16 KB têm, respectivamente, A15 igual a 0 e 1.

Os demais bits da SRAM permanecem conectados diretamente a A0–A13 da CPU.

Assim, os endereços ficam:

| CPU | SRAM física |
|---|---|
| `4000` | `0000` |
| `7FFF` | `3FFF` |
| `8000` | `4000` |
| `BFFF` | `7FFF` |

Isso elimina o espelhamento sem exigir um somador ou um circuito XOR para traduzir endereços.

Ainda precisaremos de um decodificador que habilite a SRAM exclusivamente nessa região.

## 2. Uma segunda decisão: separar o clock de vídeo do clock da CPU

Vou manter dois domínios de temporização.

O controlador de vídeo precisa produzir uma imagem estável mesmo quando a CPU estiver parada. Isso também será muito útil durante a depuração, porque poderemos executar uma instrução de cada vez sem perder o sinal de vídeo.

A CPU terá clock lento ou manual durante os testes e poderá operar mais rapidamente depois.

O acesso compartilhado à VRAM será tratado como uma interface própria, com requisição, concessão e conclusão de operação. Não vamos presumir que basta conectar os barramentos e acrescentar um sinal `WAIT`.

## 3. Primeira emulação executada

Criei e executei um emulador funcional preliminar do ISA-1 em Python. Ele não simula ainda os transistores ou os CIs 74HC; simula o comportamento esperado dos registradores, das instruções e da memória.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    **ISA-1 Rev. 0.7 — Resultado**
    <badge color="success"><icon name="check" size="xs" inline/> 4 grupos aprovados</badge>
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    <box flex="1" gap={1}>
      **RAM — 32.768 endereços distintos**

      <text color="secondary" size="xs">Teste completo de mapeamento, escrita e leitura, sem espelhamento.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    <box flex="1" gap={1}>
      **Framebuffer — 256×192 pixels**

      <text color="secondary" size="xs">49.152 pixels acesos e apagados, com endereçamento correto dos 6.144 bytes.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    <box flex="1" gap={1}>
      **CPU — programa de teste**

      <text color="secondary" size="xs">Soma 10 + 20, grava 30 na RAM, chama sub-rotina, desloca bits e retorna.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    <box flex="1" gap={1}>
      **Saltos e pilha**

      <text color="secondary" size="xs">Salto condicional, PUSH/POP e restauração do ponteiro de pilha.</text>
    </box>
  </row>
</box>

Você pode examinar e executar o código usado nesses testes:

<row align="center" gap={2}>
  <icon name="file-code" color="secondary" size="lg"/>
  [Emulador ISA-1 Rev. 0.7 — Python](sandbox:/mnt/data/isa1/isa1_rev07_emulator.py)
</row>

Para executá-lo:

```bash
python3 isa1_rev07_emulator.py
```

**Importante:** os opcodes usados são provisórios. Ainda não foi demonstrado que a futura CPU física consegue executá-los. O emulador estabelece um comportamento de referência para compararmos com o hardware.

## 4. O que a emulação ainda não prova

Esta distinção é fundamental para evitar erros de fabricação.

| Verificação | Estado |
|---|---|
| Mapeamento lógico da RAM | Aprovado |
| Endereçamento dos pixels | Aprovado |
| Instruções preliminares | Testes básicos aprovados |
| Microcódigo em EEPROM | Não implementado |
| Datapath com 74HC | Não simulado |
| Temporização CVBS | Não validada |
| Arbitragem da VRAM | Não simulada |
| Esquemático pino a pino | Não produzido |
| Compatibilidade elétrica | Não validada |

Também não considero suficiente testar apenas um programa que funciona. Precisaremos de testes para todas as instruções, valores-limite, transições de flags, endereços de fronteira e operações simultâneas.

## 5. Revisão crítica: três decisões que ainda não vou congelar

### A. CPU e microcódigo

A adição de registradores X e SP facilita muito o software, mas também aumenta o número de sinais de controle.

Antes de escolher as EEPROMs de microcódigo, precisamos determinar:

- Quantos ciclos cada instrução exige.
- Quantos sinais precisam ser controlados simultaneamente.
- Como o PC será incrementado e carregado.
- Como os endereços de 16 bits circularão pelo datapath.
- Como as flags influenciarão os saltos.
- Como a CPU será suspensa sem perder uma operação.

Minha preferência é usar uma arquitetura de barramento interno simples, mesmo que algumas instruções precisem de mais ciclos.

### B. Controlador de vídeo

A resolução de 256×192 exige 32 bytes por linha.

Usando como referência uma região ativa de 47,7 µs, teremos aproximadamente 1,49 µs por byte de imagem. Isso é uma janela promissora para uma SRAM suficientemente rápida, mas ainda precisamos calcular o tempo consumido pelo carregamento do registrador de pixels, multiplexação, estabilização e acesso da CPU.

Também precisamos decidir a temporização vertical exata. Não vamos simplesmente chamar qualquer sinal de 60 Hz de NTSC compatível: sincronismos, intervalos de apagamento e comportamento do monitor precisam ser considerados.

### C. Expansão de ROM

A EEPROM de 32 KB é interessante, mas o mapa atual expõe somente 16 KB.

Vou manter essa configuração na referência provisória e avaliar posteriormente se vale a pena usar bancos de ROM. Não quero acrescentar comutação de bancos antes de saber o tamanho real do firmware.

## 6. Próxima revisão: passar do emulador para o circuito

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Sequência de validação do ISA-1</text>
  <list marker="number" connector="solid" gap={2}>
    <list-item>
      **Fechar a ISA**

      Definir todos os opcodes, formatos e comportamento das flags. Ampliar o emulador para testes exaustivos das operações de 8 bits.
    </list-item>
    <list-item>
      **Projetar o datapath**

      Escolher registradores, multiplexadores, ALU e sinais de controle. Produzir o primeiro esquema lógico completo da CPU.
    </list-item>
    <list-item>
      **Gerar e testar microcódigo**

      Criar o conteúdo das EEPROMs e comparar cada microoperação com o emulador de referência.
    </list-item>
    <list-item>
      **Simular a interface de memória**

      Incluir tempos de leitura, escrita, espera e disputas de barramento.
    </list-item>
    <list-item>
      **Validar vídeo e teclado**

      Fechar os circuitos, conferir datasheets e simular os casos críticos.
    </list-item>
    <list-item>
      **Preparar o hardware para fabricação**

      Somente depois produzir a lista definitiva de componentes, esquemáticos elétricos e layout das placas.
    </list-item>
  </list>
</box>

### Minha conclusão desta rodada

A arquitetura do **ISA-1 continua viável em princípio**, e a primeira emulação confirmou que o mapeamento corrigido da RAM, o framebuffer e um subconjunto preliminar de instruções funcionam no modelo de software.

Ainda não temos evidência suficiente para garantir que a implementação física funcionará. O maior risco agora não é a capacidade de memória: é **a interação entre o microcódigo, os barramentos e a temporização do vídeo**.

Por isso, minha próxima prioridade será produzir uma CPU definida até o nível das microoperações, em vez de continuar acrescentando funcionalidades.

O critério permanece: **nenhuma placa será considerada pronta para fabricação enquanto seu funcionamento não estiver demonstrado e suas limitações documentadas.**

## user — bbb21136-2e0a-4453-bdbc-510a2b0114a1

Pode seguir, e quero que você vá se revisando até ter uma ideia viável e me retorne aqui
Tudo oq vc puder decidir, pode decidir
Só me pergunte o essencial
As decisões que você tomar, registra pra eu ler depois
Confio em vc para tomar as melhores decisões

## assistant — 0292991b-b7a4-427b-9182-3ce8ff1b6f37

{"content_type": "thoughts", "source_analysis_msg_id": "4f11bd20-08b0-4be7-b3bd-59f266cf4b48", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquitetura e registrou decisões e riscos técnicos"}]}

## assistant — 0672c7d8-a44d-4e6b-8d49-551baf3460c1

{"content": "Pensou por 38s", "content_type": "reasoning_recap"}

## assistant — 74f5089f-4372-47db-a747-a0c3c676381c

Combinado. Vou assumir as decisões técnicas do **ISA-1**, documentar as mudanças e só pedir sua participação quando houver uma escolha que realmente dependa de você.

Já avancei para a **revisão 0.8**, reexaminei o emulador anterior e executei novos testes. Também preparei um registro de engenharia para que você consiga acompanhar o projeto sem depender de lembrar tudo o que conversamos.

## Arquivos da revisão 0.8

<box border radius="lg" padding={3} gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Registro de decisões e riscos — Rev. 0.8](sandbox:/mnt/data/isa1/ISA-1_REV08_DECISOES_E_RISCOS.md)**

      <text color="secondary" size="xs">Arquitetura, decisões, justificativas, problemas encontrados e critérios de aprovação.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Testes de validação — Python](sandbox:/mnt/data/isa1/isa1_rev08_validation.py)**

      <text color="secondary" size="xs">Testes reproduzíveis de memória, endereçamento, aritmética de referência e frequências propostas.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Emulador de referência — Rev. 0.7](sandbox:/mnt/data/isa1/isa1_rev07_emulator.py)**

      <text color="secondary" size="xs">Base utilizada pelos testes da nova revisão.</text>
    </box>
  </row>
</box>

## O que decidi nesta revisão

A principal mudança é utilizar **um único oscilador mestre**, com divisões para a CPU e o vídeo. Isso facilita o controle de temporização e evita alguns problemas de sincronização entre circuitos independentes.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Clock proposto para estudo</text>
  <svg viewBox="0 0 320 150" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="79" y="5" width="162" height="34" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="160" y="26" fontWeight="600">Cristal 14,31818 MHz</text>
      <path d="M160 39 V56 H78 V73 M160 56 H242 V73" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="7" y="73" width="142" height="48" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="78" y="90" fontWeight="600">CPU ÷16</text>
      <text x="78" y="106" fontSize="10">~895 kHz</text>
      <rect x="171" y="73" width="142" height="48" rx="6" stroke="#4ade80" fill="#16a34a" fillOpacity=".12"/>
      <text x="242" y="90" fontWeight="600">Vídeo ÷2</text>
      <text x="242" y="106" fontSize="10">~7,159 MHz</text>
      <text x="160" y="142" fontSize="9">Frequências candidatas, ainda não validadas eletricamente</text>
    </g>
  </svg>
</box>

Isso também permite parar a execução da CPU para depuração sem parar o vídeo, usando um mecanismo de habilitação apropriado.

## Resultados obtidos

<box gap={2}>
  <row align="center" justify="between">
    <text weight="medium">Testes comportamentais</text>
    <badge color="success">Aprovados</badge>
  </row>
  <table>
    <table-row><table-cell>Mapeamento de 32 KB de RAM</table-cell><table-cell><icon name="check-circle" color="success" inline/> Passou</table-cell></table-row>
    <table-row><table-cell>Framebuffer 256×192</table-cell><table-cell><icon name="check-circle" color="success" inline/> Passou</table-cell></table-row>
    <table-row><table-cell>Limites das regiões de memória</table-cell><table-cell><icon name="check-circle" color="success" inline/> Passou</table-cell></table-row>
    <table-row><table-cell>Referência ADD/SUB, 65.536 pares</table-cell><table-cell><icon name="check-circle" color="success" inline/> Passou</table-cell></table-row>
    <table-row><table-cell>Cálculo das frequências propostas</table-cell><table-cell><icon name="check-circle" color="success" inline/> Passou</table-cell></table-row>
  </table>
</box>

Esses resultados confirmam propriedades do modelo de software. **Ainda não comprovam o funcionamento dos circuitos 74HC, do microcódigo ou da saída RCA.**

## O que ainda me preocupa

Encontrei três riscos que merecem prioridade:

1. **CPU:** o emulador ainda não representa todas as instruções e registradores que queremos construir. Precisamos fechar a arquitetura antes de desenhar a placa.
2. **Vídeo:** o clock proposto produz uma frequência de linha próxima à convencional, mas o sinal completo de sincronismo ainda não foi validado para nosso monitor.
3. **VRAM:** precisamos demonstrar que a CPU consegue escrever enquanto o controlador lê os pixels, sem conflitos elétricos ou perda de dados.

Não vou considerar nenhum desses problemas resolvido apenas porque a arquitetura parece plausível.

## Como vou registrar as próximas decisões

Cada revisão terá número, decisões adotadas, alternativas descartadas, justificativas, testes executados, problemas pendentes e critérios de aprovação.

Também vou separar claramente três estados: **proposto**, **aprovado em simulação** e **validado fisicamente**. Assim não confundiremos uma hipótese de engenharia com um circuito pronto para fabricar.

A arquitetura atual é uma base promissora, mas ainda não é um projeto liberado para compra ou fabricação.

**Você não precisa decidir nada neste momento.** A próxima etapa técnica é fechar a CPU e seu microcódigo, confrontando a execução instrução por instrução com o emulador. Depois disso, poderemos avançar para os esquemas elétricos com muito mais segurança.

O objetivo permanece: um **ISA-1 que possamos construir de verdade**, com cada componente justificado e cada risco importante testado antes de comprometer dinheiro e material.

## user — bbb21380-9987-4e38-bafd-3eafdeca4906

Pode seguir

## assistant — f1775b83-a48d-48ae-82ae-5a377635c1b6

{"content_type": "thoughts", "source_analysis_msg_id": "5945b532-0588-4c24-880f-aeb8e6f5ecd2", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementando e documentando emulador ISA de vídeo e seus testes"}]}

## assistant — 6a3377b3-b453-4e10-9093-fd66cf52ad43

{"content": "Pensou por 43s", "content_type": "reasoning_recap"}

## assistant — 46d01267-7434-4788-b452-44b8973a0d0d

## ISA-1 — Revisão 0.9: primeiros resultados

Avancei para uma emulação mais completa da CPU e do acesso à memória de vídeo.

Nesta rodada, consegui confirmar três propriedades do modelo:

- O mapeamento dos 32 KB de RAM não produz endereços físicos duplicados.
- A CPU preliminar consegue executar um programa com registrador X, endereçamento indireto, comparação, chamada de sub-rotina e retorno.
- O controlador gráfico consegue percorrer, em ordem, os 6.144 bytes do framebuffer em um quadro, dentro de um modelo abstrato de arbitragem.

O terceiro resultado é importante, mas ainda **não prova que a SRAM física terá tempo suficiente para atender à CPU e ao vídeo**. Essa é a próxima restrição que precisamos resolver.

## Arquivos da revisão 0.9

<box border radius="lg" padding={3} gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório de engenharia e decisões — Rev. 0.9](sandbox:/mnt/data/isa1/ISA-1_REV09_RELATORIO.md)**

      <text color="secondary" size="xs">Decisões D11–D16, resultados dos testes, riscos identificados e próximos critérios de aprovação.</text>
    </box>
  </row>
  <divider/>
  <row align="center" gap={3}>
    <icon name="file-code" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Emulador e testes — Rev. 0.9](sandbox:/mnt/data/isa1/isa1_rev09_model.py)**

      <text color="secondary" size="xs">Código Python executado nesta revisão. Utiliza também o emulador da Rev. 0.7.</text>
    </box>
  </row>
</box>

## O que os testes revelaram

<box gap={2}>
  <row justify="between" align="center">
    <text weight="medium">Resultados da simulação comportamental</text>
    <badge color="success">Aprovados</badge>
  </row>
  <table>
    <table-row><table-cell>RAM física</table-cell><table-cell align="end">32.768 endereços distintos</table-cell></table-row>
    <table-row><table-cell>Framebuffer</table-cell><table-cell align="end">49.152 pixels</table-cell></table-row>
    <table-row><table-cell>Leituras de vídeo por quadro</table-cell><table-cell align="end">6.144</table-cell></table-row>
    <table-row><table-cell>Requisições abstratas de CPU atendidas</table-cell><table-cell align="end">12.000</table-cell></table-row>
    <table-row><table-cell>Frequência de linha calculada</table-cell><table-cell align="end">15.734,26 Hz</table-cell></table-row>
    <table-row><table-cell>Frequência de quadro calculada</table-cell><table-cell align="end">60,0544 Hz</table-cell></table-row>
  </table>
</box>

A CPU também executou corretamente o programa de integração que utiliza X, acesso indireto à memória, comparação, salto condicional, chamada de sub-rotina e retorno.

### Um problema importante identificado

O clock de pixels proposto oferece aproximadamente **139,7 nanossegundos por pixel**.

Isso não significa que podemos realizar um acesso completo à SRAM nesse intervalo. Uma memória com tempo de acesso de 150 ns, por exemplo, já seria lenta demais para essa hipótese, mesmo antes de considerar multiplexadores e outros atrasos.

Portanto, a simulação atual demonstra a organização dos acessos, **mas não sua viabilidade elétrica**.

Vou tratar a escolha da velocidade da SRAM e a arbitragem de barramento como decisões críticas, antes de fechar o circuito de vídeo.

## Próxima decisão técnica

A Rev. 0.9 estabelece o comportamento esperado de mais instruções. O próximo passo será transformar essas instruções em microoperações reais, identificando quais registradores fornecem dados, quais recebem dados e quais sinais de controle são necessários em cada ciclo.

Isso permitirá calcular a largura do microcódigo e começar a escolher os CIs da CPU com justificativas concretas.

**Situação atual do ISA-1:** avançamos na validação de software, mas o hardware permanece bloqueado para fabricação. Não é necessário decidir nada agora; as questões pendentes são de engenharia e já estão registradas no relatório.

## user — bbb21802-22ca-4313-ba4e-384a042e5449

Pode seguir

## assistant — 3b676a5f-c787-4d81-b8fb-cce4d99da50b

{"content_type": "thoughts", "source_analysis_msg_id": "108a0766-89c3-4b48-95cd-0c5def33fabe", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou arquivos, código, testes e riscos do modelo ISA-1"}]}

## assistant — dc65c870-453b-421f-94f1-6158b44eb419

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — af95db64-4fd0-4ebf-b624-e6d3b33a94ff

## ISA-1 — Revisão 1.0: auditoria ampliada

Avancei na validação e encontrei uma questão importante no vídeo que precisamos resolver antes de definir o circuito.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Resultados dos testes executados</text>
  <table>
    <table-row><table-cell>Decodificação dos 65.536 endereços</table-cell><table-cell><icon name="check-circle" color="success" inline/> Aprovada</table-cell></table-row>
    <table-row><table-cell>ADD, SUB e CMP executados no emulador</table-cell><table-cell><icon name="check-circle" color="success" inline/> 196.608 casos</table-cell></table-row>
    <table-row><table-cell>Pilha: 256 PUSH + 256 POP</table-cell><table-cell><icon name="check-circle" color="success" inline/> Aprovada</table-cell></table-row>
    <table-row><table-cell>Sequência de leitura da imagem</table-cell><table-cell><icon name="check-circle" color="success" inline/> 6.144 bytes</table-cell></table-row>
  </table>
  <caption>São testes comportamentais em Python, ainda não simulações dos componentes eletrônicos.</caption>
</box>

### A descoberta sobre o vídeo

Com nosso clock candidato de 7,15909 MHz, transmitir 256 pixels leva aproximadamente **35,76 µs**, e não os 47,7 µs que havíamos usado como referência para a região ativa.

Isso significa que a imagem ocupará uma região horizontal menor do sinal, a menos que modifiquemos a frequência dos pixels ou a estratégia de apresentação.

Não é necessariamente um defeito, mas precisamos decidir a geometria da imagem com base em temporizações reais, e não apenas na resolução desejada.

Outro ponto: a proposta de 262 linhas por quadro é próxima de uma temporização progressiva de 60 Hz, mas não equivale automaticamente ao entrelaçamento NTSC convencional. A compatibilidade com o monitor RCA ainda precisa ser demonstrada.

**Decisão:** manter 256×192 como resolução lógica, mas não congelar o circuito gerador de vídeo até concluirmos essa análise.

## Arquivos da revisão 1.0

<box border radius="lg" padding={3} gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório de engenharia — Rev. 1.0](sandbox:/mnt/data/isa1/ISA-1_REV10_RELATORIO.md)**

      <text color="secondary" size="xs">Decisões D17–D22, testes, erros encontrados, riscos e critérios de aprovação.</text>
    </box>
  </row>
  <divider/>
  <row align="center" gap={3}>
    <icon name="file-code" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Auditoria executável — Python](sandbox:/mnt/data/isa1/isa1_rev10_audit.py)**

      <text color="secondary" size="xs">Executa os testes de endereçamento, aritmética, pilha e geometria do framebuffer.</text>
    </box>
  </row>
</box>

## O que decidi para reduzir o risco de construção

Vou manter o ISA-1 modular, com três marcos de validação física: primeiro a CPU funcionando com ROM, RAM e LEDs de diagnóstico; depois o controlador gráfico produzindo imagem independentemente; finalmente a integração dos dois com arbitragem da VRAM.

Isso nos permitirá identificar problemas em cada módulo sem precisar depurar o computador inteiro de uma vez.

Também identifiquei uma lacuna na CPU: ainda faltam definir completamente as instruções para inicializar a pilha, transferir dados entre registradores e manipular memória de forma conveniente. Não vou congelar o conjunto de instruções antes de resolver isso.

### Estado atual

<box gap={2}>
  {#each [{name:"Modelo de memória",status:"Testes comportamentais aprovados",ok:true},{name:"CPU e instruções",status:"Emulação parcial aprovada",ok:true},{name:"Microcódigo e datapath",status:"Ainda não implementados",ok:false},{name:"Vídeo e arbitragem",status:"Temporização ainda não validada",ok:false},{name:"Esquemático e lista definitiva",status:"Bloqueados até validação",ok:false}] as item}
    <row align="center" gap={2}>
      <icon name={item.ok?"check-circle-2":"circle-dashed"} color={item.ok?"success":"tertiary"}/>
      <box flex="1" gap="2px">
        <text weight="medium" size="sm">{item.name}</text>
        <caption>{item.status}</caption>
      </box>
    </row>
  {/each}
</box>

**Minha próxima prioridade técnica é construir um modelo de microoperações independente do emulador**, para verificar se uma CPU feita com registradores, ALU e sinais de controle realmente consegue executar as instruções escolhidas.

É essa comparação que começará a transformar o ISA-1 de uma arquitetura de software em um projeto de hardware verificável.

Continuamos sem necessidade de comprar componentes ou tomar decisões adicionais da sua parte.

## user — bbb21273-450a-480f-97ca-24eb4815ee7c

Você acha que está muito complexo? Seria melhor dar algum passo atrás? 

## assistant — 0c4646d6-1c5b-4652-b5c9-3282e39585d3

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — ffef473f-cf94-4633-8567-9dccf0cdb180

**Sim. Acho que o ISA-1 ficou complexo demais para a primeira versão física. E recomendo darmos um passo atrás — mas sem abandonar o que já desenvolvemos.**

O problema não é a CPU de 8 bits, nem o fato de usarmos componentes 74HC. O problema é que estamos tentando construir e validar várias partes difíceis simultaneamente.

Hoje temos quatro desafios importantes:

1. Uma CPU própria, com registradores de 8 e 16 bits, ALU e microcódigo.
2. Um sistema de memória com ROM, RAM, VRAM e dispositivos mapeados.
3. Um controlador de vídeo composto, com sincronismo, pixels e acesso compartilhado à memória.
4. Um firmware capaz de operar tudo isso, incluindo teclado, texto e gráficos.

Cada um desses desafios é viável isoladamente. Mas, juntos, aumentam muito a quantidade de componentes, conexões, possibilidades de falha e trabalho de depuração.

E você estabeleceu uma prioridade que considero correta: **queremos construir um computador que realmente funcione, não apenas demonstrar uma arquitetura interessante.**

## Minha recomendação: simplificar a primeira versão, não o projeto inteiro

Eu dividiria o ISA-1 em duas gerações de hardware compatíveis.

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="48px" align="center" justify="center">
      <icon name="cpu" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **ISA-1 Core — primeira construção**

      CPU 8 bits, ROM, RAM, clock manual, LEDs de diagnóstico e interface de expansão.

      O objetivo será executar programas reais, com todas as instruções necessárias, sem depender do vídeo para funcionar.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="48px" align="center" justify="center">
      <icon name="monitor" size="xl"/>
    </box>
    <box flex="1" gap={1}>
      **ISA-1 Video — expansão posterior**

      Controlador gráfico autônomo, VRAM e saída RCA.

      O vídeo será desenvolvido e testado como um módulo independente, conectado à CPU somente depois de funcionar isoladamente.
    </box>
  </row>
</box>

Isso permite manter nosso objetivo original: um computador próprio, programável e capaz de desenhar na tela.

A diferença é que não precisaremos fazer tudo funcionar ao mesmo tempo.

## O que eu simplificaria de verdade

| Elemento | Projeto atual | Minha proposta |
|---|---|---|
| CPU | 8 bits microprogramada | Manter |
| Registrador X | 16 bits | Adiar |
| Pilha | SP de 16 bits | Simplificar inicialmente |
| ROM | 16 KB mapeados | Manter |
| RAM | 32 KB | Manter |
| Vídeo | 256×192 | Manter como expansão |
| Teclado | 64 teclas | Manter como expansão |
| Clock | Até ~1 MHz | Começar com clock manual |
| Placas | Sistema completo | Módulos testados separadamente |

Existe uma simplificação especialmente valiosa: **não precisamos começar com uma CPU capaz de executar um sistema operacional completo**.

Podemos começar com uma CPU que execute corretamente um conjunto pequeno de instruções e depois ampliar seu microcódigo e seus recursos.

Mas devemos projetar desde já os conectores e sinais necessários para a expansão, evitando descartar as placas que construirmos.

## A primeira meta seria muito mais simples

Quero que o primeiro ISA-1 consiga executar este programa:

```asm
        LDA #10
        LDB #20
        ADD
        STA $4000
        HLT
```

E que possamos verificar fisicamente:

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Resultado esperado do primeiro programa</text>
  <grid columns={3} gap={2}>
    <grid-item>
      <box background="surface-secondary" radius="md" padding={2} gap={1} align="center">
        <caption>Registrador A</caption>
        <title size="xl" color="default" tabularNums>1E</title>
        <caption>Hexadecimal</caption>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface-secondary" radius="md" padding={2} gap={1} align="center">
        <caption>RAM $4000</caption>
        <title size="xl" color="default" tabularNums>30</title>
        <caption>Decimal</caption>
      </box>
    </grid-item>
    <grid-item>
      <box background="surface-secondary" radius="md" padding={2} gap={1} align="center">
        <caption>CPU</caption>
        <title size="xl" color="default">HLT</title>
        <caption>Parada</caption>
      </box>
    </grid-item>
  </grid>
</box>

Esse pequeno programa exercita busca de instruções, registradores, ALU, endereçamento, memória e controle da CPU.

É um marco de engenharia muito mais fácil de verificar do que tentar ligar um computador inteiro e descobrir por que a tela está preta.

## E os gráficos?

Eu não abandonaria o framebuffer único de 256×192. Continuo considerando essa uma boa arquitetura para o ISA-1.

Mas faria uma alteração importante: **o módulo de vídeo teria seu próprio acesso à VRAM e uma interface bem definida para receber dados da CPU**.

Assim, poderemos testar o vídeo usando padrões gravados na memória antes de conectar a CPU.

Também estudaria uma alternativa com VRAM de duas portas, caso a disponibilidade e o preço justifiquem a redução da complexidade de arbitragem. Não escolheria esse componente sem antes verificar o custo.

## Minha decisão

<box gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success" size="lg"/>
    **Manter o objetivo final do ISA-1.**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success" size="lg"/>
    **Reduzir o escopo da primeira placa.**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success" size="lg"/>
    **Projetar expansões sem exigir que sejam construídas agora.**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success" size="lg"/>
    **Validar a CPU fisicamente antes de integrar vídeo e teclado.**
  </row>
</box>

Há uma ressalva: isso reduz o risco de integração, mas não elimina a complexidade de construir uma CPU com componentes discretos. E ainda precisamos demonstrar seu funcionamento com um modelo de microoperações e um esquema elétrico real.

**Minha avaliação é que estamos tentando construir a versão 3 de um computador que ainda não teve sua versão 1 ligada.**

Então eu mudaria nossa estratégia para o **ISA-1 Rev. 1.1 — arquitetura modular**, preservando os objetivos anteriores, mas estabelecendo uma primeira versão mínima, testável e expansível.

Acredito que esse é o melhor equilíbrio entre ambição e possibilidade real de construção. <MemoryCite />

## user — bbb21907-b9b0-4c4b-9c77-a0c1f369b2d9

Vejo que teremos trabalho de qualquer jeito kkkk
Então pensei no seguinte
Vamos seguir como está
E ter um projeto final 100% usável de uma vez
Aí te pergunto, já teve um PC antigo semelhante o que estamos planejando? 

## assistant — 326fcc49-b192-4662-a3e8-a462485775a8

{"content_type": "thoughts", "source_analysis_msg_id": "d0d4efe9-b52f-4f05-af0c-7bb2aa54dffd", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 6 sites"}]}

## assistant — e663af25-a195-4fa3-9b99-d838bf8188ed

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 43a7db22-3ff2-4e6b-a994-e7cc39bc3c56

Kkkkk, teremos trabalho de qualquer jeito! 😄 E gostei da decisão: **vamos manter o ISA-1 completo como objetivo**, com CPU própria, memória, teclado, vídeo e capacidade de executar programas.

E sim: **já existiram computadores muito parecidos com o que estamos planejando.** Alguns são tão próximos que podem servir como referências de engenharia, permitindo aproveitar soluções comprovadas em vez de reinventar cada circuito.

O mais interessante é que nosso ISA-1 mistura características de computadores do final dos anos 1970 e início dos anos 1980 com uma abordagem moderna de construção usando lógica 74HC.

## Os computadores mais parecidos com o ISA-1

<box gap={4}>
  <row align="start" gap={3}>
    <AsyncImage query="Gigatron TTL computer assembled board retro computer" aspectRatio="4:3" maxWidth="148px"/>
    <box flex="1" gap={1}>
      <text weight="medium">1. <Entity category="product" value="Gigatron TTL Computer" disambig="computador de 8 bits construído com lógica TTL"/></text>
      <badge color="success">Referência mais próxima</badge>
      Um computador de 8 bits construído sem microprocessador convencional, usando lógica da família 74xx, ROM e RAM. Produz vídeo colorido e som, com menos de 40 circuitos integrados na configuração original. <Cite ref="turn799190search45"/>
      <text color="secondary" size="xs">O que podemos aproveitar: organização da ALU, redução de componentes e integração do vídeo.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Ben Eater 8 bit breadboard computer completed colorful wires LED" aspectRatio="4:3" maxWidth="148px"/>
    <box flex="1" gap={1}>
      <text weight="medium">2. <Entity category="other" value="Computador de 8 bits de Ben Eater" disambig="projeto educacional de computador microprogramado"/></text>
      Tem registradores, ALU, barramento de 8 bits, clock e controle por microcódigo em EEPROM, exatamente os princípios que queremos empregar na CPU do ISA-1. <Cite refs={["turn799190search0","turn799190search3"]}/>
      <text color="secondary" size="xs">O que podemos aproveitar: microcódigo, organização dos registradores e esquemas de referência.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="original Apple 1 computer 1976 wooden case keyboard monitor" aspectRatio="4:3" maxWidth="148px"/>
    <box flex="1" gap={1}>
      <text weight="medium">3. <Entity category="product" value="Apple I" disambig="computador pessoal de 1976"/></text>
      O Apple I de 1976 já reunia CPU, teclado, vídeo e monitor de sistema para escrever, examinar e executar programas. Usava o microprocessador 6502, portanto sua CPU era bem diferente da nossa. <Cite ref="turn799190search42"/>
      <text color="secondary" size="xs">O que podemos aproveitar: a experiência de uso, o monitor em ROM e a integração de teclado e tela.</text>
    </box>
  </row>
</box>

## Comparando as arquiteturas

| Característica | Gigatron | Ben Eater | ISA-1 planejado |
|---|---|---|---|
| CPU construída com lógica 74xx | Sim | Sim | Sim |
| Microcódigo em EEPROM | Não, arquitetura diferente | Sim | Sim |
| RAM de trabalho | Sim | Muito pequena | 32 KB |
| Vídeo próprio | Sim | Não | Sim |
| Teclado | Interface disponível | Não como parte central | 64 teclas |
| Gráficos | Sim, coloridos | Não | 256×192 monocromático |
| Programável | Sim | Sim | Sim |

O Gigatron demonstra que um computador útil, com gráficos e CPU de lógica discreta, é possível. Já o projeto de Ben Eater nos fornece uma referência muito boa para desenvolver uma CPU microprogramada. Nenhum dos dois, porém, é idêntico ao ISA-1.

## Uma descoberta que muda nossa estratégia

O projeto de Ben Eater disponibiliza **esquemáticos completos e um projeto KiCad**, incluindo registradores, ALU, clock e lógica de controle. <Cite ref="turn799190search2"/>

Isso é extremamente útil porque podemos estudar circuitos existentes, identificar suas limitações e adaptar as partes adequadas à nossa arquitetura de 16 bits de endereçamento.

<Link url="https://eater.net/8bit/schematics" title="Esquemáticos completos do computador de Ben Eater"/>

O Gigatron, por sua vez, mostra uma solução bastante econômica em número de chips. Mas seu método de gerar vídeo é diferente do framebuffer independente que escolhemos, então não podemos simplesmente copiar seu circuito.

## O que eu faria agora

Manteria o ISA-1 completo, como você decidiu, mas mudaria a abordagem de engenharia:

- **CPU:** usar Ben Eater como referência de circuitos, não como arquitetura final.
- **Otimização:** estudar o Gigatron para reduzir o número de chips, principalmente na ALU.
- **Experiência de uso:** seguir a filosofia dos primeiros computadores pessoais, com inicialização direta em um monitor de comandos.
- **Vídeo:** continuar desenvolvendo nosso controlador gráfico independente, aproveitando técnicas comprovadas de geração de sincronismo.

E acrescentaria um objetivo importante: ao ligar o ISA-1, quero que apareça algo assim na tela:

<box background="#101b13" theme="dark" radius="lg" padding={3} gap={1}>
  <text color="#9be29c" preserveWhitespace size="sm" weight="medium">{`ISA-1 COMPUTER
8-BIT HOME COMPUTER
REVISION 1.0

32768 BYTES RAM
16384 BYTES ROM
VIDEO 256x192 MONO

ISA-1 BASIC READY

>`}</text>
</box>
<caption>Conceito de tela inicial, não firmware já implementado.</caption>

Esse seria um computador com identidade própria, não apenas uma demonstração de LEDs piscando.

**Minha conclusão:** o Gigatron é a melhor prova de que nossa ambição é tecnicamente plausível; Ben Eater é a melhor referência inicial para a CPU; e o Apple I é uma boa inspiração para transformar tudo isso em um computador realmente utilizável.

Vou preservar essa combinação como orientação do ISA-1, sem confundir referências existentes com circuitos já validados para nosso projeto.

## user — bbb214fd-c998-4f22-80d4-3c4632ef0e87

Nossa o gigatron então eh oq estamos fazendo
Mas ele não tem ROM? 
Como funciona? 
Outro ponto, sei que pode ser difícil
Mas como seria possível não usar um PC moderno pra gravar memórias? 
E como o gigatron não tem uma? 

## assistant — 5567194a-9d96-4b70-86bc-c882f534cbfe

{"content_type": "thoughts", "source_analysis_msg_id": "05cc9f22-7936-43f7-94ee-4c850feef3a3", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 12 sites"}]}

## assistant — 965ad9bd-5e02-441e-abb9-f5984cb9ce31

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 0ef93044-066f-4267-be6f-1d1a26c0498f

Sim! 😄 E você percebeu uma semelhança muito importante: **o Gigatron é provavelmente o parente mais próximo do ISA-1 que encontramos até agora.**

Mas há uma diferença fundamental: **o Gigatron tem ROM, sim! O que ele não tem é um microprocessador convencional, como o Z80 ou o 6502.**

Isso muda bastante a forma como ele funciona.

## 1. Como o Gigatron funciona sem um processador convencional?

<AsyncImageGroup query={["Gigatron TTL computer PCB top view 74HCT ROM RAM","Gigatron TTL computer block diagram architecture ROM RAM ALU"]} aspectRatio="5:3" layout="carousel"/>

O Gigatron constrói a própria CPU com circuitos lógicos da família 74xx.

Em vez de comprar um chip que já contém uma CPU, seus criadores montaram os componentes fundamentais de um processador:

- Registradores para armazenar valores.
- Uma ALU para executar operações matemáticas e lógicas.
- Um contador de programa para selecionar instruções.
- Lógica de controle para executar essas instruções.
- Memória ROM para armazenar o programa.
- Memória RAM para armazenar dados.

O resultado é uma CPU de verdade, embora distribuída por vários circuitos integrados.

E existe uma diferença muito interessante em relação ao nosso projeto: o Gigatron usa uma arquitetura de instruções bastante simples, com controle implementado em lógica, enquanto o ISA-1 prevê uma CPU microprogramada.

## 2. A ROM do Gigatron é maior do que parece

Segundo a documentação oficial, o Gigatron utiliza:

<grid columns={2} gap={3}>
  <grid-item>
    <box border radius="lg" padding={3} gap={1}>
      <caption>Memória ROM</caption>
      <title size="2xl" color="default" tabularNums>128 KB</title>
      <text color="secondary" size="xs">64K × 16 bits, EPROM apagável por luz UV</text>
    </box>
  </grid-item>
  <grid-item>
    <box border radius="lg" padding={3} gap={1}>
      <caption>Memória RAM</caption>
      <title size="2xl" color="default" tabularNums>32 KB</title>
      <text color="secondary" size="xs">SRAM de 8 bits</text>
    </box>
  </grid-item>
</grid>
<caption>Especificações do Gigatron original. <Cite ref="turn804549search0"/></caption>

A ROM armazena instruções nativas, rotinas de vídeo, inicialização e programas. Ela já vem gravada no kit, portanto o computador funciona assim que é montado corretamente. <Cite ref="turn804549search18"/>

O segredo é que **o Gigatron executa programas de duas maneiras**.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 218" width="100%">
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <rect x="80" y="4" width="160" height="40" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x="160" y="20" fontWeight="600">ROM — 128 KB</text>
      <text x="160" y="34" fontSize="9">Instruções nativas e firmware</text>
      <path d="M160 44 V61" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="80" y="61" width="160" height="42" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".12"/>
      <text x="160" y="77" fontWeight="600">CPU física de 8 bits</text>
      <text x="160" y="92" fontSize="9">Registradores + ALU + controle</text>
      <path d="M160 103 V121 H79 V137 M160 121 H241 V137" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="4" y="137" width="151" height="49" rx="6" stroke="#4ade80" fill="#16a34a" fillOpacity=".10"/>
      <text x="79" y="153" fontWeight="600">Vídeo e som</text>
      <text x="79" y="168" fontSize="9">Gerados pelo firmware</text>
      <rect x="165" y="137" width="151" height="49" rx="6" stroke="#f59e0b" fill="#f59e0b" fillOpacity=".10"/>
      <text x="241" y="153" fontWeight="600">vCPU virtual</text>
      <text x="241" y="168" fontSize="9">Interpreta programas da RAM</text>
      <path d="M241 186 V199" stroke="#94a3b8" strokeWidth="1.5"/>
      <text x="241" y="212" fontSize="10">Jogos, BASIC e aplicativos</text>
    </g>
  </svg>
</box>

A CPU física executa diretamente as instruções da ROM. Dentro desse firmware existe um interpretador de outra CPU, chamada **vCPU**, que executa programas armazenados na RAM. Assim, o usuário consegue rodar novos programas sem trocar a ROM. <Cite refs={["turn804549search6","turn804549search9"]}/>

Esse é um dos aspectos mais inteligentes do projeto.

## 3. Como programar um computador sem usar um PC moderno?

Aqui existem três possibilidades reais.

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="keyboard" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Opção A — Digitar programas no próprio computador**

      A ROM contém um monitor de comandos ou interpretador BASIC. Você liga o ISA-1, digita seu programa no teclado e executa.

      Não precisa de outro computador para programar ou executar. A limitação é que, sem armazenamento permanente, o programa desaparece quando a energia acaba.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="save" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Opção B — Salvar programas em uma memória não volátil**

      Podemos acrescentar uma EEPROM de dados, separada da ROM de inicialização.

      O ISA-1 teria comandos como `SAVE` e `LOAD`, gravando e recuperando programas diretamente. Isso exige um circuito de escrita e rotinas de firmware, mas é tecnicamente viável sem microcontrolador.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" size="44px" align="center" justify="center">
      <icon name="wrench" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Opção C — O ISA-1 regravar seu próprio firmware**

      Usando EEPROM apropriada, a CPU pode executar uma rotina de atualização que grava uma nova versão do firmware.

      Precisamos de proteção contra escrita acidental e um mecanismo de recuperação caso a gravação seja interrompida.
    </box>
  </row>
</box>

Existe, porém, uma distinção: **programar o computador sem PC é relativamente simples; preparar a primeira ROM de inicialização sem nenhum equipamento externo é mais difícil.**

Para a primeira gravação, podemos utilizar um gravador externo, montar um gravador manual com chaves e contadores, ou adquirir uma EEPROM já programada. Depois do primeiro boot, podemos tornar o ISA-1 autossuficiente para desenvolver e salvar programas.

## 4. E como o Gigatron carrega programas novos?

O Gigatron original usa um aplicativo chamado *Loader*, já existente na ROM, que recebe programas externos e os coloca na RAM.

A documentação oficial mostra um Arduino atuando como ponte entre um computador moderno e o Gigatron. Mas isso é um acessório para facilitar a transferência, não uma parte da CPU. Também existem versões de ROM que iniciam o BASIC diretamente. <Cite refs={["turn804549search2","turn804549search6"]}/>

Ou seja: **o Gigatron não dispensa a ROM; ele evita precisar regravá-la toda vez que você cria um programa.**

## 5. O que eu escolheria para o ISA-1

A sua ideia de independência combina muito bem com nosso projeto. Eu faria o ISA-1 com três níveis de software:

| Camada | Memória | Função |
|---|---|---|
| Firmware de inicialização | ROM/EEPROM protegida | Inicializar CPU, vídeo e teclado |
| Programas em execução | RAM | Editor, BASIC e aplicativos |
| Armazenamento permanente | EEPROM separada | Salvar e carregar programas |

Assim, nosso computador poderia ligar diretamente nesta tela:

<box background="#0c1a12" theme="dark" radius="lg" padding={3} gap={1}>
  <text color="#9be29c" preserveWhitespace size="sm">{`ISA-1 HOME COMPUTER
64K ADDRESS SPACE
32768 BYTES RAM

ISA-1 BASIC READY

> 10 FOR I=1 TO 10
> 20 PRINT "OLA ISABEL"
> 30 NEXT I
> RUN

OLA ISABEL
OLA ISABEL
OLA ISABEL
...

> SAVE "TESTE"
PROGRAM SAVED

>`}</text>
</box>
<caption>Exemplo de experiência desejada, ainda não implementada.</caption>

Eu manteria a ROM principal protegida e acrescentaria uma EEPROM separada para armazenamento dos programas. Isso é mais seguro do que permitir que um erro no BASIC apague o firmware de inicialização.

E há uma decisão adicional que considero muito importante: **o ISA-1 deve conseguir compilar ou interpretar programas diretamente nele mesmo**, sem exigir que você desenvolva tudo em um PC moderno.

O PC moderno continuaria útil para desenvolver e testar o firmware inicial, mas não seria necessário para usar o computador depois de pronto.

**A grande lição do Gigatron para nós é esta:** não precisamos criar uma CPU extremamente sofisticada para ter um computador sofisticado. Uma CPU simples, combinada com um firmware bem projetado, pode fazer muito mais do que parece.

Isso merece entrar na próxima revisão da arquitetura do ISA-1.

## user — bbb21116-d0a3-422d-8bf4-2b49ccd48a9d

Me fala mais sobre o gigatron
Quantos CIs ele usa? E ele tem vídeo colorido, como ficaram isso? 

## assistant — fd7273a2-0da0-49bc-a544-86c30785aa9b

{"content_type": "thoughts", "source_analysis_msg_id": "8edbae73-5a30-435e-a019-23465a65fb5e", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 11 sites"}]}

## assistant — 40141fb7-6160-4724-8878-f5193a57f1ad

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — ed41ed06-d273-4160-b97f-6d4291033f82

O <Entity category="other" value="Gigatron TTL" disambig="computador de 8 bits construído com circuitos lógicos discretos"/> é um projeto fascinante, principalmente para quem está desenvolvendo um computador como o nosso ISA-1.

O mais impressionante é que ele consegue gerar **vídeo colorido, executar jogos, interpretar BASIC e produzir som sem utilizar um microprocessador convencional nem um chip dedicado de vídeo**.

<AsyncImageGroup query={["Gigatron TTL computer original assembled PCB red board chips","Gigatron TTL computer VGA style colorful game screen VGA monitor"]} aspectRatio="5:3" layout="carousel"/>

E existe uma lição importante aqui: os criadores do Gigatron não construíram uma CPU muito poderosa para depois acrescentar vídeo. Eles projetaram uma CPU simples cuja arquitetura facilita a geração de vídeo por software.

Essa escolha reduz bastante a quantidade de componentes, embora imponha limitações ao processamento disponível para os programas.

## 1. Quantos CIs o Gigatron utiliza?

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <caption>Lógica TTL da CPU</caption>
      <title size="2xl" color="default" tabularNums>34–36</title>
      <text color="secondary" size="xs">Conforme a revisão e a convenção de contagem</text>
    </grid-item>
    <grid-item>
      <caption>Memórias principais</caption>
      <title size="2xl" color="default" tabularNums>2</title>
      <text color="secondary" size="xs">Uma ROM e uma SRAM</text>
    </grid-item>
  </grid>
  <divider color="subtle"/>
  O projeto original é frequentemente descrito como tendo **36 CIs TTL, mais ROM e RAM**, ou aproximadamente 38 circuitos integrados principais. A documentação inicial dos criadores também menciona 34 CIs para a CPU propriamente dita. <Cite refs={["turn505935search6","turn505935search7"]}/>
</box>

E isso inclui grande parte das funções de vídeo e som!

Para comparação, nosso ISA-1 estava caminhando para uma quantidade significativamente maior de chips, principalmente por causa do microcódigo, dos registradores de 16 bits e do vídeo independente.

## 2. Como ele consegue produzir 64 cores?

Aqui está a parte mais engenhosa.

O Gigatron não possui um chip gráfico dedicado. Ele utiliza **um registrador de saída de 8 bits e resistores** para gerar sinais RGB compatíveis com VGA.

Seis bits representam as cores, enquanto dois bits controlam os sincronismos.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Distribuição dos 8 bits de saída</text>
  <grid columns={8} gap="3px">
    {#each [{b:"7",t:"V",c:"#64748b"},{b:"6",t:"H",c:"#64748b"},{b:"5",t:"B1",c:"#2563eb"},{b:"4",t:"B0",c:"#2563eb"},{b:"3",t:"G1",c:"#16a34a"},{b:"2",t:"G0",c:"#16a34a"},{b:"1",t:"R1",c:"#dc2626"},{b:"0",t:"R0",c:"#dc2626"}] as x}
      <grid-item>
        <box background={x.c} theme="dark" radius="sm" padding={{top:2,bottom:2}} align="center" gap={1}>
          <text color="#ffffff" weight="medium" size="sm">{x.t}</text>
          <text color="#ffffff" size="3xs">{x.b}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Representação lógica: V/H são sincronismos vertical e horizontal; R, G e B representam as componentes de cor.</caption>
</box>

Cada canal de cor tem 2 bits, ou seja, quatro níveis possíveis de intensidade.

\[
4_{\text{vermelho}}\times4_{\text{verde}}\times4_{\text{azul}}=64\text{ cores}
\]

<box gap={2}>
  <text weight="medium">Paleta RGB de 64 cores</text>
  <grid columns={8} gap="3px">
    {#each Array.from({length:64},(_,i)=>{const r=Math.floor(i/16),g=Math.floor(i/4)%4,b=i%4;return `rgb(${r*85},${g*85},${b*85})`}) as c,i}
      <grid-item>
        <box background={c} aspectRatio="1/1" radius="2xs" border={{size:1,color:"subtle"}}/>
      </grid-item>
    {/each}
  </grid>
  <caption>Paleta idealizada, com quatro níveis igualmente espaçados por canal. As intensidades reais dependem da rede de resistores e da carga VGA.</caption>
</box>

Os resistores funcionam como um **conversor digital-analógico (DAC)** extremamente simples. Eles combinam as saídas digitais para produzir as tensões que o monitor interpreta como intensidades de vermelho, verde e azul.

Não existe um conversor de vídeo sofisticado: apenas lógica digital, resistores e o conector VGA. <Cite refs={["turn505935search18","turn505935search3"]}/>

## 3. Como ele desenha os pixels sem placa de vídeo?

O segredo é que a própria CPU gera os pixels continuamente.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 175" width="100%">
    <g textAnchor="middle" fontSize="11" fill="currentColor">
      <rect x="5" y="18" width="88" height="48" rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="49" y="37" fontWeight="600">RAM</text>
      <text x="49" y="52" fontSize="9">Cores dos pixels</text>
      <path d="M93 42 H117" stroke="#94a3b8" strokeWidth="1.5"/>
      <path d="M113 38 L119 42 L113 46" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="119" y="18" width="85" height="48" rx="6" fill="#2563eb" fillOpacity=".12" stroke="#60a5fa"/>
      <text x="161" y="37" fontWeight="600">CPU</text>
      <text x="161" y="52" fontSize="9">Lê cada pixel</text>
      <path d="M204 42 H225" stroke="#94a3b8" strokeWidth="1.5"/>
      <path d="M221 38 L227 42 L221 46" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="227" y="18" width="88" height="48" rx="6" fill="#16a34a" fillOpacity=".12" stroke="#4ade80"/>
      <text x="271" y="37" fontWeight="600">Registrador</text>
      <text x="271" y="52" fontSize="9">RGB + sync</text>
      <path d="M271 66 V87" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="210" y="87" width="105" height="34" rx="6" fill="#f59e0b" fillOpacity=".12" stroke="#f59e0b"/>
      <text x="262" y="108" fontWeight="600">Resistores DAC</text>
      <path d="M262 121 V137" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="210" y="137" width="105" height="32" rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="262" y="157" fontWeight="600">Monitor VGA</text>
    </g>
  </svg>
</box>

A CPU executa instruções especialmente organizadas na ROM para buscar dados da RAM e enviá-los ao registrador de vídeo nos momentos corretos.

Esse método é conhecido como *racing the beam*: o programa acompanha a varredura do monitor.

O Gigatron opera a **6,25 MHz** e apresenta normalmente uma imagem lógica de **160×120 pixels**, com 64 cores, em um sinal VGA próximo de 60 Hz. Cada pixel lógico ocupa aproximadamente quatro posições horizontais do sinal VGA, e as linhas são repetidas ou tratadas de acordo com o modo de vídeo. <Cite refs={["turn505935search0","turn505935search3"]}/>

<grid columns={2} gap={2}>
  <grid-item>
    <AsyncImage query="Gigatron TTL computer game Racer colorful pixelated VGA screen" aspectRatio="4:3"/>
    <caption>Exemplo do estilo gráfico do Gigatron.</caption>
  </grid-item>
  <grid-item>
    <AsyncImage query="Gigatron TTL computer Mandelbrot fractal VGA display colorful" aspectRatio="4:3"/>
    <caption>O computador também consegue desenhar fractais.</caption>
  </grid-item>
</grid>

## 4. Mas isso não ocupa toda a CPU?

**Ocupa uma parcela enorme!**

Como a CPU precisa produzir os pixels e os sincronismos nos instantes corretos, ela não pode simplesmente parar a geração do vídeo para executar um programa.

Os criadores resolveram isso aproveitando intervalos disponíveis entre linhas e quadros e, no modo padrão, sacrificando parte das linhas para disponibilizar mais tempo de processamento aos aplicativos. <Cite ref="turn505935search1"/>

É uma troca deliberada: menos hardware, mas também menos tempo de CPU para programas.

## 5. O que isso significa para nosso ISA-1?

Aqui aparece uma oportunidade interessante.

| Característica | Gigatron | ISA-1 atual |
|---|---|---|
| CPU | 8 bits, lógica discreta | 8 bits, lógica discreta |
| Clock planejado | 6,25 MHz | ~0,9 MHz |
| Vídeo | VGA colorido | RCA monocromático |
| Resolução lógica | 160×120 | 256×192 |
| Cores | 64 | 2 |
| Geração de vídeo | Pela CPU | Controlador independente |
| Complexidade de hardware | Muito otimizada | Ainda indefinida |

O Gigatron consegue gerar vídeo colorido com poucos componentes porque **foi projetado desde o início para essa tarefa**.

Não seria correto concluir que podemos simplesmente acrescentar seis bits de cor ao ISA-1 e obter o mesmo resultado.

Mas podemos aproveitar várias ideias, especialmente a arquitetura simplificada da CPU e o uso de registradores e resistores para gerar vídeo.

### Uma decisão que vale investigar

Acho que deveríamos comparar duas arquiteturas antes de fechar nosso hardware:

**Arquitetura A — ISA-1 atual:** CPU microprogramada, vídeo independente e framebuffer monocromático.

**Arquitetura B — inspirada no Gigatron:** CPU mais simples, com instruções e temporização pensadas para gerar vídeo colorido por software.

A arquitetura B pode reduzir bastante o número de chips, mas exige reformular o conjunto de instruções e aceitar limitações de desempenho.

E tem um detalhe que considero especialmente interessante: **o Gigatron já demonstra que vídeo colorido e CPU discreta podem coexistir em menos de 40 CIs TTL, além das memórias.**

Minha inclinação é estudar profundamente essa solução antes de congelar o ISA-1. Podemos descobrir que parte da complexidade que estamos adicionando é desnecessária, sem precisar abrir mão de um computador completo e programável.

Para consultar os circuitos originais: <Link url="https://gigatronttl.eu/posts/482.html" title="Documentação técnica e esquemáticos do Gigatron"/>.

## user — bbb21935-cf1f-41e4-9352-c14904b5fcde

Vó que ele usa vga não RCA qual a diferença? 

## assistant — 2e66dc1a-47ba-4593-bc53-78b137217b5f

Essa diferença é muito importante para o ISA-1! 😄

O **Gigatron usa VGA**, enquanto nosso ISA-1 foi planejado para usar **RCA (vídeo composto)**.

Apesar de ambos transmitirem imagens analógicas, funcionam de maneiras bastante diferentes.

## 1. VGA vs. RCA

<grid columns={2} gap={3}>
  <grid-item>
    <AsyncImage query="VGA blue 15 pin male connector close up" aspectRatio="5:4"/>
    **VGA — usado pelo Gigatron**

    <text color="secondary" size="sm">Conector de 15 pinos, normalmente azul.</text>
  </grid-item>
  <grid-item>
    <AsyncImage query="yellow RCA composite video connector male plug close up" aspectRatio="5:4"/>
    **RCA — planejado para o ISA-1**

    <text color="secondary" size="sm">Conector amarelo, com um único sinal de vídeo composto.</text>
  </grid-item>
</grid>

### A principal diferença

No VGA, as informações são transmitidas separadamente:

- Vermelho (R)
- Verde (G)
- Azul (B)
- Sincronismo horizontal (HSync)
- Sincronismo vertical (VSync)

No RCA composto, todas as informações de imagem e sincronismo passam pelo **mesmo fio de sinal**. Para transmitir cores, também é necessário codificar a informação cromática no sinal composto.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Como os sinais são organizados</text>
  <svg viewBox="0 0 330 155" width="100%">
    <g fontSize="11" fill="currentColor">
      <text x="6" y="14" fontWeight="600">VGA</text>
      {#each [{y:25,label:"R",c:"#dc2626"},{y:45,label:"G",c:"#16a34a"},{y:65,label:"B",c:"#2563eb"},{y:85,label:"H",c:"#64748b"},{y:105,label:"V",c:"#64748b"}] as p}
        <text x="12" y={p.y+11}>{p.label}</text>
        <rect x="27" y={p.y} width="111" height="13" rx="3" fill={p.c} fillOpacity=".8"/>
      {/each}
      <text x="169" y="14" fontWeight="600">RCA composto</text>
      <rect x="169" y="50" width="151" height="42" rx="6" fill="#eab308" fillOpacity=".15" stroke="#eab308"/>
      <text x="245" y="67" fontSize="10" textAnchor="middle">Imagem + sincronismo</text>
      <text x="245" y="81" fontSize="10" textAnchor="middle">em um sinal</text>
      <text x="165" y="139" fontSize="9" fill="currentColor">Ambos precisam de terra de referência.</text>
    </g>
  </svg>
</box>

## 2. Qual é mais fácil de construir?

Isso é curioso: **para gerar vídeo colorido, VGA pode ser mais simples eletronicamente do que RCA composto colorido.**

No Gigatron, seis bits digitais controlam os níveis de vermelho, verde e azul por meio de resistores. Outros sinais controlam os sincronismos.

No RCA colorido, precisamos gerar também uma subportadora de cor com fase e amplitude controladas, além de sincronismo e luminância.

Porém, há uma ressalva importante: nosso ISA-1 foi planejado para **RCA monocromático**. Nesse caso, não precisamos gerar a subportadora de cor, e o circuito pode ser relativamente simples.

## 3. Comparação para o ISA-1

| Característica | VGA | RCA monocromático |
|---|---|---|
| Cores | RGB, facilmente | Preto e branco |
| Sincronismos | Separados | Misturados ao vídeo |
| Circuito de cores | Resistores DAC | Não necessário |
| Temporização | Mais rápida, em geral | Mais lenta, em geral |
| Qualidade de imagem | Melhor potencial | Menor nitidez |
| Monitores modernos | Entrada VGA cada vez mais rara | Entrada AV também cada vez mais rara |
| Nosso monitor automotivo | Depende de ter VGA | Compatível se tiver entrada AV |

## 4. E se fizéssemos o ISA-1 com VGA?

<AsyncImage query="Gigatron TTL computer colorful graphics on VGA LCD monitor retro computer" aspectRatio="16:9"/>

Poderíamos ter **vídeo colorido sem precisar construir um codificador de vídeo composto colorido**.

Mas VGA exige temporizações diferentes. Um modo clássico é 640×480 a aproximadamente 60 Hz, com clock de pixels de 25,175 MHz. Isso não significa que nossa CPU teria que funcionar nessa frequência: um controlador de vídeo independente poderia produzir os sinais enquanto a CPU executa instruções mais lentamente.

A dificuldade estaria no controlador, na velocidade de leitura da memória e na quantidade de componentes necessários.

Também poderíamos manter uma resolução lógica menor e ampliar os pixels na saída VGA.

## 5. Minha recomendação para o ISA-1

Considerando que você pretende utilizar uma tela automotiva pequena com entrada RCA, **eu manteria o vídeo composto monocromático por enquanto**.

Não porque VGA seja pior — pelo contrário, ele facilita bastante a geração de cores — mas porque já temos uma tela específica em mente, e mudar a saída exigiria rever o hardware.

Entretanto, eu faria uma alteração no planejamento: manteria o controlador gráfico como um módulo substituível, permitindo desenvolver futuramente uma placa VGA colorida sem redesenhar a CPU.

**E aqui está a pergunta mais interessante:** se o objetivo é termos um computador completo, com gráficos e jogos, talvez valha comparar o custo e a complexidade de uma saída RCA monocromática com uma VGA de 64 cores antes de fechar o circuito.

O Gigatron demonstra que VGA colorido com lógica discreta é possível. A decisão depende principalmente da tela que queremos usar, não apenas da quantidade de cores.

## user — bbb21c74-e46a-463e-a252-afd779852dbe

Um ponto, não tenho monitor com vga e não gostaria de comprar, por causa do tamanho mesmo, ou teria um bem pequeno e barato como o RCA? 
De resto, vamos sim revisar nosso projeto, acho legal usar o gigatron como base

## assistant — 93d738b8-93a9-4512-9314-b6cc2a0b10d5

{"content_type": "thoughts", "source_analysis_msg_id": "4b2c8888-214f-4e47-bcc3-9f3751eda2fe", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 7 sites"}]}

## assistant — 38f8406d-20c2-4fab-a3b4-bd590d3d57c6

{"content": "Pensou por 6s", "content_type": "reasoning_recap"}

## assistant — 8a6b5660-254c-4787-b8da-aa96954790ff

Acho que encontramos um caminho muito interessante para o ISA-1! 😄

**Minha recomendação é manter a tela pequena com RCA e aproveitar a arquitetura do Gigatron como referência para simplificar nossa CPU.** Não precisamos comprar um monitor VGA para ter um computador colorido.

E tem uma possibilidade melhor do que as duas que estávamos considerando: **usar vídeo composto colorido com uma CPU inspirada no Gigatron**, desde que a complexidade do circuito de cores se justifique.

## 1. Existem monitores VGA pequenos e baratos?

Existem monitores VGA de 4,3 a 5 polegadas, mas são bem menos comuns que os monitores automotivos RCA.

Na pesquisa de produtos disponíveis no Brasil, encontrei principalmente telas RCA de 4,3 polegadas, como estas:

<row gap={3} align="start">
  <AsyncImage ref="turn899594product1" maxWidth="124px" aspectRatio="4:3"/>
  <box flex="1" gap={1}>
    **{turn899594product1.title}**

    <title size="lg" color="default">{turn899594product1.displayed_price}</title>
    <text color="secondary" size="xs">{turn899594product1.merchant}</text>
  </box>
</row>
<row gap={3} align="start">
  <AsyncImage ref="turn899594product12" maxWidth="124px" aspectRatio="4:3"/>
  <box flex="1" gap={1}>
    **{turn899594product12.title}**

    <title size="lg" color="default">{turn899594product12.displayed_price}</title>
    <text color="secondary" size="xs">{turn899594product12.merchant}</text>
  </box>
</row>

Não encontrei uma oferta brasileira de monitor VGA pequeno que fosse tão convincente quanto essas opções RCA. Isso não significa que não exista, mas **não vale mudar o ISA-1 para VGA apenas por causa do Gigatron**.

Há também um detalhe: esses monitores automotivos geralmente exigem alimentação de 12 V, enquanto nosso computador será alimentado internamente por 5 V. Precisaremos prever isso na alimentação do conjunto.

## 2. O que vamos aproveitar do Gigatron?

A documentação oficial confirma que ele tem CPU de 8 bits, clock de 6,25 MHz, 32 KB de RAM, ROM de 64K palavras de 16 bits e vídeo VGA de 64 cores. Sua CPU utiliza apenas 17 instruções nativas. <Cite ref="turn899594search0"/>

O mais interessante não é copiar essas especificações, mas entender **por que ele precisa de tão poucos componentes**.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Nova direção de estudo para o ISA-1</text>
  <svg viewBox="0 0 330 194" width="100%">
    <g fill="currentColor" textAnchor="middle" fontSize="11">
      <rect x="89" y="4" width="152" height="34" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".10"/>
      <text x="165" y="18" fontWeight="600">CPU 8 bits 74HC/HCT</text>
      <text x="165" y="30" fontSize="9">Inspirada no Gigatron</text>
      <path d="M165 38 V54 H72 V67 M165 54 H258 V67" stroke="#94a3b8" fill="none" strokeWidth="1.5"/>
      <rect x="4" y="67" width="137" height="37" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".10"/>
      <text x="72" y="82" fontWeight="600">ROM / Firmware</text>
      <text x="72" y="95" fontSize="9">Boot e interpretador</text>
      <rect x="189" y="67" width="137" height="37" rx="6" stroke="#60a5fa" fill="#2563eb" fillOpacity=".10"/>
      <text x="258" y="82" fontWeight="600">RAM</text>
      <text x="258" y="95" fontSize="9">Programas e dados</text>
      <path d="M165 54 V117" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="83" y="117" width="164" height="34" rx="6" stroke="#4ade80" fill="#16a34a" fillOpacity=".10"/>
      <text x="165" y="131" fontWeight="600">Controlador de vídeo</text>
      <text x="165" y="143" fontSize="9">Projeto a comparar e validar</text>
      <path d="M165 151 V164" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="99" y="164" width="132" height="26" rx="6" stroke="#f59e0b" fill="#f59e0b" fillOpacity=".10"/>
      <text x="165" y="181" fontWeight="600">RCA — tela 4,3"</text>
    </g>
  </svg>
  <caption>Arquitetura candidata para estudo, não esquema elétrico validado.</caption>
</box>

Minha proposta é revisar quatro decisões:

| Parte | Decisão |
|---|---|
| CPU | Comparar nossa CPU microprogramada com uma CPU de controle simplificado, como a do Gigatron |
| ROM | Manter firmware de inicialização e programas de sistema |
| RAM | Preservar o objetivo de 32 KB |
| Vídeo | Manter RCA e estudar monocromático versus colorido |

Existe uma diferença importante: no Gigatron, a CPU gera o vídeo executando instruções. Isso economiza hardware, mas consome muito tempo de processamento. A própria documentação explica essa troca. <Cite ref="turn899594search1"/>

Portanto, **não vou assumir que copiar a geração de vídeo do Gigatron seja a melhor solução para nós**.

## 3. E se o ISA-1 tivesse cores no RCA?

<grid columns={2} gap={3}>
  <grid-item>
    <AsyncImage query="small 4.3 inch automotive LCD composite video monitor showing black and white retro pixel graphics" aspectRatio="4:3"/>
    **Opção A — Monocromático**

    Circuito de saída mais simples. Mantém a resolução gráfica de 256×192 que planejamos.
  </grid-item>
  <grid-item>
    <AsyncImage query="small 4.3 inch automotive LCD screen showing colorful 8 bit retro pixel art game" aspectRatio="4:3"/>
    **Opção B — Colorido**

    Mais possibilidades para jogos e interfaces, mas exige codificação de cor compatível com vídeo composto.
  </grid-item>
</grid>

A tela RCA pode mostrar cores — o que determina isso é o sinal que o ISA-1 produz.

O desafio é que vídeo composto colorido não funciona como VGA. Precisamos codificar corretamente a crominância, e isso pode exigir circuitos adicionais ou um codificador dedicado.

Não quero que a busca por cores comprometa nosso objetivo de construir a CPU com lógica discreta e manter o projeto acessível.

## 4. Registro das decisões — ISA-1 Rev. 1.1

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **D23 — Tela compacta RCA mantida**
  </row>
  <text color="secondary" size="sm">Não exigir monitor VGA ou compra de uma tela maior.</text>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **D24 — Gigatron adotado como referência principal de otimização**
  </row>
  <text color="secondary" size="sm">Estudar sua CPU, ALU, barramentos, decodificação de instruções e firmware.</text>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **D25 — Computador completo continua sendo o objetivo**
  </row>
  <text color="secondary" size="sm">Teclado, vídeo, execução de programas e armazenamento permanente continuam no escopo.</text>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="clock-3" color="secondary"/>
    **D26 — Vídeo colorido em avaliação**
  </row>
  <text color="secondary" size="sm">Comparar complexidade, custo, memória e desempenho antes de escolher.</text>
</box>

Temos uma vantagem adicional: os criadores do Gigatron disponibilizaram os esquemáticos, arquivos de placa e software. Podemos estudar um projeto real e comprovado, em vez de depender apenas de hipóteses. <Cite ref="turn899594search3"/>

<Link url="https://gigatronttl.eu/posts/482.html" title="Arquitetura e esquemáticos oficiais do Gigatron"/>

**Minha escolha por enquanto:** manter a tela RCA de 4,3", revisar profundamente a CPU usando o Gigatron como referência e investigar vídeo colorido sem assumir que ele será obrigatório.

A meta continua sendo um ISA-1 completo, que ligue, apresente sua interface, aceite programas pelo teclado e funcione sem depender de um computador moderno no uso cotidiano.

E, nesta etapa, não precisamos que você decida mais nada.

## user — bbb211fc-462f-4670-aa9b-c3f7b0cf47b4

Legal, vamos seguir assim então 
Teclado usando as 4 matrizes
CPU revisada, como menos CIs agora?
RCA mesmo, mas quero pensar no vídeo colorido, agora que vamos revisar a CPU pra usar menos CIs, podemos repensar aqui
Ram ROM EPROM 

## assistant — c3b9d18c-3134-41f5-a314-d2245799c6dc

{"content_type": "thoughts", "source_analysis_msg_id": "b9a7605e-44b7-4503-bbce-f732a9f429d0", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Registrou decisões e riscos do ISA-1"}]}

## assistant — 521e242a-94ab-47f7-b9fc-948326ae2efe

{"content": "Pensou por 27s", "content_type": "reasoning_recap"}

## assistant — 8987dc66-7ae6-4661-bbdd-220dbb97e07d

Perfeito! 😄 Agora temos uma direção bem definida para o **ISA-1**: um computador de 8 bits completo, inspirado na eficiência do Gigatron, mas com personalidade própria, teclado de 64 teclas e saída RCA.

E sim, **acho que podemos reduzir bastante a quantidade de CIs da CPU**, principalmente se abandonarmos parte da arquitetura microprogramada anterior.

A mudança mais promissora é substituir os vários registradores de 16 bits e as EEPROMs de microcódigo por uma CPU com conjunto pequeno de instruções e controle por lógica combinacional, inspirada no Gigatron.

## ISA-1 — Nova arquitetura candidata

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 295" width="100%">
    <g fontSize="11" fill="currentColor" textAnchor="middle">
      <rect x="92" y="5" width="156" height="44" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="170" y="22" fontWeight="600">CPU ISA-1 — 8 bits</text>
      <text x="170" y="37" fontSize="9">Controle simplificado 74HC/HCT</text>
      <path d="M170 49 V69 M62 69 H278 M62 69 V83 M170 69 V83 M278 69 V83" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="4" y="83" width="112" height="48" rx="6" fill="#2563eb" fillOpacity=".10" stroke="#60a5fa"/>
      <text x="60" y="101" fontWeight="600">ROM / EPROM</text>
      <text x="60" y="115" fontSize="9">Firmware e boot</text>
      <rect x="122" y="83" width="96" height="48" rx="6" fill="#16a34a" fillOpacity=".10" stroke="#4ade80"/>
      <text x="170" y="101" fontWeight="600">SRAM</text>
      <text x="170" y="115" fontSize="9">32 KB</text>
      <rect x="224" y="83" width="112" height="48" rx="6" fill="#f59e0b" fillOpacity=".10" stroke="#f59e0b"/>
      <text x="280" y="101" fontWeight="600">EEPROM</text>
      <text x="280" y="115" fontSize="9">Salvar programas</text>
      <path d="M170 131 V151 M66 151 H274 M66 151 V166 M274 151 V166" stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      <rect x="4" y="166" width="126" height="52" rx="6" fill="#64748b" fillOpacity=".10" stroke="#94a3b8"/>
      <text x="67" y="185" fontWeight="600">Teclado 4×16</text>
      <text x="67" y="201" fontSize="9">4 matrizes 4×4</text>
      <rect x="204" y="166" width="132" height="52" rx="6" fill="#16a34a" fillOpacity=".10" stroke="#4ade80"/>
      <text x="270" y="185" fontWeight="600">Vídeo colorido?</text>
      <text x="270" y="201" fontSize="9">Controlador a validar</text>
      <path d="M270 218 V241" stroke="#94a3b8" strokeWidth="1.5"/>
      <rect x="204" y="241" width="132" height="40" rx="6" fill="#eab308" fillOpacity=".12" stroke="#eab308"/>
      <text x="270" y="258" fontWeight="600">RCA composto</text>
      <text x="270" y="272" fontSize="9">Tela compacta 4,3"</text>
    </g>
  </svg>
  <caption>Organização funcional proposta. Ainda não representa a quantidade definitiva de CIs nem conexões elétricas validadas.</caption>
</box>

## 1. CPU com menos CIs

Eu adotaria a filosofia do Gigatron, mas não copiaria sua CPU integralmente.

| Característica | Antes | Agora, em estudo |
|---|---|---|
| Controle | EEPROMs de microcódigo | Lógica combinacional |
| Registradores | A, B, X, SP, PC, MAR, MDR, IR | Conjunto mínimo |
| Barramento de endereços | 16 bits | 16 bits, se necessário |
| Instruções | Conjunto relativamente amplo | Poucas instruções nativas |
| Recursos avançados | Implementados em hardware | Parte implementada em firmware |
| Quantidade de CIs | Elevada, não fechada | Potencialmente muito menor |

**Minha escolha é priorizar uma CPU simples e um firmware mais inteligente.**

Não vou prometer que teremos os mesmos 34–36 CIs de lógica do Gigatron, porque nosso teclado, armazenamento e saída RCA são diferentes. A contagem real depende de fechar os esquemas.

## 2. RAM, ROM, EPROM e EEPROM

Aqui eu faria uma separação bem clara:

| Memória | Função no ISA-1 | Comportamento |
|---|---|---|
| **SRAM** | Executar programas e guardar variáveis | Perde conteúdo ao desligar |
| **EPROM ou EEPROM de firmware** | Inicialização e sistema operacional básico | Mantém conteúdo desligada |
| **EEPROM de dados** | Salvar programas pelo teclado | Mantém conteúdo e permite regravação elétrica |

A EPROM tradicional, como a 27C256, normalmente precisa de luz ultravioleta para ser apagada e de um gravador para ser programada.

Já a EEPROM, como a AT28C256, pode ser regravada eletricamente, inclusive pelo próprio ISA-1 se construirmos a interface adequada.

**Minha preferência:** EEPROM para firmware e outra EEPROM para salvar programas. Entretanto, se adotarmos uma ROM de instruções de 16 bits como a do Gigatron, precisaremos rever a organização e escolher os chips apropriados. Não devemos comprar memórias antes dessa decisão.

## 3. E o vídeo RCA colorido?

Aqui eu investigaria uma solução que pode preservar a simplicidade da CPU.

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="palette" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Gerar cores digitais com lógica simples**

      Usar uma representação de cor compacta, como 2 bits por canal RGB, totalizando 64 cores, semelhante à do Gigatron.
    </box>
  </row>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="circuit-board" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Converter RGB para vídeo composto**

      Investigar um codificador dedicado RGB-para-NTSC/PAL. Ele cuidaria da codificação de cor, mas ainda exigiria clocks e sincronismos corretos. Precisamos verificar disponibilidade e custo.
    </box>
  </row>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="tv" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Enviar para a tela RCA**

      A saída final continuaria sendo um único conector amarelo, compatível com o padrão de vídeo aceito pelo monitor.
    </box>
  </row>
</box>

Isso pode ser mais simples do que construir um codificador de cor inteiramente com 74HC, mas não significa que teremos vídeo colorido por apenas um CI adicional.

Além disso, a decisão entre **vídeo produzido pela CPU** e **controlador independente** ainda precisa de uma comparação quantitativa. A primeira opção pode economizar componentes; a segunda facilita o funcionamento simultâneo de programas e vídeo.

## 4. Teclado: decisão mantida

Vamos continuar com quatro matrizes de 4×4, formando um teclado lógico de 4 linhas e 16 colunas.

Isso fornece 64 teclas, suficientes para letras, números, símbolos e comandos.

A CPU fará a leitura por varredura. Vamos preservar a capacidade de detectar combinações como `SHIFT + A` e `CTRL + C`, mas não prometer combinações arbitrárias de três ou mais teclas sem diodos individuais.

## 5. Registro desta revisão

Criei um arquivo com as decisões, alternativas e riscos, incluindo a mudança de CPU e a avaliação do vídeo colorido.

<row align="center" gap={3}>
  <icon name="file-text" size="xl" color="secondary"/>
  <box flex="1" gap={1}>
    **[ISA-1 — Registro de decisões Rev. 1.1](sandbox:/mnt/data/isa1/ISA-1_REV11_REGISTRO_DECISOES.md)**

    <text color="secondary" size="xs">Decisões D27–D33 e questões que ainda precisam de validação.</text>
  </box>
</row>

Minha prioridade agora é comparar duas implementações completas: uma mais próxima do Gigatron, com ROM de instruções de 16 bits e vídeo produzido pela CPU; outra com CPU simplificada e controlador gráfico independente.

Só depois dessa comparação vamos estabelecer a quantidade de CIs, a organização definitiva das memórias e a estratégia de vídeo colorido.

**O objetivo está mantido: ISA-1 completo, com 64 teclas, tela RCA compacta, programas próprios, armazenamento permanente e o menor número de CIs que conseguirmos sem sacrificar a confiabilidade.**

## user — bbb215cd-14dc-4d03-8503-a6a673f87653

O que a gente perde como essa alteração de CPU baseada no gigatron? 

## assistant — f49746d5-5098-412f-a916-5a44e4ec4cd1

{"content_type": "thoughts", "source_analysis_msg_id": "848eba6d-0bec-4be7-aa29-82873c29fa72", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — 96a662a7-bd63-41fd-8de9-cda3684803cc

{"content": "Pensou por 4s", "content_type": "reasoning_recap"}

## assistant — 96f37989-27e8-4b1f-a176-db90b874ea08

A principal coisa que perderíamos é **capacidade de hardware na CPU em troca de simplicidade e menos circuitos integrados**.

Mas existe uma diferença importante entre *ter menos instruções* e *ser menos capaz*.

Uma CPU inspirada no Gigatron pode continuar executando jogos, BASIC, gráficos e programas complexos. A diferença é que várias operações que nossa CPU original faria diretamente em hardware passariam a exigir mais instruções ou rotinas de software.

## Comparação das duas arquiteturas

| Recurso | ISA-1 original | CPU inspirada no Gigatron |
|---|---|---|
| Registradores | A, B, X, SP, PC e auxiliares | Conjunto menor |
| Instruções | Mais completas | Mais simples |
| Multiplicação | Por software | Por software |
| Operações de 16 bits | Mais apoio em hardware | Várias operações de 8 bits |
| Pilha e sub-rotinas | Suporte direto planejado | Podem exigir software |
| Acesso à memória | Endereçamento de 16 bits | Depende do projeto escolhido |
| Velocidade por operação complexa | Potencialmente melhor | Pode exigir mais instruções |
| Quantidade de CIs | Maior | Potencialmente menor |
| Facilidade de construir | Mais difícil | Potencialmente mais fácil |

Há uma ressalva: a CPU original ainda não teve seu circuito físico finalizado. Portanto, a vantagem de desempenho é uma expectativa arquitetural, não um resultado medido.

## 1. O que realmente perderíamos?

O Gigatron original abre mão de vários recursos que são comuns em CPUs tradicionais: registrador de flags, pilha em hardware, instruções de deslocamento e execução direta de programas nativos na RAM. Essas limitações são contornadas por software. <Cite refs={["turn914084search1","turn914084search3"]}/>

Para o ISA-1, as consequências seriam:

**Programas mais lentos em certas operações.** Por exemplo, somar dois números de 16 bits pode exigir várias instruções de 8 bits e tratamento manual do transporte (*carry*).

**Maior dependência do firmware.** Chamadas de funções, manipulação de pilha e operações mais sofisticadas precisam ser implementadas por rotinas ou por uma CPU virtual.

**Menor liberdade para executar código nativo.** No Gigatron, o código nativo é executado diretamente da ROM; os programas carregados na RAM são interpretados pela vCPU. <Cite ref="turn914084search2"/>

**Maior dificuldade para programar diretamente em Assembly nativo.** O conjunto de instruções é pequeno, mas algumas tarefas simples em uma CPU tradicional exigem sequências maiores.

## 2. O que não precisamos perder

É aqui que podemos melhorar a proposta.

Não somos obrigados a copiar todas as limitações do Gigatron. Podemos usar suas soluções para economizar CIs e preservar os recursos mais importantes para o ISA-1.

| Recurso | Minha decisão |
|---|---|
| CPU física de 8 bits | Manter |
| RAM de 32 KB | Manter |
| ROM com firmware | Manter |
| Teclado de 64 teclas | Manter |
| Vídeo RCA, possivelmente colorido | Manter |
| BASIC e monitor de comandos | Manter como objetivos |
| Programas salvos sem PC | Manter |
| Pilha em hardware | Avaliar custo antes de eliminar |
| Flags de carry e zero | Avaliar preservação |
| Programas nativos executados da RAM | Não exigir inicialmente |

A decisão mais importante é **não remover recursos úteis só para economizar um ou dois CIs**.

Por exemplo, manter um carry acessível ao software pode simplificar bastante a aritmética de 16 bits. Se o custo elétrico for pequeno, prefiro preservá-lo a reproduzir exatamente a arquitetura do Gigatron.

## 3. A diferença de desempenho pode ser grande?

Sim, principalmente se adotarmos uma CPU virtual.

O Gigatron executa código nativo diretamente da ROM, enquanto a vCPU interpreta programas armazenados na RAM. Essa interpretação custa ciclos adicionais. Além disso, a geração de vídeo consome parte substancial do tempo da CPU. <Cite refs={["turn914084search2","turn914084search7"]}/>

Mas isso não significa que nosso ISA-1 necessariamente ficará mais lento.

Se conseguirmos uma CPU física simples com clock maior e um controlador de vídeo independente, poderemos recuperar parte desse desempenho.

O problema é que essa combinação talvez não economize tantos CIs quanto o Gigatron original.

## 4. Minha escolha para o ISA-1

Eu adotaria uma **arquitetura híbrida inspirada no Gigatron**, com três prioridades:

1. **CPU mínima, mas prática:** poucos registradores e instruções, preservando operações que custariam muito em software.
2. **Firmware poderoso:** BASIC, editor simples, rotinas gráficas e monitor de memória.
3. **Vídeo RCA independente, preferencialmente colorido se a implementação se mostrar viável:** para não obrigar a CPU a gastar a maior parte do tempo gerando o sinal.

Isso mantém a simplicidade como objetivo sem comprometer desnecessariamente a experiência de uso.

### O que eu não faria

Não copiaria integralmente a CPU do Gigatron e depois tentaria encaixar nosso sistema nela. O projeto original foi otimizado para gerar VGA por software; nosso objetivo inclui RCA, quatro matrizes de teclado e armazenamento persistente.

A arquitetura precisa ser otimizada para essas necessidades.

**Resumindo:** perderíamos principalmente desempenho em operações complexas, instruções convenientes e parte da facilidade de programação em baixo nível. Não precisaríamos perder BASIC, jogos, gráficos, teclado ou independência de um PC moderno.

Minha recomendação é seguir com a CPU simplificada, mas **não eliminar ainda o carry, a pilha ou os recursos de endereçamento sem medir o custo em CIs e em desempenho**. Essa é a comparação que precisa orientar o desenho definitivo.

## user — bbb2175b-cd13-485d-b40c-fa2cb0b93756

Não quero capar nosso projeto
Vamos usar os pontos bons do gigatron e nos inspirar, por exemplo vimos e tivemos a ideia do vídeo colorido
Talvez alguns cortes de CI, um tenho de frequência, mas quero nossa identidade

## assistant — aa2abd0a-3a82-4ffe-b618-a5bb79563eea

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 88292e60-57fb-465d-a57c-a9bb0e628592

**Agora sim! Essa é a direção que eu considero ideal para o ISA-1.** 😄

O Gigatron nos mostrou possibilidades que ainda não tínhamos explorado, mas não precisamos transformar o ISA-1 em uma cópia dele.

Quero que nosso computador tenha uma CPU própria, com recursos completos, seja fácil de programar e consiga executar aplicações interessantes. Se conseguirmos reduzir a quantidade de CIs sem sacrificar isso, ótimo. Caso contrário, prefiro alguns componentes a mais.

## Nova filosofia do ISA-1

**Não vamos simplificar o computador. Vamos simplificar a maneira de construí-lo.**

Isso muda nossas prioridades:

1. **Funcionalidade primeiro.** Não remover pilha, flags ou endereçamento útil apenas para economizar chips.
2. **Otimização inteligente.** Aproveitar ideias do Gigatron para melhorar a ALU, o controle e a organização dos barramentos.
3. **Desempenho real.** Buscar um clock maior, mas definido pelos tempos de propagação e acesso das memórias, não por uma frequência arbitrária.
4. **Vídeo colorido RCA.** Investigar uma solução compatível com nossa tela compacta, preservando a independência da CPU.
5. **Identidade própria.** O ISA-1 terá seu próprio conjunto de instruções, firmware, teclado e arquitetura de expansão.

## O que vamos preservar

| Componente | Direção |
|---|---|
| CPU de 8 bits | Arquitetura própria, com instruções práticas |
| Endereçamento de 16 bits | Manter |
| Flags Zero e Carry | Manter |
| Pilha e CALL/RET | Manter |
| RAM de 32 KB | Manter como objetivo |
| ROM/EEPROM | Firmware de inicialização |
| EEPROM de dados | Salvar programas sem PC |
| Teclado | Quatro matrizes 4×4, total de 64 teclas |
| Vídeo | RCA compacto, agora com cor como objetivo de estudo |
| Clock | Otimizar conforme a capacidade real do hardware |

### Onde podemos ganhar com o Gigatron

Acredito que existem três oportunidades especialmente boas.

**Na CPU:** estudar como reduzir a quantidade de multiplexadores, buffers e lógica de decodificação sem eliminar registradores ou instruções importantes.

**Na frequência:** procurar uma organização que permita clocks maiores. Uma CPU de controle simplificado pode ter vantagens, mas precisamos comparar seu caminho crítico com o de uma CPU microprogramada antes de escolher.

**No vídeo:** investigar como gerar uma paleta compacta e convertê-la para vídeo composto colorido. Isso pode transformar bastante a experiência do ISA-1, especialmente em jogos.

Também manteria uma separação importante: o vídeo deve continuar funcionando quando a CPU estiver ocupada com um programa. É uma característica que considero valiosa para a nossa arquitetura.

## Decisões registradas — Rev. 1.2

Documentei essa mudança de direção, incluindo o que fica preservado, o que podemos otimizar e quais decisões ainda dependem de validação.

<row align="center" gap={3}>
  <icon name="file-text" size="xl" color="secondary"/>
  <box flex="1" gap={1}>
    **[ISA-1 — Diretrizes de arquitetura Rev. 1.2](sandbox:/mnt/data/isa1/ISA-1_REV12_DIRETRIZES.md)**
    <text color="secondary" size="xs">Decisões D34–D39 e critérios de validação.</text>
  </box>
</row>

Minha recomendação é manter duas alternativas de implementação da CPU em estudo, mas **uma única especificação funcional do ISA-1**. Assim podemos comparar circuitos sem ficar mudando o computador que queremos construir.

E gosto especialmente de uma ideia: enquanto o Gigatron foi projetado em torno de uma CPU que também gera vídeo, o ISA-1 pode ter uma CPU mais completa, um sistema gráfico próprio e uma interface de programação integrada.

**Nossa identidade será essa: um computador pessoal de 8 bits construído por nós, inspirado nos clássicos, mas sem ser uma reprodução de nenhum deles.**

Não precisamos perseguir o recorde de menor número de CIs. Precisamos construir o melhor ISA-1 que conseguirmos, com uma arquitetura que faça sentido e que possamos realmente fabricar.

## user — bbb216b9-71ad-48a6-a0f0-3dfaf4c49805

Perfeito, então vamos lá! 
Quero construir por partes
Podemos fazer um sanduíche de placas? Ou nem precisaria? 
Estou pensando em, quando tivermos o físico definido, encomendar as placas da China
E soldar tudo em casa
Por isso temos que ter um Hardware perfeito 

## assistant — 3c166772-cc63-4363-972a-cb854e51b800

{"content": "Pensou por 4s", "content_type": "reasoning_recap"}

## assistant — 60bee6a5-6a61-439d-9b82-ce534747831e

**Sim! E acho que um sanduíche de placas é uma excelente solução para o ISA-1**, principalmente porque você pretende encomendar as PCBs da China e soldar os componentes em casa. 😄

Mas eu faria uma distinção: **projetaria o ISA-1 como um computador modular, sem obrigatoriamente empilhar todas as placas.**

Isso nos permitiria construir e testar cada módulo separadamente, substituir uma placa defeituosa e evoluir o projeto sem refazer tudo.

E concordo com sua preocupação: antes de gastar com fabricação, precisamos ter esquemáticos completos, componentes definidos, simulações e uma revisão rigorosa das conexões.

## Como imagino o ISA-1 fisicamente

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="retro 8 bit homebrew computer modular stack PCB through hole DIP chips standoffs green circuit boards" aspectRatio="5:4" maxWidth="160px"/>
    <box flex="1" gap={1}>
      **Sanduíche de placas**

      Placas empilhadas usando espaçadores metálicos ou de nylon e conectores entre elas. Compacto e com aparência de computador artesanal.
    </box>
  </row>
  <row align="start" gap={3}>
    <AsyncImage query="modular retro computer backplane PCB expansion cards through hole DIP integrated circuits" aspectRatio="5:4" maxWidth="160px"/>
    <box flex="1" gap={1}>
      **Backplane com placas de expansão**

      Uma placa principal distribui alimentação e sinais para módulos separados. Facilita manutenção e testes, mas ocupa mais espaço e exige cuidado com a integridade dos sinais.
    </box>
  </row>
</box>

Para nosso caso, eu escolheria uma **arquitetura híbrida**: uma placa principal com CPU e memória, mais módulos conectados para vídeo, teclado e armazenamento.

Assim, podemos construir o computador por etapas e, no final, acomodá-lo em um gabinete compacto.

## Minha proposta: ISA-1 com três placas

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 250" width="100%">
    <g strokeWidth="1.5" strokeLinejoin="round">
      {#each [{y:22,c:"#7aa58a",name:"PLACA 3 — VÍDEO",sub:"VRAM • sincronismo • RCA colorido"},{y:98,c:"#6b9e87",name:"PLACA 2 — SISTEMA",sub:"RAM • ROM • EEPROM • I/O"},{y:174,c:"#55856d",name:"PLACA 1 — CPU",sub:"ALU • registradores • controle"}] as p}
        <path d={`M28 ${p.y+18} L268 ${p.y+18} L314 ${p.y} L74 ${p.y} Z`} fill={p.c} stroke="#365b47"/>
        <path d={`M28 ${p.y+18} V${p.y+45} L268 ${p.y+45} V${p.y+18} Z`} fill={p.c} fillOpacity=".65" stroke="#365b47"/>
        <path d={`M268 ${p.y+18} L314 ${p.y} V${p.y+27} L268 ${p.y+45} Z`} fill={p.c} fillOpacity=".8" stroke="#365b47"/>
        {#each Array.from({length:6},(_,i)=>i) as i}
          <rect x={70+i*29} y={p.y+4} width="19" height="10" rx="1" fill="#263a33" stroke="#b4c6b6" strokeWidth=".4"/>
        {/each}
        <text x="145" y={p.y+30} textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="600">{p.name}</text>
        <text x="145" y={p.y+40} textAnchor="middle" fill="#ffffff" fontSize="8">{p.sub}</text>
      {/each}
      <g stroke="#a7a7a7" strokeWidth="5" strokeLinecap="round">
        <path d="M48 68 V98 M290 54 V84 M48 144 V174 M290 130 V160"/>
      </g>
    </g>
  </svg>
  <caption>Conceito de organização mecânica, não desenho de fabricação.</caption>
</box>

| Placa | Componentes | Teste individual |
|---|---|---|
| **1 — CPU** | Registradores, ALU, controle, clock e diagnóstico | Executar microoperações e instruções |
| **2 — Sistema** | ROM, RAM, EEPROM, decodificação e interfaces | Inicializar e executar programas |
| **3 — Vídeo** | VRAM, temporização, circuito de cor e RCA | Gerar imagem estável |

O teclado de quatro matrizes 4×4 ficaria em uma placa frontal própria, ligada por cabo. Não faz sentido colocá-lo dentro do sanduíche.

### Um cuidado importante

Não quero que o projeto fique dependente de conectores empilhados muito longos. Barramentos de 8 e 16 bits, sinais de clock e linhas de controle podem sofrer com capacitância, ruído e reflexões.

Por isso, **três placas são uma proposta de organização, não uma quantidade definitivamente aprovada**. Se a análise elétrica mostrar que duas placas funcionam melhor, usaremos duas.

## Componentes pensados para soldagem em casa

<grid columns={2} gap={3}>
  <grid-item>
    <AsyncImage query="DIP through hole 74HC logic integrated circuits mounted in precision IC sockets PCB close up" aspectRatio="5:4"/>
    **CIs DIP e soquetes**

    Preferência por componentes de furo passante, fáceis de soldar, inspecionar e substituir.
  </grid-item>
  <grid-item>
    <AsyncImage query="through hole PCB soldering electronics workbench solder joints magnifying glass" aspectRatio="5:4"/>
    **Montagem manual**

    Trilhas, espaçamentos e identificação dos componentes pensados para soldagem doméstica.
  </grid-item>
</grid>

Também adotaria estas regras:

- Resistores e capacitores convencionais, sempre que viável.
- Capacitor de desacoplamento próximo de cada CI.
- Planos de terra contínuos, preferencialmente em PCBs de duas camadas.
- Pontos de teste para clock, reset, barramentos e sinais críticos.
- Conectores polarizados ou mecanicamente protegidos contra inversão.
- Identificação clara da orientação de todos os CIs e conectores.

Para uma placa com dezenas de CIs, soquetes podem facilitar substituições, embora acrescentem contatos e possíveis problemas de conexão. Vamos decidir onde são realmente vantajosos.

## Como garantir que as placas estejam corretas?

Não existe uma maneira honesta de garantir um hardware 100% perfeito antes de construí-lo. Até projetos profissionais passam por revisões de placa.

Mas podemos reduzir muito o risco seguindo critérios objetivos.

<box gap={2}>
  <list marker="number" connector="solid" gap={2}>
    <list-item>
      **Esquemático elétrico completo**

      Cada CI terá referência, alimentação, pinagem e conexões conferidas com seu datasheet.
    </list-item>
    <list-item>
      **Simulação da CPU e das memórias**

      Comparar o comportamento dos circuitos com nosso emulador, inclusive nos casos-limite.
    </list-item>
    <list-item>
      **Análise de temporização**

      Verificar atrasos dos 74HC, tempos das SRAMs, sinais de escrita, clock e conflitos de barramento.
    </list-item>
    <list-item>
      **Verificação das interfaces entre placas**

      Conferir todos os pinos dos conectores, alimentação, terra, sentido dos sinais e estados durante reset.
    </list-item>
    <list-item>
      **Projeto das PCBs no KiCad**

      Executar verificações elétricas (ERC) e de layout (DRC), conferir footprints e gerar arquivos de fabricação.
    </list-item>
    <list-item>
      **Protótipo e testes reais**

      Encomendar inicialmente poucas placas, montar progressivamente e medir os sinais antes de fabricar mais unidades.
    </list-item>
  </list>
</box>

## Uma decisão que considero especialmente importante

**Não vamos fazer três placas grandes e encomendar todas antes de validar os circuitos críticos.**

Vamos desenvolver o projeto completo, incluindo a integração entre módulos, mas liberar a fabricação por etapas. Assim, caso encontremos um problema na CPU, não teremos desperdiçado a fabricação do restante do computador.

E há outra vantagem: se decidirmos melhorar o vídeo colorido posteriormente, poderemos modificar apenas a placa de vídeo, desde que a interface já tenha sido definida corretamente.

## Decisões de projeto — Rev. 1.3

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Construção modular e compacta**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **PCBs fabricadas profissionalmente, soldagem em casa**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Prioridade para componentes DIP e furo passante**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Teclado frontal com quatro matrizes 4×4**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Vídeo RCA colorido como objetivo, sujeito à validação**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Fabricação somente após revisão técnica**
  </row>
</box>

**Minha escolha é desenvolver o ISA-1 como um computador modular de placas empilháveis, com o menor número de interconexões possível.** O projeto físico será pensado desde o começo para montagem manual e manutenção.

E eu acrescentaria uma exigência ao nosso processo: antes de enviar qualquer PCB para fabricação, teremos uma tabela de conexões que permita conferir cada sinal do circuito contra o esquemático e os conectores.

Quero que, quando as placas chegarem, nossa tarefa seja principalmente soldar, montar e testar — não descobrir erros básicos de projeto.

## user — bbb21948-d62a-4944-be40-984c1488bf5b

Uma dúvida, 3 placas uma sobre a outra igual módulos de Arduino uno ou então conectores igual que a ram ou placa de vídeo em PC moderno? 

## assistant — c9178a97-c4aa-4172-918a-8af4de82a124

Exatamente! 😄 São duas formas diferentes de montar o ISA-1, e ambas funcionam.

A primeira é como os **shields do Arduino Uno**, com placas empilhadas horizontalmente. A segunda é como as **placas de expansão de um PC**, encaixadas verticalmente em uma placa-mãe (*backplane*).

## Opção 1 — Sanduíche, como Arduino Uno

<AsyncImageGroup query={["Arduino Uno with multiple stacked expansion shields side view","stacked electronics PCB boards standoffs pin header connectors"]} aspectRatio="5:3"/>

As três placas ficariam uma acima da outra, conectadas por barras de pinos e conectores fêmea, com espaçadores para dar sustentação.

**Vantagens:** compacto, conexões curtas, menos peças mecânicas e possibilidade de montar tudo dentro de um gabinete pequeno.

**Desvantagens:** acessar uma placa intermediária exige desmontar parte do conjunto, e os conectores precisam ser cuidadosamente posicionados.

## Opção 2 — Placas encaixadas, como um PC

<AsyncImageGroup query={["retro computer backplane with vertical plug in expansion cards","industrial passive backplane PCB vertical daughterboards edge connectors"]} aspectRatio="5:3"/>

Teríamos uma placa-mãe com conectores, onde cada módulo seria encaixado verticalmente.

**Vantagens:** facilita retirar uma placa, medir sinais, substituir módulos e fazer manutenção.

**Desvantagens:** ocupa mais espaço, exige conectores mais caros e pode criar barramentos mais longos, o que aumenta a dificuldade de manter sinais estáveis em frequências elevadas.

## Comparação para nosso ISA-1

| Característica | Sanduíche | Backplane |
|---|---|---|
| Tamanho final | Mais compacto | Maior |
| Custo dos conectores | Geralmente menor | Geralmente maior |
| Soldagem em casa | Fácil | Fácil a moderada |
| Acesso para manutenção | Menor | Melhor |
| Distância entre placas | Curta | Potencialmente maior |
| Aparência | Computador compacto | Computador modular clássico |

## Minha escolha: sanduíche de placas

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 190" width="100%">
    {#each [{y:12,name:"PLACA 3 — VÍDEO",color:"#357a57"},{y:70,name:"PLACA 2 — MEMÓRIA E I/O",color:"#438e66"},{y:128,name:"PLACA 1 — CPU",color:"#2c6b4b"}] as p}
      <rect x="32" y={p.y} width="256" height="35" rx="4" fill={p.color} stroke="#244e38"/>
      <text x="160" y={p.y+22} fill="#ffffff" fontSize="12" fontWeight="600" textAnchor="middle">{p.name}</text>
    {/each}
    {#each [47,273] as x}
      <rect x={x} y="47" width="6" height="23" fill="#a3a3a3"/>
      <rect x={x} y="105" width="6" height="23" fill="#a3a3a3"/>
    {/each}
    {#each [110,200] as x}
      <rect x={x} y="47" width="12" height="23" fill="#64748b"/>
      <rect x={x} y="105" width="12" height="23" fill="#64748b"/>
    {/each}
    <g fontSize="10" fill="currentColor" textAnchor="middle">
      <text x="160" y="181">Conectores elétricos + espaçadores mecânicos</text>
    </g>
  </svg>
  <caption>Vista lateral conceitual, sem escala.</caption>
</box>

Eu escolheria o sanduíche porque você quer um computador pequeno, usando uma tela RCA compacta e soldando tudo em casa.

Mas faria uma melhoria em relação aos shields comuns do Arduino: **usaria conectores de placa a placa com pinagem definida e espaçadores mecânicos**, em vez de depender de barras de pinos compridas para sustentar o conjunto.

Também reservaria pontos de teste acessíveis pelas bordas, para não precisarmos desmontar tudo sempre que quisermos medir um sinal.

**Uma ideia adicional:** podemos desenvolver uma pequena placa de extensão para testes, que permita afastar temporariamente os módulos durante a depuração. Assim teremos a compacidade do sanduíche e uma maneira prática de acessar os circuitos.

Portanto, minha preferência para o ISA-1 é **três placas empilhadas como shields de Arduino, mas projetadas especificamente para funcionar juntas**, com conectores robustos, alinhamento mecânico e sinais cuidadosamente distribuídos.

## user — bbb2196b-c632-4f16-9daf-e28b4815d29d

Outra coisa
Pelo que planejamos precisa mesmo de 3 placas? Ou daria pra fazer tudo numa só? 
Mais uma coisa, eu tenho uma estação de solda, então dá pra fazer tudo de sobrepor se for possível

## assistant — f1e4cffa-c409-4bea-8b78-708cdf4c44aa

{"content": "Pensou por 8s", "content_type": "reasoning_recap"}

## assistant — 0694e394-6c50-459a-a636-34fb90637d8b

**Sim! Podemos fazer o ISA-1 inteiro em uma única placa.** 😄

E agora que você me contou que tem uma estação de solda e consegue trabalhar com componentes SMD (montagem em superfície), minha recomendação muda bastante.

**Eu passaria a considerar uma placa principal única como a melhor opção**, em vez de assumir que precisamos de três placas empilhadas.

As três placas eram uma proposta para facilitar montagem e testes, não uma necessidade da arquitetura.

## 1. Como ficariam as opções?

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="large custom retro 8 bit computer green PCB surface mount logic ICs RAM ROM compact computer motherboard top view" aspectRatio="5:4" maxWidth="152px"/>
    <box flex="1" gap={1}>
      **Uma placa principal**

      CPU, RAM, ROM, EEPROM, circuito de vídeo, alimentação e interfaces na mesma PCB.

      Menos conectores, barramentos mais curtos e montagem final mais simples.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="stacked modular green printed circuit boards multiple layers electronics standoffs" aspectRatio="5:4" maxWidth="152px"/>
    <box flex="1" gap={1}>
      **Três placas empilhadas**

      CPU, memória e vídeo distribuídos em módulos conectados.

      Mais flexibilidade para substituir módulos, mas também mais conectores, pontos de contato e trabalho de integração.
    </box>
  </row>
</box>

Para um computador que queremos construir uma vez e utilizar por muitos anos, a placa única tem vantagens importantes.

## 2. O que muda usando SMD?

Podemos utilizar componentes 74HC em encapsulamentos SOIC, TSSOP ou similares, em vez dos tradicionais DIP.

<grid columns={2} gap={3}>
  <grid-item>
    <AsyncImage query="SOIC 74HC logic integrated circuit surface mount on printed circuit board macro photo" aspectRatio="5:4"/>
    **SOIC**

    Minha preferência para soldagem manual: terminais visíveis, relativamente espaçados e fáceis de inspecionar.
  </grid-item>
  <grid-item>
    <AsyncImage query="TSSOP 74HC surface mount integrated circuit on PCB close up" aspectRatio="5:4"/>
    **TSSOP**

    Mais compacto, mas com terminais menores e maior exigência na soldagem.
  </grid-item>
</grid>

Com SMD, conseguimos reduzir a área ocupada pelos CIs e também encurtar muitas conexões.

Mas existe um detalhe: **SMD não significa automaticamente maior velocidade**. A frequência máxima depende da família lógica, da alimentação, dos tempos de propagação, das cargas e do layout.

Para nosso primeiro ISA-1, eu priorizaria SOIC onde houver disponibilidade. TSSOP seria uma alternativa quando trouxesse vantagem real.

## 3. Minha proposta de placa única

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Distribuição conceitual dos componentes</text>
  <svg viewBox="0 0 340 260" width="100%">
    <rect x="8" y="8" width="324" height="243" rx="9" fill="#245b42" stroke="#163f2e" strokeWidth="2"/>
    {#each [{x:19,y:21,w:194,h:117,label:"CPU ISA-1",sub:"ALU • registradores • controle"},{x:222,y:21,w:99,h:117,label:"MEMÓRIAS",sub:"ROM • RAM"},{x:19,y:147,w:194,h:90,label:"VÍDEO RCA",sub:"VRAM • cor • sincronismo"},{x:222,y:147,w:99,h:90,label:"I/O",sub:"Teclado"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="5" fill="#ffffff" fillOpacity=".06" stroke="#a6d5b4" strokeDasharray="4 3"/>
      <text x={p.x+p.w/2} y={p.y+18} fill="#ffffff" textAnchor="middle" fontSize="11" fontWeight="600">{p.label}</text>
      <text x={p.x+p.w/2} y={p.y+31} fill="#d2e9d7" textAnchor="middle" fontSize="8">{p.sub}</text>
      {#each Array.from({length:p.w>150?10:4},(_,i)=>i) as i}
        <rect x={p.x+10+(i%(p.w>150?5:2))* (p.w>150?36:40)} y={p.y+42+Math.floor(i/(p.w>150?5:2))*29} width="23" height="18" rx="2" fill="#172a25" stroke="#a3b7a7" strokeWidth=".6"/>
      {/each}
    {/each}
    <g fill="#d6b66a">
      {#each [0,1,2,3,4,5,6,7] as i}
        <rect x={28+i*12} y="243" width="7" height="4"/>
      {/each}
    </g>
    <g fill="#ffffff" fontSize="8">
      <text x="32" y="16">ISA-1 MAINBOARD</text>
    </g>
    {#each [[15,15],[325,15],[15,244],[325,244]] as p}
      <circle cx={p[0]} cy={p[1]} r="3" fill="#c9b67a"/>
    {/each}
  </svg>
  <caption>Ilustração da organização funcional, não layout real nem escala definida.</caption>
</box>

Nessa configuração, a PCB teria conectores externos para a tela RCA, o teclado de quatro matrizes, a alimentação e possíveis expansões.

Não definiria ainda suas dimensões. Primeiro precisamos fechar os circuitos e a quantidade de componentes.

## 4. O que ganhamos e perdemos?

| Critério | Placa única | Três placas |
|---|---|---|
| Quantidade de conectores | Menor | Maior |
| Barramentos | Mais curtos em potencial | Passam entre placas |
| Tamanho e espessura final | Geralmente menor | Mais espesso |
| Soldagem SMD | Excelente opção | Também possível |
| Substituir apenas o vídeo | Mais difícil | Fácil |
| Corrigir erros de PCB | Pode exigir refazer tudo | Pode refazer um módulo |
| Montagem final | Mais simples | Mais conexões |

O maior risco da placa única é econômico: se descobrirmos um erro importante depois da fabricação, talvez seja necessário encomendar outra PCB inteira.

Por isso, eu manteria o projeto dividido em **blocos funcionais no esquemático**, mesmo que todos estejam na mesma placa física.

## 5. O que eu decidiria para fabricação

<box gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Uma PCB principal como arquitetura preferencial**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Componentes SMD SOIC sempre que viável**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Teclado de 64 teclas separado da placa principal**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Pontos de teste e diagnóstico em cada subsistema**
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Projeto preparado para montagem e retrabalho manual**
  </row>
</box>

Também consideraria uma PCB de quatro camadas caso o roteamento e a integridade dos sinais justifiquem o custo. Duas camadas podem ser suficientes, mas não quero impor essa restrição antes de conhecer a densidade do circuito.

E manteria alguns recursos para facilitar a depuração: clock lento, reset manual, indicadores de diagnóstico e acesso aos sinais críticos.

### Uma observação importante sobre as memórias

Nem todas as EEPROMs, EPROMs e SRAMs que estamos considerando existem nos mesmos encapsulamentos SMD, especialmente em fornecedores confiáveis.

Vamos escolher primeiro os componentes reais, verificar disponibilidade, tensões, tempos de acesso e procedimentos de gravação. Só depois desenharemos os footprints.

---

**Minha decisão para a próxima revisão do ISA-1: substituir a proposta obrigatória de três placas por uma placa principal única, preferencialmente SMD, com teclado separado.**

Não é necessário sacrificar a arquitetura da CPU nem os gráficos coloridos por causa disso.

E há algo de que gosto nessa solução: teremos um computador inteiro desenvolvido em uma placa própria, com o nome **ISA-1** serigrafado nela, projetado desde o início para ser montado por você.

Antes de mandar fabricar, porém, precisaremos validar o esquema, os componentes, a temporização e o layout. Podemos reduzir muito os riscos, mas a primeira montagem física ainda será uma etapa indispensável de validação.

## user — bbb21b9f-ba5b-421f-809a-5f61530dd21d

Perfeito então
Vamos de uma placa só e SMD soic

## assistant — 1bfbac44-38a0-4802-9f55-397f458c6f2c

Fechado! 😄 **O ISA-1 terá uma única placa principal, com componentes SMD, preferencialmente SOIC.**

Essa passa a ser uma decisão definitiva da arquitetura física.

### Especificação de montagem — ISA-1

| Item | Decisão |
|---|---|
| Placa principal | PCB única |
| Tecnologia | SMD |
| Encapsulamento preferencial | SOIC |
| Soldagem | Manual, com estação de solda |
| Teclado | 64 teclas, em placa separada |
| CPU | 8 bits, lógica discreta 74HC/HCT |
| Memórias | RAM, ROM e EEPROM |
| Vídeo | RCA, com objetivo de cores |
| Fabricação | PCB encomendada da China |
| Camadas | 2 ou 4, conforme validação |

**Uma ressalva:** SOIC será nossa preferência, não uma obrigação absoluta. Algumas memórias e componentes específicos podem exigir outros encapsulamentos. Vamos evitar BGA e outros formatos difíceis de soldar manualmente.

### Próxima etapa: definir o circuito eletrônico

Agora precisamos fechar a arquitetura elétrica antes de começar a desenhar a PCB.

Minha sequência será:

1. Definir a CPU ISA-1 e seu conjunto de instruções.
2. Escolher os CIs reais da ALU, registradores e controle.
3. Definir RAM, ROM e EEPROM, incluindo o mapa de memória.
4. Projetar o circuito de vídeo composto colorido.
5. Integrar teclado, alimentação e interfaces.
6. Validar tudo antes de iniciar o layout no KiCad.

A partir daí poderemos estimar **quantos CIs teremos, o tamanho da placa, a frequência de operação e o custo dos componentes**.

E uma regra importante: **não vamos escolher componentes apenas porque são menores ou mais baratos.** Precisamos de peças disponíveis, confiáveis e compatíveis eletricamente.

O objetivo continua o mesmo: construir um computador de 8 bits completo, com arquitetura própria, que possamos programar e utilizar sem depender de outro computador.

**ISA-1: uma placa, uma CPU nossa e nenhum recurso importante sacrificado só para economizar CIs.**

## user — bbb21150-95c2-4cc7-9acd-b0bd51124ea2

Perfeito! Agora faz assim
Minha sugestão
Vc simular o circuito dos cis, en uma espécie de simulador de eletrônica
Assim dá pra ir testando até ter um Hardware confiável

## assistant — fabbdb6a-6817-406c-aea4-0c3d49650217

{"content_type": "thoughts", "source_analysis_msg_id": "18e82cb2-2411-424a-aba7-8bfe9a24b3d7", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas de simulação e validou exaustivamente uma ALU de 8 bits"}]}

## assistant — d87e844d-665a-4507-bf81-8b0828665a03

{"content": "Pensou por 24s", "content_type": "reasoning_recap"}

## assistant — 1c581e9e-7e92-457a-abc6-c274fd599615

**Concordo totalmente. Essa deve ser uma das etapas centrais do desenvolvimento do ISA-1.** 😄

Em vez de desenharmos uma PCB e torcermos para funcionar, vamos construir primeiro um **protótipo virtual dos circuitos**, testando a CPU, as memórias, o barramento e os periféricos.

E quero fazer isso em três níveis diferentes:

1. **Simulação lógica:** verificar se cada combinação de sinais produz o resultado correto, inclusive flags, instruções e estados de controle.
2. **Simulação temporal:** verificar se os sinais chegam a tempo, se há conflitos no barramento e se os tempos de leitura e escrita são respeitados.
3. **Simulação elétrica:** analisar alimentação, níveis de tensão, cargas e circuitos analógicos, especialmente a saída RCA colorida.

Esses testes se complementam. Um circuito pode estar logicamente correto e ainda falhar fisicamente por problemas de temporização ou alimentação.

**Não precisamos esperar a arquitetura inteira ficar pronta para começar.** Podemos validar cada bloco à medida que o projetamos.

## Já comecei: primeiro teste lógico do ISA-1

Para transformar essa ideia em trabalho concreto, preparei um modelo experimental de uma ALU de 8 bits usando a função de **dois somadores 74HC283 de 4 bits em cascata**.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Primeiro resultado de simulação</text>
  <row align="center" justify="between">
    <box gap={1}>
      <title size="2xl" color="success" tabularNums>196.608</title>
      <text color="secondary" size="xs">Casos lógicos verificados</text>
    </box>
    <badge color="success"><icon name="check" size="xs" inline/> Aprovado</badge>
  </row>
  <divider color="subtle"/>
  <text size="sm">Testei todas as combinações de dois operandos de 8 bits para soma com carry de entrada 0 ou 1 e subtração.</text>
  <text size="sm">As operações produziram os resultados e as flags Carry e Zero esperados em todos os casos.</text>
</box>

Isso **não significa que o circuito físico já esteja validado**. O teste foi executado em um modelo lógico em Python, não em um simulador elétrico com modelos reais dos CIs. Ele demonstra apenas que a organização aritmética estudada funciona matematicamente.

Arquivos gerados:

- <Link url="sandbox:/mnt/data/isa1/ISA-1_REV13_PLANO_SIMULACAO.md" title="Plano de simulação e critérios de aprovação — Rev. 1.3"/>
- <Link url="sandbox:/mnt/data/isa1/isa1_rev13_alu_logic_test.py" title="Código do primeiro teste lógico da ALU"/>

## Quais simuladores vamos utilizar?

Minha proposta é combinar ferramentas, porque nenhuma resolve todos os problemas do nosso computador.

| Ferramenta | Finalidade |
|---|---|
| **Digital / Logisim Evolution** | Montar e visualizar circuitos lógicos |
| **Verilog + simulador HDL** | Testar automaticamente a CPU e seus estados |
| **ngspice** | Analisar sinais elétricos e circuitos analógicos |
| **KiCad** | Criar esquemáticos, verificar conexões e projetar a PCB |

Ainda não executei uma simulação de esquemático nessas ferramentas. O primeiro experimento foi comportamental; a próxima etapa é traduzir os blocos para conexões reais de CIs e conferir os modelos de temporização.

## Como avançaremos

Quero começar pelo núcleo da CPU: **ALU, registradores, flags e barramento interno**. Depois integraremos o sequenciador de instruções, a ROM, a RAM e os periféricos.

Em cada etapa, manteremos três estados claros: *projetado*, *simulado* e *validado fisicamente*. Assim não confundiremos um teste de software bem-sucedido com garantia de funcionamento da placa.

**E uma decisão importante:** não vamos fixar o 74HC283 ou qualquer outro CI só porque passou no primeiro teste. Antes de aprovar um componente, compararemos quantidade de chips, desempenho, disponibilidade, encapsulamento SOIC e complexidade do circuito.

Esse processo permitirá otimizar o ISA-1 sem sacrificar recursos, exatamente como combinamos.

Nosso objetivo agora é sair de uma CPU descrita em ideias e chegar a uma **CPU definida por circuitos, testada instrução por instrução e preparada para virar uma PCB real**.

## user — bbb2138f-3da8-4380-9bab-b15daa78d719

Pode seguir

## assistant — a40b1a85-2021-454f-b8fd-f4e9a4ddf09f

{"content_type": "thoughts", "source_analysis_msg_id": "d7dfe47d-234d-4a03-b78c-cba6ad23b4ef", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou arquivos e fortaleceu validações da simulação da ALU"}]}

## assistant — d435e20f-1867-43df-a253-bf9259991f04

{"content": "Pensou por 34s", "content_type": "reasoning_recap"}

## assistant — 87da9862-3749-46bd-b095-dbe28bdb6955

Avançamos! 😄 Comecei a **revisão 1.4 do ISA-1**, agora com testes executáveis para os blocos fundamentais da CPU.

O objetivo é testar as decisões eletrônicas antes de transformá-las em uma placa física.

## Resultado dos primeiros testes

<box border radius="lg" padding={3} gap={3}>
  <row align="center" justify="between">
    **Simulação funcional — Rev. 1.4**
    <badge color="success">Testes aprovados</badge>
  </row>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" color="default" tabularNums>786.432</title>
      <text color="secondary" size="xs">Combinações testadas na ALU</text>
    </grid-item>
    <grid-item>
      <title size="2xl" color="default" tabularNums>100.000</title>
      <text color="secondary" size="xs">Transições de registradores e flags</text>
    </grid-item>
  </grid>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Soma, subtração e operações lógicas
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Flags Carry e Zero
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Detecção de conflito no barramento simulado
  </row>
</box>

### O que estamos simulando

O primeiro bloco é uma ALU de 8 bits, com uma implementação candidata baseada em dois somadores de 4 bits em cascata.

<box border radius="lg" padding={3} gap={1}>
  <svg viewBox="0 0 330 200" width="100%">
    <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="15" y="10" width="86" height="37" rx="5"/>
      <rect x="229" y="10" width="86" height="37" rx="5"/>
      <rect x="40" y="85" width="107" height="57" rx="6"/>
      <rect x="185" y="85" width="107" height="57" rx="6"/>
      <path d="M58 47 V85 M271 47 V85 M147 113 H185"/>
      <path d="M93 142 V175 H240 V142"/>
      <path d="M167 113 V73 H315 V55" strokeDasharray="4 4"/>
    </g>
    <g fill="currentColor" fontSize="11" textAnchor="middle">
      <text x="58" y="25" fontWeight="600">A / B</text>
      <text x="58" y="38" fontSize="9">bits 0–3</text>
      <text x="272" y="25" fontWeight="600">A / B</text>
      <text x="272" y="38" fontSize="9">bits 4–7</text>
      <text x="93" y="105" fontWeight="600">Somador 4 bits</text>
      <text x="93" y="121" fontSize="10">74HC283</text>
      <text x="239" y="105" fontWeight="600">Somador 4 bits</text>
      <text x="239" y="121" fontSize="10">74HC283</text>
      <text x="166" y="104" fontSize="9">Carry</text>
      <text x="166" y="190" fontSize="10">Resultado de 8 bits</text>
    </g>
  </svg>
  <caption>Diagrama funcional simplificado, ainda não um esquemático elétrico com pinagem real.</caption>
</box>

Testamos ADD, ADC, SUB, SBC, AND, OR e XOR. Também verificamos a seleção de fontes no barramento e introduzimos propositalmente um conflito para confirmar que o modelo consegue detectá-lo.

**Importante:** esses resultados aprovam o comportamento matemático do modelo, não os tempos elétricos dos CIs. Ainda não executamos uma simulação de circuito com modelos físicos dos componentes.

## Arquivos da revisão 1.4

<box gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Relatório técnico**
      <text color="secondary" size="xs">Resultados, decisões provisórias e limitações dos testes.</text>
      [Abrir relatório Rev. 1.4](sandbox:/mnt/data/isa1/ISA-1_REV14_RELATORIO.md)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Simulador funcional em Python**
      <text color="secondary" size="xs">Código reproduzível dos testes da ALU, barramento e registradores.</text>
      [Baixar código da simulação](sandbox:/mnt/data/isa1/isa1_rev14_logic_sim.py)
    </box>
  </row>
</box>

## Próximo passo: sair do modelo matemático e chegar aos CIs reais

Agora vem uma parte mais interessante: definir a ligação de cada componente.

Quero desenvolver o primeiro esquemático da CPU com:

- Registradores e ALU conectados por barramentos reais.
- Controle de leitura e escrita, incluindo sinais `/OE` e `/WE`.
- Clock, reset e flags.
- Pinagem e alimentação dos CIs selecionados.
- Verificação dos caminhos de dados e conflitos entre saídas.

Depois vamos confrontar o circuito com os datasheets, testar sua temporização e somente então começar a dimensionar a frequência de operação.

**O ISA-1 ainda não está pronto para fabricar, mas agora temos uma base de testes reproduzível.** A próxima meta é fazer a primeira parte da CPU funcionar em uma simulação de circuito, e não apenas em um modelo de software.

## user — bbb214ac-ce9e-4432-96b4-18432d685c64

Pode seguir

## assistant — 11e17fe3-2b11-4c64-afc8-249048267ba5

{"content_type": "thoughts", "source_analysis_msg_id": "0a75fa7a-a9f7-4762-97d5-0a72243711ad", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, implementou modelo de barramento e criou relatório ISA-1"}]}

## assistant — 5c9fbec5-f07c-40f1-a05a-1f562f43184e

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 779e944f-515c-4d6f-b93a-29b406f5cbbd

Avançamos para a **revisão 1.5 do ISA-1**! Agora começamos a testar como os registradores e o barramento da CPU trabalham juntos.

Executei novamente os testes anteriores e acrescentei um novo modelo de ciclos de leitura, carregamento e reset.

## Resultados desta etapa

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" color="success" tabularNums>786.432</title>
      <text color="secondary" size="xs">Casos da ALU aprovados</text>
    </grid-item>
    <grid-item>
      <title size="xl" color="success" tabularNums>100.000</title>
      <text color="secondary" size="xs">Transições de estado aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" color="success" tabularNums>61</title>
      <text color="secondary" size="xs">Novos casos de controle verificados</text>
    </grid-item>
    <grid-item>
      <title size="xl" color="default">Rev. 1.5</title>
      <text color="secondary" size="xs">Modelo funcional atualizado</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Resultados de testes em Python executados nesta sessão; ainda não são simulações elétricas dos CIs.</text>
</box>

### O que verificamos

- Seleção de uma única fonte para o barramento de 8 bits.
- Carregamento simultâneo dos registradores A e B.
- Preservação das flags quando não há comando de atualização.
- Prioridade do reset sobre os comandos de carregamento.
- Detecção de tentativas de carregar um registrador sem fonte de dados.

## Encontramos um risco importante

Imagine que o registrador A esteja transmitindo dados pelo barramento e a CPU precise passar o controle para a RAM.

Mesmo que nosso decodificador selecione apenas uma fonte de cada vez, **os atrasos reais dos CIs podem provocar um instante em que as duas saídas ficam habilitadas**.

Isso pode gerar conflito elétrico.

Portanto, o próximo circuito precisa garantir uma transição segura entre as fontes, usando uma fase de desabilitação ou outra solução comprovada por análise temporal.

É exatamente esse tipo de problema que queremos encontrar antes de encomendar as placas.

## Arquivos da revisão

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Relatório técnico Rev. 1.5**

      [Abrir relatório](sandbox:/mnt/data/isa1/ISA-1_REV15_RELATORIO.md)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Simulador de barramento e registradores**

      [Baixar código Python](sandbox:/mnt/data/isa1/isa1_rev15_bus_cycle.py)
    </box>
  </row>
</box>

## O que vem agora

A próxima etapa será transformar esse modelo em um circuito com componentes reais, começando por candidatos como:

| CI | Função |
|---|---|
| 74HC283 | Somador de 4 bits |
| 74HC574 | Registrador de 8 bits |
| 74HC245 | Interface de barramento |
| Lógica 74HC adicional | Seleção e controle |

Ainda precisamos verificar pinagem, tempos de propagação, compatibilidade elétrica e disponibilidade em SOIC antes de aprová-los.

**Uma limitação importante:** neste ambiente ainda não tenho um simulador HDL ou SPICE disponível para executar a simulação elétrica desses CIs. Não vou apresentar os testes Python como se fossem essa validação.

Nossa próxima meta técnica é obter um **esquemático real do primeiro bloco da CPU**, com conexões por pino, seguido de testes de temporização.

Seguimos com a arquitetura completa do ISA-1, sem eliminar recursos para reduzir a quantidade de chips. E a PCB única SMD SOIC continua sendo nossa escolha.

## user — bbb2140e-cda3-42e3-b49b-19f679f8072a

Pode analisar o risco e entender as correções e seguir com o projeto

## assistant — 131d6214-0845-45b6-beb5-7e8b1e5eb27c

{"content_type": "thoughts", "source_analysis_msg_id": "7dec1328-04cb-4c1c-a092-3d47bd168d4b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificada segurança de hardware e modelada contenção do barramento"}]}

## assistant — 72cf7d88-50b8-4e4d-96f2-8c95861159bf

{"content": "Pensou por 41s", "content_type": "reasoning_recap"}

## assistant — f6203f85-adca-4906-bdea-f39587b3d855

Analisei o risco identificado na revisão 1.5 e encontrei uma decisão importante para o ISA-1: **não devemos depender apenas de um decodificador que seleciona uma fonte por vez para garantir a segurança elétrica do barramento.**

O problema aparece quando a CPU troca a origem dos dados, por exemplo, do registrador A para a RAM. Mesmo que o controle lógico esteja correto, os circuitos reais não respondem instantaneamente. Durante alguns nanossegundos, duas saídas podem tentar controlar os mesmos fios.

Isso é diferente de um erro de cálculo: é um possível **conflito elétrico**, capaz de causar mau funcionamento e consumo excessivo.

Minha proposta é atacar o problema na arquitetura, antes de tentar resolvê-lo apenas ajustando atrasos.

### Correção escolhida para investigação

Vamos separar duas situações:

- **Dentro da CPU:** preferir multiplexadores para selecionar dados, evitando vários registradores disputando um mesmo barramento interno.
- **Na interface com a memória:** usar controle explícito de leitura, escrita e desabilitação, garantindo que a CPU e a SRAM não dirijam simultaneamente o barramento externo.

Essa solução pode exigir alguns CIs adicionais, mas segue exatamente nossa decisão de não sacrificar confiabilidade para economizar componentes.

Vou confrontá-la com o modelo anterior e testar também as transições perigosas, não apenas as operações que deveriam funcionar.

## ISA-1 — Revisão 1.6 concluída

Revisei o modelo anterior, implementei um teste adicional e documentei as correções propostas.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    **Resultados da simulação funcional**
    <badge color="success">2.959 testes aprovados</badge>
  </row>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>1</title>
      <text color="secondary" size="xs">Cenário de conflito reproduzido</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>3</title>
      <text color="secondary" size="xs">Estados de acesso à memória modelados</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Testes executados em Python com atrasos hipotéticos. Não representam simulação elétrica de CIs comerciais.</text>
</box>

### O que encontramos

No modelo, uma saída demora 12 unidades de tempo para desligar e outra demora 7 para ligar. Se os comandos mudarem simultaneamente, ocorre uma sobreposição de **5 unidades de tempo**.

Esse resultado confirma que o controle one-hot da revisão anterior, sozinho, não garante segurança durante as transições.

### Como corrigiremos

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Arquitetura proposta para o caminho de dados</text>
  <svg viewBox="0 0 340 184" width="100%">
    {#each [{x:12,t:"REG A"},{x:94,t:"REG B"},{x:176,t:"ALU"},{x:258,t:"RAM*"}] as p}
      <rect x={p.x} y="12" width="70" height="32" rx="5" fill="#64748b" fillOpacity=".16" stroke="#94a3b8"/>
      <text x={p.x+35} y="32" textAnchor="middle" fontSize="11" fill="currentColor">{p.t}</text>
      <path d={`M${p.x+35} 44 V67`} stroke="currentColor" strokeWidth="1.3"/>
    {/each}
    <rect x="73" y="67" width="194" height="45" rx="6" fill="#0d9488" fillOpacity=".18" stroke="#0d9488" strokeWidth="1.5"/>
    <text x="170" y="86" textAnchor="middle" fill="currentColor" fontSize="12" fontWeight="600">MULTIPLEXADOR</text>
    <text x="170" y="101" textAnchor="middle" fill="currentColor" fontSize="10">Uma saída selecionada</text>
    <path d="M170 112 V141" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="93" y="141" width="154" height="31" rx="5" fill="#64748b" fillOpacity=".16" stroke="#94a3b8"/>
    <text x="170" y="161" textAnchor="middle" fontSize="11" fill="currentColor">Destino / registradores</text>
  </svg>
  <caption>*A interface da RAM terá controle de direção separado. Diagrama funcional, não esquemático elétrico.</caption>
</box>

Para a memória, defini três estados conceituais:

| Estado | SRAM lê | SRAM escreve | CPU dirige dados |
|---|---|---|---|
| IDLE | Não | Não | Não |
| READ | Sim | Não | Não |
| WRITE | Não | Sim | Sim |

Entre operações que mudam a direção do barramento, incluiremos uma fase de guarda. Sua duração real ainda precisa ser calculada com os datasheets.

## Arquivos desta revisão

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Relatório técnico Rev. 1.6**

      [Abrir análise de riscos e correções](sandbox:/mnt/data/isa1/ISA-1_REV16_RISCO_BARRAMENTO_E_CORRECOES.md)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Simulador reproduzível**

      [Baixar teste de segurança do barramento](sandbox:/mnt/data/isa1/isa1_rev16_bus_safety.py)
    </box>
  </row>
</box>

## Próxima decisão de engenharia

A revisão nos dá uma direção mais segura: **usar multiplexadores no caminho interno da CPU e um controlador de acesso à memória com estados registrados**.

Isso ainda precisa ser confrontado com a quantidade de CIs, a frequência desejada e os tempos reais dos componentes.

O próximo trabalho será selecionar os modelos exatos de CIs SOIC e construir o primeiro esquemático com pinagem real. Só então poderemos avançar para uma simulação temporal fundamentada nos datasheets.

**Situação atual:** a falha conceitual foi identificada, reproduzida e recebeu uma proposta de correção testada em modelo abstrato. A correção ainda não está validada eletricamente.

Seguimos sem liberar a PCB para fabricação até termos evidências suficientes de que o hardware funciona.

## user — bbb212fe-2c98-4eb4-bef4-d5a9827b40e6

Segue pra testar essa correção, e como o gigatron resolveu, contornou isso? 

## assistant — 819e76a6-055d-4809-81c5-db9a1b2daa89

{"content_type": "thoughts", "source_analysis_msg_id": "b51a818d-b612-416e-a521-f17cebe38bd9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 10 sites"}]}

## assistant — 8297a59e-00bf-4a0b-9b50-467929b4488f

{"content_type": "thoughts", "source_analysis_msg_id": "f7a79c4c-4d2c-463b-a53e-c0f6964d7704", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou testes, simulou turnaround e criou relatório de validação"}]}

## assistant — 554e0317-e17e-4e2e-bd96-6d3e82b50851

{"content": "Pensou por 25s", "content_type": "reasoning_recap"}

## assistant — f8c204c7-d191-4566-88e8-14d7e80b2108

Avançamos para a **revisão 1.7 do ISA-1**! 😄

Testei novamente a correção do barramento e estudei os esquemáticos e a documentação do Gigatron. Encontramos uma solução interessante que podemos aproveitar **sem simplificar a nossa CPU**.

## 1. Como o Gigatron resolveu esse problema?

<AsyncImage query="Gigatron TTL computer original PCB close up 74HCT integrated circuits" aspectRatio="16:9" maxHeight={210}/>

O Gigatron não coloca todos os componentes disputando um único barramento central. Ele separa os caminhos de dados:

- **Barramento de dados:** recebe informações da RAM, do acumulador, da entrada ou do operando da instrução, selecionadas por buffers tri-state.
- **Barramento de resultado:** transporta o resultado da ALU até os registradores.
- **Barramento de instruções:** a ROM fornece instruções independentemente da RAM.

Isso reduz a quantidade de disputas e permite que diferentes partes da CPU trabalhem em paralelo. <Cite refs={["turn608890search18","turn608890search19"]}/>

Além disso, o Gigatron toma um cuidado importante: **a escrita na RAM ocorre na segunda fase do clock**, depois que o endereço teve tempo para estabilizar. Os próprios criadores analisaram os atrasos das portas lógicas nesse caminho crítico. <Cite ref="turn608890search10"/>

Portanto, ele não elimina magicamente os atrasos elétricos. Ele organiza os caminhos e o momento em que cada operação acontece.

## 2. O que testei no ISA-1

Reexecutei a análise de transição entre dois dispositivos conectados ao mesmo barramento.

O teste considera que um dispositivo demora para liberar suas saídas enquanto outro começa a habilitá-las.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Rev. 1.7 — Resultados do modelo temporal</text>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>1.764</title>
      <text color="secondary" size="xs">Cenários de atraso avaliados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>29</title>
      <text color="secondary" size="xs">Verificações adicionais de controle</text>
    </grid-item>
  </grid>
  <divider color="subtle"/>
  <Chart content={{"chartType":"bar","meta":{"footer":"Unidades de tempo abstratas; não representam nanossegundos de componentes reais."},"xKey":"guard","series":[{"dataKey":"conflicts","label":"Possíveis sobreposições"}],"yAxisMin":0,"data":[{"guard":"Sem guarda","conflicts":231},{"guard":"10 unidades","conflicts":66},{"guard":"20 unidades","conflicts":1},{"guard":"21 unidades","conflicts":0}]}}/>
  <caption>O modelo considera atrasos hipotéticos de 0 a 20 unidades. A igualdade entre desligamento e habilitação foi tratada como insegura.</caption>
</box>

**Resultado:** a fase de guarda evitou a sobreposição em todos os cenários testados quando sua duração superou o atraso máximo de desligamento assumido.

Isso valida o princípio da correção no modelo, mas **não determina ainda quantos nanossegundos serão necessários no ISA-1 real**.

## 3. A arquitetura que recomendo

Vamos aproveitar a separação de caminhos do Gigatron, mas manter os recursos que planejamos para nossa CPU.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 222" width="100%">
    <g strokeWidth="1.4" strokeLinejoin="round">
      <rect x="10" y="10" width="94" height="43" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <rect x="123" y="10" width="94" height="43" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <rect x="236" y="10" width="94" height="43" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <rect x="84" y="82" width="172" height="42" rx="5" fill="#0d9488" fillOpacity=".14" stroke="#0d9488"/>
      <rect x="106" y="148" width="128" height="38" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <g fill="none" stroke="currentColor">
        <path d="M57 53 V69 H125 V82 M170 53 V82 M283 53 V69 H215 V82"/>
        <path d="M170 124 V148 M234 167 H295 V116"/>
        <path d="M295 116 H330"/>
      </g>
      <g fill="currentColor" fontSize="11" textAnchor="middle">
        <text x="57" y="28" fontWeight="600">Registradores</text>
        <text x="57" y="41" fontSize="9">A, B, X...</text>
        <text x="170" y="28" fontWeight="600">RAM</text>
        <text x="170" y="41" fontSize="9">Interface segura</text>
        <text x="283" y="28" fontWeight="600">ROM</text>
        <text x="283" y="41" fontSize="9">Firmware</text>
        <text x="170" y="100" fontWeight="600">Seleção de dados</text>
        <text x="170" y="113" fontSize="9">Multiplexadores / buffers</text>
        <text x="170" y="164" fontWeight="600">ALU ISA-1</text>
        <text x="170" y="177" fontSize="9">8 bits + flags</text>
        <text x="287" y="106" fontSize="9">Resultado</text>
      </g>
    </g>
  </svg>
  <caption>Diagrama conceitual: a ligação definitiva entre ROM, RAM e registradores ainda será definida no esquemático.</caption>
</box>

A interface da RAM terá cinco estados:

| Estado | Comportamento |
|---|---|
| IDLE | Ninguém dirige o barramento externo |
| READ | A RAM fornece dados |
| WRITE_SETUP | CPU apresenta endereço e dados |
| WRITE_PULSE | Pulso de gravação na RAM |
| WRITE_HOLD | Dados permanecem estáveis após escrita |

A passagem entre leitura e escrita terá uma fase de guarda.

Isso preserva nossa intenção de ter uma CPU com registradores, flags, pilha e instruções próprias, sem copiar as limitações do Gigatron.

## 4. Arquivos gerados

<box gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Relatório técnico — Revisão 1.7**

      [Abrir análise, testes e comparação com o Gigatron](sandbox:/mnt/data/isa1/ISA-1_REV17_VALIDACAO_E_GIGATRON.md)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **Simulador de transições do barramento**

      [Baixar código Python reproduzível](sandbox:/mnt/data/isa1/isa1_rev17_turnaround.py)
    </box>
  </row>
</box>

## 5. O próximo teste será mais próximo do hardware real

Agora precisamos selecionar os CIs específicos em SOIC, principalmente os buffers, multiplexadores e a SRAM.

Com os datasheets, poderemos calcular os tempos máximos de desligamento e mínimos de habilitação, além dos tempos de escrita e leitura da memória.

Depois disso, construiremos uma simulação com esses limites e verificaremos se a sequência de controle continua segura.

**Minha conclusão:** a correção está funcionando no modelo abstrato, e a arquitetura do Gigatron reforça a vantagem de separar caminhos de dados. Ainda não temos evidência suficiente para liberar o circuito físico.

O próximo marco será o **primeiro subsistema do ISA-1 definido por CIs reais, com pinagem e temporização verificadas**.

## user — bbb21c41-abe5-4306-87e6-28e836ea6a2a

Só antes, essa ideia do gigatron, vale a pena pra gente? 

## assistant — 4b4e230b-c311-434d-a1d3-b2dd15654efb

{"content_type": "thoughts", "source_analysis_msg_id": "79ba0238-5aed-4d48-8224-28169fc338d0", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — 4fccf07c-98a2-45d1-ad96-93248a9328e8

{"content": "Processou por alguns segundos", "content_type": "reasoning_recap"}

## assistant — 126631de-ae62-4919-b438-afcd8d3a582f

**Sim, vale a pena — mas eu aproveitaria a filosofia de organização dos circuitos do Gigatron, não sua arquitetura inteira.**

Para o ISA-1, a ideia de separar os caminhos de dados é particularmente interessante porque pode melhorar a confiabilidade e facilitar a temporização sem eliminar recursos da nossa CPU.

Mas há uma ressalva: **não precisamos copiar o circuito do Gigatron para resolver o problema de conflito no barramento**. Podemos usar multiplexadores e sinais de controle bem definidos em uma arquitetura própria.

Minha preferência é aproveitar o que ele faz bem e preservar tudo que torna o ISA-1 um computador mais completo.

## O que realmente vale aproveitar

| Ideia do Gigatron | Vale para o ISA-1? | Minha decisão |
|---|---|---|
| Separar barramento de dados e de resultados | **Sim** | Adotar como referência |
| Organizar a ALU em estágios | **Sim** | Comparar com nossa ALU |
| Simplificar a lógica de controle | **Sim** | Investigar redução de CIs |
| Sincronizar a escrita na RAM com o clock | **Sim** | Incorporar à análise temporal |
| Executar instruções nativas somente da ROM | Não é nosso objetivo | Preservar programação prática |
| Gerar vídeo inteiramente pela CPU | Provavelmente não | Preferir vídeo independente |
| Eliminar pilha e recursos da CPU | Não | Preservar |

A documentação oficial confirma que o Gigatron utiliza caminhos separados para dados e resultados, uma ALU organizada em estágios e uma arquitetura que executa uma instrução nativa por ciclo. <Cite refs={["turn781678search11","turn781678search0"]}/>

## Mas existe uma oportunidade ainda melhor

Em vez de copiar os barramentos do Gigatron, podemos **adaptar o princípio ao ISA-1**:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 188" width="100%">
    {#each [{x:8,t:"Registradores"},{x:113,t:"RAM / ROM"},{x:218,t:"Entrada / I/O"}] as p}
      <rect x={p.x} y="9" width="94" height="32" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <text x={p.x+47} y="29" fill="currentColor" fontSize="10" textAnchor="middle">{p.t}</text>
      <path d={`M${p.x+47} 41 V61`} stroke="currentColor" strokeWidth="1.3"/>
    {/each}
    <rect x="57" y="61" width="206" height="33" rx="5" fill="#0d9488" fillOpacity=".15" stroke="#0d9488"/>
    <text x="160" y="82" fill="currentColor" fontSize="11" textAnchor="middle" fontWeight="600">Seleção segura de operandos</text>
    <path d="M160 94 V112" stroke="currentColor" strokeWidth="1.4"/>
    <rect x="100" y="112" width="120" height="30" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
    <text x="160" y="131" fill="currentColor" fontSize="11" textAnchor="middle">ALU ISA-1</text>
    <path d="M160 142 V158" stroke="currentColor" strokeWidth="1.4"/>
    <rect x="65" y="158" width="190" height="26" rx="5" fill="#0d9488" fillOpacity=".15" stroke="#0d9488"/>
    <text x="160" y="175" fill="currentColor" fontSize="10" textAnchor="middle">Barramento de resultados</text>
  </svg>
  <caption>Organização conceitual dos caminhos de dados; não representa conexões físicas aprovadas.</caption>
</box>

Isso nos permitiria manter registradores, flags, pilha, CALL/RET e endereçamento de 16 bits, enquanto investigamos se conseguimos diminuir multiplexadores e buffers.

**O principal benefício não é necessariamente a velocidade ou a redução de CIs. É uma organização mais previsível do hardware.**

E vale destacar uma diferença: a separação dos barramentos não elimina automaticamente os riscos elétricos. Ainda teremos que verificar transições de controle, temporização da SRAM e estados durante o reset.

## Minha decisão

**Sim, vamos incorporar essa ideia à arquitetura do ISA-1, mas como uma otimização, não como uma mudança radical de CPU.**

Antes de aprová-la definitivamente, compararia duas implementações do mesmo conjunto de instruções:

- Nossa arquitetura anterior, com barramento compartilhado e controle de acesso.
- Uma arquitetura com caminhos de dados e resultados separados, inspirada no Gigatron.

A vencedora será aquela que apresentar melhor equilíbrio entre quantidade de CIs, frequência segura, consumo e facilidade de fabricação.

E manteremos uma regra: **nenhuma otimização poderá retirar funcionalidades já definidas para o ISA-1.**

Assim, o Gigatron continua sendo uma referência de engenharia, enquanto o ISA-1 permanece um projeto original.

## user — bbb210e6-7d2c-4026-8137-0f254f18f411

Perfeito pode testar essas decisões

## assistant — c52cdbce-b28c-467f-bfaa-c313db188751

{"content_type": "thoughts", "source_analysis_msg_id": "18925ec5-163f-4c68-b776-09887b20653f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Elaborado relatório comparativo arquitetural ISA-1 com simulação randomizada"}]}

## assistant — 938d5b67-f63b-4dff-93a4-804925a71157

{"content": "Pensou por 40s", "content_type": "reasoning_recap"}

## assistant — a7d8dafc-d2c5-44f4-a35f-42c2bb6108ff

## ISA-1 — Revisão 1.8: primeiros testes comparativos

Executei um novo teste para comparar as duas organizações que estamos considerando: **barramento compartilhado** e **caminhos separados de dados e resultados**, inspirados no Gigatron.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" color="success" tabularNums>50.000</title>
      <text color="secondary" size="xs">Instruções comparadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success" tabularNums>40.034</title>
      <text color="secondary" size="xs">Verificações de estados da SRAM</text>
    </grid-item>
  </grid>
  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência de estado entre os dois modelos funcionais.
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma combinação proibida de sinais nos estados estáticos testados.
  </row>
</box>

O teste incluiu operações aritméticas, lógicas, leitura e escrita de memória, CALL, RET e desvio condicional.

**Uma distinção importante:** os dois modelos ainda compartilham a mesma implementação abstrata das instruções. Portanto, esse teste verifica a compatibilidade da sequência de operações com as duas organizações, mas não comprova que dois circuitos independentes já executam corretamente essas instruções.

### O risco de conflito continua sob controle?

No modelo temporal abstrato, sim, desde que exista uma margem de desabilitação suficiente.

<Chart content={{"chartType":"line","meta":{"footer":"Atrasos hipotéticos de 0 a 20 unidades; não são dados de datasheets."},"xKey":"guard","series":[{"dataKey":"unsafe","label":"Casos com possível sobreposição"}],"data":[{"guard":"0","unsafe":231},{"guard":"5","unsafe":136},{"guard":"10","unsafe":66},{"guard":"15","unsafe":21},{"guard":"20","unsafe":1},{"guard":"21","unsafe":0}]}}/>

Esse resultado reforça que a fase de guarda funciona matematicamente, mas ainda não determina o tempo necessário em nanossegundos.

## O que os testes nos permitem decidir

**Minha recomendação é manter os caminhos separados como nossa arquitetura candidata preferida**, mas ainda não definitiva.

Ela apresenta uma vantagem concreta: com multiplexadores, os registradores internos não precisam disputar eletricamente a mesma linha. Isso simplifica um dos problemas que identificamos.

Entretanto, ainda precisamos demonstrar que essa solução não aumenta demais a quantidade de CIs ou prejudica a frequência.

| Critério | Resultado atual |
|---|---|
| Comportamento funcional comparado | Compatível no modelo |
| Conflito interno entre fontes | Evitável com multiplexadores |
| Controle estático da SRAM | Aprovado no modelo |
| Transições elétricas reais | Pendente |
| Quantidade de CIs | Pendente |
| Frequência máxima | Pendente |
| Circuito pronto para fabricar | **Não** |

## Arquivos da revisão 1.8

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório técnico Rev. 1.8](sandbox:/mnt/data/isa1/ISA-1_REV18_RELATORIO.md)**

      <text color="secondary" size="xs">Resultados, limitações e decisões de engenharia.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Simulador comparativo em Python](sandbox:/mnt/data/isa1/isa1_rev18_compare.py)**

      <text color="secondary" size="xs">Código executável com testes reproduzíveis.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Resultados completos em JSON](sandbox:/mnt/data/isa1/isa1_rev18_results.json)**

      <text color="secondary" size="xs">Contagens e verificações produzidas pela execução.</text>
    </box>
  </row>
</box>

### Próximo marco de engenharia

Agora precisamos fazer uma mudança importante na forma de testar: sair de dois modelos que compartilham a mesma lógica e construir **duas implementações independentes usando portas e CIs específicos**.

Quero que a próxima revisão contenha a pinagem real dos componentes SOIC, a organização elétrica dos registradores e da ALU, e os caminhos críticos de temporização.

Isso nos permitirá comparar as alternativas em termos de hardware, não apenas comportamento de software.

**Seguimos com o ISA-1 completo, sem retirar recursos. A revisão 1.8 nos deu uma direção promissora, mas ainda não uma aprovação para fabricação.**

## user — bbb214ba-3ada-4590-979f-dc733b0dc6ac

Pode seguir com sua próxima revisão com a pinagem real

## assistant — 01d697eb-17cf-4d76-9cd2-9888ff4391f7

{"content_type": "thoughts", "source_analysis_msg_id": "863309c7-ccbb-44ec-a3bf-ab3fdf8b2a12", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas e arquivos disponíveis"}]}

## assistant — 10d0b6be-3171-44a6-aeb9-26bdca7d701e

{"content_type": "thoughts", "source_analysis_msg_id": "177a2ec7-7be6-47bf-9395-91442b9848e9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 1 site"}]}

## assistant — 44e404a8-ce87-41c1-97fb-39314bfcc299

{"content_type": "thoughts", "source_analysis_msg_id": "d1135f01-fb73-478e-be3b-f0b1c0212d89", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementadas verificações de pinos e criado relatório técnico ISA-1"}]}

## assistant — ed6ac6f1-26df-4091-876e-376afcc39fcc

{"content": "Pensou por 32s", "content_type": "reasoning_recap"}

## assistant — 308ed712-b560-4056-9f71-f6197754a243

## ISA-1 — Revisão 1.9: começamos a trabalhar com pinagem real

Já identifiquei três componentes da Texas Instruments disponíveis em encapsulamentos SOIC e conferi suas funções nos datasheets oficiais.

| CI | Função | Encapsulamento |
|---|---|---|
| **SN74HC574** | Registrador de 8 bits | SOIC-20 |
| **SN74HC157** | Multiplexador de quatro canais 2:1 | SOIC-16 |
| **SN74HC245** | Transceptor bidirecional de 8 bits | SOIC-20 |

Esses componentes são candidatos para a arquitetura de caminhos separados que escolhemos investigar. <Cite refs={["turn955480search37","turn955480search36","turn929718view0"]}/>

Executei também um primeiro verificador de pinagem e comportamento:

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" color="success" tabularNums>72</title>
      <text color="secondary" size="xs">Posições de pinos conferidas</text>
    </grid-item>
    <grid-item>
      <title size="xl" color="success" tabularNums>262.144</title>
      <text color="secondary" size="xs">Combinações lógicas de multiplexação testadas</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Verificação por script Python com tabelas de pinagem transcritas dos datasheets. Não é ainda uma simulação elétrica.</text>
</box>

Uma descoberta importante para nosso projeto: o **74HC157 não possui saída em alta impedância**. Quando desabilitado, ele força suas saídas para nível baixo. Portanto, podemos usá-lo na seleção interna de operandos, mas não tratá-lo como um buffer tri-state. <Cite ref="turn955480search1"/>

## O que descobrimos na revisão

A pinagem real revelou dois detalhes que precisam influenciar o circuito:

**1. O 74HC574 não possui reset interno.** O pino `/OE` desabilita suas saídas, mas não apaga os dados armazenados. Precisamos decidir se os registradores terão inicialização controlada ou se escolheremos um componente com reset dedicado. <Cite ref="turn955480search37"/>

**2. O 74HC245 permite isolar os barramentos.** Podemos desabilitá-lo antes de inverter a direção dos dados, reduzindo o risco de conflito entre CPU e memória. <Cite ref="turn929718view0"/>

### Primeira análise temporal com dados reais

O datasheet do 74HC245 apresenta, para condições específicas de alimentação, carga e temperatura, um tempo máximo de desabilitação de **50 ns**. <Cite ref="turn929718view0"/>

Como exercício inicial, considerei uma guarda de 80 ns, deixando 30 ns de margem sobre esse limite.

Isso **não aprova os 80 ns para o circuito final**: ainda faltam os atrasos do controlador, da SRAM e das interconexões.

### Arquivos da revisão 1.9

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório de pinagem real — Rev. 1.9](sandbox:/mnt/data/isa1/ISA-1_REV19_PINAGEM_REAL.md)**

      <text color="secondary" size="xs">Tabelas pino a pino, ligações candidatas, análise temporal e riscos pendentes.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Verificador executável de pinagem e controle](sandbox:/mnt/data/isa1/isa1_rev19_pincheck.py)**

      <text color="secondary" size="xs">Script Python usado nos testes desta revisão.</text>
    </box>
  </row>
</box>

**Minha avaliação:** estamos avançando na direção correta. Já temos pinagens de componentes reais, e a separação dos caminhos de dados continua sendo uma candidata promissora.

Mas não vou chamar isso de esquemático completo: ainda faltam a ALU, os demais registradores, o sequenciador e a SRAM escolhida.

Na **revisão 2.0**, a prioridade será resolver o reset dos registradores, selecionar a SRAM real e desenhar o primeiro circuito integrado de leitura e escrita com todos os pinos envolvidos. Esse será um passo muito mais próximo de um esquemático que poderemos levar ao KiCad e, posteriormente, à fabricação.

## user — bbb21447-dd7b-4da0-941e-6e661ece200b

Pode seguir com a revisão

## assistant — 9e231a05-c80b-41fd-9b73-7e81c456e086

{"content_type": "thoughts", "source_analysis_msg_id": "763febbd-f838-4452-8894-1acd304f169b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, arquivos disponíveis e script de especificações"}]}

## assistant — 22b3cf1e-7c18-4001-a6c2-b880ecbfe8be

{"content_type": "thoughts", "source_analysis_msg_id": "e19d77df-f0c4-41b9-a89c-4dd3256a19e5", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 9 sites"}]}

## assistant — af5c38ac-ee32-4e1b-b54a-1428ef87ce3d

{"content_type": "thoughts", "source_analysis_msg_id": "198a8e75-d629-43ff-8a37-8fc1c4d368c8", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementado modelo de SRAM e documentadas falhas críticas de controle"}]}

## assistant — 681dae90-26b3-45bc-90c4-08150c1b8f29

{"content": "Pensou por 37s", "content_type": "reasoning_recap"}

## assistant — 5a5d8e98-1c8e-49e6-bbb8-21a70e0310c9

## ISA-1 — Revisão 2.0: registradores com reset e SRAM real

Avancei com duas decisões de hardware:

**1. Substituir o 74HC574 pelo 74HC273 nos registradores que precisam iniciar em zero.** O 74HC273 possui entrada de limpeza assíncrona (`/CLR`), evitando depender de um programa para inicializar esses registradores. Ele existe em SOIC-20. <Cite ref="turn441950search28"/>

**2. Adotar como candidata a SRAM Alliance Memory AS6C62256-55SIN**, de 32 KB, com acesso nominal especificado em 55 ns e encapsulamento SOP-28, adequado à montagem SMD. <Cite refs={["turn441950search26","turn441950search4"]}/>

Essas escolhas ainda são candidatas, mas agora temos componentes reais para analisar.

### Primeiros resultados verificados

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>68</title>
      <text color="secondary" size="xs">Posições de pinos conferidas por script</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Endereços físicos da SRAM mapeados sem repetição</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>1.024</title>
      <text color="secondary" size="xs">Casos de transferência de dados verificados</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>6</title>
      <text color="secondary" size="xs">Estados de controle da memória examinados</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Resultados de um modelo lógico executado agora em Python. A verificação de pinos é automatizada sobre tabelas transcritas dos datasheets, não uma conferência elétrica independente.</text>
</box>

Também confirmei um detalhe importante: podemos mapear os 32 KB de SRAM no espaço de endereçamento de 16 bits sem repetir posições físicas, desde que conectemos corretamente o bit mais alto de endereço da memória.

## Correção do barramento e mapa de memória

A revisão agora utiliza seis estados de controle, incluindo uma fase de transição entre leitura e escrita.

| Estado | Função |
|---|---|
| IDLE | Barramento sem acesso |
| READ | SRAM envia dados à CPU |
| TURNAROUND | Desabilita os dispositivos antes de mudar a direção |
| WRITE_SETUP | Estabiliza endereço e dados |
| WRITE_PULSE | Executa a gravação |
| WRITE_HOLD | Mantém os dados após a gravação |

Os seis estados passaram nas verificações lógicas estáticas. **Ainda precisamos testar os atrasos das transições reais**, porque sinais de controle que mudam juntos podem chegar em momentos diferentes.

Também validamos o mapeamento candidato da RAM:

| Endereço CPU | Endereço físico SRAM |
|---|---|
| `4000h` | `0000h` |
| `7FFFh` | `3FFFh` |
| `8000h` | `4000h` |
| `BFFFh` | `7FFFh` |

Isso evita que duas regiões da CPU apontem acidentalmente para os mesmos endereços físicos.

## Arquivos da revisão 2.0

<box gap={3}>
  <row align="center" gap={3}>
    <icon name="file-text" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório técnico Rev. 2.0](sandbox:/mnt/data/isa1/ISA-1_REV20_REGISTRADORES_SRAM.md)**

      <text color="secondary" size="xs">Pinagem completa do 74HC273 e da SRAM, mapeamento, controle e riscos.</text>
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Simulador de controle e endereçamento](sandbox:/mnt/data/isa1/isa1_rev20_sram_controller.py)**

      <text color="secondary" size="xs">Script Python reproduzível.</text>
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" size="xl" color="secondary"/>
    <box flex="1" gap={1}>
      **[Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev20_results.json)**

      <text color="secondary" size="xs">Saída estruturada da execução.</text>
    </box>
  </row>
</box>

## Minha avaliação

Já conseguimos definir componentes reais e verificar parte da interface entre CPU e RAM. O 74HC273 resolve o problema de inicialização dos registradores selecionados, e a SRAM escolhida é compatível com nossa preferência por montagem SMD.

Ainda faltam três elementos fundamentais para considerar esse subsistema confiável: **circuito real de reset, temporização de leitura/escrita e sequenciador de controle**.

Na revisão 2.1, a prioridade será criar esses circuitos e confrontar seus tempos com os datasheets, antes de fixarmos o clock do ISA-1.

**Continuamos com uma única PCB, CPU própria e completa, sem sacrificar recursos.** E, principalmente, sem liberar uma placa para fabricação antes de validar suas conexões e seus limites elétricos.

## user — bbb21a6d-e4ea-4766-96da-b935b114e9b4

Legal! Já vi coisas legais, como testar antes vale a pena, vimos que alguns CIs tem que ser diferentes
Pode continuar

## assistant — 7f6fa9b3-1fbc-4286-af93-c97a5252e5d1

{"content_type": "thoughts", "source_analysis_msg_id": "f04d85e2-73d0-4dd1-a6c1-933a97c108b0", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou ferramentas, simulou transições SRAM e documentou falha crítica"}]}

## assistant — ed0acff2-f087-4162-a831-f0f0ea400ef8

{"content": "Pensou por 37s", "content_type": "reasoning_recap"}

## assistant — 21b23434-f7f3-45e4-baee-3b0ceb4994a6

## ISA-1 — Revisão 2.1: encontramos um risco que os testes anteriores não cobriam

Continuei a validação da interface entre CPU e SRAM e executei um novo simulador de transições, desta vez variando os atrasos individuais dos sinais de controle.

O resultado confirmou algo importante: **não basta que os estados READ e WRITE estejam corretos isoladamente. A passagem entre eles também precisa ser segura.**

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **330 cenários de transição protegida passaram**
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="danger"/>
    **A transição direta apresentou conflito**
  </row>
  <text color="secondary" size="xs">Teste lógico com atrasos artificiais de 0 a 3 unidades por sinal. Ainda não é uma simulação SPICE nem uma validação de tempos reais dos componentes.</text>
</box>

A solução que passou no modelo foi dividir a troca de direção em três fases: primeiro desabilitar as saídas, depois alterar a direção do transceptor e, finalmente, habilitar o novo acesso.

Isso nos dá uma sequência de controle mais robusta para implementar com lógica real.

## Outra descoberta: precisamos proteger também o lado da CPU

A revisão revelou uma lacuna no modelo anterior.

O 74HC245 conecta dois barramentos. Estávamos verificando se a SRAM e o transceptor disputavam o lado da memória, mas **ainda não tínhamos comprovado que os registradores da CPU liberavam o outro lado durante a leitura**.

Isso significa que precisamos controlar explicitamente quais circuitos podem transmitir dados em cada lado.

Essa verificação será incorporada ao projeto, juntamente com a proteção contra escrita acidental durante a inicialização.

### Arquivos da revisão 2.1

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Relatório técnico Rev. 2.1](sandbox:/mnt/data/isa1/ISA-1_REV21_TRANSICOES_RESET.md)**

      <text color="secondary" size="xs">Riscos encontrados, correções e critérios para aprovação.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Simulador de transições](sandbox:/mnt/data/isa1/isa1_rev21_transition_verify.py)**

      <text color="secondary" size="xs">Código Python para reproduzir os testes.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Resultados em JSON](sandbox:/mnt/data/isa1/isa1_rev21_results.json)**
    </box>
  </row>
</box>

## Próxima revisão: reset e sequenciador físico

Agora vou concentrar o desenvolvimento em três circuitos:

1. **Reset seguro:** garantir que, ao ligar o ISA-1, nenhuma escrita indevida aconteça e os registradores necessários sejam inicializados.
2. **Sequenciador de memória:** implementar as fases de leitura, escrita e guarda usando estados registrados.
3. **Controle completo dos barramentos:** impedir conflitos tanto no lado da SRAM quanto no lado da CPU.

Depois disso, poderemos começar a calcular uma frequência de clock sustentada pelos tempos dos componentes reais.

**O resultado desta revisão é positivo, mas não é uma aprovação do hardware físico.** Encontramos um conflito, demonstramos uma forma de evitá-lo no modelo e identificamos outra interface que precisa de proteção.

É justamente por isso que vale a pena simular antes de encomendar a PCB do ISA-1.

## user — bbb21191-9135-4cdb-8b99-ac723a521726

Veja correções pra esse conflito, procure por semelhantes na internet e fóruns
Use sempre o gigatron se precisar de alguma ideia
Veja também o outro PC feito com cis

## assistant — 3f3bfa66-3451-40bd-9bbf-4db9a8c1ada3

{"content_type": "thoughts", "source_analysis_msg_id": "a14eb304-6550-43dd-a27d-fc7d110fd015", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 13 sites"}]}

## assistant — 4990cea3-7a12-4c62-b9e6-41b1fdad3bad

{"content_type": "thoughts", "source_analysis_msg_id": "f85d784f-3116-405a-a899-0c7026664788", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou atrasos e segurança, criando relatório de validação"}]}

## assistant — f954ae24-85ac-4be5-85f0-0a3f4e10cebb

{"content": "Pensou por 31s", "content_type": "reasoning_recap"}

## assistant — 1019c71f-ea4d-42b8-bcf7-932d8ee32456

## ISA-1 — Revisão 2.2: pesquisa de falhas reais e correção do barramento

Encontrei casos muito parecidos com o nosso problema em computadores construídos com lógica 74xx. Pesquisei o **Gigatron**, o **Magic-1** e relatos de quem montou o computador de 8 bits de **Ben Eater**.

A descoberta mais importante é que **o conflito no barramento não deve ser tratado apenas adicionando um atraso**. Precisamos garantir que a própria arquitetura de controle impeça duas saídas de serem habilitadas simultaneamente, inclusive durante o reset e as mudanças de instrução.

### O que outros construtores descobriram

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="Gigatron TTL 8 bit computer green circuit board populated integrated circuits" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **<Entity category="product" value="Gigatron TTL microcomputer" disambig="computador caseiro de 8 bits feito com lógica TTL"/>**

      Separa o barramento de dados do barramento de resultados. Na escrita da RAM, estabiliza primeiro o endereço e só permite a gravação na segunda fase do clock. Isso foi uma decisão explícita de temporização dos criadores. <Cite refs={["turn971819search45","turn971819search2"]}/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Magic-1 Bill Buzbee homebrew TTL computer circuit boards" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **<Entity category="product" value="Magic-1 HomebrewCPU" disambig="computador artesanal com CPU de lógica TTL"/>**

      É outro computador real construído com aproximadamente 200 CIs 74xx. Seu criador relata problemas de temporização causados por diferenças na propagação do clock, chegando a escolher famílias lógicas mais rápidas ou lentas para contornar falhas. Ele próprio reconhece que uma organização melhor das fases de clock teria evitado parte desses problemas. <Cite refs={["turn225942search1","turn225942search5"]}/>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Ben Eater 8 bit breadboard computer bus wires registers 74LS245" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **<Entity category="other" value="Computador de 8 bits de Ben Eater" disambig="projeto educacional de CPU construída em protoboards"/>**

      Nos fóruns, encontrei relatos de EEPROMs gerando pulsos indesejados nos sinais de controle. Um construtor relatou até a queima de um 74LS245 por conflito entre módulos. Outros sugerem usar decodificadores para limitar a seleção das fontes do barramento. <Cite refs={["turn971819reddit44","turn971819reddit47"]}/>
    </box>
  </row>
</box>

Esses relatos reforçam que nosso cuidado é necessário. Não estamos resolvendo um problema meramente teórico.

## Correção que recomendo para o ISA-1

Vamos combinar três soluções, aproveitando o melhor de cada projeto:

1. **Caminhos separados**, inspirados no Gigatron: os resultados da ALU não precisam disputar o mesmo barramento usado para leitura da memória.
2. **Controle registrado e decodificado:** os sinais que habilitam saídas não devem depender diretamente de combinações instáveis das saídas de uma EEPROM ou de uma mudança assíncrona de instrução.
3. **Sequência segura de leitura e escrita:** desabilitar, aguardar a liberação, mudar a direção e só então habilitar o novo dispositivo.

Uma melhoria adicional: manter `/WE` da SRAM inativo durante reset, inicialização e transições. Isso protege os dados contra gravações acidentais.

## Teste da correção — Revisão 2.2

Executei um novo teste com atrasos hipotéticos de habilitação e desabilitação, incluindo uma situação em que o circuito de controle falha e habilita duas saídas.

<box border radius="lg" padding={3} gap={2}>
  <Chart content={{"chartType":"bar","xKey":"guard","series":[{"dataKey":"unsafe","label":"Possíveis conflitos"}],"data":[{"guard":"0","unsafe":231},{"guard":"10","unsafe":66},{"guard":"20","unsafe":1},{"guard":"21","unsafe":0},{"guard":"30","unsafe":0}]}}/>
  <caption>441 combinações por configuração. A escala representa unidades abstratas de atraso, não nanossegundos reais.</caption>
</box>

O teste confirmou três pontos: a transição direta é insegura, uma guarda suficiente elimina a sobreposição dentro das hipóteses testadas, e uma falha que habilite simultaneamente dois dispositivos continua perigosa mesmo com a sequência de estados correta.

Portanto, **não vamos depender somente da guarda temporal**. O controlador também precisará impedir habilitações incompatíveis.

### Outra correção que merece atenção

Encontrei uma questão na escolha anterior do 74HC273: ele possui reset, mas não possui entrada dedicada de habilitação de carga. Não devemos simplesmente combinar o clock com uma porta AND sem estudar os pulsos que isso pode gerar.

Vamos comparar um multiplexador na entrada do registrador com um componente que já tenha habilitação apropriada.

Esse é mais um exemplo de como a pesquisa e os testes estão evitando decisões precipitadas.

## Documentação gerada

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório completo — ISA-1 Rev. 2.2](sandbox:/mnt/data/isa1/ISA-1_REV22_PESQUISA_E_CORRECAO.md)**

      <text color="secondary" size="xs">Fontes, diagnóstico, soluções, riscos e próximas verificações.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Simulador de contenção do barramento](sandbox:/mnt/data/isa1/isa1_rev22_bus_test.py)**
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Resultados reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev22_results.json)**
    </box>
  </row>
</box>

## O que incorporaremos ao ISA-1

A contribuição do Gigatron será a separação inteligente dos caminhos de dados e a disciplina de temporização da memória.

Do Magic-1, aproveitaremos principalmente a lição de **não depender de atrasos acidentais entre componentes**.

E dos relatos dos construtores de computadores de 8 bits, adotaremos uma regra adicional: nenhum sinal crítico de escrita ou habilitação de barramento poderá depender diretamente de saídas instáveis da lógica de controle.

A próxima etapa é transformar essa correção em um **controlador com flip-flops e portas reais**, conferir sua pinagem SOIC e calcular as margens usando os tempos dos datasheets.

**A arquitetura está mais bem fundamentada, mas ainda não está aprovada para fabricação.** O teste atual é abstrato; falta comprovar que o circuito com os CIs escolhidos reproduz essa segurança.

E manteremos o compromisso: uma única PCB SMD, CPU completa, vídeo RCA colorido como objetivo e nenhum recurso importante eliminado apenas para economizar chips.

## user — bbb21578-4420-4511-91ee-9d019672da3b

Perfeito, agora assim, um exercício paralelo
Pensando nos nossos 74hc, EPROM, ROM, RAM, saída RCA colorida, 4 teclados matriciais 4x4, organizados em 4x16
Você vê alguma outra organização para nossos CIs, nossa CPU? 
Eh sempre bom dar uma pausa no que estamos planejando, ver como está, olhar pra fora, as vezes ideias surgem, acontece muito isso aqui no trabalho
Temos uma meta, mas tem vários jeitos de atingir
Veja outros PCs semelhantes
O nosso ISA-1 está ficando sensacional! E sei que podemos fazer um projeto excelente com ele

## assistant — 5482f10d-740a-49f4-acf7-fd3925800cf0

{"content_type": "thoughts", "source_analysis_msg_id": "63b53d81-f858-466e-916b-da315f5a08de", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 8 sites"}]}

## assistant — dbdf6850-21a9-458e-8415-7ea8c190d073

{"content": "Pensou por 11s", "content_type": "reasoning_recap"}

## assistant — c0695ee7-60ed-4a24-b9e9-d2c55c2a4db3

Acho que esse exercício pode mudar bastante o ISA-1 — para melhor. 😄

Olhando para o conjunto inteiro, percebo que estamos dedicando muita atenção à ALU e aos conflitos do barramento, mas ainda não comparamos suficientemente **a organização global do computador**.

E encontrei uma oportunidade interessante: talvez consigamos uma CPU mais rápida, com menos lógica de controle e vídeo colorido, sem retirar nenhuma funcionalidade que queremos.

Pesquisei outros computadores feitos com CIs discretos, incluindo o Gigatron, o Magic-1, o C74-6502 e o ECM-16. Há lições importantes nesses projetos.

## 1. Quatro computadores que merecem nossa atenção

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="Gigatron TTL 8 bit homebrew computer PCB" aspectRatio="5:4" maxWidth="136px"/>
    <box flex="1" gap={1}>
      **<Entity category="other" value="Gigatron TTL" disambig="computador de 8 bits construído com lógica discreta"/>**

      Seu ponto forte é a simplicidade dos caminhos de dados e a redução de lógica de endereçamento. O próprio código do projeto documenta uma unidade de endereçamento simplificada, economizando circuitos em relação a uma unidade mais completa. <Cite ref="turn812975search3"/>

      **Lição:** simplificar conexões pode render mais do que eliminar instruções.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Magic-1 Bill Buzbee TTL homebrew computer boards" aspectRatio="5:4" maxWidth="136px"/>
    <box flex="1" gap={1}>
      **<Entity category="other" value="Magic-1" disambig="computador caseiro com CPU microprogramada de lógica TTL"/>**

      Usa caminhos internos de 16 bits, barramento externo de 8 bits e controle microprogramado. Seu criador priorizou instruções úteis para linguagens de programação, incluindo pilha, sub-rotinas e modos de endereçamento. <Cite refs={["turn205286search2","turn205286search3"]}/>

      **Lição:** podemos ter uma CPU completa sem transformar todas as operações em circuitos dedicados.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="C74 6502 discrete TTL CPU circuit boards C74 project" aspectRatio="5:4" maxWidth="136px"/>
    <box flex="1" gap={1}>
      **<Entity category="other" value="C74-6502" disambig="reimplementação discreta do processador MOS 6502"/>**

      Usa microcódigo e antecipação da próxima microinstrução. O projeto relata operação de até 20 MHz, mas com aproximadamente 200 CIs e duas placas. <Cite refs={["turn205286search5","turn205286search48"]}/>

      **Lição:** podemos melhorar a frequência com uma organização temporal inteligente, mas não devemos esperar que isso venha gratuitamente.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="ECM-16 TTL homebrew 16 bit computer PCB 74HC" aspectRatio="5:4" maxWidth="136px"/>
    <box flex="1" gap={1}>
      **<Entity category="other" value="ECM-16/TTL" disambig="projeto de computador discreto de 16 bits com lógica 74HC"/>**

      O desenvolvedor relata que a organização da movimentação de dados entre registradores, ALU e memória acabou sendo mais importante do que algumas escolhas da própria ALU. <Cite ref="turn812975search4"/>

      **Lição:** precisamos otimizar o fluxo de dados antes de fixar a lista definitiva de CIs.
    </box>
  </row>
</box>

Esses projetos sugerem uma direção: o ISA-1 não precisa escolher entre a simplicidade extrema do Gigatron e a complexidade do Magic-1. Podemos projetar algo intermediário, pensado especificamente para nossas necessidades.

## 2. Três arquiteturas possíveis para o ISA-1

<box gap={3}>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      **A — CPU tradicional microprogramada**
      <badge>Referência atual</badge>
    </row>
    <svg viewBox="0 0 320 94" width="100%">
      {#each [{x:4,t:"REGISTRADORES"},{x:112,t:"BARRAMENTO"},{x:220,t:"ALU"}] as p}
        <rect x={p.x} y="8" width="96" height="31" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
        <text x={p.x+48} y="27" textAnchor="middle" fontSize="10" fill="currentColor">{p.t}</text>
      {/each}
      <path d="M100 24 H112 M208 24 H220 M160 39 V56" stroke="currentColor" fill="none" strokeWidth="1.5"/>
      <rect x="80" y="56" width="160" height="30" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
      <text x="160" y="75" textAnchor="middle" fontSize="10" fill="currentColor">CONTROLE MICROPROGRAMADO</text>
    </svg>
    Oferece flexibilidade e instruções completas, mas pode exigir muitos sinais de controle, multiplexadores e ciclos por instrução.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    **B — CPU de caminhos separados, inspirada no Gigatron**
    <svg viewBox="0 0 320 98" width="100%">
      {#each [{x:4,t:"REG A / B"},{x:112,t:"SELEÇÃO"},{x:220,t:"ALU"}] as p}
        <rect x={p.x} y="7" width="96" height="31" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
        <text x={p.x+48} y="26" textAnchor="middle" fontSize="10" fill="currentColor">{p.t}</text>
      {/each}
      <path d="M100 22 H112 M208 22 H220 M268 38 V54 H52 V68" stroke="currentColor" fill="none" strokeWidth="1.5"/>
      <rect x="4" y="68" width="312" height="24" rx="5" fill="#0d9488" fillOpacity=".13" stroke="#0d9488"/>
      <text x="160" y="84" textAnchor="middle" fontSize="10" fill="currentColor">BARRAMENTO DE RESULTADOS / DESTINOS</text>
    </svg>
    Reduz disputas entre fontes e pode simplificar a lógica interna. Ainda precisamos determinar quantos multiplexadores serão necessários.
  </box>
  <box border={{size:2,color:"default"}} radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      **C — CPU híbrida com unidades especializadas**
      <badge color="success">Minha favorita</badge>
    </row>
    <svg viewBox="0 0 320 120" width="100%">
      {#each [{x:4,y:5,t:"REGISTRADORES"},{x:112,y:5,t:"ALU 8 BITS"},{x:220,y:5,t:"ENDEREÇOS 16b"},{x:4,y:77,t:"CONTROLE"},{x:112,y:77,t:"MEMÓRIA"},{x:220,y:77,t:"VÍDEO / I/O"}] as p}
        <rect x={p.x} y={p.y} width="96" height="32" rx="5" fill="#64748b" fillOpacity=".13" stroke="#94a3b8"/>
        <text x={p.x+48} y={p.y+20} textAnchor="middle" fontSize="10" fill="currentColor">{p.t}</text>
      {/each}
      <path d="M100 21 H112 M208 21 H220 M268 37 V52 H52 V77 M160 37 V77 M268 52 V77" stroke="#0d9488" fill="none" strokeWidth="1.5"/>
    </svg>
    Mantém uma ALU de 8 bits, mas dá ao PC, ao SP e ao cálculo de endereços um caminho próprio, evitando usar a ALU principal para cada incremento de endereço.
  </box>
</box>

A arquitetura C merece atenção especial.

Imagine a CPU executando uma soma enquanto o circuito de endereçamento prepara o próximo acesso à memória. Em vez de obrigar a ALU a fazer as duas tarefas sequencialmente, podemos sobrepor parte do trabalho.

Isso pode melhorar o desempenho e reduzir a complexidade do controle, **embora provavelmente exija alguns somadores ou incrementadores adicionais**.

Não estou afirmando que será a arquitetura com menos CIs. Estou dizendo que ela pode oferecer o melhor equilíbrio para o ISA-1.

## 3. A oportunidade que eu não tinha considerado suficientemente: memória e vídeo

Aqui vejo uma decisão potencialmente ainda mais importante que a escolha da ALU.

Nossa proposta inicial incluía 32 KB de SRAM principal, memória de vídeo, ROM e EEPROM. Mas precisamos decidir como a CPU e o vídeo acessarão essas memórias.

Existem três caminhos:

| Organização | Vantagem | Desvantagem |
|---|---|---|
| RAM compartilhada com vídeo | Menos chips de memória | Disputa de acesso, possível espera da CPU |
| RAM e VRAM separadas | Vídeo independente | Mais componentes e interface de transferência |
| RAM compartilhada com vídeo por acesso alternado | Pode economizar memória | Temporização e arbitragem mais difíceis |

**Eu estudaria seriamente RAM e VRAM separadas.**

Por exemplo, um framebuffer de 160 × 120 pixels com 4 bits por pixel exige:

\[
160 \times 120 \times 4 / 8 = 9.600\text{ bytes}
\]

Isso cabe em uma SRAM de 16 KB.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Memória necessária para algumas opções gráficas</text>
  <Chart content={{"chartType":"bar","xKey":"mode","series":[{"dataKey":"kb","label":"VRAM necessária","valueSuffix":" KB"}],"yAxisMin":0,"data":[{"mode":"160×120, 16 cores","kb":9.375},{"mode":"160×120, 256 cores","kb":18.75},{"mode":"256×192, 16 cores","kb":24},{"mode":"256×192, 256 cores","kb":48}]}}/>
  <caption>Valores apenas do framebuffer, sem tabelas de cores, caracteres ou buffers auxiliares.</caption>
</box>

Isso abre uma possibilidade: **uma placa de vídeo com sua própria SRAM e um controlador de leitura independente**, integrado à nossa PCB única.

A CPU continuaria livre para executar BASIC e programas enquanto o circuito gráfico gera a imagem.

Mas precisamos resolver como a CPU escreverá na VRAM sem interromper a leitura do vídeo: arbitragem, acesso em janelas de tempo ou outra solução validada.

### E as cores no RCA?

Aqui precisamos ser cuidadosos. Gerar pixels coloridos digitais não é a mesma coisa que gerar vídeo composto colorido.

Vejo duas alternativas para investigar:

- Um codificador RGB para vídeo composto, com sincronismo e subportadora compatíveis com NTSC ou PAL.
- Um circuito próprio de geração de crominância e luminância, usando lógica e componentes analógicos.

A primeira opção provavelmente simplifica o desenvolvimento, mas precisamos verificar a disponibilidade e o preço de componentes adequados.

Eu **não escolheria a resolução nem a quantidade de cores definitivamente** antes de validar essa etapa. A tela RCA é uma restrição importante do projeto.

## 4. Outra oportunidade: o teclado 4 × 16

Nossos quatro teclados matriciais 4×4 formam uma matriz lógica de 4 linhas por 16 colunas.

Podemos fazer a varredura com um circuito pequeno e independente.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Organização proposta</text>
  <svg viewBox="0 0 320 125" width="100%">
    {#each [0,1,2,3] as i}
      <rect x={6+i*80} y="6" width="68" height="66" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      {#each [0,1,2,3] as r}
        {#each [0,1,2,3] as c}
          <rect x={14+i*80+c*14} y={14+r*13} width="10" height="9" rx="1.5" fill="#64748b" fillOpacity=".35" stroke="#94a3b8" strokeWidth=".5"/>
        {/each}
      {/each}
      <text x={40+i*80} y="85" fontSize="9" fill="currentColor" textAnchor="middle">Matriz {i+1}</text>
    {/each}
    <path d="M40 92 V102 H280 V92 M160 102 V110" stroke="currentColor" fill="none" strokeWidth="1.2"/>
    <text x="160" y="122" fontSize="10" fill="currentColor" textAnchor="middle">4 linhas compartilhadas + 16 colunas</text>
  </svg>
</box>

Em vez de gastar muitos sinais de controle da CPU, podemos usar um decodificador para selecionar uma linha por vez e buffers para ler as 16 colunas.

Isso exige um cuidado: as linhas não selecionadas devem permanecer em estado seguro, preferencialmente em alta impedância. Sem diodos individuais, combinações de três ou mais teclas podem produzir *ghosting*.

Também podemos implementar o *debounce* no firmware, evitando circuitos adicionais por tecla.

## 5. E se reorganizarmos ROM, EPROM e EEPROM?

Eu separaria **função** de **tecnologia**.

| Função | Solução candidata |
|---|---|
| Firmware de inicialização | EEPROM paralela ou Flash adequada |
| Microcódigo da CPU | ROM/EEPROM de controle, se a CPU for microprogramada |
| Memória de trabalho | SRAM |
| Memória gráfica | SRAM dedicada, se aprovada |
| Programas salvos | EEPROM ou Flash de dados separada |

Uma ideia interessante é usar **memória serial SPI para salvar programas**, controlada por lógica discreta e firmware.

Isso poderia economizar trilhas e CIs de interface em comparação com uma EEPROM paralela, embora exigisse um controlador SPI simples ou uma rotina de transmissão por software.

Também precisamos preservar um requisito essencial: depois da gravação inicial do firmware, o ISA-1 deve conseguir salvar e carregar programas sozinho.

## 6. O que eu mudaria no nosso plano atual

Não descartaria nada que já fizemos. Os testes de barramento, reset e SRAM continuam úteis.

Mas abriria uma comparação arquitetural antes de fechar a CPU.

| Decisão | Situação |
|---|---|
| CPU 8 bits com endereçamento 16 bits | Preservar |
| Flags, pilha, CALL/RET | Preservar |
| Caminhos de dados separados | Candidato preferido |
| Unidade própria de incremento/endereço | Investigar |
| Controle microprogramado ou híbrido | Comparar |
| SRAM principal de 32 KB | Preservar como base |
| VRAM independente | Investigar prioritariamente |
| Vídeo RCA colorido | Objetivo preservado |
| Teclado 4×16 | Preservar |
| PCB única SMD SOIC | Confirmado |

## Minha conclusão

A pesquisa trouxe três ideias que considero especialmente promissoras para o ISA-1:

**Primeira:** uma CPU com caminho de endereçamento próprio, inspirada na eficiência do Gigatron, mas mantendo as funcionalidades de uma CPU mais completa.

**Segunda:** separar a memória gráfica da RAM principal para que o vídeo não imponha continuamente restrições à execução dos programas.

**Terceira:** organizar o projeto em blocos que funcionem com pouca intervenção da CPU: vídeo, teclado e armazenamento.

A mais interessante é a primeira, porque pode alterar a quantidade de CIs, a frequência e a simplicidade de todo o projeto.

**Minha recomendação é comparar formalmente as arquiteturas B e C antes de continuar fixando componentes.** Precisamos contar os CIs de cada caminho, estimar os ciclos por instrução e modelar as transferências de dados com os mesmos programas de teste.

Essa comparação será muito mais útil do que simplesmente escolher o circuito com menos chips.

E tem algo que a pesquisa reforçou: o Gigatron mostra como simplificar, o Magic-1 mostra como construir uma CPU rica, e o C74-6502 mostra o quanto a organização do controle influencia o desempenho.

**O ISA-1 pode aproveitar essas três lições e continuar sendo inteiramente nosso.**

## user — bbb217ea-0935-4e35-90c0-bd9800bcbed0

Me responde uma coisa
O nosso PC ler um cartucho, cada cartucho com um programa, facilita ou complica as coisas? 

## assistant — 9fd02359-8dcd-485a-ab0e-e37fb631ad6a

**Facilita algumas coisas e complica outras. Mas, para o ISA-1, acho que cartuchos podem ser uma excelente ideia!** 😄

Principalmente porque queremos um computador de 8 bits completo, com identidade própria, capaz de executar jogos e programas sem depender de um PC moderno.

A questão mais importante é **como o cartucho se conecta à CPU**.

## Três maneiras de implementar cartuchos

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="retro 8 bit game console cartridge PCB edge connector exposed gold contacts ROM chip" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **1. Cartucho ROM mapeado na memória**

      A CPU acessa o programa diretamente no cartucho, como se fosse uma região de ROM interna.

      É a solução mais simples em termos de software, mas exige decodificação de endereços, proteção elétrica e uma região reservada no mapa de memória.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro computer game cartridge PCB EEPROM DIP integrated circuit connector edge fingers" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **2. Cartucho carregado na RAM**

      O firmware lê o conteúdo do cartucho, copia o programa para a RAM e o executa.

      É uma solução muito interessante para o ISA-1, porque permite retirar o cartucho depois do carregamento, desde que o programa caiba na memória e não precise consultar o cartucho durante a execução.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="retro video game cartridge PCB with multiple integrated circuit chips mapper memory" aspectRatio="5:4" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **3. Cartucho com hardware adicional**

      Além da ROM, pode conter RAM, armazenamento de dados ou outros circuitos.

      É o mais poderoso, mas também o mais complexo. Eu deixaria essa possibilidade para uma futura expansão.
    </box>
  </row>
</box>

## Comparação para nosso computador

| Característica | ROM mapeada | Carregar na RAM |
|---|---|---|
| Complexidade do hardware | Baixa a moderada | Baixa a moderada |
| Complexidade do firmware | Menor | Maior |
| Executar programas grandes | Melhor com bancos de memória | Limitado à RAM disponível |
| Remover após carregar | Não | Possivelmente |
| Interferência na CPU | Acesso à ROM do cartucho | Leitura apenas durante carga |
| Jogos e aplicativos | Sim | Sim |

## Minha escolha para o ISA-1

Eu escolheria **cartuchos ROM mapeados na memória, com opção de copiar programas para a RAM**.

Isso nos daria dois modos de funcionamento:

- **Executar diretamente do cartucho:** ideal para jogos e programas maiores, desde que nossa arquitetura permita buscar instruções nessa região.
- **Carregar na RAM:** ideal para aplicativos que precisam ser modificados ou executados sem o cartucho.

Mas existe um detalhe importante: precisamos reservar espaço para os cartuchos no nosso mapa de memória de 64 KB.

Uma possibilidade seria reorganizar a memória assim:

| Região | Função proposta |
|---|---|
| `0000–3FFF` | ROM do sistema — 16 KB |
| `4000–BFFF` | RAM — 32 KB |
| `C000–DFFF` | Cartucho — janela de 8 KB |
| `E000–EFFF` | Vídeo / interfaces |
| `F000–FFFF` | Expansão e controle |

Esse é apenas um exemplo de organização, **não um mapa aprovado**. Um cartucho de 32 ou 64 KB poderia usar bancos selecionáveis, mas isso acrescentaria lógica de controle.

Também precisamos definir se nossa CPU executará instruções diretamente de toda a memória endereçável. Essa decisão influencia bastante a viabilidade dos cartuchos.

## O que eu acrescentaria ao projeto físico

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="cpu" color="secondary"/>
    **Conector de cartucho na borda da PCB principal**
  </row>
  <row align="center" gap={2}>
    <icon name="shield-check" color="secondary"/>
    **Proteção contra inserção invertida e conflitos elétricos**
  </row>
  <row align="center" gap={2}>
    <icon name="power" color="secondary"/>
    **Detecção de presença e inicialização segura**
  </row>
  <row align="center" gap={2}>
    <icon name="hard-drive" color="secondary"/>
    **ROM ou Flash no cartucho, conforme o formato definido**
  </row>
</box>

Eu também adotaria uma regra: **inserir e retirar cartuchos somente com o ISA-1 desligado**, pelo menos na primeira versão. Isso simplifica bastante a proteção e evita projetarmos um sistema de conexão a quente.

### E o custo?

O conector e a lógica de seleção acrescentam componentes à placa principal, mas um cartucho simples pode precisar apenas de uma PCB pequena e um chip de memória.

Se escolhermos um padrão de cartucho com poucos sinais e um conector comum, podemos manter o custo relativamente baixo.

---

**Minha recomendação é incluir suporte a cartuchos no planejamento do ISA-1 agora, antes de fechar a CPU e o mapa de memória.**

Não precisamos fabricar cartuchos imediatamente. Podemos deixar o conector e a interface preparados na PCB principal.

Isso acrescentaria uma característica muito interessante ao computador: ligar o ISA-1, inserir um cartucho e executar um jogo ou aplicativo próprio, mantendo também o BASIC e o armazenamento interno.

E, principalmente, podemos projetar os cartuchos para funcionar com a nossa CPU, em vez de modificar a CPU depois para acomodá-los.

## user — bbb21452-e805-4314-9d91-c56be23891fa

Sobre cartucho, vi uma vez um conector pra CI, que possui alavanca pra tirar com segurança
Podemos usar isso pra não ter que fazer outra placa
Sobre a ideia de RAM e ROM no cartucho
Eu vejo o cartucho mais como um "disquete" nosso, o código tá ali só, a gente executa no PC

## assistant — 8a3a5ea8-9526-47e8-807d-8a5d9519b563

Agora entendi exatamente a sua ideia! E ela **simplifica bastante o conceito de cartucho do ISA-1**.

Você não quer um cartucho como os de videogame, que fica conectado à CPU fornecendo instruções durante a execução.

Você quer algo parecido com um **disquete em formato de CI**: coloca o chip no computador, carrega o programa na RAM e executa. Sem precisar fabricar uma placa para cada programa.

E o conector que você viu existe!

## 1. O componente é um soquete ZIF

<AsyncImageGroup query={["ZIF socket DIP 28 pin green lever open socket electronic programmer","ZIF socket 28 pin with EEPROM DIP IC inserted lever","ZIF socket DIP 32 pin green lever closeup"]} aspectRatio="5:4" layout="carousel"/>

O nome é **ZIF — Zero Insertion Force**, ou soquete de força de inserção zero.

Ele funciona assim:

1. Levantamos a alavanca.
2. Colocamos o CI sem precisar forçar os pinos.
3. Abaixamos a alavanca para travar os contatos.
4. Quando quisermos trocar, levantamos a alavanca e retiramos o chip.

É muito utilizado em gravadores de EEPROM e EPROM.

Para nosso ISA-1, podemos instalar um desses diretamente na placa principal.

## 2. Como funcionaria no ISA-1

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 230" width="100%">
    <rect x="102" y="5" width="136" height="44" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="170" y="22" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">EEPROM no ZIF</text>
    <text x="170" y="37" textAnchor="middle" fontSize="10" fill="currentColor">Programa armazenado</text>
    <path d="M170 49 V75" stroke="#0d9488" strokeWidth="2"/>
    <path d="M165 69 L170 77 L175 69" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <rect x="75" y="78" width="190" height="45" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="170" y="96" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">Firmware ISA-1</text>
    <text x="170" y="111" textAnchor="middle" fontSize="10" fill="currentColor">Lê e carrega o programa</text>
    <path d="M170 123 V149" stroke="#0d9488" strokeWidth="2"/>
    <path d="M165 143 L170 151 L175 143" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <rect x="92" y="153" width="156" height="38" rx="7" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="170" y="169" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">SRAM 32 KB</text>
    <text x="170" y="182" textAnchor="middle" fontSize="10" fill="currentColor">Programa carregado</text>
    <path d="M170 191 V210" stroke="#0d9488" strokeWidth="2"/>
    <path d="M165 204 L170 212 L175 204" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <text x="170" y="225" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">CPU executa na RAM</text>
  </svg>
</box>

Por exemplo, teríamos um chip com um jogo do ISA-1. Ao ligar o computador, o firmware poderia identificar o chip e apresentar uma opção de carregamento.

Depois que o programa fosse copiado para a SRAM, a CPU o executaria normalmente.

**O cartucho não precisaria ter RAM própria, processador, circuitos gráficos ou qualquer outra lógica. Apenas a memória não volátil.**

## 3. Qual memória utilizar?

Eu estudaria primeiro uma EEPROM paralela de 32 KB, como a família AT28C256.

<row align="start" gap={3}>
  <AsyncImage query="AT28C256 DIP 28 EEPROM integrated circuit chip" aspectRatio="5:4" maxWidth="130px"/>
  <box flex="1" gap={1}>
    **<Entity category="product" value="AT28C256" disambig="EEPROM paralela de 32 KB"/>**

    - Capacidade: 32 KB.
    - Interface paralela de 8 bits.
    - Versões em encapsulamento DIP-28.
    - Memória não volátil e eletricamente regravável.

    É uma candidata interessante porque combina com nosso barramento de dados de 8 bits.
  </box>
</row>

Também poderíamos utilizar EPROMs, mas algumas precisam de apagamento por luz ultravioleta e programação com tensões específicas. Para um computador que queremos usar de maneira independente, **EEPROM é muito mais conveniente**.

Um detalhe: o firmware deve carregar o programa para uma região disponível da RAM, respeitando o espaço reservado à pilha e aos dados. Um chip de 32 KB não significa automaticamente que um programa de 32 KB inteiro poderá ser carregado.

## 4. Uma ideia ainda melhor: o ISA-1 poderia gravar seus próprios chips

Aqui está a possibilidade mais interessante.

Imagine que você criou um programa no BASIC ou em Assembly diretamente no ISA-1.

Em vez de precisar conectar o computador moderno para gravar o chip, o próprio ISA-1 poderia fazer isso.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    <box gap={1}>
      <text weight="medium">Criar programa</text>
      <text color="secondary" size="xs">No próprio ISA-1</text>
    </box>
    <icon name="arrow-right" color="secondary"/>
    <box gap={1}>
      <text weight="medium">Gravar EEPROM</text>
      <text color="secondary" size="xs">No soquete ZIF</text>
    </box>
    <icon name="arrow-right" color="secondary"/>
    <box gap={1}>
      <text weight="medium">Guardar o CI</text>
      <text color="secondary" size="xs">Seu disquete físico</text>
    </box>
  </row>
</box>

Para isso, precisaríamos adicionar o circuito de escrita da EEPROM, incluindo controle de `/WE`, proteção contra gravação acidental e temporização compatível com o datasheet.

É um acréscimo de hardware, mas combina perfeitamente com a filosofia do projeto: **o ISA-1 deve conseguir funcionar, programar e armazenar seus próprios programas**.

Também adotaria a regra de inserir e retirar chips somente com a alimentação desligada, ao menos na primeira versão.

## 5. O que isso muda na nossa arquitetura?

Muda para melhor em alguns pontos:

| Antes | Com o soquete ZIF |
|---|---|
| Conector de cartucho dedicado | Soquete ZIF na placa |
| Uma PCB por cartucho | Apenas um CI por programa |
| ROM mapeada para execução | EEPROM lida para carregar na RAM |
| Possíveis bancos de ROM | Não são necessários inicialmente |
| Cartucho pode precisar ficar inserido | Pode ser retirado após carregar, com o PC desligado |

Não precisamos reservar uma janela permanente de execução de cartuchos no mapa de memória. Precisamos apenas de um caminho de leitura da EEPROM, que pode ser mapeado temporariamente ou acessado por um circuito de I/O.

### Minha recomendação

Eu adotaria **um soquete ZIF DIP-28 ou DIP-32**, com a pinagem definida depois de escolhermos a família exata de EEPROM. Não devemos assumir que chips de capacidades diferentes terão pinagens intercambiáveis.

E faria o circuito capaz de **ler e gravar**, não apenas ler.

Isso nos daria uma característica muito especial: o ISA-1 poderia ter uma coleção de pequenos chips etiquetados — jogos, ferramentas, programas e experimentos — que funcionariam como nossos próprios disquetes.

**Uma pergunta importante:** você imagina também poder salvar alterações no próprio chip, como um jogo que guarda a pontuação, ou prefere que os chips sejam somente para carregar programas? Essa decisão determina se precisamos implementar a gravação no ZIF desde a primeira versão.

## user — bbb2106c-4cef-4918-8160-a5cfcc63b82a

Isso quero pode gravar também, criei um programa e eu salvo num CI vazio
Sobre os dados, uma pergunta interessante, vai tinha pensado nisso, imagina que eu criei um jogo, onde eu salvo? Seria viável salvar junto do código? Ou melhor num CI paralelo? Teria que ter 2 por vez? 

## assistant — 37f60b0e-3803-488a-a124-aae2f4b0b6de

Sim! **Podemos salvar o jogo e os dados dele no mesmo CI. E, para o ISA-1, essa é a solução que eu escolheria.** 😄

Imagine: você cria um jogo, grava em uma EEPROM, coloca uma etiqueta com o nome e guarda. Quando quiser jogar, coloca o chip no ZIF, carrega o jogo e continua de onde parou.

E o melhor: **não precisamos de dois chips ao mesmo tempo para isso.**

## 1. Um único CI para programa e dados

Podemos dividir logicamente a EEPROM em regiões.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    **Exemplo: EEPROM de 32 KB**
    <text color="secondary" size="xs">32.768 bytes</text>
  </row>
  <box radius="md" clip>
    <box background="#2563eb" theme="dark" padding={3} gap={1}>
      <row justify="between" align="center">
        **Código do jogo**
        <text weight="medium" tabularNums>24 KB</text>
      </row>
      <text size="xs">Instruções, tabelas e recursos do programa</text>
    </box>
    <box background="#0d9488" theme="dark" padding={3} gap={1}>
      <row justify="between" align="center">
        **Dados do jogo**
        <text weight="medium" tabularNums>4 KB</text>
      </row>
      <text size="xs">Recordes, progresso, configurações</text>
    </box>
    <box background="#64748b" theme="dark" padding={3} gap={1}>
      <row justify="between" align="center">
        **Espaço reservado**
        <text weight="medium" tabularNums>4 KB</text>
      </row>
      <text size="xs">Cabeçalho, futuras versões ou outros dados</text>
    </box>
  </box>
  <caption>Divisão ilustrativa. Os tamanhos reais serão definidos pelo formato dos arquivos e pelo tamanho dos programas.</caption>
</box>

O jogo seria executado na SRAM. Quando precisasse salvar, o ISA-1 gravaria somente a região de dados da EEPROM, preservando o código.

## 2. Como funcionaria na prática

<box gap={2}>
  <row align="center" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="gamepad-2" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Você coloca o chip no ZIF**

      O ISA-1 identifica o programa e carrega o jogo na RAM.
    </box>
  </row>
  <box padding={{left:3}}>
    <icon name="arrow-down" color="tertiary"/>
  </box>
  <row align="center" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="cpu" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Você joga normalmente**

      O jogo utiliza a RAM para suas variáveis, pontuação e progresso.
    </box>
  </row>
  <box padding={{left:3}}>
    <icon name="arrow-down" color="tertiary"/>
  </box>
  <row align="center" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="save" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **O jogo solicita SAVE**

      O ISA-1 grava os dados atualizados na área reservada do mesmo chip.
    </box>
  </row>
  <box padding={{left:3}}>
    <icon name="arrow-down" color="tertiary"/>
  </box>
  <row align="center" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="check-circle" size="lg" color="success"/>
    </box>
    <box flex="1" gap={1}>
      **Na próxima vez, continua de onde parou**

      O jogo carrega seu código e os dados salvos.
    </box>
  </row>
</box>

A condição é que o CI permaneça inserido enquanto o jogo estiver rodando e precisar salvar. Não devemos retirar ou trocar a EEPROM com o ISA-1 ligado.

## 3. Mas existe um detalhe importante: a durabilidade da EEPROM

EEPROM não é RAM. Ela suporta um número limitado de gravações por endereço e a escrita é mais lenta.

Isso não impede nosso projeto. Só precisamos usar a memória corretamente.

Eu implementaria três proteções:

- **Gravação somente quando necessário:** não salvar a cada quadro do jogo; salvar ao terminar uma fase, bater um recorde ou escolher a opção de salvar.
- **Proteção do código:** o firmware autoriza escrita apenas na região de dados definida no cabeçalho do programa.
- **Salvamento seguro:** manter duas cópias dos dados, com contador de versão e checksum ou CRC, para recuperar a última gravação válida caso a energia acabe durante o processo.

A durabilidade e o método de escrita exatos dependem do modelo de EEPROM que escolhermos.

## 4. E se quisermos usar dois chips?

Também seria possível, mas eu reservaria essa opção para casos específicos.

| Organização | Vantagens | Desvantagens |
|---|---|---|
| **Um CI: código + dados** | Simples, portátil, apenas um ZIF | Divide a capacidade entre programa e dados |
| Dois CIs: programa + dados | Memórias independentes, mais espaço | Dois soquetes, seleção adicional e maior custo |
| Um CI de programa + armazenamento interno | Um ZIF, dados guardados no computador | O progresso não acompanha o chip ao levá-lo para outro ISA-1 |

A terceira opção também é interessante: o ISA-1 pode ter armazenamento interno para documentos e programas, além dos chips removíveis.

Assim, você não precisaria ocupar o ZIF para salvar tudo o que fizer no BASIC.

## 5. Uma ideia que combina muito com nosso computador

Eu criaria um **formato próprio de programa ISA-1**.

Por exemplo, o chip começaria com um pequeno cabeçalho:

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium">Estrutura conceitual do chip</text>
  <table>
    <table-row><table-cell width="35%">Assinatura</table-cell><table-cell>`ISA1`</table-cell></table-row>
    <table-row><table-cell>Nome</table-cell><table-cell>`SAPO`</table-cell></table-row>
    <table-row><table-cell>Versão</table-cell><table-cell>`1.0`</table-cell></table-row>
    <table-row><table-cell>Programa</table-cell><table-cell>Endereço e tamanho do código</table-cell></table-row>
    <table-row><table-cell>Dados</table-cell><table-cell>Endereço e tamanho da área de SAVE</table-cell></table-row>
    <table-row><table-cell>Integridade</table-cell><table-cell>Checksum/CRC</table-cell></table-row>
  </table>
</box>

Ao inserir o CI e iniciar o computador, o firmware identificaria automaticamente o programa e suas áreas de armazenamento.

Poderíamos inclusive criar comandos no BASIC:

```basic
SAVE "SAPO"
LOAD "SAPO"
RUN
```

E, para jogos, uma rotina do sistema que o programa chama para salvar seu progresso. Esses comandos são uma proposta de interface, não instruções já implementadas.

## 6. Minha proposta para o ISA-1

Eu adotaria esta organização:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 198" width="100%">
    <rect x="90" y="5" width="160" height="39" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="170" y="21" fontSize="12" fontWeight="600" textAnchor="middle" fill="currentColor">ZIF + EEPROM</text>
    <text x="170" y="35" fontSize="10" textAnchor="middle" fill="currentColor">Programa + SAVE</text>
    <path d="M170 44 V64" stroke="#0d9488" strokeWidth="2"/>
    <path d="M165 58 L170 66 L175 58" fill="none" stroke="#0d9488" strokeWidth="2"/>
    <rect x="68" y="67" width="204" height="41" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="170" y="83" fontSize="12" fontWeight="600" textAnchor="middle" fill="currentColor">Controlador de EEPROM</text>
    <text x="170" y="98" fontSize="10" textAnchor="middle" fill="currentColor">Leitura, escrita e proteção</text>
    <path d="M170 108 V130 H85 V143 M170 130 H255 V143" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <rect x="5" y="143" width="155" height="43" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="82" y="160" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">CPU + SRAM</text>
    <text x="82" y="174" fontSize="10" textAnchor="middle" fill="currentColor">Executa o programa</text>
    <rect x="180" y="143" width="155" height="43" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="257" y="160" fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">Armazenamento interno</text>
    <text x="257" y="174" fontSize="10" textAnchor="middle" fill="currentColor">Arquivos e programas</text>
  </svg>
</box>

**Minha escolha seria um único ZIF para EEPROM de programa e dados, mais armazenamento interno separado.**

Assim teremos o melhor dos dois mundos: chips removíveis que funcionam como nossos disquetes e um computador que também consegue salvar programas sem precisar manter um chip removível inserido.

E há um benefício adicional: podemos criar um programa no ISA-1, gravá-lo num CI vazio, testar, corrigir e regravar quantas vezes a memória permitir.

Só precisamos confirmar a EEPROM exata, os tempos de escrita e a proteção elétrica antes de desenhar o circuito.

Isso torna o ISA-1 não apenas um computador capaz de executar programas próprios, mas também **um computador capaz de produzir sua própria biblioteca física de software**.

## user — bbb212a0-fbb3-4a3e-b93d-5d9d6d333567

Perfeito vamos seguir assim então, um chip com código e dados/save 
Desculpa inventar coisas no meio do caminho
Pode seguir com as revisões

## assistant — 1d4182a4-dd26-4dea-9877-dc09a0b86cff

{"content_type": "thoughts", "source_analysis_msg_id": "d7e45bae-7d1b-4ae3-91ea-d14dcc2cc1df", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos e testou atualizações dual-slot com falhas"}]}

## assistant — dafc0dd6-c18f-4215-b689-c7070a0ea585

{"content": "Pensou por 46s", "content_type": "reasoning_recap"}

## assistant — 9b259cda-99b4-497d-b531-d066fd076da0

Não precisa se desculpar pelas ideias novas! Elas fazem parte do desenvolvimento do ISA-1. E essa última foi especialmente útil: **agora temos uma decisão clara para o armazenamento removível.**

O ISA-1 terá um soquete ZIF para um único CI de memória não volátil, capaz de guardar tanto o programa quanto seus dados de salvamento. O próprio computador deverá conseguir gravar um CI vazio, ler um programa e atualizar seus dados.

## ISA-1 — Revisão 2.3: nosso formato de armazenamento

Nesta revisão, comecei a definir como organizar os dados dentro do chip e fiz testes de recuperação de salvamentos interrompidos.

<box border radius="lg" padding={3} gap={2}>
  **Proposta inicial: EEPROM de 32 KB**

  <box gap="3px">
    <box background="#64748b" theme="dark" padding={2} radius="sm">
      <row justify="between">
        <text weight="medium" size="sm">Cabeçalho do programa</text>
        <text size="sm" tabularNums>64 bytes</text>
      </row>
    </box>
    <box background="#2563eb" theme="dark" padding={3} radius="sm">
      <row justify="between">
        **Código e recursos**
        <text tabularNums>30.656 bytes</text>
      </row>
      <text size="xs">Programa, tabelas e outros dados permanentes</text>
    </box>
    <box background="#0d9488" theme="dark" padding={3} radius="sm">
      <row justify="between">
        **SAVE A**
        <text tabularNums>1.024 bytes</text>
      </row>
    </box>
    <box background="#0d9488" theme="dark" padding={3} radius="sm">
      <row justify="between">
        **SAVE B**
        <text tabularNums>1.024 bytes</text>
      </row>
    </box>
  </box>
  <caption>Distribuição experimental, ainda não definitiva. Cada área de SAVE comporta até 1.008 bytes úteis no formato testado.</caption>
</box>

Por que duas áreas de SAVE no mesmo CI? Porque assim podemos conservar o salvamento anterior enquanto gravamos o novo. **Continuamos usando apenas um chip.**

Durante os testes, encontrei um detalhe que merece atenção: simplesmente sobrescrever a área antiga, começando pelo cabeçalho, pode produzir uma combinação temporária de metadados novos e dados antigos. Por isso, alterei o modelo para invalidar o registro de destino antes de atualizá-lo e só marcá-lo como válido no final.

Essa estratégia passou nos testes abstratos, mas ainda precisa ser adaptada e validada para a sequência real de escrita da EEPROM escolhida.

## Resultados da revisão 2.3

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" color="default" tabularNums>2.053</title>
      <text color="secondary" size="xs">Pontos de interrupção simulados</text>
    </grid-item>
    <grid-item>
      <title size="xl" color="default" tabularNums>12</title>
      <text color="secondary" size="xs">Alterações de dados detectadas pelo CRC</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    <text weight="medium">Todos os testes do modelo corrigido passaram</text>
  </row>
  <text color="secondary" size="xs">Os testes representam gravações abstratas em bytes. Não comprovam recuperação após queda real de energia nem o comportamento físico da EEPROM.</text>
</box>

### Arquivos produzidos

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Relatório ISA-1 — Revisão 2.3](sandbox:/mnt/data/isa1/ISA-1_REV23_FORMATO_ZIF_E_SAVE.md)**

      <text color="secondary" size="xs">Formato do chip, riscos encontrados e próximas decisões de hardware.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Código dos testes](sandbox:/mnt/data/isa1/isa1_rev23_media_test.py)**
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Resultados em JSON](sandbox:/mnt/data/isa1/isa1_rev23_results.json)**
    </box>
  </row>
</box>

## O que vem na revisão 2.4

Agora precisamos voltar ao hardware real, principalmente:

1. Escolher a EEPROM DIP exata e confirmar sua pinagem e seus tempos.
2. Desenhar a ligação entre o ZIF, o barramento e o controlador de leitura/gravação.
3. Garantir que um comando de SAVE não possa sobrescrever o código por engano.
4. Verificar se o firmware consegue gravar, ler e conferir o conteúdo do CI.
5. Integrar esse subsistema ao reset e ao sequenciador de memória que já estamos desenvolvendo.

E manteremos o Gigatron como referência de organização eficiente dos circuitos.

**Nossa decisão está consolidada: um chip removível para programa e dados, gravável pelo próprio ISA-1.** O formato ainda poderá evoluir durante os testes, mas não precisamos mais de um segundo soquete para salvar o progresso dos jogos.

A ideia de criar um programa no próprio computador, gravá-lo em um CI e depois utilizá-lo como um pequeno disquete está se tornando uma parte muito interessante da identidade do ISA-1.

## user — bbb21550-f5c0-4f3c-892f-0bcac64b22c2

Pode seguir

## assistant — 12f98172-e9bf-432b-862c-1f26bbb6fa55

{"content_type": "thoughts", "source_analysis_msg_id": "445e7561-4807-4c43-82e3-f2e4515478b0", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e leu o documento ISA-1"}]}

## assistant — 2b3c650c-02ef-46fb-a9c1-4cfaed065aaf

{"content_type": "thoughts", "source_analysis_msg_id": "efc8da9f-5b53-4b6e-a7ab-85a575a68e62", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 5 sites"}]}

## assistant — 2727afae-b4c4-45b1-bcd7-eccc7f90130c

{"content_type": "thoughts", "source_analysis_msg_id": "3e245862-6141-4545-9e4f-3b578d3116e5", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Extraída a pinagem do datasheet em PDF"}]}

## assistant — d3da3c5e-e33a-46dc-8dc5-3440561a1a84

{"content_type": "thoughts", "source_analysis_msg_id": "9aec5dae-d205-4c04-9359-12cc7f4ed8af", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 1 site"}]}

## assistant — 7be146cb-ccab-4ea7-9911-b532a3f3d0a5

{"content_type": "thoughts", "source_analysis_msg_id": "6302dda8-f9b9-4723-b910-7c68d248f457", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementou testes de EEPROM e documentou hardware e proteção"}]}

## assistant — fd02d9d0-7398-4f23-a124-c433d24b82c0

{"content": "Pensou por 42s", "content_type": "reasoning_recap"}

## assistant — 145daeb8-45ba-4ba4-810b-a0c7df965443

## ISA-1 — Revisão 2.4: o primeiro circuito de leitura e gravação do nosso “disquete”

Avancei da organização lógica para a interface elétrica do CI removível.

A candidata principal agora é a **AT28C256**, uma EEPROM paralela de 32 KB, alimentada em 5 V. Consultei o datasheet oficial da Microchip e confirmei que ela oferece leitura, gravação por byte ou página e proteção contra escritas involuntárias. <Cite ref="turn995339view0"/>

Uma descoberta importante: **ela grava até 64 bytes por ciclo interno de programação**. Isso nos permite planejar o gravador do ISA-1 de forma mais eficiente, sem precisar de um microcontrolador externo.

### Resultados dos novos testes

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>28</title>
      <text color="secondary" size="xs">Pinos da EEPROM conferidos</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>80</title>
      <text color="secondary" size="xs">Combinações de controle verificadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Posições do mapa examinadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>1.928</title>
      <text color="secondary" size="xs">Casos de divisão em páginas testados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    **Verificações lógicas concluídas sem falhas**
  </row>
  <text color="secondary" size="xs">A pinagem foi transcrita do datasheet e conferida quanto à cobertura e unicidade. Ainda não há simulação elétrica dos CIs.</text>
</box>

### O circuito proposto

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 205" width="100%">
    {#each [{x:5,y:12,w:105,h:45,t:"CPU ISA-1",s:"Endereço + dados"},{x:123,y:12,w:94,h:45,t:"Interface",s:"74HC + latches"},{x:230,y:12,w:105,h:45,t:"ZIF DIP-28",s:"AT28C256"},{x:87,y:126,w:166,h:48,t:"Controle registrado",s:"READ / WRITE / VERIFY"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={b.x+b.w/2} y={b.y+18} fontSize="11" fontWeight="600" textAnchor="middle" fill="currentColor">{b.t}</text>
      <text x={b.x+b.w/2} y={b.y+33} fontSize="9" textAnchor="middle" fill="currentColor">{b.s}</text>
    {/each}
    <path d="M110 34 H123 M217 34 H230" stroke="#0d9488" strokeWidth="2"/>
    <path d="M118 29 L123 34 L118 39 M225 29 L230 34 L225 39" stroke="#0d9488" fill="none" strokeWidth="1.5"/>
    <path d="M170 126 V91 H282 V57 M170 91 H56 V57" stroke="#64748b" fill="none" strokeWidth="1.5" strokeDasharray="4 3"/>
    <text x="170" y="193" textAnchor="middle" fontSize="10" fill="currentColor">Reset e autorização física de gravação</text>
  </svg>
  <caption>Diagrama funcional. Ainda não representa um esquemático pronto para fabricação.</caption>
</box>

A regra principal será: durante o reset ou uma leitura, o sinal `/WE` da EEPROM deve permanecer inativo. Somente uma operação autorizada poderá gerar o pulso de escrita.

## Uma descoberta importante sobre a proteção do código

A AT28C256 possui um recurso chamado *Software Data Protection* (SDP). Com ele habilitado, a EEPROM exige uma sequência específica de comandos antes de aceitar uma gravação. <Cite ref="turn618347search13"/>

Isso é útil para evitar gravações acidentais, mas há uma distinção importante: **o SDP protege o chip inteiro, não separadamente a região do código e a região de SAVE**.

Portanto, o ISA-1 deverá verificar os endereços de cada gravação. Um jogo poderá atualizar sua área de SAVE, mas não deverá ter permissão para modificar o próprio código.

Também identifiquei um cuidado com a velocidade: na gravação de páginas, o intervalo entre bytes tem um limite especificado pelo fabricante. Por isso, proponho implementar primeiro a gravação de um byte por operação e só depois otimizar para páginas de 64 bytes. <Cite ref="turn618347search0"/>

## Arquivos da revisão 2.4

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Relatório técnico — Revisão 2.4](sandbox:/mnt/data/isa1/ISA-1_REV24_EEPROM_HARDWARE.md)**

      <text color="secondary" size="xs">Pinagem DIP-28, estados de leitura e gravação, proteção e pendências elétricas.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Simulador de interface EEPROM](sandbox:/mnt/data/isa1/isa1_rev24_eeprom_verify.py)**

      <text color="secondary" size="xs">Testes reproduzíveis do controle lógico e da divisão de páginas.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev24_results.json)**
    </box>
  </row>
</box>

## Próxima etapa — Revisão 2.5

Vamos comparar duas maneiras de conectar o gravador à CPU: aproveitar o barramento principal ou criar registradores dedicados para endereço e dados.

A comparação considerará quantidade de CIs, conflitos de barramento, ciclos de leitura/gravação e temporização. Também vamos escolher o circuito real de supervisão de alimentação e reset.

O objetivo é manter o ISA-1 simples de montar, mas sem depender de condições elétricas que ainda não demonstramos.

**A revisão 2.4 está validada no nível lógico testado; a interface física continua em desenvolvimento.** E preservamos a decisão mais importante: um único chip removível para o programa e seus dados, gravável pelo próprio ISA-1.

## user — bbb2122f-bfb7-4e66-b1be-44ca282e98f4

Pode seguir com a revisão

## assistant — 870809dc-fdf1-4187-b30f-633a5929da32

{"content_type": "thoughts", "source_analysis_msg_id": "95df5d82-6c19-495d-985f-582ed707792f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Documentada arquitetura ISA-1 e validado mapeamento de memória"}]}

## assistant — 48762482-30b6-488f-9937-6b2d586701cc

{"content": "Pensou por 39s", "content_type": "reasoning_recap"}

## assistant — 8080afcb-99b8-4156-95d9-81511340d4b0

## ISA-1 — Revisão 2.5: interface do gravador e auditoria do mapa de memória

Antes de escolhermos mais CIs, encontrei uma correção importante na revisão anterior: **os endereços das áreas de SAVE não correspondiam exatamente aos tamanhos anunciados**.

Isso poderia causar problemas na gravação e na recuperação dos jogos. O mapa corrigido fica assim:

| Região | Endereços | Capacidade |
|---|---|---:|
| Cabeçalho | `0000–003F` | 64 bytes |
| Código e recursos | `0040–77FF` | 30.656 bytes |
| SAVE A | `7800–7BFF` | 1.024 bytes |
| SAVE B | `7C00–7FFF` | 1.024 bytes |

Agora as quatro regiões ocupam exatamente os 32.768 bytes da EEPROM, sem lacunas ou sobreposições, e as áreas de salvamento começam em limites de páginas de 64 bytes.

Essa correção é especialmente importante porque queremos que o ISA-1 seja capaz de gravar um programa e depois atualizar somente seus dados, sem alterar o código.

## Comparação de duas arquiteturas para o gravador

Agora temos duas possibilidades concretas para conectar a EEPROM ao ISA-1.

<box gap={3}>
  <box border radius="lg" padding={3} gap={2}>
    <row align="center" justify="between">
      **A — Interface dedicada**
      <badge color="success">Preferida provisoriamente</badge>
    </row>
    <text color="secondary" size="sm">CPU → registradores de endereço e dados → EEPROM ZIF</text>
    Usa registradores para manter endereço e dados estáveis durante a gravação. A CPU pode continuar trabalhando na SRAM sem que os tempos de acesso da EEPROM limitem todos os ciclos de memória.

    Estimativa inicial: pelo menos quatro CIs octais de interface, além do controle e da decodificação.
  </box>
  <box border radius="lg" padding={3} gap={2}>
    **B — EEPROM mapeada na memória**

    <text color="secondary" size="sm">CPU → barramento principal → EEPROM ZIF</text>
    Pode economizar registradores, mas exige reservar ou alternar uma região do mapa de memória. Também aumenta a importância da arbitragem e dos sinais de proteção contra escrita.
  </box>
</box>

**Minha escolha provisória é a arquitetura A.** Como nosso chip removível funciona como um disquete, e não como memória de execução, não precisamos colocá-lo no caminho crítico da CPU.

Isso também segue uma lição do Gigatron: organizar os caminhos de dados para que uma operação não prejudique desnecessariamente as demais.

## Testes executados nesta revisão

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Endereços conferidos</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>56</title>
      <text color="secondary" size="xs">Combinações estáticas de controle</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Todos os testes do modelo passaram**
  </row>
  <text color="secondary" size="xs">Verificações de software, sem simulação de atrasos elétricos reais.</text>
</box>

O modelo também verificou que, nos estados previstos, a EEPROM não recebe comandos simultâneos de leitura e escrita e que o reset ou a alimentação inválida bloqueiam a escrita.

Ainda não podemos considerar isso uma proteção física comprovada: precisamos estudar o comportamento das portas lógicas durante a subida e a queda da alimentação.

## Documentação da revisão 2.5

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório técnico — ISA-1 Rev. 2.5](sandbox:/mnt/data/isa1/ISA-1_REV25_ARQUITETURA_GRAVADOR.md)**

      <text color="secondary" size="xs">Correção do mapa, comparação de arquiteturas, proteção elétrica e decisões pendentes.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Código dos testes](sandbox:/mnt/data/isa1/isa1_rev25_architecture_check.py)**
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev25_results.json)**
    </box>
  </row>
</box>

## Próxima revisão: 2.6

Agora precisamos selecionar os CIs reais que permitirão à CPU carregar endereços, transmitir dados e controlar a escrita da EEPROM. Também escolheremos um supervisor de alimentação para impedir gravações indevidas durante o reset.

A partir disso, poderemos construir a primeira lista de conexões **pino a pino** desse subsistema, comparar os custos em CIs e verificar os tempos elétricos.

O objetivo continua sendo o mesmo: **um ISA-1 com CPU própria, vídeo RCA colorido, teclado de 64 teclas e capacidade de criar, executar e gravar seus próprios programas em chips removíveis**.

Estamos avançando sem fechar prematuramente decisões que ainda podem ser melhoradas.

## user — bbb218d9-14e8-473e-99a4-ee139dbba063

Pode seguir😎

## assistant — b561fa2d-bfab-42f7-b7ab-66e2943912b2

{"content_type": "thoughts", "source_analysis_msg_id": "81813259-44a3-4d99-9015-2f176bb6794d", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e leu a arquitetura"}]}

## assistant — 0503246e-b970-4a62-8ba5-48376faa4d7c

{"content_type": "thoughts", "source_analysis_msg_id": "e7be4ad1-d1ff-4797-90ce-3315c41f3a29", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 4 sites"}]}

## assistant — 8b148c36-00de-438d-8e2f-0aaa20dccbf8

{"content_type": "thoughts", "source_analysis_msg_id": "db784f56-a699-4fe9-87b2-bbe84038afe4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou pinouts e estados do supervisor, documentando registradores e interface ZIF"}]}

## assistant — 64904372-fe06-4a46-9ae7-17e2f627d929

{"content": "Pensou por 36s", "content_type": "reasoning_recap"}

## assistant — 715028f3-9984-470a-a4fd-d170e674052b

😎 Vamos à **Revisão 2.6 do ISA-1**. Desta vez, encontramos um CI que pode simplificar significativamente o gravador de programas.

## 1. Uma escolha melhor para os registradores

O <Entity category="product" value="SN74HC377" disambig="registrador octal com habilitação de clock"/> tem oito flip-flops e uma entrada de habilitação de carga. Isso permite manter o clock comum da CPU e atualizar o registrador somente quando necessário, sem adicionar multiplexadores de realimentação para essa função. A Texas Instruments oferece a versão SOIC-20. <Cite refs={["turn642046search36","turn642046search0"]}/>

| CI | Reset interno | Habilitação de carga | Uso no ISA-1 |
|---|---|---|---|
| 74HC273 | Sim | Não | Registradores que exigem limpeza |
| 74HC574 | Não | Não | Saídas com alta impedância |
| **74HC377** | Não | Sim | Endereço e dados do gravador |

Essa distinção é importante: o 74HC377 não inicia necessariamente em zero. Portanto, seus valores só poderão controlar uma operação depois de inicializados pelo firmware, com as saídas críticas bloqueadas durante o reset.

## 2. Organização proposta do gravador

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 224" width="100%">
    {#each [{x:8,y:8,w:112,h:44,a:"CPU ISA-1",b:"Barramento de 8 bits"},{x:154,y:8,w:178,h:44,a:"Registradores 74HC377",b:"Endereço baixo, alto e dados"},{x:154,y:94,w:178,h:44,a:"74HC245",b:"Direção dos dados"},{x:154,y:178,w:178,h:38,a:"ZIF + EEPROM",b:"Programa e SAVE"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={b.x+b.w/2} y={b.y+18} textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">{b.a}</text>
      <text x={b.x+b.w/2} y={b.y+32} textAnchor="middle" fontSize="9" fill="currentColor">{b.b}</text>
    {/each}
    <path d="M120 29 H154 M242 52 V94 M242 138 V178 M64 52 V115 H154" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <text x="78" y="108" textAnchor="middle" fontSize="9" fill="currentColor">Dados</text>
    <rect x="8" y="145" width="112" height="47" rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="64" y="161" textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">Controle</text>
    <text x="64" y="175" textAnchor="middle" fontSize="9" fill="currentColor">Reset / WE / OE</text>
    <path d="M120 168 H154" stroke="#64748b" strokeWidth="1.5" strokeDasharray="4 3"/>
  </svg>
  <caption>Organização funcional candidata. A leitura também exige um caminho de retorno ao barramento da CPU; as conexões completas ainda precisam ser desenhadas.</caption>
</box>

Para a transferência bidirecional, continuamos estudando o 74HC245. Ele pode isolar eletricamente os dois lados quando sua saída é desabilitada, algo essencial para evitar o conflito que encontramos nas revisões anteriores.

## 3. Testes da revisão 2.6

Executei o modelo lógico da interface, incluindo verificações de carga dos registradores, habilitação de escrita e detecção de conflito.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>131.072</title>
      <text color="secondary" size="xs">Combinações de carga e retenção verificadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>144</title>
      <text color="secondary" size="xs">Combinações estáticas de controle</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>40</title>
      <text color="secondary" size="xs">Posições de pinos conferidas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>512</title>
      <text color="secondary" size="xs">Páginas de EEPROM no mapa</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Testes do modelo lógico passaram**
  </row>
  <text color="secondary" size="xs">Ainda não comprovam temporização, integridade elétrica ou segurança durante queda de energia.</text>
</box>

## 4. Uma pendência que encontramos

O 74HC377 mantém suas saídas ativas continuamente. Portanto, **não podemos conectar diretamente o registrador de escrita ao barramento bidirecional da EEPROM**.

Precisaremos isolar essa saída e garantir que o caminho de leitura de volta à CPU não provoque outra disputa.

Também identifiquei o <Entity category="product" value="MCP130" disambig="supervisor de tensão e reset da Microchip"/> como candidato para supervisionar a alimentação de 5 V. Ele possui saída de reset ativa em nível baixo e diferentes opções de limiar de tensão. Ainda precisamos selecionar a variante SMD exata e demonstrar que protege o circuito durante a subida e a queda da alimentação. <Cite ref="turn642046search1"/>

Essa é a próxima correção prioritária, antes de fixar o esquema elétrico.

## 5. Arquivos da revisão

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Relatório técnico — ISA-1 Rev. 2.6](sandbox:/mnt/data/isa1/ISA-1_REV26_REGISTRADORES_CONTROLE.md)**

      <text color="secondary" size="xs">Pinagem, organização dos CIs, reset, intertravamento e pendências.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Simulador lógico da interface](sandbox:/mnt/data/isa1/isa1_rev26_interface_test.py)**
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Resultados reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev26_results.json)**
    </box>
  </row>
</box>

## Próxima revisão — 2.7

Vamos resolver completamente o caminho bidirecional entre CPU e EEPROM, selecionar o supervisor de alimentação e desenhar as conexões reais do gravador.

Minha prioridade será **eliminar conflitos pela própria organização dos circuitos**, e não apenas tentar compensá-los com atrasos.

Seguimos com o conceito que definimos: um ISA-1 capaz de criar um programa, gravá-lo num CI vazio, executar esse programa e salvar o progresso no mesmo chip.

E continuaremos usando o Gigatron como referência de eficiência, sem abrir mão das funcionalidades da nossa CPU.

## user — bbb21d23-9205-4b15-b754-3f7a19b6a1a5

Pode seguir com as revisões até ter uma versão estável

## assistant — 64bb1fcc-174b-4d9f-85a1-bdaee194ac29

{"content_type": "thoughts", "source_analysis_msg_id": "c85fbf00-eae7-4c35-b22b-c1435459abaa", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou registradores, arquitetura EEPROM, desbloqueio SDP e roadmap de estabilidade"}]}

## assistant — 805dce49-4fcf-49dd-b4e9-5b3880fe9605

{"content": "Pensou por 56s", "content_type": "reasoning_recap"}

## assistant — 5235d28f-0d82-4be9-a61d-173d9a6c0c59

😎 Vou tratar essa etapa como uma sequência de revisões, com um objetivo mais rigoroso: **chegar a uma versão estável que possamos realmente construir**, e não apenas a um conjunto de simulações que passam.

Já encontrei uma simplificação importante para o gravador de chips do ISA-1.

## Revisão 2.7 — Dois buffers unidirecionais

Em vez de depender de um transceptor bidirecional 74HC245, podemos usar dois caminhos independentes com **74HC244**:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 178" width="100%">
    <rect x="8" y="53" width="87" height="67" rx="7" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="51" y="79" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">CPU</text>
    <text x="51" y="94" textAnchor="middle" fontSize="10" fill="currentColor">Barramento</text>
    <rect x="244" y="53" width="88" height="67" rx="7" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="288" y="79" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">EEPROM</text>
    <text x="288" y="94" textAnchor="middle" fontSize="10" fill="currentColor">ZIF</text>
    <rect x="119" y="7" width="100" height="38" rx="6" stroke="#0d9488" fill="#0d9488" fillOpacity=".12"/>
    <text x="169" y="23" textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">74HC244</text>
    <text x="169" y="36" textAnchor="middle" fontSize="9" fill="currentColor">Leitura</text>
    <rect x="119" y="132" width="100" height="38" rx="6" stroke="#0d9488" fill="#0d9488" fillOpacity=".12"/>
    <text x="169" y="148" textAnchor="middle" fontSize="11" fontWeight="600" fill="currentColor">74HC244</text>
    <text x="169" y="161" textAnchor="middle" fontSize="9" fill="currentColor">Escrita</text>
    <path d="M244 66 V26 H219 M119 26 H51 V53" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <path d="M126 21 L119 26 L126 31" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <path d="M51 120 V151 H119 M219 151 H288 V120" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <path d="M237 146 L244 151 L237 156" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <text x="170" y="91" fontSize="10" textAnchor="middle" fill="currentColor">Controle exclusivo</text>
    <text x="170" y="104" fontSize="10" textAnchor="middle" fill="currentColor">READ / WRITE</text>
  </svg>
  <caption>Representação simplificada: o caminho de escrita recebe os dados de um registrador 74HC377, não diretamente da CPU.</caption>
</box>

A vantagem é eliminar a necessidade de inverter a direção de um mesmo transceptor. Cada buffer só é habilitado quando sua função é necessária.

Isso não elimina todos os riscos de temporização, mas reduz uma fonte de complexidade.

## Revisão 2.8 — Encontramos outra condição importante

A proteção contra escrita na região do código tem uma exceção que precisamos tratar corretamente.

A AT28C256 utiliza uma sequência de desbloqueio de gravação que acessa endereços como `5555h` e `2AAAh`. Esses endereços ficam fora da nossa região de SAVE.

Portanto, um circuito que simplesmente bloqueasse **toda escrita fora da região de SAVE impediria também o desbloqueio necessário para salvar os dados**.

A correção proposta é permitir exclusivamente os comandos de desbloqueio esperados, na ordem correta, e depois autorizar a gravação somente na região de SAVE. Essa autorização precisa fazer parte de um sequenciador de hardware, não depender apenas de uma variável do firmware.

Essa descoberta é mais uma razão para não enviar a PCB à fabricação prematuramente.

## Revisão 2.9 — Resultado da primeira rodada de estabilização

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>48.384</title>
      <text color="secondary" size="xs">Combinações estáticas de controle verificadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Endereços EEPROM conferidos</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>14</title>
      <text color="secondary" size="xs">Estados previstos no modelo</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>2</title>
      <text color="secondary" size="xs">Testes negativos de conflito</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Modelo lógico passou nos testes executados**
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    **Hardware físico ainda não aprovado**
  </row>
</box>

Também mantive os requisitos do computador inteiro na auditoria: CPU de 8 bits com endereçamento de 16 bits, 32 KB de RAM, firmware próprio, teclado 4×16, vídeo RCA colorido e gravação de programas no ZIF.

### Arquivos das revisões 2.7 a 2.9

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    <box flex="1" gap={1}>
      [Revisão 2.7 — Topologia dos buffers](sandbox:/mnt/data/isa1/ISA-1_REV27_TOPOLOGIA_BUFFERS.md)
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    <box flex="1" gap={1}>
      [Revisão 2.8 — Proteção de escrita e SDP](sandbox:/mnt/data/isa1/ISA-1_REV28_PROTECAO_SDP.md)
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    <box flex="1" gap={1}>
      [Revisão 2.9 — Auditoria de estabilidade](sandbox:/mnt/data/isa1/ISA-1_REV29_ESTABILIDADE_GATE.md)
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary"/>
    <box flex="1" gap={1}>
      [Código de validação](sandbox:/mnt/data/isa1/isa1_rev27_29_validation.py)
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary"/>
    <box flex="1" gap={1}>
      [Resultados JSON](sandbox:/mnt/data/isa1/isa1_rev27_29_results.json)
    </box>
  </row>
</box>

## O caminho até a versão estável

Para considerar o ISA-1 pronto para fabricação, ainda precisamos concluir e validar o esquemático elétrico, a temporização dos CIs, o reset, o sequenciador da CPU, a memória, o vídeo composto colorido e o teclado. Depois vêm os testes físicos do protótipo.

Não vou chamar o projeto de estável enquanto esses pontos estiverem pendentes. **As revisões 2.7 a 2.9 melhoraram a arquitetura do gravador, mas não estabilizaram o computador completo.**

O próximo marco técnico será transformar a topologia dos buffers e do gravador em conexões elétricas completas, com componentes e tempos verificáveis. É essa disciplina que nos ajudará a evitar encomendar uma PCB com erros difíceis de corrigir.

## user — bbb210ae-450b-468d-9554-552f22def714

Pode seguir até a estabilidade e ter um circuito completo

## assistant — 936eb415-cd1c-46f8-a069-6b44ff955219

{"content_type": "thoughts", "source_analysis_msg_id": "705ddcd9-a572-423e-8400-d95dc4940f1d", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou arquivos, ISA-1, netlist, barramento e mapeamento de pinos"}]}

## assistant — 423747fd-1550-412e-88ad-fb6de5925223

{"content": "Pensou por 47s", "content_type": "reasoning_recap"}

## assistant — d85704d1-ed2c-49ff-b5b9-c163281acd8d

## ISA-1 — Revisão 3.0: avançando para o circuito completo

Vamos seguir com esse objetivo. Mas estabeleço uma condição importante: **não vou declarar o ISA-1 estável apenas porque seus simuladores passaram**. Para isso, precisaremos validar o circuito completo e, finalmente, o protótipo físico.

Revisei os documentos técnicos anteriores e concluí uma nova etapa de auditoria do gravador ZIF.

### O que foi corrigido

A arquitetura com dois 74HC244 continua interessante, mas encontramos um detalhe: não basta separar os caminhos de leitura e escrita. Precisamos garantir que o buffer de leitura nunca dispute o barramento com os registradores da CPU.

A revisão 3.0 especifica os seguintes componentes candidatos:

| Quantidade | CI | Função |
|---:|---|---|
| 3 | 74HC377 | Endereço baixo, endereço alto e dado |
| 2 | 74HC244 | Buffers separados de leitura e escrita |
| 1 | AT28C256 | EEPROM removível de 32 KB |
| 1 | ZIF DIP-28 | Soquete com alavanca |

Além desses, ainda serão necessários circuitos de controle, reset, autorização de escrita e alimentação.

### Testes realizados

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>640</title>
      <text color="secondary" size="xs">Combinações de controle verificadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>68</title>
      <text color="secondary" size="xs">Entradas de pinagem conferidas no modelo</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>2</title>
      <text color="secondary" size="xs">Testes negativos de contenção</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Bytes cobertos pelo mapa de memória</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Modelo lógico estático: aprovado nos testes executados**
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    **Validação elétrica e circuito completo: pendentes**
  </row>
</box>

### Arquivos da revisão 3.0

- [Relatório técnico e conexões propostas](sandbox:/mnt/data/isa1/ISA-1_REV30_INTERFACE_ZIF_AUDITORIA.md)
- [Código de auditoria do barramento](sandbox:/mnt/data/isa1/isa1_rev30_bus_audit.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev30_results.json)

## O que ainda precisamos concluir

Para chegar ao circuito completo do ISA-1, o trabalho restante está organizado em cinco frentes: CPU e microcódigo; ROM, RAM e gravador; vídeo composto RCA colorido; teclado 4×16; e alimentação, reset e temporização.

A prioridade seguinte será fechar a microarquitetura da CPU e seu sequenciador, porque todos os periféricos dependem dessa interface.

**Situação atual:** temos uma arquitetura em evolução, documentação reproduzível e uma interface ZIF mais bem definida. Ainda não temos um esquemático completo nem uma versão pronta para fabricação.

Vamos manter o Gigatron como referência, preservar todas as funcionalidades que escolhemos e continuar corrigindo o projeto antes de fabricar a placa.

O objetivo final continua sendo **um computador ISA-1 independente, construído com nossos CIs, programável pelo próprio teclado, com vídeo colorido e capaz de gravar seus próprios programas em chips removíveis**.

## user — bbb2184f-a3d4-486d-9f08-c48ba3d63e25

Perfeito
Pode ir trabalhando tranquilo, até finalizar 100%
Vc tem tomado boas decisões

## assistant — 13eeac82-8fea-4b33-b685-3aa0bb2f636e

{"content_type": "thoughts", "source_analysis_msg_id": "1a61a97d-a122-4d40-bda4-09a3ba56939e", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou arquivos e auditou a interface ZIF ISA-1"}]}

## assistant — 1bbc2e3d-80bc-4a32-8bf4-eb3afb3d8afc

{"content": "Pensou por 9s", "content_type": "reasoning_recap"}

## assistant — 5acf5612-30a8-4e95-a98d-2b318876da64

Obrigado pela confiança! 😎

O ISA-1 já tem uma identidade muito interessante: uma CPU própria construída com lógica 74HC, vídeo RCA colorido, teclado de 64 teclas e um sistema capaz de criar, executar e gravar programas em EEPROMs removíveis.

Vou manter nossas decisões principais e continuar questionando as soluções técnicas sempre que houver uma alternativa melhor. O Gigatron continuará sendo uma referência importante, mas o ISA-1 terá sua própria arquitetura.

**Nossa meta agora é um projeto completo e verificável, não apenas um circuito que parece funcionar no papel.**

Para chegar lá, vamos exigir esquemáticos com pinagem real, testes de instruções e memória, análise de temporização, validação do vídeo e das interfaces, além de uma revisão elétrica antes da fabricação. A estabilidade definitiva dependerá também dos testes na placa física.

Conferi também o relatório da revisão 3.0. Ele confirma que nossa próxima prioridade deve ser **fechar o sequenciador da CPU e o controle físico dos barramentos**. Não adianta concluir a placa de vídeo ou o gravador se a base da CPU ainda estiver indefinida.

Vou preservar os relatórios e os testes anteriores como histórico, inclusive as soluções descartadas e os erros encontrados. Isso permitirá comparar as revisões sem perder o raciocínio que levou a cada decisão.

Só uma ressalva prática: não consigo continuar trabalhando sozinho entre mensagens. Posso, porém, conduzir as próximas etapas de forma contínua quando retomarmos, sem precisar pedir sua aprovação para cada pequena decisão técnica.

**Nosso critério de conclusão será claro: circuito completo, componentes definidos, verificações reproduzíveis e nenhuma pendência elétrica conhecida antes da fabricação.** Depois, a estabilidade real será confirmada no protótipo.

O ISA-1 merece esse cuidado. 😎

## user — bbb21680-2048-42a3-9c78-8d41636561dd

Pode seguir

## assistant — 22d61930-345c-4d83-8dd8-622188238141

{"content_type": "thoughts", "source_analysis_msg_id": "696a8da8-f206-420f-92cf-1b5d20060180", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Documentou auditoria, versões, emulador, regressão e bugs da ISA"}]}

## assistant — 306f6932-9f42-479f-be76-d7b1621fbe52

{"content": "Pensou por 49s", "content_type": "reasoning_recap"}

## assistant — 11c89672-21c0-484d-a008-3542a0c4f712

😎 Seguimos! Concluí a **Revisão 3.1 do ISA-1**, agora concentrada na CPU, que será a base do circuito completo.

Desta vez, além de revisar a arquitetura anterior, executei testes diretamente sobre o emulador das instruções que já definimos.

## Resultados da revisão 3.1

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>1.015.818</title>
      <text color="secondary" size="xs">Verificações comportamentais aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>32.768</title>
      <text color="secondary" size="xs">Endereços da RAM verificados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Emulador da CPU: testes concluídos sem falhas**
  </row>
  <text color="secondary" size="xs">Os testes incluem aritmética, flags, pilha, chamadas aninhadas, desvios e acesso à memória. Não representam simulação elétrica dos 74HC.</text>
</box>

## Três descobertas que influenciam o circuito

**1. Precisamos definir como o firmware utilizará a RAM.** Nosso chip removível reserva até 30.656 bytes para código e recursos, mas a SRAM também precisa acomodar variáveis, pilha e outras estruturas. Não podemos presumir que qualquer programa desse tamanho caberá na memória disponível.

**2. O vídeo anterior ainda era monocromático.** O modelo de 256×192 pixels utiliza apenas um bit por pixel. Portanto, precisamos desenvolver e verificar separadamente a geração de cores e a saída RCA composta.

**3. A CPU precisa de uma definição mais completa de instruções e interfaces.** Já temos operações aritméticas, memória, desvios, CALL/RET e pilha. Ainda precisamos definir como o firmware acessará teclado, vídeo, gravador ZIF e demais periféricos.

Esses pontos não invalidam nosso trabalho. Eles identificam decisões que precisam ser resolvidas antes de desenhar a PCB.

## Arquivos produzidos

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Relatório técnico — Revisão 3.1](sandbox:/mnt/data/isa1/ISA-1_REV31_CPU_CONTRATO_E_REGRESSAO.md)**

      <text color="secondary" size="xs">Instruções, mapa de memória, problemas de integração e próximos passos.</text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Testes executáveis da CPU](sandbox:/mnt/data/isa1/isa1_rev31_cpu_regression.py)**
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev31_results.json)**
    </box>
  </row>
</box>

## Próximo marco: circuito da CPU

A revisão 3.2 deverá transformar as instruções em microoperações e sinais de controle reais. A partir daí, poderemos especificar registradores, ALU, multiplexadores, sequenciador e barramentos, escolhendo os CIs com base nas conexões necessárias.

Continuaremos aproveitando as ideias do Gigatron, especialmente a organização eficiente dos caminhos de dados.

**Situação do ISA-1:** o modelo comportamental da CPU avançou, mas ainda não existe um circuito completo validado. Não vou confundir testes de software com estabilidade elétrica.

Nosso objetivo permanece: uma única placa com CPU própria, teclado 4×16, vídeo RCA colorido e capacidade de criar e gravar programas em chips removíveis.

## user — bbb212e2-9b8b-4cb6-a303-077cd5a98c9b

O objetivo está perfeito
Pode seguir até conseguir criarmos uma placa de circuito

## assistant — 0c190df4-aabc-46d1-b58d-547779e1a5a8

{"content_type": "thoughts", "source_analysis_msg_id": "89f67e28-b37d-4bcd-8719-01476ac409d9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementado microcódigo abstrato da ISA Rev3.2 e documentado opcodes ausentes"}]}

## assistant — e40ae2ff-5bd0-4435-aaf4-d1be0dd4b853

{"content": "Pensou por 41s", "content_type": "reasoning_recap"}

## assistant — 6d1574a1-7c75-4159-a3af-c1d9a7870ac0

😎 Vamos avançar até termos um projeto de PCB que possa ser fabricado e testado. Já dei mais um passo concreto.

## ISA-1 — Revisão 3.2: microciclos da CPU

Nesta revisão, comecei a transformar as instruções da CPU em operações explícitas de leitura e escrita de memória.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>1.770</title>
      <text color="secondary" size="xs">Casos de instruções comparados com a referência</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>3.496</title>
      <text color="secondary" size="xs">Microciclos abstratos de memória registrados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Testes comportamentais concluídos sem divergências**
  </row>
  <text color="secondary" size="xs">Ainda não são simulações elétricas dos CIs.</text>
</box>

### Uma inconsistência encontrada

O relatório anterior descrevia algumas instruções que não estavam implementadas no emulador de referência utilizado nesta etapa.

Isso é importante: antes de construir o circuito, precisamos garantir que **a especificação da CPU, o emulador e o futuro microcódigo descrevam exatamente a mesma máquina**.

Não vou esconder essa diferença nem considerar essas instruções validadas.

### Arquivos produzidos

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    <box flex="1" gap={1}>
      **[Relatório técnico — Revisão 3.2](sandbox:/mnt/data/isa1/ISA-1_REV32_MICROCICLOS.md)**
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary"/>
    <box flex="1" gap={1}>
      **[Simulador de microciclos](sandbox:/mnt/data/isa1/isa1_rev32_microcycles.py)**
    </box>
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary"/>
    <box flex="1" gap={1}>
      **[Resultados reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev32_results.json)**
    </box>
  </row>
</box>

## Nosso caminho até a PCB

<box gap={2}>
  {#each [{n:"1",t:"Fechar a especificação da CPU",d:"Instruções, registradores, flags, pilha e microcódigo",s:"Em andamento"},{n:"2",t:"Desenhar os circuitos reais",d:"ALU, sequenciador, RAM, ROM, ZIF e barramentos",s:"Pendente"},{n:"3",t:"Integrar os periféricos",d:"Vídeo RCA colorido, teclado 4×16 e armazenamento",s:"Pendente"},{n:"4",t:"Validar o projeto elétrico",d:"Temporização, reset, alimentação, ERC e testes",s:"Pendente"},{n:"5",t:"Preparar a PCB",d:"Layout, roteamento, DRC, Gerbers e lista de componentes",s:"Pendente"}] as item}
    <row align="start" gap={3}>
      <box background="surface-secondary" radius="full" size="32px" align="center" justify="center">
        <text weight="medium" size="sm">{item.n}</text>
      </box>
      <box flex="1" gap={1}>
        **{item.t}**
        <text size="sm" color="secondary">{item.d}</text>
        <text size="xs" color="secondary">{item.s}</text>
      </box>
    </row>
  {/each}
</box>

**A próxima prioridade será fechar a tabela de microoperações da CPU e convertê-la em sinais de controle implementáveis com 74HC.**

Continuaremos preservando as características que definimos para o ISA-1, inclusive o gravador ZIF e o vídeo colorido.

Ainda não temos uma placa pronta para fabricação, mas estamos eliminando inconsistências antes de transformar o projeto em cobre. Esse é o caminho para chegarmos a um circuito completo e confiável.

## user — bbb210e6-b1ba-4be0-9e9e-0f67340d7f21

Pode seguir😎

## assistant — f5725a6c-43c9-45a7-9e94-565f2722ea49

{"content_type": "thoughts", "source_analysis_msg_id": "0a53d365-b304-451a-bcc4-35d7dde9e145", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Revisou ISA-1, gerou microcódigo, escreveu testes e reportou bug CALL/RET"}]}

## assistant — eecb15ce-e63b-4950-92be-a1414fc2e6b0

{"content": "Pensou por 43s", "content_type": "reasoning_recap"}

## assistant — f00f0e6c-76cb-4b1d-ad7f-ec9e2484b8a1

😎 Avançamos para a **Revisão 3.3 do ISA-1**, com um resultado concreto: a primeira tabela executável de microoperações para todas as 19 instruções implementadas no emulador de referência.

A tabela separa busca de instruções, leitura de operandos, operações internas e escrita na memória. Também preserva a ordem de empilhamento do `CALL` e de desempilhamento do `RET`.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={3} gap={2}>
    <grid-item>
      <title size="xl" tabularNums>19</title>
      <text color="secondary" size="xs">Instruções mapeadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>101</title>
      <text color="secondary" size="xs">Etapas simbólicas totais</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>13</title>
      <text color="secondary" size="xs">Etapas na instrução mais longa</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Verificações estruturais do modelo aprovadas
  </row>
</box>

Por enquanto, são **microoperações simbólicas**, não sinais elétricos prontos para ligar aos pinos dos CIs. Isso evita congelarmos uma implementação física antes de confirmar os caminhos de dados necessários.

## Arquivos da revisão 3.3

- [Relatório técnico e pendências](sandbox:/mnt/data/isa1/ISA-1_REV33_MICROOPERACOES.md)
- [Tabela completa das microoperações — JSON](sandbox:/mnt/data/isa1/isa1_rev33_microcode.json)
- [Gerador e verificações — Python](sandbox:/mnt/data/isa1/isa1_rev33_microcode.py)

### Próxima decisão de engenharia

A prioridade passa a ser escolher a implementação física da CPU: quais registradores terão CIs próprios, como a ALU será construída, quais multiplexadores selecionarão os dados e como o microsequenciador controlará cada transferência.

Um ponto especialmente importante é o `CALL`: precisamos preservar o endereço de destino enquanto a CPU utiliza o barramento de endereços para gravar o retorno na pilha.

**Estado atual:** revisão 3.3 concluída no nível simbólico. A CPU física, o circuito completo e a PCB ainda estão pendentes.

Seguimos com o mesmo objetivo: uma placa ISA-1 fabricável, com todos os componentes e conexões definidos e verificações reproduzíveis antes de enviá-la à fabricação.

## user — bbb21cd1-bee6-400b-9b61-13ee9a16ec3c

Perfeito, pode seguir com as escolha dos CIs

## assistant — 94623d37-a1f5-44ee-8219-4905a008a18c

{"content_type": "thoughts", "source_analysis_msg_id": "472e2a35-f6f7-497e-91b3-1a0022370ca7", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou arquivos ISA, microcódigo e registradores para selecionar CIs preliminares"}]}

## assistant — a465c516-ecd4-4e95-bc33-6f8a8174c310

{"content": "Pensou por 47s", "content_type": "reasoning_recap"}

## assistant — 7bd24aaf-d840-4cb0-99bc-6d5daf320d28

😎 Vamos para a **Revisão 3.4 — Seleção dos circuitos integrados da CPU do ISA-1**.

Minha escolha é construir a CPU com registradores de 8 bits, uma ALU modular e um microsequenciador controlado por ROM. Isso facilita testar cada bloco separadamente e corrigir o circuito antes de fabricar a placa principal.

Vou priorizar CIs da família **74HC**, em encapsulamentos SOIC quando disponíveis, mantendo a CPU inteiramente em lógica discreta — sem microcontrolador escondido executando as instruções.

## CIs selecionados para o primeiro projeto elétrico

| CI | Função | Decisão |
|---|---|---|
| **74HC377** | Registradores de 8 bits com habilitação de carga | Principal candidato |
| **74HC273** | Registradores que precisam de reset | Principal candidato |
| **74HC157** | Multiplexadores de dados | Selecionado |
| **74HC245** | Isolamento de barramentos bidirecionais | Uso condicionado à direção |
| **74HC244** | Buffers unidirecionais | Selecionado |
| **74HC283** | Somadores de 4 bits, combinados para 8 bits | Candidato para ALU |
| **74HC86** | XOR e inversão condicional para subtração | Selecionado |
| **74HC08 / 74HC32** | AND / OR | Selecionados |
| **74HC00 / 74HC138** | Decodificação e controle | Candidatos |

A ROM de microcódigo e a memória de firmware serão componentes de armazenamento, não processadores comerciais.

Um detalhe importante: o 74HC377 não possui reset próprio. Por isso, os registradores que precisam assumir valores conhecidos imediatamente ao ligar deverão utilizar outra solução, como o 74HC273, ou ter sua inicialização controlada e comprovada.

## Primeira estimativa de registradores

A partir das 19 instruções da revisão 3.3, identifiquei uma configuração conservadora de **16 registradores de 8 bits**, incluindo os pares que formam PC, SP, MAR e endereços temporários.

Isso não significa que precisaremos comprar exatamente 16 CIs registradores. Vamos tentar compartilhar alguns temporários sem comprometer o funcionamento da CPU.

Também identifiquei que o registrador X, previsto na especificação mais ampla, ainda precisa ser incorporado ao microcódigo.

### Documentação da revisão 3.4

- [Relatório de seleção dos CIs](sandbox:/mnt/data/isa1/ISA-1_REV34_SELECAO_CIS_CPU.md)
- [Script de auditoria](sandbox:/mnt/data/isa1/isa1_rev34_ci_audit.py)
- [Resultados da auditoria](sandbox:/mnt/data/isa1/isa1_rev34_results.json)

## Próxima etapa: interligar os componentes

A revisão 3.5 deverá definir exatamente quais CIs se comunicam, quais sinais habilitam suas saídas e quais operações acontecem em cada ciclo.

Depois disso, poderemos começar a transformar os blocos da CPU em um **esquemático elétrico real**, com pinos numerados e conexões verificáveis.

A escolha dos componentes está avançando, mas ainda é preliminar: faltam confirmar encapsulamentos, variantes exatas e tempos elétricos nas fichas técnicas.

**Minha prioridade continua sendo evitar uma placa bonita que não funcione.** Vamos chegar ao layout somente depois de fechar essas verificações. 😎

## user — bbb2136a-5459-4f93-8ca7-4a0e9358d386

Estamos chegando na parte legal😎 pode seguir

## assistant — 46f7ed74-099c-442b-b40a-7eff10a161fc

{"content_type": "thoughts", "source_analysis_msg_id": "08630705-be24-4c8d-80e0-2132c07edc8c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou arquivos ISA, microcódigo, expansão e semântica de barramento"}]}

## assistant — 74bd4ae9-9155-4376-8ce1-ea3a0663df96

{"content": "Pensou por 41s", "content_type": "reasoning_recap"}

## assistant — 999fd8c4-345e-4788-8cf8-bb0798bb6b29

😎 Agora entramos na parte em que a arquitetura começa a virar sinais de controle reais!

## ISA-1 — Revisão 3.5: controle dos barramentos

Partindo das 19 instruções da revisão 3.3, construí um primeiro modelo que separa os acessos à memória em fases de leitura e escrita.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={3} gap={2}>
    <grid-item>
      <title size="xl" tabularNums>19</title>
      <text color="secondary" size="xs">Instruções analisadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>183</title>
      <text color="secondary" size="xs">Microestados expandidos</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>0</title>
      <text color="secondary" size="xs">Violações das regras estáticas testadas</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">São resultados de um modelo lógico, não de uma simulação elétrica.</text>
</box>

### Como funcionará uma escrita na RAM

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    <text weight="medium" size="sm">Sequência proposta</text>
    <text color="secondary" size="xs">4 fases</text>
  </row>
  <grid columns={4} gap={1}>
    {#each [{n:"1",t:"SETUP",d:"Endereço e dados estáveis"},{n:"2",t:"PULSE",d:"Ativa /WE"},{n:"3",t:"HOLD",d:"Desativa /WE; mantém dados"},{n:"4",t:"RELEASE",d:"Libera barramento"}] as s}
      <grid-item>
        <box background="surface-secondary" radius="md" padding={2} gap={2} align="center">
          <text color="secondary" size="xs">{s.n}</text>
          <text weight="medium" size="3xs">{s.t}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <text color="secondary" size="sm">O modelo exige que a escrita tenha preparação e retenção dos sinais. As durações reais ainda dependerão das fichas técnicas e da frequência escolhida.</text>
</box>

Isso é importante porque não podemos simplesmente mandar a CPU trocar endereço, dados e sinal de escrita ao mesmo tempo, esperando que a memória interprete tudo corretamente.

## Arquivos da revisão 3.5

- [Relatório técnico e decisões](sandbox:/mnt/data/isa1/ISA-1_REV35_CONTROLE_BARRAMENTOS.md)
- [Tabela completa dos 183 microestados](sandbox:/mnt/data/isa1/isa1_rev35_states.json)
- [Código de verificação](sandbox:/mnt/data/isa1/isa1_rev35_control_audit.py)
- [Resultados da execução](sandbox:/mnt/data/isa1/isa1_rev35_results.json)

### Próximo passo: o desenho físico da CPU

A revisão 3.6 será especialmente importante. Precisamos decidir como conectar os registradores de 8 bits, os pares de endereço de 16 bits, os multiplexadores e a ALU sem criar conflitos elétricos.

Também vamos definir o circuito de incremento do PC, atualização do SP e preservação do endereço de destino durante `CALL`.

**A CPU está ficando mais definida, mas ainda não temos uma implementação física validada.** A tabela atual verifica regras estruturais; falta demonstrar que todas as transferências podem ser realizadas pelos CIs escolhidos.

Quando isso estiver resolvido, poderemos avançar para um esquemático com conexões pino a pino, em vez de apenas diagramas conceituais.

Seguimos rumo à nossa primeira PCB ISA-1! 😎

## user — bbb2163f-0621-4b0d-ad36-0069f65e0d8f

Pode seguir pra revisão 3.6😎
Já temos como vai funcionar parte da comunicação, isso eh muito bom

## assistant — b2e6ed86-fe80-4733-b33d-5aa6d3dc2064

{"content_type": "thoughts", "source_analysis_msg_id": "9b47e557-f3e4-4729-a7bd-6ea47ce2b10d", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou documentação, microcódigo e datapath ISA-1, redigindo relatório preliminar"}]}

## assistant — c56f7259-a4f0-4a24-a445-2eeaf9fa1e6a

{"content": "Pensou por 50s", "content_type": "reasoning_recap"}

## assistant — 578089b7-09a3-48c9-bf34-8cc3fc56402e

😎 **Revisão 3.6 concluída!** Agora temos uma proposta concreta para organizar os registradores, a ALU e os barramentos da CPU do ISA-1.

## Arquitetura escolhida

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 222" width="100%">
    {#each [{x:8,y:8,w:75,h:32,t:"PC 16 bits"},{x:8,y:49,w:75,h:32,t:"SP 16 bits"},{x:8,y:90,w:75,h:32,t:"EA 16 bits"},{x:113,y:49,w:93,h:43,t:"MUX endereço"},{x:241,y:49,w:91,h:43,t:"MAR 16 bits"},{x:8,y:157,w:75,h:37,t:"A / B"},{x:113,y:157,w:93,h:37,t:"ALU 8 bits"},{x:241,y:157,w:91,h:37,t:"Barramento DB"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="5" stroke="#64748b" fill="#64748b" fillOpacity=".10"/>
      <text x={b.x+b.w/2} y={b.y+b.h/2+4} fontSize="10" textAnchor="middle" fill="currentColor">{b.t}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.8" fill="none" strokeLinejoin="round">
      <path d="M83 24 H99 V70 H113 M83 65 H113 M83 106 H99 V70"/>
      <path d="M206 70 H241"/>
      <path d="M83 175 H113 M206 175 H241"/>
      <path d="M286 92 V125 H286 V157"/>
    </g>
    <g fill="#0d9488"><path d="M237 66 L244 70 L237 74Z"/><path d="M237 171 L244 175 L237 179Z"/></g>
    <text x="170" y="213" fontSize="9" textAnchor="middle" fill="currentColor">Topologia funcional preliminar — não é esquema elétrico</text>
  </svg>
</box>

O resultado mais importante é a decisão de manter o endereço de destino de `CALL` em registradores próprios, enquanto o MAR acessa a pilha. Isso resolve uma dependência importante da arquitetura.

### Verificações executadas

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl">65.536</title>
      <text color="secondary" size="xs">Valores de incremento/decremento de 16 bits verificados</text>
    </grid-item>
    <grid-item>
      <title size="xl">60</title>
      <text color="secondary" size="xs">Cenários de CALL/RET testados</text>
    </grid-item>
    <grid-item>
      <title size="xl">14</title>
      <text color="secondary" size="xs">Fontes propostas para o barramento</text>
    </grid-item>
    <grid-item>
      <title size="xl">1</title>
      <text color="secondary" size="xs">Conflito artificial corretamente detectado</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Testes arquiteturais aprovados
  </row>
</box>

Esses testes confirmam propriedades do modelo, mas ainda não comprovam o funcionamento elétrico dos CIs.

### Arquivos da revisão

- [Relatório técnico completo — Rev. 3.6](sandbox:/mnt/data/isa1/ISA-1_REV36_DATAPATH_FISICO_PRELIMINAR.md)
- [Modelo executável do datapath](sandbox:/mnt/data/isa1/isa1_rev36_datapath.py)
- [Resultados das verificações](sandbox:/mnt/data/isa1/isa1_rev36_results.json)

## Próxima revisão: 3.7

Agora precisamos transformar cada transferência em conexões concretas: selecionar os multiplexadores, contar os buffers, definir as habilitações e identificar quais pinos de cada CI serão utilizados.

Também vamos comparar os incrementadores dedicados de PC/SP com uma solução compartilhada, porque isso pode reduzir bastante a quantidade de componentes.

**Estamos mais próximos do esquemático, mas ainda não da PCB pronta.** O próximo marco será um circuito de CPU com conexões completas, sem fontes de barramento indefinidas.

A parte divertida está mesmo começando: estamos passando da lógica de programação para o hardware do nosso próprio computador! 😎

## user — bbb21fc3-c996-43d2-98f3-5a1e2ece0d62

Pode seguir💻

## assistant — 94323aa4-1f74-4e7a-9a7b-1b44273baa0f

{"content_type": "thoughts", "source_analysis_msg_id": "c3296ca3-b1e1-4442-86ae-853d7636efc4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos, orçamento auditável e mux de endereço MAR rev37"}]}

## assistant — fe313f59-2395-4468-a662-0253f32b8c48

{"content": "Pensou por 1m 4s", "content_type": "reasoning_recap"}

## assistant — 7bdaa31c-e103-4ba6-b01b-26bd5c1d61ec

😎💻 **Revisão 3.7 do ISA-1 concluída!** Agora começamos a definir conexões individuais entre os circuitos integrados.

Desta vez, trabalhei no circuito que escolhe qual endereço a CPU enviará à memória.

## O primeiro circuito de endereçamento

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 204" width="100%">
    {#each [{x:8,y:12,w:75,h:30,t:"PC [15:0]"},{x:8,y:54,w:75,h:30,t:"SP [15:0]"},{x:8,y:119,w:75,h:30,t:"EA [15:0]"},{x:115,y:39,w:98,h:48,t:"4 × 74HC157"},{x:115,y:115,w:98,h:48,t:"4 × 74HC157"},{x:245,y:79,w:87,h:43,t:"2 × 74HC377"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="5" stroke="#64748b" fill="#64748b" fillOpacity=".1"/>
      <text x={b.x+b.w/2} y={b.y+b.h/2+4} fontSize="10" textAnchor="middle" fill="currentColor">{b.t}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.8" fill="none">
      <path d="M83 27 H98 V52 H115"/>
      <path d="M83 69 H115"/>
      <path d="M164 87 V115"/>
      <path d="M83 134 H115"/>
      <path d="M213 139 H229 V100 H245"/>
      <path d="M288 122 V174"/>
    </g>
    <text x="288" y="187" fontSize="11" textAnchor="middle" fill="currentColor">MAR [15:0]</text>
    <text x="170" y="199" fontSize="9" textAnchor="middle" fill="currentColor">Diagrama funcional — não representa pinagem física</text>
  </svg>
</box>

O circuito utiliza oito multiplexadores 74HC157 para selecionar entre três fontes de endereço e dois registradores 74HC377 para armazenar o endereço escolhido.

Isso permite que o computador busque instruções pelo PC, acesse a pilha pelo SP e utilize endereços temporários pelo EA.

### Resultado das verificações

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>400.000</title>
      <text color="secondary" size="xs">Verificações de seleção de endereço</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>10.000</title>
      <text color="secondary" size="xs">Verificações de carga e retenção</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Modelo lógico aprovado
  </row>
  <text color="secondary" size="xs">Ainda não foram verificadas a temporização elétrica e a pinagem dos componentes reais.</text>
</box>

Uma decisão importante: **os registradores não serão conectados diretamente a um barramento compartilhado**, evitando conflitos entre saídas permanentemente ativas.

## Arquivos produzidos

- [Relatório técnico — Revisão 3.7](sandbox:/mnt/data/isa1/ISA-1_REV37_MUX_ENDERECOS.md)
- [Lista lógica das 32 conexões dos multiplexadores](sandbox:/mnt/data/isa1/isa1_rev37_mar_mux_nets.json)
- [Código de testes reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev37_mar_mux.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev37_results.json)

## Próxima etapa: barramento de dados

Agora que temos uma proposta verificável para selecionar endereços, precisamos resolver a seleção dos dados de 8 bits, incluindo registradores, ALU e memória.

Essa etapa será fundamental para determinar quantos buffers e multiplexadores a CPU realmente precisa.

**Estado atual:** circuito de seleção de endereços definido logicamente, mas ainda sem pinagem física validada. Não estamos prontos para fabricar a PCB.

Estamos começando a transformar o ISA-1 em algo que poderá ser desenhado no KiCad e, posteriormente, montado com componentes reais. 😎

## user — bbb2184f-c6da-4001-b6bb-c4b95573cd40

Pode seguir analisando o barramento

## assistant — f40261a7-e19e-4aff-8776-920e05d562cb

{"content_type": "thoughts", "source_analysis_msg_id": "21b5aea0-9741-495b-82a8-d4279327ba40", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Revisou documentação ISA-1, validou muxes e corrigiu teste de barramento"}]}

## assistant — 3f05df2f-1ad4-4942-8855-726d60ca80a8

{"content": "Pensou por 1m 42s", "content_type": "reasoning_recap"}

## assistant — ae7c80a6-137b-4c1b-80e2-a3b19d5a2f45

😎💻 **ISA-1 — Revisão 3.8: barramento de dados de 8 bits**

Avançamos na comunicação interna da CPU. Agora temos uma proposta concreta para selecionar os dados que circulam entre registradores, ALU e memória.

## 1. Arquitetura proposta

A decisão desta revisão é utilizar **multiplexadores para selecionar a origem dos dados**, evitando conectar diretamente várias saídas dos CIs ao mesmo barramento.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 224" width="100%">
    {#each [{x:8,y:10,t:"Registrador A"},{x:8,y:43,t:"Registrador B"},{x:8,y:76,t:"ALU"},{x:8,y:109,t:"Memória RAM"},{x:8,y:142,t:"MDR / TMP"},{x:8,y:175,t:"Endereço / CONST"}] as b}
      <rect x={b.x} y={b.y} width="122" height="27" rx="5" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
      <text x="69" y={b.y+17} fontSize="11" textAnchor="middle" fill="currentColor">{b.t}</text>
      <path d={`M130 ${b.y+13.5} H158`} stroke="#0d9488" strokeWidth="1.5"/>
    {/each}
    <rect x="158" y="50" width="75" height="125" rx="8" fill="#0d9488" fillOpacity=".12" stroke="#0d9488"/>
    <text x="195" y="100" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">MUX</text>
    <text x="195" y="116" textAnchor="middle" fontSize="10" fill="currentColor">8:1</text>
    <text x="195" y="130" textAnchor="middle" fontSize="10" fill="currentColor">8 bits</text>
    <path d="M233 112 H252" stroke="#0d9488" strokeWidth="2"/>
    <rect x="252" y="85" width="80" height="55" rx="6" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
    <text x="292" y="108" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">DB</text>
    <text x="292" y="123" textAnchor="middle" fontSize="10" fill="currentColor">8 bits</text>
    <text x="170" y="218" fontSize="9" textAnchor="middle" fill="currentColor">Topologia lógica preliminar, não esquemático elétrico</text>
  </svg>
</box>

O modelo utiliza oito fontes selecionáveis:

| Seleção | Origem |
|---|---|
| 000 | Registrador A |
| 001 | Registrador B |
| 010 | Resultado da ALU |
| 011 | Leitura da memória |
| 100 | Registrador MDR |
| 101 | Registrador TMP |
| 110 | Byte de endereço PC/SP/EA |
| 111 | Constantes ou entrada ainda a definir |

## 2. Testes executados

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>1.450.000</title>
  <text color="secondary" size="sm">Verificações abstratas de seleção e retenção executadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma falha após correção do teste
  </row>
</box>

Durante a execução, o teste inicial revelou uma inconsistência no tratamento das seleções reservadas. Corrigi o verificador e executei novamente. Isso reforça a importância de testar também os próprios modelos.

## 3. Uma oportunidade importante de otimização

A implementação direta exigiria **28 multiplexadores 74HC157** apenas para a seleção principal e auxiliar de dados.

É uma quantidade considerável para nossa placa.

Por isso, antes de aprovar essa solução, quero comparar uma alternativa com multiplexadores 74HC151, que podem selecionar oito entradas por bit. Precisamos verificar disponibilidade, encapsulamento, temporização e custo real.

Não vamos escolher a solução mais compacta sem antes confirmar que ela funciona com nossos sinais.

## Arquivos da revisão 3.8

- [Relatório técnico do barramento](sandbox:/mnt/data/isa1/ISA-1_REV38_BARRAMENTO_DADOS.md)
- [Modelo executável e testes](sandbox:/mnt/data/isa1/isa1_rev38_bus.py)
- [Resultados das verificações](sandbox:/mnt/data/isa1/isa1_rev38_results.json)

## Próxima revisão: 3.9

Vamos cruzar as microoperações das 19 instruções com as fontes e destinos físicos do barramento. Isso permitirá descobrir conexões que ainda faltam e comparar as opções de multiplexação antes de desenhar o esquemático.

**Situação atual:** o modelo de seleção de dados passou nos testes abstratos, mas ainda faltam a integração completa das instruções, a validação elétrica e a pinagem real.

Estamos avançando para a parte em que cada decisão começa a determinar quantos CIs existirão na placa do ISA-1. 😎

## user — bbb211e9-639b-47d6-8312-aedbfac02534

Pode validar se esse outro Ci serve pra gente e seguir com o plano

## assistant — 6ef68df2-bc43-4b87-960f-31cd0111c83b

{"content_type": "thoughts", "source_analysis_msg_id": "23563217-8a8b-41c3-8c63-e219cc9ca6a3", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e leu a documentação ISA-1"}]}

## assistant — 214ba3cf-bdd4-4db4-aa05-74cdc8b70071

{"content_type": "thoughts", "source_analysis_msg_id": "33ee3ff1-74f6-4fbe-bacf-7aeba4d91411", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 5 sites"}]}

## assistant — 2bc163f2-ced8-47ad-afca-915f2e954329

{"content_type": "thoughts", "source_analysis_msg_id": "968e68db-c10f-48fc-9cb6-e94512afd760", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou microcódigo, ISA, pinos, caminhos e MUX 74HC151"}]}

## assistant — c4ab8f71-08a5-4b07-b9cb-d63018311c22

{"content": "Pensou por 39s", "content_type": "reasoning_recap"}

## assistant — b2f7f3da-2f85-415a-8da3-45591584cd34

😎 **O 74HC151 serve para o ISA-1, e vale a pena adotá-lo como candidato principal para o barramento de dados.**

Conferi as fichas técnicas da Texas Instruments e da Nexperia. O componente é um multiplexador de oito entradas para uma saída, existe em **SOIC-16** e pode trabalhar com nossa lógica de 5 V. <Cite refs={["turn795580search1","turn795580search25"]}/>

A vantagem é significativa:

| Circuito | Com 74HC157 | Com 74HC151 |
|---|---:|---:|
| Seleção principal de 8 fontes × 8 bits | 14 CIs | 8 CIs |
| Seleção auxiliar de bytes de endereço | 14 CIs | 8 CIs |
| **Total** | **28 CIs** | **16 CIs** |

<text color="secondary" size="xs">Comparação apenas dos dois seletores 8:1 previstos na revisão 3.8; não inclui o multiplexador de endereços do MAR nem outros circuitos.</text>

Isso representa **12 CIs a menos, aproximadamente 43% de redução**, sem precisar utilizar um barramento interno com múltiplas saídas tri-state.

Há um detalhe importante: cada 74HC151 seleciona apenas **um bit**. Portanto, precisamos de oito componentes em paralelo para formar um seletor de 8 bits.

## ISA-1 — Revisão 3.9 concluída

Além de validar o componente, avancei no plano: cruzei as **19 instruções e 101 microetapas** da CPU com os caminhos de dados propostos.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>1.600.000</title>
      <text color="secondary" size="xs">Verificações lógicas de seleção de bits</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>16</title>
      <text color="secondary" size="xs">Instâncias 74HC151 mapeadas por pino</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Testes lógicos aprovados
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    Sete categorias de conexões ainda precisam ser resolvidas
  </row>
</box>

### O que descobrimos

A seleção de dados está correta no modelo, mas ainda faltam caminhos importantes para `CALL`, `RET`, atualização do PC e do SP, além da ligação física da ALU e das flags.

Isso significa que **o 74HC151 está aprovado como candidato, mas a arquitetura completa do barramento ainda não está aprovada**.

Também confirmei sua pinagem no datasheet: entradas I0–I7, seletores S0–S2, habilitação `/E`, saída normal Y e saída invertida. A saída não fica em alta impedância quando desabilitada, algo que precisamos respeitar no circuito. <Cite refs={["turn795580search27","turn795580search24"]}/>

### Arquivos da revisão 3.9

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    [Relatório técnico completo](sandbox:/mnt/data/isa1/ISA-1_REV39_VALIDACAO_74HC151_E_COBERTURA.md)
  </row>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary"/>
    [Código de validação](sandbox:/mnt/data/isa1/isa1_rev39_mux_audit.py)
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary"/>
    [Conexões propostas com números de pino](sandbox:/mnt/data/isa1/isa1_rev39_mux_nets.json)
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary"/>
    [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev39_results.json)
  </row>
</box>

**Decisão para o ISA-1:** vamos preferir o **74HC151D em SOIC-16** para os seletores de dados, mantendo os 74HC157 onde forem mais adequados.

Na revisão 4.0, a prioridade será fechar os caminhos de 16 bits do PC, SP e EA, especialmente as transferências necessárias para `CALL` e `RET`. Depois poderemos integrar os registradores e a ALU ao mesmo esquema.

Estamos reduzindo componentes sem sacrificar as funcionalidades que definimos. Esse é exatamente o tipo de otimização que queremos antes de desenhar a placa. 😎

## user — bbb21c1c-f23a-4abf-8db7-551a3cc32d15

Gostei disso! Eh bom a gente revisar sempre as coisas 
Quem sabe não dê pra trocar mais😎
Bom trabalho

## assistant — bb544a19-fa07-4288-9a1f-82d21f58df95

Obrigado! 😎💻

E concordo totalmente: **revisar continuamente pode ser tão importante quanto desenvolver novos circuitos.**

A troca dos 74HC157 pelos 74HC151 mostrou que podemos reduzir a quantidade de componentes sem abandonar as funcionalidades do ISA-1.

Quero aplicar esse mesmo raciocínio ao restante da CPU: registradores, ALU, incrementadores de 16 bits, decodificadores e lógica de controle.

Mas vamos seguir uma regra: **menos CIs só representa uma melhoria se mantivermos a confiabilidade, a velocidade e a facilidade de montagem.** Às vezes, um componente adicional simplifica bastante o circuito.

Na revisão 4.0, vamos comparar alternativas antes de fechar os caminhos do PC, SP e EA. Também revisitaremos decisões anteriores quando encontrarmos oportunidades reais de simplificação.

O objetivo não é apenas fazer o ISA-1 funcionar. É chegar a uma arquitetura própria, elegante, eficiente e que possamos montar e compreender completamente.

Estamos construindo algo muito interessante! 😎

## user — bbb21847-8ff7-4fa2-9546-a9485e773543

Perfeito! Temos que manter qualidade! 
Pode seguir com a 4.0

## assistant — 1806ee3f-7af2-4526-ada1-0827d762b541

{"content_type": "thoughts", "source_analysis_msg_id": "e84cf7fc-fb4b-4e2e-9ef5-20dc70ab7323", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Documentou validação, microcódigo, caminhos Rev. 4.0 e seleção de muxes"}]}

## assistant — 8680196c-831f-49ca-beb4-7abfd24f4112

{"content": "Pensou por 59s", "content_type": "reasoning_recap"}

## assistant — dcb4f0b6-e34e-4ec6-9b6e-8c6f6a824193

😎💻 **ISA-1 — Revisão 4.0: caminhos de 16 bits do PC, SP e EA**

Nesta etapa, comparei duas possibilidades: utilizar circuitos dedicados para atualizar os endereços ou compartilhar a ALU de 8 bits entre essas operações.

Minha escolha para a primeira versão física é **manter o incremento do PC e o incremento/decremento do SP em caminhos dedicados**.

Isso aumenta um pouco a quantidade de lógica, mas simplifica o microcódigo e evita disputar o barramento principal toda vez que a CPU precisa avançar para a próxima instrução.

## Arquitetura proposta

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 230" width="100%">
    {#each [{x:8,y:12,w:94,h:35,t:"PC · 16 bits"},{x:8,y:91,w:94,h:35,t:"SP · 16 bits"},{x:8,y:170,w:94,h:35,t:"EA · 16 bits"},{x:133,y:12,w:98,h:35,t:"PC + 1"},{x:133,y:91,w:98,h:35,t:"SP ± 1"},{x:133,y:170,w:98,h:35,t:"MUX PC"},{x:254,y:76,w:78,h:66,t:"MUX MAR"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" fill="#64748b" fillOpacity=".10" stroke="#94a3b8"/>
      <text x={b.x+b.w/2} y={b.y+b.h/2+4} fontSize="11" textAnchor="middle" fill="currentColor">{b.t}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.8" fill="none">
      <path d="M102 29 H133 M102 108 H133 M102 187 H133"/>
      <path d="M231 29 H244 V83 H254"/>
      <path d="M231 108 H254"/>
      <path d="M102 187 H117 V197 H133"/>
      <path d="M102 29 H112 V153 H182 V170"/>
      <path d="M102 108 H119 V135 H245 V108 H254"/>
    </g>
    <text x="170" y="224" textAnchor="middle" fontSize="9" fill="currentColor">Representação conceitual dos caminhos; não é uma netlist elétrica</text>
  </svg>
</box>

O ponto essencial é que o endereço de destino de um `CALL` permanece armazenado no EA enquanto o SP e o MAR realizam os acessos à pilha.

## Testes desta revisão

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>131.072</title>
      <text color="secondary" size="xs">Verificações de incremento e decremento de 16 bits</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>50.000</title>
      <text color="secondary" size="xs">Ciclos abstratos de CALL/RET testados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Testes comportamentais aprovados
  </row>
</box>

Esses testes incluem transições como `00FFh → 0100h`, `FFFFh → 0000h` e o retorno correto do endereço após duas gravações e duas leituras da pilha.

Ainda não demonstram que a lógica física consegue realizar essas operações dentro do período de clock escolhido.

## Uma melhoria importante identificada

Na revisão 3.9, ainda faltavam caminhos físicos para transferir os bytes do PC durante `CALL` e reconstruir o PC durante `RET`.

A revisão 4.0 agora especifica esses caminhos como requisitos obrigatórios. Ainda precisamos implementá-los com CIs, mas já sabemos exatamente o que não pode faltar.

Também vamos preservar a possibilidade de otimizar os incrementadores: talvez uma combinação de portas XOR e AND seja mais vantajosa que quatro somadores 74HC283 para o PC. **Não faremos a troca antes de comparar atrasos e quantidade real de componentes.**

## Arquivos da revisão 4.0

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary"/>
    [Relatório técnico — Revisão 4.0](sandbox:/mnt/data/isa1/ISA-1_REV40_CAMINHOS_16_BITS.md)
  </row>
  <row align="center" gap={3}>
    <icon name="file-code-2" color="secondary"/>
    [Modelo executável dos caminhos de 16 bits](sandbox:/mnt/data/isa1/isa1_rev40_address_paths.py)
  </row>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary"/>
    [Resultados das verificações](sandbox:/mnt/data/isa1/isa1_rev40_results.json)
  </row>
</box>

## Próximo marco: revisão 4.1

Vamos detalhar as conexões de PC, SP, EA, MAR e registradores temporários, incluindo os sinais de carga e as fontes de cada multiplexador.

Depois, precisaremos comprovar que os microciclos conseguem utilizar essas conexões sem conflitos.

**Resultado da 4.0:** arquitetura de endereçamento mais completa, testes comportamentais aprovados e escolha conservadora para a primeira implementação física. Ainda não temos o esquemático elétrico aprovado.

Estamos mantendo exatamente a prioridade que você estabeleceu: qualidade primeiro, otimização sempre que comprovadamente vantajosa. 😎

## user — bbb213a7-4b0d-42eb-9955-45bcff503a64

Boa! Pode seguir então e vê isso de trocar por outros tipos de portas pra otimizar os incrementadores 

## assistant — 5da8d5c3-22b4-45d5-849a-331c375eda1b

{"content_type": "thoughts", "source_analysis_msg_id": "13891647-a5aa-4c1a-a6b4-ae0f2328e557", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos, leu documentação ISA-1 e validou otimizadores 16-bit"}]}

## assistant — c30f1f29-f91b-4ddc-a769-de4d20ac9ff2

{"content": "Pensou por 40s", "content_type": "reasoning_recap"}

## assistant — df08843d-b49d-436c-8e03-8e16176e6297

😎 Essa revisão tem uma oportunidade interessante: **um incrementador feito com portas XOR e AND não é necessariamente menor que um circuito com somadores 74HC283**.

Para o ISA-1, precisamos comparar três coisas: quantidade de CIs, atraso de propagação e facilidade de conectar os registradores. Vou avaliar também uma terceira alternativa: contadores binários com carga paralela, que podem integrar o incremento ao próprio registrador do PC.

Há ainda uma simplificação promissora para o SP: um somador pode realizar tanto `SP+1` quanto `SP−1`, sem precisarmos construir dois circuitos aritméticos separados.

## ISA-1 — Revisão 4.1 concluída! 😎

Encontrei uma otimização interessante para o SP e uma alternativa promissora para o PC.

### 1. Comparação dos incrementadores

| Alternativa | CIs aritméticos | Avaliação |
|---|---:|---|
| 74HC283 para PC+1 | 4 | Simples e previsível |
| Portas XOR + AND | 8 | Não reduz a quantidade de CIs |
| Contadores 74HC163 | 4 | Podem substituir também os registradores do PC |
| 74HC283 para SP±1 | 4 | Faz as duas operações com o mesmo circuito |

<text color="secondary" size="xs">Contagens preliminares; não incluem toda a lógica auxiliar, seleção e controle.</text>

### 2. A otimização mais interessante

O SP poderá usar um único conjunto de quatro 74HC283:

- Para incrementar: somamos `0001h`.
- Para decrementar: somamos `FFFFh`.

Como a aritmética é de 16 bits, as duas operações funcionam com os mesmos somadores.

Para o PC, os contadores com carga paralela merecem uma investigação adicional: eles podem armazenar o endereço e incrementá-lo, potencialmente eliminando outros componentes.

### 3. Testes executados

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>312.144</title>
  <text color="secondary" size="sm">Verificações comportamentais realizadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência encontrada
  </row>
</box>

Foram testados todos os 65.536 valores possíveis de 16 bits nas alternativas aritméticas, além de 50.000 verificações adicionais de atualização do SP.

Ainda não medimos os atrasos reais dos CIs.

### Arquivos da revisão 4.1

- [Relatório técnico e comparação das alternativas](sandbox:/mnt/data/isa1/ISA-1_REV41_OTIMIZACAO_INCREMENTADORES.md)
- [Código executável dos testes](sandbox:/mnt/data/isa1/isa1_rev41_incrementers.py)
- [Resultados JSON](sandbox:/mnt/data/isa1/isa1_rev41_results.json)

## Minha escolha para a próxima etapa

**Manter provisoriamente os 74HC283 para o SP e comparar o circuito completo do PC usando 74HC163 contra a solução com registradores e somadores separados.**

Essa comparação precisa incluir `JMP`, `CALL`, `RET`, reset, carga paralela e temporização.

Se os contadores realmente reduzirem a quantidade de componentes sem comprometer a confiabilidade, teremos uma otimização ainda melhor que a troca dos multiplexadores.

É exatamente o que queremos para o ISA-1: **menos componentes quando possível, sem abrir mão da qualidade.** 😎

## user — bbb212df-1bec-45ad-af27-919fbc640f3d

Pode testar essa comparação

## assistant — 15317a50-b849-4543-9ca5-64a2c5543eca

{"content_type": "thoughts", "source_analysis_msg_id": "b6efeb54-6235-4d28-af90-ebbead52f88d", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou documentação ISA-1 e testou transições do contador PC"}]}

## assistant — 19cb8aba-73f9-46fe-9c3c-6d205564c5cf

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — 92fc56d0-53ca-4fce-a823-a606bf0ce9a8

😎💻 **ISA-1 — Revisão 4.2 concluída!** Testei as duas arquiteturas do contador de programa (PC) e encontramos uma oportunidade real de reduzir componentes.

## Resultado da comparação

<box border radius="lg" padding={3} gap={3}>
  <row align="center" justify="between">
    **74HC163 — Contadores síncronos**
    <badge color="success">Preferido</badge>
  </row>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>14 CIs</title>
      <text color="secondary" size="xs">Registradores + 74HC283 + multiplexadores</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>8 + lógica</title>
      <text color="secondary" size="xs">74HC163 + multiplexadores + controle de carry</text>
    </grid-item>
  </grid>
  <text size="sm">A alternativa com contadores pode economizar aproximadamente cinco encapsulamentos nessa parte da CPU. As contagens ainda são preliminares.</text>
</box>

### Testes executados

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>662.208</title>
  <text color="secondary" size="sm">Comparações comportamentais aprovadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência encontrada
  </row>
</box>

Os testes incluíram todos os 65.536 valores possíveis do PC, além de 200.000 transições pseudoaleatórias com incremento, retenção, reset, `JMP`, `CALL` e `RET`.

## O detalhe que precisamos resolver

O 74HC163 possui características específicas de carga paralela, habilitação de contagem e reset. Em particular, não podemos presumir que seu reset seja assíncrono.

Também precisamos garantir que os quatro contadores atualizem seus valores corretamente na mesma borda do clock, inclusive nas transições `00FFh → 0100h` e `FFFFh → 0000h`.

**Portanto, a comparação funcional foi aprovada, mas a validação elétrica ainda está pendente.**

## Arquivos produzidos

- [Relatório completo — Revisão 4.2](sandbox:/mnt/data/isa1/ISA-1_REV42_COMPARACAO_PC.md)
- [Código de comparação executável](sandbox:/mnt/data/isa1/isa1_rev42_pc_comparison.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev42_results.json)

### Decisão para o ISA-1

Vamos promover os **quatro 74HC163 a candidatos preferidos para implementar o PC de 16 bits**, mantendo a alternativa com 74HC283 documentada.

Na revisão 4.3, o próximo trabalho será verificar a pinagem real, os sinais de carga e habilitação, a cadeia de carry e o comportamento do reset.

Estamos conseguindo exatamente o que queríamos: **simplificar a CPU sem retirar funcionalidades e sem aceitar uma otimização antes de testá-la.** 😎

## user — bbb21353-b672-40ad-b8d4-9c4d0bc61afc

Sucesso! Pode seguir então! 
Qual porcentagem você acha q estamos até chegar em uma placa que podemos testar em um ambiente virtual antes de fabricar? 

## assistant — 24992358-e5dd-432e-9071-fcbb015cd0a0

{"content_type": "thoughts", "source_analysis_msg_id": "a9ce0eb9-ae0b-48eb-b19a-0e14bc6cce1d", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, cadeia de reset e implementou controles com testes negativos"}]}

## assistant — 37c55173-539f-4940-8588-c85b43e3c3a1

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 543d84a2-1278-49bc-ac10-18874293a0bd

😎 Estamos avançando bem! E agora que começamos a escolher componentes reais, já conseguimos estimar melhor quanto falta para testar o ISA-1 virtualmente.

**Minha estimativa é que estamos em aproximadamente 35% do caminho até uma primeira placa completa simulável.**

Essa porcentagem é uma avaliação de engenharia, não uma medição exata. Ela considera o que já definimos, mas também o trabalho de integração que ainda falta.

## Progresso estimado do ISA-1

{@body const stages=[{name:"Arquitetura geral",p:85},{name:"Conjunto de instruções e CPU",p:65},{name:"Barramentos e registradores",p:50},{name:"Esquemático elétrico completo",p:10},{name:"Vídeo RCA colorido",p:10},{name:"Teclado e armazenamento",p:25},{name:"Simulação integrada",p:5}]}
<box gap={3}>
  {#each stages as s}
    <box gap={1}>
      <row align="center" justify="between">
        <text size="sm" weight="medium">{s.name}</text>
        <text size="sm" color="secondary" tabularNums>{s.p}%</text>
      </row>
      <box background="surface-tertiary" height="8px" radius="full" clip>
        <box background="rgba(13,148,136,0.9)" width={`${s.p}%`} height="100%" radius="full"/>
      </box>
    </box>
  {/each}
  <caption>Estimativas qualitativas por área, não percentuais calculados a partir de tarefas concluídas.</caption>
</box>

O motivo de não considerar nosso progresso maior é simples: **uma CPU que funciona no emulador ainda não equivale a um circuito de CIs que funciona no simulador elétrico**.

Precisamos construir essa ponte.

## Revisão 4.3 — Mais um avanço concluído

Aproveitei para continuar a validação do PC com quatro contadores 74HC163.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **396.610 verificações comportamentais aprovadas**
  </row>
  <text color="secondary" size="sm">O modelo verificou incremento, retenção, carga paralela e prioridade dos controles. Também detectou um erro artificial de habilitação.</text>
</box>

A principal decisão desta revisão é utilizar **o mesmo clock nos quatro contadores**, calculando antecipadamente quais deles precisam incrementar. Isso evita criar uma cadeia de clocks em cascata.

O modelo também respeita o reset síncrono: o PC só é zerado quando ocorre uma borda de clock válida.

Arquivos disponíveis:

- [Relatório técnico — Revisão 4.3](sandbox:/mnt/data/isa1/ISA-1_REV43_CONTROLE_PC.md)
- [Código de validação](sandbox:/mnt/data/isa1/isa1_rev43_pc_control.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev43_results.json)

A pinagem, os tempos elétricos e o comportamento da variante exata do 74HC163 ainda precisam ser conferidos antes da aprovação.

## Quando poderemos simular nossa primeira placa?

Minha proposta é criar dois marcos:

**Marco 1 — CPU ISA-1 simulável:** PC, registradores, ALU, microcódigo, ROM e RAM funcionando juntos em uma simulação digital. Esse será nosso primeiro grande teste integrado.

**Marco 2 — Computador ISA-1 simulável:** acrescentar teclado, vídeo, gravador EEPROM, reset e periféricos, com verificações elétricas dos circuitos críticos.

Não precisamos esperar terminar o vídeo para testar a CPU virtualmente.

A ferramenta mais adequada para essa fase será um simulador de lógica digital ou HDL, seguido de análise elétrica onde necessário. A simulação não substitui o protótipo, especialmente no circuito de vídeo composto.

**Minha estimativa permanece em cerca de 35% para o projeto completo simulável.** Para uma primeira CPU integrada simulável, estamos mais próximos, embora ainda faltem decisões importantes.

O próximo passo será transformar os registradores e contadores escolhidos em um circuito digital conectado, com sinais reais de carga, clock e habilitação.

Estamos chegando à etapa em que poderemos observar o ISA-1 executando instruções em uma simulação do próprio hardware, não apenas em um emulador de software. 😎

## user — bbb219a6-3397-47ab-ab56-a1cef0e5ae87

Pensando que tem 1 dia que estamos mexendo nisso, 35% eh incrível
Vamos seguir aqui com os testes e melhorias

## assistant — 4f395eee-2243-444b-a413-65fdf83f4c08

{"content_type": "thoughts", "source_analysis_msg_id": "67b61557-dc50-49e9-9d0f-d6ad5deec2f8", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, testou integração e definiu regras do PC"}]}

## assistant — 5201f2a4-1759-45b2-a4f7-ec9a24a9274f

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — 8436f8b2-280f-4c5a-ab92-75ab9971b8f0

😎💻 Estamos avançando! E o mais interessante é que agora conseguimos testar não apenas instruções isoladas, mas também como diferentes partes da CPU devem trabalhar juntas.

## ISA-1 — Revisão 4.4 concluída

Nesta revisão, integrei logicamente o contador de programa (PC) com os caminhos de carga de endereços para `JMP`, `CALL` e `RET`.

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>752.281</title>
  <text color="secondary" size="sm">Verificações comportamentais aprovadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência encontrada nos testes
  </row>
</box>

### O que validamos

- Incremento e retenção do PC para todos os 65.536 valores possíveis.
- Carga de endereços provenientes do EA ou do retorno da pilha.
- Prioridade do reset síncrono sobre a carga e a contagem.
- Comportamento sem borda de clock.
- Restauração de endereços em chamadas aninhadas, utilizando uma pilha abstrata.
- Detecção de uma implementação propositalmente incorreta do carry.

**Uma ressalva:** a pilha utilizada nesses testes ainda é um modelo em software, não a SRAM conectada ao circuito. Portanto, ainda não podemos considerar `CALL` e `RET` fisicamente validados.

## Decisão sobre os componentes

Mantemos os quatro **74HC163 como candidatos preferidos para o PC de 16 bits**, com quatro 74HC157 para selecionar o endereço de carga entre EA e RET.

A próxima revisão deverá conferir a pinagem real, a lógica de carry e a temporização da variante específica que escolhermos.

## Arquivos produzidos

- [Relatório técnico — Revisão 4.4](sandbox:/mnt/data/isa1/ISA-1_REV44_INTEGRACAO_PC.md)
- [Código dos testes](sandbox:/mnt/data/isa1/isa1_rev44_pc_integration.py)
- [Resultados reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev44_results.json)

## Nossa próxima conquista

Quero que o primeiro grande marco seja **executar um pequeno programa em uma simulação digital da CPU construída com os blocos de hardware escolhidos**.

Isso será muito mais significativo que simplesmente executar instruções no emulador de referência.

A estimativa anterior de 35% continua sendo apenas uma referência aproximada; não vou aumentá-la artificialmente com base na quantidade de testes. Ainda temos trabalho importante de integração e validação elétrica.

Mas estamos no caminho certo: cada revisão está transformando decisões arquiteturais em requisitos de circuito verificáveis.

**Qualidade primeiro, otimização quando comprovada e nenhuma PCB enviada para fabricação antes de verificarmos suas conexões.** 😎

## user — bbb217b4-0279-4d79-8e8b-17527e463f49

Sucesso! Pode seguir pra conferir a pinagem real, eh nessa hora que a gente vê o que pode melhorar

## assistant — 02349977-71e3-4344-aecb-4490cb391a02

{"content_type": "thoughts", "source_analysis_msg_id": "98280866-a128-4371-a5d2-1b183847b2ba", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e leu a documentação ISA-1"}]}

## assistant — fa5bfa23-fa64-4e5c-bbf0-a20daaa9d18f

{"content_type": "thoughts", "source_analysis_msg_id": "574ea45d-f1d8-49a1-81a6-9f41a109c2b8", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 1 site"}]}

## assistant — 6ff19db8-2af4-4973-9dc6-4aeabd164f60

{"content_type": "thoughts", "source_analysis_msg_id": "87ae5271-b6aa-4a7d-9de3-bac0f7b87944", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Gerado artefato e testes de pinagem ISA"}]}

## assistant — 8e87cad9-205e-47c6-a6b5-86e2cd820596

{"content": "Pensou por 29s", "content_type": "reasoning_recap"}

## assistant — 3c9cc94c-8fe3-40a7-ade7-37b1bd70cced

😎 **ISA-1 — Revisão 4.5: conferência da pinagem real do PC**

Encontrei uma boa notícia: a Texas Instruments oferece o **SN74HC163D em SOIC-16**, adequado à nossa preferência por componentes SMD soldáveis manualmente.

A documentação oficial confirma quatro características importantes: contagem síncrona, carga paralela, reset síncrono e saída de carry para conectar vários contadores. <Cite refs={["turn725860search0","turn725860search28"]}/>

Também confirmei que o **SN74HC157D** existe em SOIC-16 e pode selecionar entre os endereços de `EA` e `RET`, como planejamos. <Cite refs={["turn725860search1","turn725860search24"]}/>

### Pinagem confirmada do 74HC163

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 222" width="100%">
    <rect x="109" y="10" width="122" height="198" rx="9" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <path d="M156 10 Q170 28 184 10" fill="none" stroke="#94a3b8" strokeWidth="2"/>
    {#each [{l:"/CLR",r:"VCC"},{l:"CLK",r:"RCO"},{l:"A",r:"QA"},{l:"B",r:"QB"},{l:"C",r:"QC"},{l:"D",r:"QD"},{l:"ENP",r:"ENT"},{l:"GND",r:"/LOAD"}] as p,i}
      <rect x="99" y={35+i*22} width="10" height="12" fill="#94a3b8"/>
      <rect x="231" y={35+i*22} width="10" height="12" fill="#94a3b8"/>
      <text x="91" y={45+i*22} textAnchor="end" fontSize="11" fill="currentColor">{i+1} · {p.l}</text>
      <text x="249" y={45+i*22} fontSize="11" fill="currentColor">{p.r} · {16-i}</text>
    {/each}
    <text x="170" y="103" textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor">SN74HC163D</text>
    <text x="170" y="119" textAnchor="middle" fontSize="10" fill="currentColor">SOIC-16</text>
  </svg>
  <caption>Vista superior, conforme a pinagem da família SN74HC163 da Texas Instruments.</caption>
</box>

O principal ganho desta conferência é que podemos utilizar o `RCO` do contador inferior para habilitar o próximo, mantendo **um único clock comum**. Isso elimina a necessidade de construir uma cadeia externa de comparação de todos os bits inferiores.

Mas o reset continua exigindo atenção: como é síncrono, o circuito de inicialização precisará garantir bordas de clock controladas antes de liberar a CPU.

## Resultado da revisão 4.5

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>128</title>
      <text color="secondary" size="xs">Pinos atribuídos aos oito CIs</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>75</title>
      <text color="secondary" size="xs">Redes identificadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>131.112</title>
      <text color="secondary" size="xs">Verificações funcionais executadas</text>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>0</title>
      <text color="secondary" size="xs">Falhas detectadas pelo verificador</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Pinagem atribuída e modelo funcional aprovados
  </row>
</box>

Agora temos um mapeamento pino a pino dos quatro contadores e dos quatro multiplexadores, incluindo alimentação, clock, reset, seleção e carga.

### Arquivos produzidos

- [Relatório técnico — Revisão 4.5](sandbox:/mnt/data/isa1/ISA-1_REV45_PINAGEM_PC.md)
- [Netlist dos 128 pinos — JSON](sandbox:/mnt/data/isa1/isa1_rev45_nets.json)
- [Verificador executável — Python](sandbox:/mnt/data/isa1/isa1_rev45_pincheck.py)

### A melhoria encontrada

Podemos aproveitar o `RCO` do próprio 74HC163 para propagar a habilitação de contagem entre os quatro estágios. Isso evita adicionar comparadores externos de terminal de contagem.

A ressalva é que essa cadeia tem atraso de propagação. Precisamos calcular seu pior caso antes de escolher a frequência de operação.

**Próximo passo: revisão 4.6 — análise temporal do PC**, seguida da integração com os registradores EA e RET.

A revisão 4.5 ainda não é um circuito elétrico completo, mas já temos conexões concretas que poderão ser transformadas em símbolos e fios no KiCad.

Continuamos reduzindo incertezas antes de fabricar a placa. 😎

## user — bbb2115e-ba48-4963-97dd-0bc60e352755

Pode seguir

## assistant — 4180017d-d120-45a4-b7f5-995e33b52e85

{"content_type": "thoughts", "source_analysis_msg_id": "c8f67e27-902c-49ee-8d36-41fd7a817ca1", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou arquivos, netlist, propagação RCO, temporização e pinagem ISA-1"}]}

## assistant — 5d7bde65-5634-4992-ab3f-f4b1aeabaf9e

{"content": "Pensou por 27s", "content_type": "reasoning_recap"}

## assistant — 024eb235-a645-4fc5-89de-811f2d6fa73a

😎💻 **ISA-1 — Revisão 4.6 concluída!** Avançamos para a análise de temporização do contador de programa, utilizando as conexões reais que definimos na revisão 4.5.

## O que verificamos

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>131.072</title>
      <text color="secondary" size="xs">Casos de contagem verificados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Divergências no modelo lógico</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Conexões estruturais do PC aprovadas
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    Temporização elétrica ainda não aprovada
  </row>
</box>

Confirmamos que a arquitetura com quatro contadores 74HC163 consegue representar corretamente o incremento de 16 bits, mantendo um único clock compartilhado.

### Uma observação importante

O sinal `RCO`, responsável por propagar a habilitação de contagem, precisa atravessar os estágios antes da próxima borda do clock.

Por isso, a frequência máxima dependerá dos atrasos de propagação, do tempo de preparação das entradas e das condições elétricas reais.

**Não vamos escolher a frequência definitiva sem calcular esses limites a partir dos datasheets.**

## Próxima melhoria identificada

A revisão também mostrou que precisamos projetar cuidadosamente a inicialização.

O 74HC163 possui reset síncrono. Portanto, simplesmente manter o reset ativo enquanto a alimentação sobe não garante que o PC seja zerado: precisamos de uma borda de clock válida durante o reset.

Minha proposta é desenvolver um pequeno sequenciador de inicialização que mantenha a CPU inativa até que alimentação, clock e registradores estejam em condições conhecidas.

## Arquivos da revisão 4.6

- [Relatório técnico e requisitos de temporização](sandbox:/mnt/data/isa1/ISA-1_REV46_ANALISE_TEMPORAL_PC.md)
- [Código de auditoria executável](sandbox:/mnt/data/isa1/isa1_rev46_timing_audit.py)
- [Resultados da verificação](sandbox:/mnt/data/isa1/isa1_rev46_results.json)

## Próxima etapa: revisão 4.7

Vamos integrar três elementos fundamentais: o circuito de reset, a geração de clock e os registradores de endereço EA/RET.

Isso nos aproximará de um primeiro bloco de CPU que possa ser simulado como circuito conectado, em vez de apenas como operações matemáticas.

**Decisão mantida:** quatro SN74HC163D continuam sendo nossa opção preferida para o PC, mas sua aprovação elétrica permanece condicionada à análise temporal completa.

Estamos avançando com a qualidade que combinamos: testar, identificar limitações e corrigir antes de fabricar. 😎

## user — bbb21ca0-fb24-40b1-ae82-6dffaf1fd5c2

Perfeito! Temos avanço
Pode seguir

## assistant — 64bfb7e6-4daa-4197-bebd-8ecde66c6ddc

{"content_type": "thoughts", "source_analysis_msg_id": "8e1700fc-25e6-47d5-a3f5-9b5afc7dde14", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, analisou resultados ISA-1 e relatou reset crítico"}]}

## assistant — 9e09ebb3-dba1-47dd-b7e9-5940c8ca4ece

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — b93de70c-4b89-42e4-ac2b-46dbc08ef963

😎💻 **ISA-1 — Revisão 4.7: inicialização segura da CPU**

Avançamos em um ponto essencial para a confiabilidade: garantir que o computador comece a executar instruções somente depois que a alimentação, o clock e o contador de programa estiverem em condições válidas.

Identifiquei uma decisão importante: **não devemos liberar o reset simplesmente porque a tensão de alimentação atingiu o nível esperado**. Como nossos 74HC163 possuem reset síncrono, precisamos garantir pelo menos uma borda válida de clock enquanto o reset está ativo.

A arquitetura de inicialização proposta fica assim:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 180" width="100%">
    {#each [{x:8,y:12,w:100,h:38,t:"Alimentação"},{x:8,y:75,w:100,h:38,t:"Clock"},{x:131,y:43,w:105,h:57,t:"Sequenciador",sub:"de partida"},{x:257,y:43,w:75,h:57,t:"CPU",sub:"74HC163"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x={b.x+b.w/2} y={b.y+b.h/2-(b.sub?2:-4)} textAnchor="middle" fontSize="11" fill="currentColor">{b.t}</text>
      {#if b.sub}<text x={b.x+b.w/2} y={b.y+b.h/2+12} textAnchor="middle" fontSize="10" fill="currentColor">{b.sub}</text>{/if}
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M108 31 H120 V59 H131"/>
      <path d="M108 94 H131"/>
      <path d="M236 71 H257"/>
    </g>
    <path d="M253 67 L259 71 L253 75" fill="none" stroke="#0d9488" strokeWidth="2"/>
    <text x="170" y="140" fontSize="11" textAnchor="middle" fill="currentColor">Reset → borda válida → liberação</text>
    <text x="170" y="163" fontSize="9" textAnchor="middle" fill="currentColor">Diagrama funcional, ainda não elétrico</text>
  </svg>
</box>

O sequenciador deverá impedir acessos de escrita à RAM e à EEPROM durante a partida. Também precisará manter os controles da CPU em estados seguros até a liberação.

## Resultado dos testes

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>327.680</title>
      <text color="secondary" size="xs">Verificações comportamentais aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>65.536</title>
      <text color="secondary" size="xs">Estados iniciais do PC examinados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Contrato lógico de inicialização aprovado
  </row>
</box>

Também incluí um teste negativo que identifica a tentativa de liberar a CPU sem uma borda de reset registrada.

É importante distinguir: o simulador verifica as regras de inicialização, mas ainda não reproduz os sinais elétricos de um 74HC163 real.

## Uma decisão para os registradores EA e RET

Vamos considerar dois 74HC377 para armazenar os 16 bits de EA e outros dois para RET. Assim, o endereço de destino de `CALL` pode permanecer preservado enquanto a CPU acessa a pilha.

Como esses registradores não possuem reset próprio, o circuito deverá impedir seu uso antes de receberem dados válidos.

### Arquivos da revisão 4.7

- [Relatório técnico de inicialização e reset](sandbox:/mnt/data/isa1/ISA-1_REV47_STARTUP_RESET.md)
- [Simulador e testes](sandbox:/mnt/data/isa1/isa1_rev47_startup.py)
- [Resultados da execução](sandbox:/mnt/data/isa1/isa1_rev47_results.json)

## Próxima revisão — 4.8

Vamos selecionar um supervisor de alimentação específico, definir o circuito de clock e detalhar como os registradores EA/RET serão carregados.

**O avanço desta revisão é termos um contrato verificável de inicialização.** Ainda falta transformá-lo em um circuito elétrico que realmente garanta esse comportamento.

Estamos mais próximos do primeiro subsistema da CPU pronto para ser desenhado e simulado em nível de componentes. 😎

## user — bbb2175a-dd22-4ebf-91b0-b9de196bc0f8

Pode seguir

## assistant — 4c5d7c9c-b1e7-4899-858a-d47638d2aa7d

{"content_type": "thoughts", "source_analysis_msg_id": "dee7d5f0-234f-4eb8-88dd-3c51f4899dfb", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Modelado sequenciador de reset e documentadas falhas de clock e liberação"}]}

## assistant — 0ef8e462-2979-44f3-8ae6-fee4d3c143bb

{"content": "Pensou por 44s", "content_type": "reasoning_recap"}

## assistant — dd8453f0-2012-44b5-8d43-e13b6a7420eb

😎💻 **ISA-1 — Revisão 4.8 concluída!**

Nesta etapa, avançamos na inicialização segura da CPU, na liberação do clock e na proteção contra escritas acidentais durante o reset.

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>851.973</title>
  <text color="secondary" size="sm">Verificações comportamentais aprovadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Modelo lógico passou
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    Circuito elétrico ainda precisa de validação
  </row>
</box>

## O que melhoramos

**1. Reset mais seguro.** A CPU só poderá começar a buscar instruções depois de confirmar que o PC recebeu uma borda válida de clock durante o reset.

**2. Proteção das memórias.** Definimos que os sinais de escrita da SRAM e EEPROM deverão ser bloqueados independentemente do firmware durante a inicialização e em condições de alimentação inadequada.

**3. Registradores EA e RET.** Como os 74HC377 não possuem reset, vamos impedir que seus valores sejam utilizados antes da primeira carga válida.

**4. Clock sem improvisações.** Não vamos gerar pulsos de clock utilizando combinações simples de portas lógicas. Isso poderia produzir transições indesejadas.

## Arquivos da revisão

- [Relatório técnico — Revisão 4.8](sandbox:/mnt/data/isa1/ISA-1_REV48_RESET_CLOCK_CONTRATO.md)
- [Modelo executável](sandbox:/mnt/data/isa1/isa1_rev48_reset_model.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev48_results.json)

## Próximo passo — Revisão 4.9

Agora precisamos escolher as variantes exatas do supervisor de alimentação e do oscilador, conferir suas fichas técnicas e começar a desenhar as conexões reais do circuito de reset.

Depois, integraremos esse circuito aos quatro contadores do PC e aos sinais de controle da memória.

**Situação atual:** o comportamento esperado da inicialização está definido e testado em software. Ainda não existe comprovação elétrica, especialmente durante a subida e queda da alimentação.

Seguimos com a mesma filosofia: não basta o ISA-1 funcionar em condições ideais; queremos projetá-lo para inicializar corretamente e proteger seus dados também quando as condições não forem perfeitas. 😎

## user — bbb218a4-c24f-46f5-80fe-8084019148b9

Boaaa pode seguir com as validações 

## assistant — c9aa0816-c754-4f1f-9ba0-5c2ab165600a

{"content_type": "thoughts", "source_analysis_msg_id": "f290245f-72e3-4112-b682-331bd1038714", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, arquivos, relatórios e modelo de reset"}]}

## assistant — e8bcb197-f430-4587-a07e-7c2be08d4cd6

{"content_type": "thoughts", "source_analysis_msg_id": "48e3d15b-e8b7-46d6-8a69-979b84795ba5", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 3 sites"}]}

## assistant — bc84158b-1b1e-4f22-97b5-1e7793ca683e

{"content_type": "thoughts", "source_analysis_msg_id": "45eeb52f-3929-4eb7-a549-6e0541701eb6", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou reset corretivo, inicialização e liberação de clock"}]}

## assistant — e0eccefc-d01a-4302-9d9f-3b48f098af70

{"content": "Pensou por 38s", "content_type": "reasoning_recap"}

## assistant — 807c0af5-eb7e-4367-8675-2415981f02fd

😎💻 **ISA-1 — Revisão 4.9 concluída!** E encontramos uma melhoria importante no circuito de inicialização.

## 1. Corrigimos uma dependência do reset

Na revisão 4.8, nossa lógica exigia que o PC recebesse uma borda de clock enquanto o supervisor ainda mantinha o reset ativo.

Isso poderia impedir a inicialização caso o oscilador começasse a funcionar somente depois da liberação do supervisor.

A nova solução mantém o reset do PC ativo durante os primeiros ciclos de clock, mesmo após a liberação do supervisor.

<box border radius="lg" padding={3} gap={2}>
  <title size="md">Nova sequência de partida</title>
  <list marker="number" gap={2}>
    <list-item>O supervisor libera o reset após a alimentação se estabilizar.</list-item>
    <list-item>Primeira borda: o PC recebe zero e começa a sincronização.</list-item>
    <list-item>Segunda borda: o PC permanece zerado.</list-item>
    <list-item>Terceira borda: a CPU é liberada, mantendo o PC em zero.</list-item>
    <list-item>Quarta borda: a CPU pode iniciar sua execução.</list-item>
  </list>
</box>

## 2. Componentes escolhidos para avançar

| Componente | Função | Situação |
|---|---|---|
| **SN74HC74D** | Flip-flops de sincronização | Pinagem conferida |
| **TPS3808G50DBVR** | Supervisor de alimentação de 5 V | Candidato selecionado |
| **SN74HC163D** | Contador de programa | Mantido |
| Oscilador de 5 V | Clock principal | Pendente |

O SN74HC74D possui dois flip-flops com clear assíncrono por encapsulamento SOIC-14. Dois CIs são suficientes para nossa sequência de três estágios. <Cite refs={["turn194107search24","turn194107search25"]}/>

O TPS3808G50DBVR possui saída de reset open-drain, entrada de reset manual e atraso de liberação configurável. Ainda precisamos conferir sua pinagem e os limites elétricos antes de aprovar a conexão. <Cite ref="turn194107search1"/>

## 3. Resultado dos testes

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>1.310.736</title>
  <text color="secondary" size="sm">Verificações comportamentais aprovadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência encontrada
  </row>
</box>

Testamos os 65.536 estados iniciais possíveis do PC, ausência de clock durante o reset, liberação em três etapas, interrupção da partida e retorno do reset durante a execução.

Esses resultados são de um modelo lógico em Python, não de uma simulação elétrica.

## Arquivos da revisão 4.9

- [Relatório técnico completo](sandbox:/mnt/data/isa1/ISA-1_REV49_VALIDACAO_RESET_CLOCK.md)
- [Código dos testes](sandbox:/mnt/data/isa1/isa1_rev49_startup_verify.py)
- [Resultados JSON](sandbox:/mnt/data/isa1/isa1_rev49_results.json)

## Próximo passo: revisão 5.0

Vamos avançar para o **primeiro subsistema de CPU com esquemático elétrico**, integrando supervisor, sincronização de reset, clock e contador de programa.

Ainda teremos de validar o comportamento durante a subida e a queda da alimentação, os tempos de propagação e a proteção física dos sinais de escrita.

**Situação atual:** a inicialização está mais bem definida e o modelo passou nos testes, mas ainda não foi validado eletricamente.

Continuamos no caminho para ter uma placa ISA-1 que possamos simular antes de fabricar, mantendo a qualidade como prioridade. 😎

## user — bbb214c0-c891-4f98-9060-69b8ce1fbb41

Aí sim! Vamos pra 5.0

## assistant — 0ac67aa2-82a1-4d74-a879-68cd25983bfa

{"content_type": "thoughts", "source_analysis_msg_id": "7a709830-7689-45b9-ab12-83d64b020c1c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou arquivos, inspecionou pinagem e sinalizou falhas no reset do PC"}]}

## assistant — 8d6e9b5d-767a-4539-b614-5ccc8d14bb8e

{"content": "Pensou por 44s", "content_type": "reasoning_recap"}

## assistant — 3bd70a05-01d4-454a-87af-3e5f4b0bc573

😎💻 **ISA-1 — Revisão 5.0: primeira integração pino a pino do reset com o PC!**

Agora estamos começando a transformar os blocos que projetamos em uma lista de conexões que poderá alimentar o esquemático.

Integrei a pinagem da revisão 4.5 com dois 74HC74 para a sequência de inicialização e um 74HC08 para os sinais de liberação.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>11</title>
      <text color="secondary" size="xs">CIs no bloco integrado</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>170</title>
      <text color="secondary" size="xs">Atribuições de pinos verificadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>262.144</title>
      <text color="secondary" size="xs">Verificações de inicialização</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Duplicações de pinos encontradas</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Modelo estrutural e sequência lógica aprovados
  </row>
</box>

O teste percorreu todos os 65.536 valores iniciais possíveis do PC, verificando sua inicialização e o primeiro incremento. Ainda não equivale a uma simulação elétrica.

## Arquivos da revisão 5.0

- [Relatório técnico e conexões principais](sandbox:/mnt/data/isa1/ISA-1_REV50_PRIMEIRA_NETLIST_RESET_PC.md)
- [Netlist parcial com números de pino — JSON](sandbox:/mnt/data/isa1/isa1_rev50_reset_pc_nets.json)
- [Código de verificação reproduzível](sandbox:/mnt/data/isa1/isa1_rev50_reset_netlist.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev50_results.json)

## O que falta para termos um circuito realmente simulável?

O próximo trabalho é conectar o supervisor de alimentação e o oscilador, resolver a liberação segura do reset e integrar os registradores EA/RET.

Também identifiquei uma pendência importante: precisamos garantir que a liberação assíncrona do supervisor não provoque problemas de sincronização perto da borda do clock. Isso será tratado antes de aprovar o circuito.

**Estado da revisão 5.0:** temos uma netlist parcial com pinagem atribuída e testes lógicos aprovados. Ainda não temos um esquemático KiCad nem uma simulação elétrica.

Nossa próxima meta será gerar um primeiro esquemático EDA verificável, executar a checagem de regras elétricas (ERC) e preparar uma simulação digital desse subsistema.

Estamos começando a sair dos diagramas conceituais e entrar nas conexões que realmente irão para a placa. 😎

## user — bbb21f7b-1ae2-44c9-8d23-f85039a6941e

Aeeeee 🥳 vamos seguir e testar
Estamos perto

## assistant — ac767b6a-8f3d-456c-9deb-3a1146aa8a1a

{"content_type": "thoughts", "source_analysis_msg_id": "df0d946d-e163-4ef4-9f19-3e4a4699f55e", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos, testou segurança do rev51 e documentou correções do PC"}]}

## assistant — 9aad8a6e-ab61-4500-89f1-6555bc190c34

{"content": "Pensou por 39s", "content_type": "reasoning_recap"}

## assistant — f2ccf50a-dc75-4fe8-a71d-09aec11eb15e

🥳 **ISA-1 — Revisão 5.1: encontramos uma falha real de integração antes de fabricar!**

Desta vez, não apenas repetimos os testes que já passavam. Fizemos um teste de falha, permitindo que sinais ainda não conectados assumissem valores desfavoráveis.

**O teste revelou um problema na revisão 5.0:** se `PC_LOAD_N` estiver ativo durante a terceira borda de inicialização, o contador pode carregar um endereço mesmo com `CPU_RUN = 0`.

Isso acontece porque o reset do 74HC163 já foi liberado nessa borda, e a entrada de carga paralela não estava protegida.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="danger"/>
    **Falha reproduzida no modelo**
  </row>
  <table>
    <table-row><table-cell>Estado inicial do PC</table-cell><table-cell>`0000h`</table-cell></table-row>
    <table-row><table-cell>`PC_LOAD_N`</table-cell><table-cell>`0` (carga ativa)</table-cell></table-row>
    <table-row><table-cell>Borda</table-cell><table-cell>3ª</table-cell></table-row>
    <table-row><table-cell>PC observado</table-cell><table-cell>`BEEFh` (valor de teste)</table-cell></table-row>
    <table-row><table-cell>PC esperado</table-cell><table-cell>`0000h`</table-cell></table-row>
  </table>
</box>

A correção proposta é impedir **tanto a carga quanto a contagem** enquanto `CPU_RUN` estiver inativo. Assim, o PC continua zerado durante a sequência de partida, independentemente das solicitações internas.

Com essa proteção adicionada ao modelo, **1.048.576 verificações passaram**. Isso valida a regra lógica corrigida, mas ainda não a implementação elétrica.

## Arquivos da revisão 5.1

- [Relatório técnico e correção proposta](sandbox:/mnt/data/isa1/ISA-1_REV51_AUDITORIA_FALHAS.md)
- [Código do teste de falhas](sandbox:/mnt/data/isa1/isa1_rev51_safety_audit.py)
- [Resultados JSON](sandbox:/mnt/data/isa1/isa1_rev51_results.json)

## Onde estamos agora?

Estamos próximos de ter o **primeiro subsistema lógico da CPU suficientemente definido para começar a validação em EDA**. Ainda não estamos próximos de liberar a fabricação da placa completa: faltam a integração elétrica, a temporização, o vídeo, as memórias e outros blocos.

Na próxima revisão, 5.2, quero transformar a correção encontrada em conexões reais, com portas lógicas, números de pino e verificação de conflitos.

**Essa descoberta foi um ótimo avanço:** encontramos uma falha que os testes anteriores não detectavam e estabelecemos uma maneira reproduzível de evitá-la. É exatamente esse tipo de validação que queremos fazer antes de produzir o ISA-1.

## user — bbb21909-37d9-435c-80a7-0e0f3f36b5dd

Pode corrigir e seguir com os testes

## assistant — c00db04c-0bbd-4ffd-beab-db59d57f9690

{"content_type": "thoughts", "source_analysis_msg_id": "1e37c655-658e-459a-9fe9-683ee7a00d24", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificando correção da ISA-1 Rev52"}]}

## assistant — b003bf53-46e2-4ace-8421-55e48c6c17d8

{"content": "Pensou por 11s", "content_type": "reasoning_recap"}

## assistant — 8440538f-d00b-48c8-abf3-315fce7c5be4

🥳🔧 **ISA-1 — Revisão 5.2: correção aplicada e testes aprovados!**

Corrigimos a falha encontrada na revisão 5.1 e executei novamente os testes. Agora temos uma proposta de circuito com portas lógicas e números de pinos definidos.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" color="default" tabularNums>1.048.576</title>
      <text color="secondary" size="xs">Verificações lógicas aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>198</title>
      <text color="secondary" size="xs">Pinos atribuídos sem duplicação</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>13</title>
      <text color="secondary" size="xs">Circuitos integrados no bloco parcial</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>84</title>
      <text color="secondary" size="xs">Rótulos de redes</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma divergência nos testes executados
  </row>
</box>

## 1. O que corrigimos

Adicionamos duas proteções independentes para o contador de programa.

**Proteção da carga paralela**

```text
PC_LOAD_N_SAFE = PC_LOAD_N_REQ OR NOT_CPU_RUN
```

Quando a CPU não está liberada, a carga paralela fica desativada.

**Proteção da contagem**

```text
PC_COUNT_SAFE = PC_COUNT_REQ AND CPU_RUN
```

Quando a CPU não está liberada, a contagem também fica desativada.

Essas proteções impedem a falha reproduzida anteriormente, na qual o PC poderia carregar um endereço indevido durante a inicialização.

## 2. Componentes adicionados

| Componente | Função |
|---|---|
| SN74HC04D | Inverter o sinal `CPU_RUN` |
| SN74HC32D | Bloquear cargas indevidas |
| SN74HC08D existente | Aproveitar uma porta livre para bloquear a contagem |

O 74HC08 já fazia parte do projeto. Portanto, acrescentamos apenas **dois circuitos integrados**.

Também atualizamos a netlist para conectar as saídas protegidas aos quatro SN74HC163.

## 3. Arquivos técnicos

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **Relatório da revisão 5.2**

      <text color="secondary" size="xs">Correção, conexões e limitações</text>
      [Abrir relatório](sandbox:/mnt/data/isa1/ISA-1_REV52_CORRECAO_PC_PINOS_TESTES.md)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="network" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **Netlist corrigida**

      <text color="secondary" size="xs">Conexões e números de pinos em JSON</text>
      [Baixar netlist](sandbox:/mnt/data/isa1/isa1_rev52_corrected_nets.json)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-code" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **Código de verificação**

      <text color="secondary" size="xs">Testes reproduzíveis em Python</text>
      [Baixar código](sandbox:/mnt/data/isa1/isa1_rev52_build_verify.py)
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-check" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **Resultados**

      <text color="secondary" size="xs">Tabela-verdade e contagem de verificações</text>
      [Baixar resultados](sandbox:/mnt/data/isa1/isa1_rev52_results.json)
    </box>
  </row>
</box>

## 4. Próxima etapa: revisão 5.3

Agora precisamos validar o circuito fora do modelo abstrato: conferir os datasheets dos componentes, integrar o supervisor de alimentação e o oscilador, verificar as margens de temporização e preparar o esquemático para ERC.

**Estamos progredindo, mas ainda não podemos aprovar a fabricação.** A correção passou nos testes lógicos; falta demonstrar que também funciona eletricamente, inclusive durante oscilações da alimentação e transições de reset.

O avanço importante é que a falha da revisão 5.1 deixou de ser apenas um problema identificado: agora temos uma correção implementada na netlist e testada de forma reproduzível.

## user — bbb219b8-91cc-4d87-88a1-64010142bf44

Perfeito, vamos avançar

## assistant — c2176b9a-2b81-4044-8d6f-fa1cfd44869f

{"content_type": "thoughts", "source_analysis_msg_id": "e4063c3b-25d8-42cc-83c5-815f8b109136", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos, documentação e auditorias estruturais da REV53"}]}

## assistant — dd17a837-a7ed-442f-b647-51a612b7fcdd

{"content": "Pensou por 11s", "content_type": "reasoning_recap"}

## assistant — bd15959a-6a5e-4c69-baa8-6bb3ddf7e807

🥳🔧 **ISA-1 — Revisão 5.3: auditoria independente da netlist!**

Avançamos para uma verificação diferente: em vez de testar somente o comportamento do contador, examinei as conexões dos 13 circuitos integrados da revisão 5.2, procurando erros de pinagem, alimentação e conflitos entre saídas.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>198</title>
      <text color="secondary" size="xs">Pinos auditados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Erros estruturais detectados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>37</title>
      <text color="secondary" size="xs">Redes aguardando drivers externos</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>17</title>
      <text color="secondary" size="xs">Redes de saída sem receptor interno</text>
    </grid-item>
  </grid>
</box>

### O que descobrimos

**A correção do PC continua consistente**, e não encontramos pinos duplicados, pinos sem atribuição ou duas saídas lógicas ligadas indevidamente à mesma rede.

Mas identificamos precisamente o que ainda falta conectar:

- Os 32 sinais dos registradores `EA_Q` e `RET_Q`.
- Os comandos de carga e contagem do PC.
- O seletor entre EA e RET.
- O clock principal e o reset do supervisor.

As 37 redes pendentes não são necessariamente defeitos: são interfaces que precisam receber seus circuitos na integração completa.

### Uma limitação importante

Verifiquei também a disponibilidade da ferramenta de projeto eletrônico neste ambiente. **O KiCad CLI não está instalado**, portanto ainda não executei um ERC verdadeiro.

Não vou apresentar uma auditoria em Python como se fosse uma simulação elétrica ou uma validação de fabricação.

## Arquivos da revisão 5.3

- [Relatório técnico da auditoria](sandbox:/mnt/data/isa1/ISA-1_REV53_AUDITORIA_ESTRUTURAL.md)
- [Código de verificação reproduzível](sandbox:/mnt/data/isa1/isa1_rev53_audit.py)
- [Resultados detalhados em JSON](sandbox:/mnt/data/isa1/isa1_rev53_results.json)

## Próximo passo: revisão 5.4

Agora vamos trabalhar nas pendências mais críticas: **supervisor de alimentação, oscilador, proteção das escritas e sincronização do reset**.

Minha prioridade será fechar primeiro a segurança elétrica da inicialização. Depois integraremos EA/RET e prepararemos o primeiro esquemático para uma verificação ERC real.

Estamos avançando de maneira consistente. A arquitetura lógica do PC está bem encaminhada; o próximo grande marco será demonstrar que o circuito também é eletricamente seguro.

## user — bbb21e3b-359f-4ab1-982e-0505153e0914

O que eh possível fazer no ambiente aqui, sem o Cli? 

## assistant — c66a46ab-6b38-4cb7-94f6-b7ce6825ad8c

{"content_type": "thoughts", "source_analysis_msg_id": "e189440f-7e9e-40ae-bb69-0553fe251582", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas e arquivos disponíveis"}]}

## assistant — c9524011-5fbb-43b8-95a7-406b18286742

{"content": "Pensou por 10s", "content_type": "reasoning_recap"}

## assistant — f0e97511-fedf-49e6-8bb9-d1a16b598574

Temos bastante coisa que podemos fazer aqui **sem o KiCad CLI** — inclusive avançar significativamente na validação do ISA-1 antes de fabricar a placa.

A principal diferença é entre **verificar se o circuito está logicamente correto** e **comprovar que ele funcionará eletricamente**.

| Atividade | Sem KiCad CLI | Limitação |
|---|---|---|
| Auditar pinagem e conexões | <icon name="check" color="success" inline/> Sim | Depende da exatidão dos datasheets e modelos |
| Detectar conflitos entre saídas | <icon name="check" color="success" inline/> Sim | Não substitui ERC |
| Simular CPU, reset e instruções | <icon name="check" color="success" inline/> Sim | Simulação comportamental |
| Verificar temporização | <icon name="check" color="success" inline/> Parcialmente | Podemos calcular margens teóricas |
| Gerar esquemático KiCad | <icon name="check" color="success" inline/> Sim | Sem validação pelo KiCad, por enquanto |
| Gerar arquivos de PCB | <icon name="check" color="success" inline/> Sim | Precisam de DRC e inspeção |
| Executar ERC/DRC oficial | <icon name="x" color="danger" inline/> Não | Requer KiCad ou ferramenta compatível |
| Comprovar funcionamento físico | <icon name="x" color="danger" inline/> Não | Exige protótipo e medições |

O mais interessante é que **não precisamos interromper o desenvolvimento do hardware**. Podemos continuar produzindo arquivos reais de engenharia, e não apenas relatórios.

## O que eu recomendo fazer agora

Para o ISA-1, seguiria nesta ordem:

1. **Fechar a netlist elétrica:** integrar supervisor, oscilador, reset, PC e registradores EA/RET, com todas as conexões numeradas.
2. **Criar um simulador digital mais rigoroso:** testar transições de clock, prioridades de reset/carga/contagem, barramentos e condições anormais.
3. **Calcular as margens temporais:** usar os valores dos datasheets para identificar a frequência de operação segura, incluindo uma margem de projeto.
4. **Gerar o primeiro esquemático KiCad:** produzir o arquivo `.kicad_sch` para que possamos abrir e inspecionar no KiCad.
5. **Preparar a validação externa:** quando tivermos acesso ao KiCad, executar ERC, corrigir os avisos e só então avançar para o layout da PCB.

Acabei de conferir este ambiente: não encontrei os executáveis `kicad-cli`, `ngspice` ou `iverilog` disponíveis. Isso não impede a geração de arquivos ou nossos testes em Python, mas limita as verificações independentes que conseguimos executar aqui.

### Uma possibilidade adicional

Podemos construir uma **bancada de testes virtual do ISA-1** que execute instruções da CPU e registre, ciclo por ciclo, os sinais dos componentes.

<box border radius="lg" padding={3} gap={2}>
  <title size="md">Exemplo de sinais que poderemos acompanhar</title>
  <table>
    <table-row><table-cell>Clock</table-cell><table-cell>`CLK`</table-cell></table-row>
    <table-row><table-cell>Reset</table-cell><table-cell>`RESET_N`</table-cell></table-row>
    <table-row><table-cell>Contador</table-cell><table-cell>`PC[15:0]`</table-cell></table-row>
    <table-row><table-cell>Endereço</table-cell><table-cell>`EA[15:0]`</table-cell></table-row>
    <table-row><table-cell>Memória</table-cell><table-cell>`RAM_WE_N`</table-cell></table-row>
    <table-row><table-cell>Execução</table-cell><table-cell>`CPU_RUN`</table-cell></table-row>
  </table>
</box>

Isso nos permitiria detectar muitos erros antes de montar qualquer componente, embora não substitua uma simulação elétrica.

**Minha escolha para a revisão 5.4 seria combinar a netlist elétrica com essa bancada virtual.** Assim, cada conexão nova teria testes automatizados, e os arquivos poderiam ser aproveitados posteriormente no KiCad.

Não estamos bloqueados pela ausência do CLI. Estamos na fase em que podemos preparar boa parte da engenharia e reduzir os riscos da primeira placa.

## user — bbb212a5-fc49-4341-b259-811daadacff8

Legal! Então vamos continuar aqui

## assistant — 291fe4a6-a635-4b32-83d5-76eb9dbbd230

{"content_type": "thoughts", "source_analysis_msg_id": "22bf3c46-72dc-4028-ac8f-9ae81592f1a4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou ferramentas, redes críticas e bancada virtual reproduzível"}]}

## assistant — b6bb1508-7773-4ff4-babf-9db7e111bad5

{"content": "Pensou por 44s", "content_type": "reasoning_recap"}

## assistant — 2fde027a-e496-4171-95de-97b8220f7893

🥳💻 **ISA-1 — Revisão 5.4 concluída!**

Continuamos o desenvolvimento e já temos nossa primeira **bancada virtual reproduzível** para testar o contador de programa e a sequência de inicialização.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>577.702</title>
      <text color="secondary" size="xs">Verificações executadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Divergências detectadas</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Testes comportamentais aprovados
  </row>
</box>

## O que testamos

- Todos os 65.536 estados iniciais possíveis do PC.
- Bloqueio de carga e contagem durante a inicialização.
- Prioridade entre reset, carga paralela e incremento.
- Reinicialização após um sinal de queda de alimentação.
- 250 mil transições pseudoaleatórias comparadas com um modelo de referência independente.

Também produzimos um arquivo CSV com os sinais da CPU registrados borda por borda.

## Arquivos gerados

<box gap={2}>
  <row align="center" gap={2}>
    <icon name="file-text" color="secondary"/>
    [Relatório técnico — Revisão 5.4](sandbox:/mnt/data/isa1/ISA-1_REV54_BANCADA_VIRTUAL.md)
  </row>
  <row align="center" gap={2}>
    <icon name="file-code" color="secondary"/>
    [Bancada virtual em Python](sandbox:/mnt/data/isa1/isa1_rev54_bench.py)
  </row>
  <row align="center" gap={2}>
    <icon name="activity" color="secondary"/>
    [Registro de sinais por ciclo — CSV](sandbox:/mnt/data/isa1/isa1_rev54_waveform.csv)
  </row>
  <row align="center" gap={2}>
    <icon name="file-check" color="secondary"/>
    [Resultados dos testes — JSON](sandbox:/mnt/data/isa1/isa1_rev54_results.json)
  </row>
</box>

## O próximo desafio

A bancada passou nos testes lógicos, mas **ainda não demonstra que a CPU funcionará eletricamente**. Precisamos fechar a alimentação, o supervisor, o oscilador e a proteção física das escritas.

Na revisão 5.5, minha prioridade será resolver esses pontos sem aumentar desnecessariamente o número de componentes.

Estamos avançando para um ISA-1 que não apenas executa instruções corretamente no modelo, mas que também possa ser construído, testado e reparado em hardware real.

## user — bbb212f7-cece-4706-a128-bf04eba03ef3

Pode seguir pra 5.5 e fechar a alimentação

## assistant — 7e97289a-5d9c-4e13-8e1f-5644a4a24575

{"content_type": "thoughts", "source_analysis_msg_id": "7bd2fa75-0470-4e67-8952-f7abc7bdba14", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e inspecionou documentação técnica anterior"}]}

## assistant — 7e3223cb-3e60-4c4a-96cd-3074a511312e

{"content_type": "thoughts", "source_analysis_msg_id": "9050b188-4249-4c7c-9f7c-db4667ed9b67", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 7 sites"}]}

## assistant — 7fd95130-0009-403d-b987-3c7f504fe8ff

{"content_type": "thoughts", "source_analysis_msg_id": "33fbe39f-8f51-4dcb-813d-d9469490aac4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Corrigindo contagem e executando auditoria"}]}

## assistant — cc68a397-2a2d-474d-a842-b8be4d30f46d

{"content": "Pensou por 48s", "content_type": "reasoning_recap"}

## assistant — da6caf8d-20ec-455b-8166-e0d9a5db2db5

🥳🔧 **ISA-1 — Revisão 5.5: alimentação de 5 V, supervisor e proteção das memórias**

Avançamos! Defini a arquitetura preliminar de alimentação, selecionei um supervisor específico, conferi sua pinagem e executei novos testes.

Também encontramos um ponto importante: **proteger a CPU durante uma queda de tensão não significa necessariamente proteger os dados da EEPROM**. Precisamos tratar as duas situações separadamente.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>262.193</title>
      <text color="secondary" size="xs">Verificações lógicas aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Divergências após correção do teste</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Arquitetura lógica preliminar consistente
  </row>
  <row align="center" gap={2}>
    <icon name="alert-triangle" color="secondary"/>
    Segurança elétrica ainda não comprovada
  </row>
</box>

## 1. Alimentação proposta

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 177" width="100%">
    {#each [{x:7,y:10,w:90,h:37,a:"Fonte externa",b:"5 V DC"},{x:117,y:10,w:100,h:37,a:"Proteção",b:"e filtragem"},{x:238,y:10,w:85,h:37,a:"+5V_SYS",b:"GND"},{x:19,y:108,w:86,h:42,a:"Supervisor",b:"TPS3808"},{x:122,y:108,w:86,h:42,a:"Reset",b:"e clock"},{x:225,y:108,w:86,h:42,a:"CPU",b:"e memórias"}] as b}
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="6" fill="#64748b" fillOpacity=".10" stroke="#94a3b8"/>
      <text x={b.x+b.w/2} y={b.y+16} fontSize="10" fill="currentColor" textAnchor="middle">{b.a}</text>
      <text x={b.x+b.w/2} y={b.y+30} fontSize="10" fill="currentColor" textAnchor="middle">{b.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.8" fill="none">
      <path d="M97 28 H117 M217 28 H238 M280 47 V73 H62 V108 M280 73 H165 V108 M280 73 V108 M105 129 H122 M208 129 H225"/>
    </g>
    <text x="165" y="168" textAnchor="middle" fontSize="9" fill="currentColor">Arquitetura funcional — não é esquemático elétrico</text>
  </svg>
</box>

Usaremos uma fonte externa regulada de 5 V como base de projeto. A corrente necessária ainda depende do orçamento completo de consumo, incluindo vídeo e memórias.

## 2. Supervisor selecionado

**<Entity category="product" value="Texas Instruments TPS3808G50DBVR" disambig="supervisor de tensão de 5 V"/>**

Esse componente monitora a alimentação e possui limiar nominal de 4,65 V, saída de reset open-drain e atraso de liberação configurável. <Cite refs={["turn460565search1","turn460565search3"]}/>

| Pino | Função |
|---|---|
| 1 | RESET ativo em nível baixo |
| 2 | GND |
| 3 | Reset manual |
| 4 | Temporização CT |
| 5 | Monitoramento SENSE |
| 6 | Alimentação VDD |

A pinagem foi conferida para o encapsulamento SOT-23-6. <Cite ref="turn460565search26"/>

## 3. Proteção contra escritas acidentais

Definimos a regra lógica:

```text
WRITE_PERMIT =
    POWER_GOOD
    AND CPU_RUN
    AND ADDR_VALID
    AND WRITE_REQ
```

Enquanto qualquer condição não estiver satisfeita, a escrita deverá permanecer bloqueada.

Mas há uma limitação crítica: abaixo da tensão mínima de funcionamento, a saída do supervisor pode deixar de ser definida. Portanto, essa regra sozinha não garante a proteção da EEPROM durante todo o desligamento. <Cite ref="turn460565search4"/>

**Não vamos considerar a alimentação eletricamente fechada até resolver esse problema.**

## 4. Arquivos da revisão 5.5

- [Relatório técnico de alimentação e proteção](sandbox:/mnt/data/isa1/ISA-1_REV55_ALIMENTACAO_RESET_WE.md)
- [Código de auditoria executável](sandbox:/mnt/data/isa1/isa1_rev55_power_audit.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev55_results.json)

## Próxima revisão — 5.6

Minha prioridade será fechar o circuito de proteção da EEPROM e SRAM, escolher o oscilador e começar o orçamento de consumo.

O objetivo continua sendo uma única PCB principal, com componentes SMD sempre que possível, sem sacrificar os recursos do ISA-1 para economizar circuitos integrados.

**Resultado desta etapa:** avançamos na definição da alimentação e validamos seu contrato lógico. A fabricação permanece bloqueada até demonstrarmos segurança elétrica real, especialmente nas transições de alimentação.

## user — bbb218a4-1517-4d8e-a0d0-190af6f6d41d

Ponto a se pensar para alimentação 
Uma fonte 12v
E na nossa placa, um jeito para reduzir para 5v
Assim a gente também cuida da alimentação da tela

## assistant — 85ae8d68-2008-43d2-bf8c-4474a7063e6f

{"content_type": "thoughts", "source_analysis_msg_id": "7c40d068-e6d0-4d33-abea-768a2a0a4b9a", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 2 sites"}]}

## assistant — 17676d75-281f-4fe2-bd36-cb4bfd1a12e4

{"content": "Pensou por 6s", "content_type": "reasoning_recap"}

## assistant — c1f97ef5-eda6-4ee3-a5f1-06a5596d2a37

Essa é uma ótima mudança para o ISA-1! 🔧

**Minha proposta é adotarmos uma entrada externa de 12 V e fazermos a conversão para 5 V na própria PCB.** Isso permite alimentar tanto o computador quanto a tela a partir de uma única fonte.

Mas eu faria uma distinção importante: **a tela não precisa necessariamente receber 5 V**. Precisamos conferir a tensão exigida pelo modelo de 4,3 polegadas com entrada RCA que escolhemos.

A arquitetura que proponho é:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 232" width="100%">
    <g fill="#64748b" fillOpacity=".10" stroke="#94a3b8">
      <rect x="9" y="10" width="112" height="43" rx="6"/>
      <rect x="144" y="10" width="187" height="43" rx="6"/>
      <rect x="144" y="84" width="187" height="43" rx="6"/>
      <rect x="144" y="160" width="187" height="43" rx="6"/>
    </g>
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <text x="65" y="27">Fonte externa</text><text x="65" y="42">12 V DC</text>
      <text x="237" y="27">Proteção de entrada</text><text x="237" y="42">e filtragem</text>
      <text x="237" y="101">Conversor buck</text><text x="237" y="116">12 V → 5 V</text>
      <text x="237" y="177">ISA-1 + tela</text><text x="237" y="192">alimentação distribuída</text>
    </g>
    <g fill="none" stroke="#0d9488" strokeWidth="2">
      <path d="M121 31 H144"/>
      <path d="M237 53 V84"/>
      <path d="M237 127 V160"/>
    </g>
    <g fontSize="10" fill="currentColor" textAnchor="middle">
      <text x="170" y="221">Diagrama conceitual; tensões da tela a confirmar</text>
    </g>
  </svg>
</box>

Um conversor chaveado (*buck*) é preferível a um regulador linear para essa redução, porque dissipa muito menos calor.

Por exemplo, com uma carga de 1 A em 5 V, um regulador linear de 12 V para 5 V dissiparia aproximadamente **7 W em calor**. Para uma placa compacta, isso seria indesejável.

## Revisão 5.6 — Nova proposta de alimentação

Pesquisei um candidato para o conversor: o **<Entity category="product" value="TPS54302" disambig="conversor buck síncrono da Texas Instruments"/>**, da Texas Instruments.

Ele aceita entradas de 4,5 a 28 V, fornece até 3 A e integra os transistores de potência. É adequado para estudarmos a conversão de 12 V para 5 V, embora ainda precise de indutor, capacitores e resistores externos. <Cite ref="turn320396search0"/>

Eu dividiria a alimentação em três partes:

- **12V_IN:** entrada protegida contra inversão de polaridade e surtos.
- **5V_SYS:** saída regulada para CPU, memórias, lógica e supervisor.
- **DISPLAY_PWR:** alimentação da tela, derivada de 12 V ou de 5 V conforme sua especificação.

Também manteria filtragem dedicada para o vídeo composto, porque o chaveamento do conversor pode introduzir interferências na imagem.

### Uma decisão que vale a pena tomar agora

Se a tela funcionar com 12 V, podemos alimentá-la diretamente pelo barramento protegido, sem desperdiçar potência reduzindo para 5 V e depois elevando novamente.

Se funcionar com 5 V, poderemos compartilhar o conversor, desde que a corrente total e os ruídos estejam dentro dos limites.

**Adotaria os 12 V como nova tensão de entrada do ISA-1**, mantendo a escolha definitiva do conversor e da fonte condicionada ao orçamento de consumo.

Você já tem a tela RCA de 4,3 polegadas em mãos ou ainda vamos escolher o modelo? Essa informação define a última parte da arquitetura de alimentação.

## user — bbb218d4-aa8a-462c-8b87-4f6f01233bd6

Procura por telas RCA que aceitem 5v na alimentação
Aí seria possível alimentar nosso PC por um cabo USB C? Com uma fonte boa de celular mesmo

## assistant — dab1c95e-0c9d-4f0d-b401-a9f0ee17bbdc

{"content_type": "thoughts", "source_analysis_msg_id": "e4ae429c-f206-4aaa-a9a1-e786aaad9f5f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 21 sites"}]}

## assistant — b47cbc10-83bf-4d07-be69-c6b15688f139

{"content": "Pensou por 11s", "content_type": "reasoning_recap"}

## assistant — 11ad1c08-9fbf-4089-bfb8-ea22bf209287

**Sim! Podemos projetar o ISA-1 para funcionar com uma fonte USB-C de celular de 5 V**, alimentando tanto a CPU quanto uma tela RCA compatível.

Isso seria particularmente interessante para nosso computador: eliminaríamos a conversão de 12 V para 5 V, reduziríamos os componentes da alimentação e teríamos uma única entrada USB-C na PCB.

Só precisamos observar um detalhe: **USB-C não significa automaticamente que a fonte fornecerá toda a corrente desejada**. Vamos dimensionar a alimentação de acordo com a tela e o consumo real do ISA-1.

Minha preferência é procurar uma tela de 4,3 polegadas, com entrada de vídeo composto AV/CVBS e alimentação nativa de 5 V, sem depender de conversores internos improvisados.

## Encontrei telas compatíveis com nossa ideia!

A pesquisa confirmou que existem monitores de 4,3 polegadas com vídeo composto e alimentação de 5 V. O problema é que a maioria dos modelos automotivos baratos vendidos no Brasil exige 12 V.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="CJEMicro RPI-43LCD-5V 4.3 composite monitor" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      <text weight="medium"><Link url="https://cjemicros.co.uk/micros/individual/newprodpages/prodinfo.php?prodcode=RPI-43LCD-5V">CJEMicro RPI-43LCD-5V</Link></text>
      <badge color="success">Melhor encaixe técnico</badge>
      Tela de 4,3", duas entradas RCA, PAL/NTSC, 480 × 272 pixels e alimentação de **5 V, aproximadamente 400 mA ou menos**. É uma versão modificada especificamente para 5 V.

      <text color="secondary" size="xs">£36,50, loja do Reino Unido; verificar frete e disponibilidade para o Brasil. <Cite ref="turn797055search2"/></text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Vitek VTM-LCD43-5A4 4.3 inch service monitor" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **<Link url="https://avsupply.com/ITM/30056/vtm-lcd43ta.html/">Vitek VTM-LCD43TA</Link>**

      Tela de 4,3", entrada CVBS, alimentação por mini-USB de 5 V e consumo declarado inferior a 3 W.

      <text color="secondary" size="xs">É um monitor de manutenção com bateria interna, mais volumoso e complexo do que precisamos. <Cite refs={["turn797055search1","turn797055search9"]}/></text>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="Adafruit 946 4.3 NTSC PAL TFT display" aspectRatio="4:3" maxWidth="132px"/>
    <box flex="1" gap={1}>
      **<Link url="https://www.adafruit.com/product/946">Adafruit 946</Link>**

      Monitor composto de 4,3". A Adafruit relatou funcionamento com 5 V em testes, mas a especificação técnica atual indica 6–12 V.

      <text color="secondary" size="xs">Descontinuado; não recomendaria como nossa escolha de produção. <Cite refs={["turn797055search8","turn797055search13"]}/></text>
    </box>
  </row>
</box>

## Quanto de energia precisaríamos?

Usando a tela CJEMicro como referência, podemos montar um orçamento inicial. Os valores da CPU abaixo são **reservas de projeto, não medições**.

{@body const [cpu,setCpu] = DIL.useState(900)}
{@body const [screen,setScreen] = DIL.useState(400)}
{@body const [reserve,setReserve] = DIL.useState(300)}
{@body const total = cpu+screen+reserve}
<box border radius="lg" padding={3} gap={3}>
  <title size="md">Estimativa interativa de consumo em 5 V</title>
  <box gap={1}>
    <row justify="between" align="center">
      <text weight="medium" size="sm">CPU, memórias e vídeo</text>
      <text tabularNums weight="medium">{cpu} mA</text>
    </row>
    <slider min={300} max={1800} step={100} value={cpu} onChange={setCpu}/>
  </box>
  <box gap={1}>
    <row justify="between" align="center">
      <text weight="medium" size="sm">Tela</text>
      <text tabularNums weight="medium">{screen} mA</text>
    </row>
    <slider min={200} max={800} step={50} value={screen} onChange={setScreen}/>
  </box>
  <box gap={1}>
    <row justify="between" align="center">
      <text weight="medium" size="sm">Reserva adicional</text>
      <text tabularNums weight="medium">{reserve} mA</text>
    </row>
    <slider min={100} max={600} step={50} value={reserve} onChange={setReserve}/>
  </box>
  <divider color="subtle"/>
  <grid columns={2} gap={3}>
    <grid-item>
      <text color="secondary" size="xs">Corrente total estimada</text>
      <title size="xl" tabularNums>{(total/1000).toFixed(2)} A</title>
    </grid-item>
    <grid-item>
      <text color="secondary" size="xs">Potência em 5 V</text>
      <title size="xl" tabularNums>{(total*5/1000).toFixed(2)} W</title>
    </grid-item>
  </grid>
  <text color={total<=3000?"success":"danger"} weight="medium" size="sm">{total<=3000?"Dentro de um orçamento de 5 V / 3 A.":"Acima de 5 V / 3 A: será necessário rever o projeto de alimentação."}</text>
</box>

## Como ficaria a alimentação USB-C

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 181" width="100%">
    <g fill="#64748b" fillOpacity=".1" stroke="#94a3b8">
      <rect x="7" y="12" width="95" height="43" rx="6"/>
      <rect x="120" y="12" width="103" height="43" rx="6"/>
      <rect x="242" y="12" width="81" height="43" rx="6"/>
      <rect x="196" y="108" width="127" height="40" rx="6"/>
      <rect x="7" y="108" width="150" height="40" rx="6"/>
    </g>
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <text x="54" y="29">Fonte USB-C</text><text x="54" y="43">5 V / 3 A</text>
      <text x="171" y="29">Entrada USB-C</text><text x="171" y="43">CC1 / CC2</text>
      <text x="282" y="29">Proteção</text><text x="282" y="43">+5V_SYS</text>
      <text x="82" y="124">CPU + memórias</text><text x="82" y="137">+ vídeo composto</text>
      <text x="259" y="124">Tela RCA</text><text x="259" y="137">5 V</text>
    </g>
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M102 34 H120 M223 34 H242 M282 55 V83 H82 V108 M282 83 H259 V108"/>
    </g>
    <text x="165" y="170" textAnchor="middle" fontSize="9" fill="currentColor">Arquitetura proposta, não esquemático final</text>
  </svg>
</box>

Para a PCB, precisamos de dois resistores de 5,1 kΩ, um em CC1 e outro em CC2, além de proteção contra ESD, sobrecorrente, filtragem e supervisão da alimentação. <Cite refs={["turn543643search0","turn543643search4"]}/>

Uma fonte USB-C de **5 V / 3 A (15 W)** seria nossa referência inicial. Não precisamos solicitar 9 V ou 12 V via USB-PD, mas o circuito deve respeitar a corrente anunciada pela fonte. <Cite ref="turn543643search2"/>

**Minha decisão para o ISA-1:** voltar à alimentação de 5 V, agora com entrada USB-C, e priorizar a tela CJEMicro como referência técnica. Antes de fechar a PCB, precisamos confirmar uma tela realmente comprável e calcular o consumo máximo dos componentes, especialmente do circuito de vídeo.

Assim mantemos o computador compacto, com uma única fonte de celular e sem adicionar um conversor de 12 V desnecessário.

## user — bbb21e15-f792-49b1-a7e7-4c92774c2827

Qual o preço dessa tela? A outra 12v achei por r$67

## assistant — f8d32913-1649-4881-a9ea-dc59a4f4b683

{"content_type": "thoughts", "source_analysis_msg_id": "a581c92f-936d-4081-9a2e-a67ed33fabf6", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 5 sites"}]}

## assistant — c42a1207-cb5a-4574-a40c-7762cb140c00

{"content": "Pensou por 12s", "content_type": "reasoning_recap"}

## assistant — c3f84bb5-6042-46f8-81a5-0f1d39358bee

A tela **CJEMicro RPI-43LCD-5V** que encontramos custa **£36,50**, sem frete nem impostos.

Isso equivale a aproximadamente **R$ 260**, considerando uma cotação ilustrativa de R$ 7,10 por libra — ou seja, quase quatro vezes os **R$ 67** da tela de 12 V que você encontrou.

E ainda teríamos o custo da importação.

Para o ISA-1, essa diferença é grande o suficiente para reconsiderarmos a escolha da alimentação.

Conferi novamente: o preço oficial continua em **£36,50**, aproximadamente **R$ 284** pela cotação de 20/11/2026, antes de frete e impostos. <Cite refs={["turn852049search8","turn852049search11"]}/>

Encontrei também uma opção automotiva de 4,3" com entrada AV, anunciada no Mercado Livre:

<row align="center" gap={3}>
  <AsyncImage ref="turn852049product0" maxWidth="112px" aspectRatio="4:3"/>
  <box flex="1" gap={1}>
    **<Entity ref="turn852049product0" value={turn852049product0.title} category="product"/>**

    <title size="lg" color="default">{turn852049product0.displayed_price}</title>
    <text color="secondary" size="xs">{turn852049product0.merchant} · Alimentação 12/24 V anunciada</text>
  </box>
</row>

**Minha recomendação para o ISA-1:** eu não pagaria R$ 284 por uma tela de 5 V quando temos uma de 12 V por R$ 67.

Podemos manter o computador alimentado por USB-C e usar um pequeno conversor elevador de 5 V para 12 V exclusivamente para a tela, desde que seu consumo permita. Assim, preservamos a ideia da fonte de celular sem encarecer tanto o projeto.

Se você me mandar o link da tela de R$ 67, consigo verificar as especificações e dimensionar esse conversor para ela.

## user — bbb2176b-1f15-44da-b89a-8f0f1e6c8c74

Vamos seguir então com a tela 12v 🫪
Eu tenho um carregador original Motorola de 33w
Acho ele aguenta

## assistant — 210c056e-86b7-4dca-ba87-a5d59b46037c

🥳 Fechado! **O ISA-1 terá alimentação USB-C de 5 V e uma tela RCA de 4,3 polegadas alimentada em 12 V.**

E seu carregador original Motorola de 33 W é um ótimo candidato! Só precisamos verificar um detalhe importante antes de aprová-lo.

## Como ficará a alimentação

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 204" width="100%">
    <g fill="#64748b" fillOpacity=".10" stroke="#94a3b8">
      <rect x="7" y="12" width="105" height="44" rx="7"/>
      <rect x="135" y="12" width="194" height="44" rx="7"/>
      <rect x="135" y="85" width="194" height="44" rx="7"/>
      <rect x="135" y="154" width="194" height="44" rx="7"/>
    </g>
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <text x="59" y="30">Motorola</text><text x="59" y="44">33 W USB-C</text>
      <text x="232" y="30">USB-C + proteção</text><text x="232" y="44">5 V de entrada</text>
      <text x="232" y="102">5V_SYS</text><text x="232" y="116">CPU + memórias + vídeo</text>
      <text x="232" y="171">Boost 5 V → 12 V</text><text x="232" y="185">Tela RCA 4,3"</text>
    </g>
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M112 34 H135 M232 56 V85 M232 129 V154"/>
    </g>
  </svg>
</box>

O conversor *boost* elevará os 5 V para 12 V somente para a tela. Isso permite aproveitar o monitor econômico de R$ 67.

## O carregador de 33 W aguenta?

**Possivelmente sim, mas 33 W é a potência máxima anunciada, não necessariamente a potência disponível em 5 V.**

Por exemplo:

| Saída do carregador | Potência |
|---|---:|
| 5 V × 2 A | 10 W |
| 5 V × 3 A | 15 W |
| 11 V × 3 A | 33 W |

O ISA-1 não poderá utilizar automaticamente os 33 W apenas conectando o cabo USB-C. Isso depende dos perfis de alimentação e do protocolo de negociação suportados pelo carregador.

Para ilustrar, se a tela consumir 12 V × 0,5 A (6 W), o conversor boost precisará de aproximadamente 1,4 A em 5 V, considerando 85% de eficiência. A CPU consumirá corrente adicional.

Portanto, precisamos dimensionar o sistema completo antes de afirmar que o carregador é suficiente.

## Decisões da alimentação

- **Entrada:** USB-C, inicialmente 5 V.
- **CPU e memórias:** barramento de 5 V com proteção e supervisão.
- **Tela:** 12 V por conversor boost dedicado.
- **Fonte:** Motorola 33 W, candidata, aguardando confirmação dos perfis.
- **PCB:** manteremos todos os circuitos de alimentação na placa principal.

A vantagem é que o ISA-1 continuará utilizando uma única fonte externa, sem precisar de dois adaptadores.

**Uma informação que preciso agora:** consegue me dizer o que está escrito na linha **OUTPUT / SAÍDA** do seu carregador Motorola de 33 W? Pode mandar uma foto da etiqueta também.

Com isso verificamos se ele entrega 5 V / 3 A, se precisamos negociar USB-PD ou se será melhor ajustar nossa arquitetura para aproveitar a potência disponível.

## user — bbb21ee7-d0ba-4482-a08a-1f52029ed3d1

Agora não consigo
Mas eh um carregador Motorola original
Depois vou pegar ele

## assistant — 9ce18172-4612-4dde-8031-ff2fe1476477

Tranquilo! 😁🔧 Não precisamos do carregador agora para continuar o ISA-1.

Vamos manter estas decisões:

- **Entrada USB-C**, inicialmente com 5 V.
- **CPU e memórias:** alimentação de 5 V.
- **Tela RCA de 4,3":** alimentação de 12 V por conversor boost.
- **Carregador Motorola 33 W:** candidato, aguardando confirmação da saída de 5 V.

Enquanto isso, podemos continuar projetando e testando a alimentação, incluindo proteção contra curto-circuito, filtragem, supervisor de tensão e conversor boost.

Vou considerar **5 V / 2 A como cenário conservador de análise**, mas não como capacidade confirmada do seu carregador. Também avaliaremos 5 V / 3 A.

Quando você pegar o carregador, conferimos a etiqueta e ajustamos o projeto se necessário.

**O objetivo continua sendo alimentar todo o ISA-1 com um único cabo USB-C**, sem comprometer a estabilidade da CPU ou a imagem da tela. 🥳

## user — bbb21f85-389e-42f5-8859-90e7e7c081cd

Perfeito! Vamos seguir então
O que mais vamos precisar agora? Te interrompi para falar da fonte

## assistant — 20a6a3e9-7023-45d9-ac43-469acdf38067

🥳 Estamos avançando bem com o ISA-1! E você interrompeu justamente em um ponto importante: a alimentação precisa ser definida antes de fecharmos o esquemático e o layout da PCB.

Mas **não precisamos esperar pelo carregador Motorola para continuar**.

## Onde paramos

Nossa última etapa técnica foi a **revisão 5.5**, na qual começamos a definir a alimentação, o supervisor de tensão e a proteção das memórias.

Depois, decidimos mudar a arquitetura para USB-C e manter a tela RCA de 12 V, por ser muito mais econômica.

<box border radius="lg" padding={3} gap={2}>
  <title size="md">Estado atual do ISA-1</title>
  <row align="center" justify="between">
    <text weight="medium">Arquitetura da CPU de 8 bits</text>
    <badge>Definida parcialmente</badge>
  </row>
  <row align="center" justify="between">
    <text weight="medium">PC de 16 bits e reset</text>
    <badge>Testes lógicos</badge>
  </row>
  <row align="center" justify="between">
    <text weight="medium">Alimentação USB-C</text>
    <badge>Em projeto</badge>
  </row>
  <row align="center" justify="between">
    <text weight="medium">Vídeo composto colorido</text>
    <badge>Integração pendente</badge>
  </row>
  <row align="center" justify="between">
    <text weight="medium">Esquemático elétrico completo</text>
    <badge>Não concluído</badge>
  </row>
</box>

## O que precisamos fazer agora

Eu dividiria os próximos trabalhos em cinco etapas, mantendo nossa preocupação com a quantidade de componentes e a confiabilidade.

<box gap={3}>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="plug-zap" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Revisão 5.6 — Alimentação USB-C e boost**

      Dimensionar a entrada de 5 V, o conversor de 12 V para a tela, as proteções e o consumo máximo. Testar também o comportamento em quedas de tensão e curtos-circuitos.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="cpu" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Revisão 5.7 — Integração dos registradores EA/RET**

      Conectar os registradores de 16 bits ao PC e verificar operações de salto, CALL e RET, inclusive quando houver acessos à pilha.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="workflow" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Revisão 5.8 — Simulação integrada da CPU**

      Ampliar nossa bancada virtual para executar instruções reais, movimentar dados entre registradores e detectar conflitos de barramento.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="monitor" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Revisão 5.9 — Vídeo composto colorido**

      Validar a geração de sincronismo, temporização, cores e acesso à memória de vídeo, considerando a carga real da CPU.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="circuit-board" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Revisão 6.0 — Primeira integração geral**

      Consolidar CPU, memória, vídeo, teclado, armazenamento e alimentação em um projeto elétrico, com auditoria de pinagem e preparação para ERC.
    </box>
  </row>
</box>

## Uma questão técnica que quero resolver

Nossa fonte USB-C precisa alimentar duas cargas muito diferentes: a lógica digital de 5 V e a tela de 12 V através de um conversor chaveado.

Não quero que o conversor da tela introduza ruído suficiente para provocar instabilidade na CPU ou interferência no vídeo composto.

Por isso, na revisão 5.6, vamos avaliar separação das trilhas de alimentação, desacoplamento, proteção e a sequência de inicialização.

Também precisamos conferir se a fonte USB-C oferece corrente suficiente em 5 V. Os 33 W anunciados pelo carregador não garantem 33 W nesse perfil.

**Minha recomendação é continuarmos pela revisão 5.6**, sem alterar as decisões já tomadas sobre a CPU, a PCB única, o teclado separado e a EEPROM removível.

Depois de fechar a alimentação no nível de projeto, voltamos diretamente à integração da CPU, que era nosso trabalho antes dessa conversa sobre a fonte. 😎

## user — bbb2116c-9aaf-434b-9e27-4ca79c1f9b38

Fechado, se ficar ruim, ou der interferência, eu consigo uma alimentação a parte pra tela, tranquilo
Pode continuar com seus planos

## assistant — 22df9f17-a194-40d3-896f-ab80143733cf

{"content_type": "thoughts", "source_analysis_msg_id": "781e0b45-89c8-414b-9ab6-537c4124d79f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos, calculou cenários, corrigiu potência e redigiu relatório USB-C"}]}

## assistant — 4a7e426b-4c0d-4500-ae1b-3473c26a3386

{"content": "Pensou por 47s", "content_type": "reasoning_recap"}

## assistant — d192afee-f7f0-47bf-9819-6e956b0d34c6

🥳 **ISA-1 — Revisão 5.6: alimentação com opção de fonte independente para a tela**

Essa flexibilidade é muito útil. Vamos projetar o ISA-1 para funcionar com uma única fonte USB-C, mas deixar prevista uma alternativa caso o conversor de 12 V cause interferência ou consuma corrente demais.

A decisão principal é: **a alimentação da tela poderá ser separada sem modificar a CPU nem refazer a placa.**

## Primeiro teste: orçamento de corrente

Executei 72 cenários combinando consumo estimado da CPU, consumo da tela, eficiência do conversor e limites de 2 A ou 3 A na entrada USB.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>9/36</title>
      <text color="secondary" size="xs">Cenários dentro de 5 V / 2 A</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>31/36</title>
      <text color="secondary" size="xs">Cenários dentro de 5 V / 3 A</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Os consumos são hipóteses de engenharia, não medições dos componentes definitivos. Os resultados verificam apenas corrente média calculada.</text>
</box>

Por exemplo, supondo CPU e lógica consumindo 0,9 A, tela consumindo 0,4 A em 12 V e conversor com 85% de eficiência, a entrada de 5 V precisaria fornecer aproximadamente **2,18 A**, incluindo uma reserva ilustrativa de 0,15 A.

Nesse cenário, uma fonte de 5 V / 2 A seria insuficiente; uma de 5 V / 3 A teria margem de corrente, ainda sujeita a picos e perdas adicionais.

## Como vamos conectar as duas opções de alimentação

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 198" width="100%">
    <g fill="#64748b" fillOpacity=".1" stroke="#94a3b8">
      <rect x="6" y="12" width="95" height="43" rx="6"/>
      <rect x="124" y="12" width="199" height="43" rx="6"/>
      <rect x="6" y="89" width="137" height="43" rx="6"/>
      <rect x="182" y="89" width="141" height="43" rx="6"/>
      <rect x="182" y="157" width="141" height="35" rx="6"/>
    </g>
    <g fill="currentColor" fontSize="10" textAnchor="middle">
      <text x="53" y="30">USB-C 5 V</text><text x="53" y="43">Fonte Motorola</text>
      <text x="223" y="30">Proteção + 5V_SYS</text><text x="223" y="43">CPU e memórias</text>
      <text x="74" y="106">Boost 5 → 12 V</text><text x="74" y="119">desligável</text>
      <text x="252" y="106">Seletor físico</text><text x="252" y="119">uma fonte por vez</text>
      <text x="252" y="179">Tela RCA 12 V</text>
    </g>
    <g fill="none" stroke="#0d9488" strokeWidth="2">
      <path d="M101 33 H124 M223 55 V71 H74 V89 M143 110 H182 M252 132 V157"/>
    </g>
    <path d="M145 72 H164 V100 H182" stroke="#64748b" strokeWidth="1.5" strokeDasharray="4 4" fill="none"/>
    <text x="163" y="65" textAnchor="middle" fontSize="9" fill="currentColor">12 V externo</text>
  </svg>
  <caption>Diagrama funcional. A entrada externa de 12 V terá proteção própria e seleção que impede interligar duas fontes.</caption>
</box>

Isso evita depender de um único arranjo. Se o boost provocar ruído, poderemos desligá-lo e alimentar a tela externamente.

Também vamos tomar cuidado com o terra do vídeo composto: usar duas fontes não elimina automaticamente interferências e pode criar caminhos de retorno indesejados.

## Arquivos da revisão 5.6

- [Relatório técnico e decisões de alimentação](sandbox:/mnt/data/isa1/ISA-1_REV56_USB_C_TELA_12V.md)
- [Bancada de cálculo em Python](sandbox:/mnt/data/isa1/isa1_rev56_power_budget.py)
- [72 cenários de consumo — CSV](sandbox:/mnt/data/isa1/isa1_rev56_scenarios.csv)
- [Resultados dos testes — JSON](sandbox:/mnt/data/isa1/isa1_rev56_results.json)

**Uma ressalva sobre USB-C:** os resistores de identificação da entrada não garantem, por si só, autorização para consumir 3 A. Precisamos respeitar a corrente anunciada pela fonte ou implementar a negociação apropriada.

### Próximo passo: revisão 5.7

Agora podemos voltar ao coração do ISA-1: **integrar os registradores EA e RET ao contador de programa de 16 bits**.

Quero verificar especialmente se conseguimos simplificar os multiplexadores sem prejudicar `CALL`, `RET` ou os acessos à pilha.

A alimentação ficou com uma arquitetura flexível, e não precisamos escolher agora entre uma ou duas fontes. A decisão definitiva poderá ser tomada após os testes de consumo e interferência.

## user — bbb21dba-0a4a-4f07-b143-b00d1b825482

Pode seguir

## assistant — 02141281-50b5-46e3-af74-ec4334c8147c

{"content_type": "thoughts", "source_analysis_msg_id": "22acfb1e-0d48-4a63-b12a-1358f17d7b71", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou integração ISA-1 e criou testes para CALL e RET"}]}

## assistant — 732a9349-1b90-439c-94a6-864a28c344ad

{"content": "Pensou por 38s", "content_type": "reasoning_recap"}

## assistant — dd5b569c-5455-4a08-8e63-9067155fa2fd

🥳🔧 **ISA-1 — Revisão 5.7 concluída! Voltamos ao coração da CPU.**

Com a alimentação USB-C e a opção de fonte independente para a tela encaminhadas, retomei a integração dos registradores **EA e RET** com o contador de programa de 16 bits.

E conseguimos avançar nos testes de `CALL` e `RET`!

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>159.873</title>
      <text color="secondary" size="xs">Verificações comportamentais aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>65.536</title>
      <text color="secondary" size="xs">Endereços de retorno testados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>32</title>
      <text color="secondary" size="xs">Níveis de chamadas aninhadas testados</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Divergências detectadas</text>
    </grid-item>
  </grid>
</box>

## O que validamos

Nosso modelo agora utiliza uma memória de 64 KB representada byte a byte para testar a pilha, em vez de simplesmente guardar os endereços de retorno em uma lista.

Durante `CALL`, a CPU preserva o endereço de retorno na pilha e carrega o destino. Durante `RET`, recupera os dois bytes e reconstrói o endereço.

Também comparei uma alternativa para reduzir os multiplexadores.

| Arquitetura | Resultado |
|---|---|
| EA + RET + quatro 74HC157 | Mantida |
| EA + RET + registrador TARGET | Não demonstrou economia |

A alternativa TARGET exigiria mais dois registradores de 8 bits e ainda precisaria de um caminho para selecionar os dados. Portanto, **não vamos adicionar componentes sem uma vantagem comprovada**.

## Uma observação importante

Esses testes validam o comportamento proposto, não a execução elétrica. Ainda precisamos conectar fisicamente os registradores ao barramento, definir os sinais de carga e reconciliar a sequência de empilhamento com o conjunto definitivo de instruções.

## Arquivos da revisão 5.7

- [Relatório técnico completo](sandbox:/mnt/data/isa1/ISA-1_REV57_INTEGRACAO_EA_RET.md)
- [Simulador de CALL/RET em Python](sandbox:/mnt/data/isa1/isa1_rev57_call_ret.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev57_results.json)

## Próximo passo — Revisão 5.8

Agora vamos integrar **CPU, barramento de dados e SRAM** na bancada virtual.

Quero testar situações mais próximas do hardware: leitura e escrita de bytes, habilitação dos buffers, conflitos entre dispositivos, acessos à pilha e bloqueio de escrita durante reset.

Esse será um avanço importante porque passaremos a verificar não apenas *o que* a CPU calcula, mas também *como os dados circulam entre os componentes*.

**O ISA-1 está progredindo.** Ainda falta bastante integração elétrica antes de fabricar, mas estamos transformando as decisões da arquitetura em comportamentos testáveis, um subsistema de cada vez. 🥳

## user — bbb21f65-ae48-4377-bfa4-1217eb395d68

Pode seguir com o próximo passo

## assistant — 1d84e921-71b1-4908-bfe1-6f6ac26a7677

{"content_type": "thoughts", "source_analysis_msg_id": "467270c0-e3e0-4ed6-8b6c-19b53f1b39cd", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementou simulador de barramento e validou endereços da pilha CALL/RET"}]}

## assistant — 06a391e4-598e-4c21-b23f-af70b2490d3c

{"content": "Pensou por 36s", "content_type": "reasoning_recap"}

## assistant — 6fc7b50e-fd35-435a-b23e-33acda1bd79c

🥳🔧 **ISA-1 — Revisão 5.8: CPU, barramento e SRAM na mesma bancada virtual!**

Avançamos para testar como os dados circulam entre a CPU e a memória, incluindo acessos à pilha, leitura, escrita e conflitos de barramento.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>35.087</title>
      <text color="secondary" size="xs">Verificações comportamentais aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Falhas nos testes executados</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Modelo de barramento e SRAM aprovado no escopo testado
  </row>
</box>

O simulador agora utiliza uma SRAM de **32 KB organizada em bytes**, com endereços de `0000h` a `7FFFh`.

Também verificamos chamadas aninhadas com `CALL` e `RET`, incluindo a gravação e recuperação dos endereços de retorno na memória.

Uma diferença importante em relação às revisões anteriores: o modelo agora **detecta explicitamente dois dispositivos tentando dirigir o barramento ao mesmo tempo**.

## O que conseguimos testar

| Teste | Resultado |
|---|---|
| Leitura e escrita de 8 bits | Aprovado |
| Bloqueio de escrita durante reset | Aprovado no modelo |
| Dois dispositivos dirigindo o barramento | Conflito detectado |
| Leitura e escrita simultâneas | Operação rejeitada |
| CALL/RET com 32 níveis de aninhamento | Aprovado |
| Temporização elétrica da SRAM | Pendente |
| Arbitragem com vídeo | Pendente |

## Uma questão importante que apareceu

Precisamos distinguir o **endereço local da SRAM** do mapa completo de endereços da CPU.

Nosso processador tem endereçamento de 16 bits, mas a SRAM possui 32 KB. Ainda precisamos decidir exatamente como ROM, RAM, vídeo e dispositivos de entrada e saída serão selecionados.

Também precisamos prever intervalos seguros na troca de quem controla o barramento. Na simulação Python, essa troca é instantânea; nos circuitos 74HC reais, não será.

## Arquivos da revisão 5.8

- [Relatório técnico completo](sandbox:/mnt/data/isa1/ISA-1_REV58_BARRAMENTO_SRAM.md)
- [Bancada virtual em Python](sandbox:/mnt/data/isa1/isa1_rev58_bus_bench.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev58_results.json)
- [Registro de sinais por ciclo em CSV](sandbox:/mnt/data/isa1/isa1_rev58_trace.csv)

## Próxima revisão — 5.9: vídeo composto colorido

Vamos trabalhar no subsistema que fará o ISA-1 mostrar imagens na tela RCA de 4,3 polegadas.

A prioridade será estudar a temporização do sinal composto, a geração de cores e a relação entre acesso à memória de vídeo e execução da CPU.

**Minha intenção é preservar uma CPU útil e independente, sem sacrificar seus recursos para gerar vídeo.** Se houver uma solução que economize componentes sem comprometer isso, vamos compará-la e testá-la.

O avanço desta revisão é concreto: agora temos uma bancada que verifica não apenas valores calculados, mas também regras de circulação de dados. Ainda falta conectar essas regras aos sinais e aos tempos dos componentes físicos.

## user — bbb218c3-6d7d-4865-8cfe-ecb8836de69c

Esse conflito que deu no barramento e escritas simultâneas
Precisamos de ajuste? 

## assistant — e463acfa-f8a1-4527-861f-5a4cd697cbfe

{"content_type": "thoughts", "source_analysis_msg_id": "49b7aca0-e2c9-42a8-a69d-284e1b3199f9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Lendo script e resultados do benchmark"}]}

## assistant — 604f254d-2138-4ff9-b172-97214057fc19

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — 82fa6d6d-eb4a-4e84-8884-194522dcdc86

**Sim, precisamos fazer alguns ajustes preventivos no projeto, mas os testes não indicaram uma falha na CPU.** 😎🔧

Revisei o código e o relatório da revisão 5.8. A boa notícia é que os conflitos foram **provocados intencionalmente nos testes**, para verificar se nossa bancada virtual conseguia identificá-los.

Ela identificou corretamente as situações proibidas.

## O que aconteceu nos testes?

| Situação | Resultado | Precisamos corrigir? |
|---|---|---|
| CPU e EEPROM dirigindo o barramento juntas | Conflito detectado | Prevenir no hardware |
| CPU tentando escrever enquanto a SRAM dirige o barramento | Conflito detectado | Prevenir no hardware |
| Leitura e escrita simultâneas | Operação rejeitada | Garantir exclusão elétrica |
| Escrita durante reset | Bloqueada no modelo | Validar eletricamente |
| CALL/RET usando a SRAM | Funcionou | Integrar ao microcódigo |

Portanto, **não foram seis falhas que passaram despercebidas**. Foram seis testes negativos que o simulador rejeitou como esperado.

## O que vamos ajustar

### 1. Controle exclusivo do barramento

Precisamos garantir que apenas um componente possa fornecer dados ao barramento em cada instante.

Por exemplo:

```text
Ciclo de leitura:
CPU       → alta impedância
SRAM      → fornece dados
EEPROM    → alta impedância

Ciclo de escrita:
CPU       → fornece dados
SRAM      → recebe dados
EEPROM    → alta impedância
```

Os buffers tri-state 74HC245 e 74HC244 que já consideramos no ISA-1 poderão ajudar a implementar esse controle.

### 2. Intervalo seguro entre operações

Existe um detalhe que nosso simulador ainda não representa: os componentes reais não desligam suas saídas instantaneamente.

Quando passamos de uma leitura da SRAM para uma operação em que a CPU fornece dados, pode ocorrer uma pequena sobreposição.

Minha proposta é introduzir uma fase de liberação:

<box border radius="lg" padding={3} gap={2}>
  <title size="md">Sequência segura de troca do barramento</title>
  <grid columns={4} gap={1}>
    {#each [{n:"T1",t:"Leitura",s:"SRAM ativa"},{n:"T2",t:"Liberação",s:"Todos em Z"},{n:"T3",t:"Escrita",s:"CPU ativa"},{n:"T4",t:"Finalização",s:"Desativar"}] as step}
      <grid-item>
        <box background="surface-secondary" radius="md" padding={2} align="center" gap={1}>
          <text weight="medium" size="sm">{step.n}</text>
          <text size="2xs" weight="medium" textAlign="center">{step.t}</text>
          <text size="2xs" color="secondary" textAlign="center">{step.s}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Sequência conceitual. A duração necessária de cada fase dependerá dos datasheets e da frequência de clock.</caption>
</box>

Não precisamos necessariamente adicionar um ciclo inteiro a todas as operações. Podemos estudar uma implementação com fases de clock, desde que a temporização seja comprovada.

### 3. Bloqueio físico das escritas

Também precisamos garantir que SRAM e EEPROM nunca recebam comandos de escrita simultaneamente por erro de decodificação.

A solução será combinar a seleção exclusiva de memória com permissões de escrita e proteção durante reset.

## Minha decisão para o ISA-1

**Vamos manter a arquitetura atual e reforçar a lógica de controle.** Não há motivo para redesenhar a CPU nem acrescentar componentes antes de avaliar os sinais que já temos.

Na próxima revisão, vou priorizar:

1. Decodificação exclusiva de SRAM, EEPROM e dispositivos.
2. Controle dos buffers tri-state.
3. Testes de transição entre leitura e escrita.
4. Verificação de escrita bloqueada durante reset e queda de alimentação.

Depois disso, avançamos para o vídeo colorido, que também precisará compartilhar recursos com a CPU.

**Resumo:** nosso simulador fez exatamente o que deveria. Encontrou operações perigosas quando as provocamos. Agora precisamos garantir que essas situações não possam ocorrer no circuito real, inclusive durante as transições entre ciclos.

## user — bbb21bf4-a460-4ba9-ba5b-2cb8ed18d0b4

Ahh entendi
Vamos seguir então

## assistant — d1a07d2e-f286-4194-9db2-9d85feb73d51

{"content_type": "thoughts", "source_analysis_msg_id": "b6277cdb-890d-4623-8fff-519cf2f51f52", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Implementada e documentada arbitragem segura do barramento ISA-1"}]}

## assistant — 25634cbe-75e9-482d-971f-d8fdaf1f74f1

{"content": "Pensou por 31s", "content_type": "reasoning_recap"}

## assistant — f668564d-6ccb-4494-bf93-0c6d36d0dc90

🥳🔧 **ISA-1 — Revisão 5.9: proteção do barramento**

Retomamos exatamente de onde paramos: os conflitos de leitura e escrita identificados na revisão 5.8.

Desta vez, implementei uma máquina de estados para controlar qual dispositivo pode dirigir o barramento de dados de 8 bits.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>210.744</title>
      <text color="secondary" size="xs">Verificações executadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Falhas no modelo</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Exclusividade lógica do barramento aprovada
  </row>
</box>

## A melhoria implementada

Agora, quando o barramento muda de proprietário, o controlador passa por um estado em que **nenhum dispositivo pode dirigir os dados**.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={3} gap={2}>
    {#each [{n:"T1",t:"SRAM",s:"Fornece dados"},{n:"T2",t:"Alta impedância",s:"Todos desligados"},{n:"T3",t:"CPU",s:"Fornece dados"}] as x}
      <grid-item>
        <box background="surface-secondary" padding={2} radius="md" align="center" gap={1}>
          <text color="secondary" size="xs">{x.n}</text>
          <text weight="medium" size="sm" textAlign="center">{x.t}</text>
          <text size="2xs" color="secondary" textAlign="center">{x.s}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Sequência comportamental de troca de proprietário. A duração elétrica necessária ainda precisa ser calculada.</caption>
</box>

Também testei interrupções de alimentação, CPU inativa, endereço inválido e solicitações de escrita. Nesses casos, o modelo desliga os drivers e bloqueia a escrita.

**Isso resolve a exclusividade no simulador**, mas ainda não prova que os buffers reais terão tempo suficiente para desligar antes que outros sejam habilitados.

## Arquivos da revisão 5.9

- [Relatório técnico e pendências](sandbox:/mnt/data/isa1/ISA-1_REV59_ARBITRAGEM_BARRAMENTO.md)
- [Simulador de arbitragem em Python](sandbox:/mnt/data/isa1/isa1_rev59_bus_guard.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev59_results.json)
- [Registro dos sinais por ciclo](sandbox:/mnt/data/isa1/isa1_rev59_trace.csv)

## O próximo passo: revisão 6.0

Agora temos duas tarefas importantes que precisam caminhar juntas: **definir o mapa de memória de 64 KB e integrar o vídeo composto colorido**.

Quero avaliar uma arquitetura com memória de vídeo dedicada. Isso poderia permitir que a imagem fosse gerada continuamente sem interromper a CPU a cada pixel, embora possa exigir mais componentes.

Também vamos preservar nossos requisitos: CPU completa de 8 bits, endereçamento de 16 bits, SRAM de 32 KB, EEPROM removível e uma única PCB principal.

**Situação atual:** eliminamos os conflitos no modelo de controle, mas ainda precisamos transformar esse comportamento em circuitos com temporização comprovada.

Estamos chegando à fase em que as decisões de arquitetura precisam se encaixar umas nas outras. É justamente agora que vale a pena testar com rigor, antes de desenhar a placa definitiva. 🥳

## user — bbb21879-b420-4bcb-b0e9-4a768e2081b0

Pode seguir com a revisão da arquitetura de vídeo

## assistant — 7dddcbcd-5e6b-4eb8-a94d-32f42fd185d1

{"content_type": "thoughts", "source_analysis_msg_id": "d8158e36-1054-4186-bdf9-5bba44053ba9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou e corrigiu arquitetura de vídeo, VRAM e mapeamento de memória"}]}

## assistant — 41a05146-19e7-4fb9-b115-56ab6cf79f28

{"content": "Pensou por 36s", "content_type": "reasoning_recap"}

## assistant — df59cd7c-e2da-4697-be74-b9780355cdb0

🥳🖥️ **ISA-1 — Revisão 6.0: primeira arquitetura de vídeo colorido!**

Avançamos para um dos subsistemas mais importantes do nosso computador: gerar imagens coloridas na tela RCA de 4,3 polegadas, sem transformar a CPU em um simples controlador de vídeo.

Minha proposta é utilizar **memória de vídeo dedicada**, preservando os 32 KB de SRAM principal.

## 1. Arquitetura proposta

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 220" width="100%">
    <g fill="#64748b" fillOpacity=".1" stroke="#94a3b8">
      <rect x="7" y="13" width="100" height="44" rx="6"/>
      <rect x="127" y="13" width="206" height="44" rx="6"/>
      <rect x="7" y="92" width="137" height="48" rx="6"/>
      <rect x="164" y="92" width="169" height="48" rx="6"/>
      <rect x="164" y="168" width="169" height="40" rx="6"/>
    </g>
    <g fontSize="11" textAnchor="middle" fill="currentColor">
      <text x="57" y="31">CPU 8 bits</text><text x="57" y="45">ISA-1</text>
      <text x="230" y="31">SRAM principal</text><text x="230" y="45">32 KB</text>
      <text x="75" y="110">VRAM dedicada</text><text x="75" y="125">8 KB</text>
      <text x="248" y="110">Controlador de vídeo</text><text x="248" y="125">pixels + sincronismo</text>
      <text x="248" y="184">Codificador CVBS</text><text x="248" y="198">Tela RCA colorida</text>
    </g>
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M107 35 H127"/>
      <path d="M57 57 V76 H75 V92"/>
      <path d="M144 116 H164"/>
      <path d="M248 140 V168"/>
    </g>
  </svg>
  <caption>Arquitetura funcional preliminar, ainda não um circuito elétrico.</caption>
</box>

A memória de vídeo seria separada da RAM principal. Isso evita que a geração da imagem dispute diretamente cada acesso à memória de programas e dados.

Porém, uma SRAM de vídeo convencional ainda precisará ser compartilhada entre CPU e controlador de vídeo. Vamos resolver essa arbitragem antes de aprovar o circuito.

## 2. Resolução inicial proposta

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>128 × 96</title>
      <text color="secondary" size="xs">Resolução lógica</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>16</title>
      <text color="secondary" size="xs">Índices de cor por pixel</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>6 KB</title>
      <text color="secondary" size="xs">Framebuffer</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>2 KB</title>
      <text color="secondary" size="xs">VRAM restante</text>
    </grid-item>
  </grid>
</box>

<box gap={2}>
  <text weight="medium" size="sm">Exemplo de imagem lógica com 16 índices de cor</text>
  <svg viewBox="0 0 256 192" width="100%" xmlns="http://www.w3.org/2000/svg">
    {#each Array.from({length:12},(_,y)=>Array.from({length:16},(_,x)=>({x,y,c:["#101b39","#20466c","#3e7295","#76a4ba","#d7a67e","#edc68a","#397d65","#63aa74","#c6dc8c","#4b4269","#80628c","#b58eac","#7c3d4e","#bf625e","#e7e1d5","#f5f5f0"][(x*3+y*2)%16]})).flat() as p}
      <rect x={p.x*16} y={p.y*16} width="16" height="16" fill={p.c}/>
    {/each}
  </svg>
  <caption>Ilustração da organização de pixels indexados; não é uma captura do hardware.</caption>
</box>

Essa resolução é um ponto de partida, não uma limitação definitiva. Precisamos comparar o custo dos componentes com alternativas de maior resolução.

## 3. Primeiros testes concluídos

<box border radius="lg" padding={3} gap={2}>
  <title size="2xl" tabularNums>160.000</title>
  <text color="secondary" size="sm">Verificações digitais executadas</text>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Nenhuma falha encontrada no escopo testado
  </row>
</box>

Validamos o empacotamento de dois pixels por byte, os endereços do framebuffer, uma simulação simplificada de acesso à VRAM e a exclusividade de quatro regiões candidatas do mapa de memória.

O modelo de arbitragem não considera os atrasos reais dos chips nem demonstra que conseguiremos atualizar a imagem na velocidade necessária.

## 4. Encontramos uma decisão importante sobre a EEPROM

Para acomodar 32 KB de RAM, 8 KB de vídeo e os dispositivos, propus inicialmente uma janela de 16 KB para ROM.

Mas nossa EEPROM removível possui **32 KB físicos**, incluindo os espaços reservados para salvar dados.

Isso significa que precisamos de um mecanismo de seleção de bancos ou de outro mapa de memória que preserve toda a capacidade.

Não vou fechar esse mapa até verificarmos o boot, o acesso aos programas e a gravação dos dois espaços de salvamento.

## 5. Arquivos da revisão 6.0

- [Relatório técnico da arquitetura de vídeo](sandbox:/mnt/data/isa1/ISA-1_REV60_ARQUITETURA_VIDEO.md)
- [Simulador digital em Python](sandbox:/mnt/data/isa1/isa1_rev60_video_arch.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev60_video_results.json)

## Próxima revisão — 6.1

Agora vem a parte mais delicada: **transformar os pixels digitais em um sinal de vídeo composto realmente colorido**.

Precisamos escolher o padrão inicial PAL ou NTSC, avaliar um codificador de vídeo adequado, definir o clock de pixels e calcular os acessos necessários à VRAM.

Também compararemos o custo de usar SRAM convencional com buffer de linha versus alternativas de memória de vídeo.

**Minha prioridade será manter o vídeo independente da execução da CPU, sem aumentar desnecessariamente a quantidade de circuitos integrados.**

Estamos avançando, mas a geração elétrica de vídeo colorido ainda não foi demonstrada. Essa será uma das validações decisivas antes da fabricação do ISA-1.

## user — bbb21815-7291-4166-9d50-6a4b54807d77

Perfeito! Pode seguir

## assistant — 45d67ebd-c45b-425b-8e29-6010dd38607e

{"content_type": "thoughts", "source_analysis_msg_id": "0d833337-267a-4fa0-88ec-1c83be60e733", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Documentei arquitetura, temporização de vídeo e VRAM NTSC"}]}

## assistant — 96b326a2-327a-4c32-9de5-b1fa027e6fdf

{"content": "Pensou por 32s", "content_type": "reasoning_recap"}

## assistant — 4e63302b-27d6-42c0-b964-1309b55d6b98

🥳🖥️ **ISA-1 — Revisão 6.1: temporização do vídeo e acesso à VRAM**

Vamos avançar mantendo uma exigência fundamental: **a imagem precisa continuar estável mesmo quando a CPU estiver ocupada executando BASIC, jogos ou acessando a EEPROM**.

A revisão 6.0 estabeleceu uma boa base: framebuffer de 128 × 96 pixels, 16 índices de cor e 8 KB de VRAM dedicada. Agora precisamos verificar se conseguimos ler essa memória na velocidade necessária e, ao mesmo tempo, permitir que a CPU atualize a imagem.

Também vou separar duas questões que não podemos confundir: gerar os pixels digitais e produzir um sinal RCA colorido eletricamente correto.

## Resultados da revisão 6.1

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>67.127</title>
      <text color="secondary" size="xs">Verificações digitais aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Falhas encontradas no modelo</text>
    </grid-item>
  </grid>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    Endereçamento e arbitragem sintética consistentes
  </row>
</box>

### 1. Escolha inicial: NTSC

Proponho começar pelo NTSC, mantendo PAL como possibilidade posterior.

| Parâmetro | Referência inicial |
|---|---:|
| Frequência horizontal | ~15,734 kHz |
| Duração de linha | ~63,56 µs |
| Subportadora de cor | ~3,579545 MHz |
| Resolução lógica | 128 × 96 |
| Cores indexadas | 16 |
| Framebuffer | 6.144 bytes |

O NTSC nos fornece uma referência de temporização para desenvolver o controlador. Ainda precisamos confirmar a compatibilidade da tela escolhida.

### 2. Quantos acessos à VRAM precisamos?

Para uma linha de 128 pixels, com dois pixels por byte, precisamos ler **64 bytes**.

Considerando aproximadamente 52 µs de vídeo ativo, isso representa uma taxa de cerca de 1,23 milhão de leituras por segundo durante a linha.

É uma taxa plausível para uma SRAM rápida, mas ainda precisamos considerar multiplexadores, buffers e os tempos de habilitação e desabilitação.

### 3. Comparação das arquiteturas

| Alternativa | Avaliação |
|---|---|
| SRAM 6264 com arbitragem | Preferida para o próximo protótipo lógico |
| SRAM 6264 + buffer de linha | Alternativa para reduzir contenção |
| SRAM dual-port | Pendente de custo e disponibilidade |

**Não vou adicionar o buffer de linha automaticamente.** Primeiro precisamos demonstrar que ele realmente compensa a quantidade extra de componentes.

### 4. EEPROM preservada

Também verificamos o endereçamento dos dois bancos de 16 KB da EEPROM removível.

Isso mantém acessíveis seus 32 KB físicos, incluindo SAVE A e SAVE B. Ainda faltam os circuitos de seleção e proteção de escrita.

## Arquivos gerados

- [Relatório técnico — Revisão 6.1](sandbox:/mnt/data/isa1/ISA-1_REV61_TEMPORIZACAO_VIDEO.md)
- [Simulador de temporização e VRAM](sandbox:/mnt/data/isa1/isa1_rev61_video_timing.py)
- [Resultados reproduzíveis](sandbox:/mnt/data/isa1/isa1_rev61_results.json)

## Próxima revisão — 6.2

O principal desafio agora é o **codificador de vídeo composto colorido**.

Precisamos selecionar um componente real, verificar sua disponibilidade, alimentação, interface de cores e clock. Também quero examinar se podemos aproveitar um único oscilador de referência para simplificar o circuito.

**Situação do ISA-1:** o framebuffer e o endereçamento avançaram, mas o vídeo RCA colorido ainda não está eletricamente validado.

A prioridade continua sendo fazer o computador funcionar bem, preservando a CPU completa e reduzindo componentes somente quando houver uma vantagem demonstrável. 🥳

## user — bbb212be-1970-4753-98fd-4b98fe615996

Pode seguir
E vamos seguir com a tela barata mesmo 

## assistant — d23e3ae2-da28-4e3e-86a7-80201aec12b4

{"content_type": "thoughts", "source_analysis_msg_id": "2e207753-2001-4075-b417-ad6173d6fe86", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 2 sites"}]}

## assistant — 395af217-fee2-43c0-b081-728ebba44c07

{"content_type": "thoughts", "source_analysis_msg_id": "f7cf1a06-470c-4b58-91fa-d981ffba6ec3", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos e revisou a ISA-1"}]}

## assistant — 1acc9ac4-2431-4e8e-8bd7-e09e40444219

{"content_type": "thoughts", "source_analysis_msg_id": "5fa5709a-8af1-4db2-8e75-c272d85449da", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 2 sites"}]}

## assistant — 52410403-7b14-4a0d-9716-a5486ea1989a

{"content_type": "thoughts", "source_analysis_msg_id": "f8949aa3-abe5-42dd-8b60-a824d956baa1", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validei temporização e endereçamento e elaborei relatório do codificador CVBS"}]}

## assistant — 3861c04d-04ec-4fc3-b6fb-aaa87d43316a

{"content": "Pensou por 37s", "content_type": "reasoning_recap"}

## assistant — d47e22aa-16c2-4cac-abaa-f81791bb1e42

🥳🖥️ **ISA-1 — Revisão 6.2: escolhemos um caminho concreto para o vídeo colorido!**

Vamos manter a **tela RCA de 4,3 polegadas, 12 V, na faixa dos R$ 67**. Não há motivo para encarecer o projeto com aquela tela de 5 V importada.

Pesquisei os circuitos de codificação de vídeo e encontrei uma solução que combina muito bem com a filosofia do ISA-1: o **AD725**, um codificador RGB para NTSC/PAL, alimentado em 5 V e disponível em encapsulamento SOIC-16. Ele recebe sinais RGB analógicos e sincronismo e gera vídeo composto. <Cite ref="turn363131search0"/>

Porém, apareceu uma ressalva importante: a Analog Devices classifica o AD725 como **Last Time Buy**, ou seja, em processo de descontinuação. Portanto, podemos utilizá-lo como referência de engenharia, mas ainda não vou aprová-lo como componente definitivo para nossa PCB.

## Uma melhoria no clock

A documentação do AD725 especifica uma referência de 14,31818 MHz para NTSC. <Cite ref="turn363131search22"/>

Podemos estudar o aproveitamento desse clock para gerar também a cadência dos pixels, reduzindo a necessidade de osciladores independentes.

Executei uma primeira bancada digital com essa hipótese.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>19.072</title>
      <text color="secondary" size="xs">Verificações aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Divergências encontradas</text>
    </grid-item>
  </grid>
  <text color="secondary" size="xs">Testes de aritmética temporal e endereçamento, não de sinais elétricos.</text>
</box>

Com uma divisão por cinco, obtemos aproximadamente 2,864 MHz para os pixels. Uma linha de 128 pixels ocuparia 44,70 µs, deixando espaço temporal para sincronismo e apagamento. Ainda precisamos construir e validar esses intervalos corretamente.

## Como ficará o circuito de vídeo

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 204" width="100%">
    {#each [{x:8,y:12,w:96,h:42,a:"VRAM 8 KB",b:"128 × 96"},{x:121,y:12,w:201,h:42,a:"Seleção de pixel",b:"4 bits por pixel"},{x:121,y:83,w:201,h:42,a:"Paleta + RGB analógico",b:"16 índices de cor"},{x:121,y:153,w:95,h:42,a:"Codificador",b:"NTSC / PAL"},{x:234,y:153,w:88,h:42,a:"Tela RCA",b:"12 V"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x={p.x+p.w/2} y={p.y+17} fontSize="10" textAnchor="middle" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+31} fontSize="9" textAnchor="middle" fill="currentColor">{p.b}</text>
    {/each}
    <g fill="none" stroke="#0d9488" strokeWidth="2">
      <path d="M104 33 H121 M221 54 V83 M221 125 V138 H169 V153 M216 174 H234"/>
    </g>
  </svg>
  <caption>Fluxo proposto. A conversão de paleta para RGB e a saída analógica ainda precisam de dimensionamento elétrico.</caption>
</box>

O AD725 não gera os pixels por conta própria. Teremos de construir a paleta de 16 cores, gerar níveis RGB analógicos e fornecer os sincronismos. O datasheet também especifica as conexões de alimentação e a entrada de clock. <Cite ref="turn363131search23"/>

## Arquivos da revisão 6.2

- [Relatório técnico — codificador e clock](sandbox:/mnt/data/isa1/ISA-1_REV62_CODIFICADOR_CVBS.md)
- [Simulador de temporização em Python](sandbox:/mnt/data/isa1/isa1_rev62_video_clock.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev62_results.json)
- [Tabela dos 128 pixels e seus intervalos de clock](sandbox:/mnt/data/isa1/isa1_rev62_video_line.csv)

## Próxima revisão — 6.3

Vamos investigar uma solução de codificação colorida que seja **comprável, economicamente viável e compatível com a soldagem caseira**.

Não quero economizar R$ 200 na tela e depois descobrir que precisamos de um codificador raro e caro.

Também vamos projetar a paleta de 16 cores e verificar como transformá-la em sinais RGB adequados.

**Decisão mantida:** tela barata de 12 V, vídeo composto colorido e CPU independente do controlador de vídeo. O AD725 é uma referência técnica, não uma compra aprovada.

Estamos avançando, e essa revisão revelou uma questão de custo e disponibilidade que vale resolver antes de desenhar a placa. 🥳

## user — bbb21034-4399-40fa-add0-ab9659180fd5

Boa, segue então vendo oq vale a pena entre a tela e o controlador

## assistant — 6e1ac81a-537f-4ca0-8e83-4c96666297d4

{"content_type": "thoughts", "source_analysis_msg_id": "c68da077-6f3d-46be-aa6e-fa7ef7eb2764", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 6 sites"}]}

## assistant — 19b3ab03-96fe-41fe-9492-4b7a304a83e6

{"content": "Pensou por 9s", "content_type": "reasoning_recap"}

## assistant — 4e058efa-92bd-4d66-9b7f-8581a4bfb30d

## ISA-1 — Revisão 6.3: custo da tela versus custo do controlador

A pesquisa trouxe uma conclusão importante: **a tela RCA barata continua fazendo sentido. O problema está no preço e na disponibilidade dos codificadores de vídeo colorido.**

Encontrei um monitor de 4,3 polegadas na faixa que havíamos escolhido, mas os codificadores AD724 e AD725 estão em processo de descontinuação. Isso muda a maneira como devemos projetar o circuito.

### Preços encontrados

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage ref="turn318521product60" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn318521product60" category="product" value={turn318521product60.title}/>**

      <title size="lg" color="default">{turn318521product60.displayed_price}</title>
      <text color="secondary" size="xs">{turn318521product60.merchant}</text>
      Tela automotiva 4,3", entrada AV. É a categoria de monitor que queremos manter.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn318521product0" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn318521product0" category="product" value={turn318521product0.title}/>**

      <title size="lg">{turn318521product0.displayed_price}</title>
      <text color="secondary" size="xs">{turn318521product0.merchant}</text>
      Codificador RGB para NTSC/PAL, SOIC-16. Já custa mais do que a própria tela.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn318521product12" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn318521product12" category="product" value={turn318521product12.title}/>**

      <title size="lg">{turn318521product12.displayed_price}</title>
      <text color="secondary" size="xs">{turn318521product12.merchant}</text>
      Alternativa com oscilador de subportadora integrado, mas também em descontinuação.
    </box>
  </row>
</box>

Os valores são ofertas encontradas, não cotações finais com frete e impostos.

A Analog Devices confirma que tanto o <Entity category="product" value="AD725" disambig="codificador de vídeo RGB NTSC PAL Analog Devices"/> quanto o <Entity category="product" value="AD724" disambig="codificador de vídeo RGB NTSC PAL Analog Devices"/> estão classificados como *Last Time Buy*. <Cite refs={["turn318521search0","turn318521search1"]}/>

## Qual arquitetura vale mais a pena?

| Solução | Custo provável | Dificuldade | Avaliação |
|---|---|---|---|
| AD725 + tela RCA | Alto para o objetivo | Baixa a média | Funciona conceitualmente, mas depende de chip descontinuado |
| AD724 + tela RCA | Alto | Baixa a média | Mesmo problema de disponibilidade |
| Gerador composto discreto com 74HC | Ainda não determinado | Alta | Melhor caminho para investigar |
| Tela RGB paralela | Depende do módulo | Média | Alternativa de contingência |

### Minha escolha para a próxima etapa

**Manter a tela RCA de 12 V e desenvolver uma alternativa de geração de vídeo composto usando lógica 74HC e componentes analógicos simples.**

Mas existe uma condição importante: não podemos confundir vídeo monocromático com vídeo colorido.

Para gerar NTSC colorido, precisamos produzir corretamente a subportadora de aproximadamente 3,58 MHz, suas fases, a amplitude da crominância, o *color burst* e os sincronismos. Uma rede de resistores sozinha não resolve tudo isso.

O AD725 continua útil como referência de comparação. Seu preço encontrado não justifica torná-lo uma dependência permanente do ISA-1.

## Decisões da revisão 6.3

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Mantida:** tela RCA econômica de 4,3 polegadas
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Mantida:** CPU independente do gerador de vídeo
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle-2" color="success"/>
    **Mantida:** resolução inicial de 128 × 96, 16 cores
  </row>
  <row align="center" gap={2}>
    <icon name="alert-circle" color="secondary"/>
    **Em estudo:** codificação NTSC discreta e seu custo total
  </row>
  <row align="center" gap={2}>
    <icon name="alert-circle" color="secondary"/>
    **Pendente:** confirmar NTSC/PAL e comportamento da tela específica
  </row>
</box>

### Revisão 6.4 — próximo trabalho

Vou comparar uma implementação de crominância com fases digitais, mistura de luminância e sincronismo, e saída composta de 75 Ω. A avaliação deverá incluir quantidade de CIs, precisão temporal, tolerâncias, componentes analógicos e custo total.

Se o circuito discreto exigir tantos componentes que perca a vantagem econômica, reconsideraremos o codificador integrado ou outra interface de tela.

**Nosso objetivo não é apenas ter uma tela barata: é fazer o sistema completo de vídeo ser barato, reproduzível e confiável, sem sacrificar o computador ISA-1.**

## user — bbb210fe-fa48-40ef-a8c4-045da35a248d

Pode seguir, qualquer coisa, podemos mudar a tela e o padrão de tela 

## assistant — 07e760d5-dc8b-4934-bf78-9c3c5fb348c4

{"content_type": "thoughts", "source_analysis_msg_id": "c38189c4-8d51-4439-b51e-7d153a292ac1", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 14 sites"}]}

## assistant — 32eea206-72a3-476f-b636-d39733e9bf4d

{"content_type": "thoughts", "source_analysis_msg_id": "e472448f-b7f1-49ce-ac56-6dcd03ee919b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos de trabalho ISA-1"}]}

## assistant — 44e275b2-09d6-442a-aaab-83b470e03927

{"content_type": "thoughts", "source_analysis_msg_id": "557d2349-7187-4067-a16e-df62bab5ab03", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 14 sites"}]}

## assistant — cc40f3f1-acba-417b-a180-c0cc3657ce08

{"content_type": "thoughts", "source_analysis_msg_id": "dbe97218-3255-41fd-aff5-d20dddc85cd9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Calculou o orçamento quantitativo da interface de vídeo"}]}

## assistant — 2e1a321c-9667-4696-8418-970c8b548380

{"content": "Pensou por 29s", "content_type": "reasoning_recap"}

## assistant — 17892b81-214d-4815-9953-302cc4011b44

A liberdade para mudar a tela é importante. Ela permite escolher o **menor custo do conjunto tela + controlador + memória + alimentação**, em vez de insistir no RCA só porque o monitor é barato.

A pesquisa revelou uma alternativa promissora: os displays TFT com controlador <Entity category="product" value="ILI9341" disambig="controlador de display TFT colorido"/> possuem memória gráfica interna e aceitam interfaces SPI ou paralelas, dependendo do módulo. Assim, o próprio display mantém a imagem enquanto a CPU executa outras tarefas. <Cite refs={["turn673981search36","turn673981search39"]}/>

Isso elimina a necessidade de gerar NTSC, color burst e sincronismos de vídeo composto. Porém, a velocidade de atualização passa a ser o principal desafio.

## Revisão 6.4 — resultado da comparação

Comparei quatro caminhos:

| Tecnologia | Complexidade para o ISA-1 | Situação |
|---|---|---|
| RCA com NTSC discreto | Alta | Reserva |
| TFT SPI com memória interna | Baixa a média | Viável, porém atualização limitada |
| **TFT paralelo de 8 bits com memória interna** | **Média** | **Preferido** |
| TFT RGB TTL de 4,3" | Alta | Descartado por enquanto |

Atenção à diferença: uma tela RGB TTL de 4,3" pode exigir geração contínua de pixels e sincronismos. Um exemplo comercial de 480 × 272 não possui memória gráfica própria, portanto não elimina o controlador de vídeo. <Cite ref="turn877831search0"/>

### O que os cálculos mostraram

Executei **12.308 verificações matemáticas, sem falhas**, para estimar o tráfego de dados.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium" size="sm">Tempo mínimo para enviar uma imagem completa</text>
  <Chart content={{"chartType":"bar","meta":{"footer":"Tempos ideais, sem comandos ou esperas. Valores reais serão maiores."},"xKey":"interface","series":[{"dataKey":"small","label":"128 × 96","valueSuffix":" ms"},{"dataKey":"large","label":"256 × 192","valueSuffix":" ms"}],"yAxisMin":0,"data":[{"interface":"SPI 8 MHz","small":24.576,"large":98.304},{"interface":"Paralelo 2 MB/s","small":12.288,"large":49.152}]}}/>
</box>

Esses valores não são desempenho medido. A taxa de 2 MB/s do paralelo é uma hipótese que ainda precisa ser demonstrada com a lógica 74HC.

A grande vantagem é que, depois de enviada, a imagem permanece na memória interna do display. A CPU não precisa ficar redesenhando a tela para mantê-la acesa.

## Minha decisão técnica

Vamos **mudar a preferência do projeto para TFT colorido com controlador e memória gráfica interna, preferencialmente interface paralela de 8 bits**.

Ainda não escolhi o módulo definitivo: precisamos encontrar um que exponha realmente essa interface, seja economicamente viável e permita a adaptação elétrica entre nossa lógica de 5 V e a tela de 3,3 V.

A CPU continuará sendo nossa CPU 74HC de 8 bits, sem microcontrolador responsável pelo funcionamento do computador.

## Documentação produzida

- [Relatório técnico da revisão 6.4](sandbox:/mnt/data/isa1/ISA-1_REV64_COMPARACAO_INTERFACES.md)
- [Simulador de transferência](sandbox:/mnt/data/isa1/isa1_rev64_display_compare.py)
- [Resultados em JSON](sandbox:/mnt/data/isa1/isa1_rev64_results.json)
- [Tabela de desempenho em CSV](sandbox:/mnt/data/isa1/isa1_rev64_transfer_budget.csv)

**Próxima revisão 6.5:** selecionar módulos concretos, comparar o custo entregue no Brasil e desenhar a interface de comunicação entre a CPU e a tela, incluindo paleta, conversão de níveis e um mecanismo de transferência que não sobrecarregue a CPU.

Essa mudança pode simplificar bastante o ISA-1, especialmente porque deixaremos de precisar construir todo o sistema de codificação NTSC.

## user — bbb2157d-9420-47dc-b625-84091fad9f34

Pode seguir comparando e testando a tela e controlador

## assistant — 0e6c2558-42aa-4f70-8a28-490c25e2d7a5

{"content_type": "thoughts", "source_analysis_msg_id": "44a75daa-5128-4c31-9527-8ccb415e15b4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e leu relatório de interfaces"}]}

## assistant — a88f0d4f-b95c-47a8-8429-56eeac31308e

{"content_type": "thoughts", "source_analysis_msg_id": "6d858852-45c0-4b8b-975f-59110f7ea7fa", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 10 sites"}]}

## assistant — 1c5014b4-ffd9-4025-958f-0f27a3ec3685

{"content_type": "thoughts", "source_analysis_msg_id": "6db5c913-a0c8-4c3e-9fc7-d73344b35b43", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Criados benchmarks ISA1 Rev65 e avaliados displays e controladores candidatos"}]}

## assistant — 1e1aafe9-b987-4ae1-adb7-2c233243af75

{"content": "Pensou por 37s", "content_type": "reasoning_recap"}

## assistant — a528c35c-bc92-4769-b809-6b8b6a9eee14

## ISA-1 — Revisão 6.5: comparação de telas e controladores

A comparação está apontando para uma solução interessante: **uma tela TFT com memória gráfica interna pode simplificar bastante o ISA-1**, mesmo custando um pouco mais que a tela RCA original.

Confirmei nos datasheets que o ILI9341 suporta barramento paralelo de 8 bits, além de SPI, e possui memória interna para manter a imagem. O ILI9488 também suporta barramento paralelo de 8 bits e oferece resolução maior, de 320 × 480 pixels. <Cite refs={["turn479672search27","turn479672search25"]}/>

O cuidado principal é que **o controlador suportar uma interface não significa que o módulo vendido exponha essa interface**.

### Telas encontradas

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage ref="turn479672product3" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn479672product3" category="product" value={turn479672product3.title}/>**

      <title size="lg">{turn479672product3.displayed_price}</title>
      <text color="secondary" size="xs">{turn479672product3.merchant}</text>
      Candidata econômica de 2,8". A interface paralela precisa ser confirmada na versão exata do módulo.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn479672product21" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn479672product21" category="product" value={turn479672product21.title}/>**

      <title size="lg">{turn479672product21.displayed_price}</title>
      <text color="secondary" size="xs">{turn479672product21.merchant}</text>
      Alternativa SPI para um primeiro protótipo funcional, sem garantia de barramento I80.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage ref="turn479672product16" aspectRatio="1:1" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **<Entity ref="turn479672product16" category="product" value={turn479672product16.title}/>**

      <title size="lg">{turn479672product16.displayed_price}</title>
      <text color="secondary" size="xs">{turn479672product16.merchant}</text>
      Shield de 2,4" que merece avaliação pelo conector e pela pinagem, não apenas pelo nome do controlador.
    </box>
  </row>
</box>

Esses são preços anunciados, sem confirmação de frete, impostos ou custo final entregue.

## Testes da revisão 6.5

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="2xl" tabularNums>68.884</title>
      <text color="secondary" size="xs">Verificações aprovadas</text>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <text color="secondary" size="xs">Falhas no modelo</text>
    </grid-item>
  </grid>
</box>

Criei e executei uma nova bancada Python. Ela verificou a conversão de pixels de 4 bits para RGB565, a atualização de regiões retangulares, a quantidade de bytes transferidos e a sequência lógica de escrita do barramento paralelo.

<text weight="medium" size="sm">Tempo mínimo calculado para atualizar a tela</text>

<Chart content={{"chartType":"bar","xKey":"interface","series":[{"dataKey":"small","label":"128 × 96","valueSuffix":" ms"},{"dataKey":"large","label":"256 × 192","valueSuffix":" ms"}],"yAxisMin":0,"data":[{"interface":"SPI 8 MHz","small":24.576,"large":98.304},{"interface":"I80 2 MB/s*","small":12.288,"large":49.152}]}}/>

<caption>*A taxa I80 é hipotética. Os valores excluem comandos, processamento e atrasos reais.</caption>

### Uma possível economia adicional

Se usarmos a memória gráfica interna do TFT, talvez possamos eliminar a SRAM dedicada de vídeo de 8 KB e atualizar diretamente regiões da tela.

**Ainda não aprovo essa redução.** Precisamos verificar o impacto sobre jogos, animações e a independência da CPU.

## Minha escolha provisória

O **ILI9341 com interface paralela I80 de 8 bits** passa a ser nosso principal candidato. O ILI9488 continua como alternativa para uma tela maior.

Não vou fechar a compra enquanto não identificarmos um módulo específico com pinagem comprovada. Também precisaremos adaptar os sinais de 5 V da CPU para os níveis de 3,3 V do controlador.

## Documentação produzida

- [Relatório técnico — Revisão 6.5](sandbox:/mnt/data/isa1/ISA-1_REV65_SELECAO_DISPLAY.md)
- [Simulador Python](sandbox:/mnt/data/isa1/isa1_rev65_display_bench.py)
- [Resultados dos testes](sandbox:/mnt/data/isa1/isa1_rev65_results.json)
- [Tabela comparativa de transferência](sandbox:/mnt/data/isa1/isa1_rev65_transfer_budget.csv)

**Próxima revisão 6.6:** projetar a interface elétrica CPU–TFT, calcular os tempos reais de escrita, estudar a conversão de níveis e decidir se precisamos manter a VRAM.

A meta permanece: **um ISA-1 colorido, funcional, econômico e construído com nossa própria CPU 74HC**, sem depender de um microcontrolador para executar o computador.

## user — bbb21060-a76f-404a-afa1-9655564cb289

Ahh eu tenho essa tela aqui,
Acabei de encontrar isso no AliExpress: 
SHCHV-Tela sensível ao toque para framboesa Pi, 2.4 polegadas, tela TFT para Pi 4B, 3B +, 3B 3A +, 2 W, 320x240, interface SPI
https://a.aliexpress.com/_mt4iMxl

## assistant — 3c679d4a-0fa1-4d3e-8322-8dee429744ea

{"content_type": "thoughts", "source_analysis_msg_id": "4d7ddf3a-a6d6-4f59-abeb-4a9063663133", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 8 sites"}]}

## assistant — b0c04ac6-8401-4b89-a5db-a9f362b85c98

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — 24c1c949-f911-455c-9903-f6563378c37c

**Essa descoberta pode ser excelente para o ISA-1!** 😁

Como você já possui essa tela, podemos utilizá-la para desenvolver e testar o computador sem comprar outro display agora.

Pelo anúncio que você encontrou, temos:

- **Tela:** TFT de 2,4 polegadas, 320 × 240 pixels.
- **Interface anunciada:** SPI.
- **Touchscreen:** sim.
- **Formato:** módulo para Raspberry Pi.

A interface SPI é interessante porque podemos implementá-la usando nossa própria lógica 74HC, sem adicionar um microcontrolador.

Mas há um detalhe importante: **precisamos identificar o controlador real da tela**. O fato de ser anunciada para Raspberry Pi não garante que utilize ILI9341; alguns módulos semelhantes usam controladores diferentes.

## Encontrei informações mais específicas!

Uma página comercial da **SHCHV 2,4"** com a mesma descrição informa os seguintes componentes:

| Componente | Identificação |
|---|---|
| Controlador LCD | **ILI9341** |
| Controlador touch | **XPT2046** |
| Resolução | 320 × 240 |
| Interface | SPI |
| Alimentação anunciada | 5 V, aproximadamente 80 mA |

<Cite refs={["turn692116search0","turn692116search2"]}/>

Não consegui abrir diretamente o link encurtado do AliExpress. Portanto, esses dados são uma identificação provável do modelo, não uma confirmação da sua unidade.

## O que isso muda no ISA-1?

<box border radius="lg" padding={3} gap={2}>
  <row align="center" justify="between">
    **Tela SHCHV 2,4" SPI**
    <badge color="success">Candidata principal</badge>
  </row>
  <grid columns={2} gap={2}>
    <grid-item>
      <text color="secondary" size="xs">Atualização completa a 8 MHz</text>
      <title size="lg">153,6 ms</title>
    </grid-item>
    <grid-item>
      <text color="secondary" size="xs">Atualização de 128 × 96</text>
      <title size="lg">24,6 ms</title>
    </grid-item>
  </grid>
  <caption>Tempos teóricos mínimos com RGB565, sem comandos nem processamento.</caption>
</box>

O SPI será mais lento que o paralelo de 8 bits, mas pode economizar bastante lógica e fiação. Além disso, o ILI9341 mantém a imagem em sua memória interna.

**Minha proposta é utilizar essa tela como nosso primeiro display oficial de desenvolvimento**, mantendo aberta a possibilidade de migrar para um modelo maior posteriormente.

Para a próxima revisão, podemos projetar um transmissor SPI com registrador de deslocamento 74HC595, controle de clock, comandos de inicialização e conversão de níveis de 5 V para 3,3 V. Também podemos deixar o touchscreen para uma segunda etapa.

**Preciso apenas de uma coisa:** envie uma foto nítida da frente e do verso da sua tela, mostrando os componentes e as inscrições da placa.

Assim poderemos identificar a versão exata e projetar a conexão com o ISA-1 sem arriscar danificar o módulo.

## user — bbb2107c-b5ac-4fbc-acb7-6c6b5fb9c1d1

{"asset_pointer": "sediment://file_0000000013e0820e8eab8ed102b4eb86", "content_type": "image_asset_pointer", "fovea": null, "height": 1536, "metadata": {"asset_pointer_link": null, "container_pixel_height": null, "container_pixel_width": null, "dalle": null, "emu_omit_glimpse_image": null, "emu_patches_override": null, "generation": null, "gizmo": null, "is_no_auth_placeholder": null, "lpe_delta_encoding_channel": null, "lpe_keep_patch_ijhw": null, "sanitized": true, "segmentation": null, "watermarked_asset_pointer": null}, "mime_type": "image/jpeg", "size_bytes": 99575, "width": 716}
{"asset_pointer": "sediment://file_00000000aa18820e9627cd78450f7405", "content_type": "image_asset_pointer", "fovea": null, "height": 1536, "metadata": {"asset_pointer_link": null, "container_pixel_height": null, "container_pixel_width": null, "dalle": null, "emu_omit_glimpse_image": null, "emu_patches_override": null, "generation": null, "gizmo": null, "is_no_auth_placeholder": null, "lpe_delta_encoding_channel": null, "lpe_keep_patch_ijhw": null, "sanitized": true, "segmentation": null, "watermarked_asset_pointer": null}, "mime_type": "image/jpeg", "size_bytes": 57253, "width": 138}
Mandando aqui uns prints

## assistant — 3f3e8c26-36d4-4c28-b9f9-a1cb7fbc9499

Agora sim! 😁 Esses prints confirmam várias informações importantes sobre a tela que você já tem. E ela é uma candidata muito interessante para o ISA-1.

## Tela identificada

<row align="start" gap={3}>
  <AsyncImage query="2.4 inch Raspberry Pi TFT LCD ILI9341 XPT2046 26 pin blue PCB display module" aspectRatio="3:4" maxWidth="136px"/>
  <box flex="1" gap={1}>
    **SHCHV 2,4" TFT para Raspberry Pi**

    <badge color="success">Especificações confirmadas no anúncio</badge>
    <text color="secondary" size="sm">Controlador ILI9341 · Touch XPT2046 · SPI</text>
    Módulo com conector GPIO para Raspberry Pi e alimentação anunciada de 5 V.
  </box>
</row>

| Característica | Informação dos prints |
|---|---|
| Resolução | 320 × 240 pixels |
| Controlador LCD | ILI9341 |
| Controlador touch | XPT2046 |
| Interface | SPI |
| Alimentação anunciada | 5 V |
| Consumo anunciado | 80 mA (0,4 W) |
| Dimensões da placa | 56 × 65 mm |
| Área ativa | 48,96 × 36,72 mm |
| Iluminação | LED |

Esses dados estão explícitos no anúncio. A identificação elétrica da sua unidade física ainda dependerá de conferir a placa.

## O que muda na arquitetura do ISA-1?

Podemos simplificar bastante o subsistema de vídeo:

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 330 204" width="100%">
    {#each [{x:8,y:12,w:135,h:48,a:"CPU ISA-1",b:"8 bits · 74HC"},{x:188,y:12,w:134,h:48,a:"Interface SPI",b:"lógica dedicada"},{x:188,y:85,w:134,h:48,a:"ILI9341",b:"memória gráfica interna"},{x:188,y:158,w:134,h:38,a:"TFT 320 × 240",b:"imagem colorida"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="7" stroke="#94a3b8" fill="#64748b" fillOpacity=".1"/>
      <text x={p.x+p.w/2} y={p.y+18} fontSize="11" fill="currentColor" textAnchor="middle">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+34} fontSize="10" fill="currentColor" textAnchor="middle">{p.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M143 36 H188 M255 60 V85 M255 133 V158"/>
    </g>
  </svg>
</box>

A tela mantém a imagem sozinha, graças à memória interna do ILI9341. Isso significa que **não precisamos gerar continuamente pixels nem sincronismo de vídeo**, como seria necessário com a tela RCA.

Também podemos investigar a eliminação da VRAM externa de 8 KB, embora isso dependa do desempenho desejado para jogos.

## Um detalhe que precisamos resolver

O módulo recebe 5 V, mas isso **não garante que seus sinais SPI aceitem 5 V**. O ILI9341 trabalha com lógica de baixa tensão, então precisamos identificar se a placa possui conversores de nível.

Outro ponto: o conector para Raspberry Pi não é necessariamente uma interface SPI de poucos pinos. Ele reúne alimentação, sinais de controle, LCD e touchscreen.

Não devemos ligar diretamente a CPU ao conector antes de conferir sua pinagem.

## Minha decisão para a revisão 6.6

Vamos adotar essa SHCHV como **tela de referência do protótipo ISA-1**, sem comprar outra por enquanto.

Vou concentrar a próxima etapa em identificar a pinagem, projetar o transmissor SPI com lógica 74HC, verificar a adaptação de níveis e calcular a velocidade de atualização. O touchscreen poderá ser integrado depois.

**Uma última coisa:** quando puder, envie uma foto real do verso da sua placa, especialmente da região do conector e dos componentes. O anúncio confirma o modelo comercial, mas essa foto permitirá verificar a revisão de hardware que você possui.

Aproveitar uma tela que já está nas suas mãos é uma excelente oportunidade de economizar sem comprometer o projeto.

## user — bbb21afb-bb58-4f53-8f5d-2f1581355998

Enquanto não tiro uma foto da tela, eu uso ela num raspiberry pi 3b e já usei num Luckfox Lyra zero w

## assistant — 37484696-412d-4844-9996-cf7fd9505ea7

Isso é uma informação muito útil para o ISA-1! 😁

O fato de você já ter utilizado essa mesma tela tanto no **Raspberry Pi 3B** quanto no **Luckfox Lyra Zero W** nos dá uma vantagem: temos um módulo que já funcionou em dois equipamentos diferentes.

Isso reforça nossa escolha de aproveitar a SHCHV de 2,4" no protótipo.

### O que podemos concluir

- **A tela é funcional:** já foi utilizada em equipamentos reais.
- **A interface SPI é uma boa candidata:** é o padrão informado pelo fabricante.
- **Não precisamos comprar outra tela agora.**
- **Podemos aproveitar os drivers e as configurações existentes** para descobrir a sequência de inicialização e a pinagem.

Entretanto, o funcionamento nesses equipamentos não comprova que as entradas SPI toleram 5 V. Ambos podem trabalhar com sinais de 3,3 V.

### Uma oportunidade interessante

Como você já utilizou a tela no Raspberry Pi, podemos extrair informações diretamente da configuração que funcionava.

Por exemplo, podemos identificar o driver, a frequência SPI, os GPIOs utilizados para `DC`, `RESET` e `CS`, além da configuração do touchscreen XPT2046.

Isso seria mais confiável do que depender apenas do anúncio do AliExpress.

### Próximo passo da revisão 6.6

Minha proposta é desenvolver o controlador SPI do ISA-1 com três objetivos:

1. Enviar comandos e pixels RGB565 ao ILI9341 usando lógica 74HC.
2. Permitir que a CPU envie dados sem precisar controlar manualmente cada pulso de clock.
3. Manter a imagem estável enquanto a CPU executa programas.

Também vou comparar duas alternativas: transmissão SPI diretamente pela CPU e transmissão por um pequeno controlador dedicado com registrador de deslocamento.

**Uma pergunta importante:** você ainda tem o Raspberry Pi 3B com essa tela funcionando e acesso ao terminal Linux dele?

Se tiver, poderemos obter a configuração exata da tela sem precisar esperar pela fotografia.

## user — bbb21a75-f511-4fc8-9409-772a30beb677

Não
O raspi está desligado
E me veio uma dúvida
Um conversor de vga pra USB funcionaria pra gente? 
Eu tenho uma tela USB C
Também tem mini HDMI nela

## assistant — 7072900a-6109-4c54-8284-94ef05db5417

Opa! Isso abre outra possibilidade interessante para o ISA-1. Principalmente porque sua tela também possui **entrada mini HDMI**.

Um conversor VGA para USB não seria minha primeira escolha, mas um **conversor ativo de VGA para HDMI** pode funcionar muito bem.

## Como poderíamos fazer

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 130" width="100%">
    {#each [{x:5,w:95,a:"ISA-1",b:"CPU + vídeo VGA"},{x:122,w:96,a:"Conversor ativo",b:"VGA → HDMI"},{x:240,w:95,a:"Sua tela",b:"Mini HDMI"}] as p}
      <rect x={p.x} y="22" width={p.w} height="65" rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={p.x+p.w/2} y="48" textAnchor="middle" fontSize="11" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y="64" textAnchor="middle" fontSize="9" fill="currentColor">{p.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M100 54 H122 M218 54 H240"/>
      <path d="M170 110 V87"/>
    </g>
    <text x="170" y="122" fontSize="10" textAnchor="middle" fill="currentColor">Alimentação 5 V</text>
  </svg>
</box>

<row align="center" gap={3}>
  <AsyncImage query="active VGA male input to HDMI female output converter adapter USB power cable" aspectRatio="1:1" maxWidth="120px"/>
  <box gap={1}>
    **Conversor ativo VGA para HDMI**

    Precisamos especificamente do modelo com entrada VGA e saída HDMI, não o contrário.
  </box>
</row>

## Por que VGA seria interessante?

Gerar VGA utilizando componentes 74HC é consideravelmente mais simples do que gerar NTSC colorido.

Precisamos gerar cinco sinais principais: vermelho, verde, azul, sincronismo horizontal e sincronismo vertical. Não precisamos de subportadora de cor nem de um codificador AD725.

Também podemos utilizar redes de resistores para produzir diferentes intensidades de cada cor.

## Comparando nossas alternativas

| Característica | TFT SPI | VGA + HDMI | RCA NTSC |
|---|---|---|---|
| Complexidade do circuito | Baixa a média | Média | Alta |
| Memória gráfica interna | Sim | Não | Não |
| Geração contínua de vídeo | Não | Sim | Sim |
| Potencial para jogos | Bom | Muito bom | Bom |
| Tela que você já possui | Sim | Sim | Não |
| Conversor externo | Não | Sim | Não |
| Independência da CPU | Possível | Possível | Possível |

## E se fizéssemos VGA colorido?

Podemos estudar a seguinte configuração para o ISA-1:

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">640 × 480</title>
      <caption>Resolução do sinal VGA</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">160 × 120</title>
      <caption>Resolução gráfica lógica</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">16 cores</title>
      <caption>Paleta inicial</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">9,375 KiB</title>
      <caption>Framebuffer de 4 bits</caption>
    </grid-item>
  </grid>
  <caption>Proposta preliminar com ampliação de cada pixel lógico em 4 × 4 pixels físicos. Exigiria rever a capacidade da VRAM.</caption>
</box>

A grande vantagem seria termos uma saída de vídeo padronizada, permitindo conectar o ISA-1 a diversos monitores e televisores através de conversores.

## Minha recomendação

Antes de fechar a arquitetura SPI, vale muito a pena estudar o VGA. Inclusive, poderíamos manter a pequena tela SPI como display auxiliar futuramente.

Quanto ao USB-C, a questão é que monitores desse tipo normalmente recebem vídeo através de DisplayPort Alt Mode, e não dados USB comuns. Um adaptador VGA para USB convencional não resolveria isso.

**Qual é o tamanho e o modelo dessa sua tela USB-C com mini HDMI?**

Dependendo das características dela, podemos até adotar VGA como saída de vídeo principal do ISA-1. Seria uma solução bastante interessante para nosso computador retrô.

## user — bbb21351-d986-4bff-be86-10114a9d1b2e

São 15.4 polegadas da arzopa

## assistant — 639ed370-01e5-427a-a7c0-12e342ac781d

Ah, uma tela portátil Arzopa de 15,4 polegadas! Isso torna a alternativa VGA muito mais interessante para o ISA-1.

Como você já possui as duas telas, podemos desenvolver uma arquitetura que aproveite ambas, sem precisar comprar outro monitor.

## Comparação para o ISA-1

| Característica | SHCHV 2,4" | Arzopa 15,4" |
|---|---|---|
| Interface | SPI | Mini HDMI |
| Controlador necessário | Transmissor SPI | VGA + conversor ativo |
| Memória gráfica externa | Opcional | Necessária na arquitetura proposta |
| Quantidade de CIs | Menor | Maior |
| Programação em BASIC | Tela pequena | Excelente espaço de visualização |
| Jogos | Bom | Muito interessante |
| Custo da tela | R$ 0 | R$ 0 |

## Podemos estudar uma arquitetura com VGA de 64 cores

Em vez de limitar nosso computador a 16 cores, podemos investigar uma saída RGB222, com dois bits para cada componente de cor.

<box border radius="lg" padding={3} gap={3}>
  <svg viewBox="0 0 320 160" width="100%">
    {#each Array.from({length:64},(_,i)=>({r:Math.floor(i/16)*85,g:Math.floor(i/4)%4*85,b:i%4*85,x:i%8,y:Math.floor(i/8)})) as c}
      <rect x={c.x*40+1} y={c.y*20+1} width="38" height="18" rx="2" fill={`rgb(${c.r},${c.g},${c.b})`}/>
    {/each}
  </svg>
  <caption>Paleta RGB222 de 64 cores. Representação digital ideal, não uma medição da saída VGA.</caption>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl">640 × 480</title>
      <caption>Sinal VGA a ~60 Hz</caption>
    </grid-item>
    <grid-item>
      <title size="xl">160 × 120</title>
      <caption>Resolução gráfica lógica</caption>
    </grid-item>
    <grid-item>
      <title size="xl">64 cores</title>
      <caption>RGB222</caption>
    </grid-item>
    <grid-item>
      <title size="xl">18,75 KiB</title>
      <caption>VRAM com um byte por pixel</caption>
    </grid-item>
  </grid>
</box>

Poderíamos utilizar uma SRAM de vídeo de 32 KB, mantendo os outros 32 KB exclusivos da CPU.

## Próxima revisão — 6.6

Quero comparar três arquiteturas antes de tomar a decisão definitiva:

- **SPI:** aproveitar sua tela SHCHV com o mínimo de componentes.
- **VGA:** gerar vídeo colorido inteiramente com lógica 74HC e utilizar um conversor ativo para HDMI.
- **Híbrida:** VGA como saída principal e SPI como interface opcional para a tela pequena.

Também precisamos verificar se o conversor aceita o sinal VGA de 640 × 480 e se a Arzopa aceita o formato HDMI resultante.

A inspiração do Gigatron pode ser particularmente útil nessa etapa, principalmente para otimizar os contadores, a geração de sincronismo e a quantidade de CIs, **sem sacrificar a independência e os recursos da nossa CPU**.

Eu daria prioridade ao estudo do VGA agora. Ter uma saída de vídeo padronizada, capaz de conectar o ISA-1 a monitores maiores, seria uma excelente característica para o nosso computador.

## user — bbb210a6-6dcd-437a-91e4-1fa2ca0b5271

Pode seguir com o estudo da VGA 😎

## assistant — c0ced4f9-9ee5-4549-b71d-ff04f7564d63

{"content_type": "thoughts", "source_analysis_msg_id": "a52bde73-d55d-4649-be84-19a4464f6c1e", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 8 sites"}]}

## assistant — 3ddb5efc-56b1-4ac2-8d57-982cadc93e29

{"content_type": "thoughts", "source_analysis_msg_id": "45f029e4-cfa1-4e66-9a9a-cd2c23adff4f", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou temporização e endereçamento VGA, atualizando resultados ISA-1"}]}

## assistant — 5b59b31b-2466-40c3-9203-62631417d1b7

{"content": "Pensou por 40s", "content_type": "reasoning_recap"}

## assistant — 3652e05b-7f59-444b-9f44-cff48f9ff00d

# ISA-1 — Revisão 6.6: arquitetura VGA 😎

Vamos estudar o VGA como candidato a saída de vídeo principal do ISA-1, aproveitando sua tela Arzopa de 15,4 polegadas através de um conversor ativo VGA para HDMI.

Diferentemente do NTSC, o VGA permite gerar cores utilizando lógica digital e redes de resistores, sem precisar modular uma subportadora de cor.

Também quero aproveitar essa mudança para melhorar a capacidade gráfica do ISA-1, mantendo três requisitos fundamentais:

- CPU de 8 bits construída com lógica 74HC, sem microcontrolador.
- Geração de vídeo independente da execução das instruções.
- Quantidade de componentes otimizada, sem sacrificar funcionalidades.

## 1. Encontrei uma forma de reduzir o clock do vídeo

O padrão VGA de 640 × 480 utiliza um clock de referência de 25,175 MHz, com frequência horizontal de aproximadamente 31,469 kHz e atualização de 59,94 Hz. <Cite refs={["turn727907search1","turn727907search4"]}/>

Porém, como nossa resolução lógica será de 160 × 120, podemos trabalhar com grupos de quatro pixels horizontais.

**Isso permite reduzir o clock do controlador de vídeo para 6,29375 MHz**, mantendo os intervalos de sincronismo do VGA original.

<card gap={3}>
  <grid columns={2}>
    <grid-item>
      <caption>Clock de referência VGA</caption>
      <title size="2xl">25,175 MHz</title>
    </grid-item>
    <grid-item>
      <caption>Clock do controlador ISA-1</caption>
      <title size="2xl" color="success">6,294 MHz</title>
    </grid-item>
  </grid>
  <divider/>
  <svg viewBox="0 0 320 125" width="100%">
    {#each Array.from({length:8},(_,i)=>i) as i}
      {#each Array.from({length:4},(_,j)=>j) as j}
        <rect x={16+i*36+j*9} y="25" width="8" height="24" rx="1" fill={["#64748b","#0d9488","#2563eb","#ca8a04"][i%4]}/>
      {/each}
      <rect x={16+i*36} y="84" width="35" height="24" rx="2" fill={["#64748b","#0d9488","#2563eb","#ca8a04"][i%4]}/>
    {/each}
    <g fill="currentColor" fontSize="10">
      <text x="16" y="15">Pixels físicos VGA</text>
      <text x="16" y="75">Pixels lógicos ISA-1</text>
    </g>
  </svg>
  <caption>Cada pixel lógico permanece na saída durante quatro intervalos de pixels físicos.</caption>
</card>

Essa redução nos proporciona uma margem temporal mais confortável para os componentes 74HC, embora ainda precisemos verificar os atrasos de propagação reais.

## 2. Arquitetura proposta

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 305" width="100%">
    {#each [{x:5,y:8,w:150,h:48,a:"CPU ISA-1",b:"8 bits · 74HC"},{x:185,y:8,w:150,h:48,a:"RAM principal",b:"32 KB"},{x:5,y:87,w:150,h:48,a:"Arbitragem",b:"CPU / vídeo"},{x:185,y:87,w:150,h:48,a:"Contadores H / V",b:"6,29375 MHz"},{x:5,y:166,w:150,h:48,a:"VRAM",b:"32 KB · RGB222"},{x:185,y:166,w:150,h:48,a:"Latch + DAC RGB",b:"64 cores"},{x:5,y:248,w:150,h:48,a:"Conversor ativo",b:"VGA → HDMI"},{x:185,y:248,w:150,h:48,a:"Arzopa",b:"15,4 polegadas"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="6" fill="#64748b" fillOpacity=".10" stroke="#94a3b8"/>
      <text x={p.x+p.w/2} y={p.y+20} textAnchor="middle" fontSize="11" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+35} textAnchor="middle" fontSize="10" fill="currentColor">{p.b}</text>
    {/each}
    <g fill="none" stroke="#0d9488" strokeWidth="2">
      <path d="M155 32 H185 M80 56 V87 M185 111 H155 M80 135 V166 M155 190 H185 M260 214 V230 H80 V248 M155 272 H185"/>
      <path strokeDasharray="4 3" d="M320 135 V156 H330 V230 H150 V248"/>
    </g>
  </svg>
  <caption>Diagrama funcional preliminar. O sincronismo segue diretamente para a saída VGA.</caption>
</box>

A CPU poderá continuar executando programas enquanto o circuito de vídeo realiza suas próprias leituras. Nos acessos à VRAM, poderá precisar aguardar a liberação do barramento de vídeo.

## 3. Uma otimização da memória de vídeo

Em vez de calcular cada endereço multiplicando a linha por 160, podemos organizar a memória em linhas de 256 bytes.

```c
endereco_video = (y << 8) | x;
```

No hardware, isso significa concatenar os bits dos contadores, sem precisar construir um multiplicador ou somador específico para o vídeo.

| Característica | Valor |
|---|---:|
| VRAM física | 32.768 bytes |
| Pixels úteis | 19.200 |
| Bytes por pixel | 1 |
| Espaço reservado por linha | 256 bytes |
| Memória utilizada pelas linhas | 30.720 bytes |
| Bytes livres totais | 13.568 |

Parte dessa memória livre ficará distribuída no final das linhas. Podemos estudar seu aproveitamento posteriormente.

## 4. Saída VGA com 64 cores

Cada pixel terá oito bits, dos quais seis inicialmente serão utilizados.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={8} gap={1}>
    {#each ["X","X","R1","R0","G1","G0","B1","B0"] as b,i}
      <grid-item>
        <box background={i<2?"#64748b":i<4?"#b91c1c":i<6?"#15803d":"#1d4ed8"} radius="sm" padding={2} align="center">
          <text color="#ffffff" weight="medium" size="xs">{b}</text>
        </box>
        <caption textAlign="center">{7-i}</caption>
      </grid-item>
    {/each}
  </grid>
  <svg viewBox="0 0 320 160" width="100%">
    {#each Array.from({length:64},(_,i)=>i) as i}
      <rect x={i%8*40+1} y={Math.floor(i/8)*20+1} width="38" height="18" rx="2" fill={`rgb(${Math.floor(i/16)*85},${Math.floor(i/4)%4*85},${i%4*85})`}/>
    {/each}
  </svg>
  <caption>As 64 combinações possíveis da paleta RGB222.</caption>
</box>

Também calculei uma rede resistiva preliminar para cada canal RGB.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 320 145" width="100%">
    <g stroke="currentColor" strokeWidth="1.5" fill="none">
      <path d="M30 40 H65 L70 34 L80 46 L90 34 L100 46 L110 34 L120 40 H205 V108"/>
      <path d="M30 80 H65 L70 74 L80 86 L90 74 L100 86 L110 74 L120 80 H205"/>
      <path d="M205 40 H291"/>
      <path d="M205 108 L199 112 L211 117 L199 122 L205 127 V132 M192 132 H218 M197 137 H213 M202 142 H208"/>
    </g>
    <circle cx="205" cy="40" r="3" fill="currentColor"/>
    <circle cx="205" cy="80" r="3" fill="currentColor"/>
    <g fill="currentColor" fontSize="11">
      <text x="8" y="28">MSB</text>
      <text x="8" y="69">LSB</text>
      <text x="75" y="26">700 Ω</text>
      <text x="75" y="66">1,4 kΩ</text>
      <text x="224" y="28">Saída VGA</text>
      <text x="221" y="118">75 Ω</text>
      <text x="221" y="132">Carga do receptor</text>
    </g>
  </svg>
  <caption>Circuito resistivo ideal para um canal de cor. Repetido três vezes para RGB.</caption>
</box>

A primeira combinação de resistores testada ficou abaixo da amplitude desejada. Ajustei os valores no modelo e obtive:

| Intensidade | Tensão ideal calculada |
|---|---:|
| 00 | 0 V |
| 01 | 0,231 V |
| 10 | 0,462 V |
| 11 | 0,692 V |

Ainda precisamos considerar a resistência de saída dos CIs, tolerâncias e capacidade de fornecimento de corrente.

## 5. Primeiros testes realizados

Executei uma bancada Python que percorre um quadro completo de vídeo.

<card gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success" tabularNums>181.800</title>
      <caption>Verificações no laço de simulação</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>19.200</title>
      <caption>Pixels lógicos verificados</caption>
    </grid-item>
    <grid-item>
      <title size="xl">59,940 Hz</title>
      <caption>Atualização calculada</caption>
    </grid-item>
    <grid-item>
      <title size="xl">158,89 ns</title>
      <caption>Intervalo por pixel lógico</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Sincronismo horizontal","Sincronismo vertical","Limites da VRAM","Repetição vertical dos pixels","Níveis RGB no modelo resistivo ideal"] as item}
    <row align="center" gap={2}>
      <icon name="check-circle-2" color="success"/>
      <text size="sm">{item}</text>
    </row>
  {/each}
</card>

Os testes passaram após o ajuste dos resistores. São verificações comportamentais e matemáticas, não uma simulação elétrica.

## 6. Comparação atual das interfaces

| Característica | VGA | SPI | RCA |
|---|---|---|---|
| Cores propostas | 64 | 65.536 | 16 |
| Tela disponível | Sim | Sim | Não |
| Conversor externo | Sim | Não | Não |
| Complexidade | Média | Baixa | Alta |
| Geração contínua independente | Sim | Pelo display | Sim |
| Potencial de expansão | Alto | Médio | Médio |

Neste momento, considero o **VGA o candidato preferencial para o ISA-1**, condicionado à validação elétrica e à compatibilidade do conversor.

## 7. Documentação da revisão 6.6

- [Relatório técnico da arquitetura VGA](sandbox:/mnt/data/isa1/ISA-1_REV66_VGA.md)
- [Simulador Python](sandbox:/mnt/data/isa1/isa1_rev66_vga.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev66_results.json)

## Próxima revisão — 6.7

Agora precisamos transformar essa arquitetura em circuitos reais:

- Contadores horizontais e verticais com 74HC163.
- Decodificação dos sinais HSYNC e VSYNC.
- Seleção dos endereços da VRAM.
- Arbitragem entre CPU e vídeo.
- Levantamento da quantidade real de CIs e dos atrasos de propagação.

Quero especialmente verificar se conseguimos aproveitar os intervalos de apagamento do VGA para a CPU escrever na VRAM sem interromper a imagem.

**O VGA tem bastante potencial para o ISA-1.** Além de aproveitarmos sua Arzopa, teremos uma saída padronizada que poderá funcionar com outros monitores, preservando a identidade de um verdadeiro computador retrô construído com lógica discreta. 😎

## user — bbb21a1a-a448-47fe-bba3-ebd9cd3954ba

Boa pode seguir então com o VGA
A gente vai precisar revisar depois a alimentação, pois não vamos precisar dos 12v
Além disso, rgb5 funcionaria aqui pra reduzir custo e ainda entregar cores? Já usei em outros projetos com arduíno

## assistant — 9c6f8b45-72ad-4191-b48e-f2fcc4af9a82

{"content_type": "thoughts", "source_analysis_msg_id": "2f9ec2bd-a65a-469b-9f53-01c342cc5451", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 11 sites"}]}

## assistant — 403548c3-a0e5-45ab-8d63-f506a8c59a62

{"content": "Pensou por 5s", "content_type": "reasoning_recap"}

## assistant — 2aa78dae-2ef7-43ef-ac0c-975bb479c0ce

Ótima observação! 😎 Temos duas oportunidades de otimização no ISA-1: **simplificar a alimentação e reduzir a quantidade de circuitos do vídeo**.

E sim, podemos trabalhar com RGB de 5 bits, se você estiver se referindo ao formato RGB221, com cinco sinais digitais de cor. Teríamos 32 cores simultâneas, o que é bastante interessante para um computador retrô de 8 bits.

## 1. Revisão da alimentação

Com a adoção do VGA e da tela Arzopa, podemos retirar do projeto:

- Conversor boost de 5 V para 12 V.
- Circuito de seleção da alimentação externa de 12 V.
- Conector de alimentação de 12 V.
- Circuitos de proteção específicos dessa linha.

Isso reduz o custo, o espaço ocupado na PCB e uma possível fonte de interferência elétrica.

Minha proposta é manter toda a lógica principal em 5 V, alimentada por USB-C, e inicialmente alimentar a Arzopa separadamente. O conversor VGA para HDMI também poderá receber 5 V, desde que o modelo escolhido permita.

Ainda precisaremos recalcular o consumo total e dimensionar a alimentação antes de fechar a PCB.

## 2. RGB de 5 bits versus 6 bits

Podemos implementar RGB221 (2 bits de vermelho, 2 de verde e 1 de azul). A menor resolução do canal azul é uma escolha razoável devido à menor sensibilidade visual humana a esse canal.

Veja a comparação das paletas:

<box border radius="lg" padding={3} gap={3}>
  <row justify="between" align="center">
    **RGB111**
    <caption>3 bits · 8 cores</caption>
  </row>
  <svg viewBox="0 0 320 40" width="100%">
    {#each Array.from({length:8},(_,i)=>i) as i}
      <rect x={i*40+1} y="1" width="38" height="38" rx="2" fill={`rgb(${(i>>2&1)*255},${(i>>1&1)*255},${(i&1)*255})`}/>
    {/each}
  </svg>
  <divider/>
  <row justify="between" align="center">
    **RGB221**
    <caption>5 bits · 32 cores</caption>
  </row>
  <svg viewBox="0 0 320 120" width="100%">
    {#each Array.from({length:32},(_,i)=>i) as i}
      <rect x={i%8*40+1} y={Math.floor(i/8)*30+1} width="38" height="28" rx="2" fill={`rgb(${(i>>3&3)*85},${(i>>1&3)*85},${(i&1)*255})`}/>
    {/each}
  </svg>
  <divider/>
  <row justify="between" align="center">
    **RGB222**
    <caption>6 bits · 64 cores</caption>
  </row>
  <svg viewBox="0 0 320 160" width="100%">
    {#each Array.from({length:64},(_,i)=>i) as i}
      <rect x={i%8*40+1} y={Math.floor(i/8)*20+1} width="38" height="18" rx="2" fill={`rgb(${(i>>4&3)*85},${(i>>2&3)*85},${(i&3)*85})`}/>
    {/each}
  </svg>
  <divider/>
  <row justify="between" align="center">
    **RGB332**
    <caption>8 bits · 256 cores</caption>
  </row>
  <svg viewBox="0 0 320 240" width="100%">
    {#each Array.from({length:256},(_,i)=>i) as i}
      <rect x={i%16*20+0.5} y={Math.floor(i/16)*15+0.5} width="19" height="14" fill={`rgb(${Math.round((i>>5&7)*255/7)},${Math.round((i>>2&7)*255/7)},${(i&3)*85})`}/>
    {/each}
  </svg>
  <caption>Representação ideal das paletas digitais.</caption>
</box>

## 3. Mas será que realmente economizamos?

Aqui encontrei um ponto interessante. Como nossa CPU, SRAM e barramento já trabalham com 8 bits, talvez seja mais vantajoso aproveitar todos os bits do pixel.

| Característica | RGB111 | RGB221 | RGB222 | RGB332 |
|---|---:|---:|---:|---:|
| Cores | 8 | 32 | 64 | 256 |
| Resistores de cor | 3 | 5 | 6 | 8 |
| Registradores de saída de 8 bits | 1 | 1 | 1 | 1 |
| VRAM física | 32 KB | 32 KB | 32 KB | 32 KB |
| Bytes por pixel | 1 | 1 | 1 | 1 |
| Resolução | 160×120 | 160×120 | 160×120 | 160×120 |

Considerando a arquitetura atual, reduzir de seis para cinco bits economizaria apenas um resistor e uma conexão, caso utilizemos o mesmo registrador octal.

Por outro lado, aumentando para oito bits, podemos oferecer **256 cores sem aumentar a capacidade da memória nem a largura do barramento**.

## 4. E se adotássemos RGB332?

<box border radius="lg" padding={3} gap={3}>
  <grid columns={8} gap={1}>
    {#each ["R2","R1","R0","G2","G1","G0","B1","B0"] as b,i}
      <grid-item>
        <box background={i<3?"#b91c1c":i<6?"#15803d":"#1d4ed8"} radius="sm" padding={2} align="center">
          <text color="#ffffff" weight="medium" size="xs">{b}</text>
          <text color="#ffffff" size="2xs">{7-i}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <svg viewBox="0 0 320 186" width="100%">
    <rect x="2" y="4" width="316" height="40" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="160" y="28" textAnchor="middle" fill="currentColor" fontSize="12">Registrador de pixel de 8 bits</text>
    {#each [0,1,2,3,4,5,6,7] as i}
      <g stroke={i<3?"#dc2626":i<6?"#16a34a":"#2563eb"} fill="none" strokeWidth="1.5">
        <path d={`M${20+i*40} 44 V65 l-4 4 l8 5 l-8 5 l8 5 l-4 4 V112 H${i<3?60:i<6?180:280} V143`}/>
      </g>
    {/each}
    {#each [{x:60,c:"#dc2626",s:"RED"},{x:180,c:"#16a34a",s:"GREEN"},{x:280,c:"#2563eb",s:"BLUE"}] as p}
      <circle cx={p.x} cy="112" r="3" fill={p.c}/>
      <rect x={p.x-29} y="143" width="58" height="30" rx="5" fill={p.c}/>
      <text x={p.x} y="162" fontSize="11" fill="white" textAnchor="middle">{p.s}</text>
    {/each}
  </svg>
  <caption>Conversão resistiva de oito bits digitais em três canais analógicos VGA.</caption>
</box>

O princípio de utilizar resistores ponderados para gerar os níveis analógicos do VGA é bem estabelecido. Precisamos atingir aproximadamente 0,7 V por canal sobre a terminação de 75 Ω do receptor. <Cite refs={["turn808141search13","turn808141search3"]}/>

Ainda precisamos dimensionar o circuito levando em consideração a corrente máxima das saídas dos CIs, os níveis lógicos reais e as tolerâncias dos resistores.

## 5. Decisões para a revisão 6.7

Minha proposta é seguir com estas especificações:

| Item | Especificação proposta |
|---|---|
| Saída de vídeo | VGA |
| Sinal de vídeo | 640 × 480, ~60 Hz |
| Resolução lógica | 160 × 120 |
| Profundidade de cor | RGB332 — 256 cores |
| VRAM | 32 KB |
| RAM principal | 32 KB |
| Clock de vídeo | 6,29375 MHz |
| Alimentação principal | USB-C 5 V |
| Linha de 12 V | Eliminada |
| Tela principal | Arzopa |
| Tela auxiliar opcional | ILI9341 SPI |

## 6. Próximos testes

Vou priorizar a validação dos contadores de vídeo, da arbitragem da VRAM, do DAC resistivo RGB332 e do novo orçamento de alimentação de 5 V.

Também quero investigar se podemos reutilizar os intervalos de apagamento do VGA para a CPU acessar a VRAM, evitando adicionar componentes desnecessários.

**Sua sugestão de RGB de 5 bits acabou levantando uma possibilidade ainda melhor: entregar 256 cores praticamente com a mesma arquitetura de 32 cores.**

Se os cálculos elétricos confirmarem essa viabilidade, teremos um computador mais capaz graficamente, sem aumentar significativamente o custo. 😎

## user — bbb21780-48be-4ef5-9396-a6dd251ffc88

Perfeito! Melhor ainda😎 vamos validar o 332

## assistant — 0f6b8252-3148-429d-9afd-370f1ce2259f

{"content_type": "thoughts", "source_analysis_msg_id": "08ebd960-db74-41a2-8416-fea3590f11dc", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Criou diretório, calculou modelo RGB332 e gerou documentação"}]}

## assistant — 323a608b-eb4f-424a-8ec2-b58c6c1b8905

{"content": "Pensou por 38s", "content_type": "reasoning_recap"}

## assistant — f0d0a158-6c4d-4e70-a058-3c9558b38658

# ISA-1 — Revisão 6.7: validação do RGB332 😎

Vamos validar as **256 cores utilizando apenas oito saídas digitais e oito resistores**, aproveitando integralmente nosso barramento de 8 bits.

A grande vantagem dessa arquitetura é que, em relação ao RGB221 de 32 cores, não precisamos aumentar a memória de vídeo, a largura do barramento ou a quantidade de registradores de pixel.

## 1. Formato do pixel

<box border radius="lg" padding={3} gap={3}>
  <grid columns={8} gap={1}>
    {#each ["R2","R1","R0","G2","G1","G0","B1","B0"] as b,i}
      <grid-item>
        <box background={i<3?"#b91c1c":i<6?"#15803d":"#1d4ed8"} radius="sm" padding={2} align="center">
          <text color="#ffffff" weight="medium">{b}</text>
          <text color="#ffffff" size="xs">{7-i}</text>
        </box>
      </grid-item>
    {/each}
  </grid>
  <grid columns={3}>
    <grid-item>
      <title size="xl">8</title>
      <caption>Níveis de vermelho</caption>
    </grid-item>
    <grid-item>
      <title size="xl">8</title>
      <caption>Níveis de verde</caption>
    </grid-item>
    <grid-item>
      <title size="xl">4</title>
      <caption>Níveis de azul</caption>
    </grid-item>
  </grid>
  <svg viewBox="0 0 320 240" width="100%">
    {#each Array.from({length:256},(_,i)=>i) as i}
      <rect x={i%16*20+0.5} y={Math.floor(i/16)*15+0.5} width="19" height="14" fill={`rgb(${Math.round((i>>5&7)*255/7)},${Math.round((i>>2&7)*255/7)},${(i&3)*85})`}/>
    {/each}
  </svg>
  <caption>Paleta digital completa do ISA-1 em RGB332.</caption>
</box>

Cada endereço da VRAM representará diretamente a cor de um pixel. Não precisaremos de uma memória adicional para armazenar a paleta.

## 2. Primeira bancada de testes

Executei um modelo matemático do DAC resistivo, considerando a terminação VGA de 75 Ω.

Além das 256 combinações de cores, testei variações hipotéticas de alimentação, tolerância dos resistores, impedância do receptor e resistência de saída dos circuitos integrados.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success">581</title>
      <caption>Verificações aprovadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">324</title>
      <caption>Cenários de variação elétrica</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">256</title>
      <caption>Combinações de cores distintas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">8</title>
      <caption>Resistores necessários</caption>
    </grid-item>
  </grid>
</box>

Todos os níveis de intensidade permaneceram em ordem crescente nos cenários testados. Entretanto, encontrei dois pontos que precisam de ajustes: a amplitude máxima do sinal e a corrente exigida das saídas digitais.

Ou seja, **o formato RGB332 está aprovado no modelo digital, mas o circuito analógico ainda precisa de refinamento.**

## 3. Ajuste dos resistores

Após os primeiros testes, ajustei os valores da rede resistiva e executei novamente a bancada.

| Sinal | Resistência calculada |
|---|---:|
| R2 | 820 Ω |
| R1 | 1.640 Ω |
| R0 | 3.280 Ω |
| G2 | 820 Ω |
| G1 | 1.640 Ω |
| G0 | 3.280 Ω |
| B1 | 700 Ω |
| B0 | 1.400 Ω |

Esses são valores-alvo de projeto. Ainda vamos selecionar os valores comerciais definitivos.

### Resultado das tensões nominais

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 320 200" width="100%">
    {#each [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7] as v}
      <line x1="37" y1={165-v*200} x2="310" y2={165-v*200} stroke="currentColor" opacity=".12"/>
      <text x="29" y={169-v*200} fontSize="9" fill="currentColor" textAnchor="end">{v.toFixed(1)}</text>
    {/each}
    {#each Array.from({length:8},(_,i)=>i) as i}
      <rect x={40+i*34} y={165-i*.0985545*200} width="10" height={i*.0985545*200} fill="#dc2626"/>
      <rect x={51+i*34} y={165-i*.0985545*200} width="10" height={i*.0985545*200} fill="#16a34a"/>
      <text x={50+i*34} y="180" fontSize="9" fill="currentColor" textAnchor="middle">{i}</text>
    {/each}
    <line x1="37" y1="25" x2="310" y2="25" stroke="currentColor" strokeDasharray="4 3"/>
    <text x="310" y="18" textAnchor="end" fontSize="10" fill="currentColor">Alvo: 0,7 V</text>
    <text x="175" y="195" textAnchor="middle" fontSize="10" fill="currentColor">Nível digital R/G</text>
  </svg>
  <grid columns={3}>
    {#each [{c:"danger",n:"Vermelho",v:"0,690 V"},{c:"success",n:"Verde",v:"0,690 V"},{c:"info",n:"Azul",v:"0,692 V"}] as p}
      <grid-item>
        <caption>{p.n}</caption>
        <title color={p.c} size="lg">{p.v}</title>
      </grid-item>
    {/each}
  </grid>
  <caption>Tensões máximas calculadas com alimentação ideal de 5 V e carga de 75 Ω.</caption>
</box>

Ficamos muito próximos dos 0,7 V desejados em condições nominais.

Entretanto, nos cenários de tolerância simulados, os picos variaram aproximadamente entre 0,59 V e 0,76 V. Isso significa que ainda precisamos melhorar ou caracterizar a precisão do circuito.

## 4. Um cuidado com os CIs 74HC

A corrente máxima calculada por saída chegou a aproximadamente **6,9 mA**.

Precisamos verificar se o registrador escolhido consegue fornecer essa corrente mantendo os níveis de tensão adequados, inclusive quando todos os canais estiverem ativos.

Vou considerar inicialmente:

| Componente | Função |
|---|---|
| 74HC574 | Registrador de pixel de 8 bits |
| 74HC244 | Buffer de saída, se necessário |
| 8 resistores de precisão | Conversão digital-analógica |
| Conector DE-15 | Saída VGA |

O buffer adicional somente será adotado se houver necessidade elétrica comprovada.

## 5. Especificações gráficas do ISA-1

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">256</title>
      <caption>Cores simultâneas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">160 × 120</title>
      <caption>Resolução lógica</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">59,94 Hz</title>
      <caption>Atualização projetada</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">32 KB</title>
      <caption>VRAM dedicada</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">5 V</title>
      <caption>Alimentação principal</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">6,294 MHz</title>
      <caption>Clock lógico de vídeo</caption>
    </grid-item>
  </grid>
</box>

## 6. Documentação produzida

- [Relatório técnico — Revisão 6.7](sandbox:/mnt/data/isa1/ISA-1_REV67_RGB332.md)
- [Simulador do DAC RGB332](sandbox:/mnt/data/isa1/isa1_rev67_rgb332.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev67_results.json)
- [Tabela completa das 256 cores e tensões](sandbox:/mnt/data/isa1/isa1_rev67_palette.csv)

## 7. Próxima revisão — 6.8

Vamos trabalhar nos contadores horizontais e verticais, sincronismo VGA, arbitragem da VRAM e temporização dos componentes reais. Também vamos revisar a alimentação, eliminando definitivamente a necessidade dos 12 V da placa principal.

**RGB332 aprovado como formato gráfico do ISA-1.** O DAC resistivo permanece em validação elétrica antes da fabricação.

Conseguimos evoluir de 16 para 256 cores sem aumentar a largura do barramento e sem adicionar uma memória de paleta. É exatamente o tipo de otimização que buscamos para o ISA-1: mais funcionalidades com praticamente os mesmos recursos. 😎

## user — bbb2154a-f67d-4efe-bd5b-5593e32fd753

Boa pode continuar😎

## assistant — c371e96d-894a-4aea-b27e-b3b7a7637a06

{"content_type": "thoughts", "source_analysis_msg_id": "79c7139e-2b24-43cb-b2ae-a8fd472f9db9", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos isa1 e verificou temporização VGA e arbitragem de VRAM"}]}

## assistant — d2e0c61b-e4d4-4d8c-9cd5-1b715ef9ed46

{"content": "Pensou por 25s", "content_type": "reasoning_recap"}

## assistant — 4974d947-8e2b-4271-a488-89119737ab68

# ISA-1 — Revisão 6.8: sincronismo VGA e arbitragem da VRAM 😎

Com o RGB332 definido como nosso formato gráfico, vamos avançar para o circuito responsável por gerar a imagem continuamente.

Nesta etapa, quero resolver três questões fundamentais: a geração dos sincronismos VGA, o compartilhamento seguro da VRAM e a simplificação da alimentação para 5 V.

A CPU continuará independente do vídeo. Não vamos utilizar a execução de instruções para manter a imagem na tela, nem sacrificar recursos da CPU para economizar componentes.

## 1. Geração do sincronismo VGA

Consegui organizar a temporização utilizando apenas cinco contadores de 4 bits como base do circuito.

| Parâmetro | Horizontal | Vertical |
|---|---:|---:|
| Contadores 74HC163 | 2 | 3 |
| Área visível | 160 | 480 |
| Front porch | 4 | 10 |
| Pulso de sincronismo | 24 | 2 |
| Back porch | 12 | 33 |
| Contagem total | 200 | 525 |

O contador vertical avançará ao término de cada linha, utilizando o mesmo clock dos contadores horizontais. Isso evita utilizar sinais de decodificação diretamente como clock.

<box border radius="lg" padding={3} gap={3}>
  <svg viewBox="0 0 340 155" width="100%">
    <g fontSize="10" fill="currentColor">
      <text x="10" y="14">Linha VGA — 31,78 µs</text>
      <rect x="10" y="25" width="256" height="28" rx="2" fill="#16a34a"/>
      <rect x="266" y="25" width="64" height="28" rx="2" fill="#64748b"/>
      <text x="138" y="43" textAnchor="middle" fill="white">160 pixels RGB332</text>
      <text x="298" y="43" textAnchor="middle" fill="white" fontSize="9">Blanking</text>
      <text x="10" y="77">HSYNC</text>
      <text x="10" y="123">Janela de acesso da CPU à VRAM</text>
    </g>
    <path d="M10 84 H272.4 V103 H310.8 V84 H330" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <rect x="269.2" y="132" width="57.6" height="14" rx="2" fill="#2563eb"/>
    <line x1="266" y1="54" x2="266" y2="148" stroke="currentColor" strokeDasharray="3 3" opacity=".4"/>
  </svg>
  <caption>Durante o apagamento horizontal, a CPU poderá solicitar acesso à memória de vídeo.</caption>
</box>

## 2. Arbitragem da VRAM

Encontrei uma maneira conservadora de compartilhar a VRAM sem interromper a geração da imagem.

Vamos reservar os intervalos de apagamento horizontal para as operações da CPU na memória de vídeo.

Cada operação terá quatro fases:

<box border radius="lg" padding={3} gap={2}>
  <grid columns={4} gap={1}>
    {#each [{n:"T1",t:"Selecionar",s:"Endereço"},{n:"T2",t:"Acessar",s:"Leitura ou escrita"},{n:"T3",t:"Liberar",s:"Barramento"},{n:"T4",t:"Repousar",s:"Proteção"}] as p}
      <grid-item>
        <box background="surface-secondary" radius="md" padding={2} align="center">
          <text weight="medium">{p.n}</text>
          <text size="xs">{p.t}</text>
          <caption textAlign="center">{p.s}</caption>
        </box>
      </grid-item>
    {/each}
  </grid>
  <caption>Sequência proposta de 635,55 ns por transação. Temporização elétrica ainda pendente.</caption>
</box>

### Desempenho teórico

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">283 KB/s</title>
      <caption>Capacidade teórica de acesso à VRAM</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">4.725</title>
      <caption>Janelas de acesso por quadro</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">14,75</title>
      <caption>Imagens completas por segundo, no limite teórico</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">59,94 Hz</title>
      <caption>Atualização contínua do monitor</caption>
    </grid-item>
  </grid>
</box>

É importante distinguir a velocidade de atualização do conteúdo da VRAM da frequência do monitor.

A imagem continuará sendo exibida a aproximadamente 60 Hz, mesmo que a CPU não altere nenhum pixel.

Para jogos, poderemos atualizar somente as regiões modificadas, como personagens, objetos e elementos do cenário. A taxa real dependerá também da velocidade da CPU.

## 3. Primeira estimativa dos componentes

| Componente | Quantidade | Função |
|---|---:|---|
| 74HC163 | 5 | Contadores de vídeo |
| 74HC157 | 4 | Seleção de endereço da VRAM |
| 74HC574 | 1 | Registrador RGB332 |
| SRAM 32 KB | 1 | Memória de vídeo |
| Oscilador | 1 | Clock de referência |
| Resistores | 8 | DAC RGB332 |
| DE-15 | 1 | Conector VGA |

Temos uma base de **12 componentes ativos, incluindo o oscilador**, sem contar a lógica de controle, sincronismo, apagamento e eventuais buffers.

Ainda não é a quantidade definitiva de CIs. Quero dimensionar esses blocos antes de tentar reduzi-los.

## 4. Testes executados nesta revisão

Criei e executei uma bancada Python que percorre um quadro completo, verificando os contadores, endereços de vídeo e janelas de acesso da CPU.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success" tabularNums>186.525</title>
      <caption>Verificações executadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>0</title>
      <caption>Falhas encontradas</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Contagem horizontal e vertical","Endereçamento dos 19.200 pixels","Repetição vertical da imagem","Duração dos pulsos de sincronismo","Janelas de acesso sem sobreposição com a área visível","Retorno dos contadores ao início do quadro"] as item}
    <row align="center" gap={2}>
      <icon name="check-circle-2" color="success"/>
      <text size="sm">{item}</text>
    </row>
  {/each}
</box>

Encontrei também um ponto que merece atenção: precisamos buscar o primeiro pixel de cada linha antecipadamente, para que ele esteja disponível quando a área visível começar.

Reservei intervalos de proteção para isso, mas ainda precisamos demonstrar que são suficientes considerando os atrasos reais dos componentes.

## 5. Nova arquitetura de alimentação

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 220" width="100%">
    {#each [{x:105,y:5,w:130,h:40,a:"USB-C",b:"5 V"},{x:105,y:65,w:130,h:40,a:"Proteção e filtragem",b:"Distribuição 5 V"},{x:5,y:130,w:100,h:44,a:"CPU 74HC",b:"RAM + EEPROM"},{x:120,y:130,w:100,h:44,a:"Vídeo VGA",b:"VRAM + DAC"},{x:235,y:130,w:100,h:44,a:"Periféricos",b:"Teclado e I/O"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="6" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={p.x+p.w/2} y={p.y+17} textAnchor="middle" fontSize="10" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+31} textAnchor="middle" fontSize="9" fill="currentColor">{p.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M170 45 V65 M170 105 V130 M170 117 H55 V130 M170 117 H285 V130"/>
    </g>
    <text x="170" y="200" textAnchor="middle" fill="currentColor" fontSize="11">Arzopa alimentada separadamente</text>
  </svg>
</box>

Com essa arquitetura, podemos retirar definitivamente da proposta da placa principal o conversor boost de 12 V e seus componentes auxiliares.

Ainda precisamos dimensionar a corrente total, a proteção da entrada USB-C, os capacitores de desacoplamento e a alimentação do conversor VGA para HDMI.

## 6. Documentação produzida

- [Relatório técnico — Revisão 6.8](sandbox:/mnt/data/isa1/ISA-1_REV68_VGA_ARBITRAGEM.md)
- [Simulador Python de sincronismo e arbitragem](sandbox:/mnt/data/isa1/isa1_rev68.py)
- [Resultados reproduzíveis em JSON](sandbox:/mnt/data/isa1/isa1_rev68_results.json)

## 7. Estado atual do ISA-1

| Subsistema | Situação |
|---|---|
| CPU de 8 bits | Arquitetura definida |
| Endereçamento de 16 bits | Definido |
| RAM principal de 32 KB | Mantida |
| EEPROM removível de 32 KB | Mantida |
| VGA 160 × 120 | Modelo comportamental testado |
| RGB332 — 256 cores | Formato aprovado |
| VRAM dedicada de 32 KB | Modelo de endereçamento testado |
| Arbitragem de vídeo | Janelas validadas no modelo |
| Alimentação de 5 V | Arquitetura simplificada |
| Esquemático elétrico completo | Pendente |

**Próxima revisão — 6.9:** selecionar os componentes reais da VRAM, verificar os tempos máximos dos datasheets, dimensionar o caminho entre contador, multiplexador, SRAM e registrador de pixel, e implementar a lógica de arbitragem.

Estamos construindo um computador com 256 cores, saída VGA padronizada e CPU independente do vídeo. Agora precisamos comprovar que os componentes físicos conseguem executar tudo isso dentro dos 158,89 ns disponíveis por pixel lógico. 😎

## user — bbb21e94-ae81-405b-87e0-18558ddb48b9

Ihuuuu tá ficando melhor do que imaginei! Pode seguir

## assistant — 6875a39e-691b-4ce5-a524-4c568657f259

{"content_type": "thoughts", "source_analysis_msg_id": "2ab64020-1ab8-4391-a066-529ce629fb03", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 2 sites"}]}

## assistant — 0964e913-6b9f-41e2-a2bf-323d0e49226f

{"content_type": "thoughts", "source_analysis_msg_id": "cc3a882a-848b-45c5-8894-2e8549cbf2ff", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Calculou temporização VGA e documentou orçamento temporal do ISA-1"}]}

## assistant — 99112670-64cd-4efb-8c74-38a5a65c319e

{"content": "Pensou por 27s", "content_type": "reasoning_recap"}

## assistant — cc47c8bc-e83a-4d9f-9528-ce306a7714c9

# ISA-1 — Revisão 6.9: viabilidade dos componentes físicos 😎

Agora chegamos a uma etapa decisiva: verificar se os componentes conseguem acompanhar a velocidade do vídeo VGA RGB332.

Temos apenas **158,89 nanossegundos por pixel lógico**. Dentro desse intervalo, precisamos selecionar o endereço da VRAM, ler o byte correspondente e armazená-lo no registrador de saída RGB.

A boa notícia é que podemos estudar esse caminho sem aumentar o clock da CPU e sem abandonar a arquitetura de 256 cores.

## 1. Seleção dos componentes reais

Consultei os datasheets da Texas Instruments e da ISSI. Encontramos uma SRAM de 32 KB que opera diretamente com 5 V e possui versões com tempos de acesso de 25 e 45 ns. <Cite ref="turn268236search19"/>

| Componente | Função | Quantidade |
|---|---|---:|
| SN74HC163 | Contadores H/V | 5 |
| SN74HC157 | Multiplexadores de endereço | 4 |
| IS62C256AL | VRAM de 32 KB | 1 |
| 74HCT574 | Candidato a registrador de pixel | 1 |
| Oscilador | Referência temporal | 1 |

Essa é a base do circuito, ainda sem contabilizar toda a lógica de sincronismo, arbitragem, apagamento e reset.

## 2. Encontramos dois pontos críticos

**Primeiro: a velocidade da SRAM importa bastante.**

O SN74HC157 apresenta atraso máximo de propagação de 38 ns com carga de 50 pF, podendo chegar a 47 ns no caminho de dados com carga de 150 pF, nas condições de 4,5 V do datasheet. <Cite refs={["turn268236search17","turn268236search15"]}/>

**Segundo: a compatibilidade dos níveis lógicos.**

A SRAM encontrada possui saídas compatíveis com TTL. Isso significa que não devemos presumir que suas saídas atendam aos níveis de entrada CMOS de um 74HC574.

Por isso, vamos estudar a versão **74HCT574**, que possui entradas compatíveis com níveis TTL, além de alternativas com maior capacidade de corrente para o DAC RGB332.

Essa verificação é importante para evitar erros intermitentes de leitura dos pixels.

## 3. Teste do orçamento temporal

Executei uma bancada Python variando os tempos de acesso da memória e os atrasos dos demais componentes.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 122" width="100%">
    {#each [{x:8,w:98,a:"Contadores",b:"H / V"},{x:122,w:96,a:"MUX",b:"74HC157"},{x:234,w:98,a:"VRAM",b:"32 KB"}] as p}
      <rect x={p.x} y="8" width={p.w} height="43" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={p.x+p.w/2} y="25" fontSize="11" textAnchor="middle" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y="40" fontSize="10" textAnchor="middle" fill="currentColor">{p.b}</text>
    {/each}
    <rect x="234" y="76" width="98" height="38" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="283" y="99" fontSize="10" textAnchor="middle" fill="currentColor">Registro RGB</text>
    <path d="M106 29 H122 M218 29 H234 M283 51 V76" stroke="#0d9488" strokeWidth="2" fill="none"/>
  </svg>
  <caption>Caminho crítico da leitura de cada pixel.</caption>
  <divider/>
  <title size="md">Tempo ocupado no cenário conservador</title>
  {#each [{name:"SRAM 25 ns",n:152},{name:"SRAM 45 ns",n:172},{name:"SRAM 55 ns",n:182}] as r}
    <row align="center">
      <text size="sm" weight="medium">{r.name}</text>
      <spacer/>
      <text color={r.n>158.887?"danger":"success"} weight="medium" tabularNums>{r.n} ns</text>
    </row>
    <box height="14px" background="surface-tertiary" radius="sm" clip={true}>
      <box height="14px" width={`${r.n/200*100}%`} background={r.n>158.887?"#dc2626":"#16a34a"}/>
    </box>
  {/each}
  <caption>Limite disponível: 158,89 ns. Os atrasos do contador e do setup ainda são estimativas de engenharia, não máximos verificados.</caption>
</box>

Dos 12 cenários calculados, **7 ficaram dentro do orçamento temporal e 5 ultrapassaram o limite**.

Isso torna a SRAM de 25 ns nossa candidata preferencial. A versão de 45 ns ainda poderá ser utilizada se otimizarmos o caminho crítico.

Não precisamos reduzir a resolução nem abandonar as 256 cores.

## 4. Validação da leitura antecipada

Também executei uma simulação de um quadro completo, buscando cada pixel um ciclo antes de sua exibição.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">105.000</title>
      <caption>Ciclos de vídeo simulados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">76.800</title>
      <caption>Buscas de pixels</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">4.725</title>
      <caption>Transações potenciais da CPU por quadro</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">283 KB/s</title>
      <caption>Limite teórico de acesso à VRAM</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success"/>
    Nenhuma sobreposição lógica entre busca de pixels e acesso reservado à CPU.
  </row>
</box>

A arbitragem temporal continua viável no modelo. Ainda precisamos implementar a comunicação entre os domínios de clock da CPU e do vídeo.

## 5. Estado atualizado do projeto

| Subsistema | Situação |
|---|---|
| RGB332 — 256 cores | Mantido |
| Resolução 160 × 120 | Mantida |
| VGA 640 × 480 | Modelo comportamental aprovado |
| VRAM de 32 KB | Componente candidato identificado |
| SRAM de 25 ns | Preferencial |
| Alimentação de 12 V | Removida do projeto |
| USB-C 5 V | Mantido |
| Temporização elétrica | Validação parcial |
| DAC analógico | Em refinamento |

## 6. Documentação produzida

- [Relatório técnico — Revisão 6.9](sandbox:/mnt/data/isa1/ISA-1_REV69_TEMPORIZACAO_FISICA.md)
- [Bancada Python de temporização](sandbox:/mnt/data/isa1/isa1_rev69.py)
- [Resultados completos dos testes](sandbox:/mnt/data/isa1/isa1_rev69_results.json)

## 7. Próxima revisão — 7.0

Vamos começar a consolidar o circuito elétrico do vídeo:

- Pinagem real da VRAM.
- Conexões dos cinco contadores.
- Multiplexadores de endereços.
- Registrador de pixels e DAC RGB332.
- Sinais de controle da memória.
- Proteção contra conflitos entre CPU e vídeo.

Também precisaremos fechar o mapa de memória global para acomodar a VRAM sem perder a capacidade da RAM principal ou da EEPROM removível.

**O ISA-1 está ficando muito mais interessante:** começamos com uma proposta de 16 cores em uma pequena tela RCA e evoluímos para 256 cores com saída VGA padronizada, aproveitando o monitor que você já possui.

E, principalmente, mantendo nossa própria CPU. 😎

## user — bbb21395-f6fc-49f5-8306-6bf8384e0869

Sucesso! Pode seguir

## assistant — 5b6767fc-4a1d-4611-834e-a07377a570d9

{"content_type": "thoughts", "source_analysis_msg_id": "b5346cc5-6af1-4215-9491-81c385fe2443", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Analisou especificação ISA-1, memória, reset, vídeo e raster"}]}

## assistant — 2faf2d71-7d51-4c1d-a1c3-81b44b4bb1cb

{"content": "Pensou por 41s", "content_type": "reasoning_recap"}

## assistant — 4415409a-f1e9-45f6-9eb7-89466b29ae43

# ISA-1 — Revisão 7.0: integração do vídeo com a CPU 😎

Chegamos a uma etapa importante: integrar a arquitetura VGA RGB332 ao restante do computador, sem comprometer os recursos da CPU.

Temos 96 KiB de memória física distribuídos entre RAM principal, EEPROM removível e VRAM. Entretanto, nossa CPU possui endereçamento de 16 bits, permitindo acessar diretamente apenas 64 KiB.

Precisamos resolver isso antes de consolidar o esquemático.

## 1. Proposta de mapa de memória

Minha proposta é utilizar janelas de memória com seleção de bancos, preservando os 32 KiB de RAM principal permanentemente acessíveis.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 260" width="100%">
    {#each [{y:12,h:55,c:"#2563eb",a:"C000 – FFFF",b:"EEPROM · 2 bancos de 16 KiB"},{y:67,h:38,c:"#9333ea",a:"A000 – BFFF",b:"Periféricos e controle"},{y:105,h:38,c:"#0d9488",a:"8000 – 9FFF",b:"VRAM · 4 bancos de 8 KiB"},{y:143,h:106,c:"#15803d",a:"0000 – 7FFF",b:"RAM principal · 32 KiB"}] as p}
      <rect x="8" y={p.y} width="324" height={p.h-2} rx="4" fill={p.c} fillOpacity=".85"/>
      <text x="170" y={p.y+p.h/2-3} textAnchor="middle" fontSize="12" fontWeight="bold" fill="white">{p.a}</text>
      <text x="170" y={p.y+p.h/2+12} textAnchor="middle" fontSize="10" fill="white">{p.b}</text>
    {/each}
  </svg>
  <caption>Mapa de memória proposto para funcionamento normal, após o boot.</caption>
</box>

| Memória | Capacidade física | Janela acessível |
|---|---:|---:|
| RAM principal | 32 KiB | 32 KiB |
| VRAM | 32 KiB | 8 KiB |
| EEPROM removível | 32 KiB | 16 KiB |
| Periféricos | — | 8 KiB |

Assim, conseguimos acessar toda a memória física sem aumentar a largura do barramento de endereços.

Também preservei os dois espaços de salvamento da EEPROM removível.

## 2. Como selecionar os bancos?

Reservei três endereços para controle interno:

| Endereço | Função |
|---|---|
| `A000` | Selecionar banco da VRAM |
| `A001` | Selecionar banco da EEPROM |
| `A002` | Desativar o mapeamento especial de inicialização |

Durante a inicialização, a EEPROM ficará temporariamente visível no endereço `0000`, permitindo que nossa CPU comece a executar código após o reset.

Depois da inicialização, essa região volta a pertencer à RAM principal.

Precisaremos adaptar o cabeçalho da EEPROM para acomodar o salto inicial. Essa alteração ainda não está implementada no emulador da CPU.

## 3. Consolidação do circuito VGA

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 285" width="100%">
    {#each [{x:5,y:5,w:150,h:44,a:"CPU ISA-1",b:"Endereço + banco"},{x:185,y:5,w:150,h:44,a:"5 × 74HC163",b:"Contadores VGA"},{x:95,y:77,w:150,h:44,a:"4 × 74HC157",b:"Seleção de endereço"},{x:95,y:145,w:150,h:44,a:"SRAM 32 KiB",b:"25 ns — candidata"},{x:95,y:213,w:150,h:44,a:"74HCT574",b:"Registrador RGB332"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="6" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={p.x+p.w/2} y={p.y+17} fontSize="11" textAnchor="middle" fill="currentColor">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+32} fontSize="10" textAnchor="middle" fill="currentColor">{p.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M80 49 V62 H135 V77 M260 49 V62 H205 V77 M170 121 V145 M170 189 V213 M170 257 V270"/>
    </g>
    <text x="170" y="282" textAnchor="middle" fontSize="10" fill="currentColor">DAC resistivo → VGA</text>
  </svg>
  <caption>Datapath funcional preliminar. Buffers, arbitragem e sinais de controle ainda precisam ser detalhados.</caption>
</box>

Os cinco contadores utilizarão um clock comum, evitando clocks derivados diretamente de sinais combinacionais.

Os quatro multiplexadores selecionarão os 15 bits de endereço da VRAM, alternando entre o controlador de vídeo e a CPU.

## 4. Resultados dos novos testes

Criei e executei uma nova bancada de integração em Python.

<box border radius="lg" padding={3} gap={3}>
  <title size="2xl" color="success" tabularNums>1.048.576</title>
  <text color="secondary" size="sm">Combinações de endereços, bancos e estados de boot verificadas</text>
  <divider/>
  <grid columns={2} gap={3}>
    <grid-item>
      <title size="xl" tabularNums>65.536</title>
      <caption>Traduções de endereços físicos</caption>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>105.000</title>
      <caption>Ciclos de vídeo simulados</caption>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>76.800</title>
      <caption>Buscas de pixels</caption>
    </grid-item>
    <grid-item>
      <title size="xl" tabularNums>0</title>
      <caption>Falhas nas verificações executadas</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Acesso a todos os bancos da VRAM","Acesso aos 32 KiB da EEPROM","Preservação da RAM após o boot","Endereçamento dos pixels","Retorno dos contadores ao início do quadro","Separação lógica das janelas de acesso"] as item}
    <row align="center" gap={2}>
      <icon name="check-circle-2" color="success"/>
      <text size="sm">{item}</text>
    </row>
  {/each}
</box>

Esses testes validam o modelo de endereçamento e contagem. Ainda não validam eletricamente o circuito, a execução completa do boot ou a comunicação entre os clocks da CPU e do vídeo.

## 5. Um cuidado importante identificado

Quando a CPU estiver executando um programa diretamente da EEPROM, não poderá simplesmente trocar o banco da própria EEPROM.

Isso poderia fazer com que a próxima instrução fosse buscada em outra região física.

A solução proposta é executar a rotina de troca de bancos a partir da RAM. Não precisamos adicionar componentes para resolver esse problema específico.

Também precisaremos garantir que o registrador RGB332 produza preto durante o apagamento VGA, em vez de simplesmente colocar suas saídas em alta impedância.

## 6. Documentação produzida

- [Relatório técnico — Revisão 7.0](sandbox:/mnt/data/isa1/ISA-1_REV70_INTEGRACAO.md)
- [Simulador de integração em Python](sandbox:/mnt/data/isa1/isa1_rev70.py)
- [Resultados reproduzíveis dos testes](sandbox:/mnt/data/isa1/isa1_rev70_results.json)

## 7. Especificações atuais do ISA-1

<box border radius="lg" padding={3} gap={3}>
  <title size="lg">ISA-1</title>
  <caption>Computador pessoal de 8 bits com lógica discreta</caption>
  <divider/>
  <grid columns={2} gap={3}>
    {#each [{v:"8 bits",n:"CPU própria 74HC"},{v:"16 bits",n:"Endereçamento"},{v:"96 KiB",n:"Memória física total"},{v:"256 cores",n:"RGB332"},{v:"160 × 120",n:"Resolução gráfica"},{v:"59,94 Hz",n:"Atualização VGA projetada"},{v:"USB-C",n:"Alimentação 5 V"},{v:"64 teclas",n:"Teclado próprio"},{v:"ZIF",n:"EEPROM removível"},{v:"1 PCB",n:"Placa principal SMD"}] as p}
      <grid-item>
        <title size="xl">{p.v}</title>
        <caption>{p.n}</caption>
      </grid-item>
    {/each}
  </grid>
</box>

## Próxima revisão — 7.1

Vamos desenvolver o mecanismo de comunicação entre CPU e controlador de vídeo, incluindo solicitação, autorização, espera e confirmação de acesso à VRAM.

Também precisamos validar os tempos de desativação dos buffers, a proteção contra escritas indevidas e a retomada do vídeo após cada transação.

Depois disso, poderemos avançar para a netlist elétrica detalhada.

**Continuamos evoluindo sem reduzir os recursos do computador.** Agora temos uma proposta de arquitetura com 96 KiB de memória física, 256 cores e saída VGA independente da CPU. 😎

## user — bbb21f0f-8092-4f58-906e-1d6091e5d066

Vamos seguir😎

## assistant — d4a24ea8-1585-4dc7-9c8b-30e0c6dadc71

{"content_type": "thoughts", "source_analysis_msg_id": "80c8d2cf-41f3-4d03-b35d-44f90b9bcfca", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou handshake e exclusividade de VRAM, documentando revisão ISA-1"}]}

## assistant — a28d7df6-dd8a-45e0-bbee-97e9f6ed6d73

{"content": "Pensou por 44s", "content_type": "reasoning_recap"}

## assistant — cc164745-11f2-4839-abd3-05b44d85708b

# ISA-1 — Revisão 7.1: comunicação entre CPU e vídeo 😎

Agora vamos desenvolver o mecanismo que permitirá à nossa CPU escrever e ler pixels enquanto o controlador VGA continua gerando a imagem.

O objetivo é garantir três propriedades:

- A CPU e o vídeo nunca disputam eletricamente o barramento da VRAM.
- Nenhum pixel deixa de ser buscado por causa de uma operação da CPU.
- A CPU somente entra em espera quando realmente precisa acessar a VRAM.

Isso preserva a independência do processador e permite desenvolver jogos, interfaces gráficas e aplicações sem precisar controlar manualmente o sincronismo VGA.

## 1. Protocolo de comunicação

Vamos utilizar quatro sinais principais:

| Sinal | Função |
|---|---|
| `VRAM_REQ` | CPU solicita acesso |
| `VRAM_ACK` | Controlador confirma conclusão |
| `CPU_WAIT` | CPU aguarda a conclusão |
| `VRAM_SEL` | Seleciona o proprietário da memória |

A proposta é utilizar um protocolo de handshake com solicitação e confirmação mantidas até que o outro lado as reconheça.

Como a CPU e o vídeo poderão operar em frequências diferentes, precisaremos sincronizar os sinais de solicitação e confirmação utilizando flip-flops.

Não vamos simplesmente interromper o clock da CPU com uma porta lógica: isso poderia gerar pulsos incompletos e corromper o estado dos registradores.

## 2. Máquina de estados da VRAM

Organizei o controlador em cinco estados, incluindo uma etapa específica para devolver a memória ao vídeo.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 320 350" width="100%">
    {#each [{y:5,a:"VIDEO",b:"Leitura contínua dos pixels",c:"#15803d"},{y:76,a:"SELECT",b:"Selecionar endereço da CPU",c:"#2563eb"},{y:147,a:"ACCESS",b:"Executar leitura ou escrita",c:"#2563eb"},{y:218,a:"RELEASE",b:"Desativar sinais de acesso",c:"#64748b"},{y:289,a:"RESTORE",b:"Devolver memória ao vídeo",c:"#64748b"}] as p}
      <rect x="25" y={p.y} width="230" height="49" rx="6" fill={p.c} fillOpacity=".13" stroke={p.c}/>
      <text x="140" y={p.y+19} fontSize="12" fontWeight="bold" fill="currentColor" textAnchor="middle">{p.a}</text>
      <text x="140" y={p.y+35} fontSize="10" fill="currentColor" textAnchor="middle">{p.b}</text>
    {/each}
    {#each [54,125,196,267] as y}
      <path d={`M140 ${y} V${y+19} m-4 -5 l4 5 l4 -5`} fill="none" stroke="currentColor" strokeWidth="1.5"/>
    {/each}
    <path d="M255 313 H291 V29 H255 l6 -4 m-6 4 l6 4" fill="none" stroke="#16a34a" strokeWidth="1.8"/>
    <text x="281" y="175" transform="rotate(-90 281 175)" fontSize="10" textAnchor="middle" fill="currentColor">ACK — operação concluída</text>
  </svg>
</box>

Durante a transação, a CPU deverá manter estáveis o endereço, o banco selecionado, o tipo de operação e os dados de escrita.

O controlador somente autorizará o acesso dentro de uma janela segura do apagamento horizontal.

## 3. Testes executados

Acabei de executar uma nova bancada comportamental em Python, variando a frequência relativa da CPU, a fase dos clocks, o momento da solicitação e o tipo de acesso.

<card gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success" tabularNums>12.800</title>
      <caption>Cenários testados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>2.479.018</title>
      <caption>Ciclos simulados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">200</title>
      <caption>Posições de solicitação por linha VGA</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas verificações</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Nenhuma transação duplicada","Nenhuma solicitação perdida","Nenhuma sobreposição lógica com a busca de pixels","Leitura e escrita mutuamente exclusivas","Confirmação de conclusão recebida pela CPU"] as item}
    <row align="center" gap={2}>
      <icon name="check-circle-2" color="success"/>
      <text size="sm">{item}</text>
    </row>
  {/each}
</card>

O resultado é positivo. Entretanto, essa bancada utiliza clocks discretizados e não simula metastabilidade, atrasos elétricos ou interrupções por reset. Esses pontos continuam pendentes.

## 4. Proteção do barramento

Uma decisão importante desta revisão é manter o barramento de dados da VRAM separado do barramento principal da CPU, conectando-os somente durante uma transação autorizada.

Os componentes candidatos são:

| Componente | Função |
|---|---|
| 2 × 74HC74 | Sincronização de REQ e ACK |
| 74HCT245 | Interface bidirecional de dados |
| 74HCT574 | Registro dos dados de leitura |
| Lógica de controle | Máquina de estados e proteção |

O registrador de leitura permitirá que o vídeo retome o controle da VRAM antes mesmo de a CPU consumir o dado recebido.

Ainda vamos verificar se conseguimos reaproveitar portas e registradores existentes para reduzir a quantidade de CIs.

## 5. Documentação produzida

- [Relatório técnico — Revisão 7.1](sandbox:/mnt/data/isa1/ISA-1_REV71_HANDSHAKE.md)
- [Código da bancada de testes](sandbox:/mnt/data/isa1/isa1_rev71.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev71_results.json)

## 6. Próxima revisão — 7.2

Quero concentrar os próximos testes nas situações mais críticas:

- Solicitações consecutivas de leitura e escrita.
- Reset durante cada fase de uma transação.
- Proteção contra escrita durante queda de alimentação.
- Preservação dos registradores e flags da CPU durante o WAIT.
- Implementação física da máquina de estados utilizando CIs da família 74HC/HCT.
- Otimização da quantidade de componentes sem sacrificar funcionalidades.

## 7. Estado atual do ISA-1

<box border radius="lg" padding={3} gap={3}>
  <title size="xl">ISA-1</title>
  <caption>Computador pessoal de 8 bits</caption>
  <divider/>
  <grid columns={2} gap={3}>
    {#each [{v:"8 bits",n:"CPU própria"},{v:"16 bits",n:"Endereçamento"},{v:"96 KiB",n:"Memória física"},{v:"256 cores",n:"RGB332"},{v:"160 × 120",n:"Resolução gráfica"},{v:"59,94 Hz",n:"Sincronismo VGA"},{v:"5 V",n:"Alimentação USB-C"},{v:"64 teclas",n:"Teclado próprio"},{v:"1 PCB",n:"Placa principal"},{v:"SOIC",n:"Encapsulamento preferencial"}] as p}
      <grid-item>
        <title size="xl">{p.v}</title>
        <caption>{p.n}</caption>
      </grid-item>
    {/each}
  </grid>
  <divider/>
  <caption>Arquitetura em desenvolvimento. Fabricação ainda não liberada.</caption>
</box>

Estamos conseguindo manter a filosofia original do projeto: um computador realmente funcional, com CPU própria, sem microcontroladores escondidos fazendo o trabalho pesado.

E agora com um controlador gráfico dedicado de 256 cores, também construído com lógica discreta. 😎

## user — bbb214a0-9879-402f-a3b4-24caa4f3f727

Vai ficar sensacional! Pode seguir

## assistant — 21ef0385-f65a-4931-999c-7b72a744b9b5

{"content_type": "thoughts", "source_analysis_msg_id": "fac6dd0f-5080-4113-8140-b32ad81c026b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou transações síncronas ISA1 e documentou a revisão"}]}

## assistant — 56182fdc-3885-4ec5-bd26-1c26ef0238b5

{"content": "Pensou por 32s", "content_type": "reasoning_recap"}

## assistant — b6e45a31-e4eb-433d-aa8e-bc815778155d

# ISA-1 — Revisão 7.2: segurança elétrica e integridade da CPU 😎

Agora vamos trabalhar em uma parte menos visível, mas fundamental para a qualidade do ISA-1: garantir que o computador permaneça estável mesmo diante de situações inesperadas.

Não quero que tenhamos uma placa que funcione apenas em condições ideais. Precisamos considerar inicialização, reset, acessos consecutivos à memória, oscilações na alimentação e conflitos de barramento.

Continuamos mantendo a CPU própria, as 256 cores, os 96 KiB de memória física e a alimentação exclusivamente em 5 V.

## 1. Proteção durante o WAIT

Quando a CPU solicitar acesso à VRAM, ela deverá preservar seu estado até receber a confirmação do controlador de vídeo.

| Elemento da CPU | Durante o WAIT |
|---|---|
| PC — contador de programa | Preservado |
| SP — ponteiro da pilha | Preservado |
| Registradores gerais | Preservados |
| Flags | Preservadas |
| Registrador de instrução | Preservado |
| Contador de microinstruções | Preservado |
| Endereço solicitado | Mantido estável |
| Dados de escrita | Mantidos estáveis |
| Clock principal | Continua funcionando |
| Controlador VGA | Continua funcionando |

Em vez de interromper fisicamente o clock, vamos controlar os sinais de habilitação dos registradores e contadores.

Isso também evita que uma instrução seja executada duas vezes enquanto a CPU estiver aguardando a memória.

## 2. Reset e queda de alimentação

Precisamos estabelecer uma regra prioritária: nenhuma solicitação da CPU poderá se sobrepor à proteção da memória.

A autorização de escrita deverá obedecer à seguinte lógica:

\[
WE_{permit}=POWER_{GOOD}\land RUN\land GRANT\land WRITE\land ACCESS
\]

O sinal físico `/WE` da SRAM será ativo em nível baixo.

Se houver um reset ou uma queda de alimentação detectada, o circuito deverá bloquear novas escritas independentemente do estado da máquina de controle.

Existe, porém, uma limitação física: uma escrita interrompida no meio do pulso poderá deixar o byte afetado em estado indefinido. Não podemos garantir sua integridade apenas com essa lógica.

## 3. Nova bancada de testes

Executei um modelo Python com injeção de falhas em diferentes momentos das transações de leitura e escrita.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>168.400</title>
      <caption>Cenários executados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>28.099.352</title>
      <caption>Asserções executadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>108.288</title>
      <caption>Transações concluídas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>60.112</title>
      <caption>Transações abortadas por falhas injetadas</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success" size="lg"/>
    **Nenhuma asserção falhou.**
  </row>
</box>

As 60.112 interrupções foram provocadas intencionalmente pela bancada, não são defeitos espontâneos encontrados no projeto.

O modelo confirmou a exclusividade das janelas de acesso, a ausência de escritas duplicadas dentro de cada transação e o comportamento abstrato de interrupção.

**Limitação:** os testes consideram falhas nas fronteiras dos ciclos. A preservação do estado da CPU é uma condição do modelo, ainda não uma comprovação do funcionamento do circuito real. Também não simulamos metastabilidade ou quedas analógicas de tensão.

## 4. Implementação da máquina de estados

A proposta é utilizar um sequenciador construído com lógica discreta, sem recorrer a microcontroladores ou FPGAs.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 230" width="100%">
    {#each [{x:5,y:5,w:100,h:45,a:"CPU",b:"REQ / WAIT"},{x:120,y:5,w:100,h:45,a:"74HC74",b:"Sincronização"},{x:235,y:5,w:100,h:45,a:"VGA",b:"Blanking"},{x:90,y:82,w:160,h:48,a:"Sequenciador",b:"74HC163 + portas"},{x:5,y:174,w:100,h:45,a:"74HCT245",b:"Dados"},{x:120,y:174,w:100,h:45,a:"VRAM",b:"32 KiB"},{x:235,y:174,w:100,h:45,a:"Proteção",b:"Reset / WE"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={p.x+p.w/2} y={p.y+18} fontSize="11" fontWeight="bold" fill="currentColor" textAnchor="middle">{p.a}</text>
      <text x={p.x+p.w/2} y={p.y+33} fontSize="10" fill="currentColor" textAnchor="middle">{p.b}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.8" fill="none">
      <path d="M105 27 H120 M170 50 V82 M285 50 V65 H230 V82 M170 130 V174 M170 150 H55 V174 M170 150 H285 V174 M105 196 H120 M235 196 H220"/>
    </g>
  </svg>
  <caption>Arquitetura funcional proposta, ainda não equivalente a um esquemático elétrico.</caption>
</box>

| CI candidato | Responsabilidade |
|---|---|
| 74HC74 | Sincronização entre clocks |
| 74HC163 | Sequenciamento das operações |
| 74HCT245 | Isolamento dos barramentos |
| 74HCT574 | Armazenamento do dado lido |
| 74HC00 | Portas NAND de controle |
| 74HC08 | Condições de autorização |
| 74HC32 | Combinação de sinais |
| 74HC04 | Inversão de sinais |

Esses componentes possuem versões SMD compatíveis com nossa proposta de montagem doméstica. A quantidade definitiva dependerá da simplificação das equações lógicas.

## 5. Revisão da janela de acesso à VRAM

Refinei a distribuição dos ciclos horizontais para reservar tempo de proteção antes da retomada do vídeo.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 110" width="100%">
    <rect x="10" y="12" width="256" height="22" rx="2" fill="#16a34a"/>
    <rect x="266" y="12" width="64" height="22" rx="2" fill="#64748b"/>
    <text x="138" y="27" fill="white" textAnchor="middle" fontSize="10">Área visível</text>
    <text x="298" y="27" fill="white" textAnchor="middle" fontSize="9">Blanking</text>
    <path d="M266 36 L10 58 M330 36 V58" stroke="currentColor" strokeOpacity=".3" strokeDasharray="3 3"/>
    {#each Array.from({length:40},(_,i)=>i) as i}
      <rect x={10+i*8} y="60" width="7.2" height="22" rx="1" fill={i===39?"#9333ea":i===0||i>=37?"#d97706":"#2563eb"}/>
    {/each}
    {#each [160,170,180,190,199] as n}
      <text x={14+(n-160)*8} y="97" fontSize="9" textAnchor="middle" fill="currentColor">{n}</text>
    {/each}
  </svg>
  <row align="center">
    <box size="10px" background="#2563eb" radius="sm"/>
    <text size="xs">Janela da CPU</text>
    <box size="10px" background="#d97706" radius="sm"/>
    <text size="xs">Proteção</text>
    <box size="10px" background="#9333ea" radius="sm"/>
    <text size="xs">Prefetch</text>
  </row>
</box>

O último ciclo horizontal permanece reservado para buscar antecipadamente o primeiro pixel da próxima linha.

Essa distribuição ainda precisa passar pela análise dos atrasos máximos dos componentes físicos.

## 6. Documentação produzida

Os três arquivos desta revisão estão disponíveis:

- [Relatório técnico — Revisão 7.2](sandbox:/mnt/data/isa1/ISA-1_REV72_SEGURANCA.md)
- [Código Python da bancada de testes](sandbox:/mnt/data/isa1/isa1_rev72.py)
- [Resultados reproduzíveis em JSON](sandbox:/mnt/data/isa1/isa1_rev72_results.json)

## 7. Estado geral do projeto

| Subsistema | Situação |
|---|---|
| Arquitetura da CPU | Definida |
| ALU e registradores | Validação parcial |
| Pilha e CALL/RET | Modelados |
| Mapa de memória | Proposto |
| EEPROM removível | Mantida |
| VGA RGB332 | Modelo comportamental testado |
| Arbitragem da VRAM | Modelo comportamental testado |
| Proteção contra reset | Modelo preliminar testado |
| Alimentação USB-C 5 V | Dimensionamento pendente |
| Esquemático completo | Pendente |
| PCB | Pendente |
| Monitor e BASIC | Desenvolvimento pendente |

## Próxima revisão — 7.3

Vamos integrar o WAIT ao microcódigo da CPU, testar transações consecutivas, validar o rearme após reset e começar a transformar a máquina de estados em conexões reais entre os CIs.

Também vamos revisar o orçamento de alimentação, agora sem a linha de 12 V.

Continuamos respeitando todos os pilares do ISA-1: CPU própria, lógica discreta, 256 cores, EEPROM removível, uma única PCB principal e montagem doméstica.

**Nada de capar o computador para economizar componentes. Vamos otimizar a implementação, não reduzir suas capacidades.** 😎

## user — bbb2129f-b553-4439-b2f6-10dcc3eb800b

Boa tá ficando resiliente! 
Depois vamos anotar tudo o que fizemos, para fazer uma doc legal

## assistant — 64f8c2b9-0ce4-45c7-aa2c-b53933c1e36c

Com certeza! 😎 E quero que a documentação do ISA-1 seja muito mais do que um simples manual de montagem.

Vamos registrar toda a evolução do projeto, inclusive as decisões que descartamos, os problemas encontrados e como chegamos às soluções.

## Documentação oficial do ISA-1

| Capítulo | Conteúdo |
|---|---|
| 01 — História | Origem do projeto e homenagem à Isabel |
| 02 — Filosofia | Objetivos e princípios de desenvolvimento |
| 03 — Arquitetura | Visão geral do computador |
| 04 — CPU | ALU, registradores, flags e pilha |
| 05 — ISA | Conjunto de instruções, opcodes e microcódigo |
| 06 — Memória | RAM, EEPROM, VRAM e bancos |
| 07 — Vídeo | VGA, RGB332, sincronismo e DAC |
| 08 — Periféricos | Teclado e interfaces |
| 09 — Alimentação | USB-C, proteção e consumo |
| 10 — Resiliência | Reset, WAIT e proteção dos barramentos |
| 11 — Engenharia | Cálculos, decisões e alternativas descartadas |
| 12 — Validação | Simulações, testes, resultados e limitações |
| 13 — Hardware | Esquemáticos, PCB e lista de componentes |
| 14 — Montagem | Soldagem, inspeção e primeira inicialização |
| 15 — Software | Assembly, monitor, BASIC e exemplos |
| 16 — Evolução | Histórico completo das revisões |

Também quero separar claramente quatro níveis de validação:

- **Comportamental:** simulações da lógica.
- **Elétrica:** níveis de tensão, corrente e temporização.
- **Esquemática:** conexões, pinagens e ERC.
- **Física:** medições e testes na placa real.

Assim, não confundiremos uma simulação bem-sucedida com um circuito fisicamente comprovado.

Minha intenção é que a documentação seja suficientemente completa para que outra pessoa consiga estudar, compreender, construir, programar e até expandir o ISA-1.

Vamos consolidar tudo em um manual técnico ilustrado, acompanhado dos arquivos-fonte, esquemáticos e bancadas de testes reproduzíveis. Para isso, precisaremos reunir e conferir os arquivos de todas as revisões, sem presumir que todos estejam disponíveis.

**ISA-1 — Manual de Arquitetura, Engenharia e Programação.**

Praticamente um livro sobre a construção do nosso próprio computador, desde as portas lógicas até a execução de jogos em 256 cores.

Vai ser uma bela homenagem à Isabel. 😎

## user — bbb21172-ba06-428c-b586-511387ae12fa

Boa! Vamos continuar com as revisões

## assistant — 5a9df489-cd2a-4800-baff-a35b0b6b64ac

{"content_type": "thoughts", "source_analysis_msg_id": "6c7a7cb1-79fd-425e-8192-9ca67da6c15c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou protocolo assíncrono e criou relatório da revisão ISA-1 7.3"}]}

## assistant — 41d0c4b1-b6de-4f91-b617-f0404f8f177e

{"content": "Pensou por 28s", "content_type": "reasoning_recap"}

## assistant — e79070c7-636b-424b-8bf8-0f88a15d58a0

# ISA-1 — Revisão 7.3: integração do WAIT e recuperação de falhas 😎

Nesta revisão, vamos aproximar a CPU e o controlador VGA de uma implementação elétrica definitiva.

Identifiquei uma oportunidade de melhorar o protocolo de comunicação: não basta confirmar que uma operação terminou. Precisamos garantir que o controlador esteja preparado para receber a próxima solicitação, especialmente quando executamos várias escritas consecutivas na VRAM.

Isso será fundamental para o desempenho das rotinas gráficas.

## 1. Handshake de quatro fases

Vamos adotar um protocolo com retorno ao estado inicial.

<box border radius="lg" padding={3} gap={3}>
  <svg viewBox="0 0 340 180" width="100%">
    {#each [65,120,185,240] as x}
      <line x1={x} x2={x} y1="20" y2="151" stroke="currentColor" strokeDasharray="3 4" opacity=".25"/>
    {/each}
    <g fill="currentColor" fontSize="10">
      <text x="5" y="47">REQ</text>
      <text x="5" y="87">ACK</text>
      <text x="5" y="127">WAIT*</text>
      <text x="65" y="12" textAnchor="middle">1</text>
      <text x="120" y="12" textAnchor="middle">2</text>
      <text x="185" y="12" textAnchor="middle">3</text>
      <text x="240" y="12" textAnchor="middle">4</text>
    </g>
    <path d="M45 55 H65 V30 H185 V55 H330" stroke="#2563eb" strokeWidth="2.5" fill="none"/>
    <path d="M45 95 H120 V70 H240 V95 H330" stroke="#16a34a" strokeWidth="2.5" fill="none"/>
    <path d="M45 135 H65 V110 H185 V135 H330" stroke="#d97706" strokeWidth="2.5" fill="none"/>
    <text x="270" y="160" fill="currentColor" fontSize="10" textAnchor="middle">Pronto novamente</text>
  </svg>
  <caption>*WAIT ilustrativo, liberado após reconhecimento da confirmação pela CPU. A próxima transação aguarda o rearme.</caption>
</box>

| Fase | Comportamento |
|---|---|
| 1 | CPU mantém endereço e dados estáveis e ativa REQ |
| 2 | Vídeo conclui a operação e ativa ACK |
| 3 | CPU reconhece ACK, conclui a microinstrução e desativa REQ |
| 4 | Vídeo desativa ACK e permite uma nova solicitação |

Esse protocolo evita que uma solicitação mantida por vários ciclos seja interpretada como múltiplas operações de escrita.

## 2. Testes de transações consecutivas

Executei uma nova bancada Python com três escritas consecutivas, variando a relação entre os clocks, suas fases relativas e a posição horizontal do VGA no momento da solicitação.

<box border radius="lg" padding={3} gap={3}>
  <title size="2xl" tabularNums>51.200</title>
  <caption>Cenários executados nesta revisão</caption>
  <row align="center">
    <box background="#16a34a" height="12px" width="13.4765625%" radius="sm"/>
    <box background="#64748b" height="12px" flex={1} radius="sm"/>
  </row>
  <grid columns={2}>
    <grid-item>
      <title size="xl" color="success">6.900</title>
      <caption>Cenários com três escritas concluídas</caption>
    </grid-item>
    <grid-item>
      <title size="xl">44.300</title>
      <caption>Cenários encerrados por reset injetado</caption>
    </grid-item>
    <grid-item>
      <title size="xl">20.700</title>
      <caption>Escritas nos cenários sem reset</caption>
    </grid-item>
    <grid-item>
      <title size="xl" color="success">0</title>
      <caption>Falhas nas asserções executadas</caption>
    </grid-item>
  </grid>
</box>

Os testes confirmaram, dentro do modelo, que as escritas consecutivas não são duplicadas e que a conclusão de uma operação não é confundida com a confirmação da próxima.

Testei seis relações diferentes entre os períodos dos clocks.

**Limitação encontrada:** a bancada encerra a execução quando injeta um reset. Portanto, ainda não comprova o rearme e a retomada das operações após esse reset. Também não substitui a validação do microcódigo real.

## 3. Integração com o microcódigo

Precisamos separar dois acontecimentos: a conclusão da microinstrução e o rearme da interface de vídeo.

Proponho os seguintes sinais internos:

| Sinal | Responsabilidade |
|---|---|
| `CPU_ADVANCE` | Autoriza o avanço da microinstrução |
| `CPU_COMMIT` | Autoriza alterações nos registradores |
| `VRAM_READY` | Interface disponível para nova solicitação |
| `VRAM_PENDING` | Operação em andamento |
| `ACK_SYNC` | Confirmação sincronizada |
| `RESET_SAFE` | Bloqueio prioritário de operações |

Essa separação permitirá que a CPU continue executando instruções que não utilizam a VRAM enquanto a interface termina seu rearme.

Não precisamos desperdiçar ciclos de processamento desnecessariamente.

## 4. Revisão da alimentação

Agora que eliminamos os 12 V, vamos trabalhar com esta arquitetura:

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 240" width="100%">
    {#each [{x:105,y:5,w:130,h:35,a:"USB-C · 5 V"},{x:105,y:60,w:130,h:35,a:"Proteção de entrada"},{x:105,y:115,w:130,h:35,a:"Distribuição 5 V"},{x:5,y:180,w:100,h:45,a:"CPU e memória",b:"Lógica digital"},{x:120,y:180,w:100,h:45,a:"VGA RGB332",b:"Vídeo"},{x:235,y:180,w:100,h:45,a:"Periféricos",b:"Teclado e I/O"}] as p}
      <rect x={p.x} y={p.y} width={p.w} height={p.h} rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={p.x+p.w/2} y={p.y+(p.b?17:22)} textAnchor="middle" fill="currentColor" fontSize="11">{p.a}</text>
      {#if p.b}<text x={p.x+p.w/2} y={p.y+32} textAnchor="middle" fill="currentColor" fontSize="10">{p.b}</text>{/if}
    {/each}
    <path d="M170 40 V60 M170 95 V115 M170 150 V180 M170 165 H55 V180 M170 165 H285 V180" stroke="#0d9488" strokeWidth="2" fill="none"/>
  </svg>
</box>

As decisões propostas para a alimentação são:

- Resistores Rd de 5,1 kΩ independentes em CC1 e CC2 do USB-C.
- Proteção contra sobrecorrente e descargas eletrostáticas.
- Capacitores de desacoplamento de 100 nF próximos de cada CI.
- Plano de terra contínuo na PCB.
- Supervisor de tensão para proteger a inicialização e as escritas.
- Monitor Arzopa alimentado separadamente.

Ainda não vou definir a corrente nominal da fonte. Precisamos consolidar a lista de componentes e verificar a corrente anunciada pelo carregador USB-C.

## 5. Documentação da revisão

Arquivos gerados e conferidos nesta etapa:

- [Relatório técnico — Revisão 7.3](sandbox:/mnt/data/isa1/ISA-1_REV73_WAIT.md)
- [Código Python da bancada de testes](sandbox:/mnt/data/isa1/isa1_rev73.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev73_results.json)

Esses arquivos também servirão como material para nosso futuro manual técnico.

## 6. Próxima revisão — 7.4

Vamos concentrar os esforços nos pontos ainda não comprovados.

| Validação | Situação |
|---|---|
| Handshake de quatro fases | <badge color="success">Testado no modelo</badge> |
| Escritas consecutivas | <badge color="success">Testado no modelo</badge> |
| Leitura da VRAM | Pendente nesta bancada |
| Recuperação após reset | Pendente |
| Integração com microcódigo real | Pendente |
| Temporização elétrica | Parcial |
| Dimensionamento da alimentação | Pendente |
| Liberação da PCB | Bloqueada |

Quero que o ISA-1 seja capaz de se recuperar corretamente de uma interrupção, sem executar operações antigas ou gerar escritas indevidas.

Estamos avançando na direção de um computador não apenas funcional, mas confiável, expansível, reparável e completamente compreensível através dos seus circuitos.

Essa última característica é uma das coisas mais legais do nosso projeto: **poderemos explicar o funcionamento de cada instrução, desde o software até o estado das portas lógicas.** 😎

## user — bbb21aa5-6c04-4ea2-a813-a68b44df54c1

Perfeito! Pode continuar😎

## assistant — e877dd9b-ea6c-4ab2-b3c4-b8d406dd351b

{"content_type": "thoughts", "source_analysis_msg_id": "d92b0e6d-2a01-4de0-b55d-d1314c821649", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validou sincronização CDC e criou relatório de recuperação ISA-1"}]}

## assistant — ec7836e3-7a55-48d3-a18a-b6b55826ac43

{"content": "Pensou por 29s", "content_type": "reasoning_recap"}

## assistant — 4eada2a1-458e-4582-bba7-d672c4361588

# ISA-1 — Revisão 7.4: recuperação após reset e proteção da VRAM 😎

Nesta revisão, vamos corrigir uma limitação dos testes anteriores: até agora, quando ocorria um reset injetado, a simulação era encerrada. Precisamos verificar se o sistema consegue voltar a funcionar corretamente depois da interrupção.

Também vamos testar leituras e escritas intercaladas.

## 1. Estratégia de recuperação

Decidi adotar um reset global para a CPU e o controlador de vídeo, com liberação sincronizada individualmente em cada domínio de clock.

Durante o reset:

- A escrita na VRAM será bloqueada.
- Os buffers de comunicação serão desabilitados.
- As solicitações e confirmações pendentes serão descartadas.
- Os registradores de controle retornarão ao estado inicial.
- A saída RGB deverá permanecer preta.
- A CPU somente poderá iniciar novas transações após a confirmação de que o controlador de vídeo está operacional.

Não vamos apagar automaticamente toda a VRAM. Isso seria desnecessário e aumentaria a complexidade do hardware. O software de inicialização será responsável por limpar a tela.

## 2. Resultados da bancada de recuperação

Executei um novo simulador Python, utilizando cinco períodos de clock da CPU, três períodos de clock do vídeo e diferentes fases relativas entre eles.

Desta vez, após o reset, a simulação continua e executa uma nova sequência de duas escritas e duas leituras intercaladas.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>8.208</title>
      <caption>Cenários executados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>9.529.880</title>
      <caption>Passos temporais simulados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>8.151</title>
      <caption>Cenários com reset injetado</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>5.593</title>
      <caption>Resets durante solicitação pendente</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success" size="lg"/>
    **Nenhuma asserção falhou.**
  </row>
</box>

O modelo confirmou a retomada das transações, a leitura dos valores esperados, a ausência de escritas duplicadas dentro de cada período de funcionamento e a execução dos acessos dentro das janelas reservadas.

Uma escrita realizada antes do reset pode permanecer na memória. Isso é esperado: reset não significa desfazer operações já executadas.

## 3. Sequência segura de inicialização

A partir desses resultados, proponho a seguinte sequência de inicialização do ISA-1:

<box border radius="lg" padding={3}>
  <list connector="solid" marker="number" gap={2}>
    <list-item>**Alimentação USB-C**

      <caption>Estabilização da linha de 5 V.</caption>
    </list-item>
    <list-item>**Supervisor de tensão**

      <caption>Mantém CPU e vídeo em reset enquanto a alimentação não estiver adequada.</caption>
    </list-item>
    <list-item>**Inicialização do vídeo**

      <caption>Contadores VGA, arbitragem e registradores de controle.</caption>
    </list-item>
    <list-item>**VIDEO_READY**

      <caption>Confirmação de disponibilidade do controlador gráfico.</caption>
    </list-item>
    <list-item>**Inicialização da CPU**

      <caption>Execução do código de boot da EEPROM.</caption>
    </list-item>
    <list-item>**Inicialização da VRAM**

      <caption>Software limpa a tela e prepara a interface gráfica.</caption>
    </list-item>
    <list-item>**ISA-1 operacional**

      <caption>Execução normal dos programas.</caption>
    </list-item>
  </list>
</box>

Essa sequência será implementada utilizando lógica discreta e o próprio software de inicialização do ISA-1.

## 4. Regras de segurança consolidadas

| Situação | Comportamento previsto |
|---|---|
| Reset durante leitura | Descartar resultado pendente |
| Reset durante escrita | Bloquear novas escritas |
| Escrita interrompida | Byte afetado potencialmente indefinido |
| Reset durante WAIT | Reset tem prioridade |
| ACK antigo | Descartado |
| Nova solicitação | Somente após rearme |
| VRAM após reset | Conteúdo não garantido |
| Queda de alimentação | Supervisor bloqueia operações |

**Limitações da bancada:** o reset foi modelado como simultâneo e ideal. Os contadores VGA não foram efetivamente reinicializados no simulador, e a sequência de operações é reiniciada, não retomada do ponto interrompido.

Ainda precisamos validar a implementação elétrica, a metastabilidade, os pulsos incompletos de escrita e o microcódigo real da CPU.

## 5. Documentação produzida

Os arquivos desta revisão foram gerados e conferidos:

- [Relatório técnico — Revisão 7.4](sandbox:/mnt/data/isa1/ISA-1_REV74_RECUPERACAO.md)
- [Simulador Python de recuperação](sandbox:/mnt/data/isa1/isa1_rev74.py)
- [Resultados dos testes em JSON](sandbox:/mnt/data/isa1/isa1_rev74_results.json)

Também confirmei que os arquivos de diversas revisões anteriores continuam presentes no diretório do projeto. Isso será muito útil quando consolidarmos nosso manual técnico.

## 6. Próxima revisão — 7.5

Vamos voltar nossa atenção para a CPU e sua unidade de controle.

| Atividade | Prioridade |
|---|---|
| Integrar WAIT às microinstruções | Alta |
| Impedir efeitos colaterais durante WAIT | Alta |
| Validar preservação das flags | Alta |
| Revisar CALL, RET e pilha | Alta |
| Consolidar sinais de habilitação | Alta |
| Otimizar quantidade de CIs | Média |
| Dimensionar alimentação de 5 V | Alta |

Quero começar a fechar os subsistemas, reduzindo progressivamente as pendências técnicas, em vez de apenas acrescentar novas funcionalidades.

Nosso objetivo agora é transformar toda essa arquitetura em um esquemático completo, verificável e efetivamente fabricável.

**Mantendo todos os recursos do ISA-1, sem atalhos e sem capar a CPU.** 😎

## user — bbb21845-20f8-4999-86ed-d1ed0cddcbfd

Pode seguir com o objetivo

## assistant — c4db3137-cbc1-4b85-a9bc-ce74201768a1

{"content_type": "thoughts", "source_analysis_msg_id": "78100877-68f5-4d76-8f1d-f48185adef16", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou arquivos, microoperações e contrato WAIT da ISA-1"}]}

## assistant — e246eba2-aa68-4937-807c-1e1b010f67cf

{"content": "Pensou por 27s", "content_type": "reasoning_recap"}

## assistant — af4d4d1d-14fd-47fa-b05e-439d44af432a

# ISA-1 — Revisão 7.5: unidade de controle e integridade das instruções 😎

Vamos seguir com o objetivo de fechar os subsistemas e transformar o ISA-1 em um computador efetivamente fabricável.

Nesta revisão, a prioridade será a unidade de controle da CPU. Precisamos garantir que a introdução do WAIT não interfira nas instruções, na pilha, nos registradores ou nas flags.

Não vamos acrescentar novas funcionalidades agora. Vamos consolidar aquelas que já definimos.

## 1. Separação dos sinais de controle

Identifiquei uma distinção importante para nossa arquitetura: uma microinstrução pode permanecer ativa durante vários ciclos de clock, mas seus efeitos colaterais devem acontecer apenas uma vez.

| Sinal | Responsabilidade |
|---|---|
| `CPU_ADVANCE` | Avançar o microsequenciador |
| `CPU_COMMIT` | Efetivar alterações de estado |
| `MEM_START` | Iniciar uma operação de memória |
| `MEM_DONE` | Confirmar sua conclusão |
| `CPU_WAIT` | Suspender o avanço da instrução |
| `CPU_RUN` | Autorizar o funcionamento normal |

O clock continuará funcionando normalmente. Os sinais de habilitação determinarão quando cada registrador poderá mudar.

## 2. Revisão das instruções CALL e RET

Reabri a documentação das revisões 3.3 e 5.7 e o simulador da revisão 7.4 para preservar as decisões anteriores.

A convenção de funcionamento da pilha continua sendo a mesma: crescimento descendente, armazenamento do byte alto seguido pelo byte baixo e recuperação na ordem inversa.

<box border radius="lg" padding={3} gap={3}>
  <svg viewBox="0 0 340 180" width="100%">
    {#each [{x:5,t:"Antes do CALL",v:["—","—","—"],p:0},{x:120,t:"Após CALL",v:["—","12","34"],p:2},{x:235,t:"Após RET",v:["—","12","34"],p:0}] as s}
      <text x={s.x+50} y="16" fontSize="11" fontWeight="bold" textAnchor="middle" fill="currentColor">{s.t}</text>
      {#each s.v as v,i}
        <rect x={s.x+32} y={30+i*37} width="66" height="34" rx="3" stroke="#94a3b8" fill={s.p===i?"#2563eb":"#64748b"} fillOpacity={s.p===i?".25":".08"}/>
        <text x={s.x+65} y={51+i*37} fontSize="13" textAnchor="middle" fill="currentColor">{v}</text>
        <text x={s.x+26} y={51+i*37} fontSize="9" textAnchor="end" fill="currentColor">{["7FFF","7FFE","7FFD"][i]}</text>
      {/each}
      <path d={`M${s.x+103} ${47+s.p*37} h-5 l4 -3 m-4 3 l4 3`} stroke="#2563eb" fill="none"/>
      <text x={s.x+50} y="160" textAnchor="middle" fill="currentColor" fontSize="10">SP = {s.p===0?"7FFF":"7FFD"}</text>
    {/each}
  </svg>
  <caption>Exemplo de empilhamento do endereço de retorno 0x1234. Os bytes permanecem fisicamente na RAM após RET, mas deixam de integrar a pilha ativa.</caption>
</box>

Uma melhoria proposta nesta revisão é calcular o próximo endereço da pilha antes da escrita e atualizar o SP somente após a confirmação da operação.

Isso evita decrementar o SP repetidamente durante uma espera. Entretanto, precisaremos verificar se o datapath atual consegue calcular `SP-1` sem modificar o próprio SP, ou se será necessário um microestado adicional.

## 3. Resultados dos testes executados

Criei e executei uma bancada Python específica para verificar o contrato de funcionamento da pilha durante períodos de espera.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>28.672</title>
      <caption>Cenários executados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.118.208</title>
      <caption>Ciclos de espera simulados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>114.688</title>
      <caption>Operações de memória efetivadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Sete endereços de retorno diferentes","Quatro posições iniciais da pilha","Todas as combinações das flags Z e C","Atrasos independentes de 0, 1, 7 e 31 ciclos","Preservação dos registradores A e B","Recuperação do endereço de retorno e do SP"] as item}
    <row align="center" gap={2}>
      <icon name="check-circle-2" color="success"/>
      <text size="sm">{item}</text>
    </row>
  {/each}
</box>

**Limitação:** essa bancada testa o contrato abstrato das quatro operações de memória da pilha. Ainda não executa os opcodes reais, chamadas aninhadas, o salto ao destino do CALL ou o handshake completo da revisão 7.4. A preservação durante WAIT é uma regra implementada no modelo, não uma comprovação elétrica.

## 4. Integração com os componentes físicos

Precisamos respeitar o comportamento individual de cada CI.

| Componente | Ação durante WAIT |
|---|---|
| 74HC163 — PC | Bloquear contagem e carga paralela |
| 74HC377 — registradores | Bloquear habilitação de carga |
| Registrador de flags | Bloquear atualização |
| Microsequenciador | Manter microestado |
| Controlador de memória | Continuar operando |
| Controlador VGA | Continuar operando |
| Supervisor de reset | Manter prioridade absoluta |

Encontrei uma condição importante: não podemos utilizar diretamente o sinal `CPU_COMMIT` para controlar a duração do pulso de escrita `/WE`.

O pulso de escrita precisa de sua própria temporização, enquanto o COMMIT representa a conclusão da operação.

Essa separação será incorporada à unidade de controle.

## 5. Documentação produzida

Os três arquivos abaixo foram efetivamente criados nesta revisão:

- [Relatório técnico — Revisão 7.5](sandbox:/mnt/data/isa1/ISA-1_REV75_CONTROLE.md)
- [Código Python da bancada de testes](sandbox:/mnt/data/isa1/isa1_rev75.py)
- [Resultados reproduzíveis em JSON](sandbox:/mnt/data/isa1/isa1_rev75_results.json)

## 6. Caminho até a fabricação

A partir de agora, proponho organizar as revisões em etapas de fechamento técnico.

<box border radius="lg" padding={3}>
  <list connector="solid" marker="number" gap={3}>
    <list-item>**Unidade de controle — revisão 7.x**

      Consolidar microcódigo, opcodes, WAIT e sinais de habilitação.
    </list-item>
    <list-item>**Integração elétrica — revisão 8.x**

      Pinagem, barramentos, temporização, alimentação e lista de componentes.
    </list-item>
    <list-item>**Esquemático — revisão 9.x**

      Implementação no KiCad, auditoria das conexões e ERC.
    </list-item>
    <list-item>**PCB — revisão 10.x**

      Posicionamento dos componentes, roteamento, planos de alimentação e DRC.
    </list-item>
    <list-item>**Protótipo físico**

      Montagem, medições, testes progressivos e execução dos primeiros programas.
    </list-item>
    <list-item>**ISA-1 versão 1.0**

      Hardware validado, software inicial e manual técnico completo.
    </list-item>
  </list>
</box>

Essa numeração é uma proposta de organização, não um prazo fixo.

## 7. Próxima revisão — 7.6

Vamos reconciliar a tabela de microoperações da revisão 3.3 com a arquitetura atual e começar a transformar as operações simbólicas em sinais reais de controle.

O dimensionamento da alimentação de 5 V continua pendente até consolidarmos o inventário de componentes.

**Nosso objetivo agora é fechar o projeto, não aumentar indefinidamente seu escopo.** Preservaremos todos os recursos já definidos, buscando uma implementação confiável, econômica e possível de montar em casa. 😎

## user — bbb21562-4258-4f1b-9580-fb3a2fc75cee

Pode continuar
E hoje ainda vou ligar o PC pra vc poder acessar o Cli pra testar o circuito

## assistant — 97e2ec87-6037-4d30-a9d4-35381d74ffde

{"content_type": "thoughts", "source_analysis_msg_id": "4b974449-97b1-4a45-8884-619e9eef45b7", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, leu documentos e validou microcódigo ISA-1"}]}

## assistant — 7e073a33-5921-4867-8451-c8d2f40d44c7

{"content": "Pensou por 28s", "content_type": "reasoning_recap"}

## assistant — 028b62d1-f9a9-4992-bed7-9a8f1cc142fb

# ISA-1 — Revisão 7.6: consolidação do microcódigo 😎

Excelente! Quando você ligar o PC, poderemos avançar para uma etapa de validação muito mais completa, utilizando o ambiente local do Codex CLI, desde que ele tenha acesso à pasta do projeto e às ferramentas necessárias.

Enquanto isso, vamos consolidar a unidade de controle.

Quero aproveitar os testes no PC para validar o circuito de verdade, e não apenas repetir simulações comportamentais em Python.

## 1. Ferramentas para validação no PC

| Ferramenta | Finalidade |
|---|---|
| KiCad CLI | Verificação do esquemático e ERC |
| ngspice | Simulação elétrica de circuitos |
| Icarus Verilog | Simulação da lógica digital |
| GTKWave | Inspeção das formas de onda |
| Python | Testes automatizados e regressões |
| Git | Histórico das revisões |

O Verilog será utilizado exclusivamente para simular nosso hardware. A implementação física continuará utilizando os CIs discretos, sem FPGA ou microcontrolador.

## 2. Auditoria das revisões anteriores

Consegui reabrir os arquivos locais das revisões 3.3 e 7.5.

A tabela original contém 19 instruções implementadas no emulador e 101 etapas simbólicas de microoperações. Também existem sete opcodes previstos na especificação anterior que ainda não foram implementados naquele emulador.

Portanto, não devemos congelar a ISA nem fabricar a unidade de controle antes de resolver essa diferença.

Outro ponto importante é que o contrato original permite algumas operações simultâneas que talvez exijam microestados separados no hardware, especialmente durante CALL, RET e acessos à memória.

## 3. Inconsistência encontrada na pilha

Encontrei uma divergência real entre as revisões 3.3 e 7.5.

As duas utilizam uma pilha descendente, mas atualizam o SP em momentos diferentes.

Minha decisão técnica é padronizar a convenção da revisão 7.5:

- PUSH: decrementa o SP antes do armazenamento.
- POP: incrementa o SP após a leitura.
- SP inicial: `0x8000`.
- Primeiro endereço ocupado: `0x7FFF`.

Assim, aproveitamos corretamente a RAM principal de 32 KiB.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 200" width="100%">
    {#each [{x:5,t:"Inicialização",v:["—","—","—"],p:0},{x:120,t:"CALL 1234h*",v:["—","12","34"],p:2},{x:235,t:"Após RET",v:["—","12","34"],p:0}] as s}
      <text x={s.x+52} y="17" fontSize="11" fontWeight="bold" textAnchor="middle" fill="currentColor">{s.t}</text>
      {#each s.v as v,i}
        <rect x={s.x+32} y={30+i*40} width="64" height="36" rx="3" stroke="#94a3b8" fill={s.p===i?"#2563eb":"#64748b"} fillOpacity={s.p===i?".25":".08"}/>
        <text x={s.x+64} y={53+i*40} fontSize="14" textAnchor="middle" fill="currentColor">{v}</text>
        <text x={s.x+27} y={52+i*40} fontSize="9" textAnchor="end" fill="currentColor">{["8000","7FFF","7FFE"][i]}</text>
      {/each}
      <text x={s.x+55} y="169" fontSize="11" textAnchor="middle" fill="currentColor">SP = {s.p===0?"8000":"7FFE"}</text>
    {/each}
  </svg>
  <caption>*Exemplo com endereço de retorno 1234h. O endereço 8000h é apenas a posição inicial do SP, não uma posição utilizada para armazenamento na pilha.</caption>
</box>

## 4. Instruções que precisamos recuperar

Estas instruções estavam previstas na especificação 3.1, mas não foram incluídas na tabela de microoperações 3.3.

| Opcode | Instrução | Função |
|---|---|---|
| `32` | LDX | Carregar registrador X de 16 bits |
| `33` | LDA [X] | Leitura indireta |
| `34` | STA [X] | Escrita indireta |
| `35` | INX | Incrementar X |
| `36` | DEX | Decrementar X |
| `42` | JNZ | Salto condicional |
| `54` | CMP | Comparação |

Essas instruções são particularmente importantes para percorrer arrays, manipular textos, desenhar imagens e implementar o interpretador BASIC.

**Não vamos descartá-las para economizar CIs.** Precisamos incorporá-las ao datapath definitivo.

## 5. Testes efetivamente executados

Criei uma bancada de auditoria e executei os testes no ambiente atual.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success" tabularNums>196.608</title>
      <caption>Testes de empilhamento e desempilhamento</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>65.536</title>
      <caption>Endereços de retorno diferentes</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">15</title>
      <caption>Instruções expandidas estruturalmente</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções executadas</caption>
    </grid-item>
  </grid>
</box>

A bancada verificou todos os valores possíveis de endereço de retorno em três posições iniciais da pilha.

Também expandiu as operações simbólicas de memória em três fases: ISSUE, WAIT e COMMIT.

As quatro instruções relacionadas à pilha ficaram explicitamente pendentes na tabela expandida até consolidarmos seu datapath.

Ainda não é uma simulação do microcódigo executável ou do circuito elétrico.

## 6. Preparação para quando você ligar o PC

Minha proposta é organizar o projeto local desta maneira:

<box border radius="lg" padding={3}>
  <text preserveWhitespace={true}>
    <icon name="folder" color="secondary"/> ISA-1/
    {"\n"}├── hardware/
    {"\n"}│   ├── kicad/
    {"\n"}│   ├── spice/
    {"\n"}│   └── models/
    {"\n"}├── simulation/
    {"\n"}│   ├── verilog/
    {"\n"}│   ├── python/
    {"\n"}│   └── testbenches/
    {"\n"}├── firmware/
    {"\n"}├── microcode/
    {"\n"}├── documentation/
    {"\n"}├── revisions/
    {"\n"}└── tests/
  </text>
</box>

Quando estivermos no CLI, primeiro vamos verificar as ferramentas instaladas e os arquivos disponíveis.

Depois, a prioridade será simular individualmente os componentes e integrar progressivamente os circuitos.

Não encontrei KiCad CLI, ngspice ou Icarus Verilog no PATH do ambiente atual. Por isso, não executei simulações com essas ferramentas nesta revisão.

## 7. Documentação produzida

- [Relatório técnico — Revisão 7.6](sandbox:/mnt/data/isa1/ISA-1_REV76_AUDITORIA.md)
- [Bancada Python de auditoria](sandbox:/mnt/data/isa1/isa1_rev76.py)
- [Tabela intermediária de microoperações e resultados](sandbox:/mnt/data/isa1/isa1_rev76_microcode.json)

## 8. Próxima revisão — 7.7

| Atividade | Prioridade |
|---|---|
| Implementação do registrador X | Alta |
| Endereçamento indireto | Alta |
| Consolidação das 26 instruções previstas | Alta |
| Microcódigo de CALL e RET | Alta |
| Modelo digital dos CIs 74HC | Alta |
| Inventário de componentes | Alta |
| Orçamento de alimentação | Alta |

Quando você ligar o PC, podemos aproveitar para dar um salto importante na engenharia do ISA-1.

Quero chegar ao ponto de conseguirmos visualizar as formas de onda dos barramentos, dos registradores, dos clocks e dos sinais de controle durante a execução de um programa.

**Será como ligar nosso computador pela primeira vez em uma bancada virtual, antes mesmo de soldar o primeiro componente.** 😎

## user — bbb215e5-84eb-4bb5-ac4d-7b7332902ae6

Não vou conseguir ligar o PC agora
Tem algo que você pra fazer por agora? 

## assistant — b4f77869-3a0c-4a57-b6eb-e3a85c40ffd6

{"content_type": "thoughts", "source_analysis_msg_id": "a2c5a043-c48e-4b7c-a049-ac43ebb22902", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, arquivos ISA-1 e regressão da CPU"}]}

## assistant — 2a046e7a-f1c2-4c89-a1b3-f0a85c287029

{"content": "Pensou por 28s", "content_type": "reasoning_recap"}

## assistant — 8726f8b4-2bc2-4f5d-b9b2-db67ec73cb91

Tem bastante coisa que conseguimos fazer por aqui, sem precisar ligar seu PC! 😎

Não precisamos interromper o desenvolvimento do ISA-1. Podemos continuar trabalhando na arquitetura, executar testes em Python e preparar os modelos digitais que posteriormente serão utilizados no ambiente local.

## O que conseguimos adiantar

| Atividade | Podemos fazer agora? |
|---|---|
| Consolidar as 26 instruções da CPU | Sim |
| Desenvolver o microcódigo | Sim |
| Implementar o registrador X | Sim |
| Testar endereçamento indireto | Sim |
| Testar a ALU e as flags | Sim |
| Desenvolver modelos digitais dos 74HC | Sim |
| Preparar arquivos Verilog | Sim |
| Dimensionar a alimentação de 5 V | Parcialmente |
| Consolidar a lista de componentes | Sim |
| Executar ERC no KiCad local | Depende do PC |
| Testar o hardware físico | Depende do protótipo |

Minha prioridade seria continuar com a **revisão 7.7**, trabalhando no registrador X e nas instruções de endereçamento indireto. Elas serão fundamentais para manipular imagens, textos, arrays e implementar o BASIC.

## Uma melhoria que já identifiquei

Reabri os arquivos das revisões 3.1, 4.0 e 7.6 e confirmei que o registrador X de 16 bits estava previsto na arquitetura original, mas seu caminho físico até o registrador de endereços MAR ainda não foi consolidado.

Podemos aproveitar a própria ALU de 8 bits para incrementar e decrementar X em duas etapas, evitando adicionar um circuito aritmético completo de 16 bits exclusivamente para ele.

<box border radius="lg" padding={3} gap={2}>
  <svg viewBox="0 0 340 180" width="100%">
    <rect x="70" y="5" width="100" height="42" rx="5" fill="#2563eb" fillOpacity=".2" stroke="#2563eb"/>
    <rect x="170" y="5" width="100" height="42" rx="5" fill="#16a34a" fillOpacity=".2" stroke="#16a34a"/>
    <g fill="currentColor" fontSize="11" textAnchor="middle">
      <text x="120" y="23">XH</text><text x="120" y="38">8 bits superiores</text>
      <text x="220" y="23">XL</text><text x="220" y="38">8 bits inferiores</text>
    </g>
    <rect x="105" y="76" width="130" height="38" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <text x="170" y="99" textAnchor="middle" fill="currentColor" fontSize="12">Seleção de endereço</text>
    <path d="M120 47 V60 H170 V76 M220 47 V60 H170" fill="none" stroke="#0d9488" strokeWidth="2"/>
    <rect x="105" y="140" width="130" height="34" rx="5" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
    <path d="M170 114 V140" stroke="#0d9488" strokeWidth="2"/>
    <text x="170" y="161" fill="currentColor" textAnchor="middle" fontSize="12">MAR — 16 bits</text>
  </svg>
  <caption>Caminho de endereçamento indireto proposto para o registrador X.</caption>
</box>

Isso permitiria implementar:

| Instrução | Opcode | Função |
|---|---|---|
| `LDX` | `32` | Carregar endereço de 16 bits |
| `LDA [X]` | `33` | Ler memória |
| `STA [X]` | `34` | Escrever na memória |
| `INX` | `35` | Incrementar endereço |
| `DEX` | `36` | Decrementar endereço |

Precisaremos de um carry intermediário separado da flag C arquitetural, caso essas operações devam preservar as flags. Essa convenção ainda precisa ser formalizada.

## Plano de trabalho sem o PC

| Revisão | Objetivo |
|---|---|
| 7.7 | Registrador X e endereçamento indireto |
| 7.8 | Consolidação das 26 instruções |
| 7.9 | Microcódigo executável e testes integrados |
| 8.0 | Modelos digitais dos componentes |
| 8.1 | Inventário de CIs e consumo elétrico |
| 8.2 | Alimentação USB-C e proteções |
| 8.3 | Consolidação das conexões elétricas |

Também confirmei que os arquivos das revisões anteriores continuam disponíveis no ambiente atual. Podemos aproveitá-los tanto no desenvolvimento quanto na futura documentação oficial.

Não encontrei Icarus Verilog, ngspice ou KiCad CLI instalados neste ambiente. Nesta etapa, fiz a inspeção dos arquivos anteriores, mas ainda não executei novos testes do registrador X.

**Temos bastante trabalho útil para adiantar antes de precisar do seu PC.** Quando você conseguir ligá-lo, já poderemos ter modelos e bancadas de testes preparados para a validação local. 😎

## user — bbb21686-2a83-4052-b813-4826338ddee5

Boa então faz assim
Pode ir interando até terminar todas as validações que não precisem do PC 😎
Assim quando chegar no PC, já vamos ter uma versão executável legal do nosso circuito

## assistant — 2c169403-1cad-49cc-9fbe-4258d0fd9773

{"content_type": "thoughts", "source_analysis_msg_id": "43949be0-5bb5-40f9-996e-8007e8f54776", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Revisou contratos, arquivos e modelo simbólico, empacotando integração ISA-1"}]}

## assistant — 19128ec0-6fb4-457a-a3a4-574fc904593f

{"content": "Pensou por 38s", "content_type": "reasoning_recap"}

## assistant — 144243b9-b57b-4a15-939e-f89c43214e48

Combinado! 😎 Você está me dando autonomia para avançar pelas revisões, corrigir inconsistências, executar testes e tomar decisões técnicas sem precisar da sua aprovação a cada etapa.

Vou manter os requisitos originais do ISA-1 e priorizar o fechamento dos subsistemas, em vez de acrescentar funcionalidades indefinidamente.

A meta é chegar ao PC com um pacote de simulação executável, código-fonte, testes automatizados, documentação e uma lista objetiva das validações elétricas restantes.

## Primeiro lote de revisões — 7.7 a 7.9

Já avancei nesta sessão e reuni as três revisões em um modelo executável integrado.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" color="success">131.072</title>
      <caption>Testes de incremento e decremento de X</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">393.216</title>
      <caption>Casos de operações da ALU</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">26</title>
      <caption>Opcodes implementados e exercitados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">105.000</title>
      <caption>Ciclos de um quadro VGA</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success"/>
    Todos os testes executados neste lote passaram.
  </row>
</box>

Também executei um programa integrado com quatro configurações de espera diferentes, envolvendo inicialização, troca de bancos, escrita e leitura da VRAM, endereçamento indireto e chamadas aninhadas de subrotinas.

## Decisões técnicas consolidadas

| Elemento | Decisão |
|---|---|
| Registrador X | 16 bits |
| INX e DEX | Preservam as flags |
| ALU | Operações de 8 bits |
| Pilha | Descendente, SP inicial `8000h` |
| Boot | Salto para região permanente da EEPROM antes de liberar a RAM |
| WAIT | ISSUE, WAIT e COMMIT |
| VGA | RGB332, 256 cores |
| Alimentação | Exclusivamente 5 V |

Adotei também uma janela mais conservadora de cinco ciclos para os acessos à VRAM. Isso reduz o limite teórico de transferência para aproximadamente 220 KB/s, mas oferece mais espaço temporal para as etapas de proteção.

## Pacote executável atual

<card gap={2}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      **ISA-1 — Integração 7.7–7.9**
      <caption>Modelo Python, testes, resultados e documentação</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_integracao_77_79.zip)
</card>

O pacote não exige bibliotecas externas. Basta executar `python test.py`.

Ainda é um modelo comportamental: os ciclos de espera são abstratos e a CPU ainda não está conectada ao árbitro VGA real. Não é uma simulação elétrica ou uma netlist completa.

## Roteiro de fechamento autônomo

| Revisão | Objetivo | Situação |
|---|---|---|
| 7.7 | Registrador X | Modelo testado |
| 7.8 | 26 instruções | Modelo implementado |
| 7.9 | Integração da CPU | Parcialmente testada |
| 8.0 | Modelos digitais dos CIs | Pendente |
| 8.1 | Inventário de componentes | Pendente |
| 8.2 | Alimentação e proteções | Pendente |
| 8.3 | Conexões elétricas | Pendente |
| 8.4 | Integração CPU/VGA | Pendente |
| 8.5 | Teclado e EEPROM ZIF | Pendente |
| 8.6 | Auditoria geral | Pendente |
| 8.7 | Pacote para validação no PC | Pendente |

Vou preservar também os relatórios anteriores para a futura documentação oficial do ISA-1.

Uma limitação operacional: não consigo continuar executando revisões em segundo plano depois que esta resposta terminar. Mas, nas próximas interações, podemos avançar em lotes maiores, sem precisar discutir ou aprovar cada revisão individualmente.

**Você não precisa ligar o PC agora. Ainda temos bastante engenharia que podemos desenvolver e testar por aqui.** 😎

## user — bbb2100c-a08e-40ad-97b1-ff98e7faaf34

Pode seguir então por aqui, tá sensacional! 
Logo logo eu ligo o PC

## assistant — d585ce57-f0da-4543-9086-bfe3b96330a9

{"content_type": "thoughts", "source_analysis_msg_id": "4ee1c3fd-9d9c-43f9-9375-c2680782ab9c", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificou ferramentas, leu documentação ISA-1 e validou modelos digitais"}]}

## assistant — cf3deb0a-bb87-4c09-978b-a991cfb8187f

{"content": "Pensou por 25s", "content_type": "reasoning_recap"}

## assistant — 928063f9-5b5a-4299-9df2-52b7940880c1

Vamos avançar agora para as revisões 8.x, concentrando os esforços na aproximação entre o modelo da CPU e os componentes físicos do ISA-1.

## Revisão 8.0 — Biblioteca de componentes digitais

A ideia é criar modelos reutilizáveis dos CIs, respeitando seus sinais de habilitação, reset, bordas de clock e saídas de alta impedância.

Isso permitirá substituir progressivamente as operações abstratas do simulador por circuitos digitais equivalentes aos componentes que serão soldados na PCB.

### Resultados dos testes executados

<box border radius="lg" padding={3} gap={3}>
  <title size="2xl" color="success" tabularNums>765.480</title>
  <caption>Casos, ciclos e verificações executados nesta revisão</caption>
  <divider/>
  <table>
    <table-row>
      <table-cell>74HC163 — contador</table-cell>
      <table-cell align="end">4.096</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
    <table-row>
      <table-cell>PC de 16 bits</table-cell>
      <table-cell align="end">262.144</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
    <table-row>
      <table-cell>74HC157 — multiplexador</table-cell>
      <table-cell align="end">1.024</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
    <table-row>
      <table-cell>74HC377 — registrador</table-cell>
      <table-cell align="end">131.072</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
    <table-row>
      <table-cell>74HC245 — transceptor</table-cell>
      <table-cell align="end">262.144</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
    <table-row>
      <table-cell>Contadores VGA</table-cell>
      <table-cell align="end">105.000</table-cell>
      <table-cell><icon name="check-circle-2" color="success"/></table-cell>
    </table-row>
  </table>
  **Nenhuma asserção falhou.**
</box>

## Correção importante no circuito VGA

Ao revisar a arquitetura dos contadores, identifiquei uma condição que poderia comprometer a última linha do quadro VGA.

O 74HC163 possui reset síncrono com prioridade sobre a habilitação de contagem.

Portanto, não basta detectar que o contador vertical chegou à linha 524. Precisamos também confirmar que o contador horizontal terminou essa linha.

<svg viewBox="0 0 340 185" width="100%">
  <g stroke="#94a3b8" fill="#64748b" fillOpacity=".09">
    <rect x="8" y="8" width="140" height="46" rx="5"/>
    <rect x="192" y="8" width="140" height="46" rx="5"/>
    <rect x="104" y="130" width="132" height="46" rx="5"/>
  </g>
  <g fill="currentColor" textAnchor="middle" fontSize="11">
    <text x="78" y="27">Contador horizontal</text>
    <text x="78" y="43">H = 199</text>
    <text x="262" y="27">Contador vertical</text>
    <text x="262" y="43">V = 524</text>
    <text x="170" y="149">Reset síncrono</text>
    <text x="170" y="165">Contador vertical</text>
  </g>
  <g stroke="#0d9488" strokeWidth="2" fill="none">
    <path d="M78 54 V80 H145 M262 54 V98 H145"/>
    <path d="M145 70 H170 A20 20 0 0 1 170 110 H145 Z" fill="#0d9488" fillOpacity=".12"/>
    <circle cx="194" cy="90" r="4"/>
    <path d="M198 90 H220 V119 H170 V130"/>
  </g>
  <text x="168" y="94" fill="currentColor" fontSize="10" textAnchor="middle">NAND</text>
</svg>

A equação corrigida é:

`V_CLR_N = NOT (H_TERMINAL AND V_TERMINAL)`

Implementei essa correção no modelo e executei a contagem completa de um quadro VGA.

| Parâmetro | Resultado |
|---|---:|
| Grupos horizontais por linha | 200 |
| Linhas por quadro | 525 |
| Ciclos por quadro | 105.000 |
| Grupos visíveis | 76.800 |
| Resolução lógica | 160 × 120 |
| Frequência nominal | 59,94 Hz |
| Cores RGB332 | 256 |

A correção preserva nossa resolução, quantidade de cores e organização da VRAM.

## Situação geral do ISA-1

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"Arquitetura e ISA",s:"Modelo comportamental",c:"#16a34a"},{n:"CPU e registradores",s:"Testes digitais parciais",c:"#16a34a"},{n:"Controlador VGA",s:"Contadores validados no modelo",c:"#16a34a"},{n:"Integração dos circuitos",s:"Em desenvolvimento",c:"#d97706"},{n:"Alimentação e proteções",s:"Dimensionamento pendente",c:"#d97706"},{n:"Teclado e EEPROM ZIF",s:"Integração pendente",c:"#d97706"},{n:"Esquemático definitivo",s:"Pendente",c:"#94a3b8"},{n:"PCB e fabricação",s:"Pendente",c:"#94a3b8"}] as item}
    <row align="center">
      <box size="10px" radius="full" background={item.c}/>
      <box flex={1} gap=0>
        **{item.n}**
        <caption>{item.s}</caption>
      </box>
    </row>
  {/each}
</box>

## Arquivos produzidos

[Baixar ISA-1 — Revisão 8.0 (.zip)](sandbox:/mnt/data/ISA-1_rev80.zip)

O pacote contém os modelos digitais, testes automatizados, resultados em JSON e documentação técnica. Pode ser executado com Python, sem dependências externas.

**Limitações atuais:** os modelos ainda são ideais, sem atrasos de propagação, metastabilidade ou características elétricas. Os testes verificam os contratos lógicos implementados, não o comportamento do silício real. A integração completa entre CPU e VGA também continua pendente.

## Próximas etapas

Vou priorizar o inventário de componentes, a redução de CIs redundantes, o consumo elétrico, a alimentação USB-C e a integração dos barramentos.

Quando você ligar o PC, quero que aproveitemos o ambiente local principalmente para as tarefas que realmente exigem ferramentas especializadas.

Por enquanto, podemos continuar evoluindo o ISA-1 por aqui, mantendo todas as revisões documentadas para nosso futuro manual técnico.

😎

## user — bbb21388-17a7-4ec0-a40a-ffd63cabea71

Pode ir seguindo e até avançar várias etapas

## assistant — 8896dbd0-8308-432f-ac5b-ea3347fc2d59

{"content_type": "thoughts", "source_analysis_msg_id": "33474a32-cae1-4a73-8812-12d4cd02c460", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Construída máquina ISA com vídeo, teclado e arquivos comparados"}]}

## assistant — 154865d9-0aea-4084-8af2-65a7760c719f

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 6c94ff73-d34f-4e6e-bb50-1b0f9cde192b

# ISA-1 — Integração das revisões 8.1 a 8.5

Vamos trabalhar em um lote maior desta vez, priorizando a integração dos subsistemas.

O objetivo continua sendo uma CPU própria de 8 bits, construída com lógica discreta, alimentação de 5 V, vídeo VGA RGB332, teclado de 64 teclas e EEPROM removível.

Nesta etapa, vou tratar especialmente os conflitos de barramento, a arbitragem da VRAM, a decodificação de memória e a interface do teclado. São pontos que conseguimos testar logicamente antes de fechar o esquemático.

## 1. Resultados efetivamente executados

Integrei o modelo da CPU das revisões 7.x com a biblioteca de componentes digitais da revisão 8.0.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.048.576</title>
      <caption>Casos de decodificação de memória</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.600</title>
      <caption>Transações na VRAM</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>105.000</title>
      <caption>Ciclos de varredura VGA</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>256</title>
      <caption>Verificações de leitura do teclado</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success" size="lg"/>
    **Nenhuma falha nas asserções executadas.**
  </row>
</box>

Também executei um programa utilizando instruções reais da nossa ISA, escrevendo e lendo a VRAM através do registrador X, com o controlador VGA integrado ao modelo.

## 2. Revisão 8.1 — Inventário de componentes

Comecei a consolidar os componentes físicos já definidos.

| Componente | Quantidade parcial | Função |
|---|---:|---|
| 74HC163 | 4 | Program Counter |
| 74HC157 | 4 | Seleção de entrada do PC |
| 74HC377 | 4 | Registradores EA e RET |
| 74HC163 | 5 | Contadores VGA |
| 74HC157 | 4 | Seleção de endereço da VRAM |
| SRAM 32 KiB | 2 | RAM e VRAM |
| AT28C256 | 1 | EEPROM removível |
| Resistores DAC | 8 | Saída RGB332 |

São 24 CIs e oito resistores neste inventário parcial.

Ainda faltam os componentes da ALU, registradores adicionais, unidade de controle, arbitragem, teclado e alimentação. Portanto, essa ainda não é uma lista para compra.

## 3. Revisão 8.2 — Alimentação

Mantive nossa arquitetura exclusivamente em 5 V, sem necessidade de conversores para 12 V.

<box border radius="lg" padding={2}>
  <svg viewBox="0 0 340 260" width="100%">
    {#each [{x:105,y:5,w:130,h:35,t:"USB-C · 5 V"},{x:105,y:55,w:130,h:35,t:"Proteção de entrada"},{x:105,y:105,w:130,h:35,t:"Barramento de 5 V"},{x:5,y:175,w:100,h:40,t:"CPU e RAM"},{x:120,y:175,w:100,h:40,t:"VGA e VRAM"},{x:235,y:175,w:100,h:40,t:"EEPROM e I/O"}] as r}
      <rect x={r.x} y={r.y} width={r.w} height={r.h} rx="5" fill="#64748b" fillOpacity=".1" stroke="#94a3b8"/>
      <text x={r.x+r.w/2} y={r.y+r.h/2+4} fill="currentColor" textAnchor="middle" fontSize="11">{r.t}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M170 40 V55 M170 90 V105 M170 140 V175 M55 175 V155 H285 V175"/>
    </g>
    <text x="170" y="238" fill="currentColor" fontSize="11" textAnchor="middle">Desacoplamento distribuído e GND comum</text>
    <text x="170" y="253" fill="currentColor" fontSize="10" textAnchor="middle">Supervisor de tensão controla o reset</text>
  </svg>
</box>

A corrente total ainda não pode ser determinada com segurança. Precisamos finalizar a quantidade de CIs e considerar seu consumo dinâmico nas respectivas frequências de operação.

## 4. Revisão 8.3 — Mapa de memória

Executei testes cobrindo todos os 65.536 endereços possíveis, combinados com os estados do boot e os bancos de memória.

<box border radius="lg" padding={3} gap={2}>
  {#each [{a:"0000–7FFF",n:"RAM principal",s:"32 KiB",h:104,c:"#2563eb"},{a:"8000–9FFF",n:"Janela VRAM",s:"8 KiB × 4 bancos",h:48,c:"#16a34a"},{a:"A000–BFFF",n:"Periféricos",s:"8 KiB de endereçamento",h:48,c:"#d97706"},{a:"C000–FFFF",n:"Janela EEPROM",s:"16 KiB × 2 bancos",h:65,c:"#9333ea"}] as m}
    <row align="center">
      <box width="94px">
        <text size="xs" tabularNums>{m.a}</text>
      </box>
      <box flex={1} height={`${m.h}px`} background={m.c+"20"} radius="sm" justify="center" padding={2}>
        **{m.n}**
        <caption>{m.s}</caption>
      </box>
    </row>
  {/each}
  <caption>Mapa normal de funcionamento. Durante o boot, a EEPROM sobrepõe temporariamente os primeiros 16 KiB da RAM.</caption>
</box>

Também testei a detecção de conflito entre dois dispositivos dirigindo simultaneamente o barramento, inclusive quando ambos apresentam o mesmo valor.

O modelo rejeitou corretamente essa condição. Ainda precisamos implementar essa exclusividade com os sinais físicos de habilitação.

## 5. Revisão 8.4 — Integração CPU e VGA

Esta é uma das evoluções mais importantes deste lote.

O modelo agora permite que uma instrução da CPU solicite acesso à VRAM e aguarde uma janela disponível durante a varredura horizontal.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 155" width="100%">
    <text x="10" y="15" fontSize="11" fill="currentColor">Linha VGA — 200 grupos de clock</text>
    <rect x="10" y="25" width="256" height="35" rx="3" fill="#2563eb" fillOpacity=".7"/>
    <rect x="266" y="25" width="64" height="35" rx="3" fill="#16a34a" fillOpacity=".7"/>
    <text x="138" y="46" textAnchor="middle" fill="white" fontSize="11">160 grupos visíveis</text>
    <text x="298" y="46" textAnchor="middle" fill="white" fontSize="10">Blanking</text>
    <path d="M266 63 L10 87 M330 63 V87" stroke="currentColor" strokeOpacity=".4" strokeDasharray="3 3"/>
    {#each [{t:"G",w:8,c:"#94a3b8"},{t:"1",w:40,c:"#16a34a"},{t:"2",w:40,c:"#16a34a"},{t:"3",w:40,c:"#16a34a"},{t:"4",w:40,c:"#16a34a"},{t:"5",w:40,c:"#16a34a"},{t:"6",w:40,c:"#16a34a"},{t:"7",w:40,c:"#16a34a"},{t:"G",w:32,c:"#94a3b8"}] as p,i}
      <rect x={10+(i===0?0:i===8?288:8+(i-1)*40)} y="90" width={p.w-1} height="29" rx="2" fill={p.c} fillOpacity=".65"/>
      <text x={10+(i===0?4:i===8?304:28+(i-1)*40)} y="108" fontSize="10" textAnchor="middle" fill="currentColor">{p.t}</text>
    {/each}
    <text x="170" y="140" textAnchor="middle" fill="currentColor" fontSize="11">Até 7 transações de 5 ciclos por linha</text>
  </svg>
  <caption>Distribuição teórica das janelas de acesso. G representa os intervalos de proteção.</caption>
</box>

| Característica | Valor |
|---|---:|
| Resolução lógica | 160 × 120 |
| Cores | 256 |
| Memória por imagem | 19.200 bytes |
| Clock de vídeo | 6,29375 MHz |
| Janela por transação | 794,44 ns |
| Transferência teórica máxima | 220.281 bytes/s |
| Imagens completas por segundo | 11,47 |

Esses valores representam o limite das janelas disponíveis, não a velocidade real da CPU. O handshake físico e as instruções reduzirão a taxa efetiva.

## 6. Revisão 8.5 — Teclado de 64 teclas

Mantive a ideia original de quatro matrizes de 4 × 4, organizadas eletricamente como uma matriz de 4 × 16.

{@body const [activeRow,setActiveRow]=DIL.useState(0)}
{@body const [keys,setKeys]=DIL.useState([0,1,16])}
{@body const connected=(()=>{let rows=new Set([activeRow]),cols=new Set();for(let i=0;i<5;i++){keys.forEach(k=>{if(rows.has(Math.floor(k/16)))cols.add(k%16)});keys.forEach(k=>{if(cols.has(k%16))rows.add(Math.floor(k/16))})}return cols})()}
<card gap={3}>
  **Simulador interativo do teclado**

  <caption>Toque nas teclas para pressionar ou soltar e selecione a linha que a CPU está lendo.</caption>
  <svg viewBox="0 0 340 112" width="100%">
    {#each Array.from({length:4},(_,i)=>i) as r}
      <text x="2" y={25+r*23} fill={r===activeRow?"#16a34a":"currentColor"} fontSize="9">L{r}</text>
      {#each Array.from({length:16},(_,i)=>i) as c}
        <rect x={20+c*20} y={12+r*23} width="17" height="18" rx="2" fill={keys.includes(r*16+c)?"#2563eb":r===activeRow&&connected.has(c)?"#f59e0b":"#94a3b8"} fillOpacity={keys.includes(r*16+c)||r===activeRow&&connected.has(c)?".9":".15"} stroke="#94a3b8" strokeWidth=".5"/>
      {/each}
    {/each}
  </svg>
  {#each Array.from({length:4},(_,i)=>i) as r}
    <row gap={1} align="center">
      <caption>L{r}</caption>
      {#each Array.from({length:16},(_,i)=>i) as c}
        <pressable flex={1} minWidth={0} height="23px" radius="sm" background={keys.includes(r*16+c)?"#2563eb":r===activeRow&&connected.has(c)?"#f59e0b":"surface-tertiary"} onClick={()=>setKeys(old=>old.includes(r*16+c)?old.filter(k=>k!==r*16+c):[...old,r*16+c])}>
          <text size="xs" textAlign="center" color={keys.includes(r*16+c)?"#ffffff":"default"}>{c.toString(16).toUpperCase()}</text>
        </pressable>
      {/each}
    </row>
  {/each}
  <segmented-control options={[{label:"Linha 0",value:"0"},{label:"Linha 1",value:"1"},{label:"Linha 2",value:"2"},{label:"Linha 3",value:"3"}]} value={String(activeRow)} onChange={v=>setActiveRow(Number(v))}/>
  <row>
    <box flex={1} gap=0>
      <caption>Registrador de leitura</caption>
      <title size="xl" tabularNums>0x{(65535-Array.from(connected).reduce((s,c)=>s+2**c,0)).toString(16).toUpperCase().padStart(4,"0")}</title>
    </box>
    <button size="sm" variant="outline" onClick={()=>setKeys([])}>Soltar todas</button>
  </row>
  {#if Array.from(connected).some(c=>!keys.includes(activeRow*16+c))}
    <text color="warning"><icon name="alert-triangle" size="sm" inline={true}/> Ghosting detectado: uma tecla não pressionada está sendo interpretada como ativa.</text>
  {/if}
  <caption>Azul: tecla pressionada. Amarelo: tecla fantasma.</caption>
</card>

### Problema encontrado: ghosting

A bancada demonstrou que determinadas combinações de três teclas podem produzir uma quarta tecla fantasma.

Minha recomendação é utilizar um diodo por tecla na PCB do teclado. Continuaremos com um teclado totalmente passivo, sem microcontrolador, mas teremos uma leitura simultânea mais confiável.

Essa solução ainda precisa ser incorporada ao modelo e testada.

## 7. Pacote executável atualizado

<card gap={2}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      **ISA-1 — Integração 8.1 a 8.5**
      <caption>CPU, componentes digitais, VGA, memória, teclado e testes automatizados.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev81_85.zip)
</card>

O pacote foi criado e os testes foram executados. Não necessita de bibliotecas externas.

## 8. Situação do projeto

| Subsistema | Situação |
|---|---|
| ISA com 26 instruções | Modelo executável |
| ALU e registradores | Testes comportamentais |
| PC de 16 bits | Modelo digital testado |
| Mapa de memória | Testado |
| VGA RGB332 | Modelo integrado parcial |
| Arbitragem VRAM | Testada em modelo simplificado |
| Teclado | Modelo testado, correção pendente |
| EEPROM removível | Programação pendente |
| Alimentação | Dimensionamento pendente |
| Esquemático | Pendente |
| PCB | Pendente |

**Limitações desta revisão:** o simulador ainda não é preciso ciclo a ciclo, não integra os dois clocks independentes, não simula atrasos elétricos e não testa a programação da EEPROM. As revisões 8.1 a 8.5 avançaram, mas não estão integralmente encerradas.

Na próxima etapa, podemos trabalhar na correção do teclado, na programação protegida da EEPROM, na integração do handshake assíncrono e na geração dos modelos Verilog.

Quero que, quando você ligar o PC, já tenhamos uma base suficientemente organizada para começar a construir e validar o esquemático, sem precisar refazer toda a arquitetura.

Estamos avançando sem sacrificar os recursos do nosso ISA-1. 😎

## user — bbb2177e-d337-423f-8d5b-c9064ae186fe

Boa pode ir seguindo até conseguir testar tudo😎

## assistant — 19899d7d-9baf-4eb8-8d7a-4cd9421e04b4

{"content_type": "thoughts", "source_analysis_msg_id": "b3af36a9-0c26-475a-bedd-4f22c6c6af66", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificados arquivos, validados componentes e empacotados testes complementares ISA"}]}

## assistant — ea71da78-fa00-4647-8a21-8766f83382b0

{"content": "Pensou por 32s", "content_type": "reasoning_recap"}

## assistant — c3a94a78-ea0f-4a72-9262-17ee6c52945a

# ISA-1 — Revisões 8.6 a 8.8 😎

Vamos avançar em três pontos que ainda precisam de validação: teclado sem ghosting, integridade dos arquivos salvos na EEPROM e comunicação entre a CPU e o vídeo.

Confirmei que os pacotes anteriores continuam disponíveis. Também verifiquei novamente as ferramentas do ambiente: ainda não temos KiCad CLI, ngspice ou Icarus Verilog instalados aqui.

Isso não impede os testes comportamentais, mas significa que ainda não podemos declarar o circuito eletricamente validado.

## 1. Resultados dos novos testes

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>174.980</title>
      <caption>Casos de leitura do teclado</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>4.095</title>
      <caption>Pontos de interrupção de salvamento</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.914</title>
      <caption>Cenários de comunicação assíncrona</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>2.857.403</title>
      <caption>Passos temporais simulados</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success" size="lg"/>
    **Nenhuma asserção falhou.**
  </row>
</box>

Também executei novamente os testes da revisão 8.5. Todos passaram.

## 2. Revisão 8.6 — Teclado corrigido

Adotei a solução de um diodo por tecla para evitar ghosting, mantendo o teclado completamente passivo.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 250" width="100%">
    {#each [105,185,265] as x,i}
      <path d={`M${x} 42 V52 l-5 4 10 6 -10 6 10 6 -5 4 V235`} fill="none" stroke="#0d9488" strokeWidth="1.5"/>
      <text x={x} y="28" fontSize="11" fill="currentColor" textAnchor="middle">C{i}</text>
      <text x={x+10} y="62" fontSize="9" fill="currentColor">R</text>
    {/each}
    <path d="M80 42 H290" stroke="#ef4444" strokeWidth="2"/>
    <text x="60" y="45" fontSize="11" fill="#ef4444">+5V</text>
    {#each [145,225] as y,r}
      <path d={`M35 ${y} H305`} stroke="#64748b" strokeWidth="2"/>
      <text x="10" y={y+4} fontSize="11" fill="currentColor">L{r}</text>
      {#each [105,185,265] as x,c}
        <g stroke="#0d9488" strokeWidth="1.5" fill="none">
          <circle cx={x} cy={y-59} r="2.5" fill="#0d9488"/>
          <path d={`M${x} ${y-59} H${x+28} V${y-49} l-8 13 M${x+28} ${y-31} V${y-24}`}/>
          <circle cx={x+28} cy={y-31} r="2"/>
          <path d={`M${x+21} ${y-24} H${x+35} L${x+28} ${y-12} Z`} fill="#0d9488"/>
          <path d={`M${x+20} ${y-12} H${x+36} M${x+28} ${y-12} V${y}`}/>
          <circle cx={x+28} cy={y} r="2.5" fill="#0d9488"/>
        </g>
      {/each}
    {/each}
  </svg>
  <caption>Trecho representativo da matriz. Cada tecla possui seu próprio diodo, com ânodo voltado para a coluna e cátodo para a linha.</caption>
</box>

| Característica | Especificação |
|---|---|
| Teclas | 64 |
| Matriz | 4 × 16 |
| Diodos | 64 |
| Resistores pull-up | 16 |
| Microcontroladores | Nenhum |
| Comunicação | Paralela |
| Ghosting | Eliminado no modelo ideal |

Testei exaustivamente todas as combinações de até três teclas pressionadas, incluindo a leitura das quatro linhas.

Ainda precisamos validar a queda de tensão dos diodos, os níveis lógicos e o debounce.

## 3. Revisão 8.7 — Sistema de salvamento resiliente

Quero que a EEPROM removível do ISA-1 funcione de maneira semelhante aos cartuchos de videogames antigos, mas com um sistema de salvamento mais resistente a interrupções.

Mantive os dois slots de 1 KiB que definimos anteriormente.

<box border radius="lg" padding={3} gap={2}>
  <caption>Organização da EEPROM — 32 KiB</caption>
  <row align="center">
    <text size="xs" width="90px">0000–003F</text>
    <box background="#64748b20" radius="sm" padding={2} flex={1}>Cabeçalho · 64 bytes</box>
  </row>
  <row align="center">
    <text size="xs" width="90px">0040–77FF</text>
    <box background="#2563eb20" radius="sm" padding={3} flex={1} height="90px" justify="center">Programas e recursos</box>
  </row>
  <row align="center">
    <text size="xs" width="90px">7800–7BFF</text>
    <box background="#16a34a20" radius="sm" padding={2} flex={1}>SAVE A · 1.024 bytes</box>
  </row>
  <row align="center">
    <text size="xs" width="90px">7C00–7FFF</text>
    <box background="#d9770620" radius="sm" padding={2} flex={1}>SAVE B · 1.024 bytes</box>
  </row>
</box>

Cada slot terá a seguinte estrutura:

| Campo | Tamanho |
|---|---:|
| Marcador de validade | 1 byte |
| Número de geração | 4 bytes |
| Tamanho dos dados | 2 bytes |
| Dados do usuário | Até 1.013 bytes |
| CRC32 | 4 bytes |

### Simulação de interrupção durante salvamento

{@body const [stage,setStage]=DIL.useState("2")}
<card gap={3}>
  <caption>Selecione o momento em que a alimentação é interrompida.</caption>
  <radio-group direction="col" value={stage} onChange={setStage}>
    <radio value="0">Antes de iniciar o salvamento</radio>
    <radio value="1">Após invalidar o slot B</radio>
    <radio value="2">Durante a gravação dos dados</radio>
    <radio value="3">Após gravar o CRC32</radio>
    <radio value="4">Após confirmar o novo salvamento</radio>
  </radio-group>
  <grid columns={2}>
    <grid-item>
      <box border radius="md" padding={3}>
        **SAVE A**
        <icon name="check-circle-2" color="success" size="2xl"/>
        <caption>Geração 42</caption>
        Dados anteriores válidos
      </box>
    </grid-item>
    <grid-item>
      <box border radius="md" padding={3}>
        **SAVE B**
        <icon name={stage==="4"||stage==="0"?"check-circle-2":"alert-circle"} color={stage==="4"||stage==="0"?"success":"warning"} size="2xl"/>
        <caption>Geração {stage==="0"?41:43}</caption>
        {["Salvamento antigo","Invalidado","Dados incompletos","Aguardando confirmação","Novo salvamento válido"][Number(stage)]}
      </box>
    </grid-item>
  </grid>
  <divider/>
  <caption>Resultado após reinicialização</caption>
  <title size="lg" color="success">Recuperar SAVE {stage==="4"?"B":"A"}</title>
</card>

Os 4.095 testes de interrupção passaram nas fronteiras entre escritas completas de bytes.

**Importante:** isso ainda não garante proteção contra uma queda de tensão durante o pulso físico de programação da EEPROM. Essa condição deverá ser testada posteriormente.

## 4. Revisão 8.8 — Comunicação assíncrona CPU/VGA

Agora temos uma bancada separada que utiliza clocks independentes para CPU e vídeo.

<svg viewBox="0 0 340 190" width="100%">
  {#each [{n:"CLK CPU",y:25,p:"M75 35 V15 H95 V35 H115 V15 H135 V35 H155 V15 H175 V35 H195 V15 H215 V35 H235 V15 H255 V35 H275 V15 H295 V35 H315"},{n:"CLK VGA",y:60,p:"M75 70 V50 H87 V70 H99 V50 H111 V70 H123 V50 H135 V70 H147 V50 H159 V70 H171 V50 H183 V70 H195 V50 H207 V70 H219 V50 H231 V70 H243 V50 H255 V70 H267 V50 H279 V70 H291 V50 H303 V70 H315"},{n:"REQ",y:95,p:"M75 105 H115 V85 H255 V105 H315"},{n:"ACK",y:130,p:"M75 140 H195 V120 H295 V140 H315"},{n:"WAIT",y:165,p:"M75 175 H115 V155 H255 V175 H315"}] as s,i}
    <text x="5" y={s.y+4} fill="currentColor" fontSize="11">{s.n}</text>
    <path d={s.p} fill="none" stroke={["#2563eb","#9333ea","#0d9488","#16a34a","#d97706"][i]} strokeWidth="2"/>
  {/each}
  {#each [115,195,255,295] as x}
    <path d={`M${x} 78 V183`} stroke="#94a3b8" strokeDasharray="3 4" strokeOpacity=".5"/>
  {/each}
</svg>
<caption>Diagrama conceitual do handshake. Não representa uma captura elétrica real.</caption>

Foram testados cinco períodos de clock da CPU, três períodos do controlador de vídeo e diferentes fases relativas.

O modelo executou escritas e leituras alternadas, verificando os valores recuperados e o respeito às janelas de acesso à VRAM.

Ainda falta conectar esse handshake diretamente ao microsequenciador da CPU. Os sincronizadores também são ideais: não simulam metastabilidade.

## 5. Estado geral das validações

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"ALU e flags",v:"Testes comportamentais",c:"#16a34a"},{n:"26 instruções",v:"Modelo executável",c:"#16a34a"},{n:"Registradores e pilha",v:"Testes parciais",c:"#16a34a"},{n:"Decodificação de memória",v:"Testada",c:"#16a34a"},{n:"Contadores VGA",v:"Testados",c:"#16a34a"},{n:"Teclado sem ghosting",v:"Modelo ideal testado",c:"#16a34a"},{n:"Sistema de salvamento",v:"Modelo testado",c:"#16a34a"},{n:"Handshake assíncrono",v:"Modelo isolado testado",c:"#16a34a"},{n:"Microcódigo físico",v:"Pendente",c:"#d97706"},{n:"Programação da EEPROM",v:"Pendente",c:"#d97706"},{n:"Alimentação e consumo",v:"Pendente",c:"#d97706"},{n:"Esquemático e PCB",v:"Pendente",c:"#94a3b8"}] as item}
    <row align="center">
      <box size="9px" radius="full" background={item.c}/>
      <box flex={1} gap=0>
        **{item.n}**
        <caption>{item.v}</caption>
      </box>
    </row>
  {/each}
</box>

## 6. Pacote atualizado

<card gap={2}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      **ISA-1 — Revisões 8.6 a 8.8**
      <caption>Código Python, testes, documentação e resultados reproduzíveis.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev86_88.zip)
</card>

## 7. Próximas etapas

Vamos concentrar os próximos esforços em:

- Microcódigo convertido em sinais físicos de controle.
- Integração completa dos clocks independentes.
- Programação protegida da AT28C256.
- Modelos Verilog e bancadas de teste.
- Lista completa de componentes.
- Auditoria de conexões, pinagem e alimentação.
- Preparação de um programa de diagnóstico do próprio ISA-1.

Esse último item será especialmente interessante: quero que nosso computador tenha um programa de autodiagnóstico capaz de verificar RAM, VRAM, registradores, ALU, pilha, teclado e vídeo durante a inicialização.

Assim, além das ferramentas externas de simulação, teremos o próprio ISA-1 ajudando a diagnosticar seu hardware quando construirmos o primeiro protótipo. 😎

## user — bbb216b2-afb8-4508-b71e-714ab88d61b3

{"asset_pointer": "sediment://file_000000005ea8820eb2f007dbbe799dfe", "content_type": "image_asset_pointer", "fovea": null, "height": 1536, "metadata": {"asset_pointer_link": null, "container_pixel_height": null, "container_pixel_width": null, "dalle": null, "emu_omit_glimpse_image": null, "emu_patches_override": null, "generation": null, "gizmo": null, "is_no_auth_placeholder": null, "lpe_delta_encoding_channel": null, "lpe_keep_patch_ijhw": null, "sanitized": true, "segmentation": null, "watermarked_asset_pointer": null}, "mime_type": "image/jpeg", "size_bytes": 96915, "width": 1024}
Sobre o teclado, a gente vai usar aqueles de membrana, já pronto
Não dá pra por diodo 

## assistant — 92fd0318-f279-45c5-a6ee-a1e9403b12e0

Verdade! Você tem razão. Vamos utilizar quatro teclados de membrana 4 × 4 já fabricados, exatamente como o da imagem.

Eu havia considerado incorretamente a possibilidade de instalar diodos individualmente nas teclas. Como os contatos estão selados dentro da membrana, essa solução não é viável.

## ISA-1 — Revisão 8.6.1: correção do teclado

Vamos manter a configuração original:

<box border radius="lg" padding={3} gap={3}>
  <svg viewBox="0 0 340 150" width="100%">
    {#each [0,1,2,3] as m}
      <rect x={m*85+3} y="5" width="79" height="109" rx="6" fill="#20252b" stroke="#64748b"/>
      {#each Array.from({length:16},(_,i)=>i) as k}
        <rect x={m*85+9+k%4*17} y={13+Math.floor(k/4)*23} width="15" height="19" rx="2" fill={k%4===3?"#b83d3d":"#287bb2"} stroke="#94a3b8" strokeWidth=".7"/>
        <text x={m*85+16.5+k%4*17} y={26+Math.floor(k/4)*23} fontSize="10" fill="white" textAnchor="middle">{["1","2","3","A","4","5","6","B","7","8","9","C","*","0","#","D"][k]}</text>
      {/each}
      <rect x={m*85+30} y="114" width="25" height="17" fill="#94a3b8" fillOpacity=".6"/>
      <text x={m*85+42} y="145" fill="currentColor" fontSize="10" textAnchor="middle">Módulo {m+1}</text>
    {/each}
  </svg>
  <caption>Quatro módulos comerciais de membrana, totalizando 64 teclas.</caption>
</box>

## Como resolveremos o ghosting?

Em vez de eliminar fisicamente o ghosting, podemos detectar combinações ambíguas por software e impedir que teclas fantasmas sejam interpretadas como comandos.

Também podemos aproveitar o fato de termos quatro membranas independentes.

Minha recomendação é manter as quatro linhas compartilhadas e as 16 colunas independentes, selecionando uma linha por vez com saída de dreno aberto. As demais linhas permanecerão em alta impedância, evitando conflitos elétricos.

| Componente | Quantidade proposta |
|---|---:|
| Teclado de membrana 4 × 4 | 4 |
| 74HC07 — buffer de dreno aberto | 1 |
| 74HC138 — decodificador | 1 |
| 74HC244 — buffer de leitura | 2 |
| Resistores pull-up de 10 kΩ | 16 |
| Diodos individuais | **0** |
| Microcontroladores | **0** |

Essa lista ainda é preliminar.

## Tratamento pelo software

O driver de teclado do ISA-1 ficará responsável por:

- Varredura das quatro linhas.
- Debounce das teclas.
- Detecção de pressionamento e soltura.
- Repetição automática ao manter uma tecla pressionada.
- Detecção e rejeição de combinações ambíguas.
- Tratamento de SHIFT, CTRL e demais teclas especiais.

A limitação é que determinadas combinações simultâneas não poderão ser identificadas com certeza. Nenhum algoritmo consegue distinguir perfeitamente todas as teclas reais das fantasmas nessa matriz sem diodos.

Para digitação de textos, programação em BASIC e jogos simples, isso é administrável.

**Vou considerar os teclados de membrana comerciais, sem modificações internas, como requisito definitivo do ISA-1.**

Precisaremos substituir os testes de teclado da revisão 8.6 por testes de detecção de ghosting, em vez de sua eliminação física. Ainda não executei essa nova bancada.

Além de respeitar os componentes que você pretende utilizar, eliminamos 64 diodos e evitamos fabricar uma PCB específica para os contatos do teclado. 😎

## user — bbb216c6-a156-40fa-bcdb-6faf8c90d2a0

Como não vai ser um PC pra digitação frenética, não vamos ter problemas😎
Pode seguir

## assistant — 302bdc4c-1d4d-4760-ad71-3ebb5fffe5a0

{"content_type": "thoughts", "source_analysis_msg_id": "ba953ed1-c591-4cd6-92b6-07894bc2ba7b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Atualizei a validação e documentação do ISA-1 após testes de teclado"}]}

## assistant — d8e5e459-aa00-4ac8-8fa1-985403c040b3

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — f69e0f13-67ae-4125-81d9-e28167736937

Exatamente! 😎 Para a proposta do ISA-1, não precisamos de um teclado com capacidade de reconhecer dezenas de teclas simultaneamente.

Vamos preservar os quatro módulos de membrana comerciais, sem modificações, e tratar combinações ambíguas pelo software.

Também manteremos a possibilidade de utilizar SHIFT junto com outra tecla, desde que a combinação não seja ambígua.

## Revisão 8.6.2 — Validação do teclado definitivo

Vou adotar três regras: linhas inativas em alta impedância, rejeição de combinações ambíguas e leitura estável antes de reconhecer um novo pressionamento.

### Resultados dos testes

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>43.745</title>
      <caption>Combinações exaustivas de até três teclas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>10.000</title>
      <caption>Combinações aleatórias de até 64 teclas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>2.880</title>
      <caption>Combinações ambíguas detectadas nos testes exaustivos</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
</box>

Todas as combinações de uma ou duas teclas foram reconhecidas corretamente no modelo.

Também implementei um debounce que exige três varreduras consecutivas idênticas antes de registrar uma alteração.

Nenhuma tecla fantasma foi aceita como novo pressionamento nos cenários testados.

## Revisão 8.9 — Regressão dos subsistemas

Além da correção do teclado, executei novamente as bancadas anteriores para verificar se não introduzimos regressões.

| Teste | Casos executados | Resultado |
|---|---:|---|
| Decodificação de memória | 1.048.576 | <icon name="check-circle-2" color="success"/> |
| Transações VRAM | 1.600 | <icon name="check-circle-2" color="success"/> |
| Varredura VGA | 105.000 | <icon name="check-circle-2" color="success"/> |
| Interrupções de salvamento | 4.095 | <icon name="check-circle-2" color="success"/> |
| Comunicação assíncrona | 1.914 | <icon name="check-circle-2" color="success"/> |
| Novo modelo do teclado | 53.745 | <icon name="check-circle-2" color="success"/> |
| Sequência de debounce | 1 | <icon name="check-circle-2" color="success"/> |

Todos os testes executados passaram.

## Especificações consolidadas do ISA-1

<box border radius="lg" padding={3} gap={3}>
  <title size="xl">ISA-1</title>
  <caption>Computador de arquitetura própria · Revisão 8.9</caption>
  <divider/>
  <grid columns={2} gap={4}>
    <grid-item>
      <caption>Processador</caption>
      **8 bits · Lógica discreta**
    </grid-item>
    <grid-item>
      <caption>Endereçamento</caption>
      **16 bits**
    </grid-item>
    <grid-item>
      <caption>Instruções</caption>
      **26 opcodes**
    </grid-item>
    <grid-item>
      <caption>RAM principal</caption>
      **32 KiB**
    </grid-item>
    <grid-item>
      <caption>Memória de vídeo</caption>
      **32 KiB**
    </grid-item>
    <grid-item>
      <caption>EEPROM removível</caption>
      **32 KiB · ZIF**
    </grid-item>
    <grid-item>
      <caption>Resolução lógica</caption>
      **160 × 120**
    </grid-item>
    <grid-item>
      <caption>Saída de vídeo</caption>
      **VGA · 59,94 Hz**
    </grid-item>
    <grid-item>
      <caption>Paleta</caption>
      **RGB332 · 256 cores**
    </grid-item>
    <grid-item>
      <caption>Teclado</caption>
      **64 teclas de membrana**
    </grid-item>
    <grid-item>
      <caption>Alimentação</caption>
      **USB-C · 5 V**
    </grid-item>
    <grid-item>
      <caption>Microcontroladores</caption>
      **Nenhum**
    </grid-item>
  </grid>
</box>

## Pacote executável atualizado

[Baixar ISA-1 — Revisão 8.9 (.zip)](sandbox:/mnt/data/ISA-1_rev89.zip)

O pacote inclui os códigos anteriores, a correção do teclado, os testes atualizados, os resultados e a documentação. Substituí a bancada que considerava diodos por uma compatível com suas membranas comerciais.

**Limitações:** o driver de teclado ainda precisa ser convertido em código nativo do ISA-1. O modelo considera contatos estáveis durante cada varredura, e uma combinação ambígua pode atrasar o reconhecimento da soltura de uma tecla. As validações elétricas continuam pendentes.

## Próxima fase — Revisões 9.x

Quero concentrar os esforços restantes nestes pontos:

| Revisão | Objetivo |
|---|---|
| 9.0 | Microcódigo e sinais físicos de controle |
| 9.1 | Modelos Verilog dos componentes |
| 9.2 | Integração dos clocks da CPU e VGA |
| 9.3 | Programação protegida da EEPROM |
| 9.4 | Programa nativo de autodiagnóstico |
| 9.5 | Inventário completo de componentes |
| 9.6 | Dimensionamento elétrico |
| 9.7 | Netlist e auditoria de conexões |
| 9.8 | Pacote de validação para o PC |

Estamos chegando à etapa mais importante: transformar nossa arquitetura lógica em conexões físicas entre os CIs.

A intenção é chegar ao PC com o máximo possível de engenharia adiantada, sem depender dele para decisões que conseguimos resolver por aqui. 😎

## user — bbb21e55-0ee1-4220-85e7-2ae469d3ba70

Ihuuuu pode seguir então, pode fazer as análises 

## assistant — 1f45cd88-fc0b-4396-b537-0247d22c3fda

{"content_type": "thoughts", "source_analysis_msg_id": "94c0b612-39cd-4972-9aca-a341bdb2457b", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Verificada implementação ISA e empacotada revisão com testes multirritmo"}]}

## assistant — 0ad891b9-8573-4986-a11c-33632b39457b

{"content": "Pensou por 36s", "content_type": "reasoning_recap"}

## assistant — f04e6cc4-2581-4fb8-95f4-cc0d3c530dfe

# ISA-1 — Revisão 9.0: auditoria da integração

Reabri os códigos da revisão 8.9 e encontrei três pontos importantes que precisamos resolver antes de avançar para o esquemático:

- O handshake assíncrono foi testado separadamente, mas ainda não controla diretamente a execução das instruções da CPU.
- A EEPROM é somente leitura no modelo integrado, embora o sistema de salvamento já tenha sua própria bancada.
- As microoperações ainda são representadas por funções Python, não por palavras binárias de controle.

Os testes anteriores continuam úteis, mas precisamos fechar essas lacunas. A prioridade agora é aumentar a fidelidade da simulação, não simplesmente aumentar a quantidade de testes.

## 1. Integração efetiva da CPU com o vídeo

Implementei uma nova versão do simulador que conecta a execução dos opcodes ao handshake REQ/ACK da VRAM, utilizando clocks independentes.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 245" width="100%">
    {#each [{x:10,y:10,w:140,h:48,t:"CPU ISA-1",s:"Clock independente"},{x:190,y:10,w:140,h:48,t:"Controlador VGA",s:"6,29375 MHz nominal"},{x:10,y:90,w:140,h:44,t:"Microoperações",s:"ISSUE / WAIT / COMMIT"},{x:190,y:90,w:140,h:44,t:"Árbitro de memória",s:"Janelas de blanking"},{x:10,y:180,w:140,h:48,t:"RAM principal",s:"32 KiB"},{x:190,y:180,w:140,h:48,t:"VRAM",s:"32 KiB"}] as r}
      <rect x={r.x} y={r.y} width={r.w} height={r.h} rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={r.x+r.w/2} y={r.y+19} fill="currentColor" fontSize="12" fontWeight="bold" textAnchor="middle">{r.t}</text>
      <text x={r.x+r.w/2} y={r.y+34} fill="currentColor" fontSize="10" textAnchor="middle">{r.s}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M80 58 V90 M260 58 V90 M80 134 V180 M260 134 V180"/>
      <path d="M150 100 H190 l-6 -4 m6 4 l-6 4"/>
      <path d="M190 125 H150 l6 -4 m-6 4 l6 4"/>
    </g>
    <text x="170" y="95" fontSize="9" textAnchor="middle" fill="currentColor">REQ</text>
    <text x="170" y="140" fontSize="9" textAnchor="middle" fill="currentColor">ACK</text>
  </svg>
  <caption>Arquitetura lógica da integração implementada nesta revisão.</caption>
</box>

A CPU aguarda a conclusão do acesso à VRAM enquanto o controlador VGA continua executando sua varredura.

O endereço e os dados da solicitação permanecem armazenados durante a transação.

## 2. Resultados dos novos testes

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>396</title>
      <caption>Execuções completas do programa de teste</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>531.634</title>
      <caption>Passos temporais simulados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.584</title>
      <caption>Transações assíncronas na VRAM</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  <caption>Cinco períodos de clock da CPU, três do vídeo, diferentes fases relativas e seis posições horizontais iniciais.</caption>
</box>

O programa de teste utiliza instruções da nossa própria ISA, incluindo LDX, LDA, STA, INX, DEX, CALL, RET e HLT.

Verifiquei os valores finais dos registradores A, X, PC e SP, o conteúdo da VRAM e a quantidade de escritas realizadas.

## 3. Regressão geral

Também executei novamente as bancadas anteriores.

| Subsistema | Casos executados | Resultado |
|---|---:|---|
| Decodificação de memória | 1.048.576 | <icon name="check-circle-2" color="success"/> |
| Arbitragem VRAM anterior | 1.600 | <icon name="check-circle-2" color="success"/> |
| Varredura VGA | 105.000 | <icon name="check-circle-2" color="success"/> |
| Teclado de membrana | 53.745 | <icon name="check-circle-2" color="success"/> |
| Salvamento EEPROM | 4.095 | <icon name="check-circle-2" color="success"/> |
| Handshake isolado | 1.914 | <icon name="check-circle-2" color="success"/> |
| Nova integração CPU/VGA | 396 | <icon name="check-circle-2" color="success"/> |

Todos os testes executados passaram.

## 4. Análise de maturidade do projeto

Agora temos uma visão mais precisa do que está funcionando e do que ainda precisa ser desenvolvido.

| Subsistema | Situação atual |
|---|---|
| Arquitetura da CPU | Definida |
| Conjunto de 26 instruções | Modelo executável |
| ALU | Modelo testado |
| Pilha e subrotinas | Modelo testado |
| Endereçamento de 16 bits | Modelo testado |
| VGA RGB332 | Modelo testado |
| CPU/VGA assíncronos | Integração parcial testada |
| Teclado sem diodos | Modelo testado |
| Salvamento resiliente | Modelo isolado testado |
| Gravador físico da EEPROM | Pendente |
| Microcódigo binário | Pendente |
| Temporização elétrica | Pendente |
| Alimentação | Pendente |
| Esquemático | Pendente |
| PCB | Pendente |

Não vou atribuir uma porcentagem arbitrária de conclusão ao projeto. A quantidade de testes aprovados não representa diretamente a maturidade do hardware.

## 5. Pacote atualizado

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      <title size="lg">ISA-1 — Revisão 9.0</title>
      <caption>Simulador integrado, bancadas de testes, resultados JSON e documentação técnica.</caption>
    </box>
  </row>
  [Baixar pacote executável (.zip)](sandbox:/mnt/data/ISA-1_rev90.zip)
</card>

O pacote foi criado e os testes foram efetivamente executados.

**Limitações:** o modelo ainda não representa todas as operações nas bordas físicas do clock, não simula metastabilidade, não testa reset durante a nova integração e não valida eletricamente o pipeline de pixels. Também não encontrei as ferramentas de simulação HDL e elétrica instaladas neste ambiente.

## 6. Próximas análises

Minha prioridade para as próximas revisões será:

- Transformar microoperações em palavras binárias de controle.
- Definir a implementação física do microsequenciador.
- Integrar o reset ao novo simulador.
- Implementar o controlador de gravação da EEPROM.
- Desenvolver o montador Assembly do ISA-1.
- Criar o programa nativo de autodiagnóstico.
- Consolidar o inventário de componentes e conexões.
- Preparar os modelos Verilog para validação no PC.

O montador Assembly será particularmente importante. Com ele, poderemos começar a escrever programas para nosso próprio processador, sem precisar montar manualmente os bytes de cada instrução.

Imagine o momento em que executarmos o primeiro programa escrito em Assembly do ISA-1, em uma CPU projetada por nós, exibindo **ISA-1** na tela VGA.

É para esse momento que estamos trabalhando. 😎

## user — bbb216a0-eff5-454b-88c0-72cc7762394d

Booooa, temos uma lista legal de propriedades
Pode verificar todas na ordem

## assistant — 3d5392f2-a556-4c33-baa8-4cede73b65e1

{"content_type": "thoughts", "source_analysis_msg_id": "46a91486-16bc-463f-9fb4-5fbc4fda9916", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou o conteúdo ZIP e as ferramentas de código HDL"}]}

## assistant — 16a52bb2-d575-45b5-8bd7-e0587b8d2bdb

{"content_type": "thoughts", "source_analysis_msg_id": "127474ee-cbf6-48a9-8958-9e768e2fcf03", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Pesquisou 5 sites"}]}

## assistant — c5c4720a-6531-407b-a178-d9d02487e4fb

{"content_type": "thoughts", "source_analysis_msg_id": "0b26daaa-7d02-413e-98f3-0be099d7d185", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Executou testes, leu contrato e auditou defeitos reproduzíveis da ISA-1"}]}

## assistant — a685ea72-dabd-4a02-bd3b-a159d845729f

{"content": "Pensou por 35s", "content_type": "reasoning_recap"}

## assistant — 8cb72cad-eb00-4d4c-bc79-71ff75dee6c6

## Revisão 9.1 — Microcódigo e sinais de controle

A primeira constatação é que o modelo atual implementa as instruções através de funções Python. Isso não é suficiente para determinar quais portas lógicas e registradores serão necessários.

Precisamos transformar cada instrução em uma sequência explícita de operações elementares, incluindo a seleção da fonte, do destino e a condição de avanço.

Também identifiquei uma vulnerabilidade na revisão 9.0: o controlador assíncrono escreve diretamente na VRAM sem verificar `power_good`. Essa proteção existe no modelo anterior, mas não foi preservada na nova integração.

Vou classificar isso como uma regressão de segurança, e não como uma funcionalidade nova.

## 2. Microsequenciador

Precisamos separar três fases fundamentais para cada operação de memória.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 135" width="100%">
    {#each [{x:5,t:"ISSUE",s:"Solicitar"},{x:120,t:"WAIT",s:"Aguardar"},{x:235,t:"COMMIT",s:"Efetivar"}] as a}
      <rect x={a.x} y="15" width="100" height="55" rx="5" fill="#2563eb" fillOpacity=".12" stroke="#64748b"/>
      <text x={a.x+50} y="36" fill="currentColor" fontSize="12" fontWeight="bold" textAnchor="middle">{a.t}</text>
      <text x={a.x+50} y="53" fill="currentColor" fontSize="11" textAnchor="middle">{a.s}</text>
    {/each}
    <path d="M105 42 H120 M115 38 L120 42 L115 46 M220 42 H235 M230 38 L235 42 L230 46 M195 70 V96 H145 V70 L141 76 M145 70 L149 76" fill="none" stroke="#0d9488" strokeWidth="2"/>
    <text x="170" y="113" fontSize="10" fill="currentColor" textAnchor="middle">Permanece enquanto MEM_DONE = 0</text>
  </svg>
</box>

Durante WAIT, a CPU não poderá modificar PC, SP, X, A, B ou as flags por efeito da microinstrução pendente.

Esse será o contrato para o microsequenciador físico. Sua implementação binária ainda está pendente.

## 3. Reset e proteção contra falhas

Criei uma bancada adicional para reproduzir cinco condições problemáticas.

| Condição investigada | Resultado |
|---|---|
| Escrita na VRAM sem POWER_GOOD | <text color="danger">Falha confirmada</text> |
| Escrita na RAM sem POWER_GOOD | <text color="danger">Falha confirmada</text> |
| REQ/ACK permanecem ativos após reset | <text color="danger">Falha confirmada</text> |
| EEPROM não permite gravação | <text color="warning">Recurso pendente</text> |
| CPU pode interpretar cabeçalho como instrução | <text color="danger">Falha confirmada</text> |

Todas essas condições foram efetivamente reproduzidas.

É importante encontrarmos esses problemas agora. Eles passaram despercebidos nas bancadas anteriores porque os testes não cobriam essas situações específicas.

## 4. Programação da EEPROM

Consultei novamente a documentação técnica oficial da Microchip para a AT28C256.

O componente oferece proteção de escrita por software, programação por páginas de até 64 bytes e mecanismos de verificação da conclusão da gravação. <Cite refs={["turn603287search13","turn603287search15"]}/>

Para habilitar uma gravação protegida, precisaremos da seguinte sequência de endereços físicos:

| Endereço | Dado |
|---|---|
| `5555h` | `AAh` |
| `2AAAh` | `55h` |
| `5555h` | `A0h` |
| Endereço desejado | Byte a gravar |

Depois, será necessário aguardar a conclusão da programação.

Minha proposta é executar a rotina de gravação a partir da RAM principal. Assim, a CPU não dependerá da leitura de instruções da EEPROM enquanto ela estiver ocupada.

Ainda precisamos implementar e testar esse controlador.

## 5. Montador Assembly

Conferi novamente o contrato original da revisão 3.1. Os 26 opcodes permanecem definidos.

Um programa do nosso computador poderá ser escrito desta maneira:

```asm
LDX #8000h
LDA #0E0h
STA [X]
INX
LDA #01Ch
STA [X]
INX
LDA #003h
STA [X]
HALT
```

Esse exemplo escreve três pixels nas cores vermelha, verde e azul na VRAM, considerando o banco zero selecionado e a área de RAM disponível para execução.

<svg viewBox="0 0 340 95" width="100%">
  <rect x="10" y="5" width="320" height="80" rx="5" fill="#151515" stroke="#64748b"/>
  <rect x="20" y="15" width="20" height="20" fill="#ff0000"/>
  <rect x="40" y="15" width="20" height="20" fill="#00ff00"/>
  <rect x="60" y="15" width="20" height="20" fill="#0000ff"/>
</svg>
<caption>Representação ampliada do resultado esperado, não uma captura da simulação.</caption>

Outro problema encontrado: reservamos os primeiros 64 bytes da EEPROM para o cabeçalho, mas o PC inicia no endereço zero.

Proponho reservar os três primeiros bytes do cabeçalho para uma instrução JMP que direcione a CPU ao código de inicialização. Isso evita adicionar circuitos exclusivamente para selecionar outro endereço inicial.

O montador propriamente dito ainda não foi desenvolvido nesta revisão.

## 6. Programa de autodiagnóstico

Defini os testes que o firmware deverá executar:

| Teste | Verificação |
|---|---|
| RAM | Padrões `00`, `FF`, `55`, `AA` |
| VRAM | Escrita e leitura dos quatro bancos |
| ALU | Operações aritméticas e lógicas |
| Flags | Zero e carry |
| Registrador X | Incremento e decremento |
| Pilha | PUSH, POP, CALL e RET |
| VGA | Barras coloridas e padrões geométricos |
| Teclado | Identificação das 64 teclas |
| EEPROM | Cabeçalho, leitura e integridade |

O teste de RAM deverá preservar a região ocupada pelo próprio programa e pela pilha.

## 7. Inventário e conexões elétricas

Esses itens ainda dependem do fechamento do datapath e da unidade de controle.

Não vou congelar a lista de componentes prematuramente, pois isso poderia resultar na compra de CIs desnecessários ou incompatíveis.

## 8. Modelos Verilog

Continuam pendentes. Não encontrei as ferramentas HDL e de simulação elétrica instaladas no ambiente atual.

## 9. Regressão executada

Executei novamente as bancadas da revisão 9.0.

| Teste | Casos | Resultado |
|---|---:|---|
| Decodificação de memória | 1.048.576 | Aprovado |
| Transações VRAM | 1.600 | Aprovado |
| Varredura VGA | 105.000 | Aprovado |
| Teclado | 53.745 | Aprovado |
| Salvamento | 4.095 | Aprovado |
| Handshake isolado | 1.914 | Aprovado |
| Programas integrados | 396 | Aprovado |

Os testes existentes passaram, mas a nova auditoria demonstrou que precisamos ampliar sua cobertura.

## 10. Documentação e arquivos

[Baixar ISA-1 — Revisão 9.1, pacote de auditoria (.zip)](sandbox:/mnt/data/ISA-1_rev91_auditoria.zip)

[Relatório técnico da revisão 9.1](sandbox:/mnt/data/isa1_rev91/README.md)

O pacote preserva o comportamento da revisão anterior e acrescenta a bancada que reproduz os cinco problemas identificados. As correções ainda não foram aplicadas.

## Ordem de resolução

| Prioridade | Atividade |
|---:|---|
| 1 | Corrigir proteção de escrita |
| 2 | Corrigir reset do handshake |
| 3 | Consolidar microcódigo binário |
| 4 | Implementar gravação da EEPROM |
| 5 | Implementar montador Assembly |
| 6 | Desenvolver autodiagnóstico |
| 7 | Consolidar componentes e conexões |
| 8 | Validar modelos Verilog |
| 9 | Desenvolver esquemático |
| 10 | Desenvolver PCB |

Essa revisão foi especialmente útil para identificar lacunas reais de validação. Prefiro descobrir e corrigir esses problemas agora, em software, do que encontrá-los depois de fabricar e soldar nossa placa.

**O objetivo permanece o mesmo: um ISA-1 completo, confiável e fabricável, sem sacrificar funcionalidades.** 😎

## user — bbb217b5-ad85-460f-ab25-bc04e8d4dca8

Pode continuar😎

## assistant — c9982ebc-d0dc-4753-83b2-17748a3dbf84

{"content_type": "thoughts", "source_analysis_msg_id": "82a52f21-fa32-4d8c-9dcb-cc4ec82f0859", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Revisou arquivos, código e executou testes de segurança"}]}

## assistant — 0d2352bf-497a-47e6-a8dc-588f4181fa96

{"content": "Pensou por 25s", "content_type": "reasoning_recap"}

## assistant — b06239cd-6c62-45d2-9524-f44eff5d2084

# ISA-1 — Revisão 9.2: correção das falhas de segurança 😎

A prioridade é resolver as regressões identificadas na auditoria 9.1 antes de acrescentar novas funcionalidades.

O pacote intermediário da revisão 9.2 já está disponível no ambiente. Sua documentação registra duas falhas encontradas durante a implementação da proteção contra reset, seguidas de correções.

Vou conferir o código e os testes, especialmente a possibilidade de uma solicitação antiga voltar a executar depois de uma reinicialização.

## 1. Resultados da nova execução

Executei novamente todas as cinco bancadas disponíveis na revisão 9.2.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.282</title>
      <caption>Novos cenários de segurança e recuperação</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>396</title>
      <caption>Execuções integradas CPU/VGA</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.048.576</title>
      <caption>Casos de decodificação de memória</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções executadas</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success"/>
    Todas as cinco bancadas passaram.
  </row>
</box>

## 2. Proteção contra operações antigas

A revisão introduz um identificador de geração chamado `epoch`. Cada reset altera esse identificador, invalidando as transações anteriores.

<svg viewBox="0 0 340 185" width="100%">
  <rect x="10" y="10" width="140" height="50" rx="5" fill="#2563eb" fillOpacity=".12" stroke="#64748b"/>
  <text x="80" y="30" fill="currentColor" textAnchor="middle" fontSize="12">Transação antiga</text>
  <text x="80" y="46" fill="currentColor" textAnchor="middle" fontSize="11">Geração 1</text>
  <rect x="190" y="10" width="140" height="50" rx="5" fill="#16a34a" fillOpacity=".12" stroke="#64748b"/>
  <text x="260" y="30" fill="currentColor" textAnchor="middle" fontSize="12">Nova transação</text>
  <text x="260" y="46" fill="currentColor" textAnchor="middle" fontSize="11">Geração 2</text>
  <path d="M80 60 V95 M260 60 V95" stroke="#94a3b8" strokeWidth="2"/>
  <path d="M160 5 V175" stroke="#d97706" strokeDasharray="5 4" strokeWidth="2"/>
  <text x="170" y="82" fill="#d97706" fontSize="10">RESET</text>
  <rect x="10" y="95" width="140" height="45" rx="5" fill="#dc2626" fillOpacity=".12" stroke="#dc2626"/>
  <text x="80" y="122" textAnchor="middle" fill="#dc2626" fontSize="12">Operação cancelada</text>
  <rect x="190" y="95" width="140" height="45" rx="5" fill="#16a34a" fillOpacity=".12" stroke="#16a34a"/>
  <text x="260" y="122" textAnchor="middle" fill="#16a34a" fontSize="12">Operação autorizada</text>
  <text x="170" y="173" fill="currentColor" textAnchor="middle" fontSize="10">Nenhuma solicitação antiga deve sobreviver ao reset.</text>
</svg>

Esse mecanismo é utilizado pelo simulador. Não significa que precisaremos adicionar um contador de geração ao circuito físico: o hardware poderá obter comportamento equivalente por meio do reset coordenado dos estados de controle.

## 3. Regressão geral

| Subsistema | Casos testados | Resultado |
|---|---:|---|
| Proteção de escrita e reset | 1.282 | Aprovado |
| Decodificação de memória | 1.048.576 | Aprovado |
| Arbitragem VRAM | 1.600 | Aprovado |
| Varredura VGA | 105.000 | Aprovado |
| Teclado de membrana | 53.745 | Aprovado |
| Salvamento EEPROM | 4.095 | Aprovado |
| Handshake isolado | 1.914 | Aprovado |
| Integração CPU/VGA | 396 | Aprovado |

## 4. Pendências identificadas na inspeção

Apesar dos resultados positivos, encontrei limitações que ainda precisam ser resolvidas.

- A perda de alimentação durante WAIT precisa provocar uma recuperação global consistente.
- Os métodos de acesso direto à memória ainda podem contornar a proteção do barramento integrado.
- A proteção das transações não garante, por si só, o cancelamento de uma instrução inteira.
- O cabeçalho executável da EEPROM ainda não foi implementado.

Esses pontos impedem que consideremos a proteção contra reset completamente encerrada.

## 5. Controle das etapas restantes

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"Proteção de escrita",s:"Testada no barramento integrado",ok:true},{n:"Reset do handshake",s:"Testado parcialmente",ok:true},{n:"Microcódigo binário",s:"Pendente",ok:false},{n:"Programação da EEPROM",s:"Pendente",ok:false},{n:"Montador Assembly",s:"Pendente",ok:false},{n:"Firmware de autodiagnóstico",s:"Pendente",ok:false},{n:"Inventário definitivo",s:"Pendente",ok:false},{n:"Modelos Verilog",s:"Pendente",ok:false},{n:"Esquemático e PCB",s:"Pendente",ok:false}] as item}
    <row align="center">
      <icon name={item.ok?"check-circle-2":"circle"} color={item.ok?"success":"secondary"} size="lg"/>
      <box gap={0}>
        **{item.n}**
        <caption>{item.s}</caption>
      </box>
    </row>
  {/each}
</box>

## 6. Pacote atual

[Baixar ISA-1 — Revisão 9.2 (.zip)](sandbox:/mnt/data/ISA-1_rev92.zip)

[Documentação técnica da revisão 9.2](sandbox:/mnt/data/isa1_rev92/README.md)

Conferi o pacote existente, inspecionei seu código e executei novamente as bancadas. Nesta rodada, não fiz novas alterações no código-fonte.

A próxima prioridade será fechar as pendências de segurança e avançar para o microcódigo binário. Ele será a ponte entre nosso simulador e a implementação física da CPU com os CIs da família 74HC.

Continuamos preservando todos os recursos do ISA-1, sem simplificar artificialmente o processador para facilitar a fabricação. 😎

## user — bbb219a3-c0fd-46c4-90ce-59f102b52851

Pode seguir 

## assistant — c33b1e69-7bc1-4ae8-93e8-f7c790586225

{"content_type": "thoughts", "source_analysis_msg_id": "7869c998-1fe7-4476-a5f0-1cf7fdcf71c5", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou e inspecionou arquivos e conteúdos do sistema ISA"}]}

## assistant — 2fa9d371-ac72-4b4a-bbde-12f512b85090

{"content": "Pensou por 40s", "content_type": "reasoning_recap"}

## assistant — fb6d952b-c38c-4b7c-a04b-ca66fa15f868

# ISA-1 — Revisão 9.3: análise do reset global

Reabri o código-fonte da revisão 9.2 e preparei uma cópia de trabalho para a próxima revisão.

Encontrei um detalhe importante: atualmente, a proteção contra reset funciona no nível das transações de barramento, mas ainda não protege integralmente a execução de uma instrução.

## 1. Problema identificado

Imagine que a CPU esteja executando um CALL quando ocorre uma queda de alimentação.

<box border radius="lg" padding={3}>
  <list connector="solid" marker="number" gap={2}>
    <list-item>Busca do opcode CALL.</list-item>
    <list-item>Leitura do endereço de destino.</list-item>
    <list-item>Armazenamento do byte alto na pilha.</list-item>
    <list-item>
      <text color="danger" weight="medium">Queda de alimentação e reset.</text>
    </list-item>
    <list-item>O byte baixo não deve ser armazenado pela instrução antiga.</list-item>
    <list-item>CPU reinicia pelo endereço 0000h.</list-item>
  </list>
</box>

O byte já gravado pode permanecer na RAM. Isso não é necessariamente um problema, pois o SP será reinicializado.

O problema seria permitir que a instrução interrompida continuasse executando após o reset.

## 2. Comportamento definitivo proposto

| Elemento | Estado após reset |
|---|---|
| PC | `0000h` |
| SP | `8000h` |
| A e B | `00h` |
| X | `0000h` |
| Flags Z e C | Zero |
| Banco VRAM | Zero |
| Banco EEPROM | Zero |
| REQ e ACK | Inativos |
| Microsequenciador | Busca de instrução |
| Escrita em memória | Bloqueada durante reset |
| Boot overlay | Ativado |
| Instrução interrompida | Descartada |

A decisão é aplicar um reset coordenado a toda a arquitetura, incluindo a unidade de controle, e não somente aos registradores.

## 3. Auditoria dos caminhos de escrita

Também confirmei que o código atual possui caminhos de acesso direto à memória que podem contornar as proteções do barramento integrado.

Precisamos distinguir claramente:

- **Acesso de diagnóstico:** utilizado pela bancada para carregar programas e inspecionar a memória.
- **Acesso da CPU:** obrigatoriamente submetido à arbitragem e às proteções.
- **Acesso do vídeo:** autorizado pelo controlador VGA.
- **Programação da EEPROM:** submetida ao protocolo específico de gravação.

Essa separação evitará que o simulador aceite operações que seriam impossíveis no hardware real.

## 4. Situação das validações

| Propriedade | Situação |
|---|---|
| ALU de 8 bits | Testada |
| Registrador X | Testado |
| 26 opcodes | Modelo executável |
| Pilha descendente | Testada |
| Mapa de memória | Testado |
| VGA RGB332 | Modelo testado |
| Teclado de membrana | Modelo testado |
| Comunicação assíncrona | Testada parcialmente |
| Proteção de escrita | Testada parcialmente |
| Reset de instrução completa | Em aberto |
| Microcódigo binário | Pendente |
| Montador Assembly | Pendente |
| Programação da EEPROM | Pendente |
| Autodiagnóstico | Pendente |
| Circuito elétrico | Pendente |

Nesta rodada, inspecionei os arquivos e identifiquei os pontos de correção, mas ainda não implementei nem executei novas bancadas de testes. Portanto, não vou declarar a revisão 9.3 aprovada.

O próximo passo é corrigir essas lacunas e executar testes de reset em todas as etapas das 26 instruções, antes de avançar para o microcódigo binário.

Continuamos com o mesmo objetivo: chegar ao seu PC com o máximo possível de validações concluídas e uma base sólida para a simulação do circuito. 😎

## user — bbb21a3a-552d-4371-b7c2-bdfee0a7a806

Pode corrigir as lacunas 😎

## assistant — 1597d5b6-a698-4f71-9898-22be1c86eb27

{"content_type": "thoughts", "source_analysis_msg_id": "c8a6b7a9-e6e5-4042-be8c-415643c434e2", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Validada e empacotada a revisão ISA-1 9.3"}]}

## assistant — c3ea7cd2-6255-402e-9175-46bb415ed8c5

{"content": "Pensou por 47s", "content_type": "reasoning_recap"}

## assistant — d1b4c24e-d636-4bae-afb7-409b5a2849ae

# ISA-1 — Revisão 9.3: correções implementadas e testadas 😎

Desta vez, além da análise, alterei efetivamente o código do simulador e executei novas bancadas de validação.

O foco foi corrigir as lacunas de segurança identificadas nas revisões 9.1 e 9.2, antes de avançarmos para o microcódigo físico.

## 1. Correções realizadas

| Problema | Correção implementada |
|---|---|
| Instrução antiga continuar após reset | Cancelamento do gerador da instrução |
| Queda de alimentação durante WAIT | Reset global ao detectar alimentação insegura |
| Solicitações antigas no barramento | Invalidação por geração |
| Escrita direta contornando proteção | Bloqueio do método de escrita direta da máquina integrada |
| Teclado após reset | Reinicialização da seleção de linha |
| Cabeçalho EEPROM interpretado como código | Cabeçalho executável experimental com JMP |

As alterações foram aplicadas sobre o código existente, preservando os 26 opcodes e os recursos anteriores.

## 2. Teste de reset nas 26 instruções

Criei uma nova bancada que interrompe a execução das instruções em diferentes etapas, incluindo antes da primeira microoperação, durante WAIT e após a conclusão.

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.832</title>
      <caption>Novos cenários de reset</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">26 de 26</title>
      <caption>Opcodes exercitados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">3</title>
      <caption>Períodos de clock da CPU</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Reset explícito","Interrupção por alimentação insegura","Cancelamento da instrução anterior","Preservação do estado após cancelamento","Limpeza dos sinais REQ e ACK","Reinicialização e execução de novo programa"] as item}
    <row align="center">
      <icon name="check-circle-2" color="success"/>
      {item}
    </row>
  {/each}
</box>

Todos os novos testes passaram.

## 3. Comportamento do ISA-1 durante uma falha

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 295" width="100%">
    {#each [{y:5,t:"CPU executando instrução",c:"#2563eb"},{y:55,t:"Reset ou alimentação insegura",c:"#dc2626"},{y:105,t:"Bloquear operações pendentes",c:"#d97706"},{y:155,t:"Reinicializar CPU e controlador VGA",c:"#64748b"},{y:205,t:"Alimentação novamente segura",c:"#16a34a"},{y:255,t:"Executar boot da EEPROM",c:"#16a34a"}] as r,i}
      <rect x="35" y={r.y} width="270" height="34" rx="5" fill={r.c} fillOpacity=".12" stroke={r.c}/>
      <text x="170" y={r.y+21} textAnchor="middle" fill="currentColor" fontSize="12">{r.t}</text>
      {#if i<5}
        <path d={`M170 ${r.y+34} v16 l-4 -5 m4 5 l4 -5`} stroke="#94a3b8" strokeWidth="1.5" fill="none"/>
      {/if}
    {/each}
  </svg>
  <caption>Fluxo lógico de recuperação implementado no simulador.</caption>
</box>

Uma instrução interrompida não poderá retomar sua execução antiga no modelo integrado. Entretanto, escritas concluídas antes do reset não são desfeitas.

## 4. Correção do boot da EEPROM

Adotei um cabeçalho executável experimental.

| Endereço físico | Conteúdo |
|---|---|
| `0000h` | Opcode JMP (`40h`) |
| `0001h` | Byte baixo (`40h`) |
| `0002h` | Byte alto (`C0h`) |
| `0003–003Fh` | Espaço reservado ao cabeçalho |
| `0040h` | Início do programa |

Quando a CPU iniciar pelo endereço `0000h`, executará:

```asm
JMP C040h
```

Isso direciona a execução para a janela permanente da EEPROM, permitindo que posteriormente o firmware desative a sobreposição de boot sem perder o fluxo de execução.

Testei essa sequência com sucesso após cada um dos 1.832 cenários de reset, utilizando um programa mínimo terminado em HALT.

Essa solução evita adicionar componentes exclusivamente para alterar o endereço inicial do PC.

## 5. Regressão geral

Executei também todas as cinco bancadas anteriores.

<box border radius="lg" padding={3} gap={2}>
  <table>
    {#each [{n:"Decodificação de memória",v:"1.048.576"},{n:"Arbitragem VRAM",v:"1.600"},{n:"Varredura VGA",v:"105.000"},{n:"Teclado de membrana",v:"53.745"},{n:"Interrupções de salvamento",v:"4.095"},{n:"Handshake assíncrono",v:"1.914"},{n:"Programas CPU/VGA",v:"396"},{n:"Proteção do barramento",v:"1.282"},{n:"Reset de instruções",v:"1.832"}] as t}
      <table-row>
        <table-cell>{t.n}</table-cell>
        <table-cell align="end">{t.v}</table-cell>
        <table-cell align="end"><icon name="check-circle-2" color="success"/></table-cell>
      </table-row>
    {/each}
  </table>
  <divider/>
  **Nenhuma regressão detectada nas bancadas executadas.**
</box>

## 6. Arquivos produzidos

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      <title size="lg">ISA-1 — Revisão 9.3</title>
      <caption>Simulador corrigido, código-fonte, testes, resultados e documentação.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev93.zip)
  [Documentação técnica](sandbox:/mnt/data/isa1_rev93/README.md)
  [Nova bancada de testes](sandbox:/mnt/data/isa1_rev93/test_instruction_reset.py)
  [Resultados em JSON](sandbox:/mnt/data/isa1_rev93/instruction_reset_results.json)
</card>

## 7. Limitações restantes

Para manter nosso projeto tecnicamente rigoroso:

- Os resets foram testados nas fronteiras das microoperações, não em todas as bordas físicas dos clocks.
- A proteção foi aplicada à máquina integrada. As classes antigas continuam disponíveis para testes isolados.
- Os arrays de memória continuam acessíveis para carregar programas de teste.
- O cabeçalho executável ainda não constitui um firmware completo.
- Não foram simulados pulsos elétricos incompletos, metastabilidade ou quedas graduais de tensão.

## 8. Próximas etapas

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"9.1 — Auditoria de segurança",s:"Executada",ok:true},{n:"9.2 — Proteção do barramento",s:"Modelo testado",ok:true},{n:"9.3 — Reset de instruções",s:"Correções implementadas e testadas",ok:true},{n:"9.4 — Microcódigo binário",s:"Próxima prioridade",ok:false},{n:"9.5 — Montador Assembly",s:"Pendente",ok:false},{n:"9.6 — Programação da EEPROM",s:"Pendente",ok:false},{n:"9.7 — Firmware de autodiagnóstico",s:"Pendente",ok:false},{n:"9.8 — Modelos Verilog",s:"Pendente",ok:false},{n:"9.9 — Inventário e conexões",s:"Pendente",ok:false},{n:"10.0 — Esquemático integrado",s:"Pendente",ok:false}] as item}
    <row align="center">
      <icon name={item.ok?"check-circle-2":"circle"} color={item.ok?"success":"secondary"} size="lg"/>
      <box gap=0>
        **{item.n}**
        <caption>{item.s}</caption>
      </box>
    </row>
  {/each}
</box>

A próxima revisão será particularmente importante: transformar as microoperações do simulador em palavras binárias de controle, aproximando nossa CPU da implementação com os CIs 74HC.

Estamos construindo uma base cada vez mais sólida para o ISA-1, sem eliminar recursos para facilitar o projeto. 😎

## user — bbb212bf-63b5-4c75-a58d-d4de8f1f49b9

Pode seguir com todas as etapas previstas por vc
Se precisar, podem haver sub etapas para corrigir problemas ou analisar algum ponto

## assistant — 934e5e80-77c6-45fd-bc96-4109aff85345

{"content_type": "thoughts", "source_analysis_msg_id": "250e205e-c64d-4738-94bb-6e7a183a5021", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou código, implementou micro-operações e validou diagnóstico EEPROM"}]}

## assistant — d55a935c-1507-49eb-908e-22058fa10fca

{"content": "Pensou por 1m 29s", "content_type": "reasoning_recap"}

## assistant — e0550d3d-3d88-49d9-9eff-e9e9c8a9adcc

# ISA-1 — Revisões 9.4 em diante

Vamos manter a ordem de desenvolvimento, com liberdade para criar sub-revisões sempre que encontrarmos problemas. Cada alteração deverá ter sua justificativa, código, testes e limitações registrados para nosso futuro manual técnico.

Reabri o código da revisão 9.3. O conjunto de 26 instruções está implementado, incluindo as operações de pilha, saltos condicionais e endereçamento indireto por X.

Para a revisão 9.4, vou preservar essa implementação como referência de comparação. Assim, poderemos confrontar o novo microcódigo com o comportamento anterior, sem alterar inadvertidamente nossa ISA.

## 9.4 — Microcódigo binário experimental

Implementei uma primeira representação binária das microoperações, utilizando palavras de 16 bits.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 104" width="100%">
    {#each Array.from({length:16},(_,i)=>i) as i}
      <text x={20+i*20} y="15" fontSize="10" fill="currentColor" textAnchor="middle">{15-i}</text>
      <rect x={10+i*20} y="23" width="20" height="30" fill={i<8?"#2563eb":"#0d9488"} fillOpacity=".2" stroke="#94a3b8"/>
    {/each}
    <path d="M10 59 V65 H170 V59 M170 59 V65 H330 V59" fill="none" stroke="currentColor"/>
    <text x="90" y="82" fontSize="12" textAnchor="middle" fill="currentColor">Microoperação</text>
    <text x="250" y="82" fontSize="12" textAnchor="middle" fill="currentColor">Argumento</text>
    <text x="90" y="97" fontSize="10" textAnchor="middle" fill="currentColor">8 bits</text>
    <text x="250" y="97" fontSize="10" textAnchor="middle" fill="currentColor">8 bits</text>
  </svg>
  <caption>Formato intermediário adotado para validação. Ainda não corresponde diretamente aos pinos dos CIs.</caption>
</box>

Por exemplo, a instrução CALL agora possui uma sequência codificada que busca os dois bytes do endereço, armazena o endereço de retorno na pilha e realiza o salto.

### Resultados efetivamente executados

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">26/26</title>
      <caption>Opcodes implementados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">69</title>
      <caption>Palavras de microcódigo</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>6.656</title>
      <caption>Testes comparativos com a CPU anterior</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Divergências encontradas</caption>
    </grid-item>
  </grid>
</box>

Também executei dois programas integrados para confirmar que a nova representação funciona com o controlador assíncrono da VRAM.

**Limitação:** algumas microoperações ainda agrupam várias ações elementares. Precisaremos de uma sub-revisão para decompor essas ações em sinais físicos de controle.

## 9.5 — Nosso próprio montador Assembly

Essa etapa já possui uma implementação funcional!

Criei um montador de duas passagens que transforma código Assembly do ISA-1 em código de máquina.

Ele suporta os 26 opcodes, constantes decimais e hexadecimais, comentários, labels, referências futuras e endereços de 16 bits em little-endian.

<box border radius="lg" padding={3} gap={2}>
  <caption>Exemplo da tradução realizada pelo montador</caption>
  <table>
    <table-row>
      <table-cell>**Assembly**</table-cell>
      <table-cell>**Código de máquina**</table-cell>
    </table-row>
    {#each [["LDX #8000h","32 00 80"],["LDA #0E0h","10 E0"],["STA [X]","34"],["INX","35"],["LDA #1Ch","10 1C"],["STA [X]","34"],["HALT","FF"]] as r}
      <table-row>
        <table-cell><text>{r[0]}</text></table-cell>
        <table-cell><text>{r[1]}</text></table-cell>
      </table-row>
    {/each}
  </table>
</box>

O montador também rejeitou corretamente os quatro exemplos inválidos utilizados na bancada, incluindo estouro de operandos e labels duplicados.

Isso significa que já podemos escrever programas para o ISA-1 sem precisar calcular manualmente cada opcode.

## 9.6 — Controlador de programação da EEPROM

Implementei um modelo inicial de proteção para a gravação da AT28C256.

O controlador verifica se a alimentação está segura, se a CPU está autorizada a operar, se a rotina está sendo executada na RAM e se o endereço pertence a uma região autorizada.

<box border radius="lg" padding={3} gap={2}>
  <title>Organização da EEPROM — 32 KiB</title>
  <svg viewBox="0 0 340 190" width="100%">
    {#each [{y:5,h:30,c:"#64748b",a:"0000–003F",t:"Cabeçalho executável"},{y:35,h:70,c:"#2563eb",a:"0040–77FF",t:"Programas e recursos"},{y:105,h:40,c:"#16a34a",a:"7800–7BFF",t:"SAVE A — 1 KiB"},{y:145,h:40,c:"#0d9488",a:"7C00–7FFF",t:"SAVE B — 1 KiB"}] as r}
      <rect x="5" y={r.y} width="330" height={r.h} fill={r.c} fillOpacity=".17" stroke={r.c}/>
      <text x="15" y={r.y+r.h/2+4} fontSize="11" fill="currentColor">{r.a}</text>
      <text x="130" y={r.y+r.h/2+4} fontSize="11" fill="currentColor">{r.t}</text>
    {/each}
  </svg>
  <caption>Representação esquemática, sem escala proporcional.</caption>
</box>

Por segurança, nesta primeira implementação, somente as regiões SAVE A e SAVE B permitem gravação. A programação de novos aplicativos pelo próprio ISA-1 continuará prevista, mas deverá possuir um modo de manutenção específico.

| Teste | Resultado |
|---|---:|
| Combinações de endereço e autorização | 262.144 |
| Condições de conclusão | 4 |
| Cancelamento por reset | Aprovado |
| Falhas nas asserções | 0 |

O modelo ainda não está conectado à CPU e não reproduz a temporização elétrica da EEPROM.

## 9.7 — Primeiro programa de autodiagnóstico

Utilizando nosso novo montador, escrevi e compilei um programa nativo de diagnóstico.

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>112 bytes</title>
      <caption>Tamanho do programa compilado</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">3/3</title>
      <caption>Execuções aprovadas</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Escrita e leitura de uma posição da RAM","Comparação e salto condicional","Chamada e retorno de subrotinas","Endereçamento indireto por X","Escrita e leitura dos quatro bancos da VRAM","Armazenamento de três pixels RGB332","Verificação do estado final da pilha"] as item}
    <row align="center">
      <icon name="check-circle-2" color="success"/>
      {item}
    </row>
  {/each}
</box>

O programa deixa o valor `A5h` no endereço `5001h` quando termina com sucesso, ou `FFh` quando detecta uma falha.

É nosso primeiro programa de diagnóstico escrito em Assembly, compilado pelo nosso próprio montador e executado pelo novo modelo de microcódigo.

Ainda precisamos ampliar a cobertura para toda a RAM, ALU, flags, teclado e EEPROM.

## 9.8 — Modelos Verilog

Verifiquei a disponibilidade das ferramentas necessárias:

| Ferramenta | Finalidade | Disponível |
|---|---|---|
| Icarus Verilog | Simulação digital | Não |
| Verilator | Simulação HDL | Não |
| ngspice | Simulação elétrica | Não |
| KiCad CLI | Validação de esquemático | Não |

A implementação HDL completa permanece pendente. Podemos desenvolver os arquivos antes de chegar ao PC, mas não devemos considerá-los validados sem executar as ferramentas.

## 9.9 — Inventário e conexões

A análise do microcódigo reforça que precisamos fechar o datapath antes de congelar a quantidade de componentes.

Especialmente os circuitos responsáveis pelo incremento de X, atualização do SP, seleção dos barramentos e armazenamento dos endereços temporários.

Não alterei o inventário anterior nesta rodada.

## Regressão geral

Também executei novamente todas as cinco bancadas da revisão 9.3.

<box border radius="lg" padding={3} gap={2}>
  <table>
    {#each [{n:"Decodificação de memória",v:"1.048.576"},{n:"Arbitragem VRAM",v:"1.600"},{n:"Varredura VGA",v:"105.000"},{n:"Teclado",v:"53.745"},{n:"Salvamento EEPROM",v:"4.095"},{n:"Handshake assíncrono",v:"1.914"},{n:"Integração CPU/VGA",v:"396"},{n:"Proteção do barramento",v:"1.282"},{n:"Reset de instruções",v:"1.832"},{n:"Novo microcódigo",v:"6.656"},{n:"Autorização EEPROM",v:"262.144"}] as t}
      <table-row>
        <table-cell>{t.n}</table-cell>
        <table-cell align="end">{t.v}</table-cell>
        <table-cell align="end"><icon name="check-circle-2" color="success"/></table-cell>
      </table-row>
    {/each}
  </table>
  <divider/>
  **Nenhuma falha nas bancadas executadas.**
  <caption>Os testes antigos continuam utilizando a implementação de referência. Ainda precisamos repetir toda a cobertura de reset no novo microcódigo.</caption>
</box>

## Arquivos produzidos

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      <title size="lg">ISA-1 — Revisões 9.4 a 9.7</title>
      <caption>Código-fonte, montador, microcódigo, diagnóstico, bancadas e resultados.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev94_97.zip)
  <divider/>
  [Documentação técnica](sandbox:/mnt/data/isa1_rev94/README.md)

  [Microcódigo em JSON](sandbox:/mnt/data/isa1_rev94/microcode.json)

  [Montador Assembly em Python](sandbox:/mnt/data/isa1_rev94/assembler.py)

  [Autodiagnóstico em Assembly](sandbox:/mnt/data/isa1_rev94/diagnostic.asm)

  [Autodiagnóstico compilado (.bin)](sandbox:/mnt/data/isa1_rev94/diagnostic.bin)
</card>

## Sub-revisões necessárias

Como você autorizou a criação de etapas intermediárias, vou manter as seguintes pendências na nossa sequência de desenvolvimento.

| Revisão | Objetivo |
|---|---|
| 9.4.1 | Decompor microoperações em sinais físicos |
| 9.4.2 | Validar conflitos entre sinais de controle |
| 9.4.3 | Testar reset no novo microcódigo |
| 9.5.1 | Ampliar e testar o montador |
| 9.6.1 | Integrar programação EEPROM à CPU |
| 9.6.2 | Validar interrupções durante gravação |
| 9.7.1 | Autodiagnóstico completo |
| 9.8.1 | Verilog do datapath |
| 9.8.2 | Verilog da unidade de controle |
| 9.8.3 | Verilog do controlador VGA |
| 9.8.4 | Integração digital completa |
| 9.9.1 | Inventário de CIs e pinagem |
| 9.9.2 | Orçamento de consumo elétrico |
| 9.9.3 | Análise de temporização |
| 10.0 | Esquemático integrado |

**Um marco importante desta rodada:** o ISA-1 já possui uma linguagem Assembly própria, um montador funcional, uma representação binária intermediária de microcódigo e um programa nativo de diagnóstico executado em simulação.

Estamos desenvolvendo não apenas o computador, mas também seu ecossistema de software. 😎

## user — bbb21200-0470-4d57-91d8-2f5e3107476e

O avanço agora foi grande hein! Gostei😎
O que temos ainda a fazer? 

## assistant — 11d97409-a619-4163-ae03-f8dfc02e4e5c

O avanço foi grande mesmo! 😎 Agora o ISA-1 deixou de ser apenas uma proposta de arquitetura: já temos um modelo executável do processador e começamos a construir seu próprio ecossistema de software.

O próximo grande desafio é transformar essa arquitetura lógica em um circuito eletrônico fabricável.

# Roadmap geral do ISA-1

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"Arquitetura e conjunto de instruções",p:1,s:"Definidos e testados em software"},{n:"Simulador da CPU",p:1,s:"Implementado e testado"},{n:"Microcódigo físico",p:.5,s:"Representação intermediária implementada"},{n:"Montador Assembly",p:.75,s:"Funcional, necessita refinamentos"},{n:"Memória e armazenamento",p:.65,s:"Modelos testados, integração pendente"},{n:"Controlador VGA",p:.65,s:"Modelo digital testado"},{n:"Teclado",p:.65,s:"Modelo sem diodos testado"},{n:"Firmware e sistema operacional",p:.15,s:"Autodiagnóstico inicial"},{n:"Implementação eletrônica",p:.2,s:"Circuitos parciais definidos"},{n:"Esquemático integrado",p:0,s:"Pendente"},{n:"PCB",p:0,s:"Pendente"},{n:"Protótipo físico",p:0,s:"Pendente"}] as item}
    <box gap={1}>
      <row align="center">
        **{item.n}**
        <spacer/>
        <icon name={item.p===1?"check-circle-2":item.p===0?"circle":"clock"} color={item.p===1?"success":"secondary"}/>
      </row>
      <box height={6} radius="full" background="surface-tertiary" clip>
        <box height={6} radius="full" width={`${item.p*100}%`} background={item.p===1?"#16a34a":"#d97706"}/>
      </box>
      <caption>{item.s}</caption>
    </box>
  {/each}
  <caption>Barras ilustrativas de maturidade, não porcentagens medidas de conclusão.</caption>
</box>

## Fase 1 — Finalizar a arquitetura lógica

| Revisão | Atividade |
|---|---|
| 9.4.1 | Decompor o microcódigo em sinais físicos |
| 9.4.2 | Eliminar conflitos de barramento |
| 9.4.3 | Validar reset no novo microcódigo |
| 9.4.4 | Definir comportamento de opcodes inválidos |
| 9.5.1 | Refinar o montador Assembly |
| 9.5.2 | Desenvolver um desmontador |
| 9.6.1 | Integrar a gravação da EEPROM |
| 9.6.2 | Testar interrupções de gravação |
| 9.6.3 | Implementar modo de manutenção da EEPROM |
| 9.7.1 | Ampliar o autodiagnóstico |

## Fase 2 — Transformar a CPU em circuitos reais

Essa será uma das fases mais interessantes.

<box border radius="lg" padding={2}>
  <svg viewBox="0 0 340 340" width="100%">
    {#each [{x:10,y:10,w:150,h:45,t:"Unidade de controle",s:"Microsequenciador"},{x:180,y:10,w:150,h:45,t:"Clock e reset",s:"Supervisor de tensão"},{x:10,y:80,w:95,h:50,t:"Registradores",s:"A, B, X"},{x:122,y:80,w:96,h:50,t:"ALU",s:"8 bits"},{x:235,y:80,w:95,h:50,t:"PC e SP",s:"16 bits"},{x:10,y:195,w:100,h:45,t:"RAM",s:"32 KiB"},{x:120,y:195,w:100,h:45,t:"EEPROM",s:"32 KiB / ZIF"},{x:230,y:195,w:100,h:45,t:"VRAM",s:"32 KiB"},{x:10,y:280,w:150,h:45,t:"Teclado",s:"64 teclas"},{x:180,y:280,w:150,h:45,t:"VGA",s:"RGB332 / 256 cores"}] as r}
      <rect x={r.x} y={r.y} width={r.w} height={r.h} rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={r.x+r.w/2} y={r.y+19} fontSize="11" fontWeight="bold" fill="currentColor" textAnchor="middle">{r.t}</text>
      <text x={r.x+r.w/2} y={r.y+33} fontSize="10" fill="currentColor" textAnchor="middle">{r.s}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.5" fill="none">
      <path d="M85 55 V65 H282 V80 M57 65 V80 M170 65 V80 M255 55 V65"/>
      <path d="M57 130 V148 M170 130 V148 M282 130 V148"/>
      <path d="M60 174 V195 M170 174 V195 M280 174 V195 M5 161 H2 V302 H10 M280 240 V280"/>
    </g>
    <rect x="5" y="148" width="330" height="26" rx="4" fill="#0d9488" fillOpacity=".2" stroke="#0d9488"/>
    <text x="170" y="165" fill="currentColor" fontSize="11" fontWeight="bold" textAnchor="middle">Barramentos de dados, endereços e controle</text>
  </svg>
  <caption>Arquitetura funcional do ISA-1. Ainda não é o esquemático elétrico.</caption>
</box>

| Revisão | Atividade |
|---|---|
| 9.8.1 | Circuito dos registradores |
| 9.8.2 | Circuito da ALU |
| 9.8.3 | Circuito de PC e SP |
| 9.8.4 | Circuito de incremento e decremento de X |
| 9.8.5 | Unidade de controle |
| 9.8.6 | Microsequenciador |
| 9.8.7 | Decodificador de instruções |
| 9.8.8 | Arbitragem de barramentos |
| 9.8.9 | Modelos Verilog integrados |

## Fase 3 — Engenharia eletrônica

| Revisão | Atividade |
|---|---|
| 9.9.1 | Seleção definitiva dos CIs |
| 9.9.2 | Conferência de todas as pinagens |
| 9.9.3 | Compatibilidade entre HC, HCT e demais famílias |
| 9.9.4 | Análise de propagação dos sinais |
| 9.9.5 | Determinação da frequência máxima da CPU |
| 9.9.6 | Dimensionamento da alimentação USB-C |
| 9.9.7 | Desacoplamento e distribuição de energia |
| 9.9.8 | Proteção contra brownout |
| 9.9.9 | Custo e quantidade de componentes |

Aqui também vamos avaliar oportunidades de reduzir a quantidade de CIs, sem sacrificar funcionalidades.

## Fase 4 — Esquemático e fabricação

| Revisão | Atividade |
|---|---|
| 10.0 | Esquemático completo |
| 10.1 | Verificação elétrica ERC |
| 10.2 | Auditoria das conexões |
| 10.3 | Seleção de footprints |
| 10.4 | Posicionamento dos componentes |
| 10.5 | Roteamento da PCB |
| 10.6 | Integridade de sinais |
| 10.7 | Verificação DRC |
| 10.8 | Arquivos Gerber |
| 10.9 | Lista de materiais definitiva |
| 11.0 | Fabricação do primeiro protótipo |

## Fase 5 — Ecossistema de software

Não precisamos esperar a fabricação da placa para desenvolver boa parte disso.

<box border radius="lg" padding={3}>
  {#each [{n:"Simulador ISA-1",s:"Funcional"},{n:"Montador Assembly",s:"Funcional"},{n:"Desmontador",s:"Planejado"},{n:"BIOS",s:"Planejado"},{n:"Monitor de memória",s:"Planejado"},{n:"Biblioteca gráfica",s:"Planejado"},{n:"Driver de teclado",s:"Planejado"},{n:"Gerenciador de armazenamento",s:"Planejado"},{n:"Editor de texto",s:"Planejado"},{n:"Interpretador BASIC",s:"Planejado"},{n:"Editor Assembly nativo",s:"Planejado"},{n:"Jogos e aplicativos",s:"Planejado"}] as item}
    <row align="center">
      <icon name={item.s==="Funcional"?"check-circle-2":"circle"} color={item.s==="Funcional"?"success":"secondary"}/>
      <box flex={1} gap={0}>
        **{item.n}**
        <caption>{item.s}</caption>
      </box>
    </row>
  {/each}
</box>

Minha intenção é que o ISA-1 consiga criar, editar, executar e salvar seus próprios programas, sem depender de outro computador para seu uso cotidiano.

## Fase 6 — Nosso livro técnico

**ISA-1 — Manual de Arquitetura, Engenharia e Programação**

Vamos documentar a história do projeto, todas as decisões, revisões, erros encontrados, soluções, resultados de testes, arquitetura, instruções, esquemáticos, montagem e programação.

Inclusive as abordagens que abandonamos. Elas fazem parte da história da engenharia do computador.

## O que podemos fazer antes de você ligar o PC?

Ainda temos bastante trabalho possível neste ambiente:

- Desenvolver e testar o microcódigo físico.
- Validar combinações de sinais de controle.
- Desenvolver os modelos Verilog.
- Elaborar tabelas de conexões pino a pino.
- Expandir os testes automatizados.
- Desenvolver o firmware e as ferramentas de programação.
- Consolidar a documentação de todas as revisões.

As validações elétricas, a execução das ferramentas HDL indisponíveis aqui e os testes físicos continuarão pendentes até termos o ambiente adequado.

**Minha próxima prioridade é a revisão 9.4.1.** Precisamos transformar cada uma das 26 instruções em uma sequência de sinais que possam ser implementados por CIs reais.

É justamente essa etapa que fará a transição do ISA-1 de um processador simulado para o projeto de um processador físico.

E tudo isso mantendo nossa filosofia original: CPU própria, lógica discreta, sem microcontrolador escondido fazendo o trabalho do processador. 😎

## user — bbb21e19-439a-4f15-9d0e-acc2d6c0adcd

🥹 tá ficando top demais! Pode seguir com todas as fases que vc levantou

## assistant — 3390f85f-5bea-4e41-a69f-e4d721321dac

{"content_type": "thoughts", "source_analysis_msg_id": "d037caef-dc91-4ebf-b05a-6f6d35c4e0f8", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou e validou assembler, microcódigo, testes e opcodes da ISA"}]}

## assistant — 792f35ee-6dfb-4f33-b9ab-28c3537e214f

{"content": "Pensou por 50s", "content_type": "reasoning_recap"}

## assistant — fd1acb2d-5bab-42b8-8a1c-03a3faa6f1d8

Vamos seguir! 😎 A partir daqui, vou tratar o ISA-1 como um projeto de engenharia completo, mantendo as versões anteriores como referência e criando sub-revisões quando necessário.

A regra continua sendo: nenhuma funcionalidade será considerada validada eletricamente apenas porque passou em um teste Python. Também vamos preservar o histórico das decisões para o nosso livro técnico.

## Revisão 9.4.3 — Reset no novo microcódigo

Antecipei essa validação porque já tínhamos uma bancada pronta para a CPU anterior, mas ainda não havíamos aplicado a mesma cobertura à nova implementação.

Adaptei e executei a bancada utilizando a classe `EncodedMachine`, que interpreta as palavras binárias de microcódigo.

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl">26/26</title>
      <caption>Instruções exercitadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.832</title>
      <caption>Cenários de reset</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">3</title>
      <caption>Períodos de clock da CPU</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
</box>

A nova implementação passou nos testes de interrupção e reinicialização nas fronteiras das microoperações.

## Revisão 9.5.2 — Desmontador Assembly

Agora temos também a operação inversa do montador: converter código de máquina em Assembly legível.

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <caption>Código de máquina</caption>
      <text preserveWhitespace={true}>32 00 80
10 E0
34
35
FF</text>
    </grid-item>
    <grid-item>
      <caption>Assembly recuperado</caption>
      <text preserveWhitespace={true}>LDX #8000h
LDA #E0h
STA [X]
INX
HALT</text>
    </grid-item>
  </grid>
  <divider/>
  <title size="2xl" tabularNums>459.281</title>
  <caption>Combinações de instruções e operandos verificadas.</caption>
  <row align="center">
    <icon name="check-circle-2" color="success"/> Nenhuma divergência encontrada.
  </row>
</box>

O teste percorreu todos os valores possíveis dos operandos de 8 e 16 bits de cada opcode válido. Cada instrução foi desmontada e remontada, verificando se os bytes resultantes eram idênticos aos originais.

Esse recurso será muito útil para nosso futuro monitor de memória e depurador nativo.

## Revisão 9.4.4 — Proteção contra instruções inválidas

Encontrei outra lacuna: nosso processador possui 26 opcodes válidos, mas um barramento de 8 bits permite representar 256 valores diferentes.

O que acontece se a CPU encontrar um dos outros 230 valores?

Antes da correção, o simulador gerava uma exceção Python. Isso não representa um comportamento adequado para um processador físico.

Adotei provisoriamente o seguinte comportamento:

- Interromper a execução da CPU.
- Não realizar escritas na memória.
- Manter os demais registradores preservados, exceto o avanço do PC durante a busca do opcode.
- Permitir recuperação através do reset.

Testei os **230 opcodes inválidos**. Todos passaram nas verificações de parada, PC, ausência de escrita e recuperação.

Essa decisão ainda deverá ser implementada na unidade de controle física.

## Resultados desta rodada

| Validação executada | Casos | Falhas |
|---|---:|---:|
| Montador e desmontador | 459.281 | 0 |
| Opcodes inválidos | 230 | 0 |
| Reset no microcódigo | 1.832 | 0 |
| Comparação entre CPUs | 6.656 | 0 |
| Programas integrados | 2 | 0 |
| **Total** | **468.001** | **0** |

## Controle das fases do projeto

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"Fase 1 — Arquitetura lógica",s:"Em desenvolvimento",c:"#16a34a",items:[["Reset no microcódigo",true],["Tratamento de opcodes inválidos",true],["Desmontador Assembly",true],["Sinais físicos de controle",false],["EEPROM integrada",false],["Autodiagnóstico completo",false]]},{n:"Fase 2 — Circuitos digitais",s:"Parcialmente definida",c:"#d97706",items:[["Datapath completo",false],["Microsequenciador físico",false],["Verilog integrado",false]]},{n:"Fase 3 — Engenharia eletrônica",s:"Pendente",c:"#94a3b8",items:[["Inventário definitivo",false],["Temporização elétrica",false],["Alimentação e consumo",false]]},{n:"Fase 4 — Fabricação",s:"Pendente",c:"#94a3b8",items:[["Esquemático",false],["PCB e Gerber",false],["Protótipo",false]]},{n:"Fase 5 — Software",s:"Iniciada",c:"#16a34a",items:[["Simulador",true],["Montador",true],["Desmontador",true],["BIOS",false],["Monitor de memória",false],["BASIC",false]]},{n:"Fase 6 — Livro técnico",s:"Documentação incremental",c:"#d97706",items:[["Registro das revisões atuais",true],["Consolidação histórica",false],["Manual definitivo",false]]}] as f}
    <box gap={2}>
      **{f.n}**
      <caption>{f.s}</caption>
      {#each f.items as item}
        <row align="center">
          <icon name={item[1]?"check-circle-2":"circle"} color={item[1]?"success":"secondary"}/>
          <text size="sm">{item[0]}</text>
        </row>
      {/each}
    </box>
    <divider/>
  {/each}
</box>

## Arquivos atualizados

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap={0}>
      **ISA-1 — Pacote incremental**
      <caption>Código-fonte, desmontador, correções, testes e documentação.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev941_952.zip)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev941/README.md)
</card>

## Próxima prioridade

Ainda precisamos decompor as 69 palavras de microcódigo intermediário em sinais elementares que possam controlar componentes reais.

Essa etapa envolve definir:

- Fontes e destinos dos barramentos.
- Seleção das operações da ALU.
- Habilitação dos registradores.
- Controle de leitura e escrita.
- Incremento e decremento dos endereços.
- Condições de avanço do microsequenciador.
- Prevenção de conflitos elétricos.

Nesta rodada, priorizei as validações que já podiam ser executadas integralmente. As demais fases ainda não foram concluídas, e o desmontador ainda não diferencia automaticamente dados de instruções nem recupera labels originais.

Continuamos com todas as funcionalidades previstas, sem reduzir a capacidade do ISA-1 para facilitar sua implementação.

**Nosso computador já tem uma arquitetura própria, um simulador, um montador e agora um desmontador. O próximo grande marco será fechar o circuito lógico da CPU.** 😎

## user — bbb212e6-b123-41c2-9912-4d63872674d1

Boa 😎 vamos avançar

## assistant — 087e04ef-a33d-4901-9ab7-12394ec62d00

{"content_type": "thoughts", "source_analysis_msg_id": "8caec481-04dc-417e-ba57-1886d10bef53", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Auditou microcódigo, controle horizontal e documentação do processador"}]}

## assistant — 19ecd0dd-4195-42d3-9483-ff3fc4a04ddf

{"content": "Pensou por 49s", "content_type": "reasoning_recap"}

## assistant — a42bce4a-f86a-40aa-b0c2-067e43362340

# ISA-1 — Revisão 9.4.1: datapath e unidade de controle

Inspecionei novamente o código das 26 instruções. Identifiquei que algumas microoperações ainda escondem ações que, no circuito real, precisarão acontecer separadamente.

Por exemplo, PUSH envolve calcular `SP − 1`, selecionar o endereço, selecionar o dado, solicitar a escrita, aguardar sua conclusão e atualizar SP.

Vamos decompor essas operações sem alterar a ISA. Também manteremos a convenção de pilha descendente, o endereçamento de 16 bits e o comportamento das flags.

## 1. Nova palavra de controle: 26 bits

Implementei uma representação de controle mais próxima do hardware, dividida em 11 campos independentes.

<box border radius="lg" padding={3} gap={2}>
  <title>Formato da palavra de controle</title>
  <svg viewBox="0 0 338 76" width="100%">
    {#each [{n:"ADR",b:3,c:"#2563eb"},{n:"SRC",b:3,c:"#2563eb"},{n:"DST",b:3,c:"#2563eb"},{n:"MEM",b:2,c:"#d97706"},{n:"PC",b:3,c:"#0d9488"},{n:"SP",b:2,c:"#0d9488"},{n:"X",b:2,c:"#0d9488"},{n:"ALU",b:4,c:"#9333ea"},{n:"F",b:2,c:"#9333ea"},{n:"E",b:1,c:"#64748b"},{n:"H",b:1,c:"#64748b"}] as f,i}
      <rect x={13*[0,3,6,9,11,14,16,18,22,24,25][i]} y="10" width={13*f.b} height="32" fill={f.c} fillOpacity=".22" stroke="#94a3b8"/>
      <text x={13*([0,3,6,9,11,14,16,18,22,24,25][i]+f.b/2)} y="29" fontSize="9" textAnchor="middle" fill="currentColor">{f.n}</text>
      <text x={13*([0,3,6,9,11,14,16,18,22,24,25][i]+f.b/2)} y="56" fontSize="10" textAnchor="middle" fill="currentColor">{f.b}</text>
    {/each}
  </svg>
  <caption>Campos apresentados do menos significativo ao mais significativo. Os números inferiores indicam a largura em bits.</caption>
</box>

| Campo | Bits | Função |
|---|---:|---|
| ADR | 3 | Seleção do endereço |
| SRC | 3 | Fonte de dados |
| DST | 3 | Registrador de destino |
| MEM | 2 | Leitura ou escrita |
| PC | 3 | Controle do contador de programa |
| SP | 2 | Controle da pilha |
| X | 2 | Controle do registrador X |
| ALU | 4 | Operação aritmética ou lógica |
| F | 2 | Atualização das flags |
| E | 1 | Finalização da instrução |
| H | 1 | Parada da CPU |
| **Total** | **26** | |

Essa organização permite selecionar uma única fonte de dados por vez, reduzindo estruturalmente a possibilidade de conflitos no barramento.

## 2. Evolução do microcódigo

<grid columns={2}>
  <grid-item>
    <card gap={1}>
      <caption>Implementação anterior</caption>
      <title size="2xl">69 palavras</title>
      Microoperações agrupadas
      <caption>16 bits por palavra</caption>
    </card>
  </grid-item>
  <grid-item>
    <card gap={1}>
      <caption>Nova implementação</caption>
      <title size="2xl" color="success">95 palavras</title>
      Controle decomposto
      <caption>26 bits por palavra, incluindo fetch</caption>
    </card>
  </grid-item>
</grid>

Das 95 palavras utilizadas, somente 35 são diferentes entre si.

Isso abre uma possibilidade interessante de otimização futura da unidade de controle, reutilizando microoperações comuns entre diferentes instruções.

## 3. Organização atual do datapath

<box border radius="lg" padding={2}>
  <svg viewBox="0 0 340 300" width="100%">
    {#each [{x:10,y:10,w:70,h:38,t:"A",s:"8 bits"},{x:90,y:10,w:70,h:38,t:"B",s:"8 bits"},{x:180,y:10,w:70,h:38,t:"PC",s:"16 bits"},{x:260,y:10,w:70,h:38,t:"SP",s:"16 bits"},{x:10,y:75,w:150,h:40,t:"ALU",s:"8 bits"},{x:180,y:75,w:70,h:40,t:"X",s:"16 bits"},{x:260,y:75,w:70,h:40,t:"EA",s:"16 bits"},{x:10,y:180,w:100,h:40,t:"MDR",s:"8 bits"},{x:120,y:180,w:100,h:40,t:"IR",s:"8 bits"},{x:230,y:180,w:100,h:40,t:"Memória",s:"RAM / ROM / VRAM"},{x:10,y:250,w:320,h:38,t:"Unidade de controle",s:"Microcódigo de 26 bits"}] as r}
      <rect x={r.x} y={r.y} width={r.w} height={r.h} rx="4" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x={r.x+r.w/2} y={r.y+16} fontSize="12" fontWeight="bold" fill="currentColor" textAnchor="middle">{r.t}</text>
      <text x={r.x+r.w/2} y={r.y+30} fontSize="10" fill="currentColor" textAnchor="middle">{r.s}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="1.5" fill="none">
      <path d="M45 48 V75 M125 48 V75 M85 115 V140 M215 48 V62 H255 V140 M295 48 V62 H255 M215 115 V140 M295 115 V140 M60 162 V180 M170 162 V180 M280 162 V180 M170 220 V250"/>
    </g>
    <rect x="10" y="140" width="320" height="22" rx="3" fill="#0d9488" fillOpacity=".2" stroke="#0d9488"/>
    <text x="170" y="155" textAnchor="middle" fontSize="11" fill="currentColor">Barramentos e seleção de sinais</text>
  </svg>
  <caption>Diagrama funcional simplificado do datapath candidato, não uma netlist elétrica.</caption>
</box>

O modelo agora explicita dois registradores internos importantes:

**MDR — Memory Data Register:** armazena temporariamente os dados recebidos da memória.

**IR — Instruction Register:** armazena o opcode da instrução em execução.

Isso aproxima o simulador da organização que precisaremos implementar com os CIs reais.

## 4. Revisão 9.4.2 — Auditoria de conflitos

Verifiquei todas as 95 palavras de controle geradas.

| Propriedade verificada | Resultado |
|---|---|
| Seleção exclusiva da fonte | <icon name="check-circle-2" color="success"/> |
| Seleção exclusiva do endereço | <icon name="check-circle-2" color="success"/> |
| Leitura e escrita mutuamente exclusivas | <icon name="check-circle-2" color="success"/> |
| Separação de acesso e atualização de registradores | <icon name="check-circle-2" color="success"/> |
| Destinos associados a fontes válidas | <icon name="check-circle-2" color="success"/> |
| Codificação e decodificação reversíveis | <icon name="check-circle-2" color="success"/> |

Nenhum conflito estrutural foi encontrado nas palavras válidas geradas. Ainda será necessário verificar os atrasos de propagação dos decodificadores físicos.

## 5. Novos testes executados

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>6.656</title>
      <caption>Comparações com a CPU de referência</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>2.546</title>
      <caption>Cenários de reset</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">26/26</title>
      <caption>Opcodes exercitados</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success"/>
    Dois programas integrados CPU/VGA também passaram.
  </row>
</box>

A nova decomposição aumentou a cobertura de reset de 1.832 para 2.546 cenários.

Nenhuma divergência foi encontrada entre o comportamento da CPU de referência e o novo modelo nos casos executados.

## 6. Possível implementação da memória de controle

Uma consequência interessante da palavra de 26 bits é a possibilidade de utilizar quatro EEPROMs de 8 bits em paralelo.

<svg viewBox="0 0 340 180" width="100%">
  <rect x="60" y="5" width="220" height="30" rx="4" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
  <text x="170" y="24" textAnchor="middle" fontSize="12" fill="currentColor">Endereço da microinstrução</text>
  <path d="M170 35 V50 M42 50 H297" stroke="currentColor" fill="none"/>
  {#each [0,1,2,3] as i}
    <path d={`M${42+i*85} 50 V65 M${42+i*85} 115 V135`} stroke="#94a3b8" fill="none"/>
    <rect x={5+i*85} y="65" width="74" height="50" rx="4" fill="#2563eb" fillOpacity=".12" stroke="#64748b"/>
    <text x={42+i*85} y="85" textAnchor="middle" fontSize="11" fill="currentColor">EEPROM {i+1}</text>
    <text x={42+i*85} y="101" textAnchor="middle" fontSize="10" fill="currentColor">8 bits</text>
  {/each}
  <rect x="5" y="135" width="330" height="35" rx="4" stroke="#0d9488" fill="#0d9488" fillOpacity=".15"/>
  <text x="170" y="150" fontSize="11" textAnchor="middle" fill="currentColor">32 bits disponíveis</text>
  <text x="170" y="163" fontSize="10" textAnchor="middle" fill="currentColor">26 utilizados + 6 reservados</text>
</svg>

Essa é apenas uma alternativa candidata. Antes de adotá-la, vamos comparar custo, velocidade e quantidade de componentes com outras formas de implementar a unidade de controle.

Essas EEPROMs seriam internas à CPU, independentes da EEPROM removível que utilizaremos como nosso cartucho.

## 7. Arquivos produzidos

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap={0}>
      <title size="lg">ISA-1 — Revisão 9.4.2</title>
      <caption>Simulador atualizado, palavras de controle, bancadas e documentação acumulada.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev942.zip)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev942/README.md)

  [Tabela de palavras de controle](sandbox:/mnt/data/isa1_rev942/control_fields.json)

  [Código do novo modelo](sandbox:/mnt/data/isa1_rev942/control.py)
</card>

## 8. Próximas etapas

| Etapa | Situação |
|---|---|
| Microcódigo intermediário | <text color="success">Testado</text> |
| Decomposição em campos de controle | <text color="success">Testada</text> |
| Auditoria estrutural de conflitos | <text color="success">Testada</text> |
| Reset no novo modelo | <text color="success">Testado</text> |
| Microsequenciador físico | Pendente |
| Circuito da ALU | Pendente |
| Circuitos de SP e X | Pendente |
| Integração da EEPROM | Pendente |
| Autodiagnóstico completo | Pendente |
| Modelos Verilog | Pendente |
| Esquemático e PCB | Pendente |

**Limitações desta revisão:** a palavra de 26 bits ainda é candidata, o acesso à memória permanece parcialmente abstrato, e as operações de incremento e decremento ainda precisam ser implementadas em portas lógicas. Também precisamos definir o comportamento físico em caso de estouro da pilha. Não houve validação elétrica nesta rodada.

O próximo passo será projetar os circuitos que interpretam essas palavras de controle, procurando aproveitar os CIs já previstos e reduzir componentes onde for possível.

Estamos cada vez mais próximos de transformar o ISA-1 em um computador de verdade. 😎

## user — bbb21b06-fd38-4269-bd1c-4fb45a14ea4d

Pode ir pro próximo passo

## assistant — 3bfacfe6-1845-422d-a101-d6572aec75f0

{"content_type": "thoughts", "source_analysis_msg_id": "01bf809b-0a00-4a2a-a8e3-faee6062c6d4", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou e documentou candidato de microsequenciador ISA-1"}]}

## assistant — 9dcad68f-5ddf-40f2-aa6e-652745bd778a

{"content": "Pensou por 42s", "content_type": "reasoning_recap"}

## assistant — 3266eeaa-f981-433a-b41c-de850dc4c5b7

# ISA-1 — Revisão 9.8.1: implementação lógica do microsequenciador

Reabri o código da revisão 9.4.2. Temos 95 palavras de controle de 26 bits, mas ainda precisamos definir como o circuito físico selecionará e executará cada uma delas.

A proposta desta etapa é utilizar uma memória de controle interna, um contador de microetapas e um registrador de saída. Isso permitirá preservar nossa CPU de lógica discreta, sem utilizar um microcontrolador para interpretar as instruções.

Também precisamos garantir que opcodes inválidos e endereços não utilizados da memória de controle produzam uma parada segura.

## 1. Organização da memória de microcódigo

Implementei uma memória de controle com endereçamento de 13 bits e palavras de 32 bits, dos quais utilizaremos 26.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 300" width="100%">
    <rect x="10" y="5" width="145" height="42" rx="4" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="82" y="22" fontSize="12" fill="currentColor" textAnchor="middle">Registrador IR</text>
    <text x="82" y="37" fontSize="10" fill="currentColor" textAnchor="middle">Opcode — 8 bits</text>
    <rect x="185" y="5" width="145" height="42" rx="4" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
    <text x="257" y="22" fontSize="12" fill="currentColor" textAnchor="middle">Microsequenciador</text>
    <text x="257" y="37" fontSize="10" fill="currentColor" textAnchor="middle">Etapa — 4 bits</text>
    <path d="M82 47 V65 H257 V47 M170 65 V80" stroke="#94a3b8" fill="none"/>
    <rect x="45" y="80" width="250" height="30" rx="4" stroke="#0d9488" fill="#0d9488" fillOpacity=".15"/>
    <text x="170" y="99" fontSize="11" fill="currentColor" textAnchor="middle">Endereço de controle — 13 bits</text>
    <path d="M170 110 V125 H42 M170 125 H297" stroke="#94a3b8" fill="none"/>
    {#each [0,1,2,3] as i}
      <path d={`M${42+i*85} 125 V138 M${42+i*85} 186 V200`} stroke="#94a3b8" fill="none"/>
      <rect x={5+i*85} y="138" width="74" height="48" rx="4" stroke="#2563eb" fill="#2563eb" fillOpacity=".15"/>
      <text x={42+i*85} y="157" fontSize="11" fill="currentColor" textAnchor="middle">ROM {i}</text>
      <text x={42+i*85} y="173" fontSize="10" fill="currentColor" textAnchor="middle">8 KiB</text>
    {/each}
    <rect x="5" y="200" width="330" height="36" rx="4" stroke="#9333ea" fill="#9333ea" fillOpacity=".15"/>
    <text x="170" y="215" fontSize="12" fill="currentColor" textAnchor="middle">Registrador de controle</text>
    <text x="170" y="229" fontSize="10" fill="currentColor" textAnchor="middle">32 bits</text>
    <path d="M170 236 V254" stroke="#94a3b8"/>
    <rect x="5" y="254" width="330" height="36" rx="4" stroke="#0d9488" fill="#0d9488" fillOpacity=".15"/>
    <text x="170" y="276" fontSize="12" fill="currentColor" textAnchor="middle">Decodificação e controle do datapath</text>
  </svg>
  <caption>Arquitetura candidata da unidade de controle física.</caption>
</box>

A memória será organizada da seguinte maneira:

| Bits de endereço | Função |
|---|---|
| A12 | Seleção da fase FETCH |
| A11–A4 | Opcode da instrução |
| A3–A0 | Etapa da microinstrução |

Isso permite até 16 microetapas por opcode. Atualmente, nossa instrução mais complexa, CALL, utiliza 10 etapas de execução, além das duas de busca do opcode.

## 2. Geração das ROMs reais

Agora temos os primeiros arquivos binários destinados à futura memória de controle física do ISA-1.

<grid columns={2}>
  <grid-item>
    <card gap={1}>
      <caption>Capacidade total</caption>
      <title size="2xl">32 KiB</title>
      Quatro ROMs de 8 KiB
    </card>
  </grid-item>
  <grid-item>
    <card gap={1}>
      <caption>Palavras de controle</caption>
      <title size="2xl">8.192</title>
      32 bits por endereço
    </card>
  </grid-item>
  <grid-item>
    <card gap={1}>
      <caption>Posições utilizadas</caption>
      <title size="2xl">95</title>
      Incluindo FETCH
    </card>
  </grid-item>
  <grid-item>
    <card gap={1}>
      <caption>Posições protegidas</caption>
      <title size="2xl">8.097</title>
      Preenchidas com HALT
    </card>
  </grid-item>
</grid>

As posições não utilizadas foram preenchidas com uma palavra de parada sem solicitação de escrita.

Embora a ocupação da memória seja pequena, essa organização simplifica a lógica de endereçamento. Posteriormente, podemos avaliar alternativas mais econômicas.

## 3. Componentes candidatos

| Componente | Quantidade | Função |
|---|---:|---|
| EEPROM de pelo menos 8 KiB | 4 | Microcódigo |
| 74HC574 ou 74HCT574 | 4 | Registrador de controle |
| 74HC163 | 1 | Contador de microetapas |
| Registrador octal | 1 | Armazenamento do opcode |
| 74HC74 | 1 | Estados FETCH e HALT |
| Portas lógicas e multiplexadores | A definir | Decodificação e segurança |

Essa lista é preliminar. Ainda precisamos verificar compatibilidade elétrica, temporização e quantidade de portas auxiliares.

As memórias de microcódigo serão independentes da EEPROM removível que armazenará nossos programas.

## 4. Testes efetivamente executados

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.024</title>
      <caption>Sequências de opcodes</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>11.676</title>
      <caption>Ciclos de espera</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" tabularNums>1.090</title>
      <caption>Cenários de reset</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  {#each ["Todos os 256 valores possíveis de opcode","Verificação das 8.192 posições da ROM","Reconstrução das palavras a partir dos quatro bytes","Bloqueio do avanço durante WAIT","Bloqueio do avanço quando RUN está inativo","Recuperação do microsequenciador após reset"] as item}
    <row align="center">
      <icon name="check-circle-2" color="success"/>
      {item}
    </row>
  {/each}
</box>

Também executei novamente os testes da CPU da revisão anterior:

| Bancada | Casos | Falhas |
|---|---:|---:|
| Comparação entre CPUs | 6.656 | 0 |
| Reset de instruções | 2.546 | 0 |
| Programas integrados | 2 | 0 |

Esses últimos testes continuam utilizando o modelo anterior da CPU, não a nova ROM integrada ao datapath.

## 5. Um cuidado importante com a temporização

Não podemos simplesmente conectar as saídas das EEPROMs diretamente aos sinais de escrita e habilitação dos registradores.

Durante uma mudança de endereço, as saídas podem apresentar valores transitórios.

A solução candidata será dividir a execução em fases:

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 180" width="100%">
    {#each [{t:"Endereço",y:25},{t:"ROM",y:65},{t:"Captura",y:105},{t:"Execução",y:145}] as r}
      <text x="2" y={r.y+4} fontSize="11" fill="currentColor">{r.t}</text>
      <path d={`M70 ${r.y} H330`} stroke="currentColor" strokeOpacity=".12" strokeDasharray="3 3"/>
    {/each}
    <g stroke="#94a3b8" strokeDasharray="3 3">
      <path d="M100 5 V165 M180 5 V165 M235 5 V165 M310 5 V165"/>
    </g>
    <path d="M70 35 H95 L105 15 H305 L315 35 H330" fill="none" stroke="#2563eb" strokeWidth="2"/>
    <rect x="100" y="53" width="80" height="24" fill="#d97706" fillOpacity=".2" stroke="#d97706" strokeDasharray="3 2"/>
    <text x="140" y="68" textAnchor="middle" fontSize="9" fill="currentColor">Instável</text>
    <rect x="180" y="53" width="130" height="24" fill="#16a34a" fillOpacity=".15" stroke="#16a34a"/>
    <text x="245" y="68" textAnchor="middle" fontSize="10" fill="currentColor">Válida</text>
    <path d="M70 115 H180 V95 H200 V115 H330" fill="none" stroke="#9333ea" strokeWidth="2"/>
    <path d="M70 155 H235 V135 H310 V155 H330" fill="none" stroke="#0d9488" strokeWidth="2"/>
  </svg>
  <caption>Sequência temporal proposta, sem escala de nanossegundos. Ainda não validada eletricamente.</caption>
</box>

Primeiro selecionamos o endereço, aguardamos a estabilização da ROM, capturamos a palavra de controle e somente depois autorizamos sua execução.

Isso será fundamental para evitar escritas indevidas e conflitos nos barramentos.

## 6. Arquivos produzidos

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap={0}>
      <title size="lg">ISA-1 — Revisão 9.8.1</title>
      <caption>Microsequenciador, quatro ROMs binárias, testes e documentação.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev981.zip)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev981/README.md)
  <divider/>
  **Imagens binárias das memórias de controle**

  <row>
    [ROM 0](sandbox:/mnt/data/isa1_rev981/control_lane0.bin)
    <spacer/>
    <caption>Bits 0–7</caption>
  </row>
  <row>
    [ROM 1](sandbox:/mnt/data/isa1_rev981/control_lane1.bin)
    <spacer/>
    <caption>Bits 8–15</caption>
  </row>
  <row>
    [ROM 2](sandbox:/mnt/data/isa1_rev981/control_lane2.bin)
    <spacer/>
    <caption>Bits 16–23</caption>
  </row>
  <row>
    [ROM 3](sandbox:/mnt/data/isa1_rev981/control_lane3.bin)
    <spacer/>
    <caption>Bits 24–31</caption>
  </row>
</card>

## 7. Próximas etapas

| Subsistema | Situação |
|---|---|
| Microcódigo binário | <icon name="check-circle-2" color="success"/> Testado |
| Geração das ROMs | <icon name="check-circle-2" color="success"/> Implementada |
| Microsequenciador | <icon name="check-circle-2" color="success"/> Modelo lógico testado |
| Registradores físicos | Pendente |
| ALU de 8 bits | Próxima prioridade |
| Incremento e decremento de X e SP | Pendente |
| Proteção física da pilha | Pendente |
| Integração ROM e datapath | Pendente |
| Temporização elétrica | Pendente |

**Limitações desta revisão:** ainda não implementamos os pulsos físicos de controle, a captura da ROM, a integração completa com o barramento e a proteção elétrica. A escolha de quatro EEPROMs e do endereçamento de 13 bits é uma decisão de projeto candidata, não definitiva.

Na próxima etapa, vamos trabalhar na ALU de 8 bits, incluindo somadores, subtração, operações lógicas, deslocamentos e flags, buscando aproveitar os mesmos componentes para diferentes operações.

Mais um marco: **já temos os primeiros binários destinados aos chips que controlarão nossa própria CPU.** 😎

## user — bbb21bf7-f2d6-4d7e-9445-ec45b9c155bb

Esse avanço está sensacional! Vamos continuar

## assistant — 68649073-2ee2-4b9d-9f6d-5f89b9182350

{"content_type": "thoughts", "source_analysis_msg_id": "e6eb8d98-0991-44bc-a672-d7c7f841ad5e", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Inspecionou código, testou ULA e validou integração da ALU"}]}

## assistant — 39dc9d96-34ff-494d-9922-beef391705f0

{"content": "Pensou por 30s", "content_type": "reasoning_recap"}

## assistant — 56cf44ae-2674-405a-aea4-f5df48e0915a

# ISA-1 — Revisão 9.8.2: ALU de 8 bits 😎

Avançamos para um dos componentes mais importantes do nosso processador: a **Unidade Lógica e Aritmética (ALU)**.

Nesta revisão, substituí as operações aritméticas abstratas do modelo de controle por uma implementação booleana baseada em somadores de quatro bits em cascata. Também integrei essa implementação ao simulador existente e executei novos testes.

## 1. Arquitetura da ALU

<box border radius="lg" padding={2}>
  <svg viewBox="0 0 340 320" width="100%">
    {#each [{x:10,y:5,w:140,h:40,t:"Registrador A",s:"8 bits"},{x:190,y:5,w:140,h:40,t:"Registrador B",s:"8 bits"},{x:190,y:65,w:140,h:40,t:"Inversão seletiva",s:"XOR — ADD / SUB"},{x:10,y:130,w:150,h:55,t:"Unidade aritmética",s:"2 somadores de 4 bits"},{x:180,y:130,w:150,h:55,t:"Unidade lógica",s:"AND / OR / XOR / SHIFT"},{x:60,y:210,w:220,h:40,t:"Seletor de resultado",s:"Controlado pelo microcódigo"},{x:10,y:275,w:150,h:38,t:"Resultado",s:"8 bits"},{x:180,y:275,w:150,h:38,t:"Flags",s:"Zero e Carry"}] as r}
      <rect x={r.x} y={r.y} width={r.w} height={r.h} rx="5" stroke="#94a3b8" fill="#64748b" fillOpacity=".12"/>
      <text x={r.x+r.w/2} y={r.y+16} textAnchor="middle" fill="currentColor" fontSize="12" fontWeight="bold">{r.t}</text>
      <text x={r.x+r.w/2} y={r.y+30} textAnchor="middle" fill="currentColor" fontSize="10">{r.s}</text>
    {/each}
    <g fill="none" stroke="#0d9488" strokeWidth="1.5">
      <path d="M80 45 V130 M80 55 H170 V115 H240 V130 M260 45 V65 M310 45 V130 M260 105 V118 H125 V130"/>
      <path d="M85 185 V198 H170 V210 M255 185 V198 H170 M170 250 V262 H85 V275 M170 262 H255 V275"/>
    </g>
  </svg>
  <caption>Organização funcional candidata da ALU do ISA-1.</caption>
</box>

A ideia é compartilhar os mesmos somadores entre as operações de adição, subtração e comparação, economizando componentes.

## 2. Operações implementadas

| Instrução | Operação | Atualiza A | Flags |
|---|---|---|---|
| ADD | A + B | Sim | Z, C |
| SUB | A − B | Sim | Z, C |
| AND | A AND B | Sim | Z |
| OR | A OR B | Sim | Z |
| XOR | A XOR B | Sim | Z |
| SHL | Deslocamento à esquerda | Sim | Z, C |
| SHR | Deslocamento à direita | Sim | Z, C |
| CMP | Comparação A − B | Não | Z, C |

As operações lógicas preservam o valor anterior da flag Carry, conforme o comportamento já definido na nossa ISA.

## 3. Economia de componentes na subtração

Não precisamos construir um subtrator separado.

Utilizando complemento de dois:

\[
A-B=A+\overline{B}+1
\]

Podemos aproveitar os mesmos somadores da instrução ADD, acrescentando portas XOR para inverter seletivamente B.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 175" width="100%">
    {#each [{x:10,t:"74HC283",s:"Bits 0–3"},{x:190,t:"74HC283",s:"Bits 4–7"}] as r}
      <rect x={r.x} y="50" width="140" height="65" rx="5" fill="#2563eb" fillOpacity=".13" stroke="#64748b"/>
      <text x={r.x+70} y="76" textAnchor="middle" fontSize="14" fontWeight="bold" fill="currentColor">{r.t}</text>
      <text x={r.x+70} y="94" textAnchor="middle" fontSize="11" fill="currentColor">{r.s}</text>
    {/each}
    <g stroke="#0d9488" strokeWidth="2" fill="none">
      <path d="M150 83 H190 l-5 -4 m5 4 l-5 4 M80 115 V140 M260 115 V140 M45 25 V50 M115 25 V50 M225 25 V50 M295 25 V50"/>
    </g>
    <g fill="currentColor" fontSize="11" textAnchor="middle">
      <text x="45" y="18">A baixo</text><text x="115" y="18">B baixo</text>
      <text x="225" y="18">A alto</text><text x="295" y="18">B alto</text>
      <text x="170" y="73" fontSize="9">Carry</text>
      <text x="80" y="155">Resultado 0–3</text><text x="260" y="155">Resultado 4–7</text>
    </g>
  </svg>
  <caption>Dois somadores de quatro bits formando um somador de oito bits.</caption>
</box>

Essa mesma estrutura poderá ser aproveitada futuramente para operações de 16 bits realizadas em etapas.

## 4. Bancada interativa da ALU

Você já pode experimentar o comportamento lógico da nossa ALU aqui mesmo.

{@body const [a,setA]=DIL.useState(150)}
{@body const [b,setB]=DIL.useState(120)}
{@body const [op,setOp]=DIL.useState("ADD")}
{@body const [old,setOld]=DIL.useState("0")}
{@body const raw=op==="ADD"?a+b:op==="SUB"||op==="CMP"?a-b:op==="AND"?a&b:op==="OR"?a|b:op==="XOR"?a^b:op==="SHL"?a<<1:a>>1}
{@body const result=raw&255}
{@body const carry=op==="ADD"?Number(raw>255):op==="SUB"||op==="CMP"?Number(a>=b):op==="SHL"?a>>7:op==="SHR"?a&1:Number(old)}
<card gap={3}>
  <row align="center">
    <title size="lg">ISA-1 ALU</title>
    <spacer/>
    <caption>8 bits</caption>
  </row>
  <row>
    **Registrador A**
    <spacer/>
    <text tabularNums={true}>{a} / 0x{a.toString(16).toUpperCase().padStart(2,"0")}</text>
  </row>
  <slider min={0} max={255} step={1} value={a} onChange={setA}/>
  <row gap={1}>
    {#each Array.from({length:8},(_,i)=>(a>>(7-i))&1) as bit}
      <box flex={1} background={bit?"#166534":"surface-tertiary"} radius="sm" padding={2} align="center">
        <text color={bit?"#ffffff":"secondary"} weight="medium">{bit}</text>
      </box>
    {/each}
  </row>
  <row>
    **Registrador B**
    <spacer/>
    <text tabularNums={true}>{b} / 0x{b.toString(16).toUpperCase().padStart(2,"0")}</text>
  </row>
  <slider min={0} max={255} step={1} value={b} onChange={setB}/>
  <row gap={1}>
    {#each Array.from({length:8},(_,i)=>(b>>(7-i))&1) as bit}
      <box flex={1} background={bit?"#166534":"surface-tertiary"} radius="sm" padding={2} align="center">
        <text color={bit?"#ffffff":"secondary"} weight="medium">{bit}</text>
      </box>
    {/each}
  </row>
  <label>Operação</label>
  <grid columns={4} gap={1}>
    {#each ["ADD","SUB","AND","OR","XOR","SHL","SHR","CMP"] as o}
      <grid-item>
        <button block size="md" color={op===o?"primary":"secondary"} variant={op===o?"solid":"outline"} onClick={()=>setOp(o)}>{o}</button>
      </grid-item>
    {/each}
  </grid>
  <label>Carry anterior</label>
  <segmented-control options={[{label:"0",value:"0"},{label:"1",value:"1"}]} value={old} onChange={setOld}/>
  <divider/>
  <caption>Resultado interno da ALU</caption>
  <title size="2xl" tabularNums={true}>{result} / 0x{result.toString(16).toUpperCase().padStart(2,"0")}</title>
  <row gap={1}>
    {#each Array.from({length:8},(_,i)=>(result>>(7-i))&1) as bit}
      <box flex={1} background={bit?"#166534":"surface-tertiary"} radius="sm" padding={2} align="center">
        <text color={bit?"#ffffff":"secondary"} weight="medium">{bit}</text>
      </box>
    {/each}
  </row>
  <grid columns={3}>
    <grid-item>
      <caption>Zero (Z)</caption>
      <title size="xl" color={result===0?"success":"secondary"}>{Number(result===0)}</title>
    </grid-item>
    <grid-item>
      <caption>Carry (C)</caption>
      <title size="xl" color={carry?"success":"secondary"}>{carry}</title>
    </grid-item>
    <grid-item>
      <caption>A após execução</caption>
      <title size="xl">{op==="CMP"?a:result}</title>
    </grid-item>
  </grid>
  <caption>{op==="CMP"?"CMP atualiza as flags sem modificar A.":op==="SUB"?"Na subtração, Carry = 1 indica ausência de empréstimo.":["AND","OR","XOR"].includes(op)?"Operações lógicas preservam Carry.":["SHL","SHR"].includes(op)?"O bit descartado é transferido para Carry.":"Resultados superiores a 255 geram Carry."}</caption>
</card>

## 5. Validação exaustiva

Desta vez, consegui testar todas as combinações possíveis de A, B, operação e estado anterior de Carry.

\[
256\times256\times8\times2
=1.048.576
\]

<box border radius="lg" padding={3} gap={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.048.576</title>
      <caption>Combinações da ALU verificadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">100%</title>
      <caption>Cobertura das combinações de entrada</caption>
    </grid-item>
    <grid-item>
      <title size="2xl">8/8</title>
      <caption>Operações verificadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Falhas nas asserções</caption>
    </grid-item>
  </grid>
  <divider/>
  **Todos os testes executados passaram.**
</box>

Além disso, integrei a nova ALU ao modelo da CPU e executei as bancadas de regressão.

| Validação | Casos | Falhas |
|---|---:|---:|
| ALU exaustiva | 1.048.576 | 0 |
| Comparação entre CPUs | 6.656 | 0 |
| Reset de instruções | 2.546 | 0 |
| Programas integrados | 2 | 0 |
| **Total** | **1.057.780** | **0** |

## 6. Componentes candidatos

| CI | Quantidade preliminar | Função |
|---|---:|---|
| 74HC283 | 2 | Somadores |
| 74HC86 | 2 | Inversão seletiva de B |
| 74HC86 | A definir | Operação XOR |
| 74HC08 | A definir | Operação AND |
| 74HC32 | A definir | Operação OR |
| Multiplexadores | A definir | Seleção do resultado |
| Portas auxiliares | A definir | Detecção de zero |
| Flip-flops | A definir | Armazenamento das flags |

Todos esses componentes são candidatos à implementação com lógica discreta. Ainda vamos otimizar a quantidade total e confirmar as versões disponíveis em encapsulamento SOIC.

## 7. Evolução da implementação física

<box border radius="lg" padding={3} gap={3}>
  {#each [{n:"Palavras de controle",s:"Modelo testado",ok:true},{n:"ROMs de microcódigo",s:"Binários gerados",ok:true},{n:"Microsequenciador",s:"Modelo testado",ok:true},{n:"ALU de 8 bits",s:"Modelo booleano validado exaustivamente",ok:true},{n:"Registradores A e B",s:"Circuito pendente",ok:false},{n:"PC de 16 bits",s:"Circuito parcial definido",ok:false},{n:"SP de 16 bits",s:"Próxima etapa",ok:false},{n:"X de 16 bits",s:"Próxima etapa",ok:false},{n:"Barramentos físicos",s:"Pendente",ok:false},{n:"Integração eletrônica",s:"Pendente",ok:false}] as item}
    <row align="center">
      <icon name={item.ok?"check-circle-2":"circle"} color={item.ok?"success":"secondary"} size="lg"/>
      <box gap={0}>
        **{item.n}**
        <caption>{item.s}</caption>
      </box>
    </row>
  {/each}
</box>

## 8. Arquivos produzidos

<card gap={3}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      <title size="lg">ISA-1 — Revisão 9.8.2</title>
      <caption>Código atualizado, modelo booleano da ALU, ROMs e bancadas.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev982.zip)

  [Código da ALU e teste exaustivo](sandbox:/mnt/data/isa1_rev982/alu_gates.py)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev982/README.md)
</card>

**Limitações desta revisão:** o modelo utiliza portas booleanas ideais, não reproduz a topologia interna exata do 74HC283 nem seus atrasos de propagação. A pinagem, os multiplexadores físicos, o consumo e a frequência máxima ainda precisam ser validados. As ROMs anteriores foram preservadas sem alterações.

## 9. Próximas revisões

| Revisão | Objetivo |
|---|---|
| 9.8.2.1 | Otimização dos multiplexadores da ALU |
| 9.8.2.2 | Circuito físico das flags |
| 9.8.3 | Registradores e contador de programa |
| 9.8.4 | Incremento e decremento de X e SP |
| 9.8.5 | Proteção contra estouro da pilha |
| 9.8.6 | Integração do datapath |
| 9.8.7 | Unidade de controle física |
| 9.8.8 | Arbitragem dos barramentos |
| 9.8.9 | Modelos Verilog integrados |

Mais um marco importante: **a ALU do ISA-1 agora possui um modelo booleano integrado à CPU e testado em todas as combinações possíveis de entrada.**

Estamos aproximando cada vez mais nosso processador dos componentes que efetivamente vamos soldar na placa. 😎

## user — bbb2167c-d595-4733-96c7-1e5e824e5d6e

Uma pausa aqui, vc consegue gerar uma imagem preview 3d de como vai ficar mais ou menos a placa e o teclado? Quero apresentar o projeto aqui pra uma pessoa

## user — bbb21930-f754-46e7-98b0-c790b650cbda

Agora pode seguir seguir com as análises

## assistant — 84be72d7-0be6-477f-9fff-047c39661d42

{"content_type": "thoughts", "source_analysis_msg_id": "ef83eaa8-e06a-4f3d-8bea-e64e2063c0bd", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Testou datapath e ALU, atualizou README e compactou revisão 9.8.3"}]}

## assistant — 1ff83e31-bc90-4164-9c54-91e9e7d725f3

{"content": "Pensou por 48s", "content_type": "reasoning_recap"}

## assistant — c616bdef-9ccd-4bf6-9bb5-efa8b7513835

# ISA-1 — Revisão 9.8.2.1: otimização da ALU

Retomando exatamente de onde paramos antes da apresentação visual, reabri o código da ALU e das palavras de controle.

Identifiquei uma oportunidade de reduzir componentes: ADD, SUB e CMP podem compartilhar a mesma saída aritmética. Os deslocamentos SHL e SHR, por sua vez, podem ser realizados por conexões fixas entre os bits, sem precisar de um circuito deslocador dedicado.

Vamos aproveitar essas características para reduzir a quantidade de CIs, preservando as oito operações da ALU e o comportamento das flags.

## 1. Seleção das operações da ALU

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 265" width="100%">
    {#each [{t:"ADD / SUB / CMP",s:"Somadores compartilhados"},{t:"AND",s:"Portas AND"},{t:"OR",s:"Portas OR"},{t:"XOR",s:"Portas XOR"},{t:"SHL",s:"Conexões fixas"},{t:"SHR",s:"Conexões fixas"}] as r,i}
      <rect x="5" y={5+i*43} width="140" height="35" rx="4" fill="#64748b" fillOpacity=".12" stroke="#94a3b8"/>
      <text x="75" y={19+i*43} fontSize="11" fontWeight="bold" fill="currentColor" textAnchor="middle">{r.t}</text>
      <text x="75" y={32+i*43} fontSize="9" fill="currentColor" textAnchor="middle">{r.s}</text>
      <path d={`M145 ${22+i*43} H190`} stroke="#0d9488" strokeWidth="1.5"/>
    {/each}
    <path d="M190 5 L250 65 V195 L190 260 Z" fill="#2563eb" fillOpacity=".15" stroke="#64748b"/>
    <text x="220" y="125" fontSize="12" fill="currentColor" textAnchor="middle">MUX</text>
    <text x="220" y="141" fontSize="10" fill="currentColor" textAnchor="middle">8:1</text>
    <path d="M250 130 H330" stroke="#0d9488" strokeWidth="2"/>
    <text x="292" y="120" fontSize="10" fill="currentColor" textAnchor="middle">Resultado</text>
    <text x="292" y="145" fontSize="10" fill="currentColor" textAnchor="middle">8 bits</text>
  </svg>
  <caption>Seis fontes de resultado para oito operações. O seletor é replicado para cada bit.</caption>
</box>

Uma implementação candidata utiliza oito multiplexadores 74HC151, um para cada bit do resultado.

| Componente | Quantidade |
|---|---:|
| 74HC283 — somadores | 2 |
| 74HC86 — inversão seletiva | 2 |
| 74HC86 — XOR lógico | 2 |
| 74HC08 — AND | 2 |
| 74HC32 — OR | 2 |
| 74HC151 — seleção | 8 |
| **Subtotal** | **18 CIs** |

Esse subtotal ainda não inclui a decodificação da operação, as flags e os registradores. Não é uma BOM definitiva.

## 2. Revisão 9.8.2.2 — Flags

Mantive as duas flags originais do ISA-1.

| Operação | Zero (Z) | Carry (C) |
|---|---|---|
| ADD | Resultado igual a zero | Carry do somador |
| SUB e CMP | Resultado igual a zero | Ausência de empréstimo |
| AND, OR e XOR | Resultado igual a zero | Preservado |
| SHL | Resultado igual a zero | Bit 7 anterior |
| SHR | Resultado igual a zero | Bit 0 anterior |

A flag Zero pode ser implementada por uma redução NOR dos oito bits do resultado. Para armazenar as duas flags, um 74HC74 é um candidato, acompanhado da lógica de habilitação.

O modelo booleano atualizado foi comparado exaustivamente com a ALU da revisão anterior.

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>1.048.576</title>
      <caption>Combinações verificadas</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Divergências encontradas</caption>
    </grid-item>
  </grid>
</box>

## 3. Revisão 9.8.3 — Incremento e decremento de 16 bits

Precisamos dessas operações principalmente para os registradores X e SP.

Implementei um modelo utilizando quatro somadores de quatro bits em cascata.

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 150" width="100%">
    <text x="170" y="14" textAnchor="middle" fill="currentColor" fontSize="12">Entrada de 16 bits</text>
    {#each [0,1,2,3] as i}
      <path d={`M${43+i*85} 22 V45 M${43+i*85} 100 V122`} stroke="#94a3b8"/>
      <rect x={5+i*85} y="45" width="75" height="55" rx="4" stroke="#64748b" fill="#2563eb" fillOpacity=".15"/>
      <text x={42+i*85} y="67" fill="currentColor" textAnchor="middle" fontSize="11" fontWeight="bold">74HC283</text>
      <text x={42+i*85} y="84" fill="currentColor" textAnchor="middle" fontSize="10">Bits {i*4}–{i*4+3}</text>
      {#if i<3}
        <path d={`M${80+i*85} 73 h10 l-4 -3 m4 3 l-4 3`} stroke="#0d9488" strokeWidth="2" fill="none"/>
      {/if}
    {/each}
    <text x="170" y="140" textAnchor="middle" fill="currentColor" fontSize="12">Resultado de 16 bits</text>
  </svg>
</box>

Para incrementar, somamos `0001h`. Para decrementar, somamos `FFFFh`, descartando o carry final.

Testei todos os 65.536 valores possíveis nas duas operações.

| Entrada | Incremento | Decremento |
|---|---|---|
| `0000h` | `0001h` | `FFFFh` |
| `00FFh` | `0100h` | `00FEh` |
| `0100h` | `0101h` | `00FFh` |
| `7FFFh` | `8000h` | `7FFEh` |
| `FFFFh` | `0000h` | `FFFEh` |

**131.072 casos testados, sem divergências.**

O comportamento circular é válido para X, mas SP deverá possuir proteção adicional contra estouro e esvaziamento indevido da pilha.

Também existe a possibilidade de compartilhar esses quatro somadores entre X e SP, desde que o endereço calculado permaneça estável durante WAIT.

## 4. Resultado consolidado desta rodada

<box border radius="lg" padding={3} gap={3}>
  <title size="2xl" tabularNums>1.179.648</title>
  <caption>Combinações efetivamente testadas nesta revisão</caption>
  <box gap={1}>
    <row>
      <text size="sm">ALU e flags combinacionais</text>
      <spacer/>
      <text size="sm" tabularNums>1.048.576</text>
    </row>
    <box height={9} radius="sm" background="surface-tertiary" clip>
      <box background="#16a34a" width="88.89%" height={9}/>
    </box>
    <row>
      <text size="sm">Incremento e decremento</text>
      <spacer/>
      <text size="sm" tabularNums>131.072</text>
    </row>
    <box height={9} radius="sm" background="surface-tertiary" clip>
      <box background="#16a34a" width="11.11%" height={9}/>
    </box>
  </box>
  <divider/>
  <row align="center">
    <icon name="check-circle-2" color="success" size="xl"/>
    **Nenhuma divergência encontrada.**
  </row>
</box>

## 5. Características preservadas

Aproveitei também para registrar na documentação que a imagem 3D que geramos é conceitual, não uma representação definitiva da placa.

Continuamos com as especificações reais do ISA-1:

| Característica | Especificação |
|---|---|
| CPU | Própria, lógica discreta de 8 bits |
| Endereçamento | 16 bits |
| Componentes lógicos | SMD, preferencialmente SOIC |
| RAM | 32 KiB |
| VRAM | 32 KiB |
| EEPROM removível | 32 KiB, soquete ZIF |
| Vídeo | VGA, 160 × 120 pixels lógicos |
| Cores | RGB332, 256 cores |
| Teclado | Quatro módulos de membrana 4 × 4 |
| Alimentação | USB-C, 5 V |
| Placa | PCB principal única |
| Microcontroladores na CPU | Nenhum |

## 6. Arquivos atualizados

<card gap={2}>
  <row align="center">
    <icon name="file-archive" size="3xl"/>
    <box gap=0>
      **ISA-1 — Revisão 9.8.3**
      <caption>Modelos booleanos, código anterior preservado, testes e documentação.</caption>
    </box>
  </row>
  [Baixar pacote completo (.zip)](sandbox:/mnt/data/ISA-1_rev983.zip)

  [Código dos novos circuitos lógicos](sandbox:/mnt/data/isa1_rev983/datapath_blocks.py)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev983/README.md)

  [Resultados dos testes](sandbox:/mnt/data/isa1_rev983/blocks_results.txt)
</card>

## 7. Próximas etapas

| Etapa | Situação |
|---|---|
| ALU booleana | <icon name="check-circle-2" color="success"/> Testada |
| Seleção de resultados | <icon name="check-circle-2" color="success"/> Testada |
| Flags combinacionais | <icon name="check-circle-2" color="success"/> Testadas |
| Aritmética de 16 bits | <icon name="check-circle-2" color="success"/> Testada |
| Armazenamento físico das flags | Pendente |
| Compartilhamento dos somadores | Em análise |
| Registradores X e SP | Pendente |
| Proteção da pilha | Pendente |
| Datapath integrado | Pendente |
| Verilog | Pendente |
| Esquemático | Pendente |

**Limitações:** os novos blocos foram testados isoladamente, ainda não foram integrados à CPU. A redução de componentes é uma proposta, não uma economia comprovada em relação a um esquemático completo. Também não houve validação de pinagem ou temporização elétrica.

Na próxima revisão, a prioridade será fechar os circuitos dos registradores e verificar se conseguimos compartilhar os somadores de 16 bits. Quanto mais componentes conseguirmos compartilhar sem comprometer a confiabilidade, mais econômica e fácil de montar será nossa placa. 😎

## user — bbb21bb7-a45c-4c70-aec8-af306b917af0

Boa vamos seguir com a análise dos componentes

## assistant — a028b2c2-110f-4aae-a733-098c2fd6586b

{"content_type": "thoughts", "source_analysis_msg_id": "c6e63601-0274-4860-a889-2338167465bc", "thoughts": [{"chunks": [], "content": "", "finished": true, "summary": "Listou arquivos e inspecionou o datapath"}]}

## assistant — 2ffcb3a4-2e41-4935-9591-c0cc1284e771

{"content": "Pensou por 10s", "content_type": "reasoning_recap"}

## assistant — b2e58176-e5c3-4f56-8f5b-a56a24690dfa

# ISA-1 — Revisão 9.8.4: análise e otimização dos componentes

Agora vamos trabalhar com três objetivos simultâneos: reduzir o custo da placa, diminuir a quantidade de CIs que precisaremos soldar e preservar a confiabilidade do computador.

Como nossa PCB será montada manualmente, continuaremos priorizando componentes SMD com encapsulamento SOIC, alimentação de 5 V e lógica das famílias 74HC e 74HCT.

## 1. Registradores internos da CPU

A organização atual exige os seguintes registradores:

| Registrador | Largura | Função |
|---|---:|---|
| A | 8 bits | Acumulador |
| B | 8 bits | Operando da ALU |
| X | 16 bits | Endereçamento indireto |
| PC | 16 bits | Contador de programa |
| SP | 16 bits | Ponteiro da pilha |
| EA | 16 bits | Endereço efetivo |
| RET | 16 bits | Endereço de retorno temporário |
| IR | 8 bits | Instrução atual |
| MDR | 8 bits | Dados da memória |
| FLAGS | 2 bits | Zero e Carry |
| **Total** | **114 bits** | |

Isso não inclui os registradores de microcódigo, vídeo e periféricos.

Uma das oportunidades de otimização é compartilhar circuitos aritméticos entre X e SP, mantendo o armazenamento dos dois registradores independente.

## 2. Seleção preliminar dos registradores

Para os registradores que precisam manter seus valores durante ciclos de espera, o 74HC377 é um candidato interessante, pois possui habilitação de carga.

| Registrador | CI candidato | Quantidade |
|---|---|---:|
| A | 74HC377 | 1 |
| B | 74HC377 | 1 |
| X | 74HC377 | 2 |
| PC | 74HC163 | 4 |
| SP | 74HC377 | 2 |
| EA | 74HC377 | 2 |
| RET | 74HC377 | 2 |
| IR | 74HCT377 | 1 |
| MDR | 74HCT377 | 1 |
| FLAGS | 74HC74 | 1 |
| **Total** | | **17 CIs** |

A escolha da família HCT para IR e MDR é candidata devido à necessidade de compatibilidade com os níveis de saída das memórias.

Ainda precisaremos adicionar multiplexadores, buffers e circuitos de inicialização. O 74HC377, por exemplo, não possui reset dedicado.

## 3. Compartilhamento dos somadores de 16 bits

Temos duas alternativas para X e SP.

<grid columns={2}>
  <grid-item>
    <card gap={2}>
      **Circuitos independentes**
      <svg viewBox="0 0 150 180" width="100%">
        {#each [5,80] as x,i}
          <rect x={x} y="5" width="65" height="32" rx="4" stroke="#94a3b8" fill="#64748b" fillOpacity=".15"/>
          <text x={x+32.5} y="25" fontSize="13" textAnchor="middle" fill="currentColor">{i?"SP":"X"}</text>
          <path d={`M${x+32.5} 37 V65`} stroke="#94a3b8"/>
          <rect x={x} y="65" width="65" height="55" rx="4" stroke="#94a3b8" fill="#2563eb" fillOpacity=".15"/>
          <text x={x+32.5} y="85" fontSize="11" textAnchor="middle" fill="currentColor">4 × 283</text>
          <text x={x+32.5} y="102" fontSize="10" textAnchor="middle" fill="currentColor">16 bits</text>
          <path d={`M${x+32.5} 120 V145 H${x+4} V37`} stroke="#0d9488" fill="none"/>
        {/each}
      </svg>
      <title size="2xl">8 CIs</title>
      <caption>Somadores dedicados.</caption>
    </card>
  </grid-item>
  <grid-item>
    <card gap={2}>
      **Circuito compartilhado**
      <svg viewBox="0 0 150 180" width="100%">
        {#each [5,80] as x,i}
          <rect x={x} y="5" width="65" height="32" rx="4" stroke="#94a3b8" fill="#64748b" fillOpacity=".15"/>
          <text x={x+32.5} y="25" fontSize="13" textAnchor="middle" fill="currentColor">{i?"SP":"X"}</text>
          <path d={`M${x+32.5} 37 V50 H75 V65`} stroke="#94a3b8" fill="none"/>
        {/each}
        <rect x="25" y="65" width="100" height="32" rx="4" stroke="#94a3b8" fill="#d97706" fillOpacity=".15"/>
        <text x="75" y="85" fontSize="11" textAnchor="middle" fill="currentColor">4 × 157</text>
        <path d="M75 97 V110" stroke="#94a3b8"/>
        <rect x="25" y="110" width="100" height="45" rx="4" stroke="#94a3b8" fill="#2563eb" fillOpacity=".15"/>
        <text x="75" y="128" fontSize="11" textAnchor="middle" fill="currentColor">4 × 283</text>
        <text x="75" y="143" fontSize="10" textAnchor="middle" fill="currentColor">16 bits</text>
      </svg>
      <title size="2xl">8 CIs</title>
      <caption>Somadores + multiplexadores.</caption>
    </card>
  </grid-item>
</grid>

Aqui encontramos um detalhe importante: compartilhar os somadores não necessariamente reduz a quantidade de componentes.

Economizamos quatro somadores, mas acrescentamos quatro multiplexadores de quatro bits. Também aumentamos o caminho de propagação dos sinais.

Portanto, minha preferência preliminar é manter os circuitos independentes, a menos que encontremos uma alternativa realmente mais econômica.

## 4. Alternativa ainda mais interessante

Podemos investigar o **74HC193**, contador binário de quatro bits com incremento, decremento e carga paralela.

| Solução | Quantidade para X e SP* |
|---|---:|
| Registradores e somadores independentes | 12 CIs |
| Registradores e somadores compartilhados | 12 CIs |
| Contadores 74HC193 | 8 CIs |

<caption>* Subtotal dos blocos principais, sem portas auxiliares, seleção de dados e proteção.</caption>

<row align="start">
  <AsyncImage query="74HC193 SOIC 16 surface mount integrated circuit" aspectRatio="1:1" maxWidth="100px" fit="contain"/>
  <box gap={1}>
    **74HC193**

    Contador binário de quatro bits bidirecional, com carga paralela e saídas para encadeamento.
  </box>
</row>

Essa alternativa merece atenção, mas possui uma desvantagem: utiliza entradas separadas de clock para incremento e decremento. Precisaremos analisar cuidadosamente os pulsos, o encadeamento e a estabilidade dos endereços durante acessos à memória.

Não vamos substituir os registradores atuais antes dessa validação.

## 5. Inventário preliminar do ISA-1

Consolidando os principais blocos que já discutimos:

| Subsistema | CIs previstos |
|---|---:|
| Registradores da CPU | 17 |
| ALU de 8 bits | 18 |
| Aritmética de X e SP | 8 |
| Multiplexadores do PC | 4 |
| Memórias de microcódigo | 4 |
| Registradores de microcódigo | 4 |
| Microsequenciador e estados | 2 |
| Contadores VGA | 5 |
| Multiplexadores VRAM | 4 |
| RAM, VRAM e EEPROM removível | 3 |
| **Subtotal preliminar** | **69** |

<box border radius="lg" padding={3} gap={2}>
  <title>Distribuição dos componentes já estimados</title>
  {#each [{n:"ALU e aritmética",v:26,c:"#0d9488"},{n:"Registradores e PC",v:21,c:"#2563eb"},{n:"Unidade de controle",v:10,c:"#9333ea"},{n:"Controlador VGA",v:9,c:"#d97706"},{n:"Memórias principais",v:3,c:"#64748b"}] as r}
    <row>
      <text size="sm">{r.n}</text>
      <spacer/>
      **{r.v}**
    </row>
    <box height={9} radius="sm" background="surface-tertiary" clip>
      <box height={9} radius="sm" background={r.c} width={`${r.v/69*100}%`}/>
    </box>
  {/each}
  <caption>Inventário parcial, não representa a quantidade definitiva de componentes da PCB.</caption>
</box>

Ainda faltam os circuitos de teclado, alimentação, reset, decodificação de memória, arbitragem, buffers, saída VGA e diversas portas auxiliares.

## 6. Padronização dos componentes

Quero evitar que nossa placa utilize dezenas de modelos diferentes de CIs.

| Família | Função |
|---|---|
| 74HC00 | NAND |
| 74HC02 | NOR |
| 74HC04 | Inversores |
| 74HC08 | AND |
| 74HC32 | OR |
| 74HC74 | Flip-flops |
| 74HC86 | XOR |
| 74HC138 | Decodificação |
| 74HC151 | Multiplexação 8:1 |
| 74HC157 | Multiplexação 2:1 |
| 74HC163 | Contadores síncronos |
| 74HC193 | Contadores bidirecionais — candidato |
| 74HCT245 | Interface de barramento |
| 74HC283 | Somadores |
| 74HC377 | Registradores |
| 74HCT574 | Registradores e interfaces |

A padronização facilitará a compra, a soldagem, a manutenção e a substituição de componentes.

## 7. Próximas validações

- Comparar 74HC193 com 74HC377 + 74HC283.
- Definir a inicialização física de SP em `8000h`.
- Implementar a proteção contra estouro da pilha.
- Dimensionar os buffers dos barramentos.
- Conferir datasheets, pinagens e encapsulamentos.
- Integrar os circuitos ao datapath.
- Consolidar a lista de materiais (BOM).

**Situação desta revisão:** reabri o código da revisão 9.8.3 e realizei a análise arquitetural e a contagem preliminar dos componentes. Não executei novas bancadas nesta rodada, nem confirmei disponibilidade comercial, pinagens ou temporização dos novos candidatos.

O próximo ponto mais promissor é investigar os contadores bidirecionais. Se conseguirmos utilizá-los com segurança, poderemos simplificar consideravelmente os circuitos de X e SP, sem perder nenhuma funcionalidade do ISA-1.

## user — bbb21130-e035-4178-adc0-ea9046224aee

Ia te perguntar isso, mas vc já fez
Levantar todos os 74HC que tem kkk pra já ter uma ideia de quais são bons usar pra gente
Boa, pode ir pro próximo passo

## assistant — 029256e3-bf4f-4df6-8bb7-31c953a575c8

Kkkkk estamos pensando na mesma direção! 😎 Conhecer bem o catálogo da família 74HC pode nos poupar dezenas de componentes. Não faz sentido construir um circuito com várias portas lógicas se já existe um CI que realiza exatamente aquela função.

# ISA-1 — Revisão 9.8.4.1: seleção inteligente dos CIs

Vamos aprofundar a análise das famílias 74HC e 74HCT, principalmente dos componentes que podem substituir blocos inteiros da nossa arquitetura.

## 1. Encontramos um candidato melhor: 74HC191

Além do 74HC193, encontrei no catálogo da Texas Instruments o 74HC191. Ele possui uma característica particularmente interessante para nossa arquitetura: utiliza um único clock, com seleção da direção de contagem e habilitação.

Isso combina melhor com nosso sistema de WAIT e com a necessidade de manter os registradores estáveis durante acessos à memória. <Cite refs={["turn804215search1","turn804215search0"]}/>

| Característica | 74HC191 | 74HC193 |
|---|---|---|
| Capacidade | 4 bits | 4 bits |
| Incremento | Sim | Sim |
| Decremento | Sim | Sim |
| Entradas de clock | Uma | Duas |
| Habilitação de contagem | Dedicada | Controle dos pulsos |
| Carga paralela | Assíncrona | Assíncrona |
| Reset dedicado | Não | Sim |
| Propagação típica | 13 ns | 20 ns |
| Versão SOIC-16 | Sim | Sim |
| Preferência para X e SP | Principal candidato | Alternativa |

Os tempos apresentados são típicos de catálogo, não limites garantidos para nosso circuito completo.

## 2. Nova proposta para X e SP

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 255" width="100%">
    {#each [0,1] as r}
      <text x="170" y={15+r*130} textAnchor="middle" fontWeight="bold" fontSize="13" fill="currentColor">{r===0?"Registrador X":"Registrador SP"}</text>
      {#each [0,1,2,3] as i}
        <rect x={5+i*85} y={42+r*130} width="75" height="48" rx="4" fill="#2563eb" fillOpacity=".14" stroke="#94a3b8"/>
        <text x={42+i*85} y={61+r*130} textAnchor="middle" fill="currentColor" fontSize="11">74HC191</text>
        <text x={42+i*85} y={77+r*130} textAnchor="middle" fill="currentColor" fontSize="10">{i*4}–{i*4+3}</text>
        <path d={`M${42+i*85} ${30+r*130} v12 M${42+i*85} ${90+r*130} v15`} stroke="#94a3b8"/>
        {#if i<3}
          <path d={`M${80+i*85} ${65+r*130} h10`} stroke="#0d9488" strokeWidth="2"/>
        {/if}
      {/each}
      <path d={`M5 ${30+r*130} H335`} stroke="#0d9488" strokeWidth="1.5"/>
      <text x="170" y={118+r*130} fontSize="10" textAnchor="middle" fill="currentColor">Saída de 16 bits</text>
    {/each}
  </svg>
  <caption>Oito contadores de quatro bits. Diagrama funcional; a lógica de habilitação em cascata ainda precisa ser definida.</caption>
</box>

<grid columns={2}>
  <grid-item>
    <card gap={1}>
      <caption>Arquitetura anterior</caption>
      <title size="2xl">12 CIs</title>
      Registradores e somadores
    </card>
  </grid-item>
  <grid-item>
    <card gap={1}>
      <caption>Nova arquitetura candidata</caption>
      <title size="2xl" color="success">8 CIs</title>
      Contadores bidirecionais
    </card>
  </grid-item>
</grid>

Uma redução potencial de **33,3%** nesses dois blocos, antes de contabilizar a lógica auxiliar.

## 3. Testes de encadeamento dos contadores

Criei um modelo de quatro contadores de quatro bits com clock comum e habilitação individual.

Cada contador superior somente avança quando todos os inferiores atingem seu limite: `Fh` no incremento ou `0h` no decremento.

Testei todos os valores de 16 bits, nas duas direções, com a contagem habilitada e desabilitada.

<box border radius="lg" padding={3}>
  <grid columns={2}>
    <grid-item>
      <title size="2xl" tabularNums>262.144</title>
      <caption>Combinações de contagem</caption>
    </grid-item>
    <grid-item>
      <title size="2xl" color="success">0</title>
      <caption>Divergências</caption>
    </grid-item>
  </grid>
</box>

## 4. Encontramos uma particularidade importante na pilha

Não podemos substituir imediatamente o circuito de SP pelo contador.

Na instrução PUSH, precisamos calcular o endereço `SP − 1` antes de realizar a escrita, mas somente atualizar SP após a confirmação da operação.

O contador sozinho não disponibiliza simultaneamente esses dois valores.

Temos três alternativas:

| Alternativa | Avaliação |
|---|---|
| Manter somadores em SP | Preserva o microcódigo atual |
| Decrementar SP antes da escrita | Exige revisão do controle |
| Criar endereço temporário | Exige lógica adicional |

Por enquanto, considero o 74HC191 especialmente promissor para X. Para SP, vamos preservar o circuito anterior até resolvermos essa questão.

Não quero economizar quatro chips e acabar comprometendo a confiabilidade da pilha.

## 5. Proteção contra estouro da pilha

Também implementei e executei uma bancada de proteção dos endereços.

| Condição | Comportamento |
|---|---|
| Reset | SP inicializado em `8000h` |
| Primeiro PUSH | Escrita em `7FFFh` |
| POP com pilha vazia | Bloqueado |
| PUSH abaixo da RAM | Bloqueado |
| PUSH sobre área protegida de boot | Bloqueado |
| X ultrapassando `FFFFh` | Retorna a `0000h` |

<box border radius="lg" padding={3}>
  <svg viewBox="0 0 340 145" width="100%">
    <rect x="65" y="10" width="210" height="28" fill="#64748b" fillOpacity=".15" stroke="#94a3b8"/>
    <text x="170" y="28" textAnchor="middle" fontSize="11" fill="currentColor">8000h — Pilha vazia</text>
    <rect x="65" y="38" width="210" height="42" fill="#0d9488" fillOpacity=".17" stroke="#94a3b8"/>
    <text x="170" y="55" textAnchor="middle" fontSize="11" fill="currentColor">7FFFh — Primeiro PUSH</text>
    <text x="170" y="70" textAnchor="middle" fontSize="10" fill="currentColor">Pilha descendente</text>
    <rect x="65" y="80" width="210" height="52" fill="#d97706" fillOpacity=".15" stroke="#94a3b8"/>
    <text x="170" y="99" textAnchor="middle" fontSize="11" fill="currentColor">0000h–3FFFh</text>
    <text x="170" y="114" textAnchor="middle" fontSize="10" fill="currentColor">Protegida durante o boot</text>
    <path d="M45 40 V77 l-5 -7 m5 7 l5 -7" stroke="#0d9488" strokeWidth="2" fill="none"/>
    <text x="30" y="57" textAnchor="middle" fontSize="9" fill="currentColor">PUSH</text>
  </svg>
  <caption>Organização da pilha. Representação sem escala. A proteção não impede colisões com programas e dados dentro da RAM permitida.</caption>
</box>

Foram testadas mais **262.144 combinações**, sem falhas nas asserções.

## 6. Catálogo estratégico de componentes

Além dos componentes já levantados, estes merecem entrar na nossa lista de investigação.

| CI | Função | Possível aplicação |
|---|---|---|
| 74HC30 | NAND de 8 entradas | Detecção de zero |
| 74HC688 | Comparador de 8 bits | Proteção e endereçamento |
| 74HC85 | Comparador de magnitude | Limites da pilha |
| 74HC191 | Contador bidirecional | X e SP |
| 74HC153 | Dois multiplexadores 4:1 | Barramentos |
| 74HC154 | Decodificador 4:16 | Controle e periféricos |
| 74HC139 | Dois decodificadores 2:4 | Seleção de registradores |
| 74HC238 | Decodificador 3:8 | Controle do datapath |
| 74HC259 | Latch endereçável | Configuração de periféricos |
| 74HC165 | Registrador paralelo-serial | Interfaces seriais |
| 74HC595 | Registrador serial-paralelo | Expansão de saídas |
| 74HC670 | Banco de registradores 4 × 4 | Armazenamento interno |
| 74HC14 | Inversor Schmitt trigger | Condicionamento de sinais |
| 74HC03 | NAND com dreno aberto | Teclado matricial |
| 74HC541 | Buffer octal | Barramento de endereços |
| 74HC273 | Registrador octal com reset | Registradores internos |
| 74HC299 | Registrador universal | Operações de deslocamento |

Essa é uma seleção funcional de candidatos, não um catálogo exaustivo. A disponibilidade em SOIC e a situação de fabricação de cada modelo ainda precisam ser conferidas.

Referências para nossa pesquisa:

- [Catálogo de circuitos lógicos da Nexperia](https://www.nexperia.com/products/analog-logic-ics/logic)
- [Guia de seleção de componentes Nexperia](https://assets.nexperia.com/documents/selection-guide/Nexperia_Selection_Guide_2025.pdf)
- [Datasheet do SN74HC191](https://www.ti.com/lit/ds/symlink/sn74hc191.pdf)

## 7. Resultados desta revisão

<card gap={2}>
  <caption>Total de combinações testadas</caption>
  <title size="2xl" tabularNums>524.288</title>
  <row>
    <icon name="check-circle-2" color="success"/>
    Nenhuma falha nas asserções
  </row>
  <divider/>
  [Pacote incremental da revisão 9.8.4.1](sandbox:/mnt/data/ISA-1_rev984.zip)

  [Documentação técnica](sandbox:/mnt/data/isa1_rev984/README.md)

  [Código da bancada de testes](sandbox:/mnt/data/isa1_rev984/counter.py)

  [Resultados da execução](sandbox:/mnt/data/isa1_rev984/results.txt)
</card>

Os testes foram realizados em modelos lógicos ideais e isolados. Ainda não validam a temporização elétrica nem a integração desses contadores à CPU.

## 8. Próximas prioridades

| Revisão | Objetivo |
|---|---|
| 9.8.4.2 | Circuito de carga e inicialização dos contadores |
| 9.8.4.3 | Resolver o pré-decremento de SP |
| 9.8.5 | Implementar a proteção física da pilha |
| 9.8.6 | Otimizar os barramentos e registradores |
| 9.8.7 | Integrar o datapath |
| 9.8.8 | Consolidar a lógica de controle |
| 9.8.9 | Modelos Verilog |

Estou particularmente interessado no 74HC688, no 74HC153 e no 74HC670. São componentes que merecem uma análise mais profunda pelo potencial de simplificação da nossa arquitetura.

Nossa filosofia será utilizar a inteligência que já existe dentro da família 74HC para construir o ISA-1, sem precisar reinventar cada circuito com portas individuais e sem abrir mão de nenhuma funcionalidade. 😎
