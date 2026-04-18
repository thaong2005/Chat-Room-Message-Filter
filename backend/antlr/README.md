# ANTLR Integration for Chat Room Message Filter

This directory contains ANTLR grammar and tools for filtering bad words in chat messages.

## Overview

The ANTLR integration provides a robust, grammar-based approach to detecting and filtering invalid words in messages. It uses a formal grammar definition (`BadWords.g4`) to parse and identify bad words, with an automatic fallback to list-based filtering if ANTLR is unavailable.

## Files

- **`BadWords.g4`** - ANTLR 4 grammar file defining the bad words and message structure
- **`run.py`** - Python script to generate, test, and manage ANTLR code
- **`CompiledFiles/`** - Generated lexer and parser files (created by run.py)

## Prerequisites

Before using ANTLR integration, install:

1. **Java Runtime** (for ANTLR)
```bash
# Windows
choco install java  # or download from java.com

# Mac
brew install openjdk
```

2. **ANTLR4 JAR** (download or install)
```bash
# Option 1: Automatic download
cd backend/antlr
wget https://www.antlr.org/download/antlr-4.9.2-complete.jar

# Option 2: Manual download
# Download from: https://www.antlr.org/download/antlr-4.9.2-complete.jar
# Place in: C:/antlr/antlr4-4.9.2-complete.jar
```

3. **Python ANTLR4 Runtime**
```bash
pip install antlr4-python3-runtime
```

## Setup & Usage

### 1. Generate ANTLR Code

From the `backend/antlr/` directory:

```bash
python run.py gen
```

This will:
- Parse `BadWords.g4`
- Generate `BadWordsLexer.py` and `BadWordsParser.py`
- Create `CompiledFiles/` directory with generated code

**Output:**
```
Generating ANTLR code...
✓ ANTLR code generated successfully
  Location: CompiledFiles
```

### 2. Test the Filter

```bash
python run.py test
```

This will test the parser with sample messages and show:
- Input messages
- Detected bad words
- Filtered output

**Sample Output:**
```
Input: "This message contains badword1 and should be filtered"
  ✗ Bad words found: badword1
  → Filtered: "This message contains *** and should be filtered"
```

### 3. Clean Generated Files

```bash
python run.py clean
```

## Grammar Definition

The `BadWords.g4` file defines:

```antlr
// Lexer rule for bad words
BAD_WORD: ('badword1' | 'badword2' | 'hate' | 'spam' | ...);

// Normal words (anything else)
NORMAL_WORD: [a-zA-Z0-9_@.!?,;:\-\'\"]+ | [^\s\p{White_Space}]+;
```

**To add new bad words:**

Edit `BadWords.g4` and add to the `BAD_WORD` rule:

```antlr
BAD_WORD
    : ('badword1' | 'badword2' | 'hate' | 'spam' | 'newbadword')
    ;
```

Then regenerate:
```bash
python run.py gen
```

## Integration with Backend

The backend uses the `BadWordFilter` class from `backend/bad_word_filter.py`:

```python
from bad_word_filter import BadWordFilter

# Initialize filter
filter = BadWordFilter(bad_words_list=["badword1", "badword2", "hate", "spam"])

# Filter a message
filtered_text, is_filtered, bad_words_found = filter.filter_message("your message here")

# If ANTLR is available: uses ANTLR parser
# If ANTLR is unavailable: automatically falls back to list-based filtering
```

### Features

- ✅ ANTLR grammar-based detection
- ✅ Automatic fallback to list-based filtering
- ✅ Case-insensitive matching
- ✅ Multiple bad word detection
- ✅ Dynamic bad word management (add/remove)
- ✅ Integration with FastAPI backend
- ✅ WebSocket message filtering
- ✅ REST API message filtering

## Troubleshooting

### Issue: "ANTLR JAR not found"

**Solution:** Download ANTLR4 and place it in the correct location:
```bash
# Windows example
C:/antlr/antlr4-4.9.2-complete.jar
```

Update the path in `run.py` if needed:
```python
ANTLR_JAR = 'C:/antlr/antlr4-4.9.2-complete.jar'  # Adjust path
```

### Issue: "Could not import ANTLR generated files"

**Solution:** Generate the code first:
```bash
python run.py gen
```

### Issue: "antlr4 module not found"

**Solution:** Install Python ANTLR runtime:
```bash
pip install antlr4-python3-runtime
```

### ANTLR Unavailable - Using Fallback

If ANTLR is not installed, the system automatically falls back to list-based filtering. This is fully functional but lacks the advanced grammar-based detection benefits.

**To enable ANTLR:**
1. Install Java
2. Download ANTLR4 JAR
3. Install `antlr4-python3-runtime`
4. Run `python run.py gen`

## Performance Considerations

- **ANTLR-based:** More robust for complex patterns, slight overhead from parsing
- **List-based (fallback):** Faster for simple word lists, no parsing overhead
- **Recommendation:** Use ANTLR for production; fallback is automatic if unavailable

## Future Enhancements

- [ ] Support for regex patterns in grammar
- [ ] Multi-language support
- [ ] Context-aware filtering
- [ ] Machine learning-based detection
- [ ] Custom grammar rules per room
- [ ] Filter statistics and reporting
- [ ] Whitelist support

## References

- [ANTLR Official Website](https://www.antlr.org/)
- [ANTLR4 Python Target](https://github.com/antlr/antlr4/tree/master/runtime/Python3)
- [ANTLR Grammar Guide](https://github.com/antlr/grammars-v4)
