create function public.lux_claim_first_admin(p_user uuid) returns void language plpgsql security invoker set search_path=public,pg_temp as $$
begin
 perform pg_advisory_xact_lock(hashtext('lux-first-admin'));
 if exists(select 1 from public.lux_owners) then raise exception 'Admin setup is closed';end if;
 insert into public.lux_owners(user_id) values(p_user);
end $$;
revoke all on function public.lux_claim_first_admin(uuid) from public,anon,authenticated;
grant execute on function public.lux_claim_first_admin(uuid) to service_role;
