
import { GoogleGenAI } from "@google/genai";
import { CleanPostData } from "../types";

export const analyzeAccount = async (posts: CleanPostData[]) => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
  
  // Prepare data context - using a substantial sample for deep analysis
  const contextData = posts.slice(0, 200).map((p) => ({
    row: p.id,
    title: p.title,
    likes: p.likes
  }));

  const prompt = `
你是一位拥有10年经验的小红书顶级运营操盘手，目前在一家全球顶级社交媒体咨询公司担任策略合伙人。
请针对以下笔记数据，提交一份具有咨询公司水准的《账号战略审计报告》。

数据上下文 (前 200 条):
${JSON.stringify(contextData)}

### 输出规范 (结构化呈现要求):

1. **第一部分：人设资产与定位审计 (The Persona Audit)**
   - 使用 Markdown 二级标题。
   - 分析流量层级（计算中位数并归类）。
   - 定义人设标签（例如：#高客单美学、#知识增量型）。
   - 描述内容赛道细分及受众画像。

2. **第二部分：全周期增长曲线复盘 (The Growth Trajectory)**
   - 识别至少一个“关键爆发节点”或“风格转型期”。
   - 引用具体的行号（例如：从第 45 行开始...）。
   - 分析博主是如何从“原始内容”向“标准化产出”进化的。

3. **第三部分：病毒式传播基因拆解 (Viral Logic Extraction)**
   - 深度拆解 Top 3 爆款。
   - 总结其独有的“标题钩子”与“选题冲突点”。
   - 特别注意：点名批评那些点赞数与标题夸张程度不符的“标题党”笔记。

4. **第四部分：战略执行路线图 (Actionable Strategy)**
   - 提供 3 条一针见血的执行建议。
   - 每条建议包含：核心动作、预期效果、避坑提示。

### 语气风格：
- 专业、犀利、极具商业洞察力。
- 拒绝废话，多用数据支撑。
- 使用适当的 Emoji 增强可读性 (📊, 🚀, 💡, 🚩)。
- 引用数据时必须注明 (对应表格第 X 行)。
`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-flash-preview',
    contents: prompt,
    config: {
      temperature: 0.3, // Lower temperature for more analytical consistency
      topK: 40,
      topP: 0.95
    }
  });

  return response.text;
};
