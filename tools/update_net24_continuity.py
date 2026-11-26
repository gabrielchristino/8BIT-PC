"""Record request clock regrouping and the still-rejected reset pulse cases."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def prepend(name,text):
    path=ROOT/name;old=path.read_text(encoding='utf-8')
    if old.startswith('Atualização NET-24'):old=old.split('\n\n',1)[1]
    path.write_text(text+'\n\n'+old,encoding='utf-8')


def main():
    summary=('Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. '
             '32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. '
             'Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. ')
    prepend('README.md',summary+'Ver [resultados e lacuna aberta](docs/engineering/NET24.md). Próximo: encerrar a sequência de fases com pulsos completos; placa não liberada.')
    prepend('ROADMAP.md',summary+'Prioridade: investigar a drenagem do token descrita em docs/engineering/CLOCK_DRAIN_STUDY.md, ainda não implementada, e repetir os cortes; depois demais clocks/energia/DAC/firmware/união/ERC/PCB/protótipo.')
    prepend('CHANGELOG.md',summary+'Apenas U4.3/U4.11 da folha common_request mudam; modelos e resultados originais preservados. Rejeições de pulso constam explicitamente do relatório.')
    prepend('PROVENANCE.md','Atualização NET-24, 26/11/2026: base c54226afed52e04c787b91c65dc29cfacf8f661e. hardware/common_request deriva do JSON versionado, alterando somente dois clocks de U4. Projeções independentes exploram CQ hipotético onde HC74 não informa mínimo e assimetria de pulsos. Quatro rejeições7,722ns/20ns são evidências de lacuna, não testes aprovados. Guardas originais preservadas; diagnóstico de pulso só acrescenta largura/clear à mensagem. Estudos futuros são propostas, sem implementação ou liberação presumida.')
    prepend('docs/engineering/PRODUCTION_GATES.md',summary+'Fechar essa rejeição sem enfraquecer o requisito do HC74 e observar WE/bancos nos pinos. ERC parcial135 violações, sem exceções; não aprovar fabricação a partir das regressões funcionais.')
    prepend('docs/engineering/VALIDATION_STATUS.md',summary+'Escopos e evidências em [NET24](NET24.md); o boot novo foi ideal com SRAM desconhecida, programa completo temporizado segue pendente.')
    path=ROOT/'docs/engineering/VALIDATION_STATUS.md';text=path.read_text(encoding='utf-8')
    rows={
        '| 1. Relógio, raster e captura de vídeo |':'| 1. Relógio, raster e captura de vídeo | NET22/23 integrados; NET24 confirma backend50% em regime, porém quatro resets com assimetria de bordas violam20ns no modelo | Corrigir/qualificar pulsos de reset e os demais caminhos, cargas extraídas, jitter/slew/MTBF/PVT e programa/quadro temporizado completo |',
        '| 6. Temporização global |':'| 6. Temporização global | NET24 agrupa dois clocks REQ,32 cenários locais e regressões passam; pulso de7,722ns permanece rejeitado em4 casos de reset | Fechar rejeição ativa sem waiver, todos os mínimos/máximos, demais grupos/skew/hold/setup/recovery, jitter/PVT/MTBF e circuito elétrico correspondente |',
        '| 8. Esquema global e ERC |':'| 8. Esquema global e ERC | Folha common_request NET24 tem31CIs/526pinos e135 violações; fonte/reset e vídeo continuam parciais | União real de blocos/pinos/alimentações, resolver ERC e conferir footprints; não somar folhas parciais nem mascarar entrada sem fonte |',
    }
    path.write_text('\n'.join(next((new for prefix,new in rows.items() if line.startswith(prefix)),line) for line in text.splitlines())+'\n',encoding='utf-8')
    path=ROOT/'DECISIONS.md';old=path.read_text(encoding='utf-8')
    if '## ADR E29' not in old:
        path.write_text('''## ADR E29 — Agrupar os dois estágios de pedidos sem mudar a lógica

26/11/2026. Base NET23. Mover U4CLK0/CLK1 de BUF_3_3/BUF_3_4 para BUF_4_1
na variante [NET24](docs/engineering/NET24.md). Apenas dois pinos;31CIs e
todo o estado/payload/MDR/ISA preservados. Estados, payload e REQ/MDR ficam
com três cargas cada, orçamento40pF sem extração de PCB.

Datasheet HC74 dá máximo44ns e não mínimo de CLK–Q. Modelo ilustrativo6ns
com buffers1/8,5ns reproduz setup inválido no segundo estágio; não é medida
de silício. Relógio comum elimina essa dependência selecionada entre buffers.
Manter atrasos máximos iguais ocultaria a lacuna; impor CQ mínimo sem fonte
ou relaxar o monitor não é alternativa. Acrescentar/reduzir CIs não é necessário
para este agrupamento. Primeiro estágio analógico/skew de pinos seguem abertos.

Critério funcional: XML delta exato,32 cenários locais, negativo revertendo
um clock, instruções ideal/temporizadas, oito cortes/scans e boot/quadro
com SRAM desconhecida. Esses ensaios passaram; não aprovam toda a temporização.
Quatro ensaios distintos continuam rejeitados por pulso7,722ns/20ns durante
reset, embora regime50% tenha orçamento47,44ns. Registrar falha aberta e
avaliar parada por drenagem em estudo separado, sem presumir implementação
ou enfraquecer guardas. ERC135 e critérios físicos permanecem abertos.

'''+old,encoding='utf-8')
    path=ROOT/'AGENTS.md';old=path.read_text(encoding='utf-8')
    if '## Continuidade NET-24' not in old:
        path.write_text('''## Continuidade NET-24

- Leia docs/engineering/NET24.md. hardware/common_request tem31CIs/62componentes/526pinos/9NC, só U4.3 e U4.11 mudam para BUF_4_1. Três grupos de três CLK; sem mudança de lógica ou famílias. Modelo do primeiro estágio HC74 ainda não é analógico.
- HC74 SCLS094F dá44ns máximo, sem mínimo; CQ0/1/6 são hipóteses ilustrativas, não limites garantidos ou silício medido.32 cenários locais e negativo passam no agrupamento; não chamar de STA/MTBF/PVT completo.
- Backend real já usa G_2=OR(P1,P2), não P0, e tem50% em regime. Conta selecionada47,44ns não vale durante reset. run_reset_pulse_probe.py registra quatro rejeições7,722ns/20ns nos offsets30/39/40/60; failures vazio no coletor só significa coleta/classificação correta, não aprovação desses casos. Nunca suprimir o monitor para aceitar runt ativo.
- CLOCK_DRAIN_STUDY.md é proposta NÃO implementada. Considera U8 AHC164/4estágios, serial síncrono, clear RC independente, máscaras rápidas e armamento sticky dos bancos; investigar e provar antes de adotar. Não ligar warm clear ao banco sincronizado criando deadlock, nem apagar bancos via READY antes de WE alto.
- Instruções6886 ideais/dois1062 temporizados, oito cortes/scans e novo boot132197/76800pixels passaram. Boot ideal escala clocks/startup e usa SRAM desconhecida; programa completo temporizado não foi executado. ROMs originais permanecem iguais.
- SRC/modelos de uma execução ativa ficam congelados. ERC parcial135 violações sem exceções; primeiro estágio/clock/PVT/energia/POR/consumo/USB-C/DAC/firmware/união/ERC/footprints/PCB/DRC/protótipo e diagnostic.asm histórico permanecem com seus critérios próprios.

'''+old,encoding='utf-8')


if __name__=='__main__':main()
