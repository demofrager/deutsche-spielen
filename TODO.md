# TODO - Deutsche Spielen Webapp Specification

## 1) Product Scope
- [x] Define MVP goal: a webapp with a main menu, game selection page, and first playable game "Satzbauwuerfeln".
- [x] Keep stack simple, Python-first, maintainable, and easy to run locally.
- [x] Support future additional games with a modular backend and reusable frontend components.

## 2) Proposed Tech Stack (Easy to Maintain)
- [x] Backend: FastAPI (Python), Pydantic, Uvicorn.
- [x] Frontend: Jinja templates + HTMX + simple CSS (or lightweight JS only where needed).
- [x] Data storage for MVP: in-memory/static JSON files (no DB required yet).
- [x] Testing: Pytest for backend logic and endpoint tests.

## 3) Project Structure
- [x] Create folder layout:
  - app/
    - main.py
    - api/
      - routes_menu.py
      - routes_games.py
      - routes_satzbauwuerfeln.py
    - domain/
      - dice.py
      - satzbauwuerfeln_rules.py
      - sentence_validation.py
    - services/
      - satzbauwuerfeln_service.py
    - templates/
      - base.html
      - index.html
      - games.html
      - satzbauwuerfeln.html
    - static/
      - styles.css
      - app.js (optional)
  - tests/
    - test_dice.py
    - test_satzbauwuerfeln_api.py
    - test_satzbauwuerfeln_rules.py
  - requirements.txt
  - README.md

## 4) Domain Rules for Satzbauwuerfeln
- [x] Implement 3 numeric dice roll (1-6) where all three numbers are unique.
- [x] Map numeric dice categories:
  - 1 = Subjekt (Wer?)
  - 2 = Verb (Was tut das Subjekt?)
  - 3 = Akkusativobjekt (wen/was)
  - 4 = Dativobjekt (wem)
  - 5 = Lokalangabe (Wo)
  - 6 = Temporalangabe (Wann)
- [x] Add per-category suggestion pools (word/phrase lists).
- [x] For each rolled number, return one suggestion from the mapped category.
- [x] Implement sentence-type die with letters A-F.
- [x] Map sentence-type die:
  - A = Hauptsatz
  - B = Nebensatz
  - C = Fragesatz
  - D = Satz mit Infinitiv + zu
  - E = Perfekt oder Futur
  - F = Satz mit Possessivartikel

## 5) API Specification (MVP)
- [x] GET / -> main menu page.
- [x] GET /games -> game selection page.
- [x] GET /games/satzbauwuerfeln -> game page with controls and input box.
- [x] POST /api/games/satzbauwuerfeln/roll -> returns:
  - 3 unique numbers
  - resolved category labels
  - selected suggestion terms for each die
  - sentence-type letter A-F + sentence-type label
- [x] POST /api/games/satzbauwuerfeln/validate -> accepts student sentence and current roll context, returns provisional validation result.

## 6) Frontend Requirements
- [x] Global navigation/menu in base layout:
  - Home
  - Games
  - Satzbauwuerfeln
- [x] Games page with card/button for Satzbauwuerfeln.
- [x] Satzbauwuerfeln page:
  - Roll button
  - Display area for three dice outcomes and mapped prompts
  - Display sentence-type die outcome A-F
  - Text area for student sentence input
  - Validate button
  - Result box (for now: basic valid/invalid placeholder + feedback message)
- [x] Mobile-first responsive layout and accessible labels.

## 7) Validation Strategy (Phase 1: Basic, No Full Correction Yet)
- [x] Implement minimal checks only:
  - Non-empty sentence
  - Ends with valid punctuation (., ?, !)
  - Contains required suggestion tokens from roll (at least configurable subset)
  - Basic sentence-type heuristics by A-F (lightweight rules)
- [x] Return structured validation output:
  - is_valid: true/false
  - checks_passed: list
  - checks_failed: list
  - message: user-friendly feedback
- [x] Phase 1 complete (Phase 2 LanguageTool integration added as Milestone 5).

## 8) Phase 2: LanguageTool Grammar Integration
- [x] LanguageTool startup inlined into `scripts/run_local_toolbox.sh` (single distrobox, no separate script):
  - Start LanguageTool HTTP server on port 8081 inside the same distrobox
  - Verify connectivity before returning
