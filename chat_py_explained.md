# chat.py — Explained

**What chat.py does:** a chat loop in the terminal. I type a message, DeepSeek replies, and it remembers the whole conversation until I type `quit`. This is Stage 1 of my AI secretary, before adding a memory file and Telegram.

## How to run it

1. Open the `ai-secretary` folder in VS Code.
2. Check that the bottom-right corner shows `.venv (3.14.7)`.
3. Use **Run Python File** (the ⌄ next to ▶). Don't use Code Runner: it calls `python`, which doesn't exist on a Mac (only `python3` does), and it ignores `.venv`.
4. Type a message after `You: ` and press Enter. Type `quit` to exit.
5. To force-stop a stuck program: click the terminal and press `Ctrl + C`. The red `KeyboardInterrupt` message afterwards isn't a bug; it just means "you stopped me."

## The structure

```
imports
B: load the key              ← runs once
D: connect to DeepSeek       ← runs once
history = []                 ← runs once
print the quit hint          ← runs once
while True:                  ← everything indented below repeats
    C: type a message
       quit check
       save my message to history
    E: send the whole history to DeepSeek
    F: pull out the reply
       save the reply to history
    A: print the reply
```

| Step | What it does | Tool |
|---|---|---|
| B | Load the API key from `.env` | `python-dotenv` |
| D | Connect to DeepSeek using the key | `openai` |
| C | Type a message | `input()` (built into Python) |
| E | Send the history and the model name | `openai` |
| F | Pull the reply text out of DeepSeek's response | none: plain Python |
| A | Print the reply | `print()` (built into Python) |

**Why B and D are outside the loop:** the key and the connection only need to happen once. Doing them for every message would be wasted work.

**How to know which library you need:** write the steps first. For each step, ask whether Python has a built-in tool for it. If not, find a library, starting with the docs of the service I'm using. Install only the main library; pip installs its dependencies automatically.

---

## Imports

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
```

- `import os` brings in Python's built-in tool for talking to my Mac's system. It's built in, so there's nothing to install.
- `from dotenv import load_dotenv` takes the one function I need from `python-dotenv`. The library is installed as `python-dotenv`, but in code it's called `dotenv`.
- `from openai import OpenAI` takes the client-maker from the `openai` library.
- Imports always go at the very top, because the whole file shares them. Convention: built-in tools first, then installed libraries.

## B: Load the API key from .env

```python
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print("Key loaded:", api_key is not None)
```

- `load_dotenv()` finds my `.env` file and loads its contents.
- `os.getenv("DEEPSEEK_API_KEY")` gets the value with that exact name and stores it in `api_key`.
- The last line prints `True` or `False`. It deliberately doesn't print the key itself, so the key never shows up on my screen or in screenshots.
- **If the name is misspelled**, `os.getenv()` doesn't crash. It quietly returns `None` (Python's "nothing"), and this line prints `Key loaded: False`. Without this check, the problem would only show up later as a confusing error at step E. Catching problems early is a debugging habit.

## D: Connect to DeepSeek using the key

```python
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
```

- `OpenAI(...)` creates a **client**: an object whose job is to talk to an AI service for me. It's like a phone that's set up and ready to dial.
- `api_key=api_key`: the left side is the setting's name, and the right side is my variable from step B. The key is like my **ID card**.
- `base_url="https://api.deepseek.com"` is the **phone number**. By default, the `openai` library calls OpenAI's servers; this tells it to call DeepSeek instead. DeepSeek copied OpenAI's API format on purpose, which is why one library works with both.
- **Creating the client sends nothing.** A wrong key or wrong URL doesn't crash here. It only fails at step E, when the actual call happens. (Once, my URL was missing the `:` in `https://`, and nothing crashed until later.)

## Conversation memory

```python
# Conversation memory: the whole chat, sent every time.
history = []
```

- `[]` is an empty **list** (like an array in JS).
- **The model remembers nothing between requests.** Each request is a fresh start, like texting someone with total amnesia: they only know what's in the current text. To make DeepSeek "remember," my code keeps the whole conversation in `history` and sends all of it every time.
- **`history` must be created above the loop.** If it were inside, the loop would reset it to an empty list every time around, and DeepSeek would forget again.
- **I proved this:** before adding `history`, I said "my name is Jeffrey," then asked "what's my name?", and DeepSeek said it didn't know. After adding `history`, it answered "Your name is Jeffrey."
- **Cost:** every message resends the entire conversation, so each request gets a little bigger. That's why input tokens are the biggest part of the bill, and why real assistants eventually trim or summarize old messages.
- **Limit:** `history` only lives while the program runs. When I type `quit`, it's erased. Remembering across runs needs a file on disk (the next part of Stage 1).

## The loop

```python
print("Type 'quit' to exit.")
while True:
    message = input("You: ")
    if message == "quit":
        break
```

