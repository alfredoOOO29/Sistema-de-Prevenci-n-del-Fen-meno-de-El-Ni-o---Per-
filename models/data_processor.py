import pandas as pd
from .logic_engine import RuleEngine

class ElNinoDataProcessor:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self._setup_logic_rules()
        
    def _setup_logic_rules(self):
        self.rule_engine.add_rule(
            lambda f: f['precipitation_mm'] > 120 and f['temperature_c'] > 30,
            "Riesgo de Inundacion Extremo"
        )
        self.rule_engine.add_rule(
            lambda f: 80 < f['precipitation_mm'] <= 120,
            "Riesgo de Inundacion Alto"
        )
        self.rule_engine.add_rule(
            lambda f: 40 < f['precipitation_mm'] <= 80,
            "Riesgo Moderado"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        evaluate_risk = lambda row: self.rule_engine.evaluate(row.to_dict())
        
        df['risk_level'] = df.apply(evaluate_risk, axis=1)
        at_risk = df[df['risk_level'] != "Riesgo Normal"]
        
        return df, at_risk
