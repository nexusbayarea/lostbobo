create or replace function gift_signup_bonus(target_user_id uuid)
returns void as $$
begin
  update profiles
  set credit_balance = credit_balance + 10,
      last_onboarded_at = NOW()
  where id = target_user_id
  and last_onboarded_at is null;
end;
$$ language plpgsql;
