# Meridian

Translational operations console — a campaign instrument for the external queue. Sits above the frozen P0 / TSCP-PL contracts. Does not modify or extend canonical layers.

## Surfaces

| Surface | Purpose |
|--------|---------|
| **Command** | Dated queue, governance surfaces, authority chain |
| **Faculty** | TTP-T criteria, scored short list, status tracking |
| **Letters** | Editable Kamgar-Parsi and I2D drafts with copy actions |
| **Discovery** | Mom Test bank, 100-interview counter, interview log |
| **Commerce** | Five-year pro forma, market-risk sensitivity, SBIR vs STTR |
| **Custody** | IP checklist, iEdison clock, march-in record |
| **Shorthand** | Operational reference (not canonical) |

## State

All state persists in browser `localStorage`. No server, no database, no secrets.

## Deployment (free tier)

### Vercel Hobby (recommended)
1. Go to [vercel.com](https://vercel.com), sign in with GitHub
2. **Add New → Project → Import** this repository
3. Framework auto-detected (Vite / TanStack Start)
4. Click **Deploy**
5. Save the production URL
6. Future `git push` to `main` auto-deploys

### Alternative free hosts
- **Cloudflare Pages** — connect repo, same flow
- **Netlify** — connect repo, same flow
- **GitHub Pages** — static build output (if no SSR required)

## Local development

```bash
npm install
npm run dev
```

## Architecture boundary

Meridian is a **campaign instrument**, not a canonical authority. It does not:
- Modify P0 contracts
- Extend TSCP-PL
- Change the Canonical Lexicon
- Store or transmit secrets

All campaign data (letters, faculty scores, interview logs) lives in the browser only.
