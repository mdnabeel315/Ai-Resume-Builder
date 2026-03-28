"""
Global error handling for production resilience.
Streamlit context-aware error pages + logging.
"""

import streamlit as st
import structlog
import traceback
from typing import Callable, Any

logger = structlog.get_logger()

class BackendErrorHandler:
    """Central error interceptor for all backend services."""
    
    def __init__(self):
        self.error_count = 0
        self.max_errors_per_minute = 5
        
    def intercept(self, func: Callable) -> Callable:
        """Decorator: Wrap service calls with error handling."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.error_count += 1
import time
error_id = f"ERR-{int(time.time())}-{self.error_count}"
                logger.error(
                    "Backend service failed",
                    func=func.__name__,
                    error=str(e),
                    error_id=error_id,
                    traceback=traceback.format_exc(),
                )
                
                # Circuit breaker: pause after max errors
                if self.error_count >= self.max_errors_per_minute:
                    st.error("🚧 Service temporarily unavailable - too many errors. Please retry in 1 min.")
                    st.stop()
                
                # User-friendly message
                st.error(f"⚠️ Backend error (ID: {error_id}). Please try again.")
                logger.warning("Operation failed - user notified", error_id=error_id)
                return None
        return wrapper
    
    def safe_llm_call(self, llm_func: Callable, *args, **kwargs) -> Any:
        """Specialized LLM call wrapper with fallback."""
        try:
            return llm_func(*args, **kwargs)
        except Exception as e:
            logger.error("LLM call failed with fallback", error=str(e))
            return self._llm_fallback()
    
    def _llm_fallback(self):
        """Static fallback response for LLM failures."""
        return {
            "name": "Fallback Resume",
            "summary": "Resume generation temporarily unavailable. Please try again shortly.",
            "skills": {"technical": [], "soft": []},
            "experience": [],
            "education": [],
            "ats_score": 0,
            "template_style": "Standard Corporate"
        }

# Global instance
error_handler = BackendErrorHandler()

# Usage:
# @error_handler.intercept
# def risky_service():
#     ...
"""

