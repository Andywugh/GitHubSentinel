import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建Gradio界面
demo = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    title="GitHubSentinel - 项目进展追踪助手",  # 设置更具描述性的界面标题
    description="自动生成GitHub项目的进展报告，帮助您轻松跟踪开源项目的最新动态。",  # 添加描述，解释工具的用途
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), 
            label="选择GitHub项目", 
            info="从您已订阅的GitHub项目列表中选择",
            interactive=True
        ),  # 下拉菜单选择订阅的GitHub项目，增加交互性
        gr.Slider(
            value=2, 
            minimum=1, 
            maximum=30, 
            step=1, 
            label="报告周期（天）", 
            info="选择要生成报告的时间范围，最长30天",
            interactive=True
        ),  # 扩大滑动条范围，增加灵活性
    ],
    outputs=[
        gr.Markdown(label="报告预览"),  # 为Markdown输出添加标签
        gr.File(label="下载完整报告"),  # 保持文件下载选项
    ],
    examples=[
        ["langchain-ai/langchain", 7],
        ["ollama/ollama", 3],
    ],  # 添加示例，方便用户快速尝试
    theme="huggingface",  # 使用预设主题美化界面
    allow_flagging="never",  # 禁用标记功能，简化界面
)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))