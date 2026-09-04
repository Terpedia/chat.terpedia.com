# API Key Configuration for chat.terpedia.com

## Current Configuration

LibreChat is configured to use `kb.terpedia.com` as the OpenAI endpoint. There are several ways to handle API keys:

## Option 1: User-Provided Keys (Current Setup) ✅

**Current Configuration:**
- `.env`: `OPENAI_API_KEY=user_provided`
- `librechat.yaml`: `apiKey: "user_provided"`

**How it works:**
- Users enter their own API keys in the LibreChat UI
- Each user can use their own key
- Keys are stored encrypted in the database

**Pros:**
- Users can use their own keys
- No shared key management needed
- More secure (keys not stored in config)

**Cons:**
- Users need to provide their own keys
- Requires users to have valid keys for kb.terpedia.com

## Option 2: Shared API Key

If you want all users to use the same API key:

### Update .env:
```bash
OPENAI_API_KEY=your-shared-api-key-here
```

### Update librechat.yaml:
```yaml
endpoints:
  openAI:
    apiKey: "${OPENAI_API_KEY}"  # Uses value from .env
    # OR
    apiKey: "your-shared-api-key-here"  # Hardcoded (less secure)
```

**Pros:**
- No user action required
- Single key to manage

**Cons:**
- All users share the same key
- Key stored in configuration files
- Less secure if key is compromised

## Option 3: Environment Variable (Recommended for Shared Key)

Use environment variable for flexibility:

### In .env:
```bash
OPENAI_API_KEY=your-shared-api-key-here
```

### In librechat.yaml:
```yaml
endpoints:
  openAI:
    apiKey: "${OPENAI_API_KEY}"
```

**Pros:**
- Key stored in .env (not in YAML)
- Easy to change without editing YAML
- Can use different keys per environment

## Option 4: No API Key (If kb.terpedia.com Doesn't Require It)

If kb.terpedia.com doesn't require API key authentication:

### In librechat.yaml:
```yaml
endpoints:
  openAI:
    apiKey: ""  # Empty string
    # OR omit the apiKey field entirely
```

## Current Setup Details

### .env Configuration:
```bash
OPENAI_API_KEY=user_provided
OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1
```

### librechat.yaml Configuration:
```yaml
version: 1.3.1

endpoints:
  openAI:
    enabled: true
    title: "OpenAI"
    baseURL: "https://kb.terpedia.com/v1"
    apiKey: "user_provided"
    models:
      default:
        - "gpt-4o"
        - "gpt-4o-mini"
        - "gpt-4-turbo"
        - "gpt-3.5-turbo"
      fetch: false
```

## How Users Enter API Keys

With `user_provided` configuration:

1. User logs into LibreChat
2. Goes to Settings → Endpoints
3. Selects "OpenAI" endpoint
4. Enters their API key
5. Key is encrypted and stored in database

## Testing API Key Configuration

### Test from server:
```bash
# Test with a key
curl -k -X POST https://kb.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"test"}]}'
```

### Check LibreChat logs:
```bash
sudo docker logs LibreChat | grep -i "api.*key\|authentication\|401\|403"
```

## Recommendations

**For Production:**
- Use **Option 1 (user_provided)** if users have their own keys
- Use **Option 3 (environment variable)** if using a shared key
- Never hardcode keys in librechat.yaml

**For Testing:**
- Can temporarily use a shared key in .env
- Switch back to `user_provided` for production

## Changing Configuration

### To switch to shared key:

1. **Update .env:**
   ```bash
   OPENAI_API_KEY=your-actual-api-key
   ```

2. **Update librechat.yaml:**
   ```yaml
   apiKey: "${OPENAI_API_KEY}"
   ```

3. **Restart LibreChat:**
   ```bash
   sudo docker-compose restart api
   ```

### To keep user-provided keys:

Keep current configuration:
- `.env`: `OPENAI_API_KEY=user_provided`
- `librechat.yaml`: `apiKey: "user_provided"`

## Security Notes

- ✅ Keys are encrypted in the database when using `user_provided`
- ⚠️  Shared keys in .env should have restricted file permissions: `chmod 600 .env`
- ⚠️  Never commit .env or librechat.yaml with real keys to git
- ✅ Use environment variables for production deployments

## Troubleshooting

### Users can't connect:
1. Verify kb.terpedia.com endpoint is accessible
2. Check if API key format is correct
3. Verify endpoint accepts the key format

### 401/403 Errors:
- API key might be invalid
- Endpoint might require different authentication
- Check kb.terpedia.com documentation for key format

### 404 Errors:
- Endpoint URL might be incorrect
- Check if `/v1` path is correct for kb.terpedia.com
