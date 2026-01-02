from typing import Optional
from google.api_core import exceptions as gexc

class GoogleAPIChecker:
  @staticmethod
  def extract_staus_code(error: Exception) -> Optional[int]:
    """
    Extract HTTP-like status code from Google API exception.
    Link HTTP status codes: https://docs.cloud.google.com/web-risk/docs/status-codes
    """
    
    if isinstance(error, gexc.ResourceExhausted):
      return 429
    if isinstance(error, gexc.PermissionDenied):
      return 403
    if isinstance(error, gexc.Unauthorized):
      return 401
    if isinstance(error, gexc.InvalidArgument):
      return 400
    if isinstance(error, gexc.NotFound):
      return 404
    if isinstance(error, gexc.InternalServerError):
      return 500
    if isinstance(error, gexc.ServiceUnavailable):
      return 503
    if isinstance(error, gexc.DeadlineExceeded):
      return 504

    return None
  
  @staticmethod
  def should_rotate_key(status_code: int) -> bool:
    """
    Only rotate key if the error relates to key exhaustion or quota exhaustion.
    """
    return status_code in {403, 429}