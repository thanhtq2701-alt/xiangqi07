"""Content version used to let browsers cache static files safely."""
import hashlib


def content_version(raw):
    """Return an 8-character version for file bytes.

    Git may check text files out with CRLF on Windows while Production has LF,
    so line endings are normalized: the same file gets the same version on both.
    """
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()[:8]
