"""
ANTLR-based bad word filter for chat messages
Detects and replaces bad words using ANTLR grammar
"""

import os
import sys
from pathlib import Path

try:
    from antlr4 import InputStream, CommonTokenStream, Token
    
    # Add compiled ANTLR files to path
    antlr_compiled = os.path.join(os.path.dirname(__file__), 'antlr', 'CompiledFiles')
    if os.path.exists(antlr_compiled):
        sys.path.insert(0, antlr_compiled)
        from BadWordsLexer import BadWordsLexer
        from BadWordsParser import BadWordsParser
        ANTLR_AVAILABLE = True
    else:
        ANTLR_AVAILABLE = False
except ImportError:
    ANTLR_AVAILABLE = False


def load_bad_words_from_file(file_path=None):
    """
    Load bad words from a text file
    
    Args:
        file_path: Path to bad_words.txt file. If None, uses default location.
    
    Returns:
        list: List of bad words (comments and empty lines are ignored)
    """
    if file_path is None:
        # Default location: same directory as this file
        file_path = os.path.join(os.path.dirname(__file__), 'bad_words.txt')
    
    bad_words = []
    
    if not os.path.exists(file_path):
        print(f"Warning: Bad words file not found at {file_path}")
        return bad_words
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip whitespace
                word = line.strip()
                
                # Skip empty lines and comments
                if word and not word.startswith('#'):
                    bad_words.append(word.lower())
        
        print(f"✓ Loaded {len(bad_words)} bad words from {file_path}")
        return bad_words
    
    except Exception as e:
        print(f"Error reading bad words file: {e}")
        return bad_words


class BadWordFilter:
    """Filter bad words from messages using list-based or ANTLR method"""
    
    def __init__(self, bad_words_list=None, use_antlr=False):
        """
        Initialize the filter
        
        Args:
            bad_words_list: List of bad words to filter
            use_antlr: Whether to use ANTLR for filtering (default: False for file-based loading)
        """
        self.bad_words_list = bad_words_list or [
            "badword1", "badword2", "hate", "spam", "offensive", "inappropriate"
        ]
        # Only use ANTLR if explicitly requested AND ANTLR is available
        # For file-based bad words, use list-based filtering for flexibility
        self.use_antlr = use_antlr and ANTLR_AVAILABLE
    
    def filter_message(self, message):
        """
        Filter bad words from message
        
        Returns:
            tuple: (filtered_message, is_filtered, bad_words_found)
        """
        if not message or not isinstance(message, str):
            return message, False, []
        
        if self.use_antlr:
            return self._filter_with_antlr(message)
        else:
            return self._filter_with_list(message)
    
    def _filter_with_antlr(self, message):
        """Filter message using ANTLR parser"""
        try:
            input_stream = InputStream(message)
            lexer = BadWordsLexer(input_stream)
            tokens = CommonTokenStream(lexer)
            parser = BadWordsParser(tokens)
            
            # Analyze tokens for bad words
            lexer = BadWordsLexer(InputStream(message))
            token = lexer.nextToken()
            bad_words_found = []
            
            while token.type != Token.EOF:
                # Check if token type matches BAD_WORD
                token_type_name = (
                    lexer.symbolicNames[token.type] 
                    if token.type < len(lexer.symbolicNames) 
                    else "UNKNOWN"
                )
                
                if token_type_name == 'BAD_WORD':
                    bad_words_found.append(token.text)
                
                token = lexer.nextToken()
            
            # Filter message
            filtered = message
            for word in bad_words_found:
                filtered = filtered.replace(word, '***')
            
            is_filtered = len(bad_words_found) > 0
            return filtered, is_filtered, bad_words_found
            
        except Exception as e:
            print(f"ANTLR filter error: {e}, falling back to list filter")
            return self._filter_with_list(message)
    
    def _filter_with_list(self, message):
        """Fallback: Filter message using simple list comparison"""
        filtered = message
        bad_words_found = []
        
        for word in self.bad_words_list:
            # Case-insensitive search
            if word.lower() in message.lower():
                # Find and replace all occurrences (case-insensitive)
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                matches = pattern.findall(message)
                bad_words_found.extend(matches)
                filtered = pattern.sub('***', filtered)
        
        is_filtered = len(bad_words_found) > 0
        return filtered, is_filtered, bad_words_found
    
    def add_bad_word(self, word):
        """Add a new bad word to the list"""
        if word.lower() not in [w.lower() for w in self.bad_words_list]:
            self.bad_words_list.append(word)
            return True
        return False
    
    def remove_bad_word(self, word):
        """Remove a bad word from the list"""
        initial_len = len(self.bad_words_list)
        self.bad_words_list = [w for w in self.bad_words_list if w.lower() != word.lower()]
        return len(self.bad_words_list) < initial_len
    
    def get_bad_words(self):
        """Get list of bad words"""
        return self.bad_words_list.copy()
