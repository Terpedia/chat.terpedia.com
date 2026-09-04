# Baked-In API Key Configuration

## Setup Complete

✅ **API Key**: Generated and configured automatically  
✅ **User Experience**: No key input required  
✅ **Terpedia Models**: Use shared key automatically  
✅ **OpenAI Models**: Still require user's key

## How It Works

### Terpedia Models (Automatic Key)
- **terpedia/unified**
- **terpedia/kb**
- **terpedia/pubmed**
- **terpedia/rdkit**

These models automatically use a shared API key configured server-side. Users don't need to enter anything.

### OpenAI Models (User Key Required)
- **gpt-4o**
- **gpt-4o-mini**
- **gpt-4-turbo**
- **gpt-3.5-turbo**

These models still require users to provide their own OpenAI API key.

## Configuration

### librechat.yaml
```yaml
endpoints:
  openAI:
    enabled: true
    title: "Terpedia & OpenAI"
    baseURL: "https://api.terpedia.com/v1"
    apiKey: "<generated-key>"  # Baked-in key
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

### API Endpoint Behavior
- **Terpedia models**: Automatically use `TERPEDIA_API_KEY` from environment
- **OpenAI models**: Require user-provided API key

## User Experience

1. **Visit**: https://chat.terpedia.com
2. **Select Terpedia Model**: Works immediately, no key needed
3. **Select OpenAI Model**: Prompts for user's OpenAI API key

## Security

- API key is stored in configuration files (not exposed to users)
- Terpedia models use shared key automatically
- OpenAI models still require individual user keys
- Key is generated securely using OpenSSL

## Status

✅ **Configuration**: API key baked into librechat.yaml  
✅ **API Endpoint**: Handles shared key for Terpedia models  
✅ **User Experience**: No key input required for Terpedia models  
✅ **Ready**: Users can use Terpedia models without entering keys
