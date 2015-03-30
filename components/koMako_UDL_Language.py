# Copyright (c) 2008-2012 Chuck Thier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.

# Komodo Mako language service.

import logging
from koXMLLanguageBase import koHTMLLanguageBase

log = logging.getLogger("koMakoLanguage")
#log.setLevel(logging.DEBUG)


def registerLanguage(registry):
    log.debug("Registering language Mako")
    registry.registerLanguage(KoMakoLanguage())


class KoMakoLanguage(koHTMLLanguageBase):
    name = "Mako"
    lexresLangName = "Mako"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" % name
    _reg_categories_ = [("komodo-language", name)]
    _reg_clsid_ = "5207496e-a7b8-4e10-ba35-f77c07fa3539"
    defaultExtension = '.mako'

    supportsSmartIndent = "brace"

    lang_from_udl_family = {
        'CSL': 'JavaScript',
        'TPL': 'Mako',
        'M': 'HTML',
        'CSS': 'CSS',
        'SSL': 'Python',
    }
