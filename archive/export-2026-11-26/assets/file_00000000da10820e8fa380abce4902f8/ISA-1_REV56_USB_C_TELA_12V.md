# ISA-1 — Revisão 5.6 — USB-C 5 V e tela RCA 12 V com alimentação alternativa

## Decisões
- Entrada principal USB-C de 5 V, sem pressupor que o carregador Motorola de 33 W fornece 3 A a 5 V. Confirmar etiqueta e tipo de cabo. Resistores Rd individuais de 5,1 kΩ em CC1 e CC2 identificam consumidor USB-C, **não** negociam USB-PD nem garantem 3 A. Para consumir acima da corrente padrão, detectar corretamente a corrente anunciada pelo provedor USB-C ou negociar por controlador adequado. Não habilitar boost de alta potência sem orçamento autorizado.
- Barramento `5V_SYS` alimenta lógica e supervisor; ramo protegido `5V_BOOST_IN` alimenta conversor boost para `12V_DISPLAY`.
- A tela terá conector separado com pinos `12V_DISPLAY`, `GND_DISPLAY`, `CVBS`, `VIDEO_GND` conforme modelo exato. Não assumir pinagem da tela automotiva não identificada.
- Prever conector de alimentação **externa de 12 V para a tela**, com seleção física mutuamente exclusiva entre `12V_BOOST` e `12V_EXT`. Preferir jumper de 3 pinos ou chave break-before-make devidamente dimensionada, sem conectar as duas fontes em paralelo. Considerar retorno de terra de vídeo e laços de terra; não conectar terras por caminhos inesperados ou isolar galvanicamente sem análise de CVBS.
- Prever chave ou enable para desligar o boost durante diagnóstico. O boost não deve habilitar com entrada abaixo de condição válida; circuito de UVLO e comportamento na partida precisam ser escolhidos e validados no componente real.

## Arquitetura de proteção a detalhar em esquemático
USB-C -> proteção ESD e sobrecorrente + filtro -> 5V_SYS -> lógica e supervisor.
5V_SYS -> chave/limitador do ramo -> boost 5->12 V -> seleção física -> tela.
Entrada externa 12 V -> proteção apropriada -> seleção física -> tela.
O barramento de 12 V **nunca** deve retornar ao 5V_SYS nem à saída do boost. Verificar boost quanto a condução reversa em estado desligado e inrush; a seleção externa deve desconectar a saída do boost.

## Corrente e teste executado
`isa1_rev56_power_budget.py` percorre 72 cenários: 2 limites de fonte × 3 hipóteses de corrente da CPU × 4 hipóteses da tela × 3 eficiências. Fórmula: `I_5V_total = I_CPU + (12*I_tela_12V)/(5*eficiência) + 0,15 A`.
0,15 A é reserva ilustrativa, não limite garantido. Em 5 V / 2 A: 9 de 36 cenários ficam dentro do orçamento; em 5 V / 3 A: 31 de 36. Isso não é taxa de confiabilidade, pois os cenários não são amostras probabilísticas.
Exemplo: CPU 0,9 A; tela 0,4 A em 12 V; eficiência 85%; total 2,1794 A em 5 V. Em 5 V / 2 A, não atende. Em 5 V / 3 A, margem nominal ~0,82 A antes de picos, tolerâncias e cabo.

## Pendências obrigatórias
1. Modelo, corrente, conector e tensão nominal da tela de R$67. Se 12 V forem somente valor automotivo, verificar faixa permitida.
2. Saídas exatas do carregador Motorola e capacidade real de 5 V do cabo USB-C; política de anúncio/negociação de corrente.
3. Orçamento de corrente de todos os CIs, especialmente lógica de vídeo, frequência, capacitâncias e consumo dinâmico.
4. Selecionar boost real com margem de corrente, eficiência e comportamento de desligamento; calcular indutor, ripple, capacitores, layout, EMI, UVLO e proteção térmica.
5. Definir seletor físico entre fontes e proteção contra polaridade reversa; confirmar aterramento CVBS e qualidade da imagem.
6. Verificar /WE da EEPROM durante rampas e brownout; o circuito de alimentação não resolve sozinho essa segurança.
7. ERC/DRC, simulação elétrica e ensaio físico ainda não executados.

**Status: arquitetura preliminar aprovada para continuar o projeto; circuito elétrico e fabricação NÃO aprovados.**
