# llm.py
#
# A simple LLM wrapper that supports multiple providers — including free ones.
#
# Supported providers
# -------------------
#   "openai"  — OpenAI (paid, needs OPENAI_API_KEY)
#   "gemini"  — Google Gemini (FREE tier available, needs GEMINI_API_KEY)
#   "groq"    — Groq (FREE tier available, needs GROQ_API_KEY)
#   "ollama"  — Local models via Ollama (FREE, no API key, runs on your machine)
#
# Quick start with free providers
# --------------------------------
#   Gemini (recommended free option):
#     1. Get a free key at https://aistudio.google.com/apikey
#     2. export GEMINI_API_KEY="your-key"
#     3. llm = SimpleLLM(provider="gemini")
#
#   Groq (fast free option):
#     1. Get a free key at https://console.groq.com
#     2. export GROQ_API_KEY="your-key"
#     3. llm = SimpleLLM(provider="groq")
#
#   Ollama (fully local, no key needed):
#     1. Install from https://ollama.com
#     2. Run: ollama pull llama3.2
#     3. llm = SimpleLLM(provider="ollama")


import json
import os


class SimpleLLM:
    """
    A unified LLM wrapper that works with OpenAI, Gemini, Groq, and Ollama.

    Parameters
    ----------
    provider : str
        Which LLM provider to use. One of:
        "openai", "gemini", "groq", "ollama"
        Default is "gemini" (free tier available).

    model : str or None
        The model name to use. If None, a sensible default is chosen
        for the selected provider:
          openai  → "gpt-4o-mini"
          gemini  → "gemini-1.5-flash"   (free)
          groq    → "llama-3.1-8b-instant" (free)
          ollama  → "llama3.2"            (local)

    api_key : str or None
        Explicit API key. If None, reads from the environment variable:
          openai  → OPENAI_API_KEY
          gemini  → GEMINI_API_KEY
          groq    → GROQ_API_KEY
          ollama  → (no key needed)

    base_url : str or None
        Custom base URL. Only needed for Ollama (defaults to http://localhost:11434).

    Example
    -------
        # Free — Google Gemini
        llm = SimpleLLM(provider="gemini")

        # Free — Groq
        llm = SimpleLLM(provider="groq")

        # Free — local Ollama (no internet needed)
        llm = SimpleLLM(provider="ollama")

        # Paid — OpenAI
        llm = SimpleLLM(provider="openai", model="gpt-4o-mini")
    """

    # Default models for each provider
    DEFAULT_MODELS = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini-1.5-flash",
        "groq": "llama-3.1-8b-instant",
        "ollama": "llama3.2",
    }

    # Environment variable names for API keys
    ENV_VARS = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "ollama": None,  # no key needed
    }

    def __init__(self, provider="gemini", model=None, api_key=None, base_url=None):
        provider = provider.lower()

        if provider not in self.DEFAULT_MODELS:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Choose from: {list(self.DEFAULT_MODELS.keys())}"
            )

        self.provider = provider
        self.model = model or self.DEFAULT_MODELS[provider]

        # Resolve API key
        env_var = self.ENV_VARS[provider]
        self.api_key = api_key or (os.environ.get(env_var) if env_var else None)

        if provider != "ollama" and not self.api_key:
            raise ValueError(
                f"No API key found for provider '{provider}'. "
                f"Set the {env_var} environment variable or pass api_key=... "
                f"when creating SimpleLLM()."
            )

        # Build the underlying client based on provider
        self.client = self._build_client(base_url)

    def _build_client(self, base_url):
        """
        Create the appropriate API client for the chosen provider.

        All providers except Gemini use an OpenAI-compatible client
        (same interface, different base URL and key).
        Gemini uses its own google-generativeai SDK.
        """
        if self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)

        elif self.provider == "gemini":
            # google-generativeai uses its own client style
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "Install the Gemini SDK: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            # Return the genai module itself — we'll call it in ask()
            return genai

        elif self.provider == "groq":
            # Groq has an OpenAI-compatible API
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("Install openai: pip install openai")
            return OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
            )

        elif self.provider == "ollama":
            # Ollama also exposes an OpenAI-compatible endpoint locally
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("Install openai: pip install openai")
            url = base_url or "http://localhost:11434/v1"
            return OpenAI(
                api_key="ollama",   # Ollama ignores the key but the client needs one
                base_url=url,
            )

    # ------------------------------------------------------------------ #
    # Core ask methods                                                     #
    # ------------------------------------------------------------------ #

    def ask(self, prompt, system_prompt=None):
        """
        Send a prompt to the LLM and return the text response.

        Parameters
        ----------
        prompt        : str  — the user message
        system_prompt : str  — optional system instruction

        Returns
        -------
        str  — the LLM's reply as plain text
        """
        if self.provider == "gemini":
            return self._ask_gemini(prompt, system_prompt)
        else:
            # openai / groq / ollama all share the same OpenAI-compatible interface
            return self._ask_openai_compatible(prompt, system_prompt)

    def ask_json(self, prompt, system_prompt=None):
        """
        Send a prompt and parse the response as JSON.

        Returns dict or list on success, empty dict {} on parse failure.

        Parameters
        ----------
        prompt        : str
        system_prompt : str, optional

        Returns
        -------
        dict or list
        """
        # Append JSON instruction to the system prompt
        json_instruction = "You must respond with valid JSON only. No explanation, no markdown fences."
        combined_system = (
            f"{system_prompt}\n{json_instruction}" if system_prompt else json_instruction
        )

        raw = self.ask(prompt, system_prompt=combined_system)

        # Strip markdown code fences if present (e.g. ```json ... ```)
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    # ------------------------------------------------------------------ #
    # Provider-specific implementations                                   #
    # ------------------------------------------------------------------ #

    def _ask_openai_compatible(self, prompt, system_prompt=None):
        """Used for openai, groq, and ollama — all share the same API shape."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        return response.choices[0].message.content.strip()

    def _ask_gemini(self, prompt, system_prompt=None):
        """Used for Google Gemini via the google-generativeai SDK."""
        genai = self.client

        # Combine system prompt and user prompt for Gemini
        # (Gemini Flash supports system_instruction in GenerativeModel)
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0),
        )
        return response.text.strip()
