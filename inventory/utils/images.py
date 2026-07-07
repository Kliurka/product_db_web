import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image


def process_uploaded_image(
    image,
    size=(800, 800),
    filename_prefix="image",
    quality=85,
):
    if not image:
        return image

    img = Image.open(image)
    img = img.convert("RGB")

    width, height = img.size
    square_size = min(width, height)

    left = (width - square_size) // 2
    top = (height - square_size) // 2
    right = left + square_size
    bottom = top + square_size

    img = img.crop((left, top, right, bottom))
    img = img.resize(size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)

    slug = slugify(filename_prefix)

    if not slug:
        slug = "image"

    unique_id = uuid.uuid4().hex[:8]
    filename = f"{slug}-{unique_id}.jpg"

    return ContentFile(buffer.getvalue(), name=filename)
