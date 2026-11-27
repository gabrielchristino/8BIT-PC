NET36,27/11/2026: boot completo temporizado NET27/NET26 agora auditado e aceito; NET30 permanece pendente. Corrente de descarga LT3042/SET, timing real TPS3808 a4,7k e capacitância efetiva/ESR continuam sem qualificação. Proposta25mA/150uF não é BOM. Novo download LT3042 também terminou em timeout; sem PDF local. Ver engineering/NET36_REVIEW.md.

NET35, 27/11/2026: falta PDF original local LT3042 Rev. C (download terminou em timeout; leitura primária web registrada). A alternativa 3,51 V não fecha alimentação física: até 10 mA, 47 uF efetivos, ESR 50 miliohm e 20,1 us são condições a comprovar. Margens até 3,6 V e no desligamento são pequenas; selecionar componentes completos, conferir estabilidade/Kelvin/temperatura, supervisor real, partida, transientes e proteção. ERC quatro itens não aprovado, sem footprints/PCB. Proxies passivos não são modelo vendor nem ensaio físico. Ver engineering/NET35_WINDOW.md.

# Lacunas da recuperação

**A migração integral ainda não pode ser declarada concluída.** Atualização de
26/11/2026: a [exportação local](EXPORT_RECOVERY_2026-11-26.md) acrescentou quatro
registros de conversa, 240 conteúdos de biblioteca e duas Pages. Resolveu as
fontes REV33/REV76, mas contém outras ausências verificáveis.

| Item | Estado e evidência atual | Critério de fechamento |
|---|---|---|
| Conversas e alternativas | Quatro grafos completos tal como exportados, com 1.304 registros de mensagem incluindo sobreposição. Entretanto, 171 registros de biblioteca apontam a 72 IDs de origem ausentes nesses grafos | Recuperar/explicar as mensagens ausentes e conferir cobertura; não declarar todo o histórico a partir do tamanho dos JSONs |
| Pacotes anteriores/intermediários | Três ZIPs originais já preservados. A nova exportação lista 27 ZIPs, mas não traz seus bytes; os três anteriores não deixam de existir por isso | Recuperar cada conteúdo faltante, comparar entradas/hashes; não reconstruir pacote misto como original |
| diagnostic.asm | Continua ausente no pacote rev983 e no novo acervo de biblioteca | Recuperar o original e repetir a bancada histórica; a falha conhecida permanece |
| REV33 | **Fonte recuperada**: Python e JSON originais da exportação, com hashes e gerador reproduzindo JSON idêntico | Fechada a lacuna de fonte/reprodução estrutural; não equivale à CPU moderna ou elétrica validada |
| REV76 completa | **Fonte recuperada**: Python e JSON completos; reprodução em cópia temporária com JSON idêntico e 196.608 roundtrips | Fechada a lacuna de fonte/reprodução histórica; expansão de 15 instruções não é execução do microcódigo ou aprovação das 26 atuais |
| Imagens | Quatro JPG e um PNG recuperados da biblioteca, incluindo 1795536264623.jpg; imagens não são esquemas | Conferir identidade de cada preview citado, sem inferir pinagem/medida/circuito de uma imagem |
| Revisões posteriores | README 9.8.4.6.6.7 e programas exploratórios disponíveis; ZIP e mensagem de origem não constam dos conteúdos/grafos | Revisão por fonte e compatibilidade; não montar versão completa por inferência |
| Engenharia de hardware | Fontes recuperadas não demonstram placa completa. Desenvolvimento NET separado tem esquemas/netlists parciais e simulações próprias | União de circuito, componentes/cargas/energia/clock/DAC, ERC, PCB/DRC e ensaio físico |
| Integração e temporização | Testes novos distinguem ideal, portas com atrasos e SPICE condicional; não validam automaticamente PVT/CDC/MTBF ou produção | Fechar condições garantidas, integração global e medições correspondentes |
| Teclado | Pinagem de referência recebida; NET-17 tem variante candidata e política host, sem firmware CPU/medidas completas | Integrar varredura/eventos ao sistema e validar unidades/cargas; não repetir pedido de medida enquanto usuário não pode fazê-la |

O [relatório anterior de conferência](RECHECK_SHARED_CHATS.md) preserva a falha
histórica de download pelo Chrome e a recuperação parcial daquela data. Os
novos arquivos não apagam essa provenance nem transformam capturas anteriores
em downloads originais. A exportação geral de conta fica local; o recorte do
projeto tem manifestos próprios e não inclui as outras conversas.

Os 196.608 roundtrips da REV76 agora têm reprodução local em
`verification/export-2026-11-26/historical-audits.json`. O relato de 2.517 casos
da página do teclado não herda essa aprovação. Ausência de diagnostic.asm não
foi suprimida; diagnóstico novo de engenharia não substitui o arquivo histórico.

Datasheets e ensaios novos são identificados nos relatórios NET, com condições
e limitações. Não tratar valores típicos, candidatos ou arquivos disponíveis
como garantia de funcionamento físico ou disponibilidade comercial atual.
