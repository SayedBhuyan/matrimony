# Matrimony Implementation Task Tracker

## Phase 1 — Foundation (COMPLETED ✅)
- `[x]` Git init + `.gitignore`
- `[x]` Directory structure (`apps/`, `templates/`, `static/`, `media/`, `requirements/`, `tests/`)
- `[x]` `.env` + `.env.example`
- `[x]` Requirements files + install dependencies
- `[x]` Split settings (`base.py` / `development.py` / `production.py`)
- `[x]` `apps.core` app (shared utilities, template tags)
- `[x]` `apps.accounts` app (custom User model with UUID PK, manager, admin)
- `[x]` First migration applied cleanly
- `[x]` Authentication views + forms (register, login, logout, password reset)
- `[x]` Base template + CSS design system (Vivaha theme)
- `[x]` Landing page + dashboard template
- `[x]` Navigation + responsive layout + flash messages JS
- `[x]` Auth templates (register, login, password reset complete suite)
- `[x]` Unit test suite for Custom User model, Manager, and Auth views (18 tests passing)

---

## Phase 2 — Profiles & Photos (COMPLETED ✅)
- `[x]` Create `apps.profiles` app and register in `INSTALLED_APPS`
- `[x]` Define `Profile` model with UUID PK, demographic, and basic matrimonial attributes
- `[x]` Define normalized detail models:
  - `EducationDetail`
  - `ProfessionDetail`
  - `FamilyDetail`
  - `LifestyleDetail`
  - `PartnerPreference`
- `[x]` Define `ProfilePhoto` model with isolated media paths and primary photo logic
- `[x]` Implement image validator (MIME-type check, 5MB max size limit, Pillow dimensions & corruption verify)
- `[x]` Implement Profile Completion Engine (weighted sections & field recommendations)
- `[x]` Build Forms for Profile, Education, Profession, Family, Lifestyle, Partner Preferences, and Photos
- `[x]` Build Profile Views (Onboarding setup, Multi-tab editor, Public Detail View, My Profile View, Photo Manager)
- `[x]` Build Profile Templates with modern, elegant UI
- `[x]` Register Profile models in Django Admin with photo previews and inlines
- `[x]` Write automated unit tests for Profile models, completion engine, validators, and views (33 total tests passing)

---

## Phase 3 — Discovery & Matching (COMPLETED ✅)
- `[x]` Create `apps.discovery` app
- `[x]` Search & Filter views (Age, Religion, Caste, Location, Education, Profession, Diet)
- `[x]` Pluggable match scoring engine (`SimplePreferenceScorer`)
- `[x]` Profile card components & paginated discovery browsing
- `[x]` Fixed BooleanFilter bug causing empty results
- `[x]` All tests passing (40/40)

---

## Phase 4 — Connections & Interactions (COMPLETED ✅)
- `[x]` Create `apps.connections` app and register in `INSTALLED_APPS`
- `[x]` Define `Interest` model with status workflow (pending/accepted/rejected/cancelled/withdrawn)
- `[x]` Define `Favorite` model for shortlisting profiles
- `[x]` Define `Block` model for user blocking
- `[x]` Define `Report` model for trust & safety reporting
- `[x]` Create migrations and apply to database
- `[x]` Implement views: send_interest, accept_interest, reject_interest, cancel_interest
- `[x]` Implement views: received_interests, sent_interests
- `[x]` Implement views: add_favorite, remove_favorite, favorites_list
- `[x]` Register models in Django Admin
- `[x]` Create HTML templates for interests and favorites views
- `[x]` Add block and report functionality views
- `[x]` Implement notification integration when interests are sent/accepted
- `[x]` Full validation of connection and messaging flows before moving to Phase 5

### Phase 4 Completion Notes
- Interest sending, accepting, rejecting, and cancelling all work end-to-end.
- Favorite add/remove flows are active and mobile-friendly.
- Users can block or report profiles directly from the profile detail view.
- Connection actions are working in the UI and covered by automated Django tests.
- Discover cards and profile detail actions use the shared AJAX interaction layer.
- Interest and favorite actions complete without page reloads.
- Profile detail layout is responsive across phone, tablet, and desktop widths.

---

## Phase 5 — Communication & Notifications (IN PROGRESS 🚀)
- `[x]` Conversations & Messaging (gated by mutual interest)
- `[x]` Send messages with inline AJAX updates and no raw JSON responses
- `[x]` In-app notification system (creation and notifications page)
- `[x]` Unread message counts
- `[x]` Notification badge and read/unread interactions
- `[x]` Notifications automatically marked read when opened

### Phase 5 Completion Notes
- Conversations show member names from matrimonial profiles instead of email addresses.
- Message history stays in an independently scrolling thread while the composer remains visible.
- Sending messages, accepting interests, and notification read actions update without page reloads.
- Notification pages clear unread state automatically without requiring repeated clicks.
- Message composer submits on Enter and supports Shift+Enter for line breaks.

### Development Demo Data
- `[x]` Reset development data and seeded 25 complete Bangladeshi profiles with generated approved photos.

---

## Phase 6 — Trust, Safety & Moderation (Upcoming)
- `[ ]` Admin moderation queue
- `[x]` Privacy & visibility enforcement for blocked users in discovery
- `[x]` Unblock blocked profiles from the in-app blocked profiles page
- `[x]` Blocked profiles moved to dashboard quick actions instead of the main menu

### UI Completion Notes
- Profile editing uses a single-column mobile layout with horizontally scrollable section tabs.
- Dashboard activity cards for interests, accepted connections, and unread messages are clickable.
- Blocked profiles are managed from Dashboard > Quick Actions.
- Notifications are marked read automatically when the notifications page opens.
- Profile editor controls and spacing are optimized for phone widths.

---

## Phase 7 — Production Readiness (Upcoming)
- `[ ]` Comprehensive test suite
- `[ ]` Security hardening & documentation
