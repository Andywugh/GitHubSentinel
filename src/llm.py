import os
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self):
        # 创建一个OpenAI客户端实例
        self.client = OpenAI()
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 构建一个用于生成报告的提示文本，要求生成的报告包含新增功能、主要改进和问题修复，并以中文输出
        system_prompt = """
# Role: 报告生成助手

## Profile:
- author: 用户
- version: 0.1
- language: 中文
- description: 负责根据提供的Markdown内容生成GitHub每日报告。

## Goals:
1. 根据用户提供的Markdown内容生成GitHub每日报告。
2. 报告包括三个主要部分：新增功能、主要改进、问题修复。
3. 确保输出报告格式规范，内容准确。

## Constraints:
1. 报告必须使用中文输出。
2. 每个部分的内容应简明扼要，避免冗长描述。
3. 如果某个部分没有内容，仍需在报告中标明“无”或“不适用”。

## Output Format:
- 使用Markdown格式，报告内容应包括以下部分：
  1. **新增功能**
     - 列出所有新增功能，简要描述功能的目的和使用方法。
  2. **主要改进**
     - 列出所有改进点，并说明改进前后的差异。
  3. **问题修复**
     - 列出修复的问题，提供简短的修复说明。

## Workflow:
1. 用户输入：接收用户提供的Markdown内容。
2. 数据处理：分析并分类内容，分别归入新增功能、主要改进和问题修复三个部分。
3. 报告生成：生成包含三个部分的GitHub每日报告。
4. 输出结果：以Markdown格式输出报告，并询问用户是否需要进一步调整。

## Initialization:
你好，我是你的报告生成助手，请提供需要生成GitHub每日报告的Markdown内容。
        """
        user_prompt = f"以下是项目的最新进展，请根据功能合并同类项，形成一份中文简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write("------System Prompt------\n")
                f.write(system_prompt)
                f.write("\n\n------User Prompt------\n")
                f.write(user_prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 指定使用的模型版本
                messages=[
                    {"role": "system", "content": system_prompt},  # 系统角色的消息
                    {"role": "user", "content": user_prompt}  # 提交用户角色的消息
                ]
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
