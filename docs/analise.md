# Análise energética: ar-condicionado residencial

## 1. Contexto
Público: moradores de casa própria com ar-condicionado split. Necessidade: saber quanto o aparelho custa e decidir entre **ajustar o uso** ou **investir em solar**. Período de referência comum: **30 dias**. Origem e tipo de cada parâmetro: `dados/premissas_ar_condicionado.json`.

## 2. Consumo (situação atual)
Fórmula: `E (kWh) = P (kW) × h/dia × dias`.
Com P = 0,7 kW, 6 h/dia, 30 dias: **E = 0,7 × 6 × 30 = 126 kWh/mês**.
- Custo: 126 × R$ 1,10 = **R$ 138,60/mês**
- Emissão: 126 × 0,0289 = **3,64 kg CO₂/mês**

Potência e horas são **estimativas** (o usuário informa as suas). Para comparação: modelos 12.000 BTU inverter têm 28 a 63,6 kWh/mês em condições padronizadas (Canaltech/WebPrice); nosso cenário é de uso mais intenso (6 h/dia, todos os dias).

## 3. Alternativas comparadas
### A) Eficiência e ajuste de uso (sem investimento)
Hábitos: ~23 °C, filtros limpos, portas e janelas fechadas, timer.
- Economia = 126 × 15% = **18,9 kWh/mês = R$ 20,79/mês**; CO₂ evitado 0,55 kg/mês.
- Investimento R$ 0; saldo em 10 anos: 20,79 × 120 = **R$ 2.494,80**.
- O 15% é **hipótese da equipe** (sem fonte oficial). Testado com 10% e 25%.

### B) Energia solar fotovoltaica (renovável)
Dimensionamento para cobrir o consumo da alternativa:
- Geração por kWp = HSP × dias × PR = 4,589 × 30 × 0,75 = **103,3 kWh/kWp.mês**
- Potência necessária = 126 / 103,3 = **1,22 kWp**
- Custo = 1,22 kWp × 1.000 × R$ 2,45/Wp × 1,30 (acréscimo de pequeno porte) = **R$ 3.887**
- Economia = 126 × R$ 1,10 × (1 − 0,12 Fio B) = **R$ 121,97/mês**
- Payback simples = 3.887 / 121,97 = **32 meses (~2,7 anos)**
- Saldo em 10 anos = 121,97 × 120 − 3.887 = **R$ 10.749**
- CO₂ evitado: 3,64 kg/mês.

### A + B (combinação)
Com a eficiência primeiro, o sistema solar necessário cai para 18,9 kWh a menos: consumo 107,1 kWh → **1,04 kWp**, investimento total **R$ 3.304**, economia total **R$ 124,46/mês**, saldo em 10 anos **R$ 11.632**. O payback do solar continua ~32 meses porque custo e economia do solar são proporcionais ao consumo atendido.

## 4. Comparação resumida
| Critério | A) Eficiência | B) Solar | A + B |
| :--- | :--- | :--- | :--- |
| Investimento | R$ 0 | R$ 3.887 | R$ 3.304 |
| Economia/mês | R$ 20,79 | R$ 121,97 | R$ 124,46 |
| Retorno | imediato | ~32 meses | ~32 meses (solar) |
| CO₂ evitado/mês | 0,55 kg | 3,64 kg | 3,64 kg |
| Viabilidade | alta, depende de hábito | exige imóvel próprio, telhado e orçamento | idem B |
| Impacto ambiental | pequeno (rede já é limpa) | maior em kg, porém pequeno no total | — |

## 5. Justificativas da recomendação
1. **Eficiência primeiro:** custo zero, retorno imediato e reduz o tamanho (e o custo) do sistema solar necessário.
2. **Solar depois, se couber:** com os dados padrão o payback (~2,7 anos) fica dentro do limite de 5 anos que adotamos (e abaixo do limite de 10 anos para considerar inviável). A regra está em `calcular_analise` e os limites no JSON.
3. **Impacto ambiental:** como a rede brasileira emite pouco (~29 g CO₂/kWh), o ganho em CO₂ é pequeno em kg/mês. O benefício maior para o cidadão é financeiro; o ambiental é real, porém modesto.
4. **Custos:** o payback é simples, sem reajuste da tarifa, juros, degradação dos painéis ou manutenção.

## 6. Sensibilidade (uma variável por vez)
| Cenário | Economia A (R$/mês) | Custo solar (R$) | Payback solar (meses) |
| :--- | ---: | ---: | ---: |
| Base | 20,79 | 3.887 | 32 |
| Eficiência 10% | 13,86 | 3.887 | 32 |
| Eficiência 25% | 34,65 | 3.887 | 32 |
| Acréscimo de pequeno porte 0% | 20,79 | 2.990 | 25 |
| Acréscimo de pequeno porte 60% | 20,79 | 4.784 | 39 |
| PR 0,70 | 20,79 | 4.164 | 34 |
| PR 0,80 | 20,79 | 3.644 | 30 |
| Tarifa R$ 0,85 | 16,06 | 3.887 | 41 |
| Tarifa R$ 1,30 | 24,57 | 3.887 | 27 |
| Uso de 3 h/dia | 10,39 | 1.943 | 32 |
| Uso de 10 h/dia | 34,65 | 6.478 | 32 |
| Fio B 0% | 20,79 | 3.887 | 28 |
| Fio B 25% | 20,79 | 3.887 | 37 |
| Irradiação 4,0 kWh/m².dia | 20,79 | 4.459 | 37 |

O payback depende sobretudo de tarifa, custo do sistema, irradiação e Fio B. Não depende das horas de uso, porque o sistema é dimensionado para o consumo.

## 7. Limitações
- Todos os valores são estimativas, não garantias de economia, geração ou retorno.
- Sistemas de ~1 kWp são pequenos; o custo real por Wp pode ser maior e o instalador pode propor sistema maior. **Peça orçamento.**
- Solar exige casa própria e telhado adequado; moradores de apartamento ou aluguel podem ficar só com a alternativa A.
- Supomos que a casa consome mais que o mínimo faturável da distribuidora (a compensação ocorre sobre a conta toda).
- A irradiação usada é de São Paulo; troque pela da sua cidade (CRESESB SunData).
- Não consideramos reajuste de tarifa, degradação, juros, manutenção nem emissões da fabricação dos painéis.
- O fator de CO₂ é de um mês (abril/2025); a média anual pode diferir.
