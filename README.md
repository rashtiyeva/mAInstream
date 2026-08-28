<div align="center">

# mAInstream

**AI-assisted song identification and lyric continuation with Genius-backed matching and live SSE progress.**

<br>

![Python](https://img.shields.io/badge/Python-3.12-B8A7D9?style=flat-square\&logo=python\&logoColor=2D2933)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-B8A7D9?style=flat-square\&logo=fastapi\&logoColor=2D2933)
![Docker](https://img.shields.io/badge/Docker-Compose-B8A7D9?style=flat-square\&logo=docker\&logoColor=2D2933)
![Tests](https://img.shields.io/badge/tests-118%20passing-747078?style=flat-square)
[![CI](https://github.com/rashtiyeva/mAInstream/actions/workflows/tests.yml/badge.svg)](https://github.com/rashtiyeva/mAInstream/actions/workflows/tests.yml)

</div>

<br>

mAInstream takes a fragment of an **English-language song lyric**, identifies the most likely song with OpenAI, retrieves its lyrics from Genius, matches the input against the source text, and returns what comes next.

The LLM is responsible for **song identification only**. Lyric retrieval, parsing, matching, typo tolerance, and continuation selection are handled by deterministic backend logic.

---

## Demo

<div align="center">



https://github.com/user-attachments/assets/07e456ea-5e1a-4a04-b673-8d74bcc1bc2c



https://github.com/user-attachments/assets/e319d229-d152-4768-8e79-1067a36256f7



</div>

The UI streams live pipeline updates while the request is being processed and replaces them with the final song, artist, and lyric continuation.

---

## How it works

```text
Lyric fragment
      ↓
OpenAI song identification
      ↓
Genius API search
      ↓
Genius page retrieval
      ↓
Lyrics parsing & cleanup
      ↓
Progressive lyric matching
      ↓
Next meaningful lyric
      ↓
SSE result → browser UI
```

The frontend receives live updates through **SSE (Server-Sent Events)**, so the user can see the current processing stage instead of waiting on a static loading screen.

---

## Matching pipeline

Once the song and lyrics are resolved, matching becomes progressively more tolerant:

```text
Exact
  ↓
Normalized
  ↓
Normalized partial
  ↓
Aggressive partial
  ↓
Fuzzy typo-tolerant
  ↓
Match / not found
```

### Exact

Direct comparison against the original lyric text.

### Normalized

Handles casing, Unicode normalization, apostrophe variants, repeated whitespace, and surrounding whitespace while preserving punctuation.

### Normalized partial

Allows the input to match part of a longer Genius line while respecting word boundaries.

### Aggressive partial

Removes punctuation differences before comparison.

```text
"It's the climb" → "its the climb"
"I'm still here" → "im still here"
```

### Fuzzy

Uses **RapidFuzz** as the final local fallback for typo tolerance.

```text
"itss the climb"
"i remmber it all too"
"euphoriaa"
```

Fuzzy matching runs only after the higher-confidence deterministic strategies fail, reducing the risk of false positives.

---

## Continuation logic

After finding the lyric position, `NextLineService` works with the **original Genius text**, not the normalized representation.

It can:

* preserve the remainder of a partially matched line;
* continue into the following lyric line;
* skip empty lines;
* skip vocal-only lines such as `oh`, `ooh`, `yeah`, or `uh`.

Normalization is used only for comparison.

---

## Architecture

```text
Browser
   │
   │ POST /lyrics/identify/stream
   ▼
FastAPI Controller
   │
   ├── Progress Reporter ───────► SSE progress / result / error
   │
   ▼
LyricsOrchestrator
   │
   ├── LyricInputValidator
   │
   ├── SongIdentifierService
   │      └── OpenAIClient
   │
   ├── LyricsProviderService
   │      └── GeniusProvider
   │             └── GeniusClient
   │
   ├── GeniusLyricsParser
   │
   └── NextLineService
          ├── LyricMatcher
          ├── LyricNormalizer
          └── LyricLineClassifier
```

The backend uses a layered structure with FastAPI dependency injection, typed Pydantic models, asynchronous provider clients, dedicated parsing logic, and a single orchestrator coordinating the workflow.

---

## Live progress

The streaming endpoint:

```http
POST /lyrics/identify/stream
```

returns `text/event-stream`.

The pipeline exposes machine-readable progress states:

```text
VALIDATING_INPUT
IDENTIFYING_SONG
SONG_IDENTIFIED
SEARCHING_LYRICS
LYRICS_SOURCE_FOUND
FETCHING_LYRICS
PARSING_LYRICS
MATCHING_LYRIC
CONTINUATION_FOUND
```

Because the stream is POST-based, the frontend consumes it with `fetch()` and `ReadableStream` rather than native `EventSource`.

Every stream ends with either a `result` or `error` event.

---

## Error handling

Expected failures are exposed through stable backend error codes:

```text
LYRIC_TOO_GENERIC
SONG_NOT_FOUND
LYRICS_NOT_FOUND
LYRIC_NOT_FOUND
CONTINUATION_NOT_FOUND
PROVIDER_UNAVAILABLE
INTERNAL_ERROR
```

The backend keeps error responses machine-readable and neutral.

The JavaScript frontend maps those codes to friendly, playful UI messages without coupling presentation text to backend exceptions.

---

## Input safety

Lyric input is limited to **300 characters**.

The frontend mirrors the limit for UX, while the backend remains the authoritative validation layer.

Dynamic content is rendered as text rather than injected HTML. User input, song titles, artist names, continuations, and streamed content are treated as plain text.

The same-origin frontend also uses a restrictive Content Security Policy.

---

## Tech stack

| Technology                  | Purpose                            |
| --------------------------- | ---------------------------------- |
| **Python 3.12**             | Backend runtime                    |
| **FastAPI**                 | Async API and dependency injection |
| **Uvicorn**                 | ASGI server                        |
| **Pydantic**                | Typed models and validation        |
| **OpenAI API**              | Song identification                |
| **Genius API**              | Song discovery                     |
| **Genius HTML**             | Lyrics source                      |
| **httpx**                   | Async HTTP communication           |
| **Beautiful Soup**          | Lyrics HTML parsing                |
| **RapidFuzz**               | Typo-tolerant matching             |
| **pytest / pytest-asyncio** | Automated testing                  |
| **JavaScript**              | Frontend and SSE consumption       |
| **HTML / CSS**              | Same-origin UI                     |
| **Docker / Docker Compose** | Reproducible runtime               |
| **GitHub Actions**          | Continuous Integration             |

---

## Run with Docker

Set the required environment variables in your shell or local `.env` file:

```env
OPENAI_API_KEY=...
GENIUS_ACCESS_TOKEN=...
OPENAI_MODEL=...
REQUEST_TIMEOUT=30
```

Then build and start the application:

```bash
docker compose up -d --build
```

Open the UI:

```text
http://localhost:8000/app/
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/
```

Stop the application:

```bash
docker compose down
```

---

## Local development

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/app/
```

---

## Testing

Run the full automated test suite:

```bash
python -m pytest
```

The project currently has **118 passing tests** covering matching strategies, normalization, typo tolerance, multiline input, continuation extraction, Genius parsing, provider behavior, orchestration, API error mapping, SSE event ordering, settings, and dependency lifecycle.

External OpenAI and Genius calls are mocked in the automated suite.

### CI

GitHub Actions runs the test suite automatically on pushes and pull requests.

The current workflow can be inspected under the repository's **Actions** tab:

[View CI runs](https://github.com/rashtiyeva/mAInstream/actions)

---

## Design decisions

### Why deterministic matching before fuzzy matching?

Exact and normalized strategies provide higher-confidence matches. Fuzzy matching is kept as the final local fallback to improve typo tolerance without making approximate matching the default.

### Why OpenAI + Genius?

OpenAI solves the ambiguous task of identifying a song from an incomplete lyric fragment.

Genius then provides a concrete source against which the application can perform deterministic matching and continuation extraction.

**The model does not generate the continuation.**

### Why Genius API + Genius HTML?

The Genius API locates and verifies the song page. The page itself provides the lyric containers that are extracted and cleaned before matching.

### Why SSE?

Song identification, Genius lookup, page retrieval, parsing, and matching can take noticeable time.

SSE exposes those stages to the frontend over the existing HTTP request without introducing polling or a more complex bidirectional protocol.

---

