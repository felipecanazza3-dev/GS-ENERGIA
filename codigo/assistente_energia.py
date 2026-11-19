"""Módulo de energia do Citizen Assist AI.

Tema: economia e sustentabilidade no uso de ar-condicionado residencial.
Compara duas alternativas para a MESMA necessidade e o MESMO período:
  A) Eficiência energética e ajuste de uso;
  B) Energia solar fotovoltaica (fonte renovável).
Também calcula a combinação A + B e gera uma recomendação.

Uso:
    python codigo/assistente_energia.py          # menu interativo
    from assistente_energia import consultar      # integração com o assistente

Todos os parâmetros estão em dados/premissas_ar_condicionado.json, com origem e
tipo (fonte / derivado / premissa). Resultados são ESTIMATIVAS, não garantias.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Dict, List, Optional

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_PREMISSAS = RAIZ / "dados" / "premissas_ar_condicionado.json"
CAMINHO_BASE = RAIZ / "dados" / "base_conhecimento_energia.json"


# ----------------------------------------------------------------------------
# Parâmetros
# ----------------------------------------------------------------------------
@dataclass
class ParametrosConsumo:
    potencia_media_w: float = 700.0
    horas_por_dia: float = 6.0
    dias_mes: int = 30
    tarifa_kwh: float = 1.10
    reducao_eficiencia_pct: float = 15.0
    custo_ajuste_eficiencia_brl: float = 0.0
    hsp_kwh_m2_dia: float = 4.589
    desempenho_pr: float = 0.75
    custo_wp_brl: float = 2.45
    acrescimo_pequeno_porte_pct: float = 30.0
    perda_fio_b_pct: float = 12.0
    fator_co2_kg_kwh: float = 0.0289
    horizonte_anos: int = 10


def carregar_json(caminho: Path) -> Dict[str, Any]:
    with caminho.open("r", encoding="utf-8") as f:
        return json.load(f)


def parametros_do_json(meta: Dict[str, Any]) -> ParametrosConsumo:
    """Cria ParametrosConsumo lendo os 'valor' do JSON de premissas."""
    valores = {k: v["valor"] for k, v in meta["parametros"].items()}
    nomes = {f.name for f in fields(ParametrosConsumo)}
    return ParametrosConsumo(**{k: v for k, v in valores.items() if k in nomes})


def validar(p: ParametrosConsumo) -> None:
    if p.potencia_media_w <= 0 or p.dias_mes <= 0 or p.horas_por_dia < 0:
        raise ValueError("Potência e dias devem ser positivos; horas/dia não pode ser negativa.")
    if p.horas_por_dia > 24:
        raise ValueError("Horas por dia não pode passar de 24.")
    if p.tarifa_kwh < 0 or p.fator_co2_kg_kwh < 0 or p.custo_wp_brl < 0:
        raise ValueError("Tarifa, fator de emissão e custo por Wp não podem ser negativos.")
    if not (0 <= p.reducao_eficiencia_pct < 100):
        raise ValueError("A redução por eficiência deve estar entre 0 e 99,9%.")
    if not (0 < p.desempenho_pr <= 1) or p.hsp_kwh_m2_dia <= 0:
        raise ValueError("Desempenho (PR) deve estar entre 0 e 1 e a irradiação deve ser positiva.")
    if not (0 <= p.perda_fio_b_pct < 100) or p.acrescimo_pequeno_porte_pct < 0:
        raise ValueError("Perda do Fio B deve estar entre 0 e 99,9% e o acréscimo não pode ser negativo.")
    if p.horizonte_anos <= 0:
        raise ValueError("O horizonte deve ser positivo.")


# ----------------------------------------------------------------------------
# Cálculos
# ----------------------------------------------------------------------------
def _solar(consumo_alvo_kwh: float, p: ParametrosConsumo) -> Dict[str, float]:
    """Dimensiona um sistema FV para cobrir `consumo_alvo_kwh` no período."""
    kwh_por_kwp = p.hsp_kwh_m2_dia * p.dias_mes * p.desempenho_pr
    kwp = consumo_alvo_kwh / kwh_por_kwp if kwh_por_kwp > 0 else 0.0
    custo = kwp * 1000 * p.custo_wp_brl * (1 + p.acrescimo_pequeno_porte_pct / 100)
    economia_mes = consumo_alvo_kwh * p.tarifa_kwh * (1 - p.perda_fio_b_pct / 100)
    payback = custo / economia_mes if economia_mes > 0 and custo > 0 else None
    saldo = economia_mes * 12 * p.horizonte_anos - custo
    return {
        "kwh_por_kwp_mes": kwh_por_kwp,
        "kwp": kwp,
        "custo_inicial_brl": custo,
        "geracao_kwh": consumo_alvo_kwh,
        "economia_mensal_brl": economia_mes,
        "payback_meses": payback,
        "saldo_horizonte_brl": saldo,
        "co2_evitado_kg": consumo_alvo_kwh * p.fator_co2_kg_kwh,
    }


def calcular_analise(p: ParametrosConsumo, limites: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    validar(p)
    limites = limites or {"payback_solar_atrativo_meses": 60, "payback_solar_inviavel_meses": 120}

    consumo_base = (p.potencia_media_w / 1000) * p.horas_por_dia * p.dias_mes
    custo_base = consumo_base * p.tarifa_kwh
    co2_base = consumo_base * p.fator_co2_kg_kwh

    # A) Eficiência
    eco_a_kwh = consumo_base * p.reducao_eficiencia_pct / 100
    consumo_a = consumo_base - eco_a_kwh
    eco_a_brl = eco_a_kwh * p.tarifa_kwh
    saldo_a = eco_a_brl * 12 * p.horizonte_anos - p.custo_ajuste_eficiencia_brl
    a = {
        "economia_kwh": eco_a_kwh,
        "consumo_restante_kwh": consumo_a,
        "economia_mensal_brl": eco_a_brl,
        "custo_mensal_restante_brl": consumo_a * p.tarifa_kwh,
        "custo_inicial_brl": p.custo_ajuste_eficiencia_brl,
        "saldo_horizonte_brl": saldo_a,
        "co2_evitado_kg": eco_a_kwh * p.fator_co2_kg_kwh,
    }

    # B) Solar sobre o consumo atual
    b = _solar(consumo_base, p)
    b["custo_mensal_restante_brl"] = 0.0 if consumo_base == 0 else (consumo_base - b["geracao_kwh"]) * p.tarifa_kwh

    # C) A + B (solar dimensionado para o consumo já reduzido)
    s_c = _solar(consumo_a, p)
    c = {
        "kwp": s_c["kwp"],
        "custo_inicial_brl": s_c["custo_inicial_brl"] + p.custo_ajuste_eficiencia_brl,
        "economia_mensal_brl": eco_a_brl + s_c["economia_mensal_brl"],
        "payback_solar_meses": s_c["payback_meses"],
        "saldo_horizonte_brl": saldo_a + s_c["saldo_horizonte_brl"],
        "co2_evitado_kg": a["co2_evitado_kg"] + s_c["co2_evitado_kg"],
    }

    # Recomendação (regra explícita e auditável)
    pb = s_c["payback_meses"]
    if pb is None:
        nivel = "sem_solar"
    elif pb <= limites["payback_solar_atrativo_meses"]:
        nivel = "solar_atrativo"
    elif pb <= limites["payback_solar_inviavel_meses"]:
        nivel = "solar_avaliar"
    else:
        nivel = "solar_inviavel"

    return {
        "potencia_kw": p.potencia_media_w / 1000,
        "consumo_base_kwh": consumo_base,
        "custo_base_brl": custo_base,
        "co2_base_kg": co2_base,
        "A": a,
        "B": b,
        "C": c,
        "nivel_recomendacao": nivel,
    }


# ----------------------------------------------------------------------------
# Formatação (padrão brasileiro)
# ----------------------------------------------------------------------------
def _num(v: float, casas: int = 1) -> str:
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def brl(v: float) -> str:
    return "R$ " + _num(v, 2)


def _meses(v: Optional[float]) -> str:
    if v is None:
        return "não aplicável"
    return f"{_num(v, 0)} meses (~{_num(v / 12, 1)} anos)"


def montar_recomendacao(res: Dict[str, Any], p: ParametrosConsumo) -> str:
    c = res["C"]
    pb = c["payback_solar_meses"]
    base = (
        "1º passo (faça já): ajuste o uso do ar-condicionado. Não exige investimento e a economia "
        f"estimada é de {brl(res['A']['economia_mensal_brl'])}/mês."
    )
    nivel = res["nivel_recomendacao"]
    if nivel == "solar_atrativo":
        extra = (
            f"2º passo: depois do ajuste, vale pedir orçamento de energia solar (~{_num(c['kwp'], 2)} kWp). "
            f"Payback estimado de {_meses(pb)}, dentro do limite de 5 anos adotado, e saldo de "
            f"{brl(c['saldo_horizonte_brl'])} em {p.horizonte_anos} anos somando as duas medidas."
        )
    elif nivel == "solar_avaliar":
        extra = (
            f"2º passo: o solar demoraria {_meses(pb)} para se pagar. Só avalie se for dono do imóvel "
            "e se quiser reduzir também o resto da conta; compare orçamentos antes de decidir."
        )
    elif nivel == "solar_inviavel":
        extra = (
            f"O solar, com estes dados, levaria {_meses(pb)} para se pagar. Não é recomendado agora; "
            "priorize a eficiência."
        )
    else:
        extra = "Com os dados informados não há consumo a compensar com solar."
    cond = (
        "Condições: casa própria, telhado sem sombra e orçamento real de instalador. "
        "Valores são estimativas, não garantias."
    )
    return f"{base}\n{extra}\n{cond}"


def formatar_analise(res: Dict[str, Any], p: ParametrosConsumo, meta: Dict[str, Any]) -> str:
    a, b, c = res["A"], res["B"], res["C"]
    limitacoes = "\n".join(f"- {x}" for x in meta["limitacoes"])
    return f"""RESULTADO DA SIMULAÇÃO (período de referência: {p.dias_mes} dias)

