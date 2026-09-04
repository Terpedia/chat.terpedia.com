# Endpoint Configuration for kb.terpedia.com

## Current Setup

LibreChat is configured to use `kb.terpedia.com/v1` as the OpenAI-compatible endpoint.

### Configuration Files

**`.env`:**
```bash
OPENAI_API_KEY=user_provided
OPENAI_REVERSE_PROXY=https://kb.terpedia.com/v1
```

**`librechat.yaml`:**
```yaml
version: 1.3.1

endpoints:
  openAI:
    enabled: true
    title: "OpenAI (via KB Terpedia)"
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

## API Key Handling

### Current: User-Provided Keys
- Users enter their own API keys in the LibreChat UI
- Keys are encrypted in the database
- Each user can use their own key

### To Use Shared Key:

1. **Update .env:**
   ```bash
   OPENAI_API_KEY=your-shared-api-key
   ```

2. **Update librechat.yaml:**
   ```yaml
   endpoints:
     openAI:
       apiKey: "${OPENAI_API_KEY}"
   ```

3. **Restart:**
   ```bash
   sudo docker-compose restart api
   ```

## Testing the Endpoint

### From Server:
```bash
# Test models endpoint
curl -k https://kb.terpedia.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test chat completions
curl -k -X POST https://kb.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Troubleshooting

### 404 Errors
- Verify the endpoint path is correct: `/v1/models`, `/v1/chat/completions`
- Check if kb.terpedia.com actually serves an OpenAI-compatible API

### 403 Errors
- Check CloudFront/CDN configuration on kb.terpedia.com
- Verify POST requests are allowed
- Check API key format

### Connection Issues
- Verify DNS resolution: `dig kb.terpedia.com`
- Check firewall rules
- Test from server: `curl -k https://kb.terpedia.com/v1/models`

## Next Steps

1. **Verify Endpoint**: Confirm kb.terpedia.com actually serves OpenAI-compatible API
2. **Test API Key**: Test with a valid API key to ensure authentication works
3. **Configure Models**: If endpoint supports model fetching, set `fetch: true`
4. **Monitor Logs**: Check LibreChat logs for endpoint connection status
