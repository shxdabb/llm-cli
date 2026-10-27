import contextlib
import io
import os
import sys
import unittest
from unittest.mock import patch

import requests

import main


class FakeResponse:
	def __init__(self, status_code: int = 200, data: object = None, json_error: Exception | None = None):
		self.status_code = status_code
		self.data = data
		self.json_error = json_error

	def raise_for_status(self) -> None:
		if self.status_code >= 400:
			response = requests.Response()
			response.status_code = self.status_code
			raise requests.HTTPError(response=response)

	def json(self) -> object:
		if self.json_error:
			raise self.json_error
		return self.data


class AskTests(unittest.TestCase):
	@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
	def test_success_extracts_text_from_response_parts(self) -> None:
		response = FakeResponse(
			data={
				"candidates": [
					{"content": {"parts": [{"text": " first "}, {"text": "second"}]}}
				]
			}
		)
		with patch("main.requests.post", return_value=response) as post:
			self.assertEqual(main.ask([]), "first\nsecond")
		self.assertEqual(post.call_args.kwargs["timeout"], 30)

	def test_missing_key_fails_before_request(self) -> None:
		with patch.dict(os.environ, {}, clear=True), patch("main.requests.post") as post:
			with self.assertRaisesRegex(main.ChatError, "GEMINI_API_KEY is not set"):
				main.ask([])
		post.assert_not_called()

	@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
	def test_timeout_and_connection_errors_are_friendly(self) -> None:
		for error, message in (
			(requests.Timeout, "timed out"),
			(requests.ConnectionError, "Could not connect"),
		):
			with self.subTest(error=error.__name__):
				with patch("main.requests.post", side_effect=error):
					with self.assertRaisesRegex(main.ChatError, message):
						main.ask([])

	@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
	def test_http_error_is_friendly(self) -> None:
		with patch("main.requests.post", return_value=FakeResponse(status_code=500)):
			with self.assertRaisesRegex(main.ChatError, "HTTP error \\(status 500\\)"):
				main.ask([])

	@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
	def test_invalid_json_is_friendly(self) -> None:
		response = FakeResponse(json_error=ValueError("not JSON"))
		with patch("main.requests.post", return_value=response):
			with self.assertRaisesRegex(main.ChatError, "not valid JSON"):
				main.ask([])

	@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
	def test_missing_or_empty_text_is_friendly(self) -> None:
		for data in ({}, {"candidates": []}, {"candidates": [{"content": {"parts": []}}]}):
			with self.subTest(data=data), patch("main.requests.post", return_value=FakeResponse(data=data)):
				with self.assertRaisesRegex(main.ChatError, "returned no text"):
					main.ask([])


class ChatLoopTests(unittest.TestCase):
	def test_failed_request_does_not_commit_user_turn_to_history(self) -> None:
		inputs = ["failed turn", "successful turn", "follow-up", "exit"]
		output = io.StringIO()
		with (
			patch("sys.argv", ["main.py"]),
			patch("builtins.input", side_effect=inputs),
			patch("main.ask", side_effect=[main.ChatError("temporary failure"), "answer", "follow-up answer"]) as ask,
			contextlib.redirect_stdout(output),
		):
			main.main()

		requests_sent = [call.args[0] for call in ask.call_args_list]
		self.assertEqual([turn["role"] for turn in requests_sent[0]], ["user"])
		self.assertEqual(
			requests_sent[0][0]["parts"][0]["text"],
			"failed turn",
		)
		self.assertEqual(
			[turn["parts"][0]["text"] for turn in requests_sent[1]],
			["successful turn"],
		)
		self.assertEqual(
			[turn["parts"][0]["text"] for turn in requests_sent[2]],
			["successful turn", "answer", "follow-up"],
		)
		self.assertIn("temporary failure", output.getvalue())
		self.assertIn("Goodbye.", output.getvalue())

	def test_help_exits_before_any_api_request(self) -> None:
		output = io.StringIO()
		with (
			patch("sys.argv", ["main.py", "--help"]),
			patch("main.requests.post") as post,
			contextlib.redirect_stdout(output),
			self.assertRaises(SystemExit) as exit_context,
		):
			main.main()
		self.assertEqual(exit_context.exception.code, 0)
		self.assertIn("Chat with Gemini", output.getvalue())
		post.assert_not_called()

	def test_eof_and_keyboard_interrupt_exit_cleanly(self) -> None:
		for interruption in (EOFError, KeyboardInterrupt):
			with self.subTest(interruption=interruption.__name__):
				output = io.StringIO()
				with (
					patch("sys.argv", ["main.py"]),
					patch("builtins.input", side_effect=interruption),
					contextlib.redirect_stdout(output),
				):
					main.main()
				self.assertIn("Goodbye.", output.getvalue())


if __name__ == "__main__":
	unittest.main()
