import argparse
import os
from pathlib import Path

import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


class ChatError(Exception):
	"""An expected API or response problem that can be shown directly to the user."""



def ask(contents: list[dict[str, object]]) -> str:
	# Keep the secret outside the source code. The Gemini REST API expects it as
	# the "key" query parameter, but we never include it in user-facing errors.
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise ChatError("GEMINI_API_KEY is not set. Set it in your environment and try again.")

	# Gemini's REST API expects a list of role/content turns. Each turn contains
	# parts, and each text part carries the actual user or model text.
	payload = {
		"contents": contents,
		"generationConfig": {
			"maxOutputTokens": 200,
			"temperature": 0.2,
		},
	}
	headers = {"Content-Type": "application/json"}

	# A timeout prevents the CLI from waiting forever. Check the HTTP status
	# before attempting to interpret the response body as a successful answer.
	try:
		response = requests.post(
			API_URL,
			params={"key": api_key},
			headers=headers,
			json=payload,
			timeout=30,
		)
		response.raise_for_status()
	except requests.Timeout as exc:
		raise ChatError("The request to Gemini timed out. Please try again.") from exc
	except requests.ConnectionError as exc:
		raise ChatError("Could not connect to Gemini. Check your network and try again.") from exc
	except requests.HTTPError as exc:
		status_code = exc.response.status_code if exc.response is not None else "unknown"
		raise ChatError(f"Gemini returned an HTTP error (status {status_code}).") from exc
	except requests.RequestException as exc:
		raise ChatError("The request to Gemini failed. Please try again.") from exc

	# A successful HTTP response still needs to contain valid JSON; transport
	# success and a usable model response are separate checks.
	try:
		response_data = response.json()
	except ValueError as exc:
		raise ChatError("Gemini returned a response that was not valid JSON.") from exc

	# Gemini can return multiple candidates and multiple parts per candidate.
	# Walk each level defensively because blocked or unusual responses may omit
	# fields. Collect every non-empty text part rather than assuming index [0].
	text_parts: list[str] = []
	candidates = response_data.get("candidates") if isinstance(response_data, dict) else None
	if isinstance(candidates, list):
		for candidate in candidates:
			if not isinstance(candidate, dict):
				continue
			content = candidate.get("content")
			parts = content.get("parts") if isinstance(content, dict) else None
			if not isinstance(parts, list):
				continue
			for part in parts:
				text = part.get("text") if isinstance(part, dict) else None
				if isinstance(text, str) and text.strip():
					text_parts.append(text.strip())

	if not text_parts:
		raise ChatError("Gemini returned no text. Try rephrasing your request.")
	return "\n".join(text_parts)


def main() -> None:
	# Parse arguments first so --help prints and exits before checking the key,
	# opening files, or making any network request.
	parser = argparse.ArgumentParser(description="Chat with Gemini from your terminal.")
	parser.parse_args()

	# This list is the local conversation memory. The API itself does not retain
	# earlier turns, so the client sends this history with each new prompt.
	contents: list[dict[str, object]] = []
	print("Welcome to Gemini chat. Type /help for commands, or exit/quit to leave.")
	while True:
		try:
			prompt = input("You: ").strip()
			if prompt.lower() in {"exit", "quit"}:
				print("Goodbye.")
				break
			if not prompt:
				continue

			if prompt.lower() == "/help":
				print("Commands: /help (show this help), /file (send a local text file), exit/quit (leave).")
				continue

			# File mode converts a local UTF-8 text file into ordinary prompt
			# text; the file is not uploaded through a separate attachment API.
			if prompt.lower() == "/file":
				file_path = input("File path: ").strip()
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

				instruction = input("What should Gemini do with this file? ").strip()
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

			# Treat each turn like a transaction: ask() receives a new list with
			# the proposed user turn, while committed history remains untouched.
			# Only after a successful reply do we store both turns. On failure,
			# the next request therefore cannot accidentally include that prompt.
			pending = contents + [{"role": "user", "parts": [{"text": user_message}]}]
			try:
				answer = ask(pending)
			except ChatError as exc:
				print(exc)
				continue

			contents = pending + [{"role": "model", "parts": [{"text": answer}]}]
			print(f"Gemini: {answer}")
		except (EOFError, KeyboardInterrupt):
			# EOF means input was closed; Ctrl+C raises KeyboardInterrupt.
			# Both are normal ways to leave an interactive terminal session.
			print("\nGoodbye.")
			break


if __name__ == "__main__":
	main()

	