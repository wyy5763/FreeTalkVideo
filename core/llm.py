import requests
from .config import settings

class LLMError(RuntimeError):
    pass

def generate_script(topic: str, style: str = "口语化、自然、有节奏", target_seconds: int = 60) -> str:
    prompt = f"""你是短视频口播脚本编剧。
主题：{topic}
风格：{style}
目标时长：约{target_seconds}秒。

要求：
1. 直接输出可以口播的中文正文，不要标题、不要解释。
2. 开头3秒必须有吸引力。
3. 句子短一些，适合真人口播。
4. 内容具体，不要空话。
5. 结尾给出自然的行动引导。
"""
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": "你是一名中文短视频口播脚本专家。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
            },
            timeout=180,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise LLMError(f"LLM生成失败，请检查本地模型服务：{exc}") from exc
