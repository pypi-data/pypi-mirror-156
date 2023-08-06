import hashlib
import inspect
import warnings
import pandas as pd
pandas_version = tuple(map(int, pd.__version__.split('.')[:2]))
_check_pandas_change = False
if pandas_version < (1, 4):

    def _set_noconvert_columns(self):
        assert self.orig_names is not None
        ghqo__baeu = {ggd__hdq: dwuvm__alnxs for dwuvm__alnxs, ggd__hdq in
            enumerate(self.orig_names)}
        kux__saty = [ghqo__baeu[ggd__hdq] for ggd__hdq in self.names]
        ylrkl__oiibu = self._set_noconvert_dtype_columns(kux__saty, self.names)
        for yjms__zpgu in ylrkl__oiibu:
            self._reader.set_noconvert(yjms__zpgu)
    if _check_pandas_change:
        lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.
            CParserWrapper._set_noconvert_columns)
        if (hashlib.sha256(lines.encode()).hexdigest() !=
            'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3'
            ):
            warnings.warn(
                'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
                )
    (pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns
        ) = _set_noconvert_columns
