-- 처음 DB를 만들 때 한 번 실행됩니다. Supabase 가 만들어 둔 역할들의 비밀번호를 POSTGRES_PASSWORD 로 맞춥니다.
\set pgpass `echo "$POSTGRES_PASSWORD"`
alter user authenticator with password :'pgpass';
alter user pgbouncer with password :'pgpass';
alter user supabase_auth_admin with password :'pgpass';
alter user supabase_functions_admin with password :'pgpass';
alter user supabase_storage_admin with password :'pgpass';
