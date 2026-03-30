# TODO - Deutsche Spielen Webapp Specification

## 1) Product Scope
- [ ] Define MVP goal: a webapp with a main menu, game selection page, and first playable game "Satzbauwuerfeln".
- [ ] Keep stack simple, Python-first, maintainable, and easy to run locally.
- [ ] Support future additional games with a modular backend and reusable frontend components.

## 2) Proposed Tech Stack (Easy to Maintain)
- [ ] Backend: FastAPI (Python), Pydantic, Uvicorn.
- [ ] Frontend: Jinja templates + HTMX + simple CSS (or lightweight JS only where needed).
- [ ] Data storage for MVP: in-memory/static JSON files (no DB required yet).
- [ ] Testing: Pytest for backend logic and endpoint tests.

## 3) Project Structure
- [ ] Create folder layout:
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
- [ ] Implement 3 numeric dice roll (1-6) where all three numbers are unique.
- [ ] Map numeric dice categories:
  - 1 = Subjekt (Wer?)
  - 2 = Verb (Was tut das Subjekt?)
  - 3 = Akkusativobjekt (wen/was)
  - 4 = Dativobjekt (wem)
  - 5 = Lokalangabe (Wo)
  - 6 = Temporalangabe (Wann)
- [ ] Add per-category suggestion pools (word/phrase lists).
- [ ] For each rolled number, return one suggestion from the mapped category.
- [ ] Implement sentence-type die with letters A-F.
- [ ] Map sentence-type die:
  - A = Hauptsatz
  - B = Nebensatz
  - C = Fragesatz
  - D = Satz mit Infinitiv + zu
  - E = Perfekt oder Futur
  - F = Satz mit Possessivartikel

## 5) API Specification (MVP)
- [ ] GET / -> main menu page.
- [ ] GET /games -> game selection page.
- [ ] GET /games/satzbauwuerfeln -> game page with controls and input box.
- [ ] POST /api/games/satzbauwuerfeln/roll -> returns:
  - 3 unique numbers
  - resolved category labels
  - selected suggestion terms for each die
  - sentence-type letter A-F + sentence-type label
- [ ] POST /api/games/satzbauwuerfeln/validate -> accepts student sentence and current roll context, returns provisional validation result.

## 6) Frontend Requirements
- [ ] Global navigation/menu in base layout:
  - Home
  - Games
  - Satzbauwuerfeln
- [ ] Games page with card/button for Satzbauwuerfeln.
- [ ] Satzbauwuerfeln page:
  - Roll button
  - Display area for three dice outcomes and mapped prompts
  - Display sentence-type die outcome A-F
  - Text area for student sentence input
  - Validate button
  - Result box (for now: basic valid/invalid placeholder + feedback message)
- [ ] Mobile-first responsive layout and accessible labels.

## 7) Validation Strategy (Phase 1: Basic, No Full Correction Yet)
- [ ] Implement minimal checks only:
  - Non-empty sentence
  - Ends with valid punctuation (., ?, !)
  - Contains required suggestion tokens from roll (at least configurable subset)
  - Basic sentence-type heuristics by A-F (lightweight rules)
- [ ] Return structured validation output:
  - is_valid: true/false
  - checks_passed: list
  - checks_failed: list
  - message: user-friendly feedback
- [ ] Defer grammar-correction engine to later phase.

## 8) Data Design
- [ ] Create static vocab configuration file (JSON or Python dict) for category suggestions.
- [ ] Keep suggestion lists editable for teachers.
- [ ] Include at least 20+ suggestions per category for useful variety.

## 9) Testing Plan
- [ ] Unit tests:
  - unique 3-dice roll generation
  - category mapping and suggestion retrieval
  - sentence-type mapping A-F
  - basic validation heuristics
- [ ] API tests:
  - roll endpoint response schema
  - validate endpoint response schema
  - error cases (invalid payload, missing context)
- [ ] Manual UI test checklist for main user flow.

## 10) Implementation Milestones
- [x] Milestone 1: Bootstrap app skeleton and routing.
- [x] Milestone 2: Build dice domain logic + roll endpoint.
- [x] Milestone 3: Build Satzbauwuerfeln page and hook roll action.
- [x] Milestone 4: Add sentence input + validation endpoint (basic heuristics).
- [ ] Milestone 5: Add tests and stabilize UX copy.
- [ ] Milestone 6: Prepare extension points for future games.

## 11) Non-Functional Requirements
- [ ] Keep code modular and documented for easy maintenance.
- [ ] Keep dependencies minimal.
- [ ] Add clear README run instructions.
- [ ] Ensure deterministic behavior in tests (seeded randomness where needed).

## 12) Future Enhancements (Out of MVP)
- [ ] Teacher dashboard to manage vocabulary sets.
- [ ] Student accounts and progress tracking.
- [ ] Grammar correction with NLP/LLM assistance.
- [ ] Additional German-learning games under same menu.
