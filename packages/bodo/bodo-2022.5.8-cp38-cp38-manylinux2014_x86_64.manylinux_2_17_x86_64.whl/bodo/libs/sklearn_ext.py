"""Support scikit-learn using object mode of Numba """
import itertools
import numbers
import types as pytypes
import warnings
from itertools import combinations
import numba
import numpy as np
import pandas as pd
import sklearn.cluster
import sklearn.ensemble
import sklearn.feature_extraction
import sklearn.linear_model
import sklearn.metrics
import sklearn.model_selection
import sklearn.naive_bayes
import sklearn.svm
import sklearn.utils
from mpi4py import MPI
from numba.core import cgutils, types
from numba.extending import NativeValue, box, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from scipy import stats
from scipy.special import comb
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import hinge_loss, log_loss, mean_squared_error
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing._data import _handle_zeros_in_scale as sklearn_handle_zeros_in_scale
from sklearn.utils._encode import _unique
from sklearn.utils.extmath import _safe_accumulator_op as sklearn_safe_accumulator_op
from sklearn.utils.validation import _check_sample_weight, column_or_1d
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.csr_matrix_ext import CSRMatrixType
from bodo.libs.distributed_api import Reduce_Type, create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks, get_num_nodes
from bodo.utils.typing import BodoError, BodoWarning, check_unsupported_args, get_overload_const, get_overload_const_int, get_overload_const_str, is_overload_constant_number, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true
_is_sklearn_supported_version = False
_min_sklearn_version = 1, 0, 0
_min_sklearn_ver_str = '.'.join(str(x) for x in _min_sklearn_version)
_max_sklearn_version_exclusive = 1, 1, 0
_max_sklearn_ver_str = '.'.join(str(x) for x in _max_sklearn_version_exclusive)
try:
    import re
    import sklearn
    regex = re.compile('(\\d+)\\.(\\d+)\\..*(\\d+)')
    sklearn_version = sklearn.__version__
    m = regex.match(sklearn_version)
    if m:
        ver = tuple(map(int, m.groups()))
        if (ver >= _min_sklearn_version and ver <
            _max_sklearn_version_exclusive):
            _is_sklearn_supported_version = True
except ImportError as efj__shkp:
    pass


def check_sklearn_version():
    if not _is_sklearn_supported_version:
        zmv__ghfog = f""" Bodo supports scikit-learn version >= {_min_sklearn_ver_str} and < {_max_sklearn_ver_str}.
             Installed version is {sklearn.__version__}.
"""
        raise BodoError(zmv__ghfog)


def random_forest_model_fit(m, X, y):
    xuqf__owps = m.n_estimators
    rinam__zhwkc = MPI.Get_processor_name()
    mvkfz__fqcb = get_host_ranks()
    crer__ftwe = len(mvkfz__fqcb)
    psc__nehtr = bodo.get_rank()
    m.n_estimators = bodo.libs.distributed_api.get_node_portion(xuqf__owps,
        crer__ftwe, psc__nehtr)
    if psc__nehtr == mvkfz__fqcb[rinam__zhwkc][0]:
        m.n_jobs = len(mvkfz__fqcb[rinam__zhwkc])
        if m.random_state is None:
            m.random_state = np.random.RandomState()
        from sklearn.utils import parallel_backend
        with parallel_backend('threading'):
            m.fit(X, y)
        m.n_jobs = 1
    with numba.objmode(first_rank_node='int32[:]'):
        first_rank_node = get_nodes_first_ranks()
    qssan__xwxli = create_subcomm_mpi4py(first_rank_node)
    if qssan__xwxli != MPI.COMM_NULL:
        ttxi__zguu = 10
        wdimx__pkwjb = bodo.libs.distributed_api.get_node_portion(xuqf__owps,
            crer__ftwe, 0)
        vzxrf__rbf = wdimx__pkwjb // ttxi__zguu
        if wdimx__pkwjb % ttxi__zguu != 0:
            vzxrf__rbf += 1
        dsntm__jmg = []
        for uhz__asaz in range(vzxrf__rbf):
            nrs__nshaw = qssan__xwxli.gather(m.estimators_[uhz__asaz *
                ttxi__zguu:uhz__asaz * ttxi__zguu + ttxi__zguu])
            if psc__nehtr == 0:
                dsntm__jmg += list(itertools.chain.from_iterable(nrs__nshaw))
        if psc__nehtr == 0:
            m.estimators_ = dsntm__jmg
    aslcq__qidqo = MPI.COMM_WORLD
    if psc__nehtr == 0:
        for uhz__asaz in range(0, xuqf__owps, 10):
            aslcq__qidqo.bcast(m.estimators_[uhz__asaz:uhz__asaz + 10])
        if isinstance(m, sklearn.ensemble.RandomForestClassifier):
            aslcq__qidqo.bcast(m.n_classes_)
            aslcq__qidqo.bcast(m.classes_)
        aslcq__qidqo.bcast(m.n_outputs_)
    else:
        rlule__hnvbp = []
        for uhz__asaz in range(0, xuqf__owps, 10):
            rlule__hnvbp += aslcq__qidqo.bcast(None)
        if isinstance(m, sklearn.ensemble.RandomForestClassifier):
            m.n_classes_ = aslcq__qidqo.bcast(None)
            m.classes_ = aslcq__qidqo.bcast(None)
        m.n_outputs_ = aslcq__qidqo.bcast(None)
        m.estimators_ = rlule__hnvbp
    assert len(m.estimators_) == xuqf__owps
    m.n_estimators = xuqf__owps
    m.n_features_in_ = X.shape[1]


class BodoRandomForestClassifierType(types.Opaque):

    def __init__(self):
        super(BodoRandomForestClassifierType, self).__init__(name=
            'BodoRandomForestClassifierType')


random_forest_classifier_type = BodoRandomForestClassifierType()
types.random_forest_classifier_type = random_forest_classifier_type
register_model(BodoRandomForestClassifierType)(models.OpaqueModel)


@typeof_impl.register(sklearn.ensemble.RandomForestClassifier)
def typeof_random_forest_classifier(val, c):
    return random_forest_classifier_type


@box(BodoRandomForestClassifierType)
def box_random_forest_classifier(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRandomForestClassifierType)
def unbox_random_forest_classifier(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.ensemble.RandomForestClassifier, no_unliteral=True)
def sklearn_ensemble_RandomForestClassifier_overload(n_estimators=100,
    criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf
    =1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=
    None, min_impurity_decrease=0.0, bootstrap=True, oob_score=False,
    n_jobs=None, random_state=None, verbose=0, warm_start=False,
    class_weight=None, ccp_alpha=0.0, max_samples=None):
    check_sklearn_version()

    def _sklearn_ensemble_RandomForestClassifier_impl(n_estimators=100,
        criterion='gini', max_depth=None, min_samples_split=2,
        min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=
        'auto', max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=
        True, oob_score=False, n_jobs=None, random_state=None, verbose=0,
        warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None):
        with numba.objmode(m='random_forest_classifier_type'):
            if random_state is not None and get_num_nodes() > 1:
                print(
                    'With multinode, fixed random_state seed values are ignored.\n'
                    )
                random_state = None
            m = sklearn.ensemble.RandomForestClassifier(n_estimators=
                n_estimators, criterion=criterion, max_depth=max_depth,
                min_samples_split=min_samples_split, min_samples_leaf=
                min_samples_leaf, min_weight_fraction_leaf=
                min_weight_fraction_leaf, max_features=max_features,
                max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=
                min_impurity_decrease, bootstrap=bootstrap, oob_score=
                oob_score, n_jobs=1, random_state=random_state, verbose=
                verbose, warm_start=warm_start, class_weight=class_weight,
                ccp_alpha=ccp_alpha, max_samples=max_samples)
        return m
    return _sklearn_ensemble_RandomForestClassifier_impl


def parallel_predict_regression(m, X):
    check_sklearn_version()

    def _model_predict_impl(m, X):
        with numba.objmode(result='float64[:]'):
            m.n_jobs = 1
            if len(X) == 0:
                result = np.empty(0, dtype=np.float64)
            else:
                result = m.predict(X).astype(np.float64).flatten()
        return result
    return _model_predict_impl


