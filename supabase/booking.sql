-- Run once in the Supabase SQL editor. No service-role key belongs in the frontend.
create table public.studio_owners(user_id uuid primary key references auth.users(id));
alter table public.studio_owners enable row level security;
create policy owner_self on public.studio_owners for select to authenticated using(user_id=auth.uid());
grant select on public.studio_owners to authenticated;
create table public.services(id text primary key,name text not null,price integer);
insert into public.services values
('s1','Gel polish — Short',10000),
('s2','Gel polish — Medium',13000),
('s3','Gel polish — Long',16000),
('s4','Gel polish — Extra long',18000),
('s5','Acrylic nails — Short',18000),
('s6','Acrylic nails — Medium',21000),
('s7','Acrylic nails — Long',24000),
('s8','Acrylic nails — Extra long',28000),
('s9','Toe painting',4000),
('s10','Big toe fixing',5000),
('s11','Fixing all toes',7000),
('s12','Acrylic toes',11000),
('s13','Manicure',7000),
('s14','Pedicure',12000),
('s15','Soak off',5000),
('s16','Lobe (pair) piercing',10000),
('s17','Upper lobe piercing',8000),
('s18','Helix piercing',8000),
('s19','Forward helix piercing',9000),
('s20','Double helix piercing',15000),
('s21','Triple helix piercing',22000),
('s22','Flat piercing',9000),
('s23','Conch piercing',9000),
('s24','Tragus piercing',9000),
('s25','Anti-tragus piercing',8000),
('s26','Rook piercing',10000),
('s27','Daith piercing',10000),
('s28','Snug piercing',10000),
('s29','Industrial (scaffold) piercing',20000),
('s30','Nostril piercing',9000),
('s31','Septum piercing',10000),
('s32','Eyebrow piercing',15000),
('s33','Labret piercing',12000),
('s34','Medusa piercing',12000),
('s35','Monroe piercing',12000),
('s36','Madonna piercing',12000),
('s37','Surface tragus piercing',16000),
('s38','Tongue piercing',20000),
('s39','Smiley piercing',12000),
('s40','Navel (belly) piercing',15000),
('s41','Floating navel piercing',18000),
('s42','Single nipple piercing',15000),
('s43','Pair of nipples piercing',28000),
('s44','Semi-permanent tattoo consultation',null);
alter table public.services enable row level security;
create policy services_read on public.services for select using(true);
grant select on public.services to anon,authenticated;
create table public.bookings(
 id uuid primary key, customer_name text not null, phone text not null,
 service_id text not null references public.services(id), service_name text not null,base_price integer,
 preferred_at timestamptz not null, notes text not null default '',
 status text not null default 'pending' check(status in ('pending','confirmed','declined','completed','cancelled')),
 created_at timestamptz not null default now()
);
create index bookings_date on public.bookings(preferred_at);
create index bookings_phone_created on public.bookings(phone,created_at);
alter table public.bookings enable row level security;
revoke all on public.bookings from anon,authenticated;
grant select on public.bookings to authenticated;
grant update(status) on public.bookings to authenticated;
create policy owner_read on public.bookings for select to authenticated using(exists(select 1 from public.studio_owners where user_id=auth.uid()));
create policy owner_update on public.bookings for update to authenticated using(exists(select 1 from public.studio_owners where user_id=auth.uid())) with check(exists(select 1 from public.studio_owners where user_id=auth.uid()));
create function public.request_booking(p_request_id uuid,p_name text,p_phone text,p_service text,p_preferred_at timestamptz,p_notes text,p_website text default '') returns uuid
language plpgsql security definer set search_path=public,pg_temp as $$
declare svc public.services; normalized text;
begin
 if p_request_id is null or p_name is null or length(trim(p_name)) not between 1 and 80 or p_phone is null or p_phone !~ '^[+0-9 ()-]{10,20}$' or p_notes is null or length(p_notes)>1000 or coalesce(p_website,'')<>'' then raise exception 'Invalid booking details'; end if;
 if p_preferred_at is null or p_preferred_at<=now() or p_preferred_at>now()+interval '180 days' then raise exception 'Choose a future date within 180 days'; end if;
 select * into svc from public.services where id=p_service;
 if not found then raise exception 'Unknown service'; end if;
 normalized:=regexp_replace(p_phone,'[^0-9]','','g');
 if normalized like '0%' then normalized:='234'||substring(normalized from 2); end if;
 perform pg_advisory_xact_lock(hashtext(normalized));
 -- Repeat submissions use the same reference and do not create duplicates or reveal customer data.
 if exists(select 1 from public.bookings where id=p_request_id) then return p_request_id; end if;
 if (select count(*) from public.bookings where phone=normalized and created_at>now()-interval '1 hour')>=5 then raise exception 'Too many requests; contact the studio'; end if;
 insert into public.bookings(id,customer_name,phone,service_id,service_name,base_price,preferred_at,notes) values(p_request_id,trim(p_name),normalized,svc.id,svc.name,svc.price,p_preferred_at,p_notes);
 return p_request_id;
end $$;
revoke all on function public.request_booking(uuid,text,text,text,timestamptz,text,text) from public;
grant execute on function public.request_booking(uuid,text,text,text,timestamptz,text,text) to anon,authenticated;
-- Create the owner's account using Supabase Auth, then explicitly authorize its UUID:
-- insert into public.studio_owners(user_id) values ('OWNER_AUTH_UUID');
