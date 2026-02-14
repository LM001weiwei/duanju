# 环境配置与运行指南

## 快速开始

### 1. 安装 Python 依赖

在项目根目录下运行：

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填写你的配置信息：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下内容：

```env
# Azure OpenAI API 配置
AZURE_OPENAI_API_KEY="你的 API Key"
AZURE_OPENAI_BASE_URL="https://你的资源名称.openai.azure.com/openai/v1/"

# Sora 模型配置
SORA_MODEL="sora-2"
DEPLOYMENT_NAME="sora-2"

# 轮询间隔（秒）
SORA_POLL_SECONDS="20"
```

### 3. 运行 Web 应用

```bash
python app.py
```

应用将在 http://localhost:5000 启动。

在浏览器中打开该地址，即可使用图形界面生成视频！

## 功能说明

### Web 界面功能

1. **视频生成**
   - 输入视频描述（提示词）
   - 设置视频时长（1-60秒）
   - 选择分辨率（支持多种比例）
   - 点击"生成视频"按钮

2. **视频管理**
   - 查看已生成的所有视频
   - 下载视频文件
   - 查看视频元信息（大小、创建时间等）

3. **配置状态**
   - 实时显示 API 配置状态
   - 检查环境变量是否正确设置

### 命令行使用（原始方式）

#### 生成单个视频

```bash
python .claude/skills/gen_sora/scripts/gen_sora.py "视频描述" outputs/video.mp4 --seconds 8 --size 1280x720
```

#### 拼接多个视频

```bash
python .claude/skills/concat_videos/scripts/concat_videos.py outputs/final.mp4 outputs/video1.mp4 outputs/video2.mp4
```

#### 提取最后一帧

```bash
python .claude/skills/get_last_frame/scripts/get_last_frame.py outputs/video.mp4 outputs/frame.png
```

## 项目结构

```
duanju/
├── app.py                      # Flask Web 应用主文件
├── templates/                  # HTML 模板
│   └── index.html             # 主页面
├── outputs/                    # 生成的视频输出目录
├── uploads/                    # 上传文件目录
├── .claude/                    # Claude 技能配置
│   └── skills/
│       ├── gen_sora/          # Sora 视频生成
│       ├── concat_videos/     # 视频拼接
│       └── get_last_frame/    # 帧提取
├── .env                        # 环境变量配置（需手动创建）
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖
├── Claude.md                  # 项目配置说明
└── README.md                  # 项目说明文档
```

## 常见问题

### 1. 连接 GitHub 失败

如果在国内网络环境下，可能需要配置代理：

```bash
# 设置 Git 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 2. API Key 未配置

确保 `.env` 文件中正确配置了 `AZURE_OPENAI_API_KEY` 和 `AZURE_OPENAI_BASE_URL`。

### 3. ffmpeg 未安装

视频拼接功能需要 ffmpeg。如果未安装，可以：
- 安装系统 ffmpeg
- 或者依赖会自动使用 `imageio-ffmpeg` 包提供的 ffmpeg

### 4. 视频生成很慢

这是正常现象，Sora 视频生成通常需要几分钟时间。请耐心等待，Web 界面会显示实时状态。

## 技术栈

- **后端**: Python + Flask
- **前端**: HTML + CSS + JavaScript（原生）
- **视频处理**: OpenAI Sora API + ffmpeg
- **依赖管理**: pip + requirements.txt

## 下一步

- ✅ 配置环境变量
- ✅ 安装依赖
- ✅ 运行 Web 应用
- 🎬 开始生成你的第一个视频！

## 获取帮助

如有问题，请查看：
- [README.md](README.md) - 项目说明
- [Claude.md](Claude.md) - 项目配置规范
- [.env.example](.env.example) - 环境变量示例

---

祝你使用愉快！🎉
