import asyncio
import os
import threading
from collections import defaultdict
from concurrent import futures
from urllib.parse import urlparse
import pyarrow.parquet as pq
from bodo.io.fs_io import get_s3_bucket_region_njit


def get_parquet_filesnames_from_deltalake(delta_lake_path):
    try:
        from deltalake import DeltaTable
    except Exception as ncxvm__pifq:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    wtdn__oamae = None
    gjrjb__eckrg = delta_lake_path.rstrip('/')
    jwvra__qll = 'AWS_DEFAULT_REGION' in os.environ
    bnts__wzqwl = os.environ.get('AWS_DEFAULT_REGION', '')
    vceu__ketrt = False
    if delta_lake_path.startswith('s3://'):
        mwysq__aal = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if mwysq__aal != '':
            os.environ['AWS_DEFAULT_REGION'] = mwysq__aal
            vceu__ketrt = True
    shl__ywys = DeltaTable(delta_lake_path)
    wtdn__oamae = shl__ywys.files()
    wtdn__oamae = [(gjrjb__eckrg + '/' + qlavt__jld) for qlavt__jld in
        sorted(wtdn__oamae)]
    if vceu__ketrt:
        if jwvra__qll:
            os.environ['AWS_DEFAULT_REGION'] = bnts__wzqwl
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return wtdn__oamae


def _make_manifest(path_or_paths, fs, pathsep='/', metadata_nthreads=1,
    open_file_func=None):
    partitions = None
    cab__caj = None
    xjo__tmhr = None
    if isinstance(path_or_paths, list) and len(path_or_paths) == 1:
        path_or_paths = path_or_paths[0]
    if pq._is_path_like(path_or_paths) and fs.isdir(path_or_paths):
        manifest = ParquetManifest(path_or_paths, filesystem=fs,
            open_file_func=open_file_func, pathsep=getattr(fs, 'pathsep',
            '/'), metadata_nthreads=metadata_nthreads)
        cab__caj = manifest.common_metadata_path
        xjo__tmhr = manifest.metadata_path
        pieces = manifest.pieces
        partitions = manifest.partitions
    else:
        if not isinstance(path_or_paths, list):
            path_or_paths = [path_or_paths]
        if len(path_or_paths) == 0:
            raise ValueError('Must pass at least one file path')
        pieces = []
        gkvt__qzrvn = urlparse(path_or_paths[0]).scheme
        for gjrjb__eckrg in path_or_paths:
            if not gkvt__qzrvn and not fs.isfile(gjrjb__eckrg):
                raise OSError(
                    f'Passed non-file path: {gjrjb__eckrg}, but only files or glob strings (no directories) are supported when passing a list'
                    )
            piece = pq.ParquetDatasetPiece._create(gjrjb__eckrg,
                open_file_func=open_file_func)
            pieces.append(piece)
    return pieces, partitions, cab__caj, xjo__tmhr


pq._make_manifest = _make_manifest


def get_dataset_schema(dataset):
    if hasattr(dataset, '_bodo_arrow_schema'):
        return dataset._bodo_arrow_schema
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    yldq__imoqm = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for qks__vpp in dataset.partitions.partition_names:
            if yldq__imoqm.get_field_index(qks__vpp) != -1:
                xjr__bduij = yldq__imoqm.get_field_index(qks__vpp)
                yldq__imoqm = yldq__imoqm.remove(xjr__bduij)
    return yldq__imoqm


class VisitLevelThread(threading.Thread):

    def __init__(self, manifest):
        threading.Thread.__init__(self)
        self.manifest = manifest
        self.exc = None

    def run(self):
        try:
            manifest = self.manifest
            manifest.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(manifest.loop)
            manifest.loop.run_until_complete(manifest._visit_level(0,
                manifest.dirpath, []))
        except Exception as ncxvm__pifq:
            self.exc = ncxvm__pifq
        finally:
            if hasattr(manifest, 'loop') and not manifest.loop.is_closed():
                manifest.loop.close()

    def join(self):
        super(VisitLevelThread, self).join()
        if self.exc:
            raise self.exc


