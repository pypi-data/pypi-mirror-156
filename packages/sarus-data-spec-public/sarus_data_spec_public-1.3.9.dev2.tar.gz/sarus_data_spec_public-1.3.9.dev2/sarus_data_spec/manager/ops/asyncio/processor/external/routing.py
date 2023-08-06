from typing import Any, AsyncIterator
import pickle as pkl

import pandas as pd
import pyarrow as pa

from sarus_data_spec.manager.asyncio.utils import async_iter
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

from .numpy import np_mean, np_std
from .pandas import (
    pd_abs,
    pd_agg,
    pd_any,
    pd_apply,
    pd_concat,
    pd_corr,
    pd_count,
    pd_describe,
    pd_drop,
    pd_droplevel,
    pd_eq,
    pd_fillna,
    pd_get_dummies,
    pd_join,
    pd_kurtosis,
    pd_loc,
    pd_mad,
    pd_mean,
    pd_median,
    pd_quantile,
    pd_rename,
    pd_round,
    pd_select_dtypes,
    pd_skew,
    pd_sort_values,
    pd_std,
    pd_sum,
    pd_to_dict,
    pd_transpose,
    pd_unique,
    pd_value_counts,
)
from .pandas_profiling import pd_profile_report
from .sklearn import (
    model_fit,
    sk_accuracy_score,
    sk_average_precision_score,
    sk_classification_report,
    sk_confusion_matrix,
    sk_cross_val_score,
    sk_f1_score,
    sk_label_encoder_fit_transform,
    sk_plot_confusion_matrix,
    sk_precision_recall_curve,
    sk_precision_score,
    sk_random_forest_classifier_predict,
    sk_recall_score,
    sk_roc_auc_score,
    sk_roc_curve,
    sk_scale,
    sk_train_test_split,
)
from .std import (
    _abs,
    _and,
    _float,
    _int,
    _or,
    _round,
    add,
    div,
    getitem,
    greater_equal,
    greater_than,
    invert,
    length,
    lower_equal,
    lower_than,
    modulo,
    mul,
    neg,
    not_equal,
    pos,
    rand,
    rdiv,
    rmodulo,
    ror,
    rsub,
    sub,
)
from .xgboost import xgb_classifier, xgb_classifier_predict


