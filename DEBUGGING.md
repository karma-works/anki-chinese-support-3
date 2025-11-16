# Debugging Guide for Anki Chinese Support 3

## 1. Using Log Files

### Primary Log File
- **Location**: `chinese/anki-chinese-support.log`
- **Contains**: All INFO, WARNING, ERROR, CRITICAL, and DEBUG messages
- **Format**: Timestamp, log level, module name, message, and stack traces

### Fallback Log File (for import errors)
- **Location**: `chinese/anki-chinese-support-import-error.log`
- **Contains**: Errors that occur before the main logger is initialized

### Viewing Logs
```bash
# View entire log file
cat chinese/anki-chinese-support.log

# View last 50 lines
tail -n 50 chinese/anki-chinese-support.log

# Follow log in real-time (Linux/Mac)
tail -f chinese/anki-chinese-support.log

# Search for errors
grep -i error chinese/anki-chinese-support.log

# Search for specific function
grep "update_fields" chinese/anki-chinese-support.log
```

## 2. Log Levels

The logger supports these levels (from most to least verbose):
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (something went wrong)
- **CRITICAL**: Critical errors (severe problems)

Currently, all levels are logged to the file.

## 3. Adding Debug Logging

### In Your Code
```python
from .log import log

# Debug message (most verbose)
log.debug("Processing field: %s", field_name)

# Info message (general information)
log.info("Plugin was started successfully")

# Warning (non-critical issue)
log.warning("Audio download failed, but continuing")

# Error (something went wrong)
log.error("Failed to connect to database")

# Exception with full traceback
try:
    risky_operation()
except Exception as e:
    log.exception("Error in risky_operation")  # Automatically includes traceback
```

### Using the Decorator
```python
from .log import log_exceptions

@log_exceptions
def my_function():
    # Any exception here will be automatically logged
    pass
```

## 4. Common Debugging Scenarios

### Debugging Note Creation Issues
1. Check `onFocusLost` debug messages in the log
2. Look for "Error in update_fields" entries
3. Check which field is being processed
4. Look for exceptions in specific fill functions

### Debugging Import Errors
1. Check `anki-chinese-support-import-error.log` first
2. Look for "Failed to import" messages
3. Check which module is missing
4. Verify Anki version compatibility

### Debugging Audio Download Issues
1. Search for "Could not download audio" in logs
2. Check which service (gTTS, Baidu, AWS) is failing
3. Look for network-related errors
4. Check INFO level messages (not errors, since TTS can be unreliable)

### Debugging Hook Execution
1. All hooks are wrapped with `wrap_hook()` - exceptions are logged automatically
2. Look for "Exception in hook" messages
3. Check the function name in the log entry

## 5. Python Debugger (pdb)

### Adding Breakpoints
```python
import pdb; pdb.set_trace()  # Python 3.7+
# or
breakpoint()  # Python 3.7+

# Example:
def update_fields(note, focus_field, fields):
    breakpoint()  # Execution will pause here
    # ... rest of code
```

### Using pdb Commands
- `n` (next): Execute next line
- `s` (step): Step into function
- `c` (continue): Continue execution
- `p variable`: Print variable value
- `pp variable`: Pretty print variable
- `l` (list): Show current code
- `q` (quit): Quit debugger

**Note**: pdb requires Anki to be run from terminal, not GUI.

## 6. Tracing Execution Flow

### Enable Function Tracing
Add this to see function entry/exit:
```python
from .log import log

def my_function():
    log.debug("Entering my_function")
    try:
        # ... your code
        log.debug("Exiting my_function successfully")
    except Exception as e:
        log.debug("Exiting my_function with error: %s", e)
        raise
```

### Trace Hook Calls
All hooks are automatically logged. Check logs for:
- "onFocusLost called"
- "Processing field: ..."
- "Fields updated successfully"

## 7. Debugging Tips

### 1. Clear Log File
```bash
# Clear log to start fresh
> chinese/anki-chinese-support.log
```

### 2. Add Temporary Debug Code
```python
# Temporary debug - remove after debugging
log.debug("=== DEBUG: Variable value: %r ===", variable)
```

### 3. Check Log File Size
Large log files can slow down logging:
```bash
# Check file size
ls -lh chinese/anki-chinese-support.log

# If too large, archive and clear
mv chinese/anki-chinese-support.log chinese/anki-chinese-support.log.old
```

### 4. Enable More Verbose Logging
The logger is already set to DEBUG level. To add more detail:
```python
log.debug("Function called with args: %r, kwargs: %r", args, kwargs)
```

### 5. Test Specific Scenarios
1. Reproduce the issue
2. Check log file immediately after
3. Look for the most recent entries
4. Trace back through the execution flow

## 8. Debugging in Anki

### Running Anki from Terminal
```bash
# Linux/Mac
anki

# Windows
anki.exe

# With debug output
anki 2>&1 | tee anki-output.log
```

### Anki Console
- Press `Ctrl+Shift+;` (or `Cmd+Shift+;` on Mac) in Anki to open Python console
- Useful for quick testing:
```python
# In Anki console
from chinese.log import log
log.debug("Test message")

# Check if plugin loaded
from chinese.main import config
print(config)
```

## 9. Common Issues and Solutions

### Issue: No log entries appearing
- **Check**: File permissions on log directory
- **Check**: Log file path is correct
- **Check**: Plugin actually loaded (look for "Plugin was started successfully")

### Issue: Too many log entries
- **Solution**: Filter logs by level or function name
- **Solution**: Archive old logs periodically

### Issue: Can't find the error
- **Solution**: Clear log, reproduce issue, check immediately
- **Solution**: Search for "ERROR" or "CRITICAL" in logs
- **Solution**: Check both log files (main and import-error)

## 10. Performance Debugging

### Timing Operations
```python
import time
from .log import log

start = time.time()
# ... your code ...
elapsed = time.time() - start
log.debug("Operation took %.3f seconds", elapsed)
```

### Memory Debugging
```python
import sys
from .log import log

log.debug("Memory usage: %d bytes", sys.getsizeof(variable))
```

## 11. Getting Help

When reporting issues, include:
1. Relevant log entries (last 50-100 lines)
2. Steps to reproduce
3. Anki version
4. Python version (if known)
5. Operating system

