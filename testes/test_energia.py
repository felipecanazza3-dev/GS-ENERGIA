import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "codigo"))
import assistente_energia as ae  # noqa: E402


class TestCalculos(unittest.TestCase):
    def setUp(self):
        self.p = ae.ParametrosConsumo()
        self.r = ae.calcular_analise(self.p)

    def test_consumo_base(self):  # 0,7 kW x 6 h x 30 d = 126 kWh
        self.assertAlmostEqual(self.r["consumo_base_kwh"], 126.0)
        self.assertAlmostEqual(self.r["custo_base_brl"], 138.6)

    def test_eficiencia(self):  # 15% de 126 = 18,9 kWh
        self.assertAlmostEqual(self.r["A"]["economia_kwh"], 18.9)
        self.assertAlmostEqual(self.r["A"]["economia_mensal_brl"], 20.79)

    def test_solar(self):
        kwh_kwp = 4.589 * 30 * 0.75
        self.assertAlmostEqual(self.r["B"]["kwp"], 126 / kwh_kwp)
        custo = (126 / kwh_kwp) * 1000 * 2.45 * 1.30
        self.assertAlmostEqual(self.r["B"]["custo_inicial_brl"], custo)
        eco = 126 * 1.10 * 0.88
        self.assertAlmostEqual(self.r["B"]["economia_mensal_brl"], eco)
        self.assertAlmostEqual(self.r["B"]["payback_meses"], custo / eco)

    def test_combinado_menor_que_solar_sozinho(self):
        self.assertLess(self.r["C"]["kwp"], self.r["B"]["kwp"])

    def test_co2(self):
        self.assertAlmostEqual(self.r["co2_base_kg"], 126 * 0.0289)

    def test_consumo_zero(self):
        p = ae.ParametrosConsumo(horas_por_dia=0)
        r = ae.calcular_analise(p)
        self.assertEqual(r["consumo_base_kwh"], 0)
        self.assertIsNone(r["B"]["payback_meses"])
        self.assertEqual(r["nivel_recomendacao"], "sem_solar")

    def test_validacao(self):
        for kwargs in (
            {"potencia_media_w": 0}, {"horas_por_dia": 25}, {"tarifa_kwh": -1},
            {"reducao_eficiencia_pct": 100}, {"desempenho_pr": 0}, {"dias_mes": 0},
        ):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                ae.calcular_analise(ae.ParametrosConsumo(**kwargs))

    def test_recomendacao_sempre_eficiencia_primeiro(self):
        txt = ae.montar_recomendacao(self.r, self.p)
        self.assertIn("1º passo", txt)
        self.assertIn("ajuste o uso", txt)


class TestAssistente(unittest.TestCase):
    def test_pergunta_solar_traz_simulacao(self):
        resp = ae.consultar("Vale a pena instalar energia solar?")
        self.assertIn("RESULTADO DA SIMULAÇÃO", resp)
        self.assertIn("Recomendação", resp)
        self.assertIn("Limitações", resp)

    def test_pergunta_kwh_nao_simula(self):
        resp = ae.consultar("O que significa kWh?")
        self.assertNotIn("RESULTADO DA SIMULAÇÃO", resp)

    def test_pergunta_fora_do_escopo(self):
        self.assertIn("Não encontrei", ae.consultar("receita de bolo"))

    def test_busca_ignora_acento(self):
        base = ae.carregar_json(ae.CAMINHO_BASE)
        ids = [o["id"] for o in ae.buscar_orientacoes("Como reduzir a conta de luz? Dicas de hábito", base)]
        self.assertIn("EN-03", ids)

    def test_json_carrega_parametros(self):
        meta = ae.carregar_json(ae.CAMINHO_PREMISSAS)
        self.assertEqual(ae.parametros_do_json(meta), ae.ParametrosConsumo())


if __name__ == "__main__":
    unittest.main()
