import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    mtl__poas = hi - lo
    if mtl__poas < 2:
        return
    if mtl__poas < MIN_MERGE:
        jccoa__mrxi = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + jccoa__mrxi, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    eal__rpkz = minRunLength(mtl__poas)
    while True:
        pigr__rqupq = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if pigr__rqupq < eal__rpkz:
            mddy__nfsp = mtl__poas if mtl__poas <= eal__rpkz else eal__rpkz
            binarySort(key_arrs, lo, lo + mddy__nfsp, lo + pigr__rqupq, data)
            pigr__rqupq = mddy__nfsp
        stackSize = pushRun(stackSize, runBase, runLen, lo, pigr__rqupq)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += pigr__rqupq
        mtl__poas -= pigr__rqupq
        if mtl__poas == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        kyfi__fkn = getitem_arr_tup(key_arrs, start)
        drwyu__vmi = getitem_arr_tup(data, start)
        fia__madgg = lo
        mkhyc__bvm = start
        assert fia__madgg <= mkhyc__bvm
        while fia__madgg < mkhyc__bvm:
            nad__ibdt = fia__madgg + mkhyc__bvm >> 1
            if kyfi__fkn < getitem_arr_tup(key_arrs, nad__ibdt):
                mkhyc__bvm = nad__ibdt
            else:
                fia__madgg = nad__ibdt + 1
        assert fia__madgg == mkhyc__bvm
        n = start - fia__madgg
        copyRange_tup(key_arrs, fia__madgg, key_arrs, fia__madgg + 1, n)
        copyRange_tup(data, fia__madgg, data, fia__madgg + 1, n)
        setitem_arr_tup(key_arrs, fia__madgg, kyfi__fkn)
        setitem_arr_tup(data, fia__madgg, drwyu__vmi)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    ccdq__rai = lo + 1
    if ccdq__rai == hi:
        return 1
    if getitem_arr_tup(key_arrs, ccdq__rai) < getitem_arr_tup(key_arrs, lo):
        ccdq__rai += 1
        while ccdq__rai < hi and getitem_arr_tup(key_arrs, ccdq__rai
            ) < getitem_arr_tup(key_arrs, ccdq__rai - 1):
            ccdq__rai += 1
        reverseRange(key_arrs, lo, ccdq__rai, data)
    else:
        ccdq__rai += 1
        while ccdq__rai < hi and getitem_arr_tup(key_arrs, ccdq__rai
            ) >= getitem_arr_tup(key_arrs, ccdq__rai - 1):
            ccdq__rai += 1
    return ccdq__rai - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    azybj__vif = 0
    while n >= MIN_MERGE:
        azybj__vif |= n & 1
        n >>= 1
    return n + azybj__vif


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    iox__dmb = len(key_arrs[0])
    tmpLength = (iox__dmb >> 1 if iox__dmb < 2 * INITIAL_TMP_STORAGE_LENGTH
         else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    mel__ttcjt = (5 if iox__dmb < 120 else 10 if iox__dmb < 1542 else 19 if
        iox__dmb < 119151 else 40)
    runBase = np.empty(mel__ttcjt, np.int64)
    runLen = np.empty(mel__ttcjt, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    ipr__nvo = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert ipr__nvo >= 0
    base1 += ipr__nvo
    len1 -= ipr__nvo
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    pimly__nqw = 0
    wfrw__tulyy = 1
    if key > getitem_arr_tup(arr, base + hint):
        sawb__gqml = _len - hint
        while wfrw__tulyy < sawb__gqml and key > getitem_arr_tup(arr, base +
            hint + wfrw__tulyy):
            pimly__nqw = wfrw__tulyy
            wfrw__tulyy = (wfrw__tulyy << 1) + 1
            if wfrw__tulyy <= 0:
                wfrw__tulyy = sawb__gqml
        if wfrw__tulyy > sawb__gqml:
            wfrw__tulyy = sawb__gqml
        pimly__nqw += hint
        wfrw__tulyy += hint
    else:
        sawb__gqml = hint + 1
        while wfrw__tulyy < sawb__gqml and key <= getitem_arr_tup(arr, base +
            hint - wfrw__tulyy):
            pimly__nqw = wfrw__tulyy
            wfrw__tulyy = (wfrw__tulyy << 1) + 1
            if wfrw__tulyy <= 0:
                wfrw__tulyy = sawb__gqml
        if wfrw__tulyy > sawb__gqml:
            wfrw__tulyy = sawb__gqml
        tmp = pimly__nqw
        pimly__nqw = hint - wfrw__tulyy
        wfrw__tulyy = hint - tmp
    assert -1 <= pimly__nqw and pimly__nqw < wfrw__tulyy and wfrw__tulyy <= _len
    pimly__nqw += 1
    while pimly__nqw < wfrw__tulyy:
        htf__sdbfv = pimly__nqw + (wfrw__tulyy - pimly__nqw >> 1)
        if key > getitem_arr_tup(arr, base + htf__sdbfv):
            pimly__nqw = htf__sdbfv + 1
        else:
            wfrw__tulyy = htf__sdbfv
    assert pimly__nqw == wfrw__tulyy
    return wfrw__tulyy


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    wfrw__tulyy = 1
    pimly__nqw = 0
    if key < getitem_arr_tup(arr, base + hint):
        sawb__gqml = hint + 1
        while wfrw__tulyy < sawb__gqml and key < getitem_arr_tup(arr, base +
            hint - wfrw__tulyy):
            pimly__nqw = wfrw__tulyy
            wfrw__tulyy = (wfrw__tulyy << 1) + 1
            if wfrw__tulyy <= 0:
                wfrw__tulyy = sawb__gqml
        if wfrw__tulyy > sawb__gqml:
            wfrw__tulyy = sawb__gqml
        tmp = pimly__nqw
        pimly__nqw = hint - wfrw__tulyy
        wfrw__tulyy = hint - tmp
    else:
        sawb__gqml = _len - hint
        while wfrw__tulyy < sawb__gqml and key >= getitem_arr_tup(arr, base +
            hint + wfrw__tulyy):
            pimly__nqw = wfrw__tulyy
            wfrw__tulyy = (wfrw__tulyy << 1) + 1
            if wfrw__tulyy <= 0:
                wfrw__tulyy = sawb__gqml
        if wfrw__tulyy > sawb__gqml:
            wfrw__tulyy = sawb__gqml
        pimly__nqw += hint
        wfrw__tulyy += hint
    assert -1 <= pimly__nqw and pimly__nqw < wfrw__tulyy and wfrw__tulyy <= _len
    pimly__nqw += 1
    while pimly__nqw < wfrw__tulyy:
        htf__sdbfv = pimly__nqw + (wfrw__tulyy - pimly__nqw >> 1)
        if key < getitem_arr_tup(arr, base + htf__sdbfv):
            wfrw__tulyy = htf__sdbfv
        else:
            pimly__nqw = htf__sdbfv + 1
    assert pimly__nqw == wfrw__tulyy
    return wfrw__tulyy


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        qycrn__tcxe = 0
        jolwy__mmqvz = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                jolwy__mmqvz += 1
                qycrn__tcxe = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                qycrn__tcxe += 1
                jolwy__mmqvz = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not qycrn__tcxe | jolwy__mmqvz < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            qycrn__tcxe = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if qycrn__tcxe != 0:
                copyRange_tup(tmp, cursor1, arr, dest, qycrn__tcxe)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, qycrn__tcxe)
                dest += qycrn__tcxe
                cursor1 += qycrn__tcxe
                len1 -= qycrn__tcxe
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            jolwy__mmqvz = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if jolwy__mmqvz != 0:
                copyRange_tup(arr, cursor2, arr, dest, jolwy__mmqvz)
                copyRange_tup(arr_data, cursor2, arr_data, dest, jolwy__mmqvz)
                dest += jolwy__mmqvz
                cursor2 += jolwy__mmqvz
                len2 -= jolwy__mmqvz
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not qycrn__tcxe >= MIN_GALLOP | jolwy__mmqvz >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        qycrn__tcxe = 0
        jolwy__mmqvz = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                qycrn__tcxe += 1
                jolwy__mmqvz = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                jolwy__mmqvz += 1
                qycrn__tcxe = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not qycrn__tcxe | jolwy__mmqvz < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            qycrn__tcxe = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if qycrn__tcxe != 0:
                dest -= qycrn__tcxe
                cursor1 -= qycrn__tcxe
                len1 -= qycrn__tcxe
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, qycrn__tcxe)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    qycrn__tcxe)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            jolwy__mmqvz = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if jolwy__mmqvz != 0:
                dest -= jolwy__mmqvz
                cursor2 -= jolwy__mmqvz
                len2 -= jolwy__mmqvz
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, jolwy__mmqvz)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    jolwy__mmqvz)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not qycrn__tcxe >= MIN_GALLOP | jolwy__mmqvz >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    usaxt__ofi = len(key_arrs[0])
    if tmpLength < minCapacity:
        gbbk__xtysh = minCapacity
        gbbk__xtysh |= gbbk__xtysh >> 1
        gbbk__xtysh |= gbbk__xtysh >> 2
        gbbk__xtysh |= gbbk__xtysh >> 4
        gbbk__xtysh |= gbbk__xtysh >> 8
        gbbk__xtysh |= gbbk__xtysh >> 16
        gbbk__xtysh += 1
        if gbbk__xtysh < 0:
            gbbk__xtysh = minCapacity
        else:
            gbbk__xtysh = min(gbbk__xtysh, usaxt__ofi >> 1)
        tmp = alloc_arr_tup(gbbk__xtysh, key_arrs)
        tmp_data = alloc_arr_tup(gbbk__xtysh, data)
        tmpLength = gbbk__xtysh
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        alf__ykqd = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = alf__ykqd


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    yjioc__gei = arr_tup.count
    znfit__xpkm = 'def f(arr_tup, lo, hi):\n'
    for i in range(yjioc__gei):
        znfit__xpkm += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        znfit__xpkm += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        znfit__xpkm += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    znfit__xpkm += '  return\n'
    oscx__oji = {}
    exec(znfit__xpkm, {}, oscx__oji)
    std__eyakc = oscx__oji['f']
    return std__eyakc


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    yjioc__gei = src_arr_tup.count
    assert yjioc__gei == dst_arr_tup.count
    znfit__xpkm = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(yjioc__gei):
        znfit__xpkm += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    znfit__xpkm += '  return\n'
    oscx__oji = {}
    exec(znfit__xpkm, {'copyRange': copyRange}, oscx__oji)
    cnun__jwqe = oscx__oji['f']
    return cnun__jwqe


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    yjioc__gei = src_arr_tup.count
    assert yjioc__gei == dst_arr_tup.count
    znfit__xpkm = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(yjioc__gei):
        znfit__xpkm += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    znfit__xpkm += '  return\n'
    oscx__oji = {}
    exec(znfit__xpkm, {'copyElement': copyElement}, oscx__oji)
    cnun__jwqe = oscx__oji['f']
    return cnun__jwqe