- [x] Add grammar checking service (`app/services/grammar_service.py`):
  - HTTP wrapper for LanguageTool API calls
  - Parse grammar match responses into structured checks
  - Handle connection failures gracefully (fallback to Phase 1)
  - Use environment variable `LANGUAGETOOL_URL` for flexibility (default: http://localhost:8081)
- [x] Integrate grammar checks into validation pipeline (`app/domain/sentence_validation.py`):
  - Add `grammar_errors` check type
  - Combine Phase 1 + Phase 2 results
  - Grammar errors inform feedback but don't auto-fail
- [x] Update API response (`app/api/routes_satzbauwuerfeln.py`):
  - Optional: Add `grammar_errors` field to `ValidateOut`
  - Include grammar hints in feedback message
- [x] Create k8s LanguageTool deployment (`k8s/languagetool-deployment.yaml`):
  - LanguageTool service discoverable via k8s DNS
  - Separate pod from Deutsche Spielen app
  - Resource limits appropriate for JVM footprint
- [x] Update app startup (`app/main.py`):
  - Optional: Verify LanguageTool connectivity on app startup
  - Log warning if unavailable, allow graceful degradation
- [x] Add tests (`tests/test_grammar_service.py`):
  - Mock LanguageTool responses
  - Test graceful fallback when service is unavailable
  - Test grammar error integration into validation output
- [x] Add lightweight German word-order / V2 heuristic (`_word_order_heuristic` in `sentence_validation.py`):
  - Hauptsatz (A/D/E/F): finite verb must appear at token index ≤ 3
  - Fragesatz (C): finite verb must appear at token index ≤ 2
  - Nebensatz (B): finite verb must appear near the end (index ≥ len-2) when a subordinating conjunction is present
  - `word_order_hint` result surfaced in frontend with label "Satzstellung (Verbposition)"
- [x] Skip LanguageTool query when blocking failures already found (performance: avoid unnecessary HTTP call)

## 9) Data Design
- [x] Create static vocab configuration file (JSON or Python dict) for category suggestions.
- [x] Keep suggestion lists editable for teachers.
- [x] Include at least 20+ suggestions per category for useful variety.

## 10) Testing Plan
- [x] Unit tests:
  - unique 3-dice roll generation
  - category mapping and suggestion retrieval
  - sentence-type mapping A-F
  - basic validation heuristics
  - word order heuristic (V2, Nebensatz, Fragesatz — pass and fail cases per type)
  - LanguageTool early-exit (grammar check skipped when blocking failures present)
- [x] API tests:
  - roll endpoint response schema
  - validate endpoint response schema
  - error cases (invalid payload, missing context)
- [ ] Manual UI test checklist for main user flow.

## 11) Implementation Milestones
- [x] Milestone 1: Bootstrap app skeleton and routing.
- [x] Milestone 2: Build dice domain logic + roll endpoint.
- [x] Milestone 3: Build Satzbauwuerfeln page and hook roll action.
- [x] Milestone 4: Add sentence input + validation endpoint (basic heuristics).
- [x] Milestone 5: Phase 2 LanguageTool grammar integration (advanced heuristics):
  - Local dev startup script for distrobox
  - Grammar service wrapper + k8s deployment
  - Validation pipeline integration
  - Tests with graceful fallback
- [x] Milestone 6: Add tests and stabilize UX copy.
- [x] Milestone 7: Prepare extension points for future games.

## 12) Non-Functional Requirements
- [ ] Keep code modular and documented for easy maintenance.
- [x] Keep dependencies minimal.
- [x] Add clear README run instructions.
- [x] Ensure deterministic behavior in tests (seeded randomness where needed).
- [x] LanguageTool service should be optional (graceful degradation if unavailable).
- [x] Document local dev workflow: single distrobox with in-toolbox LanguageTool startup.
- [x] Document k8s deployment: LanguageTool as separate service.

## 13) Future Enhancements (Out of MVP)
- [ ] Grammar correction with NLP/LLM assistance.
- [ ] Additional German-learning games under same menu.
