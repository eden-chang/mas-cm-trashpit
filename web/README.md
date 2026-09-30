# Trashpit Web

React + TypeScript + Vite frontend for the Trashpit inventory system. It shows a character's bag as a drag-and-drop grid, along with the free space and nearby zones, and saves layout changes through the Flask API.

## Scripts

```bash
npm ci
npm run dev          # dev server; /api is proxied to http://localhost:5000
npm run build        # production build into dist/
npm run preview      # serve the production build locally
npm run fonts:woff2  # convert fonts/*.ttf to .woff2
```

## Configuration

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` when the API is hosted on another origin (for example, the deployed Railway API). Leave it empty in development to use the Vite proxy.

## Layout

- `src/app/App.tsx`: character selection, polling for changes, save/refresh
- `src/app/components/BagTab.tsx`: bag grid, item shapes, drag-and-drop
- `src/app/components/bag/`: grid constants, item chips, dialogs, drop zones
- `src/lib/`: API client, API types, and API-to-UI data transforms
- `vercel.json`: SPA rewrite for Vercel deployment
