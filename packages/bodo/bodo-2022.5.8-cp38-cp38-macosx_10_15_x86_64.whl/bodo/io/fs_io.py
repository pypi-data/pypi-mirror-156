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
            abkiz__vnxst = self.fs.open_input_file(path)
        except:
            abkiz__vnxst = self.fs.open_input_stream(path)
    elif mode == 'wb':
        abkiz__vnxst = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, abkiz__vnxst, path, mode, block_size, **kwargs)


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
    lpx__uxdh = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    vkgfu__ktezv = False
    qpbyo__hzu = get_proxy_uri_from_env_vars()
    if storage_options:
        vkgfu__ktezv = storage_options.get('anon', False)
    return S3FileSystem(anonymous=vkgfu__ktezv, region=region,
        endpoint_override=lpx__uxdh, proxy_options=qpbyo__hzu)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    lpx__uxdh = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    vkgfu__ktezv = False
    qpbyo__hzu = get_proxy_uri_from_env_vars()
    if storage_options:
        vkgfu__ktezv = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=lpx__uxdh, anonymous
        =vkgfu__ktezv, proxy_options=qpbyo__hzu)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    edixw__kmw = urlparse(path)
    if edixw__kmw.scheme in ('abfs', 'abfss'):
        khei__xggu = path
        if edixw__kmw.port is None:
            fpls__kma = 0
        else:
            fpls__kma = edixw__kmw.port
        ztld__ngwqx = None
    else:
        khei__xggu = edixw__kmw.hostname
        fpls__kma = edixw__kmw.port
        ztld__ngwqx = edixw__kmw.username
    try:
        fs = HdFS(host=khei__xggu, port=fpls__kma, user=ztld__ngwqx)
    except Exception as ibxxf__ummx:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            ibxxf__ummx))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        tzc__difm = fs.isdir(path)
    except gcsfs.utils.HttpError as ibxxf__ummx:
        raise BodoError(
            f'{ibxxf__ummx}. Make sure your google cloud credentials are set!')
    return tzc__difm


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [mac__pkcfy.split('/')[-1] for mac__pkcfy in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        edixw__kmw = urlparse(path)
        tlel__hds = (edixw__kmw.netloc + edixw__kmw.path).rstrip('/')
        myxa__quss = fs.get_file_info(tlel__hds)
        if myxa__quss.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not myxa__quss.size and myxa__quss.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as ibxxf__ummx:
        raise
    except BodoError as spnl__wnwvj:
        raise
    except Exception as ibxxf__ummx:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ibxxf__ummx).__name__}: {str(ibxxf__ummx)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    brw__qojz = None
    try:
        if s3_is_directory(fs, path):
            edixw__kmw = urlparse(path)
            tlel__hds = (edixw__kmw.netloc + edixw__kmw.path).rstrip('/')
            cldk__ljb = pa_fs.FileSelector(tlel__hds, recursive=False)
            ntnnn__ymgc = fs.get_file_info(cldk__ljb)
            if ntnnn__ymgc and ntnnn__ymgc[0].path in [tlel__hds,
                f'{tlel__hds}/'] and int(ntnnn__ymgc[0].size or 0) == 0:
                ntnnn__ymgc = ntnnn__ymgc[1:]
            brw__qojz = [oay__ryqh.base_name for oay__ryqh in ntnnn__ymgc]
    except BodoError as spnl__wnwvj:
        raise
    except Exception as ibxxf__ummx:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ibxxf__ummx).__name__}: {str(ibxxf__ummx)}
{bodo_error_msg}"""
            )
    return brw__qojz


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    edixw__kmw = urlparse(path)
    uuo__vgmbr = edixw__kmw.path
    try:
        qyyfb__nmop = HadoopFileSystem.from_uri(path)
    except Exception as ibxxf__ummx:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            ibxxf__ummx))
    rtyql__cornd = qyyfb__nmop.get_file_info([uuo__vgmbr])
    if rtyql__cornd[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not rtyql__cornd[0].size and rtyql__cornd[0].type == FileType.Directory:
        return qyyfb__nmop, True
    return qyyfb__nmop, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    brw__qojz = None
    qyyfb__nmop, tzc__difm = hdfs_is_directory(path)
    if tzc__difm:
        edixw__kmw = urlparse(path)
        uuo__vgmbr = edixw__kmw.path
        cldk__ljb = FileSelector(uuo__vgmbr, recursive=True)
        try:
            ntnnn__ymgc = qyyfb__nmop.get_file_info(cldk__ljb)
        except Exception as ibxxf__ummx:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(uuo__vgmbr, ibxxf__ummx))
        brw__qojz = [oay__ryqh.base_name for oay__ryqh in ntnnn__ymgc]
    return qyyfb__nmop, brw__qojz


def abfs_is_directory(path):
    qyyfb__nmop = get_hdfs_fs(path)
    try:
        rtyql__cornd = qyyfb__nmop.info(path)
    except OSError as spnl__wnwvj:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if rtyql__cornd['size'] == 0 and rtyql__cornd['kind'].lower(
        ) == 'directory':
        return qyyfb__nmop, True
    return qyyfb__nmop, False


def abfs_list_dir_fnames(path):
    brw__qojz = None
    qyyfb__nmop, tzc__difm = abfs_is_directory(path)
    if tzc__difm:
        edixw__kmw = urlparse(path)
        uuo__vgmbr = edixw__kmw.path
        try:
            hyw__kzcu = qyyfb__nmop.ls(uuo__vgmbr)
        except Exception as ibxxf__ummx:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(uuo__vgmbr, ibxxf__ummx))
        brw__qojz = [fname[fname.rindex('/') + 1:] for fname in hyw__kzcu]
    return qyyfb__nmop, brw__qojz


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ushjd__dhdc = urlparse(path)
    fname = path
    fs = None
    aotya__wkd = 'read_json' if ftype == 'json' else 'read_csv'
    nzs__jtnh = (
        f'pd.{aotya__wkd}(): there is no {ftype} file in directory: {fname}')
    ymav__ryvox = directory_of_files_common_filter
    if ushjd__dhdc.scheme == 's3':
        wlk__myi = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        poibo__wdeb = s3_list_dir_fnames(fs, path)
        tlel__hds = (ushjd__dhdc.netloc + ushjd__dhdc.path).rstrip('/')
        fname = tlel__hds
        if poibo__wdeb:
            poibo__wdeb = [(tlel__hds + '/' + mac__pkcfy) for mac__pkcfy in
                sorted(filter(ymav__ryvox, poibo__wdeb))]
            nikjz__nbh = [mac__pkcfy for mac__pkcfy in poibo__wdeb if int(
                fs.get_file_info(mac__pkcfy).size or 0) > 0]
            if len(nikjz__nbh) == 0:
                raise BodoError(nzs__jtnh)
            fname = nikjz__nbh[0]
        fpunr__ujq = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        imjp__nmh = fs._open(fname)
    elif ushjd__dhdc.scheme == 'hdfs':
        wlk__myi = True
        fs, poibo__wdeb = hdfs_list_dir_fnames(path)
        fpunr__ujq = fs.get_file_info([ushjd__dhdc.path])[0].size
        if poibo__wdeb:
            path = path.rstrip('/')
            poibo__wdeb = [(path + '/' + mac__pkcfy) for mac__pkcfy in
                sorted(filter(ymav__ryvox, poibo__wdeb))]
            nikjz__nbh = [mac__pkcfy for mac__pkcfy in poibo__wdeb if fs.
                get_file_info([urlparse(mac__pkcfy).path])[0].size > 0]
            if len(nikjz__nbh) == 0:
                raise BodoError(nzs__jtnh)
            fname = nikjz__nbh[0]
            fname = urlparse(fname).path
            fpunr__ujq = fs.get_file_info([fname])[0].size
        imjp__nmh = fs.open_input_file(fname)
    elif ushjd__dhdc.scheme in ('abfs', 'abfss'):
        wlk__myi = True
        fs, poibo__wdeb = abfs_list_dir_fnames(path)
        fpunr__ujq = fs.info(fname)['size']
        if poibo__wdeb:
            path = path.rstrip('/')
            poibo__wdeb = [(path + '/' + mac__pkcfy) for mac__pkcfy in
                sorted(filter(ymav__ryvox, poibo__wdeb))]
            nikjz__nbh = [mac__pkcfy for mac__pkcfy in poibo__wdeb if fs.
                info(mac__pkcfy)['size'] > 0]
            if len(nikjz__nbh) == 0:
                raise BodoError(nzs__jtnh)
            fname = nikjz__nbh[0]
            fpunr__ujq = fs.info(fname)['size']
            fname = urlparse(fname).path
        imjp__nmh = fs.open(fname, 'rb')
    else:
        if ushjd__dhdc.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ushjd__dhdc.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        wlk__myi = False
        if os.path.isdir(path):
            hyw__kzcu = filter(ymav__ryvox, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            nikjz__nbh = [mac__pkcfy for mac__pkcfy in sorted(hyw__kzcu) if
                os.path.getsize(mac__pkcfy) > 0]
            if len(nikjz__nbh) == 0:
                raise BodoError(nzs__jtnh)
            fname = nikjz__nbh[0]
        fpunr__ujq = os.path.getsize(fname)
        imjp__nmh = fname
    return wlk__myi, imjp__nmh, fpunr__ujq, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    umgel__rnuk = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            xminh__awtx, sqv__yaq = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = xminh__awtx.region
        except Exception as ibxxf__ummx:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{ibxxf__ummx}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = umgel__rnuk.bcast(bucket_loc)
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
        czs__tff = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel)
        ahm__ypu, gur__vukt = unicode_to_utf8_and_len(D)
        fyk__elw = 0
        if is_parallel:
            fyk__elw = bodo.libs.distributed_api.dist_exscan(gur__vukt, np.
                int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), ahm__ypu, fyk__elw,
            gur__vukt, is_parallel, unicode_to_utf8(czs__tff))
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
    tehhj__ljqt = get_overload_constant_dict(storage_options)
    rel__sgwyl = 'def impl(storage_options):\n'
    rel__sgwyl += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    rel__sgwyl += f'    storage_options_py = {str(tehhj__ljqt)}\n'
    rel__sgwyl += '  return storage_options_py\n'
    btzw__xcicu = {}
    exec(rel__sgwyl, globals(), btzw__xcicu)
    return btzw__xcicu['impl']
