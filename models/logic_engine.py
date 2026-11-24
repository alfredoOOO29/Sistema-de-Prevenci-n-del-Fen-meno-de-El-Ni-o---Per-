class RuleEngine:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, condition, conclusion):
        self.rules.append((condition, conclusion))
        
    def evaluate(self, fact):
        conclusions = []
        for condition, conclusion in self.rules:
            if condition(fact):
                conclusions.append(conclusion)
        
        if not conclusions:
            return "Riesgo Normal"
            
        if "Riesgo de Inundacion Extremo" in conclusions:
            return "Riesgo de Inundacion Extremo"
        elif "Riesgo de Inundacion Alto" in conclusions:
            return "Riesgo de Inundacion Alto"
        elif "Riesgo Moderado" in conclusions:
            return "Riesgo Moderado"
        return conclusions[0]
