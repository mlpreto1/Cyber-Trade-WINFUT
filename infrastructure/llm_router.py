# infrastructure/llm_router.py
# CYBER TRADE WIN v3.0

import os
import json
import logging
import asyncio

logger = logging.getLogger("llm_router")

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
DAILY_BUDGET_USD = float(os.getenv("DAILY_API_BUDGET_USD", "0.10"))

MODELS = {
    "gemma-4-31b-it": {"provider": "google", "name": "gemma-4-31b-it"},
    "gemma-4-e4b-it": {"provider": "google", "name": "gemma-4-31b-it"},
    "claude-sonnet-4-6": {"provider": "anthropic", "name": "claude-sonnet-4-6"},
}


class LLMRouter:
    def __init__(self):
        self._clientes = {}
        self._custo_acumulado = 0.0

    def _get_cliente(self, provider: str):
        if provider not in self._clientes:
            if provider == "google":
                key = os.getenv("GOOGLE_AI_API_KEY")
                if key and key != "AI_SUBSTITUA_AQUI":
                    try:
                        import google.genai as genai
                        self._clientes[provider] = genai.Client(api_key=key)
                    except Exception as e:
                        logger.warning(f"Google AI não conectado: {e}")
            elif provider == "anthropic":
                key = os.getenv("ANTHROPIC_API_KEY")
                if key:
                    try:
                        import anthropic
                        self._clientes[provider] = anthropic.Anthropic(api_key=key)
                    except Exception as e:
                        logger.warning(f"Anthropic não conectado: {e}")
        return self._clientes.get(provider)

    async def gerar(self, agent: str, user_content: str, max_tokens: int = 1500, temperature: float = 0.1) -> str:
        if PAPER_MODE:
            model = "gemma-4-31b-it"
        else:
            model = self._escolher_modelo(agent)

        config = MODELS.get(model, MODELS["gemma-4-31b-it"])
        provider = config["provider"]
        model_name = config["name"]

        if self._custo_acumulado >= DAILY_BUDGET_USD * 100:
            logger.warning("Orçamento diário excedido")
            return json.dumps({"error": "budget_exceeded"})

        cliente = self._get_cliente(provider)
        if not cliente:
            return json.dumps({"error": "no_client", "provider": provider})

        try:
            if provider == "google":
                response = cliente.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )
                return response.text

            elif provider == "anthropic":
                response = cliente.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": user_content}]
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"LLM erro ({provider}): {e}")
            if not PAPER_MODE and provider == "anthropic":
                return await self._fallback_gemma(user_content, max_tokens, temperature)
            return json.dumps({"error": str(e)})

    async def _fallback_gemma(self, user_content: str, max_tokens: int, temperature: float) -> str:
        logger.info("Fallback: Anthropic → Gemma")
        return await self.gerar("fallback", user_content, max_tokens, temperature)

    def _escolher_modelo(self, agent: str) -> str:
        if agent in ("neo", "cyberdyne"):
            return "claude-sonnet-4-6"
        elif agent == "oracle":
            return "gemma-4-e4b-it"
        else:
            return "gemma-4-31b-it"

    def custo_acumulado(self) -> float:
        return self._custo_acumulado

    def reset_custo(self):
        self._custo_acumulado = 0.0