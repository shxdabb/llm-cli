import json
import os

import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def main() -> None:
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("GEMINI_API_KEY is not set")

	prompt = "Explain what an HTTP request is in two sentences."
	payload = {
		"contents": [
			{
				"role": "user",
				"parts": [{"text": prompt}],
			}
		],
		"generationConfig": {
			"maxOutputTokens": 200,
			"temperature": 0.2,
		},
	}
	headers = {"Content-Type": "application/json"}

	response = requests.post(
		API_URL,
		params={"key": api_key},
		headers=headers,
		json=payload,
		timeout=30,
	)
	response.raise_for_status()

	print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
	main()