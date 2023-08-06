import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    kyzo__wwovw = hi - lo
    if kyzo__wwovw < 2:
        return
    if kyzo__wwovw < MIN_MERGE:
        xsct__igxs = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + xsct__igxs, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    arg__qug = minRunLength(kyzo__wwovw)
    while True:
        ckfg__avp = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if ckfg__avp < arg__qug:
            gkg__vbjal = kyzo__wwovw if kyzo__wwovw <= arg__qug else arg__qug
            binarySort(key_arrs, lo, lo + gkg__vbjal, lo + ckfg__avp, data)
            ckfg__avp = gkg__vbjal
        stackSize = pushRun(stackSize, runBase, runLen, lo, ckfg__avp)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += ckfg__avp
        kyzo__wwovw -= ckfg__avp
        if kyzo__wwovw == 0:
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
        lqw__xiir = getitem_arr_tup(key_arrs, start)
        oqd__eys = getitem_arr_tup(data, start)
        hkb__tjod = lo
        pogtm__tlth = start
        assert hkb__tjod <= pogtm__tlth
        while hkb__tjod < pogtm__tlth:
            egeby__otd = hkb__tjod + pogtm__tlth >> 1
            if lqw__xiir < getitem_arr_tup(key_arrs, egeby__otd):
                pogtm__tlth = egeby__otd
            else:
                hkb__tjod = egeby__otd + 1
        assert hkb__tjod == pogtm__tlth
        n = start - hkb__tjod
        copyRange_tup(key_arrs, hkb__tjod, key_arrs, hkb__tjod + 1, n)
        copyRange_tup(data, hkb__tjod, data, hkb__tjod + 1, n)
        setitem_arr_tup(key_arrs, hkb__tjod, lqw__xiir)
        setitem_arr_tup(data, hkb__tjod, oqd__eys)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    reiig__zsm = lo + 1
    if reiig__zsm == hi:
        return 1
    if getitem_arr_tup(key_arrs, reiig__zsm) < getitem_arr_tup(key_arrs, lo):
        reiig__zsm += 1
        while reiig__zsm < hi and getitem_arr_tup(key_arrs, reiig__zsm
            ) < getitem_arr_tup(key_arrs, reiig__zsm - 1):
            reiig__zsm += 1
        reverseRange(key_arrs, lo, reiig__zsm, data)
    else:
        reiig__zsm += 1
        while reiig__zsm < hi and getitem_arr_tup(key_arrs, reiig__zsm
            ) >= getitem_arr_tup(key_arrs, reiig__zsm - 1):
            reiig__zsm += 1
    return reiig__zsm - lo


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
    rceg__ibrbf = 0
    while n >= MIN_MERGE:
        rceg__ibrbf |= n & 1
        n >>= 1
    return n + rceg__ibrbf


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    izd__genyf = len(key_arrs[0])
    tmpLength = (izd__genyf >> 1 if izd__genyf < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    tvjx__ezf = (5 if izd__genyf < 120 else 10 if izd__genyf < 1542 else 19 if
        izd__genyf < 119151 else 40)
    runBase = np.empty(tvjx__ezf, np.int64)
    runLen = np.empty(tvjx__ezf, np.int64)
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
    pdr__dpfe = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert pdr__dpfe >= 0
    base1 += pdr__dpfe
    len1 -= pdr__dpfe
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
    knxlv__cgqp = 0
    qatnc__ztn = 1
    if key > getitem_arr_tup(arr, base + hint):
        pxz__jzkdb = _len - hint
        while qatnc__ztn < pxz__jzkdb and key > getitem_arr_tup(arr, base +
            hint + qatnc__ztn):
            knxlv__cgqp = qatnc__ztn
            qatnc__ztn = (qatnc__ztn << 1) + 1
            if qatnc__ztn <= 0:
                qatnc__ztn = pxz__jzkdb
        if qatnc__ztn > pxz__jzkdb:
            qatnc__ztn = pxz__jzkdb
        knxlv__cgqp += hint
        qatnc__ztn += hint
    else:
        pxz__jzkdb = hint + 1
        while qatnc__ztn < pxz__jzkdb and key <= getitem_arr_tup(arr, base +
            hint - qatnc__ztn):
            knxlv__cgqp = qatnc__ztn
            qatnc__ztn = (qatnc__ztn << 1) + 1
            if qatnc__ztn <= 0:
                qatnc__ztn = pxz__jzkdb
        if qatnc__ztn > pxz__jzkdb:
            qatnc__ztn = pxz__jzkdb
        tmp = knxlv__cgqp
        knxlv__cgqp = hint - qatnc__ztn
        qatnc__ztn = hint - tmp
    assert -1 <= knxlv__cgqp and knxlv__cgqp < qatnc__ztn and qatnc__ztn <= _len
    knxlv__cgqp += 1
    while knxlv__cgqp < qatnc__ztn:
        rgs__bqsk = knxlv__cgqp + (qatnc__ztn - knxlv__cgqp >> 1)
        if key > getitem_arr_tup(arr, base + rgs__bqsk):
            knxlv__cgqp = rgs__bqsk + 1
        else:
            qatnc__ztn = rgs__bqsk
    assert knxlv__cgqp == qatnc__ztn
    return qatnc__ztn


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    qatnc__ztn = 1
    knxlv__cgqp = 0
    if key < getitem_arr_tup(arr, base + hint):
        pxz__jzkdb = hint + 1
        while qatnc__ztn < pxz__jzkdb and key < getitem_arr_tup(arr, base +
            hint - qatnc__ztn):
            knxlv__cgqp = qatnc__ztn
            qatnc__ztn = (qatnc__ztn << 1) + 1
            if qatnc__ztn <= 0:
                qatnc__ztn = pxz__jzkdb
        if qatnc__ztn > pxz__jzkdb:
            qatnc__ztn = pxz__jzkdb
        tmp = knxlv__cgqp
        knxlv__cgqp = hint - qatnc__ztn
        qatnc__ztn = hint - tmp
    else:
        pxz__jzkdb = _len - hint
        while qatnc__ztn < pxz__jzkdb and key >= getitem_arr_tup(arr, base +
            hint + qatnc__ztn):
            knxlv__cgqp = qatnc__ztn
            qatnc__ztn = (qatnc__ztn << 1) + 1
            if qatnc__ztn <= 0:
                qatnc__ztn = pxz__jzkdb
        if qatnc__ztn > pxz__jzkdb:
            qatnc__ztn = pxz__jzkdb
        knxlv__cgqp += hint
        qatnc__ztn += hint
    assert -1 <= knxlv__cgqp and knxlv__cgqp < qatnc__ztn and qatnc__ztn <= _len
    knxlv__cgqp += 1
    while knxlv__cgqp < qatnc__ztn:
        rgs__bqsk = knxlv__cgqp + (qatnc__ztn - knxlv__cgqp >> 1)
        if key < getitem_arr_tup(arr, base + rgs__bqsk):
            qatnc__ztn = rgs__bqsk
        else:
            knxlv__cgqp = rgs__bqsk + 1
    assert knxlv__cgqp == qatnc__ztn
    return qatnc__ztn


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
        uqr__nqazl = 0
        qowxm__sxt = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                qowxm__sxt += 1
                uqr__nqazl = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                uqr__nqazl += 1
                qowxm__sxt = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not uqr__nqazl | qowxm__sxt < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            uqr__nqazl = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if uqr__nqazl != 0:
                copyRange_tup(tmp, cursor1, arr, dest, uqr__nqazl)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, uqr__nqazl)
                dest += uqr__nqazl
                cursor1 += uqr__nqazl
                len1 -= uqr__nqazl
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            qowxm__sxt = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if qowxm__sxt != 0:
                copyRange_tup(arr, cursor2, arr, dest, qowxm__sxt)
                copyRange_tup(arr_data, cursor2, arr_data, dest, qowxm__sxt)
                dest += qowxm__sxt
                cursor2 += qowxm__sxt
                len2 -= qowxm__sxt
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
            if not uqr__nqazl >= MIN_GALLOP | qowxm__sxt >= MIN_GALLOP:
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
        uqr__nqazl = 0
        qowxm__sxt = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                uqr__nqazl += 1
                qowxm__sxt = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                qowxm__sxt += 1
                uqr__nqazl = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not uqr__nqazl | qowxm__sxt < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            uqr__nqazl = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if uqr__nqazl != 0:
                dest -= uqr__nqazl
                cursor1 -= uqr__nqazl
                len1 -= uqr__nqazl
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, uqr__nqazl)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    uqr__nqazl)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            qowxm__sxt = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if qowxm__sxt != 0:
                dest -= qowxm__sxt
                cursor2 -= qowxm__sxt
                len2 -= qowxm__sxt
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, qowxm__sxt)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    qowxm__sxt)
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
            if not uqr__nqazl >= MIN_GALLOP | qowxm__sxt >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    qcxli__tiaui = len(key_arrs[0])
    if tmpLength < minCapacity:
        hin__tgtm = minCapacity
        hin__tgtm |= hin__tgtm >> 1
        hin__tgtm |= hin__tgtm >> 2
        hin__tgtm |= hin__tgtm >> 4
        hin__tgtm |= hin__tgtm >> 8
        hin__tgtm |= hin__tgtm >> 16
        hin__tgtm += 1
        if hin__tgtm < 0:
            hin__tgtm = minCapacity
        else:
            hin__tgtm = min(hin__tgtm, qcxli__tiaui >> 1)
        tmp = alloc_arr_tup(hin__tgtm, key_arrs)
        tmp_data = alloc_arr_tup(hin__tgtm, data)
        tmpLength = hin__tgtm
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        xvex__haku = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = xvex__haku


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    uyzrn__kau = arr_tup.count
    lre__vtqqs = 'def f(arr_tup, lo, hi):\n'
    for i in range(uyzrn__kau):
        lre__vtqqs += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        lre__vtqqs += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        lre__vtqqs += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    lre__vtqqs += '  return\n'
    lbp__dxj = {}
    exec(lre__vtqqs, {}, lbp__dxj)
    xbvn__ouu = lbp__dxj['f']
    return xbvn__ouu


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    uyzrn__kau = src_arr_tup.count
    assert uyzrn__kau == dst_arr_tup.count
    lre__vtqqs = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(uyzrn__kau):
        lre__vtqqs += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    lre__vtqqs += '  return\n'
    lbp__dxj = {}
    exec(lre__vtqqs, {'copyRange': copyRange}, lbp__dxj)
    fty__uof = lbp__dxj['f']
    return fty__uof


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    uyzrn__kau = src_arr_tup.count
    assert uyzrn__kau == dst_arr_tup.count
    lre__vtqqs = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(uyzrn__kau):
        lre__vtqqs += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    lre__vtqqs += '  return\n'
    lbp__dxj = {}
    exec(lre__vtqqs, {'copyElement': copyElement}, lbp__dxj)
    fty__uof = lbp__dxj['f']
    return fty__uof


