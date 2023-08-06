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
            psnoy__jsgn = set()
            ikp__ziis = list(self.context._get_attribute_templates(self.key))
            hrxtu__aofs = ikp__ziis.index(self) + 1
            for hcho__left in range(hrxtu__aofs, len(ikp__ziis)):
                if isinstance(ikp__ziis[hcho__left], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    psnoy__jsgn.add(ikp__ziis[hcho__left]._attr)
            self._attr_set = psnoy__jsgn
        return attr_name in self._attr_set
