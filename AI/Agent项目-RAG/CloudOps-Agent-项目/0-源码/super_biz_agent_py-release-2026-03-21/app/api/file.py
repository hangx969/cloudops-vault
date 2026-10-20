"""文件上传接口模块"""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.vector_index_service import vector_index_service
from loguru import logger

router = APIRouter()

# 文件上传后存储的路径
UPLOAD_DIR = Path("./uploads")
# 支持的文件类型
ALLOWED_EXTENSIONS = ["txt", "md"]
# 单个文件支持最大大小
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件并自动创建向量索引

    Args:
        file: 上传的文件

    Returns:
        JSONResponse: 上传结果
    """
    try:
        # 1. 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        # 2. 规范化文件名（去除空格，处理 Windows 上传的文件）
        safe_filename = _sanitize_filename(file.filename)

        # 3. 验证文件扩展名
        file_extension = _get_file_extension(safe_filename)
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # 4. 创建上传目录
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # 5. 保存文件
        file_path = UPLOAD_DIR / safe_filename

        # 如果文件已存在，先删除旧文件（实现覆盖更新）
        if file_path.exists():
            logger.info(f"文件已存在，将覆盖: {file_path}")
            file_path.unlink()

        # 读取并保存文件内容
        content = await file.read()

        # 验证文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE} 字节）")

        file_path.write_bytes(content)

        logger.info(f"文件上传成功: {file_path}")

        # 5. 自动创建向量索引
        try:
            logger.info(f"开始为上传文件创建向量索引: {file_path}")
            vector_index_service.index_single_file(str(file_path))
            logger.info(f"向量索引创建成功: {file_path}")
        except Exception as e:
            logger.error(f"向量索引创建失败: {file_path}, 错误: {e}")
            # 注意：即使索引失败，文件上传仍然成功，只是记录错误日志

        # 6. 返回响应
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success",
                "data": {
                    "filename": safe_filename,
                    "file_path": str(file_path),
                    "size": len(content),
                },
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {e}")


@router.post("/index_directory")
async def index_directory(directory_path: str = None):
    """
    索引指定目录下的所有文件

    Args:
        directory_path: 目录路径（可选，默认使用 uploads 目录）

    Returns:
        JSONResponse: 索引结果
    """
    try:
        logger.info(f"开始索引目录: {directory_path or 'uploads'}")

        # 执行索引
        result = vector_index_service.index_directory(directory_path)

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": "success" if result.success else "partial_success",
                "data": result.to_dict(),
            },
        )

    except Exception as e:
        logger.error(f"索引目录失败: {e}")
        raise HTTPException(status_code=500, detail=f"索引目录失败: {e}")


def _get_file_extension(filename: str) -> str:
    """
    获取文件扩展名

    Args:
        filename: 文件名

    Returns:
        str: 扩展名（小写，不含点）
    """
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
        return parts[1].lower()
    return ""


def _sanitize_filename(filename: str) -> str:
    """
    规范化文件名，去除空格和特殊字符

    Args:
        filename: 原始文件名

    Returns:
        str: 规范化后的文件名
    """
    # 去除空格
    sanitized = filename.replace(" ", "_")
    # 去除其他可能导致问题的字符
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        sanitized = sanitized.replace(char, "_")
    return sanitized
