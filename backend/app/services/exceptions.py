RESUME_NOT_VALID_MESSAGE = (
    "Uploaded document does not appear to be a resume. "
    "Please try again by uploading your resume."
)


class ResumeValidationError(Exception):
    """Raised when uploaded file is not a valid resume."""

    def __init__(self, message: str = RESUME_NOT_VALID_MESSAGE):
        self.message = message
        super().__init__(message)
