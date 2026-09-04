# API Deployment Status

## Issues Fixed

### 1. 405 Method Not Allowed Error ✅
- **Problem**: `kb.terpedia.com` is an S3 bucket that doesn't support POST requests
- **Solution**: Deployed API backend to GCE instance on port 8010
- **Status**: API running on `http://104.197.255.123:8010`

### 2. Model Identification (AI says "OpenAI") ⚠️
- **Problem**: When users ask "who are you", the AI responds that it's OpenAI
- **Root Cause**: The RAG module uses OpenAI models via OpenRouter, and those models identify as OpenAI in their responses
- **Solution Needed**: 
  - Add system prompt: "You are Terpedia, a scientific assistant..."
  - Or post-process responses to replace "OpenAI" with "Terpedia"
  - The model field in API responses is correct (`terpedia/unified`), but the content mentions OpenAI

## Current Configuration

### API Backend
- **Location**: GCE instance `chat-server` (104.197.255.123:8010)
- **Status**: Running (RAG disabled, SPARQL enabled)
- **Firewall**: Port 8010 open

### Proxy (api.terpedia.com)
- **Backend URL**: `http://104.197.255.123:8010`
- **Environment Variable**: `TERPEDIA_BACKEND_URL` set in Vercel
- **Status**: Deployed, but needs testing

## Next Steps

1. ✅ API deployed to GCE
2. ✅ Firewall rule created
3. ✅ Proxy updated
4. ⏳ Test complete flow
5. ⏳ Fix model identification in responses

## Testing

```bash
# Test direct API
curl -X POST http://104.197.255.123:8010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 76cc8c79f4925a7949538fd9371298dd6c74a71dfaea47f508429ee2f7f4b1a6" \
  -d '{"model":"terpedia/kb","messages":[{"role":"user","content":"SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"}]}'

# Test via proxy
curl -X POST https://api.terpedia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 76cc8c79f4925a7949538fd9371298dd6c74a71dfaea47f508429ee2f7f4b1a6" \
  -d '{"model":"terpedia/kb","messages":[{"role":"user","content":"test"}]}'
```
