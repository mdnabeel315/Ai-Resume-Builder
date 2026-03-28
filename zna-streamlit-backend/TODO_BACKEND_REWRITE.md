# Backend Rewrite for Production Robustness

Scope confirmed. Steps:

1. [x] Add pydantic validation + structlog to requirements.txt
2. [x] Create backend/validators.py (input schemas)
3. [ ] Enhance llm_service.py (circuit breaker, async, better caching)
4. [x] Add backend/error_handler.py (global interceptors)
5. [ ] Update all services with timeouts/validation
6. [ ] Enhance state_manager.py (locking/versioning)
7. [ ] Update app.py (error boundaries)
8. [ ] Test with load/stress