async def arrow_external(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Call external and convert the result to a RecordBatch iterator.

    We consider that external ops results are Datasets. For now, we consider
    that pandas.DataFrame are Datasets. For instance, the pd.loc operation only
    selects a subset of a Dataset and so is a Dataset.

    We call the implementation of `external` which returns arbitrary values,
    check that the result is indeed a DataFrame and convert it to a RecordBatch
    iterator.
    """
    val = await external(dataset)
    if isinstance(val, pd.DataFrame):
        return async_iter(
            pa.Table.from_pandas(val).to_batches(max_chunksize=batch_size)
        )

    else:
        raise TypeError(f"Cannot convert {type(val)} to Arrow batches.")


async def external(dataspec: st.DataSpec) -> Any:
    """Route an externally transformed Dataspec to its implementation."""
    transform_spec = dataspec.transform().protobuf().spec
    external_op = sp.Transform.ExternalOp.Name(transform_spec.external.op)
    implemented_ops = {
        "ADD": add,
        "MUL": mul,
        "SUB": sub,
        "RSUB": rsub,
        "DIV": div,
        "RDIV": rdiv,
        "INVERT": invert,
        "GETITEM": getitem,
        "LEN": length,
        "GT": greater_than,
        "GE": greater_equal,
        "LT": lower_than,
        "LE": lower_equal,
        "NE": not_equal,
        "INT": _int,
        "FLOAT": _float,
        "MOD": modulo,
        "RMOD": rmodulo,
        "ROUND": _round,
        "AND": _and,
        "RAND": rand,
        "OR": _or,
        "ROR": ror,
        "ABS": _abs,
        "POS": pos,
        "NEG": neg,
        "PD_LOC": pd_loc,
        "PD_EQ": pd_eq,
        "PD_MEAN": pd_mean,
        "PD_STD": pd_std,
        "PD_ANY": pd_any,
        "PD_DESCRIBE": pd_describe,
        "PD_SELECT_DTYPES": pd_select_dtypes,
        "NP_MEAN": np_mean,
        "NP_STD": np_std,
        "PD_PROFILE_REPORT": pd_profile_report,
        "SK_FIT": model_fit,
        "SK_SCALE": sk_scale,
        'PD_QUANTILE': pd_quantile,
        'PD_SUM': pd_sum,
        'PD_FILLNA': pd_fillna,
        'PD_ROUND': pd_round,
        'PD_RENAME': pd_rename,
        'PD_COUNT': pd_count,
        'PD_TRANSPOSE': pd_transpose,
        'PD_UNIQUE': pd_unique,
        'PD_VALUE_COUNTS': pd_value_counts,
        'PD_TO_DICT': pd_to_dict,
        'PD_APPLY': pd_apply,
        'PD_MEDIAN': pd_median,
        'PD_ABS': pd_abs,
        'PD_MAD': pd_mad,
        'PD_SKEW': pd_skew,
        'PD_KURTOSIS': pd_kurtosis,
        'PD_AGG': pd_agg,
        'PD_DROPLEVEL': pd_droplevel,
        'PD_SORT_VALUES': pd_sort_values,
        'PD_DROP': pd_drop,
        'PD_CORR': pd_corr,
        "SK_ONEHOT": model_fit,
        "SK_PCA": model_fit,
        # cluster
        "SK_AFFINITY_PROPAGATION": model_fit,
        "SK_AGGLOMERATIVE_CLUSTERING": model_fit,
        "SK_BIRCH": model_fit,
        "SK_DBSCAN": model_fit,
        "SK_FEATURE_AGGLOMERATION": model_fit,
        "SK_KMEANS": model_fit,
        "SK_MINIBATCH_KMEANS": model_fit,
        "SK_MEAN_SHIFT": model_fit,
        "SK_OPTICS": model_fit,
        "SK_SPECTRAL_CLUSTERING": model_fit,
        "SK_SPECTRAL_BICLUSTERING": model_fit,
        "SK_SPECTRAL_COCLUSTERING": model_fit,
        # ensemble
        "SK_ADABOOST_CLASSIFIER": model_fit,
        "SK_ADABOOST_REGRESSOR": model_fit,
        "SK_BAGGING_CLASSIFIER": model_fit,
        "SK_BAGGING_REGRESSOR": model_fit,
        "SK_EXTRA_TREES_CLASSIFIER": model_fit,
        "SK_EXTRA_TREES_REGRESSOR": model_fit,
        "SK_GRADIENT_BOOSTING_CLASSIFIER": model_fit,
        "SK_GRADIENT_BOOSTING_REGRESSOR": model_fit,
        "SK_ISOLATION_FOREST": model_fit,
        "SK_RANDOM_FOREST_CLASSIFIER": model_fit,
        "SK_RANDOM_FOREST_REGRESSOR": model_fit,
        "SK_RANDOM_TREES_EMBEDDING": model_fit,
        "SK_STACKING_CLASSIFIER": model_fit,
        "SK_STACKING_REGRESSOR": model_fit,
        "SK_VOTING_CLASSIFIER": model_fit,
        "SK_VOTING_REGRESSOR": model_fit,
        "SK_HIST_GRADIENT_BOOSTING_CLASSIFIER": model_fit,
        "SK_HIST_GRADIENT_BOOSTING_REGRESSOR": model_fit,
        # model selection
        "SK_CROSS_VAL_SCORE": sk_cross_val_score,
        "SK_TRAIN_TEST_SPLIT": sk_train_test_split,
        "SK_REPEATED_STRATIFIED_KFOLD": model_fit,
        # xgb
        "XGB_CLASSIFIER": xgb_classifier,
        "XGB_CLASSIFIER_PREDICT": xgb_classifier_predict,
        # pandas 2
        "PD_GET_DUMMIES": pd_get_dummies,
        "PD_JOIN": pd_join,
        "PD_CONCAT": pd_concat,
        # metrics
        "SK_ACCURACY_SCORE": sk_accuracy_score,
        "SK_AVERAGE_PRECISION_SCORE": sk_average_precision_score,
        "SK_CLASSIFICATION_REPORT": sk_classification_report,
        "SK_CONFUSION_MATRIX": sk_confusion_matrix,
        "SK_F1_SCORE": sk_f1_score,
        "SK_PLOT_CONFUSION_MATRIX": sk_plot_confusion_matrix,
        "SK_PRECISION_RECALL_CURVE": sk_precision_recall_curve,
        "SK_PRECISION_SCORE": sk_precision_score,
        "SK_RECALL_SCORE": sk_recall_score,
        "SK_ROC_AUC_SCORE": sk_roc_auc_score,
        "SK_ROC_CURVE": sk_roc_curve,
        # ensemble predict
        "SK_RANDOM_FOREST_CLASSIFIER_PREDICT": sk_random_forest_classifier_predict,
        "SK_LABEL_ENCODER_FIT_TRANSFORM": sk_label_encoder_fit_transform,
    }
    if external_op not in implemented_ops:
        raise NotImplementedError(
            f"{external_op} not in {list(implemented_ops.keys())}"
        )

    args = pkl.loads(transform_spec.external.arguments)
    kwargs = pkl.loads(transform_spec.external.named_arguments)
    func = implemented_ops[external_op]
    return await func(dataspec, *args, **kwargs)  # type: ignore
