# Online booking setup

This implementation is not activated on the live Render site yet. It supports pending appointment requests, not real-time slot reservations, payments or automated notifications.

1. Create a Supabase project in the business's account. Run `booking.sql` once in its SQL editor.
2. Disable public user signup. Create/invite the studio owner through Supabase Auth, then insert that account's UUID into `studio_owners` using the commented statement in the migration. Use the Supabase invitation/reset flow for the owner to set their password privately.
3. Put the project HTTPS URL and publishable/anon key in `dist/config.js`. These values are public configuration, not admin credentials. Never use a service-role/secret key.
4. Verify authenticated owner reads/updates work, anonymous and non-owner reads/updates fail, server-side service prices cannot be overridden, invalid/past requests fail, and repeat requests with the same UUID do not create duplicates. Test expiry and sign-out as well.
5. Add bot protection and project-level rate limiting before advertising at scale. The current honeypot and per-phone request limit provide only basic abuse resistance; phone ownership is not verified.
6. Test a real booking end to end with a consenting test contact, then push to `main` for Render to deploy. Owner login is at `/owner.html`.

No credentials or customer records are stored in browser localStorage. Owner sessions are in memory; reloading requires sign-in again. Supabase stores customer names, phone numbers, service selections, preferred date/time and optional notes. Establish a business retention/deletion process and privacy notice before launch. Do not request health details in notes.

The service catalog is transcribed from the supplied price lists. Nail art is an extra confirmed by the studio; tattoo pricing requires consultation. Availability, durations, opening hours and owner email still need confirmation. Regenerate neither production HTML nor SQL by rerunning `setup_booking.py`; it is a one-time source preparation script.

Status changes do not message customers. Use each booking's WhatsApp button to notify the customer. Requested times are in Africa/Lagos (UTC+01:00).
