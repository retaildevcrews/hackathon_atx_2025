class UploadError(Exception):
    """Base exception for upload client errors."""

class AuthError(UploadError):
    pass

class ValidationError(UploadError):
    pass

class ServerError(UploadError):
    pass
