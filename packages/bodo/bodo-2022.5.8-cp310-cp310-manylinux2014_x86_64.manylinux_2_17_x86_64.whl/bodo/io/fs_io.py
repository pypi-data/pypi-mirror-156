"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from fsspec.implementations.arrow import ArrowFile, ArrowFSWrapper, wrap_exceptions
from numba.core import types
from numba.extending import NativeValue, models, overload, register_model, unbox
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning, get_overload_constant_dict
from bodo.utils.utils import check_java_installation


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            mxy__zevz = self.fs.open_input_file(path)
        except:
            mxy__zevz = self.fs.open_input_stream(path)
    elif mode == 'wb':
        mxy__zevz = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, mxy__zevz, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
        (4) Wrong bucket region is used. Set AWS_DEFAULT_REGION variable with correct bucket region.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    how__itm = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    rdfn__jmted = False
    spo__doici = get_proxy_uri_from_env_vars()
    if storage_options:
        rdfn__jmted = storage_options.get('anon', False)
    return S3FileSystem(anonymous=rdfn__jmted, region=region,
        endpoint_override=how__itm, proxy_options=spo__doici)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    how__itm = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    rdfn__jmted = False
    spo__doici = get_proxy_uri_from_env_vars()
    if storage_options:
        rdfn__jmted = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=how__itm, anonymous=
        rdfn__jmted, proxy_options=spo__doici)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    netdn__fcs = urlparse(path)
    if netdn__fcs.scheme in ('abfs', 'abfss'):
        agogp__zqs = path
        if netdn__fcs.port is None:
            hocpz__cjwjw = 0
        else:
            hocpz__cjwjw = netdn__fcs.port
        fwvnu__maa = None
    else:
        agogp__zqs = netdn__fcs.hostname
        hocpz__cjwjw = netdn__fcs.port
        fwvnu__maa = netdn__fcs.username
    try:
        fs = HdFS(host=agogp__zqs, port=hocpz__cjwjw, user=fwvnu__maa)
    except Exception as uthan__nsy:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            uthan__nsy))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        vojm__eohg = fs.isdir(path)
    except gcsfs.utils.HttpError as uthan__nsy:
        raise BodoError(
            f'{uthan__nsy}. Make sure your google cloud credentials are set!')
    return vojm__eohg


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [fbafy__pza.split('/')[-1] for fbafy__pza in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        netdn__fcs = urlparse(path)
        keud__cwr = (netdn__fcs.netloc + netdn__fcs.path).rstrip('/')
        fgnkv__kdlr = fs.get_file_info(keud__cwr)
        if fgnkv__kdlr.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not fgnkv__kdlr.size and fgnkv__kdlr.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as uthan__nsy:
        raise
    except BodoError as mhgjr__eaix:
        raise
    except Exception as uthan__nsy:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(uthan__nsy).__name__}: {str(uthan__nsy)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    enj__bprz = None
    try:
        if s3_is_directory(fs, path):
            netdn__fcs = urlparse(path)
            keud__cwr = (netdn__fcs.netloc + netdn__fcs.path).rstrip('/')
            ywht__xilwj = pa_fs.FileSelector(keud__cwr, recursive=False)
            qflv__wveuh = fs.get_file_info(ywht__xilwj)
            if qflv__wveuh and qflv__wveuh[0].path in [keud__cwr,
                f'{keud__cwr}/'] and int(qflv__wveuh[0].size or 0) == 0:
                qflv__wveuh = qflv__wveuh[1:]
            enj__bprz = [flaa__xxkk.base_name for flaa__xxkk in qflv__wveuh]
    except BodoError as mhgjr__eaix:
        raise
    except Exception as uthan__nsy:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(uthan__nsy).__name__}: {str(uthan__nsy)}
{bodo_error_msg}"""
            )
    return enj__bprz


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    netdn__fcs = urlparse(path)
    oxb__xqjw = netdn__fcs.path
    try:
        crf__lgie = HadoopFileSystem.from_uri(path)
    except Exception as uthan__nsy:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            uthan__nsy))
    sgjam__lwesz = crf__lgie.get_file_info([oxb__xqjw])
    if sgjam__lwesz[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not sgjam__lwesz[0].size and sgjam__lwesz[0].type == FileType.Directory:
        return crf__lgie, True
    return crf__lgie, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    enj__bprz = None
    crf__lgie, vojm__eohg = hdfs_is_directory(path)
    if vojm__eohg:
        netdn__fcs = urlparse(path)
        oxb__xqjw = netdn__fcs.path
        ywht__xilwj = FileSelector(oxb__xqjw, recursive=True)
        try:
            qflv__wveuh = crf__lgie.get_file_info(ywht__xilwj)
        except Exception as uthan__nsy:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(oxb__xqjw, uthan__nsy))
        enj__bprz = [flaa__xxkk.base_name for flaa__xxkk in qflv__wveuh]
    return crf__lgie, enj__bprz


def abfs_is_directory(path):
    crf__lgie = get_hdfs_fs(path)
    try:
        sgjam__lwesz = crf__lgie.info(path)
    except OSError as mhgjr__eaix:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if sgjam__lwesz['size'] == 0 and sgjam__lwesz['kind'].lower(
        ) == 'directory':
        return crf__lgie, True
    return crf__lgie, False


def abfs_list_dir_fnames(path):
    enj__bprz = None
    crf__lgie, vojm__eohg = abfs_is_directory(path)
    if vojm__eohg:
        netdn__fcs = urlparse(path)
        oxb__xqjw = netdn__fcs.path
        try:
            grug__zzhsp = crf__lgie.ls(oxb__xqjw)
        except Exception as uthan__nsy:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(oxb__xqjw, uthan__nsy))
        enj__bprz = [fname[fname.rindex('/') + 1:] for fname in grug__zzhsp]
    return crf__lgie, enj__bprz


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    qomfn__etfkz = urlparse(path)
    fname = path
    fs = None
    zwo__vkh = 'read_json' if ftype == 'json' else 'read_csv'
    uuqo__rwm = (
        f'pd.{zwo__vkh}(): there is no {ftype} file in directory: {fname}')
    grsmm__uapb = directory_of_files_common_filter
    if qomfn__etfkz.scheme == 's3':
        ooyc__oicwg = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        klc__fjypf = s3_list_dir_fnames(fs, path)
        keud__cwr = (qomfn__etfkz.netloc + qomfn__etfkz.path).rstrip('/')
        fname = keud__cwr
        if klc__fjypf:
            klc__fjypf = [(keud__cwr + '/' + fbafy__pza) for fbafy__pza in
                sorted(filter(grsmm__uapb, klc__fjypf))]
            cqeb__fui = [fbafy__pza for fbafy__pza in klc__fjypf if int(fs.
                get_file_info(fbafy__pza).size or 0) > 0]
            if len(cqeb__fui) == 0:
                raise BodoError(uuqo__rwm)
            fname = cqeb__fui[0]
        ngtb__ctc = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        dlsoz__cnm = fs._open(fname)
    elif qomfn__etfkz.scheme == 'hdfs':
        ooyc__oicwg = True
        fs, klc__fjypf = hdfs_list_dir_fnames(path)
        ngtb__ctc = fs.get_file_info([qomfn__etfkz.path])[0].size
        if klc__fjypf:
            path = path.rstrip('/')
            klc__fjypf = [(path + '/' + fbafy__pza) for fbafy__pza in
                sorted(filter(grsmm__uapb, klc__fjypf))]
            cqeb__fui = [fbafy__pza for fbafy__pza in klc__fjypf if fs.
                get_file_info([urlparse(fbafy__pza).path])[0].size > 0]
            if len(cqeb__fui) == 0:
                raise BodoError(uuqo__rwm)
            fname = cqeb__fui[0]
            fname = urlparse(fname).path
            ngtb__ctc = fs.get_file_info([fname])[0].size
        dlsoz__cnm = fs.open_input_file(fname)
    elif qomfn__etfkz.scheme in ('abfs', 'abfss'):
        ooyc__oicwg = True
        fs, klc__fjypf = abfs_list_dir_fnames(path)
        ngtb__ctc = fs.info(fname)['size']
        if klc__fjypf:
            path = path.rstrip('/')
            klc__fjypf = [(path + '/' + fbafy__pza) for fbafy__pza in
                sorted(filter(grsmm__uapb, klc__fjypf))]
            cqeb__fui = [fbafy__pza for fbafy__pza in klc__fjypf if fs.info
                (fbafy__pza)['size'] > 0]
            if len(cqeb__fui) == 0:
                raise BodoError(uuqo__rwm)
            fname = cqeb__fui[0]
            ngtb__ctc = fs.info(fname)['size']
            fname = urlparse(fname).path
        dlsoz__cnm = fs.open(fname, 'rb')
    else:
        if qomfn__etfkz.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {qomfn__etfkz.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        ooyc__oicwg = False
        if os.path.isdir(path):
            grug__zzhsp = filter(grsmm__uapb, glob.glob(os.path.join(os.
                path.abspath(path), '*')))
            cqeb__fui = [fbafy__pza for fbafy__pza in sorted(grug__zzhsp) if
                os.path.getsize(fbafy__pza) > 0]
            if len(cqeb__fui) == 0:
                raise BodoError(uuqo__rwm)
            fname = cqeb__fui[0]
        ngtb__ctc = os.path.getsize(fname)
        dlsoz__cnm = fname
    return ooyc__oicwg, dlsoz__cnm, ngtb__ctc, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    ukjer__houtj = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            zrax__tikc, wkwk__weji = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = zrax__tikc.region
        except Exception as uthan__nsy:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{uthan__nsy}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = ukjer__houtj.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, is_parallel=False):

    def impl(path_or_buf, D, is_parallel=False):
        umd__yrtuw = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        ahvil__nkag, rcgap__fce = unicode_to_utf8_and_len(D)
        tsoks__gabuq = 0
        if is_parallel:
            tsoks__gabuq = bodo.libs.distributed_api.dist_exscan(rcgap__fce,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), ahvil__nkag, tsoks__gabuq,
            rcgap__fce, is_parallel, unicode_to_utf8(umd__yrtuw))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    gxvvm__oldy = get_overload_constant_dict(storage_options)
    pxw__kpdb = 'def impl(storage_options):\n'
    pxw__kpdb += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    pxw__kpdb += f'    storage_options_py = {str(gxvvm__oldy)}\n'
    pxw__kpdb += '  return storage_options_py\n'
    ukbq__gigl = {}
    exec(pxw__kpdb, globals(), ukbq__gigl)
    return ukbq__gigl['impl']
