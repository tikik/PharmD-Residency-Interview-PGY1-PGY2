### Developer Notes: Lessons from the Trenches
For future me or newbies— save time, avoid pain, remain focus on the models' rationales and end-user pain points. 

#### 1. Git Hygiene: Never Commit Build Artifacts or Secrets

Mistake: Accidentally committed 13k+ files (venv/, build/, dist/, .exe) → bloated repo, broken clones.
Fix:
Always create .gitignore before git init or creating a virtual env.
Use a comprehensive Python .gitignore.
Never run git add . blindly — review staged files first.
Recovery:
bash
123
git rm -r --cached venv/ build/ dist/ __pycache__/ *.exe  # untrack
git add .gitignore
git commit -m "fix: enforce .gitignore"

#### 2. PyInstaller: You Can’t Build Windows .exe on Linux

Mistake: Ran pyinstaller on Linux, got a “working” output, but it doesn’t run on Windows.
Truth: PyInstaller does not cross-compile.
→ Linux → Linux binary
→ Windows → Windows .exe
Fix:
Build .exe only on Windows (native or VM).
Use GitHub Actions with runs-on: windows-latest if automating.
Pro Tip: Bundle data/models explicitly using a .spec file.

#### 3. Distribute Binaries via GitHub Releases — Not Git

Mistake: Tried to commit .exe → Git rejected it (>100 MB) or bloated history.
Best Practice:
Source code → Git (clean, no binaries)
Binaries → GitHub Releases
Upload .exe, .zip, etc.
Include SHA256 checksum for integrity
Why: Keeps repo fast, cloneable, and audit-friendly.

#### 4. Always Be on a Named Branch Before Pushing

Mistake: git push -u origin main failed with “src refspec main does not match any”.
Cause: Never created or checked out main → Git had nothing to push.
Fix:
bash
12
git checkout -b main    # create & switch
git push -u origin main
Prevention: Set default branch globally:
bash
1
git config --global init.defaultBranch main

#### 5. SSH > HTTPS for Git (But Protect Your Key)

Good: You use git@github.com:... (SSH) → no token leakage risk.
Improve: Add a passphrase to your SSH key:
bash
1
ssh-keygen -p -f ~/.ssh/id_ed25519
→ Prevents misuse if your laptop is compromised.

#### 6. Test on Target OS Before Releasing

Mistake: Uploaded .exe built on Linux as v0.1.1 → doesn’t work on Windows.
Rule:
“If it’s not tested on the user’s machine, it’s not shipped.”

Process:
Build on Windows
Test on clean Windows VM/user machine
Then publish to GitHub Releases

✅ Final Checklist Before Committing or Releasing
.gitignore is present and correct
No venv/, build/, dist/, .exe, models in Git
On a named branch (main)
SSH key has passphrase (optional but recommended)
Binaries go to Releases, not source
Tested on target OS before release
