# 🔍 InfraNest PRISM - Debug Trace Log

**Last Updated**: Auto-generated timestamp placeholder

---

## 📋 API Endpoint Checklist

### 1. `/api/v1/parse-prompt` - DSL Generation
- **Status**: ✅ Enhanced with DEBUG logging
- **Input Logged**: Prompt preview (200 chars), length, LLM config (temp/max_tokens/top_p), context presence
- **Output Logged**: DSL project name, model count, DSL size (bytes), keys list
- **Error Logged**: Exception type, message, full context
- **Fallback Behavior**: None (raises error if fails)

### 2. `/api/v1/generate-followup-questions` - Question Generation  
- **Status**: ✅ Enhanced with DEBUG logging
- **Input Logged**: User answers keys, answer count, requested question count, sample answers (300 chars)
- **Output Logged**: Questions array, question count, provider type (Groq/fallback)
- **Error Logged**: Exception type, message, LLM failure details
- **Fallback Behavior**: ⚠️ Returns hardcoded questions (marked with `is_fallback: true`)

### 3. `/api/v1/generate-code` - Code Generation
- **Status**: ✅ Enhanced with DEBUG logging
- **Input Logged**: Framework, DSL size, project name, model count, DSL preview (300 chars)
- **Output Logged**: File count, file list (first 10), framework, total code size, provider type
- **Error Logged**: Exception type, message, framework validation errors, DSL validation errors
- **Fallback Behavior**: Uses template-based generation (no LLM)

### 4. `/api/v1/health` - Health Check
- **Status**: ✅ Functional (no LLM dependency)
- **Returns**: System status, PRISM pipeline availability

---

## 📊 Logs to Review

### Backend Console (Flask DEBUG mode)
1. **Enable DEBUG logging**: Set `FLASK_ENV=development` or `LOG_LEVEL=DEBUG`
2. **Look for**:
   - Lines starting with `🔍 [API TRACE]` - Full input/output traces
   - Lines starting with `⚠️  [API TRACE]` - Fallback mode activations
   - Lines starting with `❌ [API TRACE]` - Error details
   - `="*80` separators - Section boundaries

### Frontend Console (Browser DevTools)
1. **Enable dev mode**: `npm run dev` (not build)
2. **Look for**:
   - `🔁 Follow-up API:` - Raw API response from question generation
   - `🔨 Code Gen API:` - Raw API response from code generation
   - Network tab → Fetch/XHR → Response payload

### Test Script Output
1. **Run**: `python infranest/core/test_api_debug.py`
2. **Check**:
   - ✅ All 3 tests pass (health, followup, code generation)
   - 📊 Status codes (should be 200)
   - 🎯 Provider field (should be 'groq', not 'default' or 'fallback')
   - ⚠️ `is_fallback` flag (should be `false` for real LLM responses)

---

## 🎛️ LLM Configuration Flags

### Current Settings (from UI sliders)
- **Temperature**: 0.7 (default) - Controls creativity
- **Max Tokens**: 4096 (default) - Max response length
- **Top P**: 0.9 (default) - Nucleus sampling threshold

### How to Verify in Logs
Search backend logs for:
```
🎛️ LLM Config: temp=X.X, max_tokens=XXXX, top_p=X.X
```

---

## 🚨 Known Issues & Resolutions

### Issue 1: Silent Fallback to Templates
- **Symptom**: `provider: 'fallback'` or `is_fallback: true` in response
- **Root Cause**: LLM API failure (network, rate limit, auth)
- **Fix**: Check Groq API key in `.env`, verify network connectivity
- **Status**: ⏳ Pending - Need to disable silent fallbacks (raise errors instead)

### Issue 2: Frontend Shows Mock/Stale Data
- **Symptom**: Same questions every time, no variation
- **Root Cause**: Browser cache or using hardcoded fallback
- **Fix**: Clear browser cache, check Network tab for actual API calls
- **Status**: ✅ Resolved - Cache-busting enabled via Vite config

### Issue 3: Missing DEBUG Logs
- **Symptom**: No `[API TRACE]` lines in backend console
- **Root Cause**: Log level set to INFO/WARNING instead of DEBUG
- **Fix**: Set environment variable `LOG_LEVEL=DEBUG` or edit `app_clean.py` logger config
- **Status**: ✅ Resolved - DEBUG logging active on all 3 endpoints

---

## ✅ Success Criteria

- [x] All AI-dependent actions log: **Input**, **Output**, **Errors**
- [ ] `test_api_debug.py` passes all 3 routes (health, followup, code gen)
- [ ] Frontend console shows real API response, not mock fallback
- [ ] No more silent API failures or ghost logic (pending: disable silent fallbacks)
- [x] Backend logs show `🔍 [API TRACE]` sections with minified content
- [ ] `provider` field never shows 'default' or 'fallback' in production (pending: error raising)

---

## 📝 Manual Test Steps

1. **Start Backend**: 
   ```bash
   cd infranest/core
   python server.py
   ```

2. **Run Test Script**:
   ```bash
   python test_api_debug.py
   ```

3. **Check Backend Logs**:
   - Look for DEBUG traces with 80-char separators
   - Verify Input/Output/Error sections present
   - Confirm no silent exceptions

4. **Test via Frontend**:
   ```bash
   cd infranest
   npm run dev
   ```
   - Open browser DevTools → Console
   - Enter a prompt, submit
   - Check for `🔁 Follow-up API:` logs
   - Verify `is_fallback: false` in response

---

## 🔧 Debugging Toolkit Checklist

- [x] **API Trace Logging** - All 3 endpoints log I/O/E
- [x] **Test Script** - `test_api_debug.py` created with 3 functions
- [x] **Debug Log** - This markdown file
- [ ] **Frontend Console Logging** - Pending (dev mode only)
- [ ] **Disable Silent Fallbacks** - Pending (raise errors in `simple_ai_manager.py`)
- [ ] **Final Verification** - Pending (run all tests, confirm no ghost logic)

---

**Next Steps**:
1. Add frontend console.log for dev mode
2. Disable silent fallbacks in `simple_ai_manager.py`
3. Run full test suite to verify success criteria
4. Update this file with actual test timestamps
