# E-Commerce Chatbot

A simple Rasa-based assistant prototype for e-commerce demos. This repository contains a minimal assistant that can answer product price questions, recommend products, and discuss product quality using template replies and story flows.

## What this project does
- Recognizes intents like `greet`, `check_price`, `recommend_product`, and `ask_quality`.
- Replies using template utterances defined in `domain.yml` (e.g., `utter_price`, `utter_recommend_product`).
- Demonstrates conversation flows in `data/stories.yml` and rules in `data/rules.yml`.
- Supports custom actions via `actions/actions.py` if dynamic behavior is needed.

## What has been done
- Project scaffold created with Rasa files: `domain.yml`, `data/`, `actions/`, and `endpoints.yml`.
- Fixed missing-action errors by registering previously missing utterances in `domain.yml`:
  - `utter_ask_quality` added
  - `utter_recommend_product` added
- Standardized story references to use existing utterances (e.g., `utter_quality`).

## Quick start (Windows PowerShell)
1. Create and activate a virtual environment (recommended):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install Rasa (pick a version compatible with your environment):
```powershell
pip install rasa
```
3. Train the assistant:
```powershell
rasa train
```
4. Run the action server (if you add custom actions):
```powershell
rasa run actions
```
5. Start the assistant interactively:
```powershell
rasa shell
```

## Important files
- `domain.yml` — intents, entities, slots, and `responses:` (utterances).
- `data/nlu.yml` — NLU training examples.
- `data/stories.yml`, `data/rules.yml` — conversation flows and rules.
- `actions/actions.py` — custom action implementations.
- `endpoints.yml` — action server and tracker configuration.
- `tests/` — example test stories.

## Troubleshooting: missing actions or utterances
If the bot complains about a missing action or utterance, it usually means a story or rule refers to a name that isn't declared in `domain.yml`.

Common fixes:
- For template replies: add the utterance under `responses:` in `domain.yml`.
- For code-backed actions: implement a custom action (named `action_<name>`) in `actions/actions.py` and list it under `actions:` in `domain.yml`.
- Or update stories to reference an existing utterance.
- After edits, re-run `rasa train` to apply changes.

## Next suggested steps
- Add more NLU examples to `data/nlu.yml` to improve intent classification.
- Implement `action_recommend_product` for dynamic recommendations (DB/API lookups).
- Add tests for stories and custom actions using `rasa test`.
- Configure `endpoints.yml` for production (tracker store, remote action server).

If you want, I can run `rasa train` now and do a quick smoke test, or implement a simple dynamic recommendation action. Tell me which you'd prefer.

## LLM integration (optional)
This project contains an example custom action (`action_call_llm`) that demonstrates how to call an external LLM (OpenAI-style). To enable it:

- Install the OpenAI client in the environment where actions run:
```powershell
pip install openai
```
- Set your API key on the action server machine (do NOT commit this to source):
```powershell
$env:OPENAI_API_KEY = 'sk-...'
```
- Optional: set the model name the action uses:
```powershell
$env:OPENAI_MODEL = 'gpt-3.5-turbo'
```

The action builds a brief prompt from the user's latest message and an optional `product` slot, calls the LLM, and returns the generated reply to the user. For development, you can also stub this action to return a canned reply to avoid API usage.

Security notes:
- Never commit API keys or credentials. Store secrets in environment variables, a secrets manager, or a CI/CD secret store.
- Consider adding request rate limits, caching, and prompt sanitization before using an LLM in production.

## Git ignore and secrets
We added a recommended `.gitignore` to keep virtual environments, model artifacts, caches, and credential files out of source control. Important files you should NOT commit:

- `credentials.yml`, `secrets.yml`, and any other file that contains API keys or passwords
- model archives and `.rasa/` cache directories
- local virtual environment folders like `.venv/`, `venv/`, or `env/`

If you accidentally committed secrets, rotate them immediately and remove them from the repo history (tools: `git filter-repo` or `git rebase` + force push).
