# NET-18 — Alimentação e supervisor: envelope condicional e folha de reset

26/11/2026. Base Git `b439a3aa84505654ea064e0ccd6bc1e3636b4c0b` (NET-17).
Trabalho novo; nenhuma fonte histórica, NET-16 ou NET-17 foi sobrescrita.
**Não há alimentação global homologada nem liberação de fabricação.**

## Resultado que esta etapa sustenta

| Ensaio | Resultado e limite |
|---|---|
| Reserva isolada de energia | 64 cenários ngspice completos; três negativos completos rejeitados por tensão, não por erro da ferramenta |
| Janela DC | 16 cantos do monitor e 16 do ajuste do regulador; três combinações impróprias rejeitadas; parâmetros ainda condicionais |
| Folha `hardware/power_reset` | 18 componentes: seis CIs, oito capacitores, quatro resistores; 100 pinos, 14 NC; XML conferido |
| Reset digital derivado dos pinos | 16 configurações, cada uma com 32 cortes, 11 pausas de CPU e 11 de backend; dois negativos rejeitados |
| Fronteira assíncrona | Duas políticas binárias, dez cortes por política, três eventos de recovery por estágio/domínio; modelo estrito continua rejeitado |
| Negativos de topologia | Alterar o divisor e reconectar o inibidor à saída crua são rejeitados pela conferência de XML |
| ERC parcial | Cinco violações: duas de alimentação, duas de entradas e uma etiqueta isolada. Retorno nativo 5, sem exceções |
| Modelo oficial TPS63070 | Nenhuma tentativa concluiu o transitório com medida final. Compatibilidade/convergência permanece aberta |

O reset é simulado no ponto `RAW_SAFE_N`, representando a saída de um supervisor
qualificado. O CI TPS3703 está na folha com pinos/passivos reais, mas seus circuitos
internos **não** foram substituídos por um modelo fictício aprovado. A projeção
digital omite somente esse CI analógico e confere todos os seus pinos no XML.
O RC conserva a abstração inercial da NET-16; não cobre memória de carga em trens
de pulsos. Metastabilidade, subida finita de RESET e VDD abaixo da faixa válida
continuam fora da aprovação digital.

## Candidatos e seleção para análise

Originais TI e extrações separadas estão identificados por URL/SHA-256 em
`verification/net18/research/sources.json`. Datasheets, limites e alternativas:

- **TPS3703F6050DSER**, SBVS249B: candidato UV-only de referência nominal 0,5 V,
  tolerância de janela −6%, resultando em UV nominal de 0,47 V. A precisão usada é
  **±1%** para VIT < 800 mV; a precisão de ±0,7% da primeira linha não se aplica.
  Histerese máxima 0,7%; CT aberto propõe liberação em 0,7–1,3 ms. Detecção máxima
  de 30 us exige 5% de overdrive, saída com pull-up 10k e carga 10 pF. A extensão
  a rampas arbitrárias/lentas não foi qualificada. Startup de 300 us é típico,
  não um máximo que feche POR. MR fica alto na folha; a tabela temporal usa MR
  aberto, outra condição a confirmar na homologação da aplicação.
- Divisor de SENSE candidato **950/100 ohm**, tolerância efetiva ±0,1% incluindo
  temperatura/envelhecimento, filtro candidato 1 nF. O limite de corrente SENSE
  de ±10 uA é **orçamento de qualificação**, não limite de datasheet nesta tensão;
  o máximo publicado de 1,5 uA tem condição VSENSE=5 V. O filtro recebe orçamento
  de 1 us, também ainda por qualificar com parasitas e rampas.
- **TPS63070**, SLVSC58B: candidato buck-boost de entrada USB 5 V para trilho
  interno nominal **5,232 V**, ajuste proposto 55,4k/10k, VFB 0,8 V ±1%, fuga FB
  até 100 nA. Modo PWM exige PS/SYNC baixo. Esse alvo é proposta elétrica, não BOM
  ou resistor comercial homologado; não altera a tensão USB nem permite retorno
  de energia a VBUS. Faixa/cargas de todos os futuros periféricos ainda precisam
  de conferência.
- **TPS25947**, SLVSFC9C: candidato de isolamento/limitação. RON máximo de 45 mΩ
  entra na conta DC; bloqueio reverso de 1 us é **típico**, sem fechar carga
  reversa máxima. Limitação de corrente não impõe o teto instantâneo de 1,5 A
  do estudo, e clamp com máximo de 6,2 V não protege, por si só, lógica de 5,5 V.
- **TUSB320LAI**: alternativa para reconhecer corrente anunciada em USB-C. Não
  foi implementada nesta folha. Não presumir 3 A em qualquer porta; controle de
  corrente, rampa de VDD, inicialização e proteção de VBUS continuam pendentes.
- TPS3808 foi consultado, mas seus tempos de detecção SENSE/MR são típicos na
  tabela examinada. TLV3501 tem máximos de propagação, porém offset e deriva não
  fecham automaticamente o limiar em toda temperatura. REF31 e TPS63020 ficam
  como alternativas consultadas; nenhum deles virou BOM validada.

Na folha nova, U6 usa SENSE=1, VDD=2, CT=3 aberto, RESET=4 open-drain, GND=5,
MR=6 alto, conforme DSE seis pinos. O buffer U1 recebe sozinho a saída RESET;
U4 passa a receber `RAW_BUFFERED`, em vez de acrescentar carga a `RAW_SAFE_N`.
O orçamento total de 10 pF exige entrada + encapsulamento + trilha reais e ainda
não está medido. O buffer acrescenta atraso no caminho rápido; os ensaios
selecionados mantêm inibição antes do reset dos bancos.

## Conta de energia e janela DC

