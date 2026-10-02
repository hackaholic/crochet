# Task 3.6 — Safe VPS age-key bootstrap

**Owner:** Gemini

**Goal:** Provide a repeatable command to provision the VPS age private key safely.

**Requirements:**

- Create `/etc/sulocraft/age/` as `root:root` mode `0700`.
- Generate `/etc/sulocraft/age/keys.txt` only when it does not exist; fail without changing anything if a key is already present.
- Generate an age key using an installed tool or an ephemeral container; do not require an unnecessary host OS package installation.
- Store the private key `root:root` mode `0600`; never print or copy it out of the VPS.
- Print/return only the public `age1…` recipient and a clear success/failure status.
- Do not mount the key into application containers.

**Verify:** Test absent-key creation, existing-key refusal, owner/mode validation, and output redaction using a disposable test directory/key. Update Work 003 task 3.6 and notes.
