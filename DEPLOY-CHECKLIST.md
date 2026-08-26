# Meridian — Zero-Dollar Deployment Checklist

## Phase 1: Export from Grok Build (time-sensitive — do while credits last)

- [ ] In Grok Build Meridian conversation, send the export prompt:
      "Export the complete source code of this project to the existing private GitHub repository `Cartilage-Stairwells/meridian-ops` on the `main` branch. Include all application source, configuration files, and assets required to run it outside Grok. Overwrite existing files if needed. Do not include secrets. Return the repository URL and a short file tree when finished."
- [ ] Confirm repo tree on GitHub (should see `src/`, `package.json`, `public/`, config files)
- [ ] If Grok can't push to GitHub directly, request a full file dump/archive and bring it to Elowen for manual push

## Phase 2: Capture browser state (before closing Grok)

- [ ] Copy Kamgar-Parsi letter (subject + body) to STATE-CAPTURE.md or local file
- [ ] Copy I2D follow-up text
- [ ] Copy any faculty names and scores entered
- [ ] Copy interview log entries
- [ ] Copy any IP/custody notes

## Phase 3: Deploy on Vercel (free)

- [ ] Go to vercel.com, sign in with GitHub (Hobby plan, free for personal use)
- [ ] Add New → Project → Import `Cartilage-Stairwells/meridian-ops`
- [ ] Confirm framework detection (Vite / TanStack Start)
- [ ] Click Deploy
- [ ] Save the production URL

## Phase 4: Verify

- [ ] Open the Vercel URL — all seven surfaces should load
- [ ] Test: open Letters, enter a draft, refresh — state should persist (localStorage)
- [ ] Bookmark the URL for daily use

## Phase 5: Ongoing updates (no paid tools needed)

- [ ] Clone repo locally: `git clone https://github.com/Cartilage-Stairwells/meridian-ops.git`
- [ ] Edit, commit, push: `git add -A && git commit -m "update" && git push origin main`
- [ ] Vercel auto-deploys on push — no manual deploy needed

## Constraints

- Vercel Hobby: free for personal/non-commercial use, subject to usage caps
- localStorage data does NOT transfer between deployments or devices — re-enter manually
- Do not commit `.env` files or secrets
- Meridian is a campaign instrument only — no P0/TSCP-PL internals in the public deploy
