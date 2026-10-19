# Studio backend: implementation and activation

Status: implemented on `codex/studio-backend`, not provisioned or deployed. Existing production static site is unchanged.

## Design

Render Node web service serves the existing website and same-origin JSON API. Supabase stores private client, booking, payment and work records; Auth verifies explicitly approved owner accounts. Photos use a private bucket and five-minute signed URLs. Paystack hosts checkout and sends signed webhooks to the Node API.

Customer → service and preferred date/time → server-calculated deposit → Paystack checkout → signed webhook/server verification → atomic payment record and booking confirmation → owner dashboard.

The studio accepts overlapping appointments. No exclusive slots, opening-hours limits or service durations are invented. Confirm these operational rules with the owner before enabling automatic payment bookings. Payment confirmation is not evidence that a time is exclusive.

## Setup

1. Create a Supabase project and run `supabase/studio.sql` once. This uses `lux_*` tables independently of the earlier inactive prototype. Set up an owner Auth account privately and add its UUID to `lux_owners`. Disable public signup. No customer account is required.
2. Add approved services and deposit percentages to `lux_services`; prices are naira, while booking/payment amounts are kobo. The existing `dist/price-menu.json` is the source for the owner's price review. The checkout catalog must be populated with approved prices; it never accepts amounts from the browser.
3. Create a Render web service from this feature branch using `render-backend.yaml` or `npm start`. Configure the exact HTTPS origin and Supabase keys privately. The service-role key stays server-side.
4. Configure a Paystack test secret (`sk_test_...`) and `PAYSTACK_MODE=test`. Set webhook URL to `https://YOUR_ORIGIN/api/paystack/webhook`. Callback URL is generated from APP_ORIGIN as `/payment.html`.
5. Run `npm test`. Verify SQL privileges, RPCs, owner login and photo access against a real test project. Then enable BOOKING_ENABLED for test checkout. Test duplicate callbacks, signature failures, wrong amount/currency, cancellations, paid bookings and photo consent before production.
6. When approved, configure live Paystack keys, set mode to live and verify the live webhook setting. Do not accept test payments as real bookings. Update homepage booking links to `/reserve.html` only when the backend is connected and ready. Preserve the old static site as a rollback option.

## Screens

- `/reserve.html`: online booking and deposit checkout.
- `/payment.html`: verifies payment after redirect, with WhatsApp follow-up.
- `/studio.html`: owner login, booking history/status, client notes and visit histories, photo uploads and public/private controls.
- `/api/gallery`: published, consented photos only, with expiring links. The existing homepage static gallery is not yet wired to this endpoint.

## Security and transaction rules

- Owner token is in an HttpOnly, SameSite=Strict cookie, Secure on HTTPS; each owner API call validates the token and owner membership. Mutations require the configured Origin. No credentials are put into localStorage.
- Paystack webhook signatures use HMAC-SHA512 over raw body bytes. The server verifies transactions with Paystack and checks reference, integer amount, NGN currency and test/live domain. It never trusts a callback status or submitted amount.
- SQL row locking makes repeated payment delivery idempotent. Payment after cancellation is marked `payment_review` and does not silently reopen the appointment. Cancellation does not issue refunds. No card data is stored.
- Booking UUIDs are idempotency keys. If initialization times out, the booking remains awaiting payment; verify/reconcile its Paystack reference before attempting a different charge. Durable checkout recovery/reconciliation should be completed before live activation.
- Public APIs cannot read client records from Supabase. All tables have RLS and revoked anon/authenticated grants; server-only RPCs require service_role. Confirm these grants in the test project.
- Uploads are limited to 5 MB with MIME signatures; no public bucket or anonymous uploads. Photos start private. Publishing requires consent. Previously issued URLs may work for up to five minutes after hiding.
- Limitations: rate limiting is process-local, not distributed; the Render proxy may group requests by proxy address. Add shared rate limiting and bot protection before high-volume advertising. No automated email/WhatsApp reminders, refunds, calendar synchronization, password reset UI or encrypted backups are implemented. Set a retention/deletion/export process for client records.
- Lists are bounded (200 bookings/photos, 500 clients); pagination and full-history views are required as volume grows. Photo insert failure can leave a private orphan object; add cleanup/reconciliation before scaling.

## Required end-to-end QA

Use Paystack test mode and consenting test client data. Verify owner and non-owner access; anonymous API denial; actual database persistence; amount mismatch rejection; webhook replay; expired sessions; client-to-photo linkage; hidden/private photo access; consent removal; and cancellation after payment. Current local tests cover pure payment/signature validation only; database and provider integration are not yet verified.
