# standard library
import itertools

# third party
import pandas as pd


def aggregate(df, cols, grouper, agg='mean'):
    df_count = df.groupby(grouper)[grouper].count().to_frame()
    df_agg = df.groupby(grouper)[cols].agg([agg]).round(1)
    df_agg.columns = [col for col in df_agg.columns]
    df_agg = df_count.join(df_agg)
    df_agg = df_agg.T
    df_agg['std'] = df_agg.agg('std', axis=1).round(2)
    return df_agg


def normalize_cols(df, columns, size_variable, invert=False):
    """
    Normalize a collection of columns by dividing them by a size_variable.
    If invert=True, normalize by dividing size_variable by columns instead.

    Parameters
    ==========
    :param df: `DataFrame`
    :param columns:
        Collection of column names to be normalized.
    :param size_variable: `str`
        Name of column to use as size variable.

    Optional key-word arguments
    ===========================
    :param invert: `boolean`, default=False
        If True divide size_variable by columns.

    Return
    ======
    :normalize_cols: `DataFrame`
    """

    if invert:
        df_ = 1 / df[columns].div(df[size_variable], axis=0)
        df_.columns = [f"{size_variable}/{col}" for col in columns]
    else:
        df_ = df[columns].div(df[size_variable], axis=0)
        df_.columns = [f"{col}/{size_variable}" for col in columns]
    return df.join(df_)
