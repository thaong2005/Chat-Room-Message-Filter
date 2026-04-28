grammar BadWords;

/**
 * ANTLR Grammar for detecting and filtering bad words
 * This grammar defines rules to identify bad words in messages
 */

// ========== Parser Rules ==========
program
    : message* EOF
    ;

message
    : word+
    ;

word
    : BAD_WORD
    | NORMAL_WORD
    | WHITESPACE
    ;

// ========== Lexer Rules ==========

// Bad words list - Can be extended
BAD_WORD
    : ('badword1' | 'badword2' | 'hate' | 'spam' | 'offensive' | 'inappropriate')
    ;

// Normal words and characters - match any non-whitespace
NORMAL_WORD
    : [a-zA-Z0-9_@.!?,;:\-]+ 
    ;

// Whitespace
WHITESPACE
    : [ \t\n\r]+
    ;

// Catch-all rule for any remaining characters
ANY
    : .
    ;
