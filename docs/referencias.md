# Referências

Acessadas em 19/11/2026. Cada número do projeto aponta para uma delas em `dados/premissas_ar_condicionado.json`.

| Dado | Valor usado | Fonte |
| :--- | :--- | :--- |
| Tarifa média residencial (B1) 2026 | R$ 849/MWh sem tributos → R$ 1,10/kWh com ICMS 18% e PIS/Cofins 4,9% (conta da equipe) | ANEEL, boletim *Luz na Tarifa* (Ano I, nº 3), reproduzido em [infoTARIFA mar/2026](https://cenarioenergia.com.br/wp-content/uploads/2026/03/17032026_infoTARIFA_MAR_2026.pdf) |
| Bandeira tarifária em nov/2026 | Verde (sem cobrança extra) | ANEEL, via [Folha de Pernambuco](https://www.folhape.com.br/economia/aneel-mes-de-novembro-tera-bandeira-tarifaria-verde/521664/) |
| Fator de emissão do SIN | 0,0289 kg CO₂/kWh (abril/2025; jan–abr/2025: 21,5 a 28,9 kg/MWh) | MCTI/SIRENE, via [Canal Solar](https://canalsolar.com.br/emissoes-de-co%e2%82%82-geracao-eletrica-mcti/) |
| Irradiação solar (São Paulo) | 4,589 kWh/m².dia (média anual) | Atlas Brasileiro de Energia Solar (INPE), via [ABSOLAR](https://www.absolar.org.br/wp-content/uploads/2021/02/São%20Paulo.pdf) |
| Custo de sistema FV residencial | R$ 2,45/Wp (média nacional, 1º tri 2026) | Radar Solfácil, via [Cenário Energia](https://cenarioenergia.com.br/2026/06/09/preco-do-watt-pico-residencial-recua-7-em-um-ano-e-abre-janela-de-oportunidade-na-mmgd/) |
| Regras de compensação / Fio B | 60% em 2026, 75% em 2027, 90% em 2028 (art. 27) | [Lei 14.300/2022](https://www.gov.br/mme/pt-br/acesso-a-informacao/legislacao/leis/lei-n-14-300-2022.pdf) |
| Consumo de split 12.000 BTU inverter (comparação) | 28 a 63,6 kWh/mês em condições padronizadas (IDRS) | [Canaltech](https://canaltech.com.br/eletro/ar-condicionado-de-12000-btu-gasta-muito-veja-consumo-de-14-modelos-a-venda/), dados WebPrice |
| Temperatura de 23 °C | citada como ideal pela Anvisa | [Canaltech](https://canaltech.com.br/produtos/8-dicas-para-economizar-energia-ao-utilizar-o-ar-condicionado/) |
| Selo/ENCE de eficiência | Procel/PBE (classes A a G) | PBE/INMETRO e Procel (conceito geral; consulte a etiqueta do aparelho) |

## O que NÃO tem fonte oficial (premissas da equipe)
Potência média (700 W), horas/dia (6 h), redução por eficiência (15%), desempenho do sistema solar (PR 0,75), acréscimo de pequeno porte (30%) e participação do Fio B na tarifa (~20%, que gera a perda de 12%). Todos são testados na análise de sensibilidade em `docs/analise.md` e podem ser trocados no JSON.

## Pontos a conferir antes de publicar
- Tarifa com tributos (R$ 1,10) é **derivada**; confirme com a sua conta.
- O fator de CO₂ é **mensal**; a média anual oficial está no site do MCTI.
