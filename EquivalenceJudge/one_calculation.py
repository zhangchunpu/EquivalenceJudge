import re
from graphviz import Digraph
import sympy as sy

from TangentS.math_tan.math_extractor import MathExtractor

# TODO: TreeInformationとSympyConverterを一つのクラスにまとめる
class TreeInformation:

    def __init__(self, file_name, tree_list=None):

        if file_name is not None:
            self.file_name = file_name
            try:
                self._tree_list_for_slt = self.convert_into_slt()
            except:
                print('content mathml')

        else:
            self._tree_list_for_slt = tree_list

        if hasattr(self, '_tree_list_for_slt'):
            self._var_dic = self.get_var_info()
            self._info = self.get_calculation_info()

    def convert_into_slt(self):
        with open(self.file_name, 'r', encoding='utf-8') as f:
            formula_content = re.findall(r'<math.*</math>', f.read(), flags=re.DOTALL)[0]
            math_extractor = MathExtractor()
            slt_tree = math_extractor.convert_to_layoutsymbol(formula_content)
            tree_list = [('', slt_tree)]
            return tree_list

    def convert_into_opt(self): #これはあまり使わない
        with open(self.file_name, 'r', encoding='utf-8') as f:
            formula_content = re.findall(r'<math.*</math>', f.read(), flags=re.DOTALL)[0]
            math_extractor = MathExtractor()
            opt_tree = math_extractor.convert_to_semanticsymbol(formula_content)
            tree_list = [opt_tree]
            return tree_list

    def __getitem__(self, item):
        return self.info[item]

    def show_the_graph(self, use_slt_or_opt='slt'):
        if use_slt_or_opt == 'slt':
            try:
                self.graph_for_slt(self.tree_list_for_slt)

            except:
                print('sltで表現できない可能性がある')

        else:
            try:
                tree_list = self.convert_into_opt()
                self.graph_for_opt(tree_list)

            except:
                self.graph_for_slt(self.tree_list_for_slt)
                print('optで表現できない可能性があり、sltで表しました')

    def get_var_info(self):

        var_list = []
        #この時点ではsin cos logなどの初等関数はまだ入っている
        var_list_with_func = self.extract_var(self.tree_list_for_slt, var_list)
        # 初等関数は変数ではないので、取り除いていく
        var_list = var_list_with_func.copy()
        for var in var_list_with_func:
            if var in ['sin', 'cos', 'tan', 'sec', 'cosec', 'cotan', 'log', 'asin', 'acos', 'atan']:
                var_list.remove(var)

        #ネイピア数やΠなども変数として抽出されるが、
        # ここではSymPyのネイピア数、Πのオブジェクトで置き換える。
        # その他の変数はSymPyのsymbolsメソッドで変数オブジェクトへ変換する
        var_dic = {}
        for var in set(var_list):
            if var == 'e':
                var_dic[var] = sy.E
            elif var == 'pi':
                var_dic[var] = sy.pi
            else:
                var_dic[var] = sy.symbols(var)

        return var_dic

    def get_calculation_info(self):
        formula_element = []

        # A list holding the hierarchical information of a formula
        # is created from SLT-tangents.
        formula_info_with_func = self.parse_tree(
            self.tree_list_for_slt, formula_element, self.var_dic)

        #logを除いた関数に対する処理、log関数を除くのはlog関数の木構造が特殊だからです
        for var in formula_info_with_func:

            # ['sin', [STL of 'a', None, 'within']]
            # --> ['sin', [STL of 'a', None, 'sin']]
            if var in ['sin', 'cos', 'tan', 'sec', 'cosec', 'cotan', 'asin', 'acos', 'atan']:
                index = formula_info_with_func.index(var)
                if type(formula_info_with_func[index+1]) == list:
                    formula_info_with_func[index + 1][2] = var
                else:   #これは起きえないはず, 関数が作用する数式は<mfence>タグで囲めば、その数式がリストの中に入る。
                    raise Exception('関数が作用する範囲が明確ではありません')


            elif type(var) == list and var[2] == 'log':
                index = formula_info_with_func.index(var)
                if  type(formula_info_with_func[index+1]) == list:
                    logarithm = formula_info_with_func[index+1]
                    var[1] = logarithm[0]
                else:
                    raise Exception('関数が作用する範囲が明確ではありません')
                formula_info_with_func.pop(index+1)

        formula_info = formula_info_with_func.copy()

        for var in formula_info_with_func:
            # ['sin', [STL of 'a', None, 'sin']]
            # --> [[STL of 'a', None, 'sin']]
            if var in ['sin', 'cos', 'tan', 'sec', 'cosec', 'cotan', 'asin', 'acos', 'atan']:
                formula_info.remove(var)

        return formula_info


    @property
    def tree_list_for_slt(self):
        return self._tree_list_for_slt

    @property
    def info(self):
        return self._info

    @property
    def var_dic(self):
        return self._var_dic

    @classmethod
    def graph_for_slt(cls, tree_list):
        Tree = Digraph(format='png')
        Tree.attr("node", shape="square", style="filled")
        Tree.attr("graph", rankdir="LR")
        slt_tree_list = []

        if not tree_list:
            pass

        else:
            for slt_tree in tree_list:
                if not slt_tree[1].active_children():
                    Tree.node(slt_tree[1].tag)
                else:
                    for children_tuple in slt_tree[1].active_children():
                        absolute_path = slt_tree[0]
                        tag_ancestor = slt_tree[1].tag
                        tag_children = children_tuple[1].tag
                        tag_ancestor += ',' + absolute_path
                        absolute_path += children_tuple[0]
                        tag_children += ',' + absolute_path
                        Tree.edge(tag_ancestor, tag_children)

                for children_tuple in slt_tree[1].active_children():
                    absolute_path = slt_tree[0]
                    children = children_tuple[1]
                    if children.active_children():
                        absolute_path += children_tuple[0]
                        slt_tree_list.append((absolute_path, children))

            return cls.graph_for_slt(slt_tree_list)

        Tree.view()

    @classmethod
    def graph_for_opt(cls, tree_list, node_id='0'):
        Tree = Digraph(format='png')
        Tree.attr("node", shape="square", style="filled")
        Tree.attr("graph", rankdir="LR")
        opt_tree_list = []

        if not tree_list:
            pass

        else:
            for opt_tree in tree_list:
                for children_object in opt_tree.children:
                    node_id = str(int(node_id) + 1)
                    children_object.tag += ',' + node_id
                    Tree.edge(opt_tree.tag, children_object.tag)

                for children_object in opt_tree.children:
                    if children_object.children != None:
                        opt_tree_list.append(children_object)

            return cls.graph_for_opt(opt_tree_list, node_id)

        Tree.view()

    @classmethod
    def deal_with_vtag(cls, tree_list):
        variable = None
        formula = None
        for slt_tree in tree_list:
            variable = slt_tree[1].tag
            children_list = slt_tree[1].active_children()

            if variable.startswith('V!'):
                variable = variable.split('!')[1]
                #三角関数の逆関数をここで捕まえる
                if variable in ['sin', 'cos', 'tan']:
                    for children_tuple in children_list:
                        position = children_tuple[0]
                        if position == 'a' and children_tuple[1].tag == 'N!-1':
                            variable = 'a'+variable
                        else:
                            pass

            elif variable.startswith('N!'):
                pass

            for children_tuple in children_list:
                position = children_tuple[0]

                if position == 'b':
                    tag_under = children_tuple[1].tag
                    tag_under = tag_under.split('!')[1]
                    variable += '_' + tag_under

                elif position == 'o':
                    # どう処理するか後で考えましょう　これはハット付きの変数　
                    pass

                elif position == 'n':
                    formula = [('', children_tuple[1])]

        return variable, formula

    @classmethod
    def deal_with_fraction(cls, tree_list):
        over_formula = None
        under_formula = None
        formula = None
        for slt_tree in tree_list:
            for children_tuple in slt_tree[1].active_children():
                position = children_tuple[0]
                # 上付き文字に対応する
                if position == 'o':
                    over_formula = [('', children_tuple[1])]

                elif position == 'u':
                    under_formula = [('', children_tuple[1])]

                elif position == 'n':
                    formula = [('', children_tuple[1])]

        return over_formula, under_formula, formula

    @classmethod
    def deal_with_paren(cls, tree_list):
        formula_within = None
        formula = None
        for slt_tree in tree_list:
            for children_tuple in slt_tree[1].active_children():
                position = children_tuple[0]
                if position == 'w':
                    formula_within = [('', children_tuple[1])]

                elif position == 'n':
                    formula = [('', children_tuple[1])]
        return formula_within, formula

    @classmethod
    def deal_with_exp(cls, tree_list):
        formula_above = None
        for slt_tree in tree_list:
            for children_tuple in slt_tree[1].active_children():
                position = children_tuple[0]
                if position == 'a':
                    formula_above = [('', children_tuple[1])]
        return formula_above

    @classmethod
    def deal_with_root(cls, tree_list):
        formula_within = None
        formula_pre_above = None
        formula = None
        for slt_tree in tree_list:
            for children_tuple in slt_tree[1].active_children():
                position = children_tuple[0]
                if position == 'w':
                    formula_within = [('', children_tuple[1])]

                elif position == 'n':
                    formula = [('', children_tuple[1])]

                elif position == 'c':
                    formula_pre_above = [('', children_tuple[1])]

        return formula_within, formula_pre_above, formula

    @classmethod
    def deal_with_log(cls, tree_list):
        formula_below = None
        formula_next = None
        for slt_tree in tree_list:
            for children_tuple in slt_tree[1].active_children():
                position = children_tuple[0]
                if position == 'b':
                    formula_below = [children_tuple]
                elif position == 'n':
                    formula_next =[children_tuple]
        return formula_below, formula_next

    @classmethod
    def parse_tree(cls, tree_list, formula_element, var_dic):
        if not tree_list:
            return formula_element

        else:
            for slt_tree in tree_list:
                if slt_tree[1].tag.startswith('O!divide'):
                    numerator, denominator, formula_next = cls.deal_with_fraction([slt_tree])
                    formula_element.append([numerator, denominator, 'frac'])
                    return cls.parse_tree(formula_next, formula_element, var_dic)

                elif slt_tree[1].tag.startswith('V!') and (not slt_tree[1].tag.startswith('V!log')) or \
                     slt_tree[1].tag.startswith('N!'):
                    var, formula_next = cls.deal_with_vtag(tree_list)
                    formula_above = cls.deal_with_exp([slt_tree])
                    if formula_above != None and var not in ['asin', 'acos', 'atan']:
                        formula_element.append([var_dic[var], formula_above, 'exp'])
                    else:
                        formula_element.append(var)
                    return cls.parse_tree(formula_next, formula_element, var_dic)

                elif slt_tree[1].tag.startswith('M!'):
                    formula_within, formula_next = cls.deal_with_paren([slt_tree])
                    formula_above = cls.deal_with_exp([slt_tree])
                    if formula_above != None:
                        formula_element.append([formula_within, formula_above, 'exp'])
                    else:
                        formula_element.append([formula_within, None, 'within'])
                    return cls.parse_tree(formula_next, formula_element, var_dic)

                elif slt_tree[1].tag.startswith('O!root'):
                    formula_within, formula_pre_above, formula_next = cls.deal_with_root([slt_tree])
                    formula_element.append([formula_within, formula_pre_above, 'root'])
                    return cls.parse_tree(formula_next, formula_element, var_dic)

                elif slt_tree[1].tag.startswith('V!log'):
                    formula_below, formula_next = cls.deal_with_log([slt_tree])
                    formula_element.append([formula_below, None, 'log'])
                    return cls.parse_tree(formula_next, formula_element, var_dic)

                elif slt_tree[1].tag in ['+', '-', '=', '*']:
                    formula_element.append(slt_tree[1].tag)
                    formula_next = slt_tree[1].active_children()
                    return cls.parse_tree(formula_next, formula_element, var_dic)

    @classmethod
    def extract_var(cls, tree_list, var_list):

        slt_tree_list = []

        if len(tree_list) == 0:
            return var_list

        else:
            for slt_tree in tree_list:
                # slt_tree = [親ノードとの位置関係, SLT本体]
                tag = slt_tree[1].tag
                # この例外はformula_5をみれば
                if 'V!' in tag:
                    variable, formula = cls.deal_with_vtag([slt_tree])
                    # formulaについては特になにもしない
                    var_list.append(variable)

                # 下付き文字は付属情報なので変数として扱わない
                children_list = list(
                    filter(lambda x: x[0] != 'b', slt_tree[1].active_children()))
                slt_tree_list.extend(children_list)

            return cls.extract_var(slt_tree_list, var_list)