def getitem_arr_tup(arr_tup, ind):
    icwre__ded = [arr[ind] for arr in arr_tup]
    return tuple(icwre__ded)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    yjioc__gei = arr_tup.count
    znfit__xpkm = 'def f(arr_tup, ind):\n'
    znfit__xpkm += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(yjioc__gei)]), ',' if yjioc__gei == 1 else '')
    oscx__oji = {}
    exec(znfit__xpkm, {}, oscx__oji)
    bnvp__gvmqu = oscx__oji['f']
    return bnvp__gvmqu


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, andjt__ydw in zip(arr_tup, val_tup):
        arr[ind] = andjt__ydw


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    yjioc__gei = arr_tup.count
    znfit__xpkm = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(yjioc__gei):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            znfit__xpkm += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            znfit__xpkm += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    znfit__xpkm += '  return\n'
    oscx__oji = {}
    exec(znfit__xpkm, {}, oscx__oji)
    bnvp__gvmqu = oscx__oji['f']
    return bnvp__gvmqu


def test():
    import time
    dyd__tle = time.time()
    zkwb__tfxf = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((zkwb__tfxf,), 0, 3, data)
    print('compile time', time.time() - dyd__tle)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    ujw__ubt = np.random.ranf(n)
    wmjdx__duvk = pd.DataFrame({'A': ujw__ubt, 'B': data[0], 'C': data[1]})
    dyd__tle = time.time()
    yvpw__czdkx = wmjdx__duvk.sort_values('A', inplace=False)
    uegk__hqylh = time.time()
    sort((ujw__ubt,), 0, n, data)
    print('Bodo', time.time() - uegk__hqylh, 'Numpy', uegk__hqylh - dyd__tle)
    np.testing.assert_almost_equal(data[0], yvpw__czdkx.B.values)
    np.testing.assert_almost_equal(data[1], yvpw__czdkx.C.values)


if __name__ == '__main__':
    test()
