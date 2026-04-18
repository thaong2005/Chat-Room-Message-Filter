# Generated from c:\Users\hung1\Learn\Sem2_2026\PPL\Chat-Room-Message-Filter\backend\antlr\BadWords.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\6")
        buf.write("\30\4\2\t\2\4\3\t\3\4\4\t\4\3\2\7\2\n\n\2\f\2\16\2\r\13")
        buf.write("\2\3\2\3\2\3\3\6\3\22\n\3\r\3\16\3\23\3\4\3\4\3\4\2\2")
        buf.write("\5\2\4\6\2\3\3\2\3\5\2\26\2\13\3\2\2\2\4\21\3\2\2\2\6")
        buf.write("\25\3\2\2\2\b\n\5\4\3\2\t\b\3\2\2\2\n\r\3\2\2\2\13\t\3")
        buf.write("\2\2\2\13\f\3\2\2\2\f\16\3\2\2\2\r\13\3\2\2\2\16\17\7")
        buf.write("\2\2\3\17\3\3\2\2\2\20\22\5\6\4\2\21\20\3\2\2\2\22\23")
        buf.write("\3\2\2\2\23\21\3\2\2\2\23\24\3\2\2\2\24\5\3\2\2\2\25\26")
        buf.write("\t\2\2\2\26\7\3\2\2\2\4\13\23")
        return buf.getvalue()


class BadWordsParser ( Parser ):

    grammarFileName = "BadWords.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "BAD_WORD", "NORMAL_WORD", "WHITESPACE", 
                      "ANY" ]

    RULE_program = 0
    RULE_message = 1
    RULE_word = 2

    ruleNames =  [ "program", "message", "word" ]

    EOF = Token.EOF
    BAD_WORD=1
    NORMAL_WORD=2
    WHITESPACE=3
    ANY=4

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(BadWordsParser.EOF, 0)

        def message(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BadWordsParser.MessageContext)
            else:
                return self.getTypedRuleContext(BadWordsParser.MessageContext,i)


        def getRuleIndex(self):
            return BadWordsParser.RULE_program




    def program(self):

        localctx = BadWordsParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << BadWordsParser.BAD_WORD) | (1 << BadWordsParser.NORMAL_WORD) | (1 << BadWordsParser.WHITESPACE))) != 0):
                self.state = 6
                self.message()
                self.state = 11
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 12
            self.match(BadWordsParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessageContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def word(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BadWordsParser.WordContext)
            else:
                return self.getTypedRuleContext(BadWordsParser.WordContext,i)


        def getRuleIndex(self):
            return BadWordsParser.RULE_message




    def message(self):

        localctx = BadWordsParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_message)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 14
                    self.word()

                else:
                    raise NoViableAltException(self)
                self.state = 17 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BAD_WORD(self):
            return self.getToken(BadWordsParser.BAD_WORD, 0)

        def NORMAL_WORD(self):
            return self.getToken(BadWordsParser.NORMAL_WORD, 0)

        def WHITESPACE(self):
            return self.getToken(BadWordsParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return BadWordsParser.RULE_word




    def word(self):

        localctx = BadWordsParser.WordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_word)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << BadWordsParser.BAD_WORD) | (1 << BadWordsParser.NORMAL_WORD) | (1 << BadWordsParser.WHITESPACE))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





