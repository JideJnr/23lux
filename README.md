# 23 Lux Nails

Image-led, responsive landing page for nails, piercings and semi-permanent tattoos in Mafoluku, Oshodi, Lagos.

## Current functionality

- Filterable portfolio and image lightbox.
- WhatsApp appointment enquiries (not automatic confirmed appointments).
- TikTok and map direction links.
- Responsive layouts and reduced-motion support.

The current gallery is static. Owner login, photo uploads and a database are not implemented yet. Confirm the WhatsApp number and address with the business before public launch. Replace screenshot-derived images with original photos when available.

## Local preview

Run `python -m http.server 4173 --directory dist` and visit http://localhost:4173.

## Render deployment

Connect this GitHub repository to Render and create a Blueprint using `render.yaml`, or create a Static Site with:

- Branch: `main`
- Build command: `echo "Static site ready"`
- Publish directory: `dist`

Render hosts the contents of `dist`; no Node server or package installation is required. `.openai/hosting.json` retains the separate existing Sites deployment identity and is not used by Render.

## Recommended gallery backend

Use Supabase Storage for images, Postgres for gallery entries and Supabase Auth for the studio owner. Render can continue serving the frontend as a static site. No separate Express server is required for this scope.

Proposed gallery fields: id, image_path, caption, category (nails/piercings/tattoos), featured, published, created_at. Serve paginated published entries with lazy-loaded responsive thumbnails.

Use a private storage bucket with short-lived signed URLs for published images so hiding a gallery entry also prevents new public access to its image. Restrict all write operations to an explicitly approved owner user ID using database and storage row-level policies. Being signed in alone must not grant upload or edit permission. Create owner accounts administratively; do not expose public owner registration. Never put a Supabase service-role key in browser code or GitHub.

The owner dashboard should support mobile photo uploads, captions, categories, preview, publishing and hiding. Resize photos before upload, enforce image MIME types and size limits in storage, and validate dimensions. Do not use Render's local filesystem for durable customer uploads.

Provisioning and end-to-end tests of owner-only writes and public read restrictions are required before enabling uploads. No Supabase credentials are configured in this repository.