def getitem_arr_tup(arr_tup, ind):
    incjv__iptd = [arr[ind] for arr in arr_tup]
    return tuple(incjv__iptd)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    uyzrn__kau = arr_tup.count
    lre__vtqqs = 'def f(arr_tup, ind):\n'
    lre__vtqqs += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(uyzrn__kau)]), ',' if uyzrn__kau == 1 else '')
    lbp__dxj = {}
    exec(lre__vtqqs, {}, lbp__dxj)
    orsk__jif = lbp__dxj['f']
    return orsk__jif


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, tcksw__roo in zip(arr_tup, val_tup):
        arr[ind] = tcksw__roo


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    uyzrn__kau = arr_tup.count
    lre__vtqqs = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(uyzrn__kau):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            lre__vtqqs += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            lre__vtqqs += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    lre__vtqqs += '  return\n'
    lbp__dxj = {}
    exec(lre__vtqqs, {}, lbp__dxj)
    orsk__jif = lbp__dxj['f']
    return orsk__jif


def test():
    import time
    ieqzq__ypam = time.time()
    oxr__frrqg = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((oxr__frrqg,), 0, 3, data)
    print('compile time', time.time() - ieqzq__ypam)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    wtvml__hvkwb = np.random.ranf(n)
    ssctr__yoeay = pd.DataFrame({'A': wtvml__hvkwb, 'B': data[0], 'C': data[1]}
        )
    ieqzq__ypam = time.time()
    cycfz__nuiun = ssctr__yoeay.sort_values('A', inplace=False)
    agvo__rfaw = time.time()
    sort((wtvml__hvkwb,), 0, n, data)
    print('Bodo', time.time() - agvo__rfaw, 'Numpy', agvo__rfaw - ieqzq__ypam)
    np.testing.assert_almost_equal(data[0], cycfz__nuiun.B.values)
    np.testing.assert_almost_equal(data[1], cycfz__nuiun.C.values)


if __name__ == '__main__':
    test()
