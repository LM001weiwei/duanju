"""
Sora 视频生成 Web 应用
提供网页界面来生成和管理视频
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大 16MB
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['OUTPUT_FOLDER'] = Path('outputs')

# 创建必要的目录
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频 API"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        seconds = data.get('seconds', 8)
        size = data.get('size', '1280x720')

        if not prompt:
            return jsonify({'error': '请输入视频描述'}), 400

        # 检查环境变量
        if not os.getenv('AZURE_OPENAI_API_KEY'):
            return jsonify({'error': '未配置 AZURE_OPENAI_API_KEY'}), 500

        # 创建输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = app.config['OUTPUT_FOLDER'] / timestamp
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / 'video.mp4'

        # 调用生成脚本
        cmd = [
            'python',
            '.claude/skills/gen_sora/scripts/gen_sora.py',
            prompt,
            str(output_path),
            '--seconds', str(seconds),
            '--size', size
        ]

        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            return jsonify({
                'error': '视频生成失败',
                'details': result.stderr
            }), 500

        return jsonify({
            'success': True,
            'output_path': str(output_path.relative_to(app.config['OUTPUT_FOLDER'])),
            'message': '视频生成成功！'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/concat', methods=['POST'])
def concat_videos():
    """拼接视频 API"""
    try:
        data = request.json
        input_files = data.get('inputs', [])

        if len(input_files) < 2:
            return jsonify({'error': '至少需要两个视频文件'}), 400

        # 创建输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = app.config['OUTPUT_FOLDER'] / f'concat_{timestamp}.mp4'

        # 调用拼接脚本
        cmd = [
            'python',
            '.claude/skills/concat_videos/scripts/concat_videos.py',
            str(output_path),
            *input_files
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            return jsonify({
                'error': '视频拼接失败',
                'details': result.stderr
            }), 500

        return jsonify({
            'success': True,
            'output_path': str(output_path.relative_to(app.config['OUTPUT_FOLDER'])),
            'message': '视频拼接成功！'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/videos', methods=['GET'])
def list_videos():
    """获取已生成的视频列表"""
    try:
        videos = []
        output_folder = app.config['OUTPUT_FOLDER']

        if output_folder.exists():
            for item in output_folder.rglob('*.mp4'):
                videos.append({
                    'name': item.name,
                    'path': str(item.relative_to(output_folder)),
                    'size': item.stat().st_size,
                    'created': datetime.fromtimestamp(item.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })

        return jsonify({'videos': videos})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<path:filename>')
def download_video(filename):
    """下载视频文件"""
    try:
        file_path = app.config['OUTPUT_FOLDER'] / filename
        if not file_path.exists():
            return jsonify({'error': '文件不存在'}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    config = {
        'has_api_key': bool(os.getenv('AZURE_OPENAI_API_KEY')),
        'base_url': os.getenv('AZURE_OPENAI_BASE_URL', ''),
        'model': os.getenv('SORA_MODEL', 'sora-2')
    }
    return jsonify(config)


if __name__ == '__main__':
    print('启动 Sora 视频生成 Web 应用...')
    print('访问地址: http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
