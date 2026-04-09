import httpx
from bot.config import OLLAMA_BASE_URL


async def generate(prompt: str, model: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]
    except httpx.TimeoutException:
        return "Превышено время ожидания ответа от LLM."
    except httpx.ConnectError:
        return "Сервис LLM временно недоступен. Попробуйте позже."
    except Exception:
        return "Сервис LLM временно недоступен. Попробуйте позже."
