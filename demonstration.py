import sympy as sy
import streamlit as st
import pandas as pd
import pickle
import os

from EquivalenceJudge.mathml_to_eq_group import mathml_to_eq_group


if __name__ == '__main__':

    st.markdown("<h1 style='text-align: center; color: black; font-size: 9mm '>equivalence judgment of equation groups</h1>", unsafe_allow_html=True)

    # fileのpathを取得する
    file_name_1 = st.selectbox(
        'enter file path one',
        ['equation_group_{}.html'.format(str(i)) for i in range(1, 17)]
    )

    file_name_2 = st.selectbox(
        'enter file path two',
        ['equation_group_{}.html'.format(str(i)) for i in range(1, 17)]
    )

    cwd = os.getcwd()
    eq_group_one_path = cwd + '/test_data/test_data_equation/' + file_name_1
    eq_group_two_path = cwd + '/test_data/test_data_equation/' + file_name_2

    #同義性判定を行う
    eq_group_obj_1, eq_group_obj_2 = mathml_to_eq_group(eq_group_one_path, eq_group_two_path)
    is_same = eq_group_obj_1 == eq_group_obj_2

    #mathmlの内容を取得
    with open(eq_group_one_path, 'r') as f:
        mathml_content_one = f.read()
    with open(eq_group_two_path, 'r') as f:
        mathml_content_two = f.read()

    #パラメーターの情報を取得
    eq_group_one_param = eq_group_obj_1.parameter.copy()
    eq_group_two_param = eq_group_obj_2.parameter.copy()

    left_col, right_col = st.beta_columns(2)
    button = st.sidebar.checkbox('show information of equation groups')

    #数式群1を表示する
    left_col.subheader('equation group one')
    for eq in eq_group_obj_1.equation_list:
        left_col.latex(sy.latex(eq))

    #数式群2を表示する
    right_col.subheader('equation group two')
    for eq in eq_group_obj_2.equation_list:
        right_col.latex(sy.latex(eq))

    #数式の詳しい情報を表示させる
    left_col_2, right_col_2 = st.beta_columns(2)
    if button:
        if right_col_2.checkbox('show the mathml content of equation group two'):
            right_col_2.text(mathml_content_two)
        if right_col_2.checkbox('show the variables to be eliminated in equation group two'):
            if eq_group_two_param:
                eq_group_two_param_str = '\hspace{0.1in}'.join(map(str, eq_group_two_param))
                right_col_2.latex(eq_group_two_param_str)
            else:
                right_col_2.text('no variables to eliminate')

        if left_col_2.checkbox('show the mathml content of equation group one'):
            left_col_2.text(mathml_content_one)
        if left_col_2.checkbox('show the variables to be eliminated in equation group one'):
            if eq_group_one_param:
                eq_group_one_param_str = '\hspace{0.1in}'.join(map(str, eq_group_one_param))
                left_col_2.latex(eq_group_one_param_str)
            else:
                left_col_2.text('no variables to eliminate')

    #同義性の判定結果を示す
    if st.sidebar.checkbox('show result'):
        if is_same:
            st.subheader('same')
        else:
            st.subheader('different')


    #判定の過程と結果を示す
    if st.sidebar.checkbox('confirm the process of judgment'):

        st.subheader('process of judgment')

        if eq_group_obj_1.degree_of_freedom != eq_group_obj_2.degree_of_freedom:
            st.write('degree of freedom different')
        else:
            st.write('equations with variables eliminated')

            left_col_3, right_col_3 = st.beta_columns(2)

            # with open('EquivalenceJudge/equation_one_final_latex.txt', 'r') as f:
            with open(cwd + '/equation_one_final_latex.txt', 'r') as f:
                for eq in f.read().strip().split('\n'):
                    left_col_3.latex(eq)

            # with open('EquivalenceJudge/equation_two_final_latex.txt', 'r') as f:
            with open(cwd + '/equation_two_final_latex.txt', 'r') as f:
                for eq in f.read().strip().split('\n'):
                    right_col_3.latex(eq)

            left_col_4, right_col_4 = st.beta_columns(2)

            #数式群1の最終形態
            eq_group_one = pickle.load(open(cwd + '/equation_one_final_pickle.dump', 'rb'))
            # eq_group_one = pickle.load(open('EquivalenceJudge/equation_one_final_pickle.dump', 'rb'))
            dfs_one=[]
            for eq in eq_group_one:
                var_lst = list(eq.free_symbols)
                index_pd = list(map(str, var_lst))
                solution_lst = []
                for var in var_lst:
                    try:
                        solution_lst.append(str(sy.solve(eq, var)[0]))
                    except:
                        solution_lst.append('no solution')

                df = pd.DataFrame({'solution':solution_lst}, index=var_lst)
                dfs_one.append(df)
            for df in dfs_one:
                left_col_4.write(df)

            #数式群2の最終形態
            eq_group_two = pickle.load(open(cwd + '/equation_two_final_pickle.dump', 'rb'))
            # eq_group_two = pickle.load(open('EquivalenceJudge/equation_two_final_pickle.dump', 'rb'))
            dfs_two = []
            for eq in eq_group_two:
                var_lst = list(eq.free_symbols)
                index_pd = list(map(str, var_lst))
                solution_lst = []
                for var in var_lst:
                    try:
                        solution_lst.append(str(sy.solve(eq, var)[0]))
                    except:
                        solution_lst.append('no solution')

                df = pd.DataFrame({'solution': solution_lst}, index=var_lst)
                dfs_two.append(df)
            for df in dfs_one:
                right_col_4.write(df)






