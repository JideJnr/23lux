-- Fresh studio backend; independent of the earlier unactivated booking prototype.
create table public.lux_owners(user_id uuid primary key references auth.users(id));
create table public.lux_services(id uuid primary key default gen_random_uuid(),name text not null,category text not null,price integer not null check(price>0),deposit_percent integer not null check(deposit_percent between 1 and 100),active boolean not null default true);
create table public.lux_clients(id uuid primary key default gen_random_uuid(),name text not null,phone text unique not null,email text not null,notes text not null default '',created_at timestamptz not null default now());
create table public.lux_bookings(id uuid primary key,client_id uuid not null references public.lux_clients(id),service_id uuid not null references public.lux_services(id),customer_name text not null,phone text not null,email text not null,service_name text not null,preferred_at timestamptz not null,notes text not null default '',amount_due integer not null check(amount_due>0),total_price integer not null,payment_reference text unique not null,status text not null default 'awaiting_payment' check(status in ('awaiting_payment','confirmed','completed','cancelled','payment_review')),paid_at timestamptz,created_at timestamptz not null default now());
create index lux_bookings_time on public.lux_bookings(preferred_at);
create table public.lux_payments(reference text primary key,booking_id uuid not null references public.lux_bookings(id),amount integer not null,currency text not null,paid_at timestamptz not null default now());
create table public.lux_work(id uuid primary key default gen_random_uuid(),client_id uuid not null references public.lux_clients(id),booking_id uuid references public.lux_bookings(id),caption text not null,category text not null check(category in ('nails','piercings','tattoos')),object_path text unique not null,public_consent boolean not null default false,published boolean not null default false,created_at timestamptz not null default now(),check(not published or public_consent));
-- All client data and photo access goes through the authenticated server.
do $$ declare t text; begin foreach t in array array['lux_owners','lux_services','lux_clients','lux_bookings','lux_payments','lux_work'] loop execute format('alter table public.%I enable row level security',t);execute format('revoke all on public.%I from anon, authenticated',t);end loop;end $$;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values('lux-work','lux-work',false,5242880,array['image/jpeg','image/png','image/webp']);
create function public.lux_create_booking(p_id uuid,p_name text,p_phone text,p_email text,p_service uuid,p_at timestamptz,p_notes text) returns public.lux_bookings language plpgsql security definer set search_path=public,pg_temp as $$
declare svc public.lux_services; client uuid; booking public.lux_bookings; local_at timestamp;
begin
 if length(trim(p_name)) not between 1 and 80 or length(p_notes)>1000 or p_at<=now() or p_at>now()+interval '180 days' then raise exception 'Invalid booking';end if;
 perform pg_advisory_xact_lock(hashtext(p_id::text));
 select * into booking from public.lux_bookings where id=p_id;
 if found then
 if booking.status<>'awaiting_payment' or booking.created_at<now()-interval '20 minutes' then raise exception 'Reservation expired or already processed';end if;
 return booking;end if;
 local_at:=p_at at time zone 'Africa/Lagos';
 if extract(isodow from local_at)=7 or local_at::time<time '10:00' or local_at::time>=time '21:00' then raise exception 'Book Monday to Saturday, 10am to 9pm Lagos time';end if;
 perform pg_advisory_xact_lock(hashtext('lux-day-'||local_at::date::text));
 if (select count(*) from public.lux_bookings where (preferred_at at time zone 'Africa/Lagos')::date=local_at::date and (status in ('confirmed','completed') or (status='awaiting_payment' and created_at>now()-interval '20 minutes')))>=5 then raise exception 'This day is fully booked';end if;
 select * into svc from public.lux_services where id=p_service and active;
 if not found then raise exception 'Service unavailable';end if;
 insert into public.lux_clients(name,phone,email) values(p_name,p_phone,p_email) on conflict(phone) do nothing;
 select id into client from public.lux_clients where phone=p_phone;
 insert into public.lux_bookings(id,client_id,service_id,customer_name,phone,email,service_name,preferred_at,notes,amount_due,total_price,payment_reference)
 values(p_id,client,svc.id,p_name,p_phone,p_email,svc.name,p_at,p_notes,500000,svc.price*100,'lux-'||p_id::text) returning * into booking;
 return booking;
end $$;
create function public.lux_apply_payment(p_reference text,p_amount integer,p_currency text) returns text language plpgsql security definer set search_path=public,pg_temp as $$
declare booking public.lux_bookings; occupied integer;
begin
 select * into booking from public.lux_bookings where payment_reference=p_reference for update;
 if not found or booking.amount_due<>p_amount or p_currency<>'NGN' then raise exception 'Payment mismatch';end if;
 insert into public.lux_payments(reference,booking_id,amount,currency) values(p_reference,booking.id,p_amount,p_currency) on conflict(reference) do nothing;
 if booking.paid_at is null then
 perform pg_advisory_xact_lock(hashtext('lux-day-'||(booking.preferred_at at time zone 'Africa/Lagos')::date::text));
 select count(*) into occupied from public.lux_bookings where id<>booking.id and (preferred_at at time zone 'Africa/Lagos')::date=(booking.preferred_at at time zone 'Africa/Lagos')::date and (status in ('confirmed','completed') or (status='awaiting_payment' and created_at>now()-interval '20 minutes'));
 update public.lux_bookings set paid_at=now(),status=case when status='awaiting_payment' and occupied<5 and preferred_at>now() then 'confirmed' else 'payment_review' end where id=booking.id;
 end if;
 return (select status from public.lux_bookings where id=booking.id);
end $$;
revoke all on function public.lux_create_booking(uuid,text,text,text,uuid,timestamptz,text) from public,anon,authenticated;
revoke all on function public.lux_apply_payment(text,integer,text) from public,anon,authenticated;
grant execute on function public.lux_create_booking(uuid,text,text,text,uuid,timestamptz,text) to service_role;
grant execute on function public.lux_apply_payment(text,integer,text) to service_role;
-- Explicitly grant the owner after creating their Supabase Auth user:
-- insert into public.lux_owners(user_id) values ('OWNER_AUTH_UUID');
-- Add services only after the studio confirms its deposit rule. price is naira.
-- insert into public.lux_services(name,category,price,deposit_percent) values ('Gel polish — Short','nails',10000,50);
