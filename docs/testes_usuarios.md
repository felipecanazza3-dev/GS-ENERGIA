# Testes com usuários e ajustes

> Privacidade: não registrar nome, endereço nem outro dado pessoal. Usar apenas o perfil geral (ex.: "morador de casa, 30 anos").
> **Preencher somente com testes realmente feitos pela equipe.**

## Roteiro (5 a 10 minutos por pessoa)
1. Rodar `python codigo/assistente_energia.py`, opção 1, e pedir que a pessoa faça **sua própria pergunta** sobre energia.
2. Opção 2: pedir que informe potência/horas/tarifa (ou aceite os padrões) e leia o resultado.
3. Perguntar: (a) entendeu a recomendação? (b) entendeu o que é kWh e payback? (c) os avisos de limitação ficaram claros? (d) o que faltou?
4. Registrar o comentário, o ajuste feito no código/dados e a data.

## Registro
| Caso | Perfil geral (sem dados pessoais) | Situação testada | Comentário recebido | Ajuste realizado |
| :--- | :--- | :--- | :--- | :--- |
| CT-01 | | | | |
| CT-02 | | | | |
| CT-03 | | | | |

## Ajustes já feitos durante o desenvolvimento (testes automáticos)
- Pergunta "O que significa kWh?" estava ativando a simulação completa; o termo foi retirado das palavras-chave de consumo (`testes/test_energia.py::test_pergunta_kwh_nao_simula`).
