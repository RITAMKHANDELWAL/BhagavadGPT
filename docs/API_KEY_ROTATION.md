# API Key Rotation Feature

## Overview

BhagvadGPT now supports **automatic API key rotation** to handle high traffic and avoid rate limits. The system uses 5 Groq API keys in a smart rotation strategy.

## How It Works

### 1. Round-Robin Rotation
- Keys are rotated in sequence for each request
- Distributes load evenly across all keys
- Prevents any single key from being overused

### 2. Intelligent Failure Handling
- If a key hits rate limit, it's automatically marked as "failed"
- Failed keys are skipped for 60 seconds (cooling period)
- System tries the next available key immediately
- If all keys fail, user gets a friendly "high volume" message

### 3. Automatic Retry
- System tries up to 5 times (one attempt per key)
- Seamlessly switches between keys on failure
- Users don't experience interruptions

## Key Statistics

### Check Key Status
Visit: `http://localhost:8000/api/key-stats`

This endpoint shows:
- Total number of keys
- Current key being used
- Usage count per key
- Failure count per key
- Status (available/cooling_down)

### Example Response
```json
{
  "total_keys": 5,
  "current_key_index": 3,
  "keys": [
    {
      "key_number": 1,
      "masked_key": "gsk_DwCCD8...s5lt",
      "total_uses": 45,
      "total_failures": 2,
      "last_failure_seconds_ago": 120,
      "status": "available"
    },
    ...
  ]
}
```

## Benefits

✅ **Higher Availability** - 5x the rate limit capacity
✅ **Better User Experience** - Fewer "high volume" errors
✅ **Automatic Failover** - Seamless key switching
✅ **Load Distribution** - Even usage across all keys
✅ **Self-Healing** - Failed keys automatically recover after 60s

## Configuration

The API keys are configured in `main.py`:

```python
GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY1"),
    os.getenv("GROQ_API_KEY2"),
    os.getenv("GROQ_API_KEY3"),
    os.getenv("GROQ_API_KEY4"),
    os.getenv("GROQ_API_KEY5"),
]
```

All keys are loaded from environment variables in the `.env` file for security.

## Monitoring

Watch the backend logs to see key rotation in action:

```
🔑 Using API key #1 (Used 12 times)
✅ Successfully got response using key #1

🔑 Using API key #2 (Used 8 times)
⚠️ Rate limit hit on key #2
🔄 Retrying with next API key... (Attempt 2/5)

🔑 Using API key #3 (Used 15 times)
✅ Successfully got response using key #3
```

## Testing

1. Start the backend:
   ```bash
   cd bhagvadgpt-backend
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Check key stats:
   ```bash
   curl http://localhost:8000/api/key-stats
   ```

3. Send multiple requests and watch the rotation in logs

## Security Note

⚠️ API keys are currently hardcoded in `main.py`. For production deployment:
- Move all keys to environment variables
- Use a secrets management service (AWS Secrets Manager, Azure Key Vault, etc.)
- Never commit actual API keys to Git

---

**Radhe Radhe! 🙏**

Your BhagvadGPT can now handle 5x more traffic!