class SympyConvert:
    def __init__(self, var_dic, formula_info):
        self._var_dic = var_dic
        self._formula_info = formula_info

    def get_sympy_object(self):
        formula_information = self.formula_info.copy()
        return SympyConvert.expand_formula_info(formula_information, self.var_dic)

    @property
    def formula_info(self):
        return self._formula_info

    @property
    def var_dic(self):
        return self._var_dic

    @classmethod
    def make_simple_formula(cls, formula_info, var_dic):

        try:
            if '*' in formula_info:
                print('乗算の演算子は使われている')

            else:
                formula_info = cls.add_multiple_operator(formula_info)

            for index, element in enumerate(formula_info):

                if type(element) == str and 'N!' in element:
                    formula_info[index] = int(element.split('!')[1])

                elif element in var_dic:
                    formula_info[index] = var_dic[element]

                else:
                    pass

            # 乗算を先に計算しないといけませんね
            formula_info = cls.do_multiple_calculation(formula_info)

            if formula_info[0] in ['+', '-']:
                formula_info.insert(0, 0)

            formula = formula_info[0]  # 数式の一番目に来るのが変数か、数字であると仮定する

            for i, element in enumerate(formula_info):

                if element == '+':
                    formula += formula_info[i + 1]

                elif element == '-':
                    formula -= formula_info[i + 1]

            result = formula

        #sympy object がきた時にそのまま返す
        except:
            result = formula_info

        return result

    @classmethod
    def judge_simple(cls, formula_info):

        #sympy objectが渡される可能性があるため try
        try:
            lst = list(filter(lambda x: type(x) == list, formula_info))
            if not lst:
                return True
            else:
                return False

        #sympyのオブジェクトになった数式は簡単な数式である
        except:
            return True

    @classmethod
    def judge_simple_list(cls, lst, var_dic):

        if lst[2] == 'frac':
            formula_over_element = []
            formula_under_element = []

            #クラスメソッドをクラスの外部で使うのはどうかと思ったけど、簡単な式については問題ないと思います。
            try:
                formula_over_info = TreeInformation.parse_tree(lst[0], formula_over_element, var_dic)
            except:
                formula_over_info = lst[0]
            try:
                formula_under_info = TreeInformation.parse_tree(lst[1], formula_under_element, var_dic)
            except:
                formula_under_info = lst[1]

            if cls.judge_simple(formula_over_info) and cls.judge_simple(formula_under_info):
                return True
            else:
                return False

        elif lst[2] == 'exp':
            formula_below_element = []
            formula_above_element = []

            try:
                formula_below_info = TreeInformation.parse_tree(lst[0], formula_below_element, var_dic)
            except:
                formula_below_info = lst[0]
            try:
                formula_above_info = TreeInformation.parse_tree(lst[1], formula_above_element, var_dic)
            except:
                formula_above_info = lst[1]

            if cls.judge_simple(formula_below_info) and cls.judge_simple(formula_above_info):
                return True
            else:
                return False

        elif (lst[2] == 'within') or (lst[2] in ['sin', 'cos', 'tan', 'sec', 'cosec', 'cotan', 'log', 'asin', 'acos', 'atan']):
            formula_within_element = []

            try:
                formula_within_info = TreeInformation.parse_tree(lst[0], formula_within_element, var_dic)
            except:
                formula_within_info = lst[0]

            if cls.judge_simple(formula_within_info):
                return True
            else:
                return False

        elif lst[2] == 'root':
            formula_within_element = []
            formula_pre_above_element = []

            try:
                formula_within_info = TreeInformation.parse_tree(lst[0], formula_within_element, var_dic)
            except:
                formula_within_info = lst[0]
            try:
                formula_pre_above_info = TreeInformation.parse_tree(lst[1], formula_pre_above_element, var_dic)
            except:
                formula_pre_above_info = lst[1]

            if cls.judge_simple(formula_within_info) and cls.judge_simple(formula_pre_above_info):
                return True
            else:
                return False

    @classmethod
    def add_multiple_operator(cls, formula_info):
        if len(formula_info) == 1:
            return formula_info
        elif not formula_info:
            print('何も入ってない')
        else:
            for i, element in enumerate(formula_info):
                if i == len(formula_info) - 1:
                    return formula_info
                element_n = formula_info[i + 1]
                if element not in ['+', '-', '*'] and element_n not in ['+', '-', '*']:  # 演算子でなければ、数字あるいは変数である
                    formula_info.insert(i + 1, '*')
                    break
            return cls.add_multiple_operator(formula_info)

    @classmethod
    def do_multiple_calculation(cls, formula_info):
        if not list(filter(lambda x: x == '*', formula_info)):
            return formula_info
        else:
            for element in formula_info:
                if element == '*':
                    index = formula_info.index(element)
                    multiple = formula_info[index - 1] * formula_info[index + 1]
                    formula_info[index - 1:index + 2] = [multiple]
                    break
            return cls.do_multiple_calculation(formula_info)

    @classmethod
    def deal_with_simple_list(cls, lst, var_dic):
        if lst[2] == 'within':
            formula_element = []
            try:
                formula_info = TreeInformation.parse_tree(lst[0], formula_element, var_dic)
            except:
                formula_info = lst[0]
            formula = cls.make_simple_formula(formula_info, var_dic)
            return formula

        elif lst[2] == 'frac':
            formula_over_element = []
            formula_under_element = []

            try:
                formula_over_info = TreeInformation.parse_tree(lst[0], formula_over_element, var_dic)
            except:
                formula_over_info = lst[0]
            try:
                formula_under_info = TreeInformation.parse_tree(lst[1], formula_under_element, var_dic)
            except:
                formula_under_info = lst[1]

            formula_over = cls.make_simple_formula(formula_over_info, var_dic)
            formula_under = cls.make_simple_formula(formula_under_info, var_dic)

            if type(formula_over) == int and type(formula_under) == int:
                return sy.Rational(formula_over, formula_under)
            else:
                return formula_over / formula_under

        elif lst[2] == 'exp':
            formula_below_element = []
            formula_above_element = []

            try:
                formula_below_info = TreeInformation.parse_tree(lst[0], formula_below_element, var_dic)
            except:
                formula_below_info = lst[0]
            try:
                formula_above_info = TreeInformation.parse_tree(lst[1], formula_above_element, var_dic)
            except:
                formula_above_info = lst[1]

            formula_below = cls.make_simple_formula(formula_below_info, var_dic)
            formula_above = cls.make_simple_formula(formula_above_info, var_dic)
            return formula_below ** formula_above

        elif lst[2] == 'root':
            formula_within_element = []
            formula_pre_above_element = []
            try:
                formula_within_info = TreeInformation.parse_tree(lst[0], formula_within_element, var_dic)
                formula_within = cls.make_simple_formula(formula_within_info, var_dic)
            except:
                formula_within = lst[0]

            if lst[1] is not None:
                try:
                    formula_pre_above_info = TreeInformation.parse_tree(lst[1], formula_pre_above_element, var_dic)
                    formula_pre_above = cls.make_simple_formula(formula_pre_above_info, var_dic)
                except:
                    formula_pre_above = lst[1]
            else:
                formula_pre_above = 2

            if type(formula_pre_above) == int:
                return formula_within ** sy.Rational(1, formula_pre_above)
            else:
                return formula_within ** (1 / formula_pre_above)

        elif lst[2] == 'log':
            formula_below_element = []
            formula_logarithm_element = []

            if lst[0] is not None:
                try:
                    formula_below_info = TreeInformation.parse_tree(lst[0], formula_below_element, var_dic)
                    formula_below = cls.make_simple_formula(formula_below_info, var_dic)
                except:
                    formula_below = lst[0]
            else:
                formula_below = sy.E

            try:
                formula_logarithm_info = TreeInformation.parse_tree(lst[1], formula_logarithm_element, var_dic)
                formula_logarithm = cls.make_simple_formula(formula_logarithm_info, var_dic)
            except:
                formula_logarithm = lst[1]

            return sy.log(formula_logarithm, formula_below)

        elif lst[2] in ['sin', 'cos', 'tan', 'sec', 'cosec', 'cotan', 'asin', 'acos', 'atan']:
            formula_within_element = []

            try:
                formula_within_info = TreeInformation.parse_tree(lst[0], formula_within_element, var_dic)
                formula_within = cls.make_simple_formula(formula_within_info, var_dic)
            except:
                formula_within = lst[0]

            if lst[2] == 'sin':
                return sy.sin(formula_within)

            elif lst[2] == 'cos':
                return sy.cos(formula_within)

            elif lst[2] == 'tan':
                return sy.tan(formula_within)

            elif lst[2] == 'cosec':
                return 1 / sy.sin(formula_within)

            elif lst[2] == 'sec':
                return 1 / sy.cos(formula_within)

            elif lst[2] == 'cotan':
                return 1 / sy.tan(formula_within)

            elif lst[2] == 'asin':
                return sy.asin(formula_within)

            elif lst[2] == 'acos':
                return sy.acos(formula_within)

            elif lst[2] == 'atan':
                return sy.atan(formula_within)

    @classmethod
    def expand_formula_info(cls, formula_info, var_dic):
        # 複雑な式はあるかを確認し、あればリストに追加する
        whether_simple = cls.judge_simple(formula_info)
        if whether_simple:
            sympy_formula = cls.make_simple_formula(formula_info, var_dic)
            return sympy_formula

        else:
            # 複雑な式を[object1, object2, calculation]形式で返す
            complex_formula_list = list(filter(lambda x: type(x) == list, formula_info))

            for lst in complex_formula_list:
                index = formula_info.index(lst)
                if cls.judge_simple_list(lst, var_dic):
                    formula_info[index] = cls.deal_with_simple_list(lst, var_dic)

                else:
                    for i, tree_list in enumerate(lst):
                        if i == 2 :
                            break
                        if type(tree_list) is not list:
                            continue

                        tree = TreeInformation(file_name=None, tree_list=tree_list)
                        info = tree.get_calculation_info()
                        lst[i] = cls(formula_info=info, var_dic=var_dic)

                    for i in range(2):
                        if lst[i] is not None:
                            #この時点すでにsympyのオブジェクトに変換されるものもある
                            if hasattr(lst[i], 'get_sympy_object'):
                                formula = lst[i].get_sympy_object()
                                lst[i] = formula
                            else:
                                pass

                    formula_info[index] = lst

            return cls.expand_formula_info(formula_info, var_dic)



if __name__ == '__main__':
    tree = TreeInformation(file_name='formula_for_graph.html')
    tree.show_the_graph(use_slt_or_opt='opt')
