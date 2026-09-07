# Moonwork: Raw Gemini API Calls

Phase 1 is a small CLI for learning what an LLM API call actually is. We are
using the Gemini Developer API because it has a free tier for learning. The
code should use raw `requests` or `httpx` calls only: no Gemini SDK, LangChain,
LlamaIndex, or agent framework.

## Setup

1. Create a Gemini API key in Google AI Studio.
2. Export it in the shell without putting it in source control:

	 ```bash
	 export GEMINI_API_KEY="your-key-here"
	 ```

3. Install the one HTTP dependency you choose:

	 ```bash
	 python -m pip install requests
	 ```

## Build order

Implement one checkpoint at a time in `main.py`.

### 1. One raw request

Hardcode one prompt and send:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=YOUR_KEY
Content-Type: application/json
```

The first request body should look like this:

```json
{
	"contents": [
		{
			"role": "user",
			"parts": [{"text": "Explain what an HTTP request is in two sentences."}]
		}
	],
	"generationConfig": {
		"maxOutputTokens": 200,
		"temperature": 0.2
	}
}
```

Print the complete JSON response first. Before extracting any text, identify
the request URL, headers, `contents`, `parts`, and generation settings. Then
find the response text under `candidates[0].content.parts[0].text`.

Gemini names the conversation input `contents` rather than Anthropic's
`messages`. The idea is the same: the model receives structured JSON, not a
magic string.

### 2. Wrap the call

Create `ask(prompt: str) -> str`, read a prompt from `input()` or `sys.argv`,
and return only the extracted text.

### 3. Add history

Keep a `contents` list. For each turn, append the user's content and the
model's returned content, then send the complete list again. Gemini uses
`role: "user"` and `role: "model"` for these turns. Print the list length on
each request so the growing context is visible.

### 4. Add useful context

Accept either a local file path or a URL, obtain its text, and include that
text in a user prompt asking for a summary or explanation. Do not add a vector
database or retrieval framework yet.

### 5. Polish

Add handling for missing keys, empty input, network errors, non-2xx responses,
malformed responses, `--help`, and optionally persisted history.

## Gemini field translation

| Concept | Gemini REST API |
| --- | --- |
| API key | `GEMINI_API_KEY`, sent as the `key` query parameter |
| Input history | `contents` |
| User turn | `role: "user"` |
| Assistant turn | `role: "model"` |
| Text | `parts: [{"text": "..."}]` |
| Output limit | `generationConfig.maxOutputTokens` |
| Randomness | `generationConfig.temperature` |
| Returned text | `candidates[0].content.parts[0].text` |

The API is stateless between requests. History only exists because the client
resends it. A context window is the model's finite limit for the combined
conversation and generated output; eventually the request must be shortened
or it will fail.

## First exercise

Write the smallest possible `main.py` that performs checkpoint 1 and prints
the raw response. Do not extract the answer or add a loop yet. Once it runs,
we can inspect each JSON field together and make the next small change.

Keep API keys out of `main.py`, shell history where possible, and git. Never
paste a real key into a commit or chat message.
