"use strict";

const API_ENDPOINT = "/lyrics/identify/stream";
const MAX_CHARACTERS = 300;

const PROGRESS_MESSAGES = Object.freeze({
  VALIDATING_INPUT: "Let me see what you’ve got…",
  IDENTIFYING_SONG: "Trying to figure out what song is on your mind🎧",
  SEARCHING_LYRICS: "Digging through the lyrics…",
  LYRICS_SOURCE_FOUND: "Found the lyrics source 👀",
  FETCHING_LYRICS: "Pulling the lyrics together…",
  PARSING_LYRICS: "Cleaning up the lyric chaos…",
  MATCHING_LYRIC: "Looking for your exact moment 👀",
  CONTINUATION_FOUND: "Got it ✨",
});

const ERROR_MESSAGES = Object.freeze({
  INVALID_REQUEST: "That request looks a little off-key. Check it and try again.",
  LYRIC_TOO_GENERIC: "This one’s a little too generic 😭 I’ll need a longer lyric.",
  SONG_NOT_FOUND:
    "Looks like this song isn’t mAInstream enough for me 🥲 Try a longer or more recognizable line.",
  LYRICS_NOT_FOUND: "I found the song, but its lyrics are playing hide-and-seek 👀",
  LYRIC_NOT_FOUND:
    "I found the song, but not that line 👀 Check the wording or give me a little more.",
  CONTINUATION_NOT_FOUND:
    "I found the line… and then the song basically gave up on me 😭",
  PROVIDER_UNAVAILABLE:
    "One of my backstage assistants stopped cooperating 💀 Try again in a moment.",
  INTERNAL_ERROR:
   "Something broke backstage 💀 Tell the developer she probably broke something again or she is out of tokens.",
});

const FALLBACK_ERROR_MESSAGE = "Something went off-key 💀 Try again in a moment.";
const UNKNOWN_PROGRESS_MESSAGE = "Still working on it…";

const form = document.querySelector("#lyric-form");
const lyricInput = document.querySelector("#lyric-input");
const characterCount = document.querySelector("#character-count");
const submitButton = document.querySelector("#submit-button");
const buttonLabel = submitButton.querySelector(".button-label");
const outputPanel = document.querySelector("#output-panel");

let activeController = null;

class PublicApiError extends Error {
  constructor(code) {
    super(code);
    this.name = "PublicApiError";
    this.code = code;
  }
}

class SseParser {
  constructor() {
    this.buffer = "";
  }

  push(chunk) {
    this.buffer += chunk;
    const events = [];
    let separator = this.buffer.match(/\r?\n\r?\n/);

    while (separator?.index !== undefined) {
      const block = this.buffer.slice(0, separator.index);
      this.buffer = this.buffer.slice(separator.index + separator[0].length);
      const event = this.parseBlock(block);

      if (event) {
        events.push(event);
      }

      separator = this.buffer.match(/\r?\n\r?\n/);
    }

    return events;
  }

  flush() {
    const block = this.buffer;
    this.buffer = "";
    return block.trim() ? [this.parseBlock(block)].filter(Boolean) : [];
  }

  parseBlock(block) {
    let eventName = "message";
    const dataLines = [];

    for (const line of block.split(/\r?\n/)) {
      if (!line || line.startsWith(":")) {
        continue;
      }

      const colonIndex = line.indexOf(":");
      const field = colonIndex === -1 ? line : line.slice(0, colonIndex);
      let value = colonIndex === -1 ? "" : line.slice(colonIndex + 1);

      if (value.startsWith(" ")) {
        value = value.slice(1);
      }

      if (field === "event") {
        eventName = value;
      } else if (field === "data") {
        dataLines.push(value);
      }
    }

    if (dataLines.length === 0) {
      return null;
    }

    return { event: eventName, data: dataLines.join("\n") };
  }
}

function createElement(tagName, className, text) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (text !== undefined) {
    element.textContent = text;
  }

  return element;
}

function replaceOutput(content, stateClass) {
  outputPanel.className = `output-panel ${stateClass}`;
  outputPanel.replaceChildren(content);
  outputPanel.classList.remove("output-transition");
  void outputPanel.offsetWidth;
  outputPanel.classList.add("output-transition");
}

function renderStatus(message) {
  const wrapper = createElement("div", "status-content");
  const indicator = createElement("div", "status-indicator");
  indicator.setAttribute("aria-hidden", "true");
  indicator.append(
    document.createElement("span"),
    document.createElement("span"),
    document.createElement("span"),
  );
  wrapper.append(indicator, createElement("p", "status-message", message));
  outputPanel.setAttribute("aria-live", "polite");
  replaceOutput(wrapper, "is-status");
}

