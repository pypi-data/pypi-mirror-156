# -*- coding: utf-8 -*-
# @Time    : 2022/5/2 19:30
# @Author  : Zhongyi Hua
# @File    : functions.py
# @Usage   :
# @Note    : 

import pandas as pd
from pathos.pools import ProcessPool
from functools import partial
from os import path


def TGMI(expression, TFs, genes, permutation=1000, ncores=4):
    """
    :param expression: expression matrix. index are genes, columns are samples
    :param TFs: TFs gene list
    :param genes: pathway genes list
    :param permutation: permutation times
    :param ncores: number of parallel cores
    :return: TF-gene correlation, TF freq, gene freq
    """
    from functions import triple_interaction, p_adjust, discretize
    # generate a discretized dictionary
    discretized = expression.apply(discretize, axis=1).to_dict()
    # generate gene_pairs
    gene_name_pairs = [(gene1, gene2) for idx, gene1 in enumerate(genes) for idx2, gene2 in enumerate(genes[idx+1:])]
    gene_value_pairs = [(discretized[gene_pair[0]], discretized[gene_pair[1]]) for gene_pair in gene_name_pairs]
    tf_values = [discretized[_] for _ in TFs]

    # for parallel
    def per_tf(TF, _tf_values, _permutation, _gene_value_pairs, func1):
        tf_p_value = []
        for gene1, gene2 in _gene_value_pairs:
            p_value = func1(_tf_values, gene1, gene2, permutation=_permutation)
            tf_p_value.append(p_value)
        return TF, tf_p_value

    partial_wrapper = partial(per_tf,
                              _permutation=permutation,
                              _gene_value_pairs=gene_value_pairs,
                              func1=triple_interaction)

    pool = ProcessPool(ncores)
    tmp_result = list(pool.amap(partial_wrapper, TFs, tf_values).get())

    # tidy results
    tf_df_lst = []
    for tf_result in tmp_result:
        tmp_dict = {'TF': tf_result[0]}
        gene1 = []
        gene2 = []
        p_values = []
        for gene_names_value in zip(gene_name_pairs, tf_result[1]):
            gene1.append(gene_names_value[0][0])
            gene2.append(gene_names_value[0][1])
            p_values.append(gene_names_value[1])
        tmp_dict.update({'gene1': gene1, 'gene2': gene2, 'pvalue': p_values})
        tf_df_lst.append(pd.DataFrame(tmp_dict))
    TGMI_result = pd.concat(tf_df_lst)
    # filter MIM < 0
    TGMI_result = TGMI_result[~(TGMI_result['pvalue'] == 2)]
    # adjusted p value
    TGMI_result['padjusted'] = p_adjust(TGMI_result['pvalue'])
    # get statistics
    TGMI_result = pd.concat([
        TGMI_result[['TF', 'gene1', 'padjusted']].rename(columns={'gene1': 'gene'}),
        TGMI_result[['TF', 'gene2', 'padjusted']].rename(columns={'gene2': 'gene'})
    ])
    TGMI_network = TGMI_result.groupby(['TF', 'gene']).mean().reset_index()
    TF_network = TGMI_network[TGMI_network['padjusted'] < 0.05]
    TF_rank = TF_network.groupby('TF').count().reset_index().rename(columns={'padjusted': 'Freq'}).sort_values(by='Freq', ascending=False)
    gene_rank = TF_network.groupby('gene').count().reset_index().rename(columns={'padjusted': 'Freq'}).sort_values(by='Freq', ascending=False)
    return TF_network, TF_rank, gene_rank


def getArgs():
    import argparse
    cmdparser = argparse.ArgumentParser(
        prog="TGMI",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        -------------------------------------------------------------------------------------------------------
        %(prog)s 
        Author:  Zhongyi Hua
        Version: v1.0
        Infer Gene regulation networt (GRN) using TGMI algorithm.
        -------------------------------------------------------------------------------------------------------
        ''')
    cmdparser.add_argument('-i', '--input', required=True,
                           help='The expression matrix')
    cmdparser.add_argument('-t', '--tf', required=True,
                           help='The transcription factors (TFs) list file')
    cmdparser.add_argument('-g', '--gene', required=True,
                           help='The genes list file')
    cmdparser.add_argument('-@', '--threads', default=4,
                           help='Parallel cores number. Default: 4')
    cmdparser.add_argument('-p', '--permutation', default=1000,
                           help='Permutation times for calculate P-value. Default: 1000')
    cmdparser.add_argument('-o', '--output', required=True,
                           help='Output file path. e.g. /root/TGMI.txt')
    args = cmdparser.parse_args()
    return args


def main(args):
    tb_expression = pd.read_table(args.input)
    tb_expression.index = tb_expression.iloc[:, 0]
    tb_expression = tb_expression.iloc[:, 1:]
    tfs = open(args.tf).read().strip().split('\n')
    genes = open(args.gene).read().strip().split('\n')
    TF_network, TF_rank, gene_rank = TGMI(tb_expression, tfs, genes, permutation=args.permutation, ncores=args.threads)
    TF_network.to_csv('_network'.join(path.splitext(args.out)), sep='\t', index=False)
    TF_rank.to_csv('_TF'.join(path.splitext(args.out)), sep='\t', index=False)
    gene_rank.to_csv('_Gene'.join(path.splitext(args.out)), sep='\t', index=False)


if __name__ == '__main__':
    main(getArgs())
