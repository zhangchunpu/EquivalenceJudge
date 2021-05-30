import re
import sympy as sy
import time

import sys
sys.path.append('/Users/hariotc/Downloads/TangentCFT-master_20200823/')


from EquivalenceJudge.one_calculation import slt_into_sympyobj
from EquivalenceJudge.one_mathml import MathMlProcess
from EquivalenceJudge.formula_group_test import EquationGroup

def eq_judgment(file_path_1, file_path_2):
    with open(file_path_1, 'r', encoding='utf-8') as f:
        mathml_1_lst = re.findall(r'<math.*?</math>', f.read(), flags=re.DOTALL)

    with open(file_path_2, 'r', encoding='utf-8') as f:
        mathml_2_lst = re.findall(r'<math.*?</math>', f.read(), flags=re.DOTALL)

    eq_group_1 = []
    for mathml in mathml_1_lst:
        slt_group_1 = MathMlProcess(mathml=mathml).convert_mathml_into_slt()
        formula_lst = list(map(slt_into_sympyobj, slt_group_1))
        if len(formula_lst) == 2:
            eq_group_1.append(sy.Eq(formula_lst[0], formula_lst[1]))
        else:
            raise Exception

    eq_group_2 = []
    for mathml in mathml_2_lst:
        slt_group_2 = MathMlProcess(mathml=mathml).convert_mathml_into_slt()
        formula_lst = list(map(slt_into_sympyobj, slt_group_2))
        if len(formula_lst) == 2:
            eq_group_2.append(sy.Eq(formula_lst[0], formula_lst[1]))
        else:
            raise Exception

    eq_group_obj_1 = EquationGroup(equation_list=eq_group_1)
    eq_group_obj_2 = EquationGroup(equation_list=eq_group_2)

    return eq_group_obj_1, eq_group_obj_2

if __name__ == '__main__':

    eq_group_one_path = '../test_data/test_data_equation/equation_group_12.html'
    eq_group_two_path = '../test_data/test_data_equation/equation_group_11.html'

    eq_group_one, eq_group_two = eq_judgment(eq_group_one_path, eq_group_two_path)

    print(eq_group_one == eq_group_two)





