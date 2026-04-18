# Generated from c:\Users\hung1\Learn\Sem2_2026\PPL\Chat-Room-Message-Filter\backend\antlr\BadWords.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\6")
        buf.write("G\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\3\2\3\2\3\2")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3")
        buf.write("\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3")
        buf.write("\2\3\2\5\2:\n\2\3\3\6\3=\n\3\r\3\16\3>\3\4\6\4B\n\4\r")
        buf.write("\4\16\4C\3\5\3\5\2\2\6\3\3\5\4\7\5\t\6\3\2\4\b\2##.\60")
        buf.write("\62=A\\aac|\5\2\13\f\17\17\"\"\2M\2\3\3\2\2\2\2\5\3\2")
        buf.write("\2\2\2\7\3\2\2\2\2\t\3\2\2\2\39\3\2\2\2\5<\3\2\2\2\7A")
        buf.write("\3\2\2\2\tE\3\2\2\2\13\f\7d\2\2\f\r\7c\2\2\r\16\7f\2\2")
        buf.write("\16\17\7y\2\2\17\20\7q\2\2\20\21\7t\2\2\21\22\7f\2\2\22")
        buf.write(":\7\63\2\2\23\24\7d\2\2\24\25\7c\2\2\25\26\7f\2\2\26\27")
        buf.write("\7y\2\2\27\30\7q\2\2\30\31\7t\2\2\31\32\7f\2\2\32:\7\64")
        buf.write("\2\2\33\34\7j\2\2\34\35\7c\2\2\35\36\7v\2\2\36:\7g\2\2")
        buf.write("\37 \7u\2\2 !\7r\2\2!\"\7c\2\2\":\7o\2\2#$\7q\2\2$%\7")
        buf.write("h\2\2%&\7h\2\2&\'\7g\2\2\'(\7p\2\2()\7u\2\2)*\7k\2\2*")
        buf.write("+\7x\2\2+:\7g\2\2,-\7k\2\2-.\7p\2\2./\7c\2\2/\60\7r\2")
        buf.write("\2\60\61\7r\2\2\61\62\7t\2\2\62\63\7q\2\2\63\64\7r\2\2")
        buf.write("\64\65\7t\2\2\65\66\7k\2\2\66\67\7c\2\2\678\7v\2\28:\7")
        buf.write("g\2\29\13\3\2\2\29\23\3\2\2\29\33\3\2\2\29\37\3\2\2\2")
        buf.write("9#\3\2\2\29,\3\2\2\2:\4\3\2\2\2;=\t\2\2\2<;\3\2\2\2=>")
        buf.write("\3\2\2\2><\3\2\2\2>?\3\2\2\2?\6\3\2\2\2@B\t\3\2\2A@\3")
        buf.write("\2\2\2BC\3\2\2\2CA\3\2\2\2CD\3\2\2\2D\b\3\2\2\2EF\13\2")
        buf.write("\2\2F\n\3\2\2\2\6\29>C\2")
        return buf.getvalue()


class BadWordsLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    BAD_WORD = 1
    NORMAL_WORD = 2
    WHITESPACE = 3
    ANY = 4

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
 ]

    symbolicNames = [ "<INVALID>",
            "BAD_WORD", "NORMAL_WORD", "WHITESPACE", "ANY" ]

    ruleNames = [ "BAD_WORD", "NORMAL_WORD", "WHITESPACE", "ANY" ]

    grammarFileName = "BadWords.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


