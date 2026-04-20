create or replace function gift_signup_bonus(target_user_id uuid)
returns void as $$
begin
  if not exists (select 1 from credit_ledger where user_id = target_user_id and reason = 'signup_bonus') then
    
    -- 1. Add 10 Credits
    update profiles set credit_balance = credit_balance + 10 where id = target_user_id;
    insert into credit_ledger (user_id, amount, reason) values (target_user_id, 10, 'signup_bonus');

    -- 2. Inject Sample Simulation (The "Wedge")
    insert into simulation_history (
        user_id, 
        job_id, 
        status, 
        progress, 
        certificate_hash, 
        model_config, 
        target_geometry,
        created_at
    ) values (
        target_user_id,
        'demo-' || gen_random_uuid()::text,
        'completed',
        100,
        'sha256:d34f-demo-b0b0',
        'Parametric Sweep',
        'Turbine Blade',
        NOW()
    );
  end if;
end;
$$ language plpgsql;
