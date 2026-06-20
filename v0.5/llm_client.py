import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("Missing DEEPSEEK_API_KEY. Please set it in .env.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


SYSTEM_PROMPT = """
你是一个个人机会观察教练。

你的任务是分析用户输入的一条野生信息，判断它是否包含值得关注的学习、项目、内容或商业机会。

信号分类只能从以下 5 类中选择一个：
1. 技术趋势
2. 项目灵感
3. 内容选题
4. 需求信号
5. 待观察信号

机会分数 score 必须是 1-5 的整数：
1 = 暂时价值很弱，只适合记录
2 = 有一点观察价值，但还不明确
3 = 有明确学习或内容价值
4 = 有明确项目或产品验证价值
5 = 强机会，值得优先投入行动

你必须输出 JSON，字段如下：
{
  "category": "信号分类",
  "score": 1-5,
  "reason": "为什么这个信号值得关注",
  "project_suggestion": "一个可执行的最小项目建议",
  "content_idea": "一个内容选题建议"
}

要求：
- 只输出 JSON
- 不要输出 Markdown
- 不要输出解释性前后缀
- score 必须是整数
- category 必须是上述 5 类之一
"""


def analyze_signal(signal: str, source: str | None, note: str | None):
    user_prompt = f"""
请分析下面这条信号：

signal: {signal}
source: {source or "unknown"}
note: {note or ""}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        required_fields = [
            "category",
            "score",
            "reason",
            "project_suggestion",
            "content_idea",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"LLM response missing field: {field}")

        data["score"] = int(data["score"])

        return {
            "category": data["category"],
            "score": data["score"],
            "reason": data["reason"],
            "project_suggestion": data["project_suggestion"],
            "content_idea": data["content_idea"],
        }

    except Exception as exc:
        raise RuntimeError(f"Failed to analyze signal with DeepSeek: {exc}") from exc