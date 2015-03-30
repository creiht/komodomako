#!/usr/bin/env python
# Copyright (c) 2008-2011 Chuck Thier
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

"""Mako support for codeintel.

This file will be imported by the codeintel system on startup and the
register() function called to register this language with the system. All
Code Intelligence for this language is controlled through this module.
"""

import os
import sys
import logging

from codeintel2.common import *
from codeintel2.langintel import LangIntel
from codeintel2.udl import UDLLexer, UDLBuffer, UDLCILEDriver, XMLParsingBufferMixin

try:
    from xpcom.server import UnwrapObject
    _xpcom_ = True
except ImportError:
    _xpcom_ = False

#---- globals

lang = "Mako"
log = logging.getLogger("codeintel.mako")
#log.setLevel(logging.DEBUG)

#---- Lexer class

class MakoLexer(UDLLexer):
    lang = lang

#---- LangIntel class

# Dev Notes:
# All language should define a LangIntel class. (In some rare cases it
# isn't needed but there is little reason not to have the empty subclass.)
#
# One instance of the LangIntel class will be created for each codeintel
# language. Code browser functionality and some buffer functionality
# often defers to the LangIntel singleton.
#
# This is especially important for multi-lang files. For example, an
# HTML buffer uses the JavaScriptLangIntel and the CSSLangIntel for
# handling codeintel functionality in <script> and <style> tags.
#
# See other lang_*.py files in your Komodo installation for examples of
# usage.
class MakoLangIntel(LangIntel):
    lang = lang

    ##
    # Implicit codeintel triggering event, i.e. when typing in the editor.
    #
    # @param buf {components.interfaces.koICodeIntelBuffer}
    # @param pos {int} The cursor position in the editor/text.
    # @param implicit {bool} Automatically called, else manually called?
    #
    def trg_from_pos(self, buf, pos, implicit=True, DEBUG=False, ac=None):
        #DEBUG = True
        if pos < 1:
            return None

        # accessor {codeintel2.accessor.Accessor} - Examine text and styling.
        accessor = buf.accessor
        last_pos = pos-1
        char = accessor.char_at_pos(last_pos)
        style = accessor.style_at_pos(last_pos)
        if DEBUG:
            print "trg_from_pos: char: %r, style: %d" % (char, accessor.style_at_pos(last_pos), )
        if style in (SCE_UDL_SSL_WORD, SCE_UDL_SSL_IDENTIFIER):
            # Functions/builtins completion trigger.
            start, end = accessor.contiguous_style_range_from_pos(last_pos)
            if DEBUG:
                print "identifier style, start: %d, end: %d" % (start, end)
            # Trigger when two characters have been typed.
            if (last_pos - start) == 1:
                if DEBUG:
                    print "triggered:: complete identifiers"
                return Trigger(self.lang, TRG_FORM_CPLN, "identifiers",
                               start, implicit,
                               word_start=start, word_end=end)
        return None


    ##
    # Explicit triggering event, i.e. Ctrl+J.
    #
    # @param buf {components.interfaces.koICodeIntelBuffer}
    # @param pos {int} The cursor position in the editor/text.
    # @param implicit {bool} Automatically called, else manually called?
    #
    def preceding_trg_from_pos(self, buf, pos, curr_pos,
                               preceding_trg_terminators=None, DEBUG=False):
        #DEBUG = True
        if pos < 1:
            return None

        # accessor {codeintel2.accessor.Accessor} - Examine text and styling.
        accessor = buf.accessor
        last_pos = pos-1
        char = accessor.char_at_pos(last_pos)
        style = accessor.style_at_pos(last_pos)
        if DEBUG:
            print "pos: %d, curr_pos: %d" % (pos, curr_pos)
            print "char: %r, style: %d" % (char, style)
        if style in (SCE_UDL_SSL_WORD, SCE_UDL_SSL_IDENTIFIER):
            # Functions/builtins completion trigger.
            start, end = accessor.contiguous_style_range_from_pos(last_pos)
            if DEBUG:
                print "triggered:: complete identifiers"
            return Trigger(self.lang, TRG_FORM_CPLN, "identifiers",
                           start, implicit=False,
                           word_start=start, word_end=end)
        return None

    ##
    # Provide the list of completions or the calltip string.
    # Completions are a list of tuple (type, name) items.
    #
    # Note: This example is *not* asynchronous.
    def async_eval_at_trg(self, buf, trg, ctlr):
        if _xpcom_:
            trg = UnwrapObject(trg)
            ctlr = UnwrapObject(ctlr)
        pos = trg.pos
        ctlr.start(buf, trg)

        if trg.id == (self.lang, TRG_FORM_CPLN, "identifiers"):
            word_start = trg.extra.get("word_start")
            word_end = trg.extra.get("word_end")
            if word_start is not None and word_end is not None:
                # Only return keywords that start with the given 2-char prefix.
                prefix = buf.accessor.text_range(word_start, word_end)[:2]
                cplns = [x for x in keywords if x.startswith(prefix)]
                cplns = [("keyword", x) for x in sorted(cplns, cmp=CompareNPunctLast)]
                ctlr.set_cplns(cplns)
                ctlr.done("success")
                return

        ctlr.error("Unknown trigger type: %r" % (trg, ))
        ctlr.done("error")

#---- Buffer class

class MakoBuffer(UDLBuffer, XMLParsingBufferMixin):
    lang = lang
    tpl_lang = lang
    m_lang = "HTML"
    css_lang = "CSS"
    csl_lang = "JavaScript"
    ssl_lang = "Python"
    tpl_lang = "MAKO"

    cb_show_if_empty = True

    cpln_stop_chars = "'\" (;},~`@#%^&*()=+{}]|\\;,.<>?/"

#---- CILE Driver class

# Dev Notes:
# A CILE (Code Intelligence Language Engine) is the code that scans
# Mako content and returns a description of the code in that file.
# See "cile_mako.py" for more details.
#
# The CILE Driver is a class that calls this CILE. If Mako is
# multi-lang (i.e. can contain sections of different language content,
# e.g. HTML can contain markup, JavaScript and CSS), then you will need
# to also implement "scan_multilang()".
#class MakoCILEDriver(CILEDriver):
#    lang = lang
#
#    def scan_purelang(self, buf):
#        import cile_mako
#        return cile_mako.scan_buf(buf)

class MakoCILEDriver(UDLCILEDriver):
    lang = lang
    csl_lang = "JavaScript"
    ssl_lang = "Python"

#---- registration

def register(mgr):
    """Register language support with the Manager."""
    mgr.set_lang_info(
        lang,
        silvercity_lexer=MakoLexer(),
        buf_class=MakoBuffer,
        langintel_class=MakoLangIntel,
        import_handler_class=None,
        cile_driver_class=MakoCILEDriver,
        is_cpln_lang=True)
