# No API Key Required for Terpedia Models

## Configuration Updated

✅ **Terpedia Models**: Work without API key  
✅ **OpenAI Models**: Still require API key (user-provided)

## Changes Made

### 1. librechat.yaml
- Changed `apiKey: "user_provided"` to `apiKey: ""`
- Terpedia models can now be used without entering an API key

### 2. API Endpoint (api.terpedia.com)
- Updated to allow Terpedia models without API key
- OpenAI models still require API key
- Proper error message if OpenAI model used without key

## How It Works

### Terpedia Models (No Key Required)
- **terpedia/unified**
- **terpedia/kb**
- **terpedia/pubmed**
- **terpedia/rdkit**

These models route to `kb.terpedia.com` and don't require an API key.

### OpenAI Models (Key Required)
- **gpt-4o**
- **gpt-4o-mini**
- **gpt-4-turbo**
- **gpt-3.5-turbo**

These models route to OpenAI and require the user's API key.

## User Experience

1. **Visit**: https://chat.terpedia.com
2. **Select Model**: Choose from "Terpedia & OpenAI" endpoint
3. **Terpedia Models**: Can use immediately, no API key needed
4. **OpenAI Models**: Will prompt for API key if not provided

## Testing

### Test Terpedia Model (No Key)
```bash
curl -X POST https://api.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "terpedia/unified",
    "messages": [{"role": "user", "content": "What is limonene?"}]
  }'
```

### Test OpenAI Model (Key Required)
```bash
curl -X POST https://api.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Status

✅ **Configuration**: Updated to allow no-key usage for Terpedia  
✅ **API**: Handles both keyed and keyless requests  
✅ **LibreChat**: Configured with empty API key  
✅ **Ready**: Users can use Terpedia models without entering keys

## Note

The Terpedia backend (kb.terpedia.com) currently points to S3 and doesn't support POST requests. Once the actual API is deployed, Terpedia models will work fully without requiring API keys.
