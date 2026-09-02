import os
from django.core.exceptions import ValidationError
from PIL import Image

MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}
MIN_DIMENSION = 200
MAX_DIMENSION = 5000


def validate_profile_photo(image_file):
    """
    Validate uploaded profile photo for size, format, and corruption.
    Protects against malicious file uploads and format spoofing.
    """
    # 1. Check file size
    if image_file.size > MAX_PHOTO_SIZE_BYTES:
        raise ValidationError(
            f'Image file size exceeds maximum limit of 5 MB (current: {image_file.size / (1024 * 1024):.1f} MB).'
        )

    # 2. Check extension
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'Unsupported file extension "{ext}". Allowed formats are: JPG, JPEG, PNG, WEBP.'
        )

    # 3. Verify actual image payload using Pillow
    try:
        image_file.seek(0)
        with Image.open(image_file) as img:
            img.verify()  # Verifies file integrity
            format_name = img.format
            if format_name not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError(
                    f'Invalid image format: {format_name}. Expected JPEG, PNG, or WEBP.'
                )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError('The uploaded file is not a valid or readable image.')
    finally:
        image_file.seek(0)

    # 4. Check image dimensions
    try:
        image_file.seek(0)
        with Image.open(image_file) as img:
            width, height = img.size
            if width < MIN_DIMENSION or height < MIN_DIMENSION:
                raise ValidationError(
                    f'Image resolution is too small ({width}x{height}px). Minimum is {MIN_DIMENSION}x{MIN_DIMENSION}px.'
                )
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                raise ValidationError(
                    f'Image resolution is too large ({width}x{height}px). Maximum is {MAX_DIMENSION}x{MAX_DIMENSION}px.'
                )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError('Could not process image dimensions.')
    finally:
        image_file.seek(0)
