import re
from TangentS.math_tan.math_extractor import MathExtractor


# MathML を受け取ってSLTを返す

class MathMlProcess:

    plus_minus_operator = re.compile(r'<mo>&PlusMinus;</mo>', flags=re.DOTALL)
    function_apply = re.compile(r'<mo>&ApplyFunction;</mo>', flags=re.DOTALL)
    multiply_operator = re.compile(r'<mo>&InvisibleTimes;</mo>', flags=re.DOTALL)
    equation_operator = re.compile(r'<mo>=</mo>', flags=re.DOTALL)
    napier_number = re.compile(r'<mi>&ExponentialE;</mi>', flags=re.DOTALL)
    integral = re.compile(r'<mo>&int;</mo>', flags=re.DOTALL)
    derivative_d = re.compile(r'<mo>&DifferentialD;</mo>', flags=re.DOTALL)

    def __init__(self, mathml):
        self.mathml = mathml

    def convert_mathml_into_slt(self):
        return self.deal_with_equation(self.mathml)

    def is_equation(self):
        equal_lst = self.equation_operator.findall(self.mathml)
        if equal_lst:
            return True
        else:
            return False

    def has_function(self):
        func_lst = self.function_apply.findall(self.mathml)
        if func_lst:
            return True
        else:
            return False

    def has_plusminus_sign(self):
        plusminus_list = self.plus_minus_operator.findall(self.mathml)
        if plusminus_list:
            return True
        else:
            return False

    @classmethod
    def deal_with_equation(cls, mathml):
        lst=[]
        formula_mathml_list = cls.equation_operator.split(mathml)
        for formula in formula_mathml_list:
            formula.strip()
            if formula.startswith(r'<math'):
                formula_mathml = formula+r'</mrow></math>'
                lst.append(formula_mathml)
            elif formula.endswith(r'</math>'):
                formula_mathml = r'<math><mrow>'+formula
                lst.append(formula_mathml)
            else:
                formula_mathml = r'<math><mrow>' + formula + r'</mrow></math>'
                lst.append(formula_mathml)

        lst_element_slt = list(map(MathExtractor.convert_to_layoutsymbol, lst))
        return lst_element_slt

    @classmethod
    def deal_with_func(cls, mathml):
        pass


if __name__ == '__main__':
    with open('../test_data/sample_formula/formula_equation_22.html', 'r', encoding='utf-8') as f:
        mathml = f.read()
        a = MathMlProcess(mathml=mathml)
        print(a.convert_mathml_into_slt())







