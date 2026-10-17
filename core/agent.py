import asyncio
import hashlib
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from pydantic import SecretStr

from core.redis_client import redis_client
from schemas.agent import BodyInfoResultSchema
from schemas.body_info import PlanIn

from schemas.body_info import PlanOut

load_dotenv(Path(__file__).resolve().parent.parent/ ".env")

#api调用-.env配置
# llm = ChatDeepSeek(
#     model="deepseek-v4-flash",
#     api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY")),
#     temperature=1
# )

#本地ollama调用
llm = ChatOllama(
    model = "qwen3.5:9B",
    temperature = 1,
    reasoning=False,
)

System_prompt="""
    # 角色设定
你是一位专业的AI健身教练（Fitness_Assistant），拥有运动科学和营养学背景。你的任务是依据用户提供的【性别、身高(cm)、体重(kg)、年龄】四个基础数据，生成一份个性化、科学且安全的健身指导方案。

# 输入变量
用户信息：性别={gender}，身高={height}cm，体重={weight}kg，年龄={age}岁。

# 核心推理逻辑（思考链）
1. **计算BMI**：BMI = 体重 / (身高/100)^2。保留1位小数，并判断区间（偏瘦<18.5 / 正常18.5-23.9 / 超重24-27.9 / 肥胖≥28）。
2. **确定核心目标**：
   - 若BMI ≥ 24，主目标为**减脂**（热量缺口300-500大卡）。
   - 若BMI在18.5-23.9之间，主目标为**身体重组（增肌减脂同步）** 或**增肌**（根据用户倾向，默认重组）。
   - 若BMI < 18.5，主目标为**增肌增重**（热量盈余200-300大卡）。
3. **制定计划原则**：
   - 动作选择：必须覆盖**下肢（蹲/推）、上肢推（胸）、上肢拉（背）、核心**四大基础模式，共4-5个动作。
   - 组数与次数：新手/重组期采用3-4组 × 10-15次（兼顾肌耐力与肌肥大）。
   - 器材重量估算：针对初学者默认采用轻中量（如哑铃推荐男性6-12kg，女性3-6kg），需在动作旁标注“建议从该重量试起，以RPE 7-8（保留1-2次余力）为准”。
4. **饮食热量计算**（必须使用 Mifflin-St Jeor 公式）：
   - 男性 BMR = 10×体重 + 6.25×身高 - 5×年龄 + 5
   - 女性 BMR = 10×体重 + 6.25×身高 - 5×年龄 - 161
   - TDEE = BMR × 活动系数（久坐1.2，轻活动1.375，默认取1.3）。
   - 目标热量 = TDEE + 调整值（减脂-300，重组-200，增肌+200）。
5. **蛋白质摄入**：固定推荐 1.6~2.0g × 体重kg，并换算成常见食物表述。

# 输出格式要求（必须严格遵守）
请只输出一个合法的紧凑 JSON 对象，不要输出 Markdown 代码块，不要输出任何解释或开场白。
如果字段内需要换行，请使用转义字符 \\n。JSON 必须严格符合：
{"plans":[{"bmi":"...","plan":"...","goal":"...","reason":"...","food_suggestion":"...","rest":"..."}]}

字段说明：
- bmi：BMI 数值与结论
- plan：训练计划表（可用 Markdown 表格）
- goal：短期与长期目标
- reason：计划理由
- food_suggestion：饮食建议
- rest：休息与恢复建议

# 额外约束
- 不要输出任何与 JSON 无关的内容。
- 体重kg和身高cm需代入公式计算，不得跳过。
- 所有重量建议后必须附带“可根据自身情况增减”的隐含提醒（可在表格内用“建议”字样体现）。
"""


def _extract_json_object(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("DeepSeek 未返回有效的 JSON 内容")
    return match.group(0)

async def generate_plan(plan_info:PlanIn)->BodyInfoResultSchema:
    prompt = (f"用户性别:{plan_info.gender},身高:{plan_info.height}cm,体重:{plan_info.weight}kg,年龄:{plan_info.age},特殊要求:{plan_info.demand}")
    result = await llm.ainvoke([
        ("system", System_prompt),
        ("human", prompt),
    ])
    content = result.content if isinstance(result.content, str) else str(result.content)
    return BodyInfoResultSchema.model_validate_json(_extract_json_object(content))


#测试
async def main():
    body_info=PlanIn(
        gender="男",
        height=175,
        weight=65.5,
        age=19,
        demand="我身边的器材只有哑铃，健腹轮，弹力带"
    )
    plans = await generate_plan(body_info)
    print("===== AI 健身方案 =====")
    for index, plan in enumerate(plans.plans, start=1):
        print(f"\n--- 方案 {index} ---")
        print(f"BMI: {plan.bmi}")
        print(f"\n计划表:\n{plan.plan}")
        print(f"\n目标:\n{plan.goal}")
        print(f"\n计划理由:\n{plan.reason}")
        print(f"\n饮食建议:\n{plan.food_suggestion}")
        print(f"\n休息建议:\n{plan.rest}")

if __name__ == "__main__":
    asyncio.run(main())
