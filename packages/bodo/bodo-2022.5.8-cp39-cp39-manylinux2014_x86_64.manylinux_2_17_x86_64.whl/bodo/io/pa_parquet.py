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
    except Exception as xoq__xpjt:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    dioeu__ctrkb = None
    xjkz__freq = delta_lake_path.rstrip('/')
    arvyw__nbuk = 'AWS_DEFAULT_REGION' in os.environ
    tva__waqp = os.environ.get('AWS_DEFAULT_REGION', '')
    elpq__jmhsq = False
    if delta_lake_path.startswith('s3://'):
        nzor__ocyzt = get_s3_bucket_region_njit(delta_lake_path, parallel=False
            )
        if nzor__ocyzt != '':
            os.environ['AWS_DEFAULT_REGION'] = nzor__ocyzt
            elpq__jmhsq = True
    eqj__bxpbt = DeltaTable(delta_lake_path)
    dioeu__ctrkb = eqj__bxpbt.files()
    dioeu__ctrkb = [(xjkz__freq + '/' + dpet__hqskb) for dpet__hqskb in
        sorted(dioeu__ctrkb)]
    if elpq__jmhsq:
        if arvyw__nbuk:
            os.environ['AWS_DEFAULT_REGION'] = tva__waqp
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return dioeu__ctrkb


def _make_manifest(path_or_paths, fs, pathsep='/', metadata_nthreads=1,
    open_file_func=None):
    partitions = None
    sku__qayok = None
    fmyt__muuj = None
    if isinstance(path_or_paths, list) and len(path_or_paths) == 1:
        path_or_paths = path_or_paths[0]
    if pq._is_path_like(path_or_paths) and fs.isdir(path_or_paths):
        manifest = ParquetManifest(path_or_paths, filesystem=fs,
            open_file_func=open_file_func, pathsep=getattr(fs, 'pathsep',
            '/'), metadata_nthreads=metadata_nthreads)
        sku__qayok = manifest.common_metadata_path
        fmyt__muuj = manifest.metadata_path
        pieces = manifest.pieces
        partitions = manifest.partitions
    else:
        if not isinstance(path_or_paths, list):
            path_or_paths = [path_or_paths]
        if len(path_or_paths) == 0:
            raise ValueError('Must pass at least one file path')
        pieces = []
        glu__vjfrq = urlparse(path_or_paths[0]).scheme
        for xjkz__freq in path_or_paths:
            if not glu__vjfrq and not fs.isfile(xjkz__freq):
                raise OSError(
                    f'Passed non-file path: {xjkz__freq}, but only files or glob strings (no directories) are supported when passing a list'
                    )
            piece = pq.ParquetDatasetPiece._create(xjkz__freq,
                open_file_func=open_file_func)
            pieces.append(piece)
    return pieces, partitions, sku__qayok, fmyt__muuj


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
    osvn__yrk = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for ijy__bqsu in dataset.partitions.partition_names:
            if osvn__yrk.get_field_index(ijy__bqsu) != -1:
                nxzb__givqj = osvn__yrk.get_field_index(ijy__bqsu)
                osvn__yrk = osvn__yrk.remove(nxzb__givqj)
    return osvn__yrk


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
        except Exception as xoq__xpjt:
            self.exc = xoq__xpjt
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
        cua__hlo = VisitLevelThread(self)
        cua__hlo.start()
        cua__hlo.join()
        for maw__jgajb in self.partition_vals.keys():
            self.partition_vals[maw__jgajb] = sorted(self.partition_vals[
                maw__jgajb])
        for qer__vradv in self.partitions.levels:
            qer__vradv.keys = sorted(qer__vradv.keys)
        for fpj__iuytm in self.pieces:
            if fpj__iuytm.partition_keys is not None:
                fpj__iuytm.partition_keys = [(slqp__laes, self.
                    partition_vals[slqp__laes].index(ehbw__rbgtk)) for 
                    slqp__laes, ehbw__rbgtk in fpj__iuytm.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, nnq__tkdui, base_path, ekfc__xfiwp):
        fs = self.filesystem
        gxe__vuupz, qcss__ewrt, bsfan__qpg = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if nnq__tkdui == 0 and '_delta_log' in qcss__ewrt:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        mzwbp__rvf = []
        for xjkz__freq in bsfan__qpg:
            if xjkz__freq == '':
                continue
            jbj__eimu = self.pathsep.join((base_path, xjkz__freq))
            if xjkz__freq.endswith('_common_metadata'):
                self.common_metadata_path = jbj__eimu
            elif xjkz__freq.endswith('_metadata'):
                self.metadata_path = jbj__eimu
            elif self._should_silently_exclude(xjkz__freq):
                continue
            elif self.delta_lake_filter and jbj__eimu not in self.delta_lake_filter:
                continue
            else:
                mzwbp__rvf.append(jbj__eimu)
        stfue__yung = [self.pathsep.join((base_path, ecs__jhdgp)) for
            ecs__jhdgp in qcss__ewrt if not pq._is_private_directory(
            ecs__jhdgp)]
        mzwbp__rvf.sort()
        stfue__yung.sort()
        if len(mzwbp__rvf) > 0 and len(stfue__yung) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(stfue__yung) > 0:
            await self._visit_directories(nnq__tkdui, stfue__yung, ekfc__xfiwp)
        else:
            self._push_pieces(mzwbp__rvf, ekfc__xfiwp)

    async def _visit_directories(self, nnq__tkdui, qcss__ewrt, ekfc__xfiwp):
        ujm__vay = []
        for xjkz__freq in qcss__ewrt:
            orcc__cnsht, qtky__qjvbs = pq._path_split(xjkz__freq, self.pathsep)
            slqp__laes, bdh__izv = pq._parse_hive_partition(qtky__qjvbs)
            kkifz__cvyt = self.partitions.get_index(nnq__tkdui, slqp__laes,
                bdh__izv)
            self.partition_vals[slqp__laes].add(bdh__izv)
            hpfg__dmh = ekfc__xfiwp + [(slqp__laes, bdh__izv)]
            ujm__vay.append(self._visit_level(nnq__tkdui + 1, xjkz__freq,
                hpfg__dmh))
        await asyncio.wait(ujm__vay)


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
