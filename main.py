import os
from pathlib import Path

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

		if prompt.lower() == "/file":
			try:
				file_path = input("File path: ").strip()
			except EOFError:
				break

			if not file_path:
				print("File path cannot be empty.")
				continue

			path = Path(file_path).expanduser()
			if not path.is_file():
				print(f"Not a file or file does not exist: {path}")
				continue

			try:
				file_text = path.read_text(encoding="utf-8")
			except (OSError, UnicodeDecodeError) as exc:
				print(f"Could not read {path}: {exc}")
				continue

			if not file_text.strip():
				print(f"File is empty: {path}")
				continue

			try:
				instruction = input("What should Gemini do with this file? ").strip()
			except EOFError:
				break

			if not instruction:
				print("Instruction cannot be empty.")
				continue

			user_message = (
				f"{instruction}\n\n"
				f"File: {path.name}\n"
				f"--- File contents ---\n{file_text}\n"
				f"--- End of file contents ---"
			)
		else:
			user_message = prompt

		contents.append({"role": "user", "parts": [{"text": user_message}]})
		answer = ask(contents)
		contents.append({"role": "model", "parts": [{"text": answer}]})
		print(f"Gemini: {answer}")


if __name__ == "__main__":
	main()

	