`tools/run_power_hold_up.py` usa limite inferior conservador de trip 4,8673086 V
e observação a 95% desse limite: **4,6239432 V**. Após 30 us de detecção, 1 us de
filtro e 100 ns de lógica/WE, o orçamento até inibir WE é 31,1 us. Até afirmar
reset dos bancos, reserva-se mais 19,1 us: **50,2 us** no total.

O envelope exige capacitância **efetiva mínima de 4,4 mF**, ESR até 20 mΩ,
carga até 1,5 A, pico reverso até 0,5 A e carga reversa total até 50 uC. Uma
proposta nominal de 6,6 mF não comprova esses limites sob tolerância, temperatura,
envelhecimento, frequência e corrente. Os limites independentes pessimistas são
**4,5619773 V em WE** e **4,5554659 V no reset dos bancos**, acima do piso de
temporização usado de 4,5 V. São margens condicionais, não medições.

Cada caso SPICE tem saída zero e três medidas, comparadas à solução independente
de corrente constante e ESR (resíduo <0,2 mV). Os negativos reduzem C a 220 uF,
ampliam ESR a 0,2 ohm ou carga a 20 A. Todos completam e violam a tensão exigida.
O pulso retangular testa 50 uC; a conta analítica coloca toda a carga reversa
antes da observação, sem depender dessa forma específica de pulso. O teto de
pico também é necessário: carga total sozinha não limita a queda em ESR.

A janela DC reserva 45 mΩ no isolador, 10 mΩ de trilha e ±20 mV para regulação/
ripple. Esses dois últimos são **orçamentos propostos**, não limites garantidos
do conversor. Resultado: 5,062879–5,318827 V; pior liberação do supervisor
5,037908 V, margem DC de aproximadamente **25 mV**. A enumeração de cantos tem
limite de detecção 18 uV menos pessimista que a fórmula de hold-up, que combina
o maior Rtop para o erro de corrente com o menor para o ganho; as contas não são
apresentadas como idênticas. Ripple/transientes reais podem invalidar a janela.

**1,5 A não é o consumo calculado da placa.** O inventário combina sete folhas
candidatas, agora com a variante nova de reset: 456 CIs e 29 famílias, cujos
limites estáticos/dinâmicos/carga continuam explicitamente abertos. A contagem
não inclui os futuros CIs de conversão/USB/DAC/oscilador nem equivale a uma placa
integrada. A baseline de 455 CIs foi preservada separadamente.

Este estudo não cobre curto no trilho sustentado pelo capacitor, queda arbitrária
sem os limites de corrente, sobretensão catastrófica, partida fria ou garantia de
WE durante VDD inválido. Esses casos não podem herdar a aprovação do hold-up.

## Modelo oficial e tentativas preservadas

ZIP original TI `slvmbp8a.zip`: dez arquivos extraídos byte a byte e verificados.
Biblioteca original Final 1.00 de 22/07/2016, destinada a PSpice 16.2; avisos TI
preservados, nenhuma licença nova aplicada. O modelo exclui temperatura e
corrente de repouso/desligamento; seu limite de partida é 1 A.

ngspice 42 sem compatibilidade rejeita sintaxe PSpice. `ngbehavior=ps` resolve
essa sintaxe, mas não o parâmetro Rser do indutor da bancada; ele foi trocado
somente na bancada por resistência explícita de 30 mΩ. A biblioteca permaneceu
inalterada. Integração padrão não terminou em 55 s; Gear terminou com erro de
passo temporal em aproximadamente 80 us. Três ensaios adicionais com parâmetros
numéricos explícitos também não completaram (dois timeouts de 60 s e um erro).
Nenhum tem medida `final_v` válida: **não há aprovação do regulador**. Não se
trocaram seus circuitos por fonte ideal para declarar aprovação do fabricante.

As primeiras tentativas usam alvo 5,136 V; as três últimas usam 5,232 V.
Logs, decks, códigos e status ficam em `verification/net18/vendor-trial`.
`development/hold-preload-equation` preserva a falha da primeira conta ESR:
antes do corte, a corrente DC do capacitor é zero mesmo com carga na fonte;
depois, sua ESR conduz toda a carga. A correção da equação da bancada é
identificada; não foi um componente físico que falhou. Uma falha de recuperação
de fonte via `inspect` também está preservada e corrigida usando o emissor textual.

## Reproduzir e continuar

No Ubuntu WSL, a partir de `/mnt/c/Users/gabri/projetos/isa1`:

```text
python3 tools/check_power_references.py
python3 tools/inventory_power_loads.py
python3 tools/run_power_window.py
python3 tools/run_power_hold_up.py
python3 tools/build_power_reset.py
python3 tools/prepare_power_reset_checks.py
python3 tools/run_power_reset.py
python3 tools/run_power_apertures.py
python3 tools/check_power_topology.py
python3 tools/check_power_reset_erc.py
python3 tools/run_power_vendor.py
python3 tools/record_net18_manifest.py --check
```

ERC retorna 5 pelas pendências reais. O coletor de pesquisa vendor retorna zero
para registrar tentativas; **esse retorno não aprova nenhuma delas**: verificar
`completed`, medida final e código individual. Ferramentas e comandos completos
estão nos relatórios, incluindo Icarus 12, ngspice 42 e KiCad 10.0.8.

Continuar por consumo/carga reais, conversor e isolamento reverso qualificados,
sequência USB-C/POR, integração dos domínios CPU/backend/MMIO/memórias/raster,
relógios/DAC, cargas e temporização global. União de esquemas, footprints, ERC,
PCB/DRC, montagem e ensaios físicos continuam critérios de produção. Nada nesta
etapa exige repetir ao usuário a medição das membranas que ele ainda não pode fazer.
