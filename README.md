# Storyboard-to-Video

This repo is for:
- Generating/reviewing storyboards with custom agents
- Generating Sora video segments shot-by-shot from the storyboard
- Extracting the last frame from each segment (optionally used as the next shot’s reference image)
- Concatenating all segments into a final video

## Prerequisites

### 1) Python dependencies

- Python 3.11+ (recommended)

Create a venv and install dependencies in the repo root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

### 2) Azure OpenAI / Sora environment variables

Copy [.env.example](.env.example) to `.env` and fill in real values:

```dotenv
AZURE_OPENAI_API_KEY="..."
AZURE_OPENAI_BASE_URL="https://<your-resource-name>.openai.azure.com/openai/v1/"
DEPLOYMENT_NAME="sora-2"
```

## Run the end-to-end workflow in VS Code with `/genvideo`

This repo includes a Copilot Chat prompt file: [.github/prompts/genvideo.prompt.md](.github/prompts/genvideo.prompt.md)

In VS Code Copilot Chat, run (this is your example):

```
/genvideo Story: On a rainy night after work, a person is stopped in their tracks by an almost inaudible “meow” from an alley; they bring home a shivering, chilled kitten and, through a series of careful, gentle care, help it stop being afraid—finally rewarded with a steady, peaceful purr. Each shot is 8 seconds. 5 shots total. Style: cinematic film look. Resolution: 720x1280.
```

It follows the workflow described in the prompt:
- Calls the custom agents to generate a storyboard (saved to `outputs/<topic>/storyboard.md`)
- Reviews the storyboard and iterates
- Generates `shot_<n>.mp4` shot-by-shot, and also saves `frame_<n>.png`
- Concatenates all shots into a final video

Custom agents are defined in:
- [.github/agents/storyboard-designer.agent.md](.github/agents/storyboard-designer.agent.md)
- [.github/agents/storyboard-reviewer.agent.md](.github/agents/storyboard-reviewer.agent.md)