def parallel_predict(m, X):
    check_sklearn_version()

    def _model_predict_impl(m, X):
        with numba.objmode(result='int64[:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty(0, dtype=np.int64)
            else:
                result = m.predict(X).astype(np.int64).flatten()
        return result
    return _model_predict_impl


def parallel_predict_proba(m, X):
    check_sklearn_version()

    def _model_predict_proba_impl(m, X):
        with numba.objmode(result='float64[:,:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty((0, 0), dtype=np.float64)
            else:
                result = m.predict_proba(X).astype(np.float64)
        return result
    return _model_predict_proba_impl


def parallel_predict_log_proba(m, X):
    check_sklearn_version()

    def _model_predict_log_proba_impl(m, X):
        with numba.objmode(result='float64[:,:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty((0, 0), dtype=np.float64)
            else:
                result = m.predict_log_proba(X).astype(np.float64)
        return result
    return _model_predict_log_proba_impl


def parallel_score(m, X, y, sample_weight=None, _is_data_distributed=False):
    check_sklearn_version()

    def _model_score_impl(m, X, y, sample_weight=None, _is_data_distributed
        =False):
        with numba.objmode(result='float64[:]'):
            result = m.score(X, y, sample_weight=sample_weight)
            if _is_data_distributed:
                result = np.full(len(y), result)
            else:
                result = np.array([result])
        if _is_data_distributed:
            result = bodo.allgatherv(result)
        return result.mean()
    return _model_score_impl


@overload_method(BodoRandomForestClassifierType, 'predict', no_unliteral=True)
def overload_model_predict(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict. (Data parallelization)"""
    return parallel_predict(m, X)


@overload_method(BodoRandomForestClassifierType, 'predict_proba',
    no_unliteral=True)
def overload_rf_predict_proba(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict_proba. (Data parallelization)"""
    return parallel_predict_proba(m, X)


@overload_method(BodoRandomForestClassifierType, 'predict_log_proba',
    no_unliteral=True)
def overload_rf_predict_log_proba(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict_log_proba. (Data parallelization)"""
    return parallel_predict_log_proba(m, X)


@overload_method(BodoRandomForestClassifierType, 'score', no_unliteral=True)
def overload_model_score(m, X, y, sample_weight=None, _is_data_distributed=
    False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


def precision_recall_fscore_support_helper(MCM, average):

    def multilabel_confusion_matrix(y_true, y_pred, *, sample_weight=None,
        labels=None, samplewise=False):
        return MCM
    mbtos__fwia = sklearn.metrics._classification.multilabel_confusion_matrix
    result = -1.0
    try:
        sklearn.metrics._classification.multilabel_confusion_matrix = (
            multilabel_confusion_matrix)
        result = (sklearn.metrics._classification.
            precision_recall_fscore_support([], [], average=average))
    finally:
        sklearn.metrics._classification.multilabel_confusion_matrix = (
            mbtos__fwia)
    return result


@numba.njit
def precision_recall_fscore_parallel(y_true, y_pred, operation, average=
    'binary'):
    labels = bodo.libs.array_kernels.unique(y_true, parallel=True)
    labels = bodo.allgatherv(labels, False)
    labels = bodo.libs.array_kernels.sort(labels, ascending=True, inplace=False
        )
    eutu__jjej = len(labels)
    fjnb__aoyum = np.zeros(eutu__jjej, np.int64)
    owdto__svda = np.zeros(eutu__jjej, np.int64)
    jdgjj__uqfv = np.zeros(eutu__jjej, np.int64)
    mco__ioeo = (bodo.hiframes.pd_categorical_ext.
        get_label_dict_from_categories(labels))
    for uhz__asaz in range(len(y_true)):
        owdto__svda[mco__ioeo[y_true[uhz__asaz]]] += 1
        if y_pred[uhz__asaz] not in mco__ioeo:
            continue
        edq__xgt = mco__ioeo[y_pred[uhz__asaz]]
        jdgjj__uqfv[edq__xgt] += 1
        if y_true[uhz__asaz] == y_pred[uhz__asaz]:
            fjnb__aoyum[edq__xgt] += 1
    fjnb__aoyum = bodo.libs.distributed_api.dist_reduce(fjnb__aoyum, np.
        int32(Reduce_Type.Sum.value))
    owdto__svda = bodo.libs.distributed_api.dist_reduce(owdto__svda, np.
        int32(Reduce_Type.Sum.value))
    jdgjj__uqfv = bodo.libs.distributed_api.dist_reduce(jdgjj__uqfv, np.
        int32(Reduce_Type.Sum.value))
    roqvs__hnoaw = jdgjj__uqfv - fjnb__aoyum
    jnrxm__kozk = owdto__svda - fjnb__aoyum
    bqmj__asxre = fjnb__aoyum
    vflw__gfuu = y_true.shape[0] - bqmj__asxre - roqvs__hnoaw - jnrxm__kozk
    with numba.objmode(result='float64[:]'):
        MCM = np.array([vflw__gfuu, roqvs__hnoaw, jnrxm__kozk, bqmj__asxre]
            ).T.reshape(-1, 2, 2)
        if operation == 'precision':
            result = precision_recall_fscore_support_helper(MCM, average)[0]
        elif operation == 'recall':
            result = precision_recall_fscore_support_helper(MCM, average)[1]
        elif operation == 'f1':
            result = precision_recall_fscore_support_helper(MCM, average)[2]
        if average is not None:
            result = np.array([result])
    return result


@overload(sklearn.metrics.precision_score, no_unliteral=True)
def overload_precision_score(y_true, y_pred, labels=None, pos_label=1,
    average='binary', sample_weight=None, zero_division='warn',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _precision_score_impl(y_true, y_pred, labels=None,
                pos_label=1, average='binary', sample_weight=None,
                zero_division='warn', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.precision_score(y_true, y_pred,
                        labels=labels, pos_label=pos_label, average=average,
                        sample_weight=sample_weight, zero_division=
                        zero_division)
                return score
            return _precision_score_impl
        else:

            def _precision_score_impl(y_true, y_pred, labels=None,
                pos_label=1, average='binary', sample_weight=None,
                zero_division='warn', _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'precision', average=average)
            return _precision_score_impl
    elif is_overload_false(_is_data_distributed):

        def _precision_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.precision_score(y_true, y_pred,
                    labels=labels, pos_label=pos_label, average=average,
                    sample_weight=sample_weight, zero_division=zero_division)
            return score
        return _precision_score_impl
    else:

        def _precision_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred,
                'precision', average=average)
            return score[0]
        return _precision_score_impl


@overload(sklearn.metrics.recall_score, no_unliteral=True)
def overload_recall_score(y_true, y_pred, labels=None, pos_label=1, average
    ='binary', sample_weight=None, zero_division='warn',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _recall_score_impl(y_true, y_pred, labels=None, pos_label=1,
                average='binary', sample_weight=None, zero_division='warn',
                _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.recall_score(y_true, y_pred,
                        labels=labels, pos_label=pos_label, average=average,
                        sample_weight=sample_weight, zero_division=
                        zero_division)
                return score
            return _recall_score_impl
        else:

            def _recall_score_impl(y_true, y_pred, labels=None, pos_label=1,
                average='binary', sample_weight=None, zero_division='warn',
                _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'recall', average=average)
            return _recall_score_impl
    elif is_overload_false(_is_data_distributed):

        def _recall_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.recall_score(y_true, y_pred, labels
                    =labels, pos_label=pos_label, average=average,
                    sample_weight=sample_weight, zero_division=zero_division)
            return score
        return _recall_score_impl
    else:

        def _recall_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred,
                'recall', average=average)
            return score[0]
        return _recall_score_impl


@overload(sklearn.metrics.f1_score, no_unliteral=True)
def overload_f1_score(y_true, y_pred, labels=None, pos_label=1, average=
    'binary', sample_weight=None, zero_division='warn',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _f1_score_impl(y_true, y_pred, labels=None, pos_label=1,
                average='binary', sample_weight=None, zero_division='warn',
                _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.f1_score(y_true, y_pred, labels
                        =labels, pos_label=pos_label, average=average,
                        sample_weight=sample_weight, zero_division=
                        zero_division)
                return score
            return _f1_score_impl
        else:

            def _f1_score_impl(y_true, y_pred, labels=None, pos_label=1,
                average='binary', sample_weight=None, zero_division='warn',
                _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'f1', average=average)
            return _f1_score_impl
    elif is_overload_false(_is_data_distributed):

        def _f1_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.f1_score(y_true, y_pred, labels=
                    labels, pos_label=pos_label, average=average,
                    sample_weight=sample_weight, zero_division=zero_division)
            return score
        return _f1_score_impl
    else:

        def _f1_score_impl(y_true, y_pred, labels=None, pos_label=1,
            average='binary', sample_weight=None, zero_division='warn',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred, 'f1',
                average=average)
            return score[0]
        return _f1_score_impl


def mse_mae_dist_helper(y_true, y_pred, sample_weight, multioutput, squared,
    metric):
    if metric == 'mse':
        qexb__idyn = sklearn.metrics.mean_squared_error(y_true, y_pred,
            sample_weight=sample_weight, multioutput='raw_values', squared=True
            )
    elif metric == 'mae':
        qexb__idyn = sklearn.metrics.mean_absolute_error(y_true, y_pred,
            sample_weight=sample_weight, multioutput='raw_values')
    else:
        raise RuntimeError(
            f"Unrecognized metric {metric}. Must be one of 'mae' and 'mse'")
    aslcq__qidqo = MPI.COMM_WORLD
    cfj__sqsa = aslcq__qidqo.Get_size()
    if sample_weight is not None:
        psuck__odnm = np.sum(sample_weight)
    else:
        psuck__odnm = np.float64(y_true.shape[0])
    ujje__cmtm = np.zeros(cfj__sqsa, dtype=type(psuck__odnm))
    aslcq__qidqo.Allgather(psuck__odnm, ujje__cmtm)
    mmg__wzjp = np.zeros((cfj__sqsa, *qexb__idyn.shape), dtype=qexb__idyn.dtype
        )
    aslcq__qidqo.Allgather(qexb__idyn, mmg__wzjp)
    suw__sautx = np.average(mmg__wzjp, weights=ujje__cmtm, axis=0)
    if metric == 'mse' and not squared:
        suw__sautx = np.sqrt(suw__sautx)
    if isinstance(multioutput, str) and multioutput == 'raw_values':
        return suw__sautx
    elif isinstance(multioutput, str) and multioutput == 'uniform_average':
        return np.average(suw__sautx)
    else:
        return np.average(suw__sautx, weights=multioutput)


@overload(sklearn.metrics.mean_squared_error, no_unliteral=True)
def overload_mean_squared_error(y_true, y_pred, sample_weight=None,
    multioutput='uniform_average', squared=True, _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', squared=True, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=squared, metric='mse')
                    else:
                        err = sklearn.metrics.mean_squared_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput, squared=squared)
                return err
            return _mse_impl
        else:

            def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', squared=True, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=squared, metric='mse')
                    else:
                        err = sklearn.metrics.mean_squared_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput, squared=squared)
                return err
            return _mse_impl
    elif is_overload_none(sample_weight):

        def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', squared=True, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        squared, metric='mse')
                else:
                    err = sklearn.metrics.mean_squared_error(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=
                        multioutput, squared=squared)
            return err
        return _mse_impl
    else:

        def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', squared=True, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        squared, metric='mse')
                else:
                    err = sklearn.metrics.mean_squared_error(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=
                        multioutput, squared=squared)
            return err
        return _mse_impl


@overload(sklearn.metrics.mean_absolute_error, no_unliteral=True)
def overload_mean_absolute_error(y_true, y_pred, sample_weight=None,
    multioutput='uniform_average', _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=True, metric='mae')
                    else:
                        err = sklearn.metrics.mean_absolute_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput)
                return err
            return _mae_impl
        else:

            def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=True, metric='mae')
                    else:
                        err = sklearn.metrics.mean_absolute_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput)
                return err
            return _mae_impl
    elif is_overload_none(sample_weight):

        def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        True, metric='mae')
                else:
                    err = sklearn.metrics.mean_absolute_error(y_true,
                        y_pred, sample_weight=sample_weight, multioutput=
                        multioutput)
            return err
        return _mae_impl
    else:

        def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        True, metric='mae')
                else:
                    err = sklearn.metrics.mean_absolute_error(y_true,
                        y_pred, sample_weight=sample_weight, multioutput=
                        multioutput)
            return err
        return _mae_impl


def log_loss_dist_helper(y_true, y_pred, eps, normalize, sample_weight, labels
    ):
    loss = sklearn.metrics.log_loss(y_true, y_pred, eps=eps, normalize=
        False, sample_weight=sample_weight, labels=labels)
    aslcq__qidqo = MPI.COMM_WORLD
    loss = aslcq__qidqo.allreduce(loss, op=MPI.SUM)
    if normalize:
        bqshs__uxp = np.sum(sample_weight
            ) if sample_weight is not None else len(y_true)
        bqshs__uxp = aslcq__qidqo.allreduce(bqshs__uxp, op=MPI.SUM)
        loss = loss / bqshs__uxp
    return loss


@overload(sklearn.metrics.log_loss, no_unliteral=True)
def overload_log_loss(y_true, y_pred, eps=1e-15, normalize=True,
    sample_weight=None, labels=None, _is_data_distributed=False):
    check_sklearn_version()
    ohs__kjc = 'def _log_loss_impl(\n'
    ohs__kjc += '    y_true,\n'
    ohs__kjc += '    y_pred,\n'
    ohs__kjc += '    eps=1e-15,\n'
    ohs__kjc += '    normalize=True,\n'
    ohs__kjc += '    sample_weight=None,\n'
    ohs__kjc += '    labels=None,\n'
    ohs__kjc += '    _is_data_distributed=False,\n'
    ohs__kjc += '):\n'
    ohs__kjc += '    y_true = bodo.utils.conversion.coerce_to_array(y_true)\n'
    ohs__kjc += '    y_pred = bodo.utils.conversion.coerce_to_array(y_pred)\n'
    if not is_overload_none(sample_weight):
        ohs__kjc += (
            '    sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight)\n'
            )
    if not is_overload_none(labels):
        ohs__kjc += (
            '    labels = bodo.utils.conversion.coerce_to_array(labels)\n')
    ohs__kjc += "    with numba.objmode(loss='float64'):\n"
    if is_overload_false(_is_data_distributed):
        ohs__kjc += '        loss = sklearn.metrics.log_loss(\n'
    else:
        if is_overload_none(labels):
            ohs__kjc += (
                '        labels = bodo.libs.array_kernels.unique(y_true, parallel=True)\n'
                )
            ohs__kjc += '        labels = bodo.allgatherv(labels, False)\n'
        ohs__kjc += '        loss = log_loss_dist_helper(\n'
    ohs__kjc += '            y_true, y_pred, eps=eps, normalize=normalize,\n'
    ohs__kjc += '            sample_weight=sample_weight, labels=labels\n'
    ohs__kjc += '        )\n'
    ohs__kjc += '        return loss\n'
    xcc__jtzw = {}
    exec(ohs__kjc, globals(), xcc__jtzw)
    dnca__mze = xcc__jtzw['_log_loss_impl']
    return dnca__mze


def accuracy_score_dist_helper(y_true, y_pred, normalize, sample_weight):
    score = sklearn.metrics.accuracy_score(y_true, y_pred, normalize=False,
        sample_weight=sample_weight)
    aslcq__qidqo = MPI.COMM_WORLD
    score = aslcq__qidqo.allreduce(score, op=MPI.SUM)
    if normalize:
        bqshs__uxp = np.sum(sample_weight
            ) if sample_weight is not None else len(y_true)
        bqshs__uxp = aslcq__qidqo.allreduce(bqshs__uxp, op=MPI.SUM)
        score = score / bqshs__uxp
    return score


@overload(sklearn.metrics.accuracy_score, no_unliteral=True)
def overload_accuracy_score(y_true, y_pred, normalize=True, sample_weight=
    None, _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_false(_is_data_distributed):
        if is_overload_none(sample_weight):

            def _accuracy_score_impl(y_true, y_pred, normalize=True,
                sample_weight=None, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64'):
                    score = sklearn.metrics.accuracy_score(y_true, y_pred,
                        normalize=normalize, sample_weight=sample_weight)
                return score
            return _accuracy_score_impl
        else:

            def _accuracy_score_impl(y_true, y_pred, normalize=True,
                sample_weight=None, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(score='float64'):
                    score = sklearn.metrics.accuracy_score(y_true, y_pred,
                        normalize=normalize, sample_weight=sample_weight)
                return score
            return _accuracy_score_impl
    elif is_overload_none(sample_weight):

        def _accuracy_score_impl(y_true, y_pred, normalize=True,
            sample_weight=None, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = accuracy_score_dist_helper(y_true, y_pred,
                    normalize=normalize, sample_weight=sample_weight)
            return score
        return _accuracy_score_impl
    else:

        def _accuracy_score_impl(y_true, y_pred, normalize=True,
            sample_weight=None, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(score='float64'):
                score = accuracy_score_dist_helper(y_true, y_pred,
                    normalize=normalize, sample_weight=sample_weight)
            return score
        return _accuracy_score_impl


def check_consistent_length_parallel(*arrays):
    aslcq__qidqo = MPI.COMM_WORLD
    wrla__lavxv = True
    kela__cpdsy = [len(jnchg__qkk) for jnchg__qkk in arrays if jnchg__qkk
         is not None]
    if len(np.unique(kela__cpdsy)) > 1:
        wrla__lavxv = False
    wrla__lavxv = aslcq__qidqo.allreduce(wrla__lavxv, op=MPI.LAND)
    return wrla__lavxv


def r2_score_dist_helper(y_true, y_pred, sample_weight, multioutput):
    aslcq__qidqo = MPI.COMM_WORLD
    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))
    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))
    if not check_consistent_length_parallel(y_true, y_pred, sample_weight):
        raise ValueError(
            'y_true, y_pred and sample_weight (if not None) have inconsistent number of samples'
            )
    kda__pblh = y_true.shape[0]
    rbr__izvz = aslcq__qidqo.allreduce(kda__pblh, op=MPI.SUM)
    if rbr__izvz < 2:
        warnings.warn(
            'R^2 score is not well-defined with less than two samples.',
            UndefinedMetricWarning)
        return np.array([float('nan')])
    if sample_weight is not None:
        sample_weight = column_or_1d(sample_weight)
        tzo__lepsq = sample_weight[:, np.newaxis]
    else:
        sample_weight = np.float64(y_true.shape[0])
        tzo__lepsq = 1.0
    ugls__jfsm = (tzo__lepsq * (y_true - y_pred) ** 2).sum(axis=0, dtype=np
        .float64)
    nbi__bkfwo = np.zeros(ugls__jfsm.shape, dtype=ugls__jfsm.dtype)
    aslcq__qidqo.Allreduce(ugls__jfsm, nbi__bkfwo, op=MPI.SUM)
    mrmgd__eoaj = np.nansum(y_true * tzo__lepsq, axis=0, dtype=np.float64)
    uezga__xon = np.zeros_like(mrmgd__eoaj)
    aslcq__qidqo.Allreduce(mrmgd__eoaj, uezga__xon, op=MPI.SUM)
    fmvuw__pqhp = np.nansum(sample_weight, dtype=np.float64)
    hcf__xzpxp = aslcq__qidqo.allreduce(fmvuw__pqhp, op=MPI.SUM)
    zpvmr__glz = uezga__xon / hcf__xzpxp
    uuz__frsc = (tzo__lepsq * (y_true - zpvmr__glz) ** 2).sum(axis=0, dtype
        =np.float64)
    glr__naxh = np.zeros(uuz__frsc.shape, dtype=uuz__frsc.dtype)
    aslcq__qidqo.Allreduce(uuz__frsc, glr__naxh, op=MPI.SUM)
    tzim__cmqv = glr__naxh != 0
    ocokv__jls = nbi__bkfwo != 0
    drxp__gacij = tzim__cmqv & ocokv__jls
    ptchc__qzwl = np.ones([y_true.shape[1] if len(y_true.shape) > 1 else 1])
    ptchc__qzwl[drxp__gacij] = 1 - nbi__bkfwo[drxp__gacij] / glr__naxh[
        drxp__gacij]
    ptchc__qzwl[ocokv__jls & ~tzim__cmqv] = 0.0
    if isinstance(multioutput, str):
        if multioutput == 'raw_values':
            return ptchc__qzwl
        elif multioutput == 'uniform_average':
            btpe__rbt = None
        elif multioutput == 'variance_weighted':
            btpe__rbt = glr__naxh
            if not np.any(tzim__cmqv):
                if not np.any(ocokv__jls):
                    return np.array([1.0])
                else:
                    return np.array([0.0])
    else:
        btpe__rbt = multioutput
    return np.array([np.average(ptchc__qzwl, weights=btpe__rbt)])


@overload(sklearn.metrics.r2_score, no_unliteral=True)
def overload_r2_score(y_true, y_pred, sample_weight=None, multioutput=
    'uniform_average', _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) not in ['raw_values', 'uniform_average',
        'variance_weighted']:
        raise BodoError(
            f"Unsupported argument {get_overload_const_str(multioutput)} specified for 'multioutput'"
            )
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _r2_score_impl(y_true, y_pred, sample_weight=None,
                multioutput='uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    if _is_data_distributed:
                        score = r2_score_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                    else:
                        score = sklearn.metrics.r2_score(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                return score
            return _r2_score_impl
        else:

            def _r2_score_impl(y_true, y_pred, sample_weight=None,
                multioutput='uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(score='float64[:]'):
                    if _is_data_distributed:
                        score = r2_score_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                    else:
                        score = sklearn.metrics.r2_score(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                return score
            return _r2_score_impl
    elif is_overload_none(sample_weight):

        def _r2_score_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                if _is_data_distributed:
                    score = r2_score_dist_helper(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
                    score = score[0]
                else:
                    score = sklearn.metrics.r2_score(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
            return score
        return _r2_score_impl
    else:

        def _r2_score_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(score='float64'):
                if _is_data_distributed:
                    score = r2_score_dist_helper(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
                    score = score[0]
                else:
                    score = sklearn.metrics.r2_score(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
            return score
        return _r2_score_impl


def confusion_matrix_dist_helper(y_true, y_pred, labels=None, sample_weight
    =None, normalize=None):
    if normalize not in ['true', 'pred', 'all', None]:
        raise ValueError(
            "normalize must be one of {'true', 'pred', 'all', None}")
    aslcq__qidqo = MPI.COMM_WORLD
    try:
        sjhq__erqq = sklearn.metrics.confusion_matrix(y_true, y_pred,
            labels=labels, sample_weight=sample_weight, normalize=None)
    except ValueError as kwhud__tun:
        sjhq__erqq = kwhud__tun
    lbz__pbq = isinstance(sjhq__erqq, ValueError
        ) and 'At least one label specified must be in y_true' in sjhq__erqq.args[
        0]
    qzwt__wfb = aslcq__qidqo.allreduce(lbz__pbq, op=MPI.LAND)
    if qzwt__wfb:
        raise sjhq__erqq
    elif lbz__pbq:
        dtype = np.int64
        if sample_weight is not None and sample_weight.dtype.kind not in {'i',
            'u', 'b'}:
            dtype = np.float64
        xoebz__zbj = np.zeros((labels.size, labels.size), dtype=dtype)
    else:
        xoebz__zbj = sjhq__erqq
    vtfsn__pbqjc = np.zeros_like(xoebz__zbj)
    aslcq__qidqo.Allreduce(xoebz__zbj, vtfsn__pbqjc)
    with np.errstate(all='ignore'):
        if normalize == 'true':
            vtfsn__pbqjc = vtfsn__pbqjc / vtfsn__pbqjc.sum(axis=1, keepdims
                =True)
        elif normalize == 'pred':
            vtfsn__pbqjc = vtfsn__pbqjc / vtfsn__pbqjc.sum(axis=0, keepdims
                =True)
        elif normalize == 'all':
            vtfsn__pbqjc = vtfsn__pbqjc / vtfsn__pbqjc.sum()
        vtfsn__pbqjc = np.nan_to_num(vtfsn__pbqjc)
    return vtfsn__pbqjc


@overload(sklearn.metrics.confusion_matrix, no_unliteral=True)
def overload_confusion_matrix(y_true, y_pred, labels=None, sample_weight=
    None, normalize=None, _is_data_distributed=False):
    check_sklearn_version()
    ohs__kjc = 'def _confusion_matrix_impl(\n'
    ohs__kjc += '    y_true, y_pred, labels=None,\n'
    ohs__kjc += '    sample_weight=None, normalize=None,\n'
    ohs__kjc += '    _is_data_distributed=False,\n'
    ohs__kjc += '):\n'
    ohs__kjc += '    y_true = bodo.utils.conversion.coerce_to_array(y_true)\n'
    ohs__kjc += '    y_pred = bodo.utils.conversion.coerce_to_array(y_pred)\n'
    ohs__kjc += '    y_true = bodo.utils.typing.decode_if_dict_array(y_true)\n'
    ohs__kjc += '    y_pred = bodo.utils.typing.decode_if_dict_array(y_pred)\n'
    nouky__iti = 'int64[:,:]', 'np.int64'
    if not is_overload_none(normalize):
        nouky__iti = 'float64[:,:]', 'np.float64'
    if not is_overload_none(sample_weight):
        ohs__kjc += (
            '    sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight)\n'
            )
        if numba.np.numpy_support.as_dtype(sample_weight.dtype).kind not in {
            'i', 'u', 'b'}:
            nouky__iti = 'float64[:,:]', 'np.float64'
    if not is_overload_none(labels):
        ohs__kjc += (
            '    labels = bodo.utils.conversion.coerce_to_array(labels)\n')
    elif is_overload_true(_is_data_distributed):
        ohs__kjc += (
            '    labels = bodo.libs.array_kernels.concat([y_true, y_pred])\n')
        ohs__kjc += (
            '    labels = bodo.libs.array_kernels.unique(labels, parallel=True)\n'
            )
        ohs__kjc += '    labels = bodo.allgatherv(labels, False)\n'
        ohs__kjc += """    labels = bodo.libs.array_kernels.sort(labels, ascending=True, inplace=False)
"""
    ohs__kjc += f"    with numba.objmode(cm='{nouky__iti[0]}'):\n"
    if is_overload_false(_is_data_distributed):
        ohs__kjc += '      cm = sklearn.metrics.confusion_matrix(\n'
    else:
        ohs__kjc += '      cm = confusion_matrix_dist_helper(\n'
    ohs__kjc += '        y_true, y_pred, labels=labels,\n'
    ohs__kjc += '        sample_weight=sample_weight, normalize=normalize,\n'
    ohs__kjc += f'      ).astype({nouky__iti[1]})\n'
    ohs__kjc += '    return cm\n'
    xcc__jtzw = {}
    exec(ohs__kjc, globals(), xcc__jtzw)
    rfbwj__rmn = xcc__jtzw['_confusion_matrix_impl']
    return rfbwj__rmn


class BodoSGDRegressorType(types.Opaque):

    def __init__(self):
        super(BodoSGDRegressorType, self).__init__(name='BodoSGDRegressorType')


sgd_regressor_type = BodoSGDRegressorType()
types.sgd_regressor_type = sgd_regressor_type
register_model(BodoSGDRegressorType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.SGDRegressor)
def typeof_sgd_regressor(val, c):
    return sgd_regressor_type


@box(BodoSGDRegressorType)
def box_sgd_regressor(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoSGDRegressorType)
def unbox_sgd_regressor(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.SGDRegressor, no_unliteral=True)
def sklearn_linear_model_SGDRegressor_overload(loss='squared_error',
    penalty='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter
    =1000, tol=0.001, shuffle=True, verbose=0, epsilon=0.1, random_state=
    None, learning_rate='invscaling', eta0=0.01, power_t=0.25,
    early_stopping=False, validation_fraction=0.1, n_iter_no_change=5,
    warm_start=False, average=False):
    check_sklearn_version()

    def _sklearn_linear_model_SGDRegressor_impl(loss='squared_error',
        penalty='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True,
        max_iter=1000, tol=0.001, shuffle=True, verbose=0, epsilon=0.1,
        random_state=None, learning_rate='invscaling', eta0=0.01, power_t=
        0.25, early_stopping=False, validation_fraction=0.1,
        n_iter_no_change=5, warm_start=False, average=False):
        with numba.objmode(m='sgd_regressor_type'):
            m = sklearn.linear_model.SGDRegressor(loss=loss, penalty=
                penalty, alpha=alpha, l1_ratio=l1_ratio, fit_intercept=
                fit_intercept, max_iter=max_iter, tol=tol, shuffle=shuffle,
                verbose=verbose, epsilon=epsilon, random_state=random_state,
                learning_rate=learning_rate, eta0=eta0, power_t=power_t,
                early_stopping=early_stopping, validation_fraction=
                validation_fraction, n_iter_no_change=n_iter_no_change,
                warm_start=warm_start, average=average)
        return m
    return _sklearn_linear_model_SGDRegressor_impl


@overload_method(BodoSGDRegressorType, 'fit', no_unliteral=True)
def overload_sgdr_model_fit(m, X, y, coef_init=None, intercept_init=None,
    sample_weight=None, _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_true(_is_data_distributed):
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.SGDRegressor.fit() : 'sample_weight' is not supported for distributed data."
                )
        if not is_overload_none(coef_init):
            raise BodoError(
                "sklearn.linear_model.SGDRegressor.fit() : 'coef_init' is not supported for distributed data."
                )
        if not is_overload_none(intercept_init):
            raise BodoError(
                "sklearn.linear_model.SGDRegressor.fit() : 'intercept_init' is not supported for distributed data."
                )

        def _model_sgdr_fit_impl(m, X, y, coef_init=None, intercept_init=
            None, sample_weight=None, _is_data_distributed=False):
            with numba.objmode(m='sgd_regressor_type'):
                m = fit_sgd(m, X, y, _is_data_distributed)
            bodo.barrier()
            return m
        return _model_sgdr_fit_impl
    else:

        def _model_sgdr_fit_impl(m, X, y, coef_init=None, intercept_init=
            None, sample_weight=None, _is_data_distributed=False):
            with numba.objmode(m='sgd_regressor_type'):
                m = m.fit(X, y, coef_init, intercept_init, sample_weight)
            return m
        return _model_sgdr_fit_impl


@overload_method(BodoSGDRegressorType, 'predict', no_unliteral=True)
def overload_sgdr_model_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoSGDRegressorType, 'score', no_unliteral=True)
def overload_sgdr_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoSGDClassifierType(types.Opaque):

    def __init__(self):
        super(BodoSGDClassifierType, self).__init__(name=
            'BodoSGDClassifierType')


sgd_classifier_type = BodoSGDClassifierType()
types.sgd_classifier_type = sgd_classifier_type
register_model(BodoSGDClassifierType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.SGDClassifier)
def typeof_sgd_classifier(val, c):
    return sgd_classifier_type


@box(BodoSGDClassifierType)
def box_sgd_classifier(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoSGDClassifierType)
def unbox_sgd_classifier(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.SGDClassifier, no_unliteral=True)
def sklearn_linear_model_SGDClassifier_overload(loss='hinge', penalty='l2',
    alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000, tol=
    0.001, shuffle=True, verbose=0, epsilon=0.1, n_jobs=None, random_state=
    None, learning_rate='optimal', eta0=0.0, power_t=0.5, early_stopping=
    False, validation_fraction=0.1, n_iter_no_change=5, class_weight=None,
    warm_start=False, average=False):
    check_sklearn_version()

    def _sklearn_linear_model_SGDClassifier_impl(loss='hinge', penalty='l2',
        alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000, tol
        =0.001, shuffle=True, verbose=0, epsilon=0.1, n_jobs=None,
        random_state=None, learning_rate='optimal', eta0=0.0, power_t=0.5,
        early_stopping=False, validation_fraction=0.1, n_iter_no_change=5,
        class_weight=None, warm_start=False, average=False):
        with numba.objmode(m='sgd_classifier_type'):
            m = sklearn.linear_model.SGDClassifier(loss=loss, penalty=
                penalty, alpha=alpha, l1_ratio=l1_ratio, fit_intercept=
                fit_intercept, max_iter=max_iter, tol=tol, shuffle=shuffle,
                verbose=verbose, epsilon=epsilon, n_jobs=n_jobs,
                random_state=random_state, learning_rate=learning_rate,
                eta0=eta0, power_t=power_t, early_stopping=early_stopping,
                validation_fraction=validation_fraction, n_iter_no_change=
                n_iter_no_change, class_weight=class_weight, warm_start=
                warm_start, average=average)
        return m
    return _sklearn_linear_model_SGDClassifier_impl


def fit_sgd(m, X, y, y_classes=None, _is_data_distributed=False):
    aslcq__qidqo = MPI.COMM_WORLD
    bri__ajzen = aslcq__qidqo.allreduce(len(X), op=MPI.SUM)
    zqm__rgtlx = len(X) / bri__ajzen
    spgz__fqqy = aslcq__qidqo.Get_size()
    m.n_jobs = 1
    m.early_stopping = False
    wrrpn__nwjf = np.inf
    tme__kjh = 0
    if m.loss == 'hinge':
        zuqjs__xwwf = hinge_loss
    elif m.loss == 'log':
        zuqjs__xwwf = log_loss
    elif m.loss == 'squared_error':
        zuqjs__xwwf = mean_squared_error
    else:
        raise ValueError('loss {} not supported'.format(m.loss))
    rnru__igy = False
    if isinstance(m, sklearn.linear_model.SGDRegressor):
        rnru__igy = True
    for lbokl__mmnj in range(m.max_iter):
        if rnru__igy:
            m.partial_fit(X, y)
        else:
            m.partial_fit(X, y, classes=y_classes)
        m.coef_ = m.coef_ * zqm__rgtlx
        m.coef_ = aslcq__qidqo.allreduce(m.coef_, op=MPI.SUM)
        m.intercept_ = m.intercept_ * zqm__rgtlx
        m.intercept_ = aslcq__qidqo.allreduce(m.intercept_, op=MPI.SUM)
        if rnru__igy:
            y_pred = m.predict(X)
            mjdqo__gksk = zuqjs__xwwf(y, y_pred)
        else:
            y_pred = m.decision_function(X)
            mjdqo__gksk = zuqjs__xwwf(y, y_pred, labels=y_classes)
        gxy__ogdi = aslcq__qidqo.allreduce(mjdqo__gksk, op=MPI.SUM)
        mjdqo__gksk = gxy__ogdi / spgz__fqqy
        if m.tol > np.NINF and mjdqo__gksk > wrrpn__nwjf - m.tol * bri__ajzen:
            tme__kjh += 1
        else:
            tme__kjh = 0
        if mjdqo__gksk < wrrpn__nwjf:
            wrrpn__nwjf = mjdqo__gksk
        if tme__kjh >= m.n_iter_no_change:
            break
    return m


@overload_method(BodoSGDClassifierType, 'fit', no_unliteral=True)
def overload_sgdc_model_fit(m, X, y, coef_init=None, intercept_init=None,
    sample_weight=None, _is_data_distributed=False):
    check_sklearn_version()
    """
    Provide implementations for the fit function.
    In case input is replicated, we simply call sklearn,
    else we use partial_fit on each rank then use we re-compute the attributes using MPI operations.
    """
    if is_overload_true(_is_data_distributed):
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.SGDClassifier.fit() : 'sample_weight' is not supported for distributed data."
                )
        if not is_overload_none(coef_init):
            raise BodoError(
                "sklearn.linear_model.SGDClassifier.fit() : 'coef_init' is not supported for distributed data."
                )
        if not is_overload_none(intercept_init):
            raise BodoError(
                "sklearn.linear_model.SGDClassifier.fit() : 'intercept_init' is not supported for distributed data."
                )

        def _model_sgdc_fit_impl(m, X, y, coef_init=None, intercept_init=
            None, sample_weight=None, _is_data_distributed=False):
            y_classes = bodo.libs.array_kernels.unique(y, parallel=True)
            y_classes = bodo.allgatherv(y_classes, False)
            with numba.objmode(m='sgd_classifier_type'):
                m = fit_sgd(m, X, y, y_classes, _is_data_distributed)
            return m
        return _model_sgdc_fit_impl
    else:

        def _model_sgdc_fit_impl(m, X, y, coef_init=None, intercept_init=
            None, sample_weight=None, _is_data_distributed=False):
            with numba.objmode(m='sgd_classifier_type'):
                m = m.fit(X, y, coef_init, intercept_init, sample_weight)
            return m
        return _model_sgdc_fit_impl


@overload_method(BodoSGDClassifierType, 'predict', no_unliteral=True)
def overload_sgdc_model_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoSGDClassifierType, 'predict_proba', no_unliteral=True)
def overload_sgdc_model_predict_proba(m, X):
    return parallel_predict_proba(m, X)


@overload_method(BodoSGDClassifierType, 'predict_log_proba', no_unliteral=True)
def overload_sgdc_model_predict_log_proba(m, X):
    return parallel_predict_log_proba(m, X)


@overload_method(BodoSGDClassifierType, 'score', no_unliteral=True)
def overload_sgdc_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoSGDClassifierType, 'coef_')
def get_sgdc_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:,:]'):
            result = m.coef_
        return result
    return impl


class BodoKMeansClusteringType(types.Opaque):

    def __init__(self):
        super(BodoKMeansClusteringType, self).__init__(name=
            'BodoKMeansClusteringType')


kmeans_clustering_type = BodoKMeansClusteringType()
types.kmeans_clustering_type = kmeans_clustering_type
register_model(BodoKMeansClusteringType)(models.OpaqueModel)


@typeof_impl.register(sklearn.cluster.KMeans)
def typeof_kmeans_clustering(val, c):
    return kmeans_clustering_type


@box(BodoKMeansClusteringType)
def box_kmeans_clustering(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoKMeansClusteringType)
def unbox_kmeans_clustering(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.cluster.KMeans, no_unliteral=True)
def sklearn_cluster_kmeans_overload(n_clusters=8, init='k-means++', n_init=
    10, max_iter=300, tol=0.0001, verbose=0, random_state=None, copy_x=True,
    algorithm='auto'):
    check_sklearn_version()

    def _sklearn_cluster_kmeans_impl(n_clusters=8, init='k-means++', n_init
        =10, max_iter=300, tol=0.0001, verbose=0, random_state=None, copy_x
        =True, algorithm='auto'):
        with numba.objmode(m='kmeans_clustering_type'):
            m = sklearn.cluster.KMeans(n_clusters=n_clusters, init=init,
                n_init=n_init, max_iter=max_iter, tol=tol, verbose=verbose,
                random_state=random_state, copy_x=copy_x, algorithm=algorithm)
        return m
    return _sklearn_cluster_kmeans_impl


def kmeans_fit_helper(m, len_X, all_X, all_sample_weight, _is_data_distributed
    ):
    aslcq__qidqo = MPI.COMM_WORLD
    psc__nehtr = aslcq__qidqo.Get_rank()
    rinam__zhwkc = MPI.Get_processor_name()
    mvkfz__fqcb = get_host_ranks()
    llqic__kjef = m.n_jobs if hasattr(m, 'n_jobs') else None
    ffe__fci = m._n_threads if hasattr(m, '_n_threads') else None
    m._n_threads = len(mvkfz__fqcb[rinam__zhwkc])
    if psc__nehtr == 0:
        m.fit(X=all_X, y=None, sample_weight=all_sample_weight)
    if psc__nehtr == 0:
        aslcq__qidqo.bcast(m.cluster_centers_)
        aslcq__qidqo.bcast(m.inertia_)
        aslcq__qidqo.bcast(m.n_iter_)
    else:
        m.cluster_centers_ = aslcq__qidqo.bcast(None)
        m.inertia_ = aslcq__qidqo.bcast(None)
        m.n_iter_ = aslcq__qidqo.bcast(None)
    if _is_data_distributed:
        qhrz__jlui = aslcq__qidqo.allgather(len_X)
        if psc__nehtr == 0:
            ofx__yhb = np.empty(len(qhrz__jlui) + 1, dtype=int)
            np.cumsum(qhrz__jlui, out=ofx__yhb[1:])
            ofx__yhb[0] = 0
            wmn__dzp = [m.labels_[ofx__yhb[tjus__welo]:ofx__yhb[tjus__welo +
                1]] for tjus__welo in range(len(qhrz__jlui))]
            jwpa__zza = aslcq__qidqo.scatter(wmn__dzp)
        else:
            jwpa__zza = aslcq__qidqo.scatter(None)
        m.labels_ = jwpa__zza
    elif psc__nehtr == 0:
        aslcq__qidqo.bcast(m.labels_)
    else:
        m.labels_ = aslcq__qidqo.bcast(None)
    m._n_threads = ffe__fci
    return m


@overload_method(BodoKMeansClusteringType, 'fit', no_unliteral=True)
def overload_kmeans_clustering_fit(m, X, y=None, sample_weight=None,
    _is_data_distributed=False):

    def _cluster_kmeans_fit_impl(m, X, y=None, sample_weight=None,
        _is_data_distributed=False):
        if _is_data_distributed:
            all_X = bodo.gatherv(X)
            if sample_weight is not None:
                all_sample_weight = bodo.gatherv(sample_weight)
            else:
                all_sample_weight = None
        else:
            all_X = X
            all_sample_weight = sample_weight
        with numba.objmode(m='kmeans_clustering_type'):
            m = kmeans_fit_helper(m, len(X), all_X, all_sample_weight,
                _is_data_distributed)
        return m
    return _cluster_kmeans_fit_impl


def kmeans_predict_helper(m, X, sample_weight):
    ffe__fci = m._n_threads if hasattr(m, '_n_threads') else None
    m._n_threads = 1
    if len(X) == 0:
        preds = np.empty(0, dtype=np.int64)
    else:
        preds = m.predict(X, sample_weight).astype(np.int64).flatten()
    m._n_threads = ffe__fci
    return preds


@overload_method(BodoKMeansClusteringType, 'predict', no_unliteral=True)
def overload_kmeans_clustering_predict(m, X, sample_weight=None):

    def _cluster_kmeans_predict(m, X, sample_weight=None):
        with numba.objmode(preds='int64[:]'):
            preds = kmeans_predict_helper(m, X, sample_weight)
        return preds
    return _cluster_kmeans_predict


@overload_method(BodoKMeansClusteringType, 'score', no_unliteral=True)
def overload_kmeans_clustering_score(m, X, y=None, sample_weight=None,
    _is_data_distributed=False):

    def _cluster_kmeans_score(m, X, y=None, sample_weight=None,
        _is_data_distributed=False):
        with numba.objmode(result='float64'):
            ffe__fci = m._n_threads if hasattr(m, '_n_threads') else None
            m._n_threads = 1
            if len(X) == 0:
                result = 0
            else:
                result = m.score(X, y=y, sample_weight=sample_weight)
            if _is_data_distributed:
                aslcq__qidqo = MPI.COMM_WORLD
                result = aslcq__qidqo.allreduce(result, op=MPI.SUM)
            m._n_threads = ffe__fci
        return result
    return _cluster_kmeans_score


@overload_method(BodoKMeansClusteringType, 'transform', no_unliteral=True)
def overload_kmeans_clustering_transform(m, X):

    def _cluster_kmeans_transform(m, X):
        with numba.objmode(X_new='float64[:,:]'):
            ffe__fci = m._n_threads if hasattr(m, '_n_threads') else None
            m._n_threads = 1
            if len(X) == 0:
                X_new = np.empty((0, m.n_clusters), dtype=np.int64)
            else:
                X_new = m.transform(X).astype(np.float64)
            m._n_threads = ffe__fci
        return X_new
    return _cluster_kmeans_transform


class BodoMultinomialNBType(types.Opaque):

    def __init__(self):
        super(BodoMultinomialNBType, self).__init__(name=
            'BodoMultinomialNBType')


multinomial_nb_type = BodoMultinomialNBType()
types.multinomial_nb_type = multinomial_nb_type
register_model(BodoMultinomialNBType)(models.OpaqueModel)


@typeof_impl.register(sklearn.naive_bayes.MultinomialNB)
def typeof_multinomial_nb(val, c):
    return multinomial_nb_type


@box(BodoMultinomialNBType)
def box_multinomial_nb(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoMultinomialNBType)
def unbox_multinomial_nb(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.naive_bayes.MultinomialNB, no_unliteral=True)
def sklearn_naive_bayes_multinomialnb_overload(alpha=1.0, fit_prior=True,
    class_prior=None):
    check_sklearn_version()

    def _sklearn_naive_bayes_multinomialnb_impl(alpha=1.0, fit_prior=True,
        class_prior=None):
        with numba.objmode(m='multinomial_nb_type'):
            m = sklearn.naive_bayes.MultinomialNB(alpha=alpha, fit_prior=
                fit_prior, class_prior=class_prior)
        return m
    return _sklearn_naive_bayes_multinomialnb_impl


@overload_method(BodoMultinomialNBType, 'fit', no_unliteral=True)
def overload_multinomial_nb_model_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _naive_bayes_multinomial_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _naive_bayes_multinomial_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.naive_bayes.MultinomialNB.fit() : 'sample_weight' not supported."
                )
        ohs__kjc = 'def _model_multinomial_nb_fit_impl(\n'
        ohs__kjc += (
            '    m, X, y, sample_weight=None, _is_data_distributed=False\n')
        ohs__kjc += '):  # pragma: no cover\n'
        ohs__kjc += '    y = bodo.utils.conversion.coerce_to_ndarray(y)\n'
        if isinstance(X, DataFrameType):
            ohs__kjc += '    X = X.to_numpy()\n'
        else:
            ohs__kjc += '    X = bodo.utils.conversion.coerce_to_ndarray(X)\n'
        ohs__kjc += '    my_rank = bodo.get_rank()\n'
        ohs__kjc += '    nranks = bodo.get_size()\n'
        ohs__kjc += '    total_cols = X.shape[1]\n'
        ohs__kjc += '    for i in range(nranks):\n'
        ohs__kjc += (
            '        start = bodo.libs.distributed_api.get_start(total_cols, nranks, i)\n'
            )
        ohs__kjc += (
            '        end = bodo.libs.distributed_api.get_end(total_cols, nranks, i)\n'
            )
        ohs__kjc += '        if i == my_rank:\n'
        ohs__kjc += (
            '            X_train = bodo.gatherv(X[:, start:end:1], root=i)\n')
        ohs__kjc += '        else:\n'
        ohs__kjc += '            bodo.gatherv(X[:, start:end:1], root=i)\n'
        ohs__kjc += '    y_train = bodo.allgatherv(y, False)\n'
        ohs__kjc += '    with numba.objmode(m="multinomial_nb_type"):\n'
        ohs__kjc += '        m = fit_multinomial_nb(\n'
        ohs__kjc += """            m, X_train, y_train, sample_weight, total_cols, _is_data_distributed
"""
        ohs__kjc += '        )\n'
        ohs__kjc += '    bodo.barrier()\n'
        ohs__kjc += '    return m\n'
        xcc__jtzw = {}
        exec(ohs__kjc, globals(), xcc__jtzw)
        tkrhe__elbi = xcc__jtzw['_model_multinomial_nb_fit_impl']
        return tkrhe__elbi


def fit_multinomial_nb(m, X_train, y_train, sample_weight=None, total_cols=
    0, _is_data_distributed=False):
    m._check_X_y(X_train, y_train)
    lbokl__mmnj, n_features = X_train.shape
    m.n_features_in_ = n_features
    srfqc__qmvqa = LabelBinarizer()
    idvo__pkpz = srfqc__qmvqa.fit_transform(y_train)
    m.classes_ = srfqc__qmvqa.classes_
    if idvo__pkpz.shape[1] == 1:
        idvo__pkpz = np.concatenate((1 - idvo__pkpz, idvo__pkpz), axis=1)
    if sample_weight is not None:
        idvo__pkpz = idvo__pkpz.astype(np.float64, copy=False)
        sample_weight = _check_sample_weight(sample_weight, X_train)
        sample_weight = np.atleast_2d(sample_weight)
        idvo__pkpz *= sample_weight.T
    class_prior = m.class_prior
    hwl__voiay = idvo__pkpz.shape[1]
    m._init_counters(hwl__voiay, n_features)
    m._count(X_train.astype('float64'), idvo__pkpz)
    alpha = m._check_alpha()
    m._update_class_log_prior(class_prior=class_prior)
    twapq__updf = m.feature_count_ + alpha
    crml__kxgs = twapq__updf.sum(axis=1)
    aslcq__qidqo = MPI.COMM_WORLD
    spgz__fqqy = aslcq__qidqo.Get_size()
    cglyq__qbat = np.zeros(hwl__voiay)
    aslcq__qidqo.Allreduce(crml__kxgs, cglyq__qbat, op=MPI.SUM)
    eiip__xno = np.log(twapq__updf) - np.log(cglyq__qbat.reshape(-1, 1))
    kad__wboij = eiip__xno.T.reshape(n_features * hwl__voiay)
    htp__gkn = np.ones(spgz__fqqy) * (total_cols // spgz__fqqy)
    vxqug__sphy = total_cols % spgz__fqqy
    for rxar__bxg in range(vxqug__sphy):
        htp__gkn[rxar__bxg] += 1
    htp__gkn *= hwl__voiay
    korgc__dyh = np.zeros(spgz__fqqy, dtype=np.int32)
    korgc__dyh[1:] = np.cumsum(htp__gkn)[:-1]
    xdrxp__lby = np.zeros((total_cols, hwl__voiay), dtype=np.float64)
    aslcq__qidqo.Allgatherv(kad__wboij, [xdrxp__lby, htp__gkn, korgc__dyh,
        MPI.DOUBLE_PRECISION])
    m.feature_log_prob_ = xdrxp__lby.T
    m.n_features_in_ = m.feature_log_prob_.shape[1]
    return m


@overload_method(BodoMultinomialNBType, 'predict', no_unliteral=True)
def overload_multinomial_nb_model_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoMultinomialNBType, 'score', no_unliteral=True)
def overload_multinomial_nb_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoLogisticRegressionType(types.Opaque):

    def __init__(self):
        super(BodoLogisticRegressionType, self).__init__(name=
            'BodoLogisticRegressionType')


logistic_regression_type = BodoLogisticRegressionType()
types.logistic_regression_type = logistic_regression_type
register_model(BodoLogisticRegressionType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.LogisticRegression)
def typeof_logistic_regression(val, c):
    return logistic_regression_type


@box(BodoLogisticRegressionType)
def box_logistic_regression(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLogisticRegressionType)
def unbox_logistic_regression(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.LogisticRegression, no_unliteral=True)
def sklearn_linear_model_logistic_regression_overload(penalty='l2', dual=
    False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1,
    class_weight=None, random_state=None, solver='lbfgs', max_iter=100,
    multi_class='auto', verbose=0, warm_start=False, n_jobs=None, l1_ratio=None
    ):
    check_sklearn_version()

    def _sklearn_linear_model_logistic_regression_impl(penalty='l2', dual=
        False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1,
        class_weight=None, random_state=None, solver='lbfgs', max_iter=100,
        multi_class='auto', verbose=0, warm_start=False, n_jobs=None,
        l1_ratio=None):
        with numba.objmode(m='logistic_regression_type'):
            m = sklearn.linear_model.LogisticRegression(penalty=penalty,
                dual=dual, tol=tol, C=C, fit_intercept=fit_intercept,
                intercept_scaling=intercept_scaling, class_weight=
                class_weight, random_state=random_state, solver=solver,
                max_iter=max_iter, multi_class=multi_class, verbose=verbose,
                warm_start=warm_start, n_jobs=n_jobs, l1_ratio=l1_ratio)
        return m
    return _sklearn_linear_model_logistic_regression_impl


@register_jitable
def _raise_SGD_warning(sgd_name):
    with numba.objmode:
        warnings.warn(
            f'Data is distributed so Bodo will fit model with SGD solver optimization ({sgd_name})'
            , BodoWarning)


@overload_method(BodoLogisticRegressionType, 'fit', no_unliteral=True)
def overload_logistic_regression_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _logistic_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _logistic_regression_fit_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.LogisticRegression.fit() : 'sample_weight' is not supported for distributed data."
                )

        def _sgdc_logistic_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDClassifier')
            with numba.objmode(clf='sgd_classifier_type'):
                if m.l1_ratio is None:
                    l1_ratio = 0.15
                else:
                    l1_ratio = m.l1_ratio
                clf = sklearn.linear_model.SGDClassifier(loss='log',
                    penalty=m.penalty, tol=m.tol, fit_intercept=m.
                    fit_intercept, class_weight=m.class_weight,
                    random_state=m.random_state, max_iter=m.max_iter,
                    verbose=m.verbose, warm_start=m.warm_start, n_jobs=m.
                    n_jobs, l1_ratio=l1_ratio)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
                m.classes_ = clf.classes_
            return m
        return _sgdc_logistic_regression_fit_impl


@overload_method(BodoLogisticRegressionType, 'predict', no_unliteral=True)
def overload_logistic_regression_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoLogisticRegressionType, 'predict_proba', no_unliteral=True
    )
def overload_logistic_regression_predict_proba(m, X):
    return parallel_predict_proba(m, X)


@overload_method(BodoLogisticRegressionType, 'predict_log_proba',
    no_unliteral=True)
def overload_logistic_regression_predict_log_proba(m, X):
    return parallel_predict_log_proba(m, X)


@overload_method(BodoLogisticRegressionType, 'score', no_unliteral=True)
def overload_logistic_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoLogisticRegressionType, 'coef_')
def get_logisticR_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:,:]'):
            result = m.coef_
        return result
    return impl


class BodoLinearRegressionType(types.Opaque):

    def __init__(self):
        super(BodoLinearRegressionType, self).__init__(name=
            'BodoLinearRegressionType')


linear_regression_type = BodoLinearRegressionType()
types.linear_regression_type = linear_regression_type
register_model(BodoLinearRegressionType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.LinearRegression)
def typeof_linear_regression(val, c):
    return linear_regression_type


@box(BodoLinearRegressionType)
def box_linear_regression(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLinearRegressionType)
def unbox_linear_regression(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.LinearRegression, no_unliteral=True)
def sklearn_linear_model_linear_regression_overload(fit_intercept=True,
    copy_X=True, n_jobs=None, positive=False):
    check_sklearn_version()

    def _sklearn_linear_model_linear_regression_impl(fit_intercept=True,
        copy_X=True, n_jobs=None, positive=False):
        with numba.objmode(m='linear_regression_type'):
            m = sklearn.linear_model.LinearRegression(fit_intercept=
                fit_intercept, copy_X=copy_X, n_jobs=n_jobs, positive=positive)
        return m
    return _sklearn_linear_model_linear_regression_impl


@overload_method(BodoLinearRegressionType, 'fit', no_unliteral=True)
def overload_linear_regression_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _linear_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _linear_regression_fit_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.LinearRegression.fit() : 'sample_weight' is not supported for distributed data."
                )

        def _sgdc_linear_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                clf = sklearn.linear_model.SGDRegressor(loss=
                    'squared_error', penalty=None, fit_intercept=m.
                    fit_intercept)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
            return m
        return _sgdc_linear_regression_fit_impl


@overload_method(BodoLinearRegressionType, 'predict', no_unliteral=True)
def overload_linear_regression_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoLinearRegressionType, 'score', no_unliteral=True)
def overload_linear_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoLinearRegressionType, 'coef_')
def get_lr_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.coef_
        return result
    return impl


class BodoLassoType(types.Opaque):

    def __init__(self):
        super(BodoLassoType, self).__init__(name='BodoLassoType')


lasso_type = BodoLassoType()
types.lasso_type = lasso_type
register_model(BodoLassoType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.Lasso)
def typeof_lasso(val, c):
    return lasso_type


@box(BodoLassoType)
def box_lasso(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLassoType)
def unbox_lasso(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.Lasso, no_unliteral=True)
def sklearn_linear_model_lasso_overload(alpha=1.0, fit_intercept=True,
    precompute=False, copy_X=True, max_iter=1000, tol=0.0001, warm_start=
    False, positive=False, random_state=None, selection='cyclic'):
    check_sklearn_version()

    def _sklearn_linear_model_lasso_impl(alpha=1.0, fit_intercept=True,
        precompute=False, copy_X=True, max_iter=1000, tol=0.0001,
        warm_start=False, positive=False, random_state=None, selection='cyclic'
        ):
        with numba.objmode(m='lasso_type'):
            m = sklearn.linear_model.Lasso(alpha=alpha, fit_intercept=
                fit_intercept, precompute=precompute, copy_X=copy_X,
                max_iter=max_iter, tol=tol, warm_start=warm_start, positive
                =positive, random_state=random_state, selection=selection)
        return m
    return _sklearn_linear_model_lasso_impl


@overload_method(BodoLassoType, 'fit', no_unliteral=True)
def overload_lasso_fit(m, X, y, sample_weight=None, check_input=True,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _lasso_fit_impl(m, X, y, sample_weight=None, check_input=True,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight, check_input)
            return m
        return _lasso_fit_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.Lasso.fit() : 'sample_weight' is not supported for distributed data."
                )
        if not is_overload_true(check_input):
            raise BodoError(
                "sklearn.linear_model.Lasso.fit() : 'check_input' is not supported for distributed data."
                )

        def _sgdc_lasso_fit_impl(m, X, y, sample_weight=None, check_input=
            True, _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                clf = sklearn.linear_model.SGDRegressor(loss=
                    'squared_error', penalty='l1', alpha=m.alpha,
                    fit_intercept=m.fit_intercept, max_iter=m.max_iter, tol
                    =m.tol, warm_start=m.warm_start, random_state=m.
                    random_state)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
            return m
        return _sgdc_lasso_fit_impl


@overload_method(BodoLassoType, 'predict', no_unliteral=True)
def overload_lass_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoLassoType, 'score', no_unliteral=True)
def overload_lasso_score(m, X, y, sample_weight=None, _is_data_distributed=
    False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoRidgeType(types.Opaque):

    def __init__(self):
        super(BodoRidgeType, self).__init__(name='BodoRidgeType')


ridge_type = BodoRidgeType()
types.ridge_type = ridge_type
register_model(BodoRidgeType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.Ridge)
def typeof_ridge(val, c):
    return ridge_type


@box(BodoRidgeType)
def box_ridge(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRidgeType)
def unbox_ridge(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.Ridge, no_unliteral=True)
def sklearn_linear_model_ridge_overload(alpha=1.0, fit_intercept=True,
    copy_X=True, max_iter=None, tol=0.001, solver='auto', positive=False,
    random_state=None):
    check_sklearn_version()

    def _sklearn_linear_model_ridge_impl(alpha=1.0, fit_intercept=True,
        copy_X=True, max_iter=None, tol=0.001, solver='auto', positive=
        False, random_state=None):
        with numba.objmode(m='ridge_type'):
            m = sklearn.linear_model.Ridge(alpha=alpha, fit_intercept=
                fit_intercept, copy_X=copy_X, max_iter=max_iter, tol=tol,
                solver=solver, positive=positive, random_state=random_state)
        return m
    return _sklearn_linear_model_ridge_impl


@overload_method(BodoRidgeType, 'fit', no_unliteral=True)
def overload_ridge_fit(m, X, y, sample_weight=None, _is_data_distributed=False
    ):
    if is_overload_false(_is_data_distributed):

        def _ridge_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _ridge_fit_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.linear_model.Ridge.fit() : 'sample_weight' is not supported for distributed data."
                )

        def _ridge_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                if m.max_iter is None:
                    max_iter = 1000
                else:
                    max_iter = m.max_iter
                clf = sklearn.linear_model.SGDRegressor(loss=
                    'squared_error', penalty='l2', alpha=0.001,
                    fit_intercept=m.fit_intercept, max_iter=max_iter, tol=m
                    .tol, random_state=m.random_state)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
            return m
        return _ridge_fit_impl


@overload_method(BodoRidgeType, 'predict', no_unliteral=True)
def overload_linear_regression_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoRidgeType, 'score', no_unliteral=True)
def overload_linear_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoRidgeType, 'coef_')
def get_ridge_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.coef_
        return result
    return impl


class BodoLinearSVCType(types.Opaque):

    def __init__(self):
        super(BodoLinearSVCType, self).__init__(name='BodoLinearSVCType')


linear_svc_type = BodoLinearSVCType()
types.linear_svc_type = linear_svc_type
register_model(BodoLinearSVCType)(models.OpaqueModel)


@typeof_impl.register(sklearn.svm.LinearSVC)
def typeof_linear_svc(val, c):
    return linear_svc_type


@box(BodoLinearSVCType)
def box_linear_svc(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLinearSVCType)
def unbox_linear_svc(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.svm.LinearSVC, no_unliteral=True)
def sklearn_svm_linear_svc_overload(penalty='l2', loss='squared_hinge',
    dual=True, tol=0.0001, C=1.0, multi_class='ovr', fit_intercept=True,
    intercept_scaling=1, class_weight=None, verbose=0, random_state=None,
    max_iter=1000):
    check_sklearn_version()

    def _sklearn_svm_linear_svc_impl(penalty='l2', loss='squared_hinge',
        dual=True, tol=0.0001, C=1.0, multi_class='ovr', fit_intercept=True,
        intercept_scaling=1, class_weight=None, verbose=0, random_state=
        None, max_iter=1000):
        with numba.objmode(m='linear_svc_type'):
            m = sklearn.svm.LinearSVC(penalty=penalty, loss=loss, dual=dual,
                tol=tol, C=C, multi_class=multi_class, fit_intercept=
                fit_intercept, intercept_scaling=intercept_scaling,
                class_weight=class_weight, verbose=verbose, random_state=
                random_state, max_iter=max_iter)
        return m
    return _sklearn_svm_linear_svc_impl


@overload_method(BodoLinearSVCType, 'fit', no_unliteral=True)
def overload_linear_svc_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _svm_linear_svc_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _svm_linear_svc_fit_impl
    else:
        if not is_overload_none(sample_weight):
            raise BodoError(
                "sklearn.svm.LinearSVC.fit() : 'sample_weight' is not supported for distributed data."
                )

        def _svm_linear_svc_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDClassifier')
            with numba.objmode(clf='sgd_classifier_type'):
                clf = sklearn.linear_model.SGDClassifier(loss='hinge',
                    penalty=m.penalty, tol=m.tol, fit_intercept=m.
                    fit_intercept, class_weight=m.class_weight,
                    random_state=m.random_state, max_iter=m.max_iter,
                    verbose=m.verbose)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
                m.classes_ = clf.classes_
            return m
        return _svm_linear_svc_fit_impl


@overload_method(BodoLinearSVCType, 'predict', no_unliteral=True)
def overload_svm_linear_svc_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoLinearSVCType, 'score', no_unliteral=True)
def overload_svm_linear_svc_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoPreprocessingOneHotEncoderType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingOneHotEncoderType, self).__init__(name=
            'BodoPreprocessingOneHotEncoderType')


preprocessing_one_hot_encoder_type = BodoPreprocessingOneHotEncoderType()
types.preprocessing_one_hot_encoder_type = preprocessing_one_hot_encoder_type
register_model(BodoPreprocessingOneHotEncoderType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.OneHotEncoder)
def typeof_preprocessing_one_hot_encoder(val, c):
    return preprocessing_one_hot_encoder_type


@box(BodoPreprocessingOneHotEncoderType)
def box_preprocessing_one_hot_encoder(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingOneHotEncoderType)
def unbox_preprocessing_one_hot_encoder(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


class BodoPreprocessingOneHotEncoderCategoriesType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingOneHotEncoderCategoriesType, self).__init__(name
            ='BodoPreprocessingOneHotEncoderCategoriesType')


preprocessing_one_hot_encoder_categories_type = (
    BodoPreprocessingOneHotEncoderCategoriesType())
types.preprocessing_one_hot_encoder_categories_type = (
    preprocessing_one_hot_encoder_categories_type)
register_model(BodoPreprocessingOneHotEncoderCategoriesType)(models.OpaqueModel
    )


@box(BodoPreprocessingOneHotEncoderCategoriesType)
def box_preprocessing_one_hot_encoder_categories(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingOneHotEncoderCategoriesType)
def unbox_preprocessing_one_hot_encoder_categories(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


class BodoPreprocessingOneHotEncoderDropIdxType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingOneHotEncoderDropIdxType, self).__init__(name
            ='BodoPreprocessingOneHotEncoderDropIdxType')


preprocessing_one_hot_encoder_drop_idx_type = (
    BodoPreprocessingOneHotEncoderDropIdxType())
types.preprocessing_one_hot_encoder_drop_idx_type = (
    preprocessing_one_hot_encoder_drop_idx_type)
register_model(BodoPreprocessingOneHotEncoderDropIdxType)(models.OpaqueModel)


@box(BodoPreprocessingOneHotEncoderDropIdxType)
def box_preprocessing_one_hot_encoder_drop_idx(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingOneHotEncoderDropIdxType)
def unbox_preprocessing_one_hot_encoder_drop_idx(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload_attribute(BodoPreprocessingOneHotEncoderType, 'categories_')
def get_one_hot_encoder_categories_(m):

    def impl(m):
        with numba.objmode(result=
            'preprocessing_one_hot_encoder_categories_type'):
            result = m.categories_
        return result
    return impl


@overload_attribute(BodoPreprocessingOneHotEncoderType, 'drop_idx_')
def get_one_hot_encoder_drop_idx_(m):

    def impl(m):
        with numba.objmode(result='preprocessing_one_hot_encoder_drop_idx_type'
            ):
            result = m.drop_idx_
        return result
    return impl


@overload_attribute(BodoPreprocessingOneHotEncoderType, 'n_features_in_')
def get_one_hot_encoder_n_features_in_(m):

    def impl(m):
        with numba.objmode(result='int64'):
            result = m.n_features_in_
        return result
    return impl


@overload(sklearn.preprocessing.OneHotEncoder, no_unliteral=True)
def sklearn_preprocessing_one_hot_encoder_overload(categories='auto', drop=
    None, sparse=True, dtype=np.float64, handle_unknown='error'):
    check_sklearn_version()
    cyp__phrjj = {'sparse': sparse, 'dtype': 'float64' if 'float64' in repr
        (dtype) else repr(dtype)}
    jblbl__pesc = {'sparse': False, 'dtype': 'float64'}
    check_unsupported_args('OneHotEncoder', cyp__phrjj, jblbl__pesc, 'ml')

    def _sklearn_preprocessing_one_hot_encoder_impl(categories='auto', drop
        =None, sparse=True, dtype=np.float64, handle_unknown='error'):
        with numba.objmode(m='preprocessing_one_hot_encoder_type'):
            m = sklearn.preprocessing.OneHotEncoder(categories=categories,
                drop=drop, sparse=sparse, dtype=dtype, handle_unknown=
                handle_unknown)
        return m
    return _sklearn_preprocessing_one_hot_encoder_impl


def sklearn_preprocessing_one_hot_encoder_fit_dist_helper(m, X):
    aslcq__qidqo = MPI.COMM_WORLD
    try:
        bakbs__hgns = m._fit(X, handle_unknown=m.handle_unknown,
            force_all_finite='allow-nan')
    except ValueError as kwhud__tun:
        if 'Found unknown categories' in kwhud__tun.args[0]:
            bakbs__hgns = kwhud__tun
        else:
            raise kwhud__tun
    nnjp__bvdj = int(isinstance(bakbs__hgns, ValueError))
    veab__uxotl, klt__lwy = aslcq__qidqo.allreduce((nnjp__bvdj,
        aslcq__qidqo.Get_rank()), op=MPI.MAXLOC)
    if veab__uxotl:
        if aslcq__qidqo.Get_rank() == klt__lwy:
            sjexr__ftgxd = bakbs__hgns.args[0]
        else:
            sjexr__ftgxd = None
        sjexr__ftgxd = aslcq__qidqo.bcast(sjexr__ftgxd, root=klt__lwy)
        if nnjp__bvdj:
            raise bakbs__hgns
        else:
            raise ValueError(sjexr__ftgxd)
    if m.categories == 'auto':
        dfamf__tlh = m.categories_
        gujo__mkd = []
        for ilquk__gygk in dfamf__tlh:
            ldose__pwo = bodo.allgatherv(ilquk__gygk)
            kfakv__poiz = _unique(ldose__pwo)
            gujo__mkd.append(kfakv__poiz)
        m.categories_ = gujo__mkd
    m.drop_idx_ = m._compute_drop_idx()
    return m


@overload_method(BodoPreprocessingOneHotEncoderType, 'fit', no_unliteral=True)
def overload_preprocessing_one_hot_encoder_fit(m, X, y=None,
    _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _preprocessing_one_hot_encoder_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_one_hot_encoder_type'):
                if X.ndim == 1 and isinstance(X[0], np.ndarray):
                    X = np.vstack(X)
                m = sklearn_preprocessing_one_hot_encoder_fit_dist_helper(m, X)
            return m
    else:

        def _preprocessing_one_hot_encoder_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_one_hot_encoder_type'):
                if X.ndim == 1 and isinstance(X[0], np.ndarray):
                    X = np.vstack(X)
                m = m.fit(X, y)
            return m
    return _preprocessing_one_hot_encoder_fit_impl


@overload_method(BodoPreprocessingOneHotEncoderType, 'transform',
    no_unliteral=True)
def overload_preprocessing_one_hot_encoder_transform(m, X):

    def _preprocessing_one_hot_encoder_transform_impl(m, X):
        with numba.objmode(transformed_X='float64[:,:]'):
            if X.ndim == 1 and isinstance(X[0], np.ndarray):
                X = np.vstack(X)
            transformed_X = m.transform(X)
        return transformed_X
    return _preprocessing_one_hot_encoder_transform_impl


@overload_method(BodoPreprocessingOneHotEncoderType,
    'get_feature_names_out', no_unliteral=True)
def overload_preprocessing_one_hot_encoder_get_feature_names_out(m,
    input_features=None):

    def _preprocessing_one_hot_encoder_get_feature_names_out_impl(m,
        input_features=None):
        with numba.objmode(out_features='string[:]'):
            out_features = get_feature_names_out(input_features)
        return out_features
    return _preprocessing_one_hot_encoder_get_feature_names_out_impl


class BodoPreprocessingStandardScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingStandardScalerType, self).__init__(name=
            'BodoPreprocessingStandardScalerType')


preprocessing_standard_scaler_type = BodoPreprocessingStandardScalerType()
types.preprocessing_standard_scaler_type = preprocessing_standard_scaler_type
register_model(BodoPreprocessingStandardScalerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.StandardScaler)
def typeof_preprocessing_standard_scaler(val, c):
    return preprocessing_standard_scaler_type


@box(BodoPreprocessingStandardScalerType)
def box_preprocessing_standard_scaler(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingStandardScalerType)
def unbox_preprocessing_standard_scaler(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.StandardScaler, no_unliteral=True)
def sklearn_preprocessing_standard_scaler_overload(copy=True, with_mean=
    True, with_std=True):
    check_sklearn_version()

    def _sklearn_preprocessing_standard_scaler_impl(copy=True, with_mean=
        True, with_std=True):
        with numba.objmode(m='preprocessing_standard_scaler_type'):
            m = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=
                with_mean, with_std=with_std)
        return m
    return _sklearn_preprocessing_standard_scaler_impl


def sklearn_preprocessing_standard_scaler_fit_dist_helper(m, X):
    aslcq__qidqo = MPI.COMM_WORLD
    cfj__sqsa = aslcq__qidqo.Get_size()
    wzzb__gifoc = m.with_std
    qefzt__zrxt = m.with_mean
    m.with_std = False
    if wzzb__gifoc:
        m.with_mean = True
    m = m.fit(X)
    m.with_std = wzzb__gifoc
    m.with_mean = qefzt__zrxt
    if not isinstance(m.n_samples_seen_, numbers.Integral):
        xnax__pvokt = False
    else:
        xnax__pvokt = True
        m.n_samples_seen_ = np.repeat(m.n_samples_seen_, X.shape[1]).astype(np
            .int64, copy=False)
    cyov__hor = np.zeros((cfj__sqsa, *m.n_samples_seen_.shape), dtype=m.
        n_samples_seen_.dtype)
    aslcq__qidqo.Allgather(m.n_samples_seen_, cyov__hor)
    lmo__xoj = np.sum(cyov__hor, axis=0)
    m.n_samples_seen_ = lmo__xoj
    if m.with_mean or m.with_std:
        lysoj__vmux = np.zeros((cfj__sqsa, *m.mean_.shape), dtype=m.mean_.dtype
            )
        aslcq__qidqo.Allgather(m.mean_, lysoj__vmux)
        lysoj__vmux[np.isnan(lysoj__vmux)] = 0
        objug__jelk = np.average(lysoj__vmux, axis=0, weights=cyov__hor)
        m.mean_ = objug__jelk
    if m.with_std:
        tpmtv__qkf = sklearn_safe_accumulator_op(np.nansum, (X -
            objug__jelk) ** 2, axis=0) / lmo__xoj
        nxpxp__fvrbm = np.zeros_like(tpmtv__qkf)
        aslcq__qidqo.Allreduce(tpmtv__qkf, nxpxp__fvrbm, op=MPI.SUM)
        m.var_ = nxpxp__fvrbm
        m.scale_ = sklearn_handle_zeros_in_scale(np.sqrt(m.var_))
    xnax__pvokt = aslcq__qidqo.allreduce(xnax__pvokt, op=MPI.LAND)
    if xnax__pvokt:
        m.n_samples_seen_ = m.n_samples_seen_[0]
    return m


@overload_method(BodoPreprocessingStandardScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_standard_scaler_fit(m, X, y=None, sample_weight=
    None, _is_data_distributed=False):
    if is_overload_true(_is_data_distributed) and not is_overload_none(
        sample_weight):
        raise BodoError(
            "sklearn.preprocessing.StandardScaler.fit() : 'sample_weight' is not supported for distributed data."
            )

    def _preprocessing_standard_scaler_fit_impl(m, X, y=None, sample_weight
        =None, _is_data_distributed=False):
        with numba.objmode(m='preprocessing_standard_scaler_type'):
            if _is_data_distributed:
                m = sklearn_preprocessing_standard_scaler_fit_dist_helper(m, X)
            else:
                m = m.fit(X, y, sample_weight)
        return m
    return _preprocessing_standard_scaler_fit_impl


@overload_method(BodoPreprocessingStandardScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_standard_scaler_transform(m, X, copy=None):

    def _preprocessing_standard_scaler_transform_impl(m, X, copy=None):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X, copy=copy)
        return transformed_X
    return _preprocessing_standard_scaler_transform_impl


@overload_method(BodoPreprocessingStandardScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_standard_scaler_inverse_transform(m, X, copy=None):

    def _preprocessing_standard_scaler_inverse_transform_impl(m, X, copy=None):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X, copy=copy)
        return inverse_transformed_X
    return _preprocessing_standard_scaler_inverse_transform_impl


class BodoPreprocessingMaxAbsScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingMaxAbsScalerType, self).__init__(name=
            'BodoPreprocessingMaxAbsScalerType')


preprocessing_max_abs_scaler_type = BodoPreprocessingMaxAbsScalerType()
types.preprocessing_max_abs_scaler_type = preprocessing_max_abs_scaler_type
register_model(BodoPreprocessingMaxAbsScalerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.MaxAbsScaler)
def typeof_preprocessing_max_abs_scaler(val, c):
    return preprocessing_max_abs_scaler_type


@box(BodoPreprocessingMaxAbsScalerType)
def box_preprocessing_max_abs_scaler(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingMaxAbsScalerType)
def unbox_preprocessing_max_abs_scaler(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload_attribute(BodoPreprocessingMaxAbsScalerType, 'scale_')
def get_max_abs_scaler_scale_(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.scale_
        return result
    return impl


@overload_attribute(BodoPreprocessingMaxAbsScalerType, 'max_abs_')
def get_max_abs_scaler_max_abs_(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.max_abs_
        return result
    return impl


@overload_attribute(BodoPreprocessingMaxAbsScalerType, 'n_samples_seen_')
def get_max_abs_scaler_n_samples_seen_(m):

    def impl(m):
        with numba.objmode(result='int64'):
            result = m.n_samples_seen_
        return result
    return impl


@overload(sklearn.preprocessing.MaxAbsScaler, no_unliteral=True)
def sklearn_preprocessing_max_abs_scaler_overload(copy=True):
    check_sklearn_version()

    def _sklearn_preprocessing_max_abs_scaler_impl(copy=True):
        with numba.objmode(m='preprocessing_max_abs_scaler_type'):
            m = sklearn.preprocessing.MaxAbsScaler(copy=copy)
        return m
    return _sklearn_preprocessing_max_abs_scaler_impl


def sklearn_preprocessing_max_abs_scaler_fit_dist_helper(m, X, partial=False):
    aslcq__qidqo = MPI.COMM_WORLD
    cfj__sqsa = aslcq__qidqo.Get_size()
    if hasattr(m, 'n_samples_seen_'):
        cufn__zstrl = m.n_samples_seen_
    else:
        cufn__zstrl = 0
    if partial:
        m = m.partial_fit(X)
    else:
        m = m.fit(X)
    lmo__xoj = aslcq__qidqo.allreduce(m.n_samples_seen_ - cufn__zstrl, op=
        MPI.SUM)
    m.n_samples_seen_ = lmo__xoj + cufn__zstrl
    kwsik__ywupc = np.zeros((cfj__sqsa, *m.max_abs_.shape), dtype=m.
        max_abs_.dtype)
    aslcq__qidqo.Allgather(m.max_abs_, kwsik__ywupc)
    flvd__rzwds = np.nanmax(kwsik__ywupc, axis=0)
    m.scale_ = sklearn_handle_zeros_in_scale(flvd__rzwds)
    m.max_abs_ = flvd__rzwds
    return m


@overload_method(BodoPreprocessingMaxAbsScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_max_abs_scaler_fit(m, X, y=None,
    _is_data_distributed=False):
    if _is_data_distributed:

        def _preprocessing_max_abs_scaler_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_max_abs_scaler_type'):
                m = sklearn_preprocessing_max_abs_scaler_fit_dist_helper(m,
                    X, partial=False)
            return m
    else:

        def _preprocessing_max_abs_scaler_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_max_abs_scaler_type'):
                m = m.fit(X, y)
            return m
    return _preprocessing_max_abs_scaler_fit_impl


@overload_method(BodoPreprocessingMaxAbsScalerType, 'partial_fit',
    no_unliteral=True)
def overload_preprocessing_max_abs_scaler_partial_fit(m, X, y=None,
    _is_data_distributed=False):
    if _is_data_distributed:

        def _preprocessing_max_abs_scaler_partial_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_max_abs_scaler_type'):
                m = sklearn_preprocessing_max_abs_scaler_fit_dist_helper(m,
                    X, partial=True)
            return m
    else:

        def _preprocessing_max_abs_scaler_partial_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_max_abs_scaler_type'):
                m = m.partial_fit(X, y)
            return m
    return _preprocessing_max_abs_scaler_partial_fit_impl


@overload_method(BodoPreprocessingMaxAbsScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_max_abs_scaler_transform(m, X):

    def _preprocessing_max_abs_scaler_transform_impl(m, X):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X)
        return transformed_X
    return _preprocessing_max_abs_scaler_transform_impl


@overload_method(BodoPreprocessingMaxAbsScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_max_abs_scaler_inverse_transform(m, X):

    def _preprocessing_max_abs_scaler_inverse_transform_impl(m, X):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X)
        return inverse_transformed_X
    return _preprocessing_max_abs_scaler_inverse_transform_impl


class BodoModelSelectionLeavePOutType(types.Opaque):

    def __init__(self):
        super(BodoModelSelectionLeavePOutType, self).__init__(name=
            'BodoModelSelectionLeavePOutType')


model_selection_leave_p_out_type = BodoModelSelectionLeavePOutType()
types.model_selection_leave_p_out_type = model_selection_leave_p_out_type
register_model(BodoModelSelectionLeavePOutType)(models.OpaqueModel)


@typeof_impl.register(sklearn.model_selection.LeavePOut)
def typeof_model_selection_leave_p_out(val, c):
    return model_selection_leave_p_out_type


@box(BodoModelSelectionLeavePOutType)
def box_model_selection_leave_p_out(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoModelSelectionLeavePOutType)
def unbox_model_selection_leave_p_out(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


class BodoModelSelectionLeavePOutSplitType(types.Opaque):

    def __init__(self):
        super(BodoModelSelectionLeavePOutSplitType, self).__init__(name=
            'BodoModelSelectionLeavePOutSplitType')


model_selection_leave_p_out_split_type = BodoModelSelectionLeavePOutSplitType()
types.model_selection_leave_p_out_split_type = (
    model_selection_leave_p_out_split_type)
register_model(BodoModelSelectionLeavePOutSplitType)(models.OpaqueModel)


@box(BodoModelSelectionLeavePOutSplitType)
def box_model_selection_leave_p_out_split(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoModelSelectionLeavePOutSplitType)
def unbox_model_selection_leave_p_out_split(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.model_selection.LeavePOut, no_unliteral=True)
def sklearn_model_selection_leave_p_out_overload(p):
    check_sklearn_version()

    def _sklearn_model_selection_leave_p_out_impl(p):
        with numba.objmode(m='model_selection_leave_p_out_type'):
            m = sklearn.model_selection.LeavePOut(p=p)
        return m
    return _sklearn_model_selection_leave_p_out_impl


def sklearn_model_selection_leave_p_out_split_dist_helper(m, X):
    psc__nehtr = bodo.get_rank()
    spgz__fqqy = bodo.get_size()
    grkkj__xted = np.empty(spgz__fqqy, np.int64)
    bodo.libs.distributed_api.allgather(grkkj__xted, len(X))
    if psc__nehtr > 0:
        ftnnl__cidq = np.sum(grkkj__xted[:psc__nehtr])
    else:
        ftnnl__cidq = 0
    sgn__muxgp = ftnnl__cidq + grkkj__xted[psc__nehtr]
    pdx__elarm = np.sum(grkkj__xted)
    if pdx__elarm <= m.p:
        raise ValueError(
            f'p={m.p} must be strictly less than the number of samples={pdx__elarm}'
            )
    zyb__urbjk = np.arange(ftnnl__cidq, sgn__muxgp)
    for xuxul__gbny in combinations(range(pdx__elarm), m.p):
        cvofx__uha = np.array(xuxul__gbny)
        cvofx__uha = cvofx__uha[cvofx__uha >= ftnnl__cidq]
        cvofx__uha = cvofx__uha[cvofx__uha < sgn__muxgp]
        pfyk__czbyj = np.zeros(len(X), dtype=bool)
        pfyk__czbyj[cvofx__uha - ftnnl__cidq] = True
        kwytw__rjb = zyb__urbjk[np.logical_not(pfyk__czbyj)]
        yield kwytw__rjb, cvofx__uha


@overload_method(BodoModelSelectionLeavePOutType, 'split', no_unliteral=True)
def overload_model_selection_leave_p_out_split(m, X, y=None, groups=None,
    _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _model_selection_leave_p_out_split_impl(m, X, y=None, groups=
            None, _is_data_distributed=False):
            with numba.objmode(gen='model_selection_leave_p_out_split_type'):
                gen = sklearn_model_selection_leave_p_out_split_dist_helper(m,
                    X)
            return gen
    else:

        def _model_selection_leave_p_out_split_impl(m, X, y=None, groups=
            None, _is_data_distributed=False):
            with numba.objmode(gen='model_selection_leave_p_out_split_type'):
                gen = m.split(X, y=y, groups=groups)
            return gen
    return _model_selection_leave_p_out_split_impl


@overload_method(BodoModelSelectionLeavePOutType, 'get_n_splits',
    no_unliteral=True)
def overload_model_selection_leave_p_out_get_n_splits(m, X, y=None, groups=
    None, _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _model_selection_leave_p_out_get_n_splits_impl(m, X, y=None,
            groups=None, _is_data_distributed=False):
            with numba.objmode(out='int64'):
                pdx__elarm = bodo.libs.distributed_api.dist_reduce(len(X),
                    np.int32(Reduce_Type.Sum.value))
                out = int(comb(pdx__elarm, m.p, exact=True))
            return out
    else:

        def _model_selection_leave_p_out_get_n_splits_impl(m, X, y=None,
            groups=None, _is_data_distributed=False):
            with numba.objmode(out='int64'):
                out = m.get_n_splits(X)
            return out
    return _model_selection_leave_p_out_get_n_splits_impl


class BodoModelSelectionKFoldType(types.Opaque):

    def __init__(self):
        super(BodoModelSelectionKFoldType, self).__init__(name=
            'BodoModelSelectionKFoldType')


model_selection_kfold_type = BodoModelSelectionKFoldType()
types.model_selection_kfold_type = model_selection_kfold_type
register_model(BodoModelSelectionKFoldType)(models.OpaqueModel)


@typeof_impl.register(sklearn.model_selection.KFold)
def typeof_model_selection_kfold(val, c):
    return model_selection_kfold_type


@box(BodoModelSelectionKFoldType)
def box_model_selection_kfold(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoModelSelectionKFoldType)
def unbox_model_selection_kfold(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


class BodoModelSelectionKFoldSplitType(types.Opaque):

    def __init__(self):
        super(BodoModelSelectionKFoldSplitType, self).__init__(name=
            'BodoModelSelectionKFoldSplitType')


model_selection_kfold_split_type = BodoModelSelectionKFoldSplitType()
types.model_selection_kfold_split_type = model_selection_kfold_split_type
register_model(BodoModelSelectionKFoldSplitType)(models.OpaqueModel)


@box(BodoModelSelectionKFoldSplitType)
def box_model_selection_kfold_split(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoModelSelectionKFoldSplitType)
def unbox_model_selection_kfold_split(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.model_selection.KFold, no_unliteral=True)
def sklearn_model_selection_kfold_overload(n_splits=5, shuffle=False,
    random_state=None):
    check_sklearn_version()

    def _sklearn_model_selection_kfold_impl(n_splits=5, shuffle=False,
        random_state=None):
        with numba.objmode(m='model_selection_kfold_type'):
            m = sklearn.model_selection.KFold(n_splits=n_splits, shuffle=
                shuffle, random_state=random_state)
        return m
    return _sklearn_model_selection_kfold_impl


def sklearn_model_selection_kfold_split_dist_helper(m, X, y=None, groups=None):
    psc__nehtr = bodo.get_rank()
    spgz__fqqy = bodo.get_size()
    grkkj__xted = np.empty(spgz__fqqy, np.int64)
    bodo.libs.distributed_api.allgather(grkkj__xted, len(X))
    if psc__nehtr > 0:
        ftnnl__cidq = np.sum(grkkj__xted[:psc__nehtr])
    else:
        ftnnl__cidq = 0
    sgn__muxgp = ftnnl__cidq + len(X)
    pdx__elarm = np.sum(grkkj__xted)
    if pdx__elarm < m.n_splits:
        raise ValueError(
            f'number of splits n_splits={m.n_splits} greater than the number of samples {pdx__elarm}'
            )
    ofhpx__pqk = np.arange(pdx__elarm)
    if m.shuffle:
        if m.random_state is None:
            vpij__iat = bodo.libs.distributed_api.bcast_scalar(np.random.
                randint(0, 2 ** 31))
            np.random.seed(vpij__iat)
        else:
            np.random.seed(m.random_state)
        np.random.shuffle(ofhpx__pqk)
    zyb__urbjk = ofhpx__pqk[ftnnl__cidq:sgn__muxgp]
    xmdj__hrs = np.full(m.n_splits, pdx__elarm // (spgz__fqqy * m.n_splits),
        dtype=np.int32)
    hgnlp__luo = pdx__elarm % (spgz__fqqy * m.n_splits)
    wise__yibnk = np.full(m.n_splits, hgnlp__luo // m.n_splits, dtype=int)
    wise__yibnk[:hgnlp__luo % m.n_splits] += 1
    gat__yrtws = np.repeat(np.arange(m.n_splits), wise__yibnk)
    vwf__wayn = gat__yrtws[psc__nehtr::spgz__fqqy]
    xmdj__hrs[vwf__wayn] += 1

    def _kfold_split_dist_generator(X, y=None, groups=None):
        xdye__ciir = 0
        for qsrk__eiy in xmdj__hrs:
            zpyf__qbwex = xdye__ciir + qsrk__eiy
            cvofx__uha = zyb__urbjk[xdye__ciir:zpyf__qbwex]
            kwytw__rjb = np.concatenate((zyb__urbjk[:xdye__ciir],
                zyb__urbjk[zpyf__qbwex:]), axis=0)
            yield kwytw__rjb, cvofx__uha
            xdye__ciir = zpyf__qbwex
    return _kfold_split_dist_generator(X, y=y, groups=groups)


@overload_method(BodoModelSelectionKFoldType, 'split', no_unliteral=True)
def overload_model_selection_kfold_split(m, X, y=None, groups=None,
    _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _model_selection_kfold_split_impl(m, X, y=None, groups=None,
            _is_data_distributed=False):
            with numba.objmode(gen='model_selection_kfold_split_type'):
                gen = sklearn_model_selection_kfold_split_dist_helper(m, X,
                    y=None, groups=None)
            return gen
    else:

        def _model_selection_kfold_split_impl(m, X, y=None, groups=None,
            _is_data_distributed=False):
            with numba.objmode(gen='model_selection_kfold_split_type'):
                gen = m.split(X, y=y, groups=groups)
            return gen
    return _model_selection_kfold_split_impl


@overload_method(BodoModelSelectionKFoldType, 'get_n_splits', no_unliteral=True
    )
def overload_model_selection_kfold_get_n_splits(m, X=None, y=None, groups=
    None, _is_data_distributed=False):

    def _model_selection_kfold_get_n_splits_impl(m, X=None, y=None, groups=
        None, _is_data_distributed=False):
        with numba.objmode(out='int64'):
            out = m.n_splits
        return out
    return _model_selection_kfold_get_n_splits_impl


def get_data_slice_parallel(data, labels, len_train):
    sldj__eaf = data[:len_train]
    glv__tdhqw = data[len_train:]
    sldj__eaf = bodo.rebalance(sldj__eaf)
    glv__tdhqw = bodo.rebalance(glv__tdhqw)
    ynaz__rtyh = labels[:len_train]
    esfv__avilp = labels[len_train:]
    ynaz__rtyh = bodo.rebalance(ynaz__rtyh)
    esfv__avilp = bodo.rebalance(esfv__avilp)
    return sldj__eaf, glv__tdhqw, ynaz__rtyh, esfv__avilp


@numba.njit
def get_train_test_size(train_size, test_size):
    if train_size is None:
        train_size = -1.0
    if test_size is None:
        test_size = -1.0
    if train_size == -1.0 and test_size == -1.0:
        return 0.75, 0.25
    elif test_size == -1.0:
        return train_size, 1.0 - train_size
    elif train_size == -1.0:
        return 1.0 - test_size, test_size
    elif train_size + test_size > 1:
        raise ValueError(
            'The sum of test_size and train_size, should be in the (0, 1) range. Reduce test_size and/or train_size.'
            )
    else:
        return train_size, test_size


def set_labels_type(labels, label_type):
    return labels


@overload(set_labels_type, no_unliteral=True)
def overload_set_labels_type(labels, label_type):
    if get_overload_const_int(label_type) == 1:

        def _set_labels(labels, label_type):
            return pd.Series(labels)
        return _set_labels
    elif get_overload_const_int(label_type) == 2:

        def _set_labels(labels, label_type):
            return labels.values
        return _set_labels
    else:

        def _set_labels(labels, label_type):
            return labels
        return _set_labels


def reset_labels_type(labels, label_type):
    return labels


@overload(reset_labels_type, no_unliteral=True)
def overload_reset_labels_type(labels, label_type):
    if get_overload_const_int(label_type) == 1:

        def _reset_labels(labels, label_type):
            return labels.values
        return _reset_labels
    elif get_overload_const_int(label_type) == 2:

        def _reset_labels(labels, label_type):
            return pd.Series(labels, index=np.arange(len(labels)))
        return _reset_labels
    else:

        def _reset_labels(labels, label_type):
            return labels
        return _reset_labels


@overload(sklearn.model_selection.train_test_split, no_unliteral=True)
def overload_train_test_split(data, labels=None, train_size=None, test_size
    =None, random_state=None, shuffle=True, stratify=None,
    _is_data_distributed=False):
    check_sklearn_version()
    cyp__phrjj = {'stratify': stratify}
    jblbl__pesc = {'stratify': None}
    check_unsupported_args('train_test_split', cyp__phrjj, jblbl__pesc, 'ml')
    if is_overload_false(_is_data_distributed):
        uiesf__zobn = f'data_split_type_{numba.core.ir_utils.next_label()}'
        zua__xao = f'labels_split_type_{numba.core.ir_utils.next_label()}'
        for frs__ees, cio__hhax in ((data, uiesf__zobn), (labels, zua__xao)):
            if isinstance(frs__ees, (DataFrameType, SeriesType)):
                qrwu__iio = frs__ees.copy(index=NumericIndexType(types.int64))
                setattr(types, cio__hhax, qrwu__iio)
            else:
                setattr(types, cio__hhax, frs__ees)
        ohs__kjc = 'def _train_test_split_impl(\n'
        ohs__kjc += '    data,\n'
        ohs__kjc += '    labels=None,\n'
        ohs__kjc += '    train_size=None,\n'
        ohs__kjc += '    test_size=None,\n'
        ohs__kjc += '    random_state=None,\n'
        ohs__kjc += '    shuffle=True,\n'
        ohs__kjc += '    stratify=None,\n'
        ohs__kjc += '    _is_data_distributed=False,\n'
        ohs__kjc += '):  # pragma: no cover\n'
        ohs__kjc += (
            """    with numba.objmode(data_train='{}', data_test='{}', labels_train='{}', labels_test='{}'):
"""
            .format(uiesf__zobn, uiesf__zobn, zua__xao, zua__xao))
        ohs__kjc += """        data_train, data_test, labels_train, labels_test = sklearn.model_selection.train_test_split(
"""
        ohs__kjc += '            data,\n'
        ohs__kjc += '            labels,\n'
        ohs__kjc += '            train_size=train_size,\n'
        ohs__kjc += '            test_size=test_size,\n'
        ohs__kjc += '            random_state=random_state,\n'
        ohs__kjc += '            shuffle=shuffle,\n'
        ohs__kjc += '            stratify=stratify,\n'
        ohs__kjc += '        )\n'
        ohs__kjc += (
            '    return data_train, data_test, labels_train, labels_test\n')
        xcc__jtzw = {}
        exec(ohs__kjc, globals(), xcc__jtzw)
        _train_test_split_impl = xcc__jtzw['_train_test_split_impl']
        return _train_test_split_impl
    else:
        global get_data_slice_parallel
        if isinstance(get_data_slice_parallel, pytypes.FunctionType):
            get_data_slice_parallel = bodo.jit(get_data_slice_parallel,
                all_args_distributed_varlength=True,
                all_returns_distributed=True)
        label_type = 0
        if isinstance(data, DataFrameType) and isinstance(labels, types.Array):
            label_type = 1
        elif isinstance(data, types.Array) and isinstance(labels, SeriesType):
            label_type = 2
        if is_overload_none(random_state):
            random_state = 42

        def _train_test_split_impl(data, labels=None, train_size=None,
            test_size=None, random_state=None, shuffle=True, stratify=None,
            _is_data_distributed=False):
            if data.shape[0] != labels.shape[0]:
                raise ValueError(
                    'Found input variables with inconsistent number of samples\n'
                    )
            train_size, test_size = get_train_test_size(train_size, test_size)
            pdx__elarm = bodo.libs.distributed_api.dist_reduce(len(data),
                np.int32(Reduce_Type.Sum.value))
            len_train = int(pdx__elarm * train_size)
            exrmd__jqmfg = pdx__elarm - len_train
            if shuffle:
                labels = set_labels_type(labels, label_type)
                psc__nehtr = bodo.get_rank()
                spgz__fqqy = bodo.get_size()
                grkkj__xted = np.empty(spgz__fqqy, np.int64)
                bodo.libs.distributed_api.allgather(grkkj__xted, len(data))
                wsuf__szy = np.cumsum(grkkj__xted[0:psc__nehtr + 1])
                fuqk__nri = np.full(pdx__elarm, True)
                fuqk__nri[:exrmd__jqmfg] = False
                np.random.seed(42)
                np.random.permutation(fuqk__nri)
                if psc__nehtr:
                    xdye__ciir = wsuf__szy[psc__nehtr - 1]
                else:
                    xdye__ciir = 0
                aitir__ousyw = wsuf__szy[psc__nehtr]
                vwlyz__trs = fuqk__nri[xdye__ciir:aitir__ousyw]
                sldj__eaf = data[vwlyz__trs]
                glv__tdhqw = data[~vwlyz__trs]
                ynaz__rtyh = labels[vwlyz__trs]
                esfv__avilp = labels[~vwlyz__trs]
                sldj__eaf = bodo.random_shuffle(sldj__eaf, seed=
                    random_state, parallel=True)
                glv__tdhqw = bodo.random_shuffle(glv__tdhqw, seed=
                    random_state, parallel=True)
                ynaz__rtyh = bodo.random_shuffle(ynaz__rtyh, seed=
                    random_state, parallel=True)
                esfv__avilp = bodo.random_shuffle(esfv__avilp, seed=
                    random_state, parallel=True)
                ynaz__rtyh = reset_labels_type(ynaz__rtyh, label_type)
                esfv__avilp = reset_labels_type(esfv__avilp, label_type)
            else:
                sldj__eaf, glv__tdhqw, ynaz__rtyh, esfv__avilp = (
                    get_data_slice_parallel(data, labels, len_train))
            return sldj__eaf, glv__tdhqw, ynaz__rtyh, esfv__avilp
        return _train_test_split_impl


@overload(sklearn.utils.shuffle, no_unliteral=True)
def sklearn_utils_shuffle_overload(data, random_state=None, n_samples=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):
        uiesf__zobn = f'utils_shuffle_type_{numba.core.ir_utils.next_label()}'
        if isinstance(data, (DataFrameType, SeriesType)):
            mxdt__kqq = data.copy(index=NumericIndexType(types.int64))
            setattr(types, uiesf__zobn, mxdt__kqq)
        else:
            setattr(types, uiesf__zobn, data)
        ohs__kjc = 'def _utils_shuffle_impl(\n'
        ohs__kjc += (
            '    data, random_state=None, n_samples=None, _is_data_distributed=False\n'
            )
        ohs__kjc += '):\n'
        ohs__kjc += f"    with numba.objmode(out='{uiesf__zobn}'):\n"
        ohs__kjc += '        out = sklearn.utils.shuffle(\n'
        ohs__kjc += (
            '            data, random_state=random_state, n_samples=n_samples\n'
            )
        ohs__kjc += '        )\n'
        ohs__kjc += '    return out\n'
        xcc__jtzw = {}
        exec(ohs__kjc, globals(), xcc__jtzw)
        _utils_shuffle_impl = xcc__jtzw['_utils_shuffle_impl']
    else:

        def _utils_shuffle_impl(data, random_state=None, n_samples=None,
            _is_data_distributed=False):
            m = bodo.random_shuffle(data, seed=random_state, n_samples=
                n_samples, parallel=True)
            return m
    return _utils_shuffle_impl


class BodoPreprocessingMinMaxScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingMinMaxScalerType, self).__init__(name=
            'BodoPreprocessingMinMaxScalerType')


preprocessing_minmax_scaler_type = BodoPreprocessingMinMaxScalerType()
types.preprocessing_minmax_scaler_type = preprocessing_minmax_scaler_type
register_model(BodoPreprocessingMinMaxScalerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.MinMaxScaler)
def typeof_preprocessing_minmax_scaler(val, c):
    return preprocessing_minmax_scaler_type


@box(BodoPreprocessingMinMaxScalerType)
def box_preprocessing_minmax_scaler(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingMinMaxScalerType)
def unbox_preprocessing_minmax_scaler(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.MinMaxScaler, no_unliteral=True)
def sklearn_preprocessing_minmax_scaler_overload(feature_range=(0, 1), copy
    =True, clip=False):
    check_sklearn_version()

    def _sklearn_preprocessing_minmax_scaler_impl(feature_range=(0, 1),
        copy=True, clip=False):
        with numba.objmode(m='preprocessing_minmax_scaler_type'):
            m = sklearn.preprocessing.MinMaxScaler(feature_range=
                feature_range, copy=copy, clip=clip)
        return m
    return _sklearn_preprocessing_minmax_scaler_impl


def sklearn_preprocessing_minmax_scaler_fit_dist_helper(m, X):
    aslcq__qidqo = MPI.COMM_WORLD
    cfj__sqsa = aslcq__qidqo.Get_size()
    m = m.fit(X)
    lmo__xoj = aslcq__qidqo.allreduce(m.n_samples_seen_, op=MPI.SUM)
    m.n_samples_seen_ = lmo__xoj
    mijw__qbzf = np.zeros((cfj__sqsa, *m.data_min_.shape), dtype=m.
        data_min_.dtype)
    aslcq__qidqo.Allgather(m.data_min_, mijw__qbzf)
    wdmbd__yioex = np.nanmin(mijw__qbzf, axis=0)
    hazg__zllnj = np.zeros((cfj__sqsa, *m.data_max_.shape), dtype=m.
        data_max_.dtype)
    aslcq__qidqo.Allgather(m.data_max_, hazg__zllnj)
    nqssk__aag = np.nanmax(hazg__zllnj, axis=0)
    mnt__hqg = nqssk__aag - wdmbd__yioex
    m.scale_ = (m.feature_range[1] - m.feature_range[0]
        ) / sklearn_handle_zeros_in_scale(mnt__hqg)
    m.min_ = m.feature_range[0] - wdmbd__yioex * m.scale_
    m.data_min_ = wdmbd__yioex
    m.data_max_ = nqssk__aag
    m.data_range_ = mnt__hqg
    return m


@overload_method(BodoPreprocessingMinMaxScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_minmax_scaler_fit(m, X, y=None,
    _is_data_distributed=False):

    def _preprocessing_minmax_scaler_fit_impl(m, X, y=None,
        _is_data_distributed=False):
        with numba.objmode(m='preprocessing_minmax_scaler_type'):
            if _is_data_distributed:
                m = sklearn_preprocessing_minmax_scaler_fit_dist_helper(m, X)
            else:
                m = m.fit(X, y)
        return m
    return _preprocessing_minmax_scaler_fit_impl


@overload_method(BodoPreprocessingMinMaxScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_minmax_scaler_transform(m, X):

    def _preprocessing_minmax_scaler_transform_impl(m, X):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X)
        return transformed_X
    return _preprocessing_minmax_scaler_transform_impl


@overload_method(BodoPreprocessingMinMaxScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_minmax_scaler_inverse_transform(m, X):

    def _preprocessing_minmax_scaler_inverse_transform_impl(m, X):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X)
        return inverse_transformed_X
    return _preprocessing_minmax_scaler_inverse_transform_impl


class BodoPreprocessingRobustScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingRobustScalerType, self).__init__(name=
            'BodoPreprocessingRobustScalerType')


preprocessing_robust_scaler_type = BodoPreprocessingRobustScalerType()
types.preprocessing_robust_scaler_type = preprocessing_robust_scaler_type


@register_model(BodoPreprocessingRobustScalerType)
class BodoPreprocessingRobustScalerModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yhmym__fpp = [('meminfo', types.MemInfoPointer(
            preprocessing_robust_scaler_type)), ('pyobj', types.pyobject)]
        super().__init__(dmm, fe_type, yhmym__fpp)


@typeof_impl.register(sklearn.preprocessing.RobustScaler)
def typeof_preprocessing_robust_scaler(val, c):
    return preprocessing_robust_scaler_type


@box(BodoPreprocessingRobustScalerType)
def box_preprocessing_robust_scaler(typ, val, c):
    xef__msq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = xef__msq.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


@unbox(BodoPreprocessingRobustScalerType)
def unbox_preprocessing_robust_scaler(typ, obj, c):
    xef__msq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xef__msq.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    xef__msq.pyobj = obj
    return NativeValue(xef__msq._getvalue())


@overload_attribute(BodoPreprocessingRobustScalerType, 'with_centering')
def get_robust_scaler_with_centering(m):

    def impl(m):
        with numba.objmode(result='boolean'):
            result = m.with_centering
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'with_scaling')
def get_robust_scaler_with_scaling(m):

    def impl(m):
        with numba.objmode(result='boolean'):
            result = m.with_scaling
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'quantile_range')
def get_robust_scaler_quantile_range(m):
    typ = numba.typeof((25.0, 75.0))

    def impl(m):
        with numba.objmode(result=typ):
            result = m.quantile_range
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'unit_variance')
def get_robust_scaler_unit_variance(m):

    def impl(m):
        with numba.objmode(result='boolean'):
            result = m.unit_variance
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'copy')
def get_robust_scaler_copy(m):

    def impl(m):
        with numba.objmode(result='boolean'):
            result = m.copy
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'center_')
def get_robust_scaler_center_(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.center_
        return result
    return impl


@overload_attribute(BodoPreprocessingRobustScalerType, 'scale_')
def get_robust_scaler_scale_(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.scale_
        return result
    return impl


@overload(sklearn.preprocessing.RobustScaler, no_unliteral=True)
def sklearn_preprocessing_robust_scaler_overload(with_centering=True,
    with_scaling=True, quantile_range=(25.0, 75.0), copy=True,
    unit_variance=False):
    check_sklearn_version()

    def _sklearn_preprocessing_robust_scaler_impl(with_centering=True,
        with_scaling=True, quantile_range=(25.0, 75.0), copy=True,
        unit_variance=False):
        with numba.objmode(m='preprocessing_robust_scaler_type'):
            m = sklearn.preprocessing.RobustScaler(with_centering=
                with_centering, with_scaling=with_scaling, quantile_range=
                quantile_range, copy=copy, unit_variance=unit_variance)
        return m
    return _sklearn_preprocessing_robust_scaler_impl


@overload_method(BodoPreprocessingRobustScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_robust_scaler_fit(m, X, y=None,
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_true(_is_data_distributed):
        ohs__kjc = f'def preprocessing_robust_scaler_fit_impl(\n'
        ohs__kjc += f'  m, X, y=None, _is_data_distributed=False\n'
        ohs__kjc += f'):\n'
        if isinstance(X, DataFrameType):
            ohs__kjc += f'  X = X.to_numpy()\n'
        ohs__kjc += (
            f"  with numba.objmode(qrange_l='float64', qrange_r='float64'):\n")
        ohs__kjc += f'    (qrange_l, qrange_r) = m.quantile_range\n'
        ohs__kjc += f'  if not 0 <= qrange_l <= qrange_r <= 100:\n'
        ohs__kjc += f'    raise ValueError(\n'
        ohs__kjc += f"""      'Invalid quantile range provided. Ensure that 0 <= quantile_range[0] <= quantile_range[1] <= 100.'
"""
        ohs__kjc += f'    )\n'
        ohs__kjc += (
            f'  qrange_l, qrange_r = qrange_l / 100.0, qrange_r / 100.0\n')
        ohs__kjc += f'  X = bodo.utils.conversion.coerce_to_array(X)\n'
        ohs__kjc += f'  num_features = X.shape[1]\n'
        ohs__kjc += f'  if m.with_scaling:\n'
        ohs__kjc += f'    scales = np.zeros(num_features)\n'
        ohs__kjc += f'  else:\n'
        ohs__kjc += f'    scales = None\n'
        ohs__kjc += f'  if m.with_centering:\n'
        ohs__kjc += f'    centers = np.zeros(num_features)\n'
        ohs__kjc += f'  else:\n'
        ohs__kjc += f'    centers = None\n'
        ohs__kjc += f'  if m.with_scaling or m.with_centering:\n'
        ohs__kjc += f'    numba.parfors.parfor.init_prange()\n'
        ohs__kjc += (
            f'    for feature_idx in numba.parfors.parfor.internal_prange(num_features):\n'
            )
        ohs__kjc += f"""      column_data = bodo.utils.conversion.ensure_contig_if_np(X[:, feature_idx])
"""
        ohs__kjc += f'      if m.with_scaling:\n'
        ohs__kjc += (
            f'        q1 = bodo.libs.array_kernels.quantile_parallel(\n')
        ohs__kjc += f'          column_data, qrange_l, 0\n'
        ohs__kjc += f'        )\n'
        ohs__kjc += (
            f'        q2 = bodo.libs.array_kernels.quantile_parallel(\n')
        ohs__kjc += f'          column_data, qrange_r, 0\n'
        ohs__kjc += f'        )\n'
        ohs__kjc += f'        scales[feature_idx] = q2 - q1\n'
        ohs__kjc += f'      if m.with_centering:\n'
        ohs__kjc += (
            f'        centers[feature_idx] = bodo.libs.array_ops.array_op_median(\n'
            )
        ohs__kjc += f'          column_data, True, True\n'
        ohs__kjc += f'        )\n'
        ohs__kjc += f'  if m.with_scaling:\n'
        ohs__kjc += (
            f'    constant_mask = scales < 10 * np.finfo(scales.dtype).eps\n')
        ohs__kjc += f'    scales[constant_mask] = 1.0\n'
        ohs__kjc += f'    if m.unit_variance:\n'
        ohs__kjc += f"      with numba.objmode(adjust='float64'):\n"
        ohs__kjc += (
            f'        adjust = stats.norm.ppf(qrange_r) - stats.norm.ppf(qrange_l)\n'
            )
        ohs__kjc += f'      scales = scales / adjust\n'
        ohs__kjc += f'  with numba.objmode():\n'
        ohs__kjc += f'    m.center_ = centers\n'
        ohs__kjc += f'    m.scale_ = scales\n'
        ohs__kjc += f'  return m\n'
        xcc__jtzw = {}
        exec(ohs__kjc, globals(), xcc__jtzw)
        _preprocessing_robust_scaler_fit_impl = xcc__jtzw[
            'preprocessing_robust_scaler_fit_impl']
        return _preprocessing_robust_scaler_fit_impl
    else:

        def _preprocessing_robust_scaler_fit_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_robust_scaler_type'):
                m = m.fit(X, y)
            return m
        return _preprocessing_robust_scaler_fit_impl


@overload_method(BodoPreprocessingRobustScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_robust_scaler_transform(m, X):
    check_sklearn_version()

    def _preprocessing_robust_scaler_transform_impl(m, X):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X)
        return transformed_X
    return _preprocessing_robust_scaler_transform_impl


@overload_method(BodoPreprocessingRobustScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_robust_scaler_inverse_transform(m, X):
    check_sklearn_version()

    def _preprocessing_robust_scaler_inverse_transform_impl(m, X):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X)
        return inverse_transformed_X
    return _preprocessing_robust_scaler_inverse_transform_impl


class BodoPreprocessingLabelEncoderType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingLabelEncoderType, self).__init__(name=
            'BodoPreprocessingLabelEncoderType')


preprocessing_label_encoder_type = BodoPreprocessingLabelEncoderType()
types.preprocessing_label_encoder_type = preprocessing_label_encoder_type
register_model(BodoPreprocessingLabelEncoderType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.LabelEncoder)
def typeof_preprocessing_label_encoder(val, c):
    return preprocessing_label_encoder_type


@box(BodoPreprocessingLabelEncoderType)
def box_preprocessing_label_encoder(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingLabelEncoderType)
def unbox_preprocessing_label_encoder(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.LabelEncoder, no_unliteral=True)
def sklearn_preprocessing_label_encoder_overload():
    check_sklearn_version()

    def _sklearn_preprocessing_label_encoder_impl():
        with numba.objmode(m='preprocessing_label_encoder_type'):
            m = sklearn.preprocessing.LabelEncoder()
        return m
    return _sklearn_preprocessing_label_encoder_impl


@overload_method(BodoPreprocessingLabelEncoderType, 'fit', no_unliteral=True)
def overload_preprocessing_label_encoder_fit(m, y, _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _sklearn_preprocessing_label_encoder_fit_impl(m, y,
            _is_data_distributed=False):
            y = bodo.utils.typing.decode_if_dict_array(y)
            y_classes = bodo.libs.array_kernels.unique(y, parallel=True)
            y_classes = bodo.allgatherv(y_classes, False)
            y_classes = bodo.libs.array_kernels.sort(y_classes, ascending=
                True, inplace=False)
            with numba.objmode:
                m.classes_ = y_classes
            return m
        return _sklearn_preprocessing_label_encoder_fit_impl
    else:

        def _sklearn_preprocessing_label_encoder_fit_impl(m, y,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_label_encoder_type'):
                m = m.fit(y)
            return m
        return _sklearn_preprocessing_label_encoder_fit_impl


@overload_method(BodoPreprocessingLabelEncoderType, 'transform',
    no_unliteral=True)
def overload_preprocessing_label_encoder_transform(m, y,
    _is_data_distributed=False):

    def _preprocessing_label_encoder_transform_impl(m, y,
        _is_data_distributed=False):
        with numba.objmode(transformed_y='int64[:]'):
            transformed_y = m.transform(y)
        return transformed_y
    return _preprocessing_label_encoder_transform_impl


@numba.njit
def le_fit_transform(m, y):
    m = m.fit(y, _is_data_distributed=True)
    transformed_y = m.transform(y, _is_data_distributed=True)
    return transformed_y


@overload_method(BodoPreprocessingLabelEncoderType, 'fit_transform',
    no_unliteral=True)
def overload_preprocessing_label_encoder_fit_transform(m, y,
    _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _preprocessing_label_encoder_fit_transform_impl(m, y,
            _is_data_distributed=False):
            transformed_y = le_fit_transform(m, y)
            return transformed_y
        return _preprocessing_label_encoder_fit_transform_impl
    else:

        def _preprocessing_label_encoder_fit_transform_impl(m, y,
            _is_data_distributed=False):
            with numba.objmode(transformed_y='int64[:]'):
                transformed_y = m.fit_transform(y)
            return transformed_y
        return _preprocessing_label_encoder_fit_transform_impl


class BodoFExtractHashingVectorizerType(types.Opaque):

    def __init__(self):
        super(BodoFExtractHashingVectorizerType, self).__init__(name=
            'BodoFExtractHashingVectorizerType')


f_extract_hashing_vectorizer_type = BodoFExtractHashingVectorizerType()
types.f_extract_hashing_vectorizer_type = f_extract_hashing_vectorizer_type
register_model(BodoFExtractHashingVectorizerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.feature_extraction.text.HashingVectorizer)
def typeof_f_extract_hashing_vectorizer(val, c):
    return f_extract_hashing_vectorizer_type


@box(BodoFExtractHashingVectorizerType)
def box_f_extract_hashing_vectorizer(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoFExtractHashingVectorizerType)
def unbox_f_extract_hashing_vectorizer(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.feature_extraction.text.HashingVectorizer, no_unliteral=True)
def sklearn_hashing_vectorizer_overload(input='content', encoding='utf-8',
    decode_error='strict', strip_accents=None, lowercase=True, preprocessor
    =None, tokenizer=None, stop_words=None, token_pattern=
    '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', n_features=2 **
    20, binary=False, norm='l2', alternate_sign=True, dtype=np.float64):
    check_sklearn_version()

    def _sklearn_hashing_vectorizer_impl(input='content', encoding='utf-8',
        decode_error='strict', strip_accents=None, lowercase=True,
        preprocessor=None, tokenizer=None, stop_words=None, token_pattern=
        '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word',
        n_features=2 ** 20, binary=False, norm='l2', alternate_sign=True,
        dtype=np.float64):
        with numba.objmode(m='f_extract_hashing_vectorizer_type'):
            m = sklearn.feature_extraction.text.HashingVectorizer(input=
                input, encoding=encoding, decode_error=decode_error,
                strip_accents=strip_accents, lowercase=lowercase,
                preprocessor=preprocessor, tokenizer=tokenizer, stop_words=
                stop_words, token_pattern=token_pattern, ngram_range=
                ngram_range, analyzer=analyzer, n_features=n_features,
                binary=binary, norm=norm, alternate_sign=alternate_sign,
                dtype=dtype)
        return m
    return _sklearn_hashing_vectorizer_impl


@overload_method(BodoFExtractHashingVectorizerType, 'fit_transform',
    no_unliteral=True)
def overload_hashing_vectorizer_fit_transform(m, X, y=None,
    _is_data_distributed=False):
    types.csr_matrix_float64_int64 = CSRMatrixType(types.float64, types.int64)

    def _hashing_vectorizer_fit_transform_impl(m, X, y=None,
        _is_data_distributed=False):
        with numba.objmode(transformed_X='csr_matrix_float64_int64'):
            transformed_X = m.fit_transform(X, y)
            transformed_X.indices = transformed_X.indices.astype(np.int64)
            transformed_X.indptr = transformed_X.indptr.astype(np.int64)
        return transformed_X
    return _hashing_vectorizer_fit_transform_impl


class BodoRandomForestRegressorType(types.Opaque):

    def __init__(self):
        super(BodoRandomForestRegressorType, self).__init__(name=
            'BodoRandomForestRegressorType')


random_forest_regressor_type = BodoRandomForestRegressorType()
types.random_forest_regressor_type = random_forest_regressor_type
register_model(BodoRandomForestRegressorType)(models.OpaqueModel)


@typeof_impl.register(sklearn.ensemble.RandomForestRegressor)
def typeof_random_forest_regressor(val, c):
    return random_forest_regressor_type


@box(BodoRandomForestRegressorType)
def box_random_forest_regressor(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRandomForestRegressorType)
def unbox_random_forest_regressor(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.ensemble.RandomForestRegressor, no_unliteral=True)
def overload_sklearn_rf_regressor(n_estimators=100, criterion=
    'squared_error', max_depth=None, min_samples_split=2, min_samples_leaf=
    1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=
    None, min_impurity_decrease=0.0, bootstrap=True, oob_score=False,
    n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=
    0.0, max_samples=None):
    check_sklearn_version()

    def _sklearn_ensemble_RandomForestRegressor_impl(n_estimators=100,
        criterion='squared_error', max_depth=None, min_samples_split=2,
        min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=
        'auto', max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=
        True, oob_score=False, n_jobs=None, random_state=None, verbose=0,
        warm_start=False, ccp_alpha=0.0, max_samples=None):
        with numba.objmode(m='random_forest_regressor_type'):
            if random_state is not None and get_num_nodes() > 1:
                print(
                    'With multinode, fixed random_state seed values are ignored.\n'
                    )
                random_state = None
            m = sklearn.ensemble.RandomForestRegressor(n_estimators=
                n_estimators, criterion=criterion, max_depth=max_depth,
                min_samples_split=min_samples_split, min_samples_leaf=
                min_samples_leaf, min_weight_fraction_leaf=
                min_weight_fraction_leaf, max_features=max_features,
                max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=
                min_impurity_decrease, bootstrap=bootstrap, oob_score=
                oob_score, n_jobs=1, random_state=random_state, verbose=
                verbose, warm_start=warm_start, ccp_alpha=ccp_alpha,
                max_samples=max_samples)
        return m
    return _sklearn_ensemble_RandomForestRegressor_impl


@overload_method(BodoRandomForestRegressorType, 'predict', no_unliteral=True)
def overload_rf_regressor_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoRandomForestRegressorType, 'score', no_unliteral=True)
def overload_rf_regressor_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_method(BodoRandomForestRegressorType, 'fit', no_unliteral=True)
@overload_method(BodoRandomForestClassifierType, 'fit', no_unliteral=True)
def overload_rf_classifier_model_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    cux__yqeg = 'RandomForestClassifier'
    if isinstance(m, BodoRandomForestRegressorType):
        cux__yqeg = 'RandomForestRegressor'
    if not is_overload_none(sample_weight):
        raise BodoError(
            f"sklearn.ensemble.{cux__yqeg}.fit() : 'sample_weight' is not supported for distributed data."
            )

    def _model_fit_impl(m, X, y, sample_weight=None, _is_data_distributed=False
        ):
        with numba.objmode(first_rank_node='int32[:]'):
            first_rank_node = get_nodes_first_ranks()
        if _is_data_distributed:
            crer__ftwe = len(first_rank_node)
            X = bodo.gatherv(X)
            y = bodo.gatherv(y)
            if crer__ftwe > 1:
                X = bodo.libs.distributed_api.bcast_comm(X, comm_ranks=
                    first_rank_node, nranks=crer__ftwe)
                y = bodo.libs.distributed_api.bcast_comm(y, comm_ranks=
                    first_rank_node, nranks=crer__ftwe)
        with numba.objmode:
            random_forest_model_fit(m, X, y)
        bodo.barrier()
        return m
    return _model_fit_impl


class BodoFExtractCountVectorizerType(types.Opaque):

    def __init__(self):
        super(BodoFExtractCountVectorizerType, self).__init__(name=
            'BodoFExtractCountVectorizerType')


f_extract_count_vectorizer_type = BodoFExtractCountVectorizerType()
types.f_extract_count_vectorizer_type = f_extract_count_vectorizer_type
register_model(BodoFExtractCountVectorizerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.feature_extraction.text.CountVectorizer)
def typeof_f_extract_count_vectorizer(val, c):
    return f_extract_count_vectorizer_type


@box(BodoFExtractCountVectorizerType)
def box_f_extract_count_vectorizer(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoFExtractCountVectorizerType)
def unbox_f_extract_count_vectorizer(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.feature_extraction.text.CountVectorizer, no_unliteral=True)
def sklearn_count_vectorizer_overload(input='content', encoding='utf-8',
    decode_error='strict', strip_accents=None, lowercase=True, preprocessor
    =None, tokenizer=None, stop_words=None, token_pattern=
    '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', max_df=1.0,
    min_df=1, max_features=None, vocabulary=None, binary=False, dtype=np.int64
    ):
    check_sklearn_version()
    if not is_overload_constant_number(min_df) or get_overload_const(min_df
        ) != 1:
        raise BodoError(
            """sklearn.feature_extraction.text.CountVectorizer(): 'min_df' is not supported for distributed data.
"""
            )
    if not is_overload_constant_number(max_df) or get_overload_const(min_df
        ) != 1:
        raise BodoError(
            """sklearn.feature_extraction.text.CountVectorizer(): 'max_df' is not supported for distributed data.
"""
            )

    def _sklearn_count_vectorizer_impl(input='content', encoding='utf-8',
        decode_error='strict', strip_accents=None, lowercase=True,
        preprocessor=None, tokenizer=None, stop_words=None, token_pattern=
        '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', max_df=
        1.0, min_df=1, max_features=None, vocabulary=None, binary=False,
        dtype=np.int64):
        with numba.objmode(m='f_extract_count_vectorizer_type'):
            m = sklearn.feature_extraction.text.CountVectorizer(input=input,
                encoding=encoding, decode_error=decode_error, strip_accents
                =strip_accents, lowercase=lowercase, preprocessor=
                preprocessor, tokenizer=tokenizer, stop_words=stop_words,
                token_pattern=token_pattern, ngram_range=ngram_range,
                analyzer=analyzer, max_df=max_df, min_df=min_df,
                max_features=max_features, vocabulary=vocabulary, binary=
                binary, dtype=dtype)
        return m
    return _sklearn_count_vectorizer_impl


@overload_attribute(BodoFExtractCountVectorizerType, 'vocabulary_')
def get_cv_vocabulary_(m):
    types.dict_string_int = types.DictType(types.unicode_type, types.int64)

    def impl(m):
        with numba.objmode(result='dict_string_int'):
            result = m.vocabulary_
        return result
    return impl


def _cv_fit_transform_helper(m, X):
    ukqz__rgiq = False
    local_vocabulary = m.vocabulary
    if m.vocabulary is None:
        m.fit(X)
        local_vocabulary = m.vocabulary_
        ukqz__rgiq = True
    return ukqz__rgiq, local_vocabulary


@overload_method(BodoFExtractCountVectorizerType, 'fit_transform',
    no_unliteral=True)
def overload_count_vectorizer_fit_transform(m, X, y=None,
    _is_data_distributed=False):
    check_sklearn_version()
    types.csr_matrix_int64_int64 = CSRMatrixType(types.int64, types.int64)
    if is_overload_true(_is_data_distributed):
        types.dict_str_int = types.DictType(types.unicode_type, types.int64)

        def _count_vectorizer_fit_transform_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(local_vocabulary='dict_str_int', changeVoc=
                'bool_'):
                changeVoc, local_vocabulary = _cv_fit_transform_helper(m, X)
            if changeVoc:
                local_vocabulary = bodo.utils.conversion.coerce_to_array(list
                    (local_vocabulary.keys()))
                jvuus__oyrl = bodo.libs.array_kernels.unique(local_vocabulary,
                    parallel=True)
                jvuus__oyrl = bodo.allgatherv(jvuus__oyrl, False)
                jvuus__oyrl = bodo.libs.array_kernels.sort(jvuus__oyrl,
                    ascending=True, inplace=True)
                hdrl__iead = {}
                for uhz__asaz in range(len(jvuus__oyrl)):
                    hdrl__iead[jvuus__oyrl[uhz__asaz]] = uhz__asaz
            else:
                hdrl__iead = local_vocabulary
            with numba.objmode(transformed_X='csr_matrix_int64_int64'):
                if changeVoc:
                    m.vocabulary = hdrl__iead
                transformed_X = m.fit_transform(X, y)
                transformed_X.indices = transformed_X.indices.astype(np.int64)
                transformed_X.indptr = transformed_X.indptr.astype(np.int64)
            return transformed_X
        return _count_vectorizer_fit_transform_impl
    else:

        def _count_vectorizer_fit_transform_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(transformed_X='csr_matrix_int64_int64'):
                transformed_X = m.fit_transform(X, y)
                transformed_X.indices = transformed_X.indices.astype(np.int64)
                transformed_X.indptr = transformed_X.indptr.astype(np.int64)
            return transformed_X
        return _count_vectorizer_fit_transform_impl


@overload_method(BodoFExtractCountVectorizerType, 'get_feature_names_out',
    no_unliteral=True)
def overload_count_vectorizer_get_feature_names_out(m):
    check_sklearn_version()

    def impl(m):
        with numba.objmode(result=bodo.string_array_type):
            result = m.get_feature_names_out()
        return result
    return impl
