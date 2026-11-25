# Critérios para liberar o ISA-1 para produção

Este é o roteiro de evidências para chegar a uma placa produzível. Uma bancada isolada aprovada não marca um bloco ou a placa inteira como liberado.

| Etapa | Evidência necessária | Estado atual |
|---|---|---|
| Especificação | ISA, flags, mapa, reset, pilha, boot e periféricos conciliados | Modelos recuperados; divergências ainda documentadas |
| Modelos de componentes | Funções, níveis ativos, carga/reset e comparação com datasheets identificados | HC191/157/377 candidatos modelados; demais CIs pendentes |
| Controle/datapath | Carga, retenção e efeitos únicos de COMMIT, inclusive reset/WAIT em fronteiras | Banco de carga testado isoladamente; integração pendente |
| Esquemático completo | Todos os pinos e alimentações, portas, inicialização e interfaces definidos | Primeiro esquema parcial do banco X; sem controle completo |
| Simulação de netlist | Modelo derivado das ligações reais e regressão das 26 instruções | Pendente; HDL e mapa de pinos ainda são representações separadas |
| Temporização | Setup/hold com mínimos/máximos, carga, skew, duty cycle e cantos | Cenário parcial e monitores executados; fechamento completo pendente |
| Elétrica | TTL/CMOS, drivers, DAC VGA, memória, ruído, alimentação, reset/brownout | Datasheets de candidatos arquivados; SPICE e medidas pendentes |
| Teclado | Pinagem medida, corrente de linha, bounce, pares/ambiguidades e CPU/VGA | Proposta e modelos ideais; interface física pendente |
| ERC | Erros resolvidos e exceções justificadas em esquema completo | Não executado; CLI 7 disponível não tem subcomando ERC |
| Layout | Footprints conferidos, desacoplamento, retorno, conectores e montagem | Pendente |
| DRC e fabricação | DRC, BOM, posições, Gerbers, furos e revisão independente | Pendente |
| Protótipo | Medições de funcionamento, margens e testes de produção | Pendente |

Para cada iteração, registrar revisão, arquivos de entrada, hashes, ferramentas/versões, comandos, saídas, falhas e limitações. Testes negativos devem comprovar que os monitores detectam violações reais. Arquivos históricos não são corrigidos em seu lugar.

As decisões de rotina podem seguir autonomamente. Consultar o usuário quando dependerem de um dado físico não disponível (por exemplo pinagem da membrana), de uma mudança material nos requisitos ou de uma decisão de compra/fabricação.