function renderProgress(payload) {
  if (payload.step === "SONG_IDENTIFIED") {
    const song = typeof payload.song === "string" ? payload.song : "the song";
    const artist = typeof payload.artist === "string" ? payload.artist : "the artist";
    renderStatus(`Got it — ${song} by ${artist} ✨`);
    return;
  }

  renderStatus(PROGRESS_MESSAGES[payload.step] ?? UNKNOWN_PROGRESS_MESSAGE);
}

function renderResult(payload) {
  const song = typeof payload.song === "string" ? payload.song : "Unknown song";
  const artist = typeof payload.artist === "string" ? payload.artist : "Unknown artist";
  const continuation =
    typeof payload.continuation === "string" ? payload.continuation : "";

  const wrapper = createElement("div", "result-content");
  wrapper.append(
    createElement("p", "result-label", "Now playing"),
    createElement("p", "track-title", song),
    createElement("p", "track-artist", artist),
    createElement("p", "continuation", continuation),
  );
  outputPanel.setAttribute("aria-live", "polite");
  replaceOutput(wrapper, "is-result");
}

function renderError(code) {
  const message = ERROR_MESSAGES[code] ?? FALLBACK_ERROR_MESSAGE;
  const wrapper = createElement("div", "error-content");
  wrapper.setAttribute("role", "alert");
  wrapper.append(
    createElement("span", "error-icon", "♪"),
    createElement("p", "error-label", "That didn’t land"),
    createElement("p", "error-message", message),
  );
  outputPanel.setAttribute("aria-live", "assertive");
  replaceOutput(wrapper, "is-error");
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.classList.toggle("is-loading", isLoading);
  buttonLabel.textContent = isLoading ? "Listening…" : "Finish the lyrics";
  lyricInput.setAttribute("aria-busy", String(isLoading));
}

function updateCharacterCount() {
  characterCount.textContent = `${lyricInput.value.length} / ${MAX_CHARACTERS}`;
}

function parseJson(data) {
  try {
    return JSON.parse(data);
  } catch {
    throw new Error("Malformed JSON in the event stream.");
  }
}

function handleStreamEvent(streamEvent) {
  const payload = parseJson(streamEvent.data);

  if (streamEvent.event === "progress") {
    renderProgress(payload);
    return false;
  }

  if (streamEvent.event === "result") {
    renderResult(payload);
    return true;
  }

  if (streamEvent.event === "error") {
    throw new PublicApiError(payload.code);
  }

  return false;
}

async function errorFromResponse(response) {
  try {
    const payload = await response.json();
    return new PublicApiError(payload.code);
  } catch (error) {
    if (error instanceof PublicApiError) {
      return error;
    }
    return new PublicApiError("INTERNAL_ERROR");
  }
}

async function consumeSse(response) {
  if (!response.ok) {
    throw await errorFromResponse(response);
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("text/event-stream") || !response.body) {
    throw new Error("The server did not return an event stream.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const parser = new SseParser();
  let terminalEventReceived = false;

  try {
    while (!terminalEventReceived) {
      const { value, done } = await reader.read();
      const events = parser.push(decoder.decode(value ?? new Uint8Array(), { stream: !done }));

      for (const event of events) {
        terminalEventReceived = handleStreamEvent(event);
        if (terminalEventReceived) {
          break;
        }
      }

      if (done) {
        break;
      }
    }

    if (!terminalEventReceived) {
      for (const event of parser.flush()) {
        terminalEventReceived = handleStreamEvent(event);
      }
    }
  } finally {
    reader.releaseLock();
  }

  if (!terminalEventReceived) {
    throw new Error("The event stream ended before returning a result.");
  }
}

async function submitLyric() {
  if (activeController) {
    return;
  }

  const lyric = lyricInput.value.trim();
  if (!lyric) {
    renderError("INVALID_REQUEST");
    lyricInput.focus();
    return;
  }

  activeController = new AbortController();
  setLoading(true);
  renderStatus(PROGRESS_MESSAGES.VALIDATING_INPUT);

  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        Accept: "text/event-stream",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ lyric }),
      cache: "no-store",
      credentials: "same-origin",
      signal: activeController.signal,
    });

    await consumeSse(response);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      return;
    }

    if (error instanceof PublicApiError) {
      renderError(error.code);
    } else {
      renderError("UNKNOWN_ERROR");
    }
  } finally {
    activeController = null;
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  void submitLyric();
});

lyricInput.addEventListener("input", updateCharacterCount);
lyricInput.addEventListener("keydown", (event) => {
  if (!event.ctrlKey || event.key !== "Enter" || event.repeat) {
    return;
  }

  event.preventDefault();
  void submitLyric();
});

window.addEventListener("beforeunload", () => {
  activeController?.abort();
});

updateCharacterCount();