- `while True:` repeats forever, like `while (true) { }` in JS.
- **Python uses indentation (4 spaces) instead of `{ }`.** Everything indented under `while` is inside the loop. Code below the loop that isn't indented only runs after the loop ends.
- `break` exits the loop. It's indented one level deeper because it's inside the `if`.
- `==` checks whether two things are equal (`=` is for storing a value).
- To indent several lines at once in VS Code: select them and press `Tab`. `Shift + Tab` removes indentation.
- The quit hint is a `print()` above the loop, so it shows once. (Once, I used a second `input()` for the hint. That was a bug: every `input()` waits for typing, so my `quit` went into the second `input()`, wasn't saved anywhere, and the loop never ended.)

## C: Type a message, then save it

```python
    message = input("You: ")
    ...
    history.append({"role": "user", "content": message})
```

- `input()` shows the text inside the parentheses, waits for me to type, and gives back what I typed. It works like `prompt()` in JavaScript.
- The text shows **exactly** as written, spaces included. That's why it's `"You: "` with a space at the end, so my typing doesn't stick to the label.
- `.append(...)` adds an item to the end of a list, like `push()` in JS.
- The item is a **dictionary** (Python's version of a JS object): `"role": "user"` means I said it, and `"content"` is the text.
- My message is saved **after** the quit check, so `quit` itself is never sent to DeepSeek.

## E: Send the conversation to DeepSeek

```python
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=history,
    )
```

- `client.chat.completions.create(...)` is the actual dialing. `create` means "send a new request."
- `messages=history` sends the whole conversation, not just the newest message.
- `model="deepseek-flash"` chooses the model. **This is how I choose which model the API uses.** `deepseek-v4-pro` is on standby for harder tasks.
- **Model name vs. model version:** DeepSeek's docs (Models & Pricing page) list two different things. The **MODEL** row (`deepseek-flash`) is the name I type in code. The **MODEL VERSION** row (e.g. `DeepSeek-V4.1-Flash`) is the version currently running behind that name. Use the name from the docs, not the version.
- **Don't ask the model which model it is.** Models often don't know their own name, because their knowledge comes from training data collected before they were released. Trust the API's answer instead (see step F).
- `response =` saves DeepSeek's whole answer.

## F: Pull the reply out, then save it

```python
    reply = response.choices[0].message.content
    model = response.model
    history.append({"role": "assistant", "content": reply})
```

DeepSeek's response is nested, like objects inside objects in JS:

```
response
 ├─ model          ← which model actually answered (one level deep)
 └─ choices        ← a list (it could hold several answers; I get one)
     └─ [0]        ← the first answer (lists start counting at 0)
         └─ message
             └─ content   ← the reply text
```

- Dots (`.`) go one level deeper into an object; `[0]` picks the first item of a list.
- `response.model` tells me which model answered. This is the reliable way to check the model.
- The reply is saved to `history` with `"role": "assistant"`, so DeepSeek's own answers are part of the memory too.
- No library is needed here. `openai` already handed me the response in step E; this is plain Python.

## A: Print the reply

```python
    print("DeepSeek:", reply)
    print("Model:", model)
```

- `print()` automatically adds a space between items separated by a comma, so the label doesn't need its own space at the end.
- **Two kinds of spaces:** spaces *inside* quotes show up in the output. Spaces *outside* quotes (like after the comma) are only for readability; Python ignores them. Convention: always put a space after a comma.
- The `Model:` line was for a mini task and is optional.

---

## Errors I've run into

| Error | What it meant | Fix |
|---|---|---|
| `/bin/sh: python: command not found` (exit code 127) | Code Runner's ▶ button calls `python`, which doesn't exist on a Mac | Use **Run Python File** |
| `NameError: name 'reply' is not defined` | I used `reply` before it was created. Python runs top to bottom, and `reply` is only created in step F | Use a name that already exists at that point (`message`) |
| `KeyboardInterrupt` | I pressed `Ctrl + C` to stop the program | Not a bug |
| Stuck forever on `You:` | Steps E, F, and A weren't indented, so they were outside the loop | Indent them under `while True:` |

- "Did you mean: …?" suggestions in error messages are Python's guesses. They're often wrong.
- VS Code highlighting every copy of a name when my cursor is on it isn't an error. It's a way to trace a variable through the file.

---

## Other files in this project

- `.venv/`: my project's private "box" of libraries. It keeps each project's library versions separate, so installing a new version for one project can't break another.
- `.env`: my API key. Stays on my Mac only. Never screenshot or share it.
- `.gitignore`: the "never upload" list for Git. It contains `.env` and `.venv/`.
- `hello.py`: the first test file. Can be deleted.

## .env rules

- Format: `DEEPSEEK_API_KEY=sk-...` on its own line.
- No spaces around the `=`, and no quotes around the key.
- `#` comments are fine, but on their own line, never on the same line as the key.
- The file sits directly in `ai-secretary`, not inside `.venv`.
- Line order doesn't matter.

## Every new Terminal session

If I'm not using VS Code's terminal (which activates `.venv` automatically):

```
cd ~/ai-secretary
source .venv/bin/activate
```
