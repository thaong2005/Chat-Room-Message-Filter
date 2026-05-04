import sys
import os
import subprocess
from pathlib import Path
from antlr4 import *


# Define your variables
DIR = os.path.dirname(os.path.abspath(__file__))
ANTLR_JAR = 'C:/antlr/antlr4-4.9.2-complete.jar'
GRAMMAR_DIR = DIR
COMPILED_DIR = os.path.join(DIR, 'CompiledFiles')
GRAMMAR_FILE = os.path.join(DIR, 'BadWords.g4')


def print_usage():
    print('Usage:')
    print('  python run.py gen      - Generate ANTLR code from BadWords.g4')
    print('  python run.py test     - Test the generated ANTLR parser')
    print('  python run.py clean    - Remove generated files')


def print_break():
    print('-----------------------------------------------')


def generate_antlr():
    """Generate Python3 code from ANTLR grammar"""
    print('Generating ANTLR code...')
    
    # Create compiled files directory if it doesn't exist
    os.makedirs(COMPILED_DIR, exist_ok=True)
    
    # Run ANTLR
    try:
        subprocess.run([
            'java', '-jar', ANTLR_JAR,
            '-o', COMPILED_DIR,
            '-no-listener',
            '-Dlanguage=Python3',
            GRAMMAR_FILE
        ], check=True)
        print('✓ ANTLR code generated successfully')
        print(f'  Location: {COMPILED_DIR}')
    except subprocess.CalledProcessError as e:
        print(f'✗ Error generating ANTLR code: {e}')
        return False
    except FileNotFoundError:
        print(f'✗ Error: ANTLR JAR not found at {ANTLR_JAR}')
        print('  Please download ANTLR from: https://www.antlr.org/download/antlr-4.9.2-complete.jar')
        return False
    
    return True


def test_antlr():
    """Test the ANTLR parser with sample messages"""
    print('Testing ANTLR parser...')
    print_break()
    
    try:
        sys.path.insert(0, COMPILED_DIR)
        from BadWordsLexer import BadWordsLexer
        from BadWordsParser import BadWordsParser
    except ImportError as e:
        print(f'✗ Error: Could not import ANTLR generated files')
        print(f'  {e}')
        print('  Please run: python run.py gen')
        return False
    
    # Test messages
    test_messages = [
        "Hello world this is a normal message",
        "This message contains badword1 and should be filtered",
        "I hate spam in my inbox",
        "Normal text with some offensive language here",
        "Good morning everyone"
    ]
    
    print('Testing messages:\n')
    
    for message in test_messages:
        print(f'Input: "{message}"')
        
        # Tokenize and analyze
        input_stream = InputStream(message)
        lexer = BadWordsLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = BadWordsParser(tokens)
        tree = parser.program()
        
        # Find bad words
        bad_words = []
        for i in range(tree.getChildCount()):
            child = tree.getChild(i)
            if hasattr(child, 'getChildCount'):
                for j in range(child.getChildCount()):
                    subchild = child.getChild(j)
                    if hasattr(subchild, 'BAD_WORD'):
                        bad_words.append(subchild.getText())
        
        # Alternative: check tokens directly
        lexer = BadWordsLexer(InputStream(message))
        token = lexer.nextToken()
        bad_words = []
        while token.type != Token.EOF:
            token_type_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN"
            if token_type_name == 'BAD_WORD':
                bad_words.append(token.text)
            token = lexer.nextToken()
        
        if bad_words:
            print(f'  ✗ Bad words found: {", ".join(bad_words)}')
            print(f'  → Filtered: "{message}"')
            # Show filtering
            filtered = message
            for word in bad_words:
                filtered = filtered.replace(word, '***')
            print(f'  → Result: "{filtered}"')
        else:
            print(f'  ✓ No bad words found')
        
        print()
    
    print_break()
    print('Test completed successfully')


def clean_generated():
    """Remove generated ANTLR files"""
    print('Cleaning generated files...')
    
    import shutil
    if os.path.exists(COMPILED_DIR):
        shutil.rmtree(COMPILED_DIR)
        print(f'✓ Removed {COMPILED_DIR}')
    else:
        print('✗ No generated files found')


def main(argv):
    print('Chat Room Message Filter - ANTLR Integration')
    print(f'ANTLR JAR: {ANTLR_JAR}')
    print(f'Grammar: {GRAMMAR_FILE}')
    print_break()
    
    if len(argv) < 1:
        print_usage()
    elif argv[0] == 'gen':
        generate_antlr()
    elif argv[0] == 'test':
        if not os.path.exists(COMPILED_DIR):
            print('Generated files not found. Running generation first...')
            print_break()
            if generate_antlr():
                print_break()
                test_antlr()
        else:
            test_antlr()
    elif argv[0] == 'clean':
        clean_generated()
    else:
        print_usage()


if __name__ == '__main__':
    main(sys.argv[1:])
