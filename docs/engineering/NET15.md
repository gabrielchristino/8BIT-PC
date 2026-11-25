# NET-15 — MMIO, matriz de teclas e espera de acomodação

Base Git: `c1eac2581f8c08b92aff576c700a6465e16056d2`, 25/11/2026. Desenvolvimento novo, separado dos originais e das integrações anteriores. Não é liberação para fabricação.

## Circuitos e compatibilidade

`hardware/mmio_keyboard` contém 40 CIs, 40 capacitores propostos, 20 resistores e quatro conectores: 104 componentes, 782 pinos e 39 NC. Registrador HC174 conserva VB[1:0], EB, ROW[1:0] e BOOT_OFF pegajoso; multiplexadores de realimentação qualificam as atualizações por IO_COMMIT e ACCESS_SAFE, sem clock por portas. Leituras usam árvore de AHCT157. Endereços/ISA, valores e escrita única continuam os da base; leitura de ROW e seleções não implementadas retornam FFh. Reset de bancos é uma entrada separada do bloqueio de acessos: sua sequência elétrica global ainda precisa ser implementada.

Um HC139 seleciona quatro drivers AHC125 de nível baixo ou alta impedância. Cada linha recebe pull-up fraco de 100 kohm; cada coluna, 150 kohm, todos ±5%. Linhas inativas não são saídas push-pull em alto. Três AHC14 recebem as dezesseis colunas; quatro AHC574 implementam duas etapas de amostragem. As membranas permanecem intactas, sem diodos por tecla. Conectores J1–J4 têm pinos 1–4 L1–L4 comuns e 5–8 C1–C4 do respectivo módulo, conforme as fotos de referência. A orientação física e continuidade ainda precisam ser conferidas nas unidades e no footprint escolhido.

Quatro LV161A formam um contador saturante de 8.192 ciclos de backend, reiniciado durante reset ou escrita de ROW. KEY_READY libera leituras de colunas após aproximadamente 1,302 ms com mestre de 25,175 MHz dividido por quatro. `hardware/keyboard_access`, variante separada da NET-13, tem 31 CIs/31 capacitores, 526 pinos e nove NC. Só leituras de colunas esperam KEY_READY; as demais operações mantêm as fases/posse/payload e desligamento antecipado de drivers. O temporizador não é debounce nem corrige ghosting.

## Verificações digitais realizadas

XML exportado pelo KiCad gera os modelos conectados por pinos, com verificação de inventário, entradas, drivers e conectores. Máximo de quatro cargas internas de sinal por net nestas folhas; isso não inclui a união global nem capacitância de PCB. Modelos de atraso usam limites selecionados, incluindo HC139 44 ns e AHC14 12 ns; não são fechamento de mínimos, PVT ou distribuição de clocks.

* Matriz, ideal e com atrasos: 5.681 padrões por modo, 22.724 varreduras, 23.504 escritas e 45.969 leituras. Inclui vazio, 64 teclas individuais, todos os 2.016 pares, 2.880 trios em L e 720 retângulos. A referência calcula fechamento elétrico booleano independente; ghosting é esperado, não reconhecimento irrestrito de simultâneas. Esta bancada de MMIO direto não espera os 8.192 ciclos a cada padrão.
* Controlador: três configurações, cada uma com 890 transações e 128 cortes digitais de reset/alimentação. Os testes anteriores de payload, efeitos únicos e posse são preservados.
* Integração decoder/controlador/MMIO: ideal e temporizada, onze transações, quatro leituras longas, sete acessos curtos, reset com leitura pendente e pedido antigo retido. Menor espera observada: 1.301.684,770 ns no cenário temporizado.
* Negativos rejeitam troca de linhas/colunas no conector, driver forçado em alto, bypass de KEY_READY, payload indevido, posse indevida da VRAM e clock de payload desconectado.

Não houve integração nova desta folha ao programa completo da CPU/raster. A NET-14C publicada continua usando teclado/MMIO comportamentais. A primeira etapa de amostragem recebe entradas humanas assíncronas: modelos booleanos não qualificam metastabilidade/MTBF, histerese analógica ou bounce.

## Envelope elétrico condicional, não medição

O usuário informou não poder medir as membranas agora. `electrical-envelope.json` registra 96 cenários ngspice, com decks e saídas brutas. Os 48 cenários dentro do orçamento passaram; 44 externos falharam e quatro pontos externos passaram sem receber qualificação. Contato fechado ≤150 ohm por contato; até sete contatos e oito trechos de fio de até 10 ohm; capacitância efetiva ≤1 nF por fio; fuga local de coluna ≤1,5 uA, de linha ≤4 uA, envelope agregado ±40 uA. Esses números são requisitos condicionais de qualificação, não propriedades comprovadas das membranas.

O ensaio concentra os vinte pull-ups/capacitâncias num nó distante e usa um caminho resistivo conservador de primeira ordem; inclui resistência no caminho de carga após soltar a tecla e verifica separadamente o piso em alto por polarização local. Não demonstra todos os circuitos RC distribuídos possíveis nem substitui modelo dos pads/ESD/PCB. A fuga IOZ de drivers inativos motivou adicionar os pull-ups das linhas: não é correto concentrar essa fuga indefinidamente em uma única coluna flutuante.

Nos cenários qualificados do modelo: acomodação máxima de 379,184 us, margem baixa mínima de 119,886 mV, margem alta conservadora mínima de 184,8 mV e corrente máxima de 0,812312 mA. Limites globais usados: VT− mínimo 1,35 V, VT+ máximo 3,85 V, clamp VOL 0,44 V e orçamento de sink 8 mA, a partir das condições explicitadas nos PDFs. A espera digital supera o orçamento de 1 ms. Interpolação contínua de tensão, PVT, medições, proteção e limites reais de componentes ainda não estão aprovados.

AHC14 é candidato utilizado; HC14 foi consultado como alternativa. HCS125 foi consultado e não selecionado: o documento consultado não forneceu a garantia de IOZ necessária, e corrente de entrada não substitui corrente de saída em alta impedância. Nenhum desses PDFs constitui BOM homologada.

## Reproduzir e revisar

No Ubuntu WSL, a partir da raiz: `python3 tools/build_mmio_keyboard.py`, `python3 tools/build_keyboard_access.py`, `python3 tools/prepare_keyboard_access_checks.py`, `python3 tools/run_mmio_keyboard.py`, `python3 tools/run_keyboard_access_control.py`, `python3 tools/run_key_settle.py`, `python3 tools/run_keypad_envelope.py` e `python3 tools/check_keyboard_erc.py`. Os JSONs registram ferramentas, comandos, fontes/hashes e resultados. ERC de folhas parciais permanece com violações, sem waivers; o retorno nativo é preservado. A inspeção gráfica não equivale a ERC de uma placa unida.

`verification/net15/development` preserva tentativas intermediárias: amostragem no mesmo instante da atualização, orçamento de acomodação incompleto e regra indevida que exigia falha de todo ponto externo. No registro anterior aos pull-ups de linha, uma cópia de fonte terminou depois da edição: o aviso identifica essas cópias tardias; fontes reconstruídas pela reversão da edição foram verificadas contra os hashes efetivamente registrados no ensaio e salvas separadamente. Não são apresentadas como cópias contemporâneas originais.

Próxima dependência para integrar CPU/teclado temporizados: reset/energia global que bloqueie WE antes de modificar bancos e libere os registradores com clocks válidos. Também pendem proteção/conectores reais, firmware de debounce/cancelamento/fila/ambiguidades, ensaio físico das quatro membranas, esquema unido, BOM/footprints, ERC/DRC e protótipo.
