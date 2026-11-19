# Citizen Assist AI — Energia e Sustentabilidade (ar-condicionado residencial)

Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis (1CC)** à Global Solution **Citizen Assist AI**. Tudo o que está neste repositório é a parte de **energia** do assistente.

## Integrantes
| Nome completo | RM |
| :--- | :--- |
| Felipe Canazza | 572470 |
| Pedro Andreaza | 571107 |
| Eduardo Reis | 569727 |

## Público e problema
- **Público:** moradores de casa própria que usam ar-condicionado split e querem reduzir a conta de luz sem abrir mão do conforto.
- **Necessidade energética:** o ar-condicionado é um dos maiores consumos da casa. O cidadão precisa **estimar quanto gasta** e **decidir** entre melhorar o uso do aparelho ou investir em energia solar.
- **Como ajudamos:** o assistente responde perguntas em linguagem simples, simula o consumo com os dados do usuário, compara duas alternativas (mesmo período de 30 dias), recomenda e informa fontes e limitações.

## Funcionalidades de energia
1. **Perguntas em linguagem natural** (busca por pontuação de palavras-chave em `dados/base_conhecimento_energia.json`): consumo, kWh, economia, solar, Lei 14.300, CO₂, tarifa e confiabilidade das estimativas.
2. **Simulação com dados do usuário** (potência, horas/dia, tarifa) — consumo, custo e emissão.
3. **Comparação de alternativas:** (A) eficiência/ajuste de uso; (B) energia solar fotovoltaica (renovável); e (A+B). Inclui custo, payback, saldo em 10 anos, CO₂ e viabilidade.
4. **Recomendação automática** coerente com os cálculos (regra explícita em `montar_recomendacao`).
5. **Fontes e limitações** em toda resposta; o menu mostra a origem de cada número.
6. **Integração:** a função `consultar(pergunta)` é o ponto de entrada para o assistente principal (ver abaixo).

## Como executar
Requer Python 3.10+ (só biblioteca padrão).
```bash
python codigo/assistente_energia.py        # menu interativo
python testes/test_energia.py              # 13 testes automáticos dos cálculos e do assistente
```
Exemplos de perguntas no menu (opção 1): *"Vale a pena energia solar?"*, *"Como economizar no ar-condicionado?"*, *"O que é a Lei 14.300?"*.

### Integração com o assistente principal
```python
from assistente_energia import consultar
print(consultar("Meu ar-condicionado deixa a conta alta. Vale a pena solar?"))
```
O assistente principal (classes `Assistente`/`BaseConhecimento`) pode chamar `consultar()` quando a pergunta for sobre energia, ou carregar `dados/base_conhecimento_energia.json` como novas orientações. A contribuição desta disciplina fica isolada em `codigo/`, `dados/` e `docs/`.

## Estrutura
```
├── README.md
├── codigo/assistente_energia.py          # cálculos, recomendação, busca e menu
├── dados/premissas_ar_condicionado.json  # parâmetros com origem e tipo (fonte/derivado/premissa)
├── dados/base_conhecimento_energia.json  # orientações do assistente
├── docs/analise.md                       # cálculos, comparação, justificativas, sensibilidade
├── docs/referencias.md                   # fontes com links
├── docs/testes_usuarios.md               # registro dos testes com usuários e ajustes
├── docs/roteiro_video.md                 # roteiro do vídeo de 3 minutos
└── testes/test_energia.py
```

## Resultado com os parâmetros padrão (estimativas)
| | Investimento | Economia/mês | Observação |
| :--- | ---: | ---: | :--- |
| Situação atual | — | — | 126 kWh = R$ 138,60/mês |
| A) Eficiência | R$ 0 | R$ 20,79 | hipótese de 15% |
| B) Solar (~1,22 kWp) | R$ 3.887 | R$ 121,97 | payback ~32 meses |

**Recomendação:** ajustar o uso primeiro; depois pedir orçamento de solar (menor, ~1,04 kWp). Detalhes e sensibilidade em `docs/analise.md`.

## Limitações
Os números são **estimativas**, não garantias de economia, geração ou retorno. Parâmetros marcados como *premissa* são hipóteses da equipe e devem ser trocados por dados reais (conta de luz, orçamento de instalador). Lista completa em `docs/analise.md` e no JSON de premissas.

## Uso de IA generativa
Usamos IA generativa como apoio para estruturar o código e a documentação. Os dados, cálculos, fontes e recomendações foram conferidos pela equipe (ver `docs/referencias.md` e os testes automáticos).
