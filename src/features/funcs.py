"""
Module containing data processing functions
"""

import numpy as np
import pandas as pd
from category_encoders import TargetEncoder
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

def check_nan(
        df: pd.DataFrame = None
    ):
    """
    Data summary for missing values

    Args:
        df (pd.DataFrame):
        Dataframe for analysis.

    Returns:
        pd.DataFrame: Dataframe with the amount of missing values ​​per column in the dataframe.
    """

    dic_nan = {'feature':[], 'missing_total':[], 'percentage':[]}
    total = df.shape[0]
    for col in df.columns:
        sum_na = df[col].isna().sum()
        if sum_na > 0:
            dic_nan['feature'].append(col)
            dic_nan['missing_total'].append(sum_na)
            dic_nan['percentage'].append(round(sum_na/total, 3))
    return pd.DataFrame(dic_nan)

def cat_onehotencoding(
        df: pd.DataFrame = None,
        cols_enc: list = None
    ):
    """
    Encoding categorical features

    Args:
        df (pd.DataFrame):
        Dataframe that will be used to encode the respective categorical features.

        cols_enc (list):
        A list containing the name of the columns that will be encoded.

    Returns:
        pd.DataFrame: Dataframe with the categorical columns encoded.
    """

    encoder = LabelEncoder()
    enc_mapping = list()

    for col in cols_enc:
        encoded = encoder.fit_transform(df[col].astype(str))
        df[col] = encoded
        mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
        enc_mapping.append([col, mapping])

    return df

def cat_targetencoding(
        df: pd.DataFrame = None,
        cols_enc: list = None,
        target_col: str = None
    ):
    """
    Encoding categorical features

    Args:
        df (pd.DataFrame):
        Dataframe that will be used to encode the respective categorical features.

        cols_enc (list):
        A list containing the name of the columns that will be encoded.

        target_col (str):
        A string with the name of the target column.

    Returns:
        pd.DataFrame: Dataframe with the categorical columns encoded.
    """

    encoder = TargetEncoder()

    for col in cols_enc:
        df[f'{col}_encoded'] = encoder.fit_transform(df[col], df[target_col])

    df_encoded = df.drop(cols_enc, axis=1)

    return df_encoded

def norm_features(
        df: pd.DataFrame = None,
        except_cols: list = None
    ):
    """
    Normalizing numerical features

    Args:
        df (pd.DataFrame):
        Dataframe that will be used to normalize the respective numerical features.

        except_cols (list):
        List containing the name of the numerical columns that will be excluded from df.

    Returns:
        pd.DataFrame: Dataframe with the numerical columns normalized.
    """

    num_cols = [x for x in df.select_dtypes(include=['int64', 'float64']).columns]
    cols_norm = list(set(num_cols) - set(except_cols))

    scaler = MinMaxScaler()

    for coluna in cols_norm:
        encoded = scaler.fit_transform(df[coluna].values.reshape(-1, 1))
        df[coluna] = encoded

    return df