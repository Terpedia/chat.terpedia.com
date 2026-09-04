# Models Visibility Fix Applied

## Issue
Terpedia models configured in `librechat.yaml` but not visible in UI.

## Root Cause
Conflict between `.env` file settings and `librechat.yaml`:
- `.env` had `OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1`
- `librechat.yaml` had `baseURL: "https://api.terpedia.com/v1"`
- `.env` had old model list without Terpedia models

## Fix Applied

### 1. Updated .env File
```bash
OPENAI_REVERSE_PROXY=https://api.terpedia.com/v1
OPENAI_MODELS=terpedia/unified,terpedia/kb,terpedia/pubmed,terpedia/rdkit,gpt-4o,gpt-4o-mini,gpt-4-turbo,gpt-3.5-turbo
```

### 2. Verified librechat.yaml
```yaml
endpoints:
  openAI:
    enabled: true
    title: "Terpedia & OpenAI"
    baseURL: "https://api.terpedia.com/v1"
    apiKey: "user_provided"
    models:
      default:
        - "terpedia/unified"
        - "terpedia/kb"
        - "terpedia/pubmed"
        - "terpedia/rdkit"
        - "gpt-4o"
        - "gpt-4o-mini"
        - "gpt-4-turbo"
        - "gpt-3.5-turbo"
      fetch: false
```

### 3. Restarted LibreChat
Services restarted to load new configuration.

## Next Steps for User

1. **Clear Browser Cache** (Critical):
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Clear data

2. **Or Use Incognito/Private Window**:
   - Chrome: `Ctrl+Shift+N` (Windows) or `Cmd+Shift+N` (Mac)
   - Visit https://chat.terpedia.com

3. **Hard Refresh**:
   - `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

4. **Check Model Selector**:
   - Look for "Terpedia & OpenAI" endpoint
   - Should see 8 models (4 Terpedia + 4 OpenAI)

## Verification

After clearing cache, models should appear:
- terpedia/unified
- terpedia/kb
- terpedia/pubmed
- terpedia/rdkit
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

## Status

✅ Configuration fixed
✅ Services restarted
⏳ User needs to clear browser cache to see models