1) Situação atual: {_num(p.potencia_media_w, 0)} W médios x {_num(p.horas_por_dia, 1)} h/dia
   - Consumo: {_num(res['consumo_base_kwh'])} kWh/mês
   - Gasto na tarifa de {brl(p.tarifa_kwh)}/kWh: {brl(res['custo_base_brl'])}/mês
   - Emissão estimada: {_num(res['co2_base_kg'], 2)} kg CO₂/mês

2) Comparação das alternativas (mesma necessidade, mesmo período)
   A) Eficiência e ajuste de uso (hipótese de {_num(p.reducao_eficiencia_pct, 0)}% de redução)
      - Economia: {_num(a['economia_kwh'])} kWh/mês = {brl(a['economia_mensal_brl'])}/mês
      - Investimento inicial: {brl(a['custo_inicial_brl'])}
      - Saldo em {p.horizonte_anos} anos: {brl(a['saldo_horizonte_brl'])}
      - CO₂ evitado: {_num(a['co2_evitado_kg'], 2)} kg/mês
      - Viabilidade: alta e imediata; depende de mudar o hábito.
   B) Energia solar fotovoltaica (renovável), dimensionada para o consumo atual
      - Sistema: ~{_num(b['kwp'], 2)} kWp gerando ~{_num(b['kwh_por_kwp_mes'], 0)} kWh/kWp.mês
      - Economia: {brl(b['economia_mensal_brl'])}/mês (já descontado o Fio B de {_num(p.perda_fio_b_pct, 0)}%)
      - Investimento estimado: {brl(b['custo_inicial_brl'])} | Payback simples: {_meses(b['payback_meses'])}
      - Saldo em {p.horizonte_anos} anos: {brl(b['saldo_horizonte_brl'])}
      - CO₂ evitado: {_num(b['co2_evitado_kg'], 2)} kg/mês
      - Viabilidade: exige investimento, imóvel próprio, telhado adequado e instalador habilitado.
   A + B) Eficiência primeiro, solar menor (~{_num(c['kwp'], 2)} kWp)
      - Economia total: {brl(c['economia_mensal_brl'])}/mês | Investimento: {brl(c['custo_inicial_brl'])}
      - Payback do solar: {_meses(c['payback_solar_meses'])} | Saldo em {p.horizonte_anos} anos: {brl(c['saldo_horizonte_brl'])}

