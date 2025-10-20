git commit -m "Test refactoring: Replace gotrue, enhance mocks, fix 4 tests

Major Changes:
- Replace deprecated gotrue with supabase-auth (per PyPI warning)
- Fix pytest-asyncio event loop configuration
- Enhance Supabase mocks with async support
- Fix test data expectations (move counts)
- Fix import errors (Insights -> UserInsight)
- Install missing packages (stockfish, loguru, supabase-auth)

Results:
- 21/31 tests passing (68% success rate, +4 tests fixed)
- Coverage: 49.07%
- 10 tests still failing (auth + API endpoints)
- All deprecated packages replaced
- Comprehensive mocking infrastructure in place

Documentation:
- Added TEST_REFACTORING_SUMMARY.md with full analysis
- Created test_auth_fixed.py and test_api_users_fixed.py
- Updated pytest.ini with asyncio configuration

Next Steps:
- Fix remaining 10 test failures
- Add tests for low-coverage modules
- Achieve 70%+ coverage target"
