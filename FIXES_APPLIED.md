# Fixes Applied

## ✅ Fixed: 405 Method Not Allowed Error

**Problem**: `kb.terpedia.com` is an S3 bucket that doesn't support POST requests, causing 405 errors.

**Solution**:
1. Deployed API backend to GCE instance (`chat-server`) on port 8010
2. Created firewall rule to allow traffic on port 8010
3. Updated `api.terpedia.com` proxy to point to `http://104.197.255.123:8010`
4. Set `TERPEDIA_BACKEND_URL` environment variable in Vercel

**Status**: ✅ API deployed and running

## ⚠️ In Progress: Model Identification (AI says "OpenAI")

**Problem**: When users ask "who are you", the AI responds that it's OpenAI instead of Terpedia.

**Root Cause**: 
- The RAG module uses OpenAI models via OpenRouter
- Those models identify as OpenAI in their response content
- The `model` field in API responses is correct (`terpedia/unified`), but the content mentions OpenAI

**Solution Needed**:
1. Add system prompt: "You are Terpedia, a scientific assistant for terpene research..."
2. Or post-process responses to replace "OpenAI" with "Terpedia" in content
3. Update RAG module system prompts to identify as Terpedia

**Current Status**: RAG is disabled (dependencies missing), so this primarily affects:
- Future RAG responses when enabled
- Any responses that mention the model's identity

## Configuration

### API Backend
- **URL**: `http://104.197.255.123:8010`
- **Status**: Running (RAG disabled, SPARQL enabled)
- **Firewall**: Port 8010 open

### Proxy
- **URL**: `https://api.terpedia.com`
- **Backend**: Points to GCE instance
- **Status**: Deployed

## Next Steps

1. ✅ Fix 405 error - DONE
2. ⏳ Fix model identification in responses
3. ⏳ Test complete flow end-to-end
4. ⏳ Enable RAG when dependencies are available
