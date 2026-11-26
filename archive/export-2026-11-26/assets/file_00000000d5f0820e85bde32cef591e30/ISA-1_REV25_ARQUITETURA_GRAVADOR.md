# ISA-1 — Revisão 2.5: arquitetura do gravador ZIF e auditoria
Data: 2026-11-23. Status: **estudo arquitetural, não aprovado para fabricação**.

## Decisão consolidada
Um único AT28C256 DIP-28 removível no ZIF contém programa e dados de SAVE; o ISA-1 deve ler, gravar, verificar e executar cópia do programa na SRAM. Troca de CI somente com a alimentação desligada. CPU 74HC/HCT discreta, sem microcontrolador executando a CPU. Armazenamento interno futuro é independente.

## Erro corrigido da Rev. 2.4
O mapa publicado na Rev. 2.4 tinha tamanhos inconsistentes: `0040–783F` equivale a 30.720 bytes, não 30.656; `7C40–7FFF` tem 960 bytes, não 1.024. Corrigimos:

| Região | Intervalo inclusivo | Bytes | Páginas de 64 B |
|---|---|---:|---:|
| Cabeçalho | 0000–003F | 64 | 1 |
| Código/recursos | 0040–77FF | 30656 | 479 |
| SAVE A | 7800–7BFF | 1024 | 16 |
| SAVE B | 7C00–7FFF | 1024 | 16 |
| Total | 0000–7FFF | 32768 | 512 |

O cabeçalho e o código têm proteção de endereço por firmware; isso **não é proteção física contra firmware defeituoso**. A proteção SDP da AT28C256 é global, não por setor.

## Alternativa A — Porta dedicada com registradores (preferida provisoriamente)
CPU -> registradores de endereço (15 bits, dois CIs octais), registrador de dados (8 bits, um CI octal), transceptor de dados bidirecional (um CI octal) -> EEPROM no ZIF. O firmware configura endereço, escreve ou lê e aguarda conclusão. /CE, /OE, /WE vêm de um controlador registrado, com intertravamento e reset.

Benefícios: a EEPROM lenta não limita todos os acessos da CPU à RAM; endereços/dados permanecem estáveis durante o ciclo interno de gravação; controle simples de auditar. Custo: pelo menos quatro CIs octais de interface, **sem contar** controle, seleção, reset, decodificação e eventuais multiplexadores. Esses quatro não são uma BOM definitiva. Os 74HC273 não possuem habilitação de carga: para usar registradores desse tipo, a carga precisa ser implementada com multiplexadores na entrada ou outra solução síncrona, **não com AND direto no clock**. Alternativas com load enable devem ser verificadas em datasheet e estoque.

**Atenção:** para leitura, o transceptor não deve dirigir a EEPROM; para escrita, a EEPROM deve ter /OE inativo antes de habilitar o driver CPU→EEPROM. /WE deve permanecer alto durante o reset e enquanto endereço/dados não estiverem estabilizados.

## Alternativa B — Janela de memória mapeada
A EEPROM é acessada como região do espaço de 64 KB da CPU. Vantagens: menos registradores dedicados e operações de leitura/escrita naturais. Problemas: disputa com ROM, RAM, VRAM e I/O; remapeamento/banking; temporização da EEPROM; controle especial para SDP; risco de escrita por instruções erradas. Não há prova de economia líquida de CIs até que o mapa completo seja fechado.

## Comparação e decisão
Preferimos **A provisoriamente**, porque o chip removível é um meio de armazenamento, não memória de execução. Isso desacopla o gravador do caminho crítico da CPU. A preferência pode mudar após contagem completa dos CIs e simulação temporal dos dois caminhos. É possível implementar a porta dedicada como registradores de I/O acessados pelo próprio barramento da CPU, sem inventar um segundo processador.

## Proteção elétrica e de reset
- Alimentação de 5 V e terra, desacoplamento junto à EEPROM, ZIF com orientação e pinagem verificadas.
- /WE, /OE, /CE inativos durante power-up, power-down e reset. Pull-ups isoladamente não provam segurança em rampa de alimentação; saídas de 74HC podem estar indefinidas antes de VCC válido.
- Supervisor real de alimentação/reset **a selecionar** conforme limiares de VCC, tolerâncias, saída e atraso. Não escolher part number sem datasheet.
- Estado de escrita só pode ser alcançado por transição registrada; autorização explícita; bloqueio lógico para impedir /OE=0 e /WE=0 simultaneamente.
- Necessário estudar se um gate combinacional pode gerar pulso em /WE por skew de entradas; considerar registro de /WE e habilitação de chip, além de circuito de power-good.
- SDP, verificação pós-gravação e SAVE A/B com commit final; ensaios reais de queda de energia são obrigatórios.
- Inserção e remoção com computador **desligado**; não presumir hot-swap.

## Temporização — pendência crítica
Os valores de tACC, tCE, tOE, tDF, tWP, tDS, tDH, tAS, tAH, tempo de ciclo de escrita e tempos dos 74HC/EEPROM/supervisor devem ser extraídos das variantes e condições corretas dos datasheets. **Não atribuímos frequência de clock nem margem em nanossegundos nesta revisão.** A operação de gravação pode levar milissegundos, independentemente da frequência de CPU. Implementar polling/timeout e verify; começar com escrita de um byte por ciclo, depois estudar páginas.

Fonte de componente candidata: [Microchip AT28C256, DS20006386](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C256-Industrial-Grade-256-Kbit-Paged-Parallel-EEPROM-Data-Sheet-DS20006386.pdf). Confirmar revisão, pacote PDIP e variante comprada antes de atribuir tempos.

## Testes desta revisão
`python isa1_rev25_architecture_check.py` verificou exaustivamente 32.768 posições no mapa corrigido, alinhamento de páginas e 56 combinações estáticas de fase/reset/power-good/autorização. Passou. O modelo é propositalmente simples: **não é circuito elétrico, SPICE, HDL com atraso, teste de barramento bidirecional físico nem validação de reset real**. A comparação entre arquiteturas é qualitativa e não prova menor quantidade de chips.

## Próxima revisão 2.6
1. Escolher CIs específicos para latch com enable e controle de escrita e confrontar pinagens dos datasheets.
2. Elaborar netlist pin-to-pin com duas opções de interface e registrar BOM comparativa completa.
3. Definir supervisor de tensão com datasheet e arquitetura de bloqueio de escrita durante rampas.
4. Simular atrasos máximos/mínimos com modelo temporal, inclusive reset e leitura→escrita→leitura.
5. Conferir um caso de escrita SDP e SAVE com leitura/verify, usando testes de falha injetada.
