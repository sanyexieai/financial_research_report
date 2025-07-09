@echo off
echo === 安装GPU版本的金融研究报告系统 ===

REM 检查CUDA是否可用
echo 检查CUDA环境...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo NVIDIA驱动已安装
    nvidia-smi
) else (
    echo 警告: 未检测到NVIDIA驱动，请先安装NVIDIA驱动
    echo 参考: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/
)

REM 检查Python版本
echo 检查Python版本...
python --version

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv_gpu
call venv_gpu\Scripts\activate.bat

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装PyTorch GPU版本
echo 安装PyTorch GPU版本...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

REM 安装其他依赖
echo 安装其他依赖...
pip install -r requirements_gpu.txt

REM 测试GPU可用性
echo 测试GPU可用性...
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU数量: {torch.cuda.device_count()}') if torch.cuda.is_available() else None"

echo === 安装完成 ===
echo 使用方法:
echo 1. 激活虚拟环境: venv_gpu\Scripts\activate.bat
echo 2. 复制环境变量: copy env_example_gpu.txt .env
echo 3. 编辑.env文件，设置你的API密钥
echo 4. 运行测试: python test_gpu_rag.py
echo 5. 启动PostgreSQL: docker-compose up -d
echo 6. 运行研报生成: python macro_workflow_postgres.py

pause 