3) Recomendação
{montar_recomendacao(res, p)}

4) Limitações
{limitacoes}

Fontes e origem de cada número: dados/premissas_ar_condicionado.json e docs/referencias.md
"""


# ----------------------------------------------------------------------------
# Base de conhecimento e busca por pontuação
# ----------------------------------------------------------------------------
def _normalizar(texto: str) -> List[str]:
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    sem_acento = "".join(ch for ch in sem_acento if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-z0-9.]+", sem_acento)


def buscar_orientacoes(pergunta: str, base: Dict[str, Any], limite: int = 3) -> List[Dict[str, Any]]:
    """Pontua cada orientação pelas palavras-chave presentes na pergunta."""
    tokens = set(_normalizar(pergunta))
    achadas = []
    for item in base["orientacoes"]:
        chaves = {k for k in item["palavras_chave"]}
        pontos = len(tokens & chaves)
        if pontos > 0:
            achadas.append({**item, "pontuacao": pontos})
    achadas.sort(key=lambda x: (-x["pontuacao"], x["id"]))
    return achadas[:limite]


def consultar(pergunta: str, params: Optional[ParametrosConsumo] = None) -> str:
    """Ponto de integração: o assistente principal chama esta função com a pergunta
    do cidadão e recebe a resposta pronta (orientação + simulação + fontes)."""
    meta = carregar_json(CAMINHO_PREMISSAS)
    base = carregar_json(CAMINHO_BASE)
    params = params or parametros_do_json(meta)
    achadas = buscar_orientacoes(pergunta, base)
    if not achadas:
        return (
            "[Citizen Assist AI | Energia] Não encontrei uma orientação sobre isso. "
            "Posso ajudar com: consumo do ar-condicionado, como economizar, energia solar, "
            "Lei 14.300, CO₂ e tarifa. Tente reformular a pergunta."
        )
    partes = ["[Citizen Assist AI | Energia e Sustentabilidade]"]
    for o in achadas:
        partes.append(f"\n> {o['titulo']} ({o['id']})\n{o['texto']}")
    if any(o["usa_simulacao"] for o in achadas):
        res = calcular_analise(params, meta.get("limites_decisao"))
        partes.append("\n" + formatar_analise(res, params, meta))
    else:
        partes.append(
            "\nObs.: são estimativas, não garantias. Fontes: docs/referencias.md. "
            "Para ver números com os seus dados, pergunte sobre consumo ou solar."
        )
    return "\n".join(partes)


# ----------------------------------------------------------------------------
# Menu interativo
# ----------------------------------------------------------------------------
def _ler_float(rotulo: str, padrao: float) -> float:
    while True:
        bruto = input(f"{rotulo} [{_num(padrao, 2)}]: ").strip().replace(",", ".")
        if bruto == "":
            return padrao
        try:
            return float(bruto)
        except ValueError:
            print("Valor inválido. Digite um número (ex.: 700 ou 1,10).")


def coletar_parametros(meta: Dict[str, Any]) -> ParametrosConsumo:
    p = parametros_do_json(meta)
    print("\nInforme seus dados (Enter mantém o valor padrão, que é uma estimativa):")
    p.potencia_media_w = _ler_float("Potência média do aparelho em uso (W)", p.potencia_media_w)
    p.horas_por_dia = _ler_float("Horas de uso por dia", p.horas_por_dia)
    p.tarifa_kwh = _ler_float("Tarifa da sua conta (R$/kWh)", p.tarifa_kwh)
    return p


def main() -> None:
    meta = carregar_json(CAMINHO_PREMISSAS)
    params = parametros_do_json(meta)
    print("=== Citizen Assist AI | Energia e Sustentabilidade ===")
    while True:
        print(
            "\n1) Fazer uma pergunta sobre energia\n"
            "2) Simular com os meus dados (ar-condicionado)\n"
            "3) Ver fontes e origem dos números\n"
            "4) Ver limitações\n"
            "0) Sair"
        )
        op = input("Escolha: ").strip()
        try:
            if op == "1":
                pergunta = input("Sua pergunta: ").strip()
                print("\n" + consultar(pergunta, params))
            elif op == "2":
                params = coletar_parametros(meta)
                res = calcular_analise(params, meta.get("limites_decisao"))
                print("\n" + formatar_analise(res, params, meta))
            elif op == "3":
                for nome, d in meta["parametros"].items():
                    print(f"- {nome} = {d['valor']} {d['unidade']} [{d['tipo']}] {d['origem']}")
                    if d.get("url"):
                        print(f"    {d['url']}")
            elif op == "4":
                print("\n".join(f"- {x}" for x in meta["limitacoes"]))
            elif op == "0":
                print("Até logo!")
                break
            else:
                print("Opção inválida.")
        except ValueError as erro:
            print(f"Dados inválidos: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrado.")
            break


if __name__ == "__main__":
    main()