class ParquetManifest:

    def __init__(self, dirpath, open_file_func=None, filesystem=None,
        pathsep='/', partition_scheme='hive', metadata_nthreads=1):
        filesystem, dirpath = pq._get_filesystem_and_path(filesystem, dirpath)
        self.filesystem = filesystem
        self.open_file_func = open_file_func
        self.pathsep = pathsep
        self.dirpath = pq._stringify_path(dirpath)
        self.partition_scheme = partition_scheme
        self.partitions = pq.ParquetPartitions()
        self.pieces = []
        self._metadata_nthreads = metadata_nthreads
        self._thread_pool = futures.ThreadPoolExecutor(max_workers=
            metadata_nthreads)
        self.common_metadata_path = None
        self.metadata_path = None
        self.delta_lake_filter = set()
        self.partition_vals = defaultdict(set)
        wpxzl__twa = VisitLevelThread(self)
        wpxzl__twa.start()
        wpxzl__twa.join()
        for oxnfy__ajfa in self.partition_vals.keys():
            self.partition_vals[oxnfy__ajfa] = sorted(self.partition_vals[
                oxnfy__ajfa])
        for lsvio__mjq in self.partitions.levels:
            lsvio__mjq.keys = sorted(lsvio__mjq.keys)
        for wer__sqmlb in self.pieces:
            if wer__sqmlb.partition_keys is not None:
                wer__sqmlb.partition_keys = [(mpsd__iea, self.
                    partition_vals[mpsd__iea].index(ikjtk__ekpzg)) for 
                    mpsd__iea, ikjtk__ekpzg in wer__sqmlb.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, yjb__umw, base_path, fta__njfl):
        fs = self.filesystem
        ryhj__bivio, mfsi__heb, otbz__kbk = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if yjb__umw == 0 and '_delta_log' in mfsi__heb:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        paqln__lofq = []
        for gjrjb__eckrg in otbz__kbk:
            if gjrjb__eckrg == '':
                continue
            cagu__ykb = self.pathsep.join((base_path, gjrjb__eckrg))
            if gjrjb__eckrg.endswith('_common_metadata'):
                self.common_metadata_path = cagu__ykb
            elif gjrjb__eckrg.endswith('_metadata'):
                self.metadata_path = cagu__ykb
            elif self._should_silently_exclude(gjrjb__eckrg):
                continue
            elif self.delta_lake_filter and cagu__ykb not in self.delta_lake_filter:
                continue
            else:
                paqln__lofq.append(cagu__ykb)
        gtswk__ruuv = [self.pathsep.join((base_path, ime__ukch)) for
            ime__ukch in mfsi__heb if not pq._is_private_directory(ime__ukch)]
        paqln__lofq.sort()
        gtswk__ruuv.sort()
        if len(paqln__lofq) > 0 and len(gtswk__ruuv) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(gtswk__ruuv) > 0:
            await self._visit_directories(yjb__umw, gtswk__ruuv, fta__njfl)
        else:
            self._push_pieces(paqln__lofq, fta__njfl)

    async def _visit_directories(self, yjb__umw, mfsi__heb, fta__njfl):
        ywtz__yxgz = []
        for gjrjb__eckrg in mfsi__heb:
            tuov__iqh, xrww__ehrw = pq._path_split(gjrjb__eckrg, self.pathsep)
            mpsd__iea, bob__nxpn = pq._parse_hive_partition(xrww__ehrw)
            qld__kgii = self.partitions.get_index(yjb__umw, mpsd__iea,
                bob__nxpn)
            self.partition_vals[mpsd__iea].add(bob__nxpn)
            izj__iwg = fta__njfl + [(mpsd__iea, bob__nxpn)]
            ywtz__yxgz.append(self._visit_level(yjb__umw + 1, gjrjb__eckrg,
                izj__iwg))
        await asyncio.wait(ywtz__yxgz)


ParquetManifest._should_silently_exclude = (pq.ParquetManifest.
    _should_silently_exclude)
ParquetManifest._parse_partition = pq.ParquetManifest._parse_partition
ParquetManifest._push_pieces = pq.ParquetManifest._push_pieces
pq.ParquetManifest = ParquetManifest


def pieces(self):
    return self._pieces


pq.ParquetDataset.pieces = property(pieces)


def partitions(self):
    return self._partitions


pq.ParquetDataset.partitions = property(partitions)
