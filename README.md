# chaoxing-exam-next-for-by-chrome
简介 📖
本项目是一个基于AI技术的超星学习通自动考试助手，原作者是https://github.com/myxuebi/chaoxingStudy-exam，原作者好久没更新了，旨在为用户提供一个便捷的考试辅助工具。通过对接通义千问，兼容openai格式调用的模型或Ollama等AI模型，程序能够自动完成考试中的单选题、多选题、填空题和判断题。
免责声明 ⚠️
请注意：
本项目仅供娱乐和学习交流使用。 🎮
严禁将本项目用于任何形式的考试舞弊或其他违法违规行为。 🚫
使用本程序所产生的一切后果由使用者自行承担。 💡
开发者不对任何因使用本项目而产生的法律责任负责。 ⚖️
使用教程
一、基础环境准备（全新电脑必做）
1. 安装Python 3.10（关键步骤）
为什么必须3.10+：项目使用sys.stdout.reconfigure()等新特性，旧版本不兼容

下载安装包：

访问Python官网
选择 Windows installer (64-bit)（建议3.10.12版本）
关键安装设置：

勾选 ✅ Add Python to PATH（必须！）
勾选 ✅ Install launcher for all users
点击 Customize installation
在Optional Features页面：全部勾选
在Advanced Options页面：
勾选 ✅ Install for all users
勾选 ✅ Precompile standard library
设置安装路径为：C:\Python310（避免中文路径问题）
验证安装：

cmd
python --version
# 应显示 Python 3.10.x
pip --version
# 应显示 pip 2x.x.x
二、该项目程序集成了chrome，无需配置
三、获取项目代码
1. 下载项目源码
cmd
cd d:\
git clone https://github.com/your-repo/chaoxingStudy-exam-main.git
若未安装Git，请直接下载ZIP包：

访问项目GitHub页面
点击绿色"Code"按钮 → "Download ZIP"
解压到d:\chaoxingStudy-exam-main
2. 验证目录结构
确保以下关键文件存在：

d:\chaoxingStudy-exam-main\
├── main.py                # 核心脚本
├── chromedriver\         # 必须包含
│   ├── chrome.exe        # 从Chrome安装目录复制
│   ├── chromedriver.exe  # 下载的驱动
│   └── chrome++.ini      # 手动创建的配置
四、安装Python依赖库
1. 升级pip（重要！）
cmd
python -m pip install --upgrade pip
2. 安装必需库
cmd
cd d:\chaoxingStudy-exam-main
pip install selenium
pip install requests
pip install dashscope
pip install openai
pip install ollama
pip install webdriver-manager

五、AI服务配置（三选一）
方案A：通义千问（推荐新手）
注册账号：

访问DashScope控制台
使用支付宝/淘宝扫码注册
获取API Key：

右上角头像 → API-KEY管理
点击创建API-KEY
复制生成的Key（格式：sk-xxxxxxxx）
方案B：OpenAI兼容服务（如SiliconFlow）
注册SiliconFlow
在API Keys页面创建Key
记录：
API Endpoint: https://api.siliconflow.com/v1/chat/completions
模型名称: Qwen/Qwen3-VL-32B-Instruct
方案C：本地Ollama（需高性能电脑）
下载安装Ollama
安装后运行：
cmd
ollama serve  # 保持窗口开启
ollama pull qwen2
六、首次运行配置
1. 防火墙设置（重要！）
避免被安全软件拦截
先关闭防火墙

cmd
cd d:\chaoxingStudy-exam-main
python test_env.py
成功标志：弹出百度页面后自动关闭，命令行显示"浏览器启动成功！"

七、正式使用指南
1. 交互式运行（推荐首次使用）
直接点击main.py即可
按提示输入：

请输入超星账号: [您的学号]
请输入超星密码: [您的密码]
请输入进入考试页面后的网址: [考试URL]
答案获取方式：
  1. 本地ollama 
  2. 通义千问 
  3. OpenAI兼容服务
> 2  # 选择通义千问
请输入通义千问api token：sk-xxxxxxxx
2. 命令行参数运行（适合重复使用）
cmd
python main.py ^
  --username 20230001 ^
  --password YourPassword123 ^
  --url "https://mooc.chaoxing.com/exam/test/reVersionTestStartNew" ^
  --api-type tongyi ^
  --tongyi-api sk-xxxxxxxx
八、常见问题解决方案
❌ 问题1：ModuleNotFoundError: No module named 'selenium'
原因：依赖未正确安装
解决：

cmd
pip uninstall -y selenium
pip install selenium==4.15.2 --trusted-host pypi.org
❌ 问题2：'chromedriver.exe' executable needs to be in PATH
原因：驱动路径配置错误
检查：

确认d:\chaoxingStudy-exam-main\chromedriver\chromedriver.exe存在
在main.py中搜索executable_path，确认路径为：
python
os.path.join(chromedriver_dir, 'chromedriver.exe')
❌ 问题3：浏览器启动后立即关闭
原因：缺少--no-sandbox参数
修复：在main.py第38行附近添加：

python
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')  # 新增此行
❌ 问题4：图片题处理失败
原因：图床服务限制
临时解决：

打开main.py
搜索url = "https://image.myxuebi.top/api/v1/upload"
替换为备用图床（如sm.ms）：
python
url = "https://sm.ms/api/v2/upload"
九、高级配置技巧
1. 永久保存配置（避免重复输入）
创建config.bat在项目目录：

bat
@echo off
python main.py ^
  --username %1 ^
  --password %2 ^
  --url "https://mooc.chaoxing.com/exam/test/reVersionTestStartNew" ^
  --api-type tongyi ^
  --tongyi-api sk-xxxxxxxx
使用方式：

cmd
config.bat 20230001 YourPassword123


十、安全与合规提醒
仅限学习用途：本工具设计用于模拟练习环境，请勿在正式考试中使用
数据安全：
API Key不要提交到GitHub
考试结束后及时关闭浏览器
性能建议：
填空题建议人工复核
多选题答案可能不完整
运行前关闭其他Chrome实例
希望项目原作者看到我的项目后联系我
