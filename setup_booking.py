from pathlib import Path
import json,re
p=Path(__file__).parent
services=[]
def add(category,name,price):
    services.append(dict(id='s'+str(len(services)+1),category=category,name=name,price=price))
for kind,prices in [('Gel polish',[10000,13000,16000,18000]),('Acrylic nails',[18000,21000,24000,28000])]:
    for length,price in zip(['Short','Medium','Long','Extra long'],prices):add('Nails',kind+' — '+length,price)
for name,price in [('Toe painting',4000),('Big toe fixing',5000),('Fixing all toes',7000),('Acrylic toes',11000),('Manicure',7000),('Pedicure',12000),('Soak off',5000)]:add('Nails',name,price)
for name,price in [('Lobe (pair)',10000),('Upper lobe',8000),('Helix',8000),('Forward helix',9000),('Double helix',15000),('Triple helix',22000),('Flat',9000),('Conch',9000),('Tragus',9000),('Anti-tragus',8000),('Rook',10000),('Daith',10000),('Snug',10000),('Industrial (scaffold)',20000),('Nostril',9000),('Septum',10000),('Eyebrow',15000),('Labret',12000),('Medusa',12000),('Monroe',12000),('Madonna',12000),('Surface tragus',16000),('Tongue',20000),('Smiley',12000),('Navel (belly)',15000),('Floating navel',18000),('Single nipple',15000),('Pair of nipples',28000)]:add('Piercing',name+' piercing',price)
add('Semi-permanent tattoo','Semi-permanent tattoo consultation',None)
(p/'dist/services.js').write_text('window.SERVICES = '+json.dumps(services)+';\n',encoding='utf-8')
html=(p/'dist/index.html').read_text(encoding='utf-8')
html=html.replace("Tell us what you have in mind.<br>We'll take it from there on WhatsApp.","Choose your service and request an appointment online.<br>Continue on WhatsApp whenever you like.")
start=html.index('<form id="booking-form">');end=html.index('</form>',start)+len('</form>')
form='''<div><form id="booking-form"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required maxlength="80"><label for="phone">Phone / WhatsApp number</label><input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="080… or +234…" pattern="[+0-9 ()-]{10,20}" required maxlength="20"><label for="service">Choose your service</label><select id="service" name="service"></select><p id="service-price" class="form-note"></p><label for="date">Preferred date</label><input id="date" name="date" type="date" required><label for="time">Preferred time (Lagos)</label><input id="time" name="time" type="time" required><label for="notes">Design ideas or questions (optional)</label><textarea id="notes" name="notes" maxlength="1000" rows="3" placeholder="Mention nail art extras or your preferred look. Please don't include medical details."></textarea><div class="honeypot" aria-hidden="true"><label for="website">Leave this empty</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div><p class="form-note">Your name, contact number and request are stored privately for the studio to manage your appointment. Your preferred time requires confirmation. No payment is taken online.</p><button class="button dark" type="submit">Request appointment <span>↗</span></button></form><p id="booking-status" role="status" aria-live="polite"></p><a id="booking-whatsapp" class="button" hidden target="_blank" rel="noopener">Continue on WhatsApp ↗</a></div>'''
html=html[:start]+form+html[end:]
html=html.replace('<script src="app.js"></script>','<script src="app.js"></script><script src="config.js"></script><script src="services.js"></script><script src="booking.js"></script>')
html=html.replace('<div><a href="https://www.tiktok.com','<div><a href="owner.html">Studio login ↗</a><a href="https://www.tiktok.com')
(p/'dist/index.html').write_text(html,encoding='utf-8')
js=(p/'dist/app.js').read_text(encoding='utf-8')
js='\n'.join(line for line in js.splitlines() if not line.startswith("document.querySelectorAll('[data-service]')") and not line.startswith("document.querySelector('#booking-form').addEventListener"))
(p/'dist/app.js').write_text(js,encoding='utf-8')
values=',\n'.join("('%s','%s',%s)"%(s['id'],s['name'].replace("'","''"),'null' if s['price'] is None else s['price']) for s in services)
sql='''-- Run once in the Supabase SQL editor. No service-role key belongs in the frontend.
create table public.studio_owners(user_id uuid primary key references auth.users(id));
alter table public.studio_owners enable row level security;
create policy owner_self on public.studio_owners for select to authenticated using(user_id=auth.uid());
grant select on public.studio_owners to authenticated;
create table public.services(id text primary key,name text not null,price integer);
insert into public.services values
'''+values+''';
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
'''
(p/'supabase').mkdir(exist_ok=True)
(p/'supabase/booking.sql').write_text(sql,encoding='utf-8')
