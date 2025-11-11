from __future__ import annotations

# Minimal stub for form-based applications; we do not implement CAPTCHA/SSO.
# Returns REQUIRES_APPROVAL for now.


def attempt_form_apply(url: str) -> tuple[str, str]:
    # Future: add domain-based field maps and Playwright flows.
    return "REQUIRES_APPROVAL", "Form apply not implemented; manual approval required"


