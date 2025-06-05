"""Endpoints for uploading, updating, retrieving, and deleting user avatars."""

from pathlib import Path
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import SessionLocal

router = APIRouter(prefix="/avatar", tags=["Avatar"])


@router.put("/", status_code=200)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Upload or replace the user's avatar.

    Args:
        avatar (UploadFile): The image file.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: If the file is not an image or exceeds size limit.

    Returns:
        dict: Success message.
    """
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")

    max_size = 10 * 1024 * 1024  # 10 MB
    content = await avatar.read()
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="File size exceeds 10 MB limit.")

    avatar.file.seek(0)
    try:
        with Image.open(avatar.file) as img:
            width, height = img.size
            max_dim = 512

            if width > max_dim or height > max_dim:
                if width > height:
                    new_width = max_dim
                    new_height = int((new_width / width) * height)
                elif height > width:
                    new_height = max_dim
                    new_width = int((new_height / height) * width)
                else:
                    new_width = new_height = max_dim
                img = img.resize((new_width, new_height), Image.LANCZOS)

            save_path = Path(f"./avatars/{current_user.id}.png")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path, format="PNG")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {exc}") from exc

    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    user.avatar = f"avatars/{current_user.id}.png"
    db.commit()
    db.close()

    return {"message": "Avatar updated successfully."}


@router.delete("/", status_code=200)
def delete_avatar(current_user: User = Depends(get_current_user)) -> dict:
    """
    Delete the current user's avatar.

    Args:
        current_user (User): Authenticated user.

    Raises:
        HTTPException: If avatar file is missing.

    Returns:
        dict: Success message.
    """
    avatar_path = Path(f"./avatars/{current_user.id}.png")
    if not avatar_path.exists():
        raise HTTPException(status_code=404, detail="Avatar not found.")

    avatar_path.unlink()

    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    user.avatar = None
    db.commit()
    db.close()

    return {"message": "Avatar deleted successfully."}


@router.get("/{image_name}", response_class=FileResponse)
def get_avatar_image(image_name: str) -> FileResponse:
    """
    Retrieve a specific avatar image.

    Args:
        image_name (str): Image filename.

    Raises:
        HTTPException: If image not found.

    Returns:
        FileResponse: Image file.
    """
    file_path = Path(f"./avatars/{image_name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Avatar image not found.")

    return FileResponse(file_path)
