import sympy as sy
import re


from EquivalenceJudge.formula_group_test import EquationGroup
from TangentS.math_tan.math_extractor import MathExtractor
from EquivalenceJudge.one_calculation import TreeInformation, SympyConvert


def mathml_to_eq_group(file_path_1, file_path_2):

    math_reg = r'<math.*?</math>'
    with open(file_path_1, 'r', encoding='utf-8') as f:
        mathml_1_list = re.findall(math_reg, f.read(), flags=re.DOTALL)
    with open(file_path_2, 'r', encoding='utf-8') as f:
        mathml_2_list = re.findall(math_reg, f.read(), flags=re.DOTALL)

    sympy_obj_list_1 = mathml_to_sympy_obj(mathml_1_list)
    sympy_obj_list_2 = mathml_to_sympy_obj(mathml_2_list)

    eq_group_1 = EquationGroup(equation_list=sympy_obj_list_1)
    eq_group_2 = EquationGroup(equation_list=sympy_obj_list_2)

    return eq_group_1, eq_group_2


def mathml_to_sympy_obj(mathml_list):
    sympy_obj_list = []
    for mathml_ in mathml_list:
        slt_list = mathml_to_slt(mathml_)
        formula_list = list(map(slt_into_sympyobj, slt_list))
        if len(formula_list) == 2:
            sympy_obj_list.append(sy.Eq(formula_list[0], formula_list[1]))
        else:
            raise Exception
    return sympy_obj_list


def mathml_to_slt(mathml):
    equation_operator = re.compile(r'<mo>=</mo>', flags=re.DOTALL)
    formula_mathml_list=[]

    for formula_ in equation_operator.split(mathml):
        formula_.strip()
        if formula_.startswith(r'<math'):
            formula_mathml = formula_ + r'</mrow></math>'
            formula_mathml_list.append(formula_mathml)
        elif formula_.endswith(r'</math>'):
            formula_mathml = r'<math><mrow>' + formula_
            formula_mathml_list.append(formula_mathml)
        else:
            formula_mathml = r'<math><mrow>' + formula_ + r'</mrow></math>'
            formula_mathml_list.append(formula_mathml)

    slt_list = \
        list(map(MathExtractor.convert_to_layoutsymbol, formula_mathml_list))
    return slt_list


def slt_into_sympyobj(slt):
    tree_list = [('', slt)]
    tree = TreeInformation(tree_list=tree_list, file_name=None)
    var_dic = tree.var_dic
    formula_info = tree.info
    sympy_convert_instance = \
        SympyConvert(var_dic=var_dic, formula_info=formula_info)
    return sympy_convert_instance.get_sympy_object()
