import os

import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"



def ask(contents: list[dict[str, object]]) -> str:
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("GEMINI_API_KEY is not set")

	payload = {
		"contents": contents,
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

	response_data = response.json()
	return response_data["candidates"][0]["content"]["parts"][0]["text"]


def main() -> None:
	contents: list[dict[str, object]] = []
	while True:
		try:
			prompt = input("You: ").strip()
		except EOFError:
			break

		if prompt.lower() in {"exit", "quit"}:
			break
		if not prompt:
			continue

		contents.append({"role": "user", "parts": [{"text": prompt}]})
		answer = ask(contents)
		contents.append({"role": "model", "parts": [{"text": answer}]})
		print(f"Gemini: {answer}")


if __name__ == "__main__":
	main()