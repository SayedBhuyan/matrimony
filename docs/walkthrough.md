# Walkthrough — Foundation & Matrimonial Profiles (Phases 1 & 2)

## 1. Inspection Summary & Discovery
Upon inspecting the repository:
- The project was initialized with Django 6.1 on Python 3.14.
- `apps.accounts` custom `User` model, authentication templates, and initial migration were established.
- Dependencies including `Pillow`, `django-filter`, `python-dotenv`, and `django-debug-toolbar` were installed in the virtual environment.

---

## 2. Phase 1: Foundation & Authentication (Completed ✅)
- **Custom User Model ([models.py](file:///c:/Users/user/code/projects/matrimony/apps/accounts/models.py))**:
  - UUID Primary Key for non-sequential IDs and IDOR protection.
  - Normalized email-based authentication (no username required).
  - Extended fields: `phone`, `is_email_verified`, `last_activity`, `deactivated_at`.
- **Authentication Flows ([views.py](file:///c:/Users/user/code/projects/matrimony/apps/accounts/views.py))**:
  - Registration with automatic password validation and auto-login upon creation.
  - Custom login with email, and custom logout.
  - Full password reset suite with styled templates and console email backend in dev.
- **Base UI Design System ([main.css](file:///c:/Users/user/code/projects/matrimony/static/css/main.css))**:
  - Warm rose & gold color palette, glassmorphism header, responsive layout.
  - Interactive JavaScript for mobile navigation, auto-dismissing alerts, and scroll effects ([main.js](file:///c:/Users/user/code/projects/matrimony/static/js/main.js)).

---

## 3. Phase 2: Matrimonial Profiles & Media (Completed ✅)
- **Normalized Data Architecture ([models.py](file:///c:/Users/user/code/projects/matrimony/apps/profiles/models.py))**:
  - `Profile`: UUID PK, `OneToOneField` with User, demographic details, religious & cultural backgrounds, location, visibility levels, dynamic `age`, `height_formatted`, and `primary_photo` properties.
  - `EducationDetail`: Highest education, degrees, institution, field of study.
  - `ProfessionDetail`: Occupation, industry, employer, income range, visibility toggle.
  - `FamilyDetail`: Family type, values, status, parents' occupations, siblings, location.
  - `LifestyleDetail`: Dietary preferences, smoking/drinking habits, hobbies, spoken languages.
  - `PartnerPreference`: Age & height ranges, preferred marital status, religion, mother tongue, education, location, notes.
  - `ProfilePhoto`: Secure media path (`profile_photos/<user_id>/<uuid>.ext`), primary photo auto-selection, visibility modes, and moderation status.
- **Image Security Validator ([validators.py](file:///c:/Users/user/code/projects/matrimony/apps/profiles/validators.py))**:
  - 5 MB file size limit enforcement.
  - Extension whitelist (`.jpg`, `.jpeg`, `.png`, `.webp`).
  - Pillow image verification to prevent file corruption, memory exhaustion, and format spoofing.
- **Profile Completion Engine ([services.py](file:///c:/Users/user/code/projects/matrimony/apps/profiles/services.py))**:
  - Declarative weighted scoring system (100 total points).
  - Breakdown by section (Basic, Photos, Education, Profession, Family, Lifestyle, Preferences).
  - Actionable recommendation list for missing fields.
- **Views & UI ([views.py](file:///c:/Users/user/code/projects/matrimony/apps/profiles/views.py))**:
  - `profile_setup`: Initial onboarding view.
  - `profile_edit`: Multi-tabbed editor with real-time profile completion progress meter.
  - `photo_upload` & `photo_delete` / `photo_set_primary`: Secure photo management with IDOR checks.
  - `my_profile`: Private preview for account owners.
  - `profile_detail`: Public profile view enforcing privacy and redirection with `?next=` handling.
- **Django Admin Integration ([admin.py](file:///c:/Users/user/code/projects/matrimony/apps/profiles/admin.py))**:
  - Profile inline editing for all detail models.
  - Avatar thumbnail previews and photo moderation controls.

---

## 4. Test Verification
Ran the automated test suite across all apps:
```powershell
.\venv\Scripts\python.exe manage.py test
```
**Results:**
```
Ran 33 tests in 49.127s
OK
Found 33 test(s).
System check identified no issues (0 silenced).
```

### Key Test Coverage:
1. **Accounts (`apps.accounts.tests`)**:
   - `UserModelTests`: User creation, normalization, missing email validation, superuser permissions.
   - `AuthViewsTests`: Registration, duplicate prevention, password mismatch, login, logout, password reset.
   - `CoreViewsTests`: Landing page unauthenticated and authenticated redirects, dashboard view.
2. **Profiles (`apps.profiles.tests`)**:
   - `ProfileModelTests`: Profile creation, dynamic age calculation, height formatting, detail model relations.
   - `ProfilePhotoTests`: Image validation, resolution limits, primary photo switching logic.
   - `ProfileCompletionServiceTests`: Partial and 100% complete profile scoring.
   - `ProfileViewsTests`: First-time setup, tabbed editing, photo upload, photo deletion, cross-user deletion authorization (IDOR protection), and unauthenticated access redirects.
