class UploadError(Exception):
    """Base class for upload related errors."""

class AuthError(UploadError):
    pass

class ValidationError(UploadError):
    pass

class SizeLimitError(UploadError):
    pass

class StorageError(UploadError):
    pass
