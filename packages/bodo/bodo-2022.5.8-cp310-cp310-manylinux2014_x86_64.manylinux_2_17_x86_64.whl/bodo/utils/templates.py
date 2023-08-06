"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            cgdu__bfy = set()
            iiaxr__wvmf = list(self.context._get_attribute_templates(self.key))
            nfp__sohrq = iiaxr__wvmf.index(self) + 1
            for asr__kiul in range(nfp__sohrq, len(iiaxr__wvmf)):
                if isinstance(iiaxr__wvmf[asr__kiul], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    cgdu__bfy.add(iiaxr__wvmf[asr__kiul]._attr)
            self._attr_set = cgdu__bfy
        return attr_name in self._attr_set
