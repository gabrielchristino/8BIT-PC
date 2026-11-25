# Lacunas da recuperação

**A migração integral ainda não pode ser declarada concluída.** Os materiais efetivamente recuperados estão publicados; referências a materiais ausentes foram preservadas para recuperação posterior.

Atualização da nova conferência: relatórios originais locais 7.4/7.5 e auditoria 7.6 foram preservados; o JSON REV76 integral e a dependência rev33 seguem ausentes. O Chrome bloqueou a nova tentativa de baixar o incremento 9.8.4.1 com `ERR_BLOCKED_BY_CLIENT`. A cópia desse ZIP recuperada anteriormente continua preservada. Detalhes em [RECHECK_SHARED_CHATS.md](RECHECK_SHARED_CHATS.md).

| Lacuna | Evidência e impacto | Como resolver |
|---|---|---|
| Conversas completas e versões alternativas | A API devolveu cinco trocas recentes, sem cursor; a interface complementa trechos, sem garantia de cobertura total | Exportação integral com anexos ou recuperação das partes restantes |
| Pacotes individuais anteriores e intermediários | Três ZIPs foram recuperados; referências às demais revisões não equivalem a seus arquivos | Recuperar cada pacote original e comparar hashes/diffs |
| diagnostic.asm | `revisions/rev983/test_assembler.py` exige o arquivo, que não consta do ZIP | Recuperar firmware original e repetir bancada; não gerar substituto como original |
| REV33 | `isa1_rev76.py` depende de isa1_rev33_microcode.json | Recuperar a dependência original antes de reproduzir a auditoria 7.6 |
| REV76 completa | Auditoria local em bytes disponível; Python recuperado da prévia; JSON continua fragmentado | Recuperar JSON integral e original Python verificável |
| Imagens | Foto 1795536264623.jpg e preview 3D citados; imagem não equivale a esquemático | Recuperar arquivos da Library e preservar metadados/origem |
| Engenharia de hardware | Não há esquema/netlist/PCB/HDL/SPICE completos recuperados nos ZIPs | Localizar originais ou desenvolver nova versão identificada como trabalho novo |
| Integração e temporização | Testes locais são modelos ideais; não validam circuito físico nem CDC analógico | Validar com modelos e medições apropriados |
| Mapa e teclado | Página baseada na REV76 mantém MMIO simbólico; sistema posterior usa A010–A012 sem o mesmo ENABLE | Conciliar explicitamente o contrato do periférico antes de integrar |

As tentativas de abrir links e baixar anexos históricos pela interface não produziram todos os arquivos citados. Arquivos cuja cópia não foi retida e verificada não são contabilizados como recuperados. Os resultados históricos de 196.608 roundtrips da REV76 e de 2.517 casos da página de teclado são relatos das fontes, salvo reprodução independente registrada.

Nenhuma afirmação sobre componentes atuais, disponibilidade comercial ou frequência física garantida foi revalidada durante a migração. Referências de datasheets foram preservadas como referências históricas, sem transformar valores típicos em limites de projeto.
