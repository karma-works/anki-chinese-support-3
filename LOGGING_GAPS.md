# What Is NOT Currently Logged

This document lists operations and events that are **not** currently being logged in the application.

## 1. Successful Operations

### Database Operations
- ✅ **Logged**: Database errors, connection failures
- ❌ **NOT Logged**: 
  - Successful database connections
  - Successful database queries
  - Query results (number of rows returned)
  - Database disconnections
  - Index creation success

### Audio Operations
- ✅ **Logged**: Audio download failures
- ❌ **NOT Logged**:
  - Successful audio downloads
  - Audio file paths created
  - Audio cache hits (when file already exists)

### Field Filling Operations
- ✅ **Logged**: Field filling errors, some debug messages
- ❌ **NOT Logged**:
  - Successful field fills (which fields were updated)
  - Number of fields updated per operation
  - Field values before/after updates
  - Which fill functions were called and succeeded

## 2. User Interactions

### Menu Actions
- ❌ **NOT Logged**:
  - Menu item clicks (Phonetics, Speech Engine, Bulk Fill options)
  - Configuration changes via menu
  - Menu loading/unloading

### Button Actions
- ✅ **Logged**: Button setup errors, toggle errors
- ❌ **NOT Logged**:
  - Button toggle state changes
  - When plugin is enabled/disabled for a note type
  - Button click events

### Editor Actions
- ✅ **Logged**: Field focus lost, some debug messages
- ❌ **NOT Logged**:
  - Field focus gained
  - Note type changes
  - Editor state changes (beyond errors)

## 3. Configuration Operations

### Config Changes
- ❌ **NOT Logged**:
  - Configuration updates (target, speech engine changes)
  - Configuration saves
  - Configuration loads
  - First run initialization

### Model Operations
- ❌ **NOT Logged**:
  - Model creation (Chinese Advanced/Basic)
  - Model additions to Anki
  - Template installations

## 4. Data Processing Operations

### Translation Operations
- ❌ **NOT Logged**:
  - Translation requests
  - Translation results (success/failure, language)
  - Dictionary lookups

### Transcription Operations
- ❌ **NOT Logged**:
  - Pinyin transcription operations
  - Bopomofo transcription
  - Jyutping transcription
  - Transcription failures (only exceptions are logged)

### Text Processing
- ❌ **NOT Logged**:
  - Ruby processing
  - Colorization operations
  - Text cleanup operations
  - Hanzi detection operations

### Frequency Operations
- ✅ **Logged**: Frequency fill errors
- ❌ **NOT Logged**:
  - Frequency lookups
  - Frequency values retrieved

## 5. Profile/Collection Operations

### Profile Events
- ✅ **Logged**: Hook errors
- ❌ **NOT Logged**:
  - Profile open events
  - Profile close events
  - Collection connection/disconnection

### Database Initialization
- ❌ **NOT Logged**:
  - First run detection
  - Index creation operations
  - Database schema operations

## 6. Performance Metrics

- ❌ **NOT Logged**:
  - Operation execution times
  - Database query performance
  - Network request latencies
  - Memory usage
  - Function call counts

## 7. Bulk Operations

### Bulk Fill Operations
- ✅ **Logged**: Bulk fill errors in fill.py
- ❌ **NOT Logged**:
  - Bulk fill start/completion
  - Progress updates (number of notes processed)
  - Bulk fill statistics (successful vs failed)
  - Which bulk operation was initiated

## 8. Template Operations

- ❌ **NOT Logged**:
  - Template installation
  - Template rendering
  - CSS injection operations

## 9. Network Operations

### Successful Requests
- ✅ **Logged**: Network request failures
- ❌ **NOT Logged**:
  - Successful HTTP requests
  - Request URLs
  - Response codes (for successful requests)
  - Request/response sizes

## 10. State Changes

- ❌ **NOT Logged**:
  - Plugin enabled/disabled state changes
  - Note type enable/disable
  - Editor state transitions

## 11. Validation Operations

- ❌ **NOT Logged**:
  - Input validation (what was validated, passed/failed)
  - Field format validation
  - Data sanitization operations

## 12. Ruby/Text Processing

- ❌ **NOT Logged**:
  - Ruby tag processing
  - Ruby extraction operations
  - Text colorization operations
  - HTML processing

## Summary

**Currently Logged:**
- ✅ All exceptions (handled and unhandled)
- ✅ Import errors
- ✅ Plugin startup
- ✅ Hook execution errors
- ✅ Audio download failures
- ✅ Database errors
- ✅ Some debug messages in field updates

**NOT Logged:**
- ❌ Successful operations (only failures)
- ❌ User interactions (menu clicks, button toggles)
- ❌ Configuration changes
- ❌ Data processing operations (translation, transcription)
- ❌ Performance metrics
- ❌ Bulk operation progress
- ❌ Network request details (successful ones)
- ❌ State changes
- ❌ Most successful database operations

## Recommendations

To improve debugging, consider adding logging for:
1. **Critical user actions** (menu selections, button toggles)
2. **Successful operations** (to trace execution flow)
3. **Performance metrics** (for slow operation detection)
4. **Configuration changes** (to track settings changes)
5. **Bulk operation progress** (for long-running operations)

