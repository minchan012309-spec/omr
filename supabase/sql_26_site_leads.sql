-- 26. 소개 페이지의 무료 체험 신청 · 문의 (trial.html · contact.html → 개발자 탭 「체험 신청 · 문의」)
-- 로그인하지 않은 방문자도 남길 수 있게 insert 만 열고, 읽기 · 처리 · 삭제는 개발자(is_dev, sql_15)만.
create table if not exists site_leads (
  id bigserial primary key,
  t timestamptz not null default now(),
  kind text not null check (kind in ('trial','contact')),
  academy text check (char_length(academy) <= 60),
  name text not null check (char_length(name) between 1 and 40),
  phone text check (char_length(phone) <= 30),
  email text check (char_length(email) <= 120),
  students text check (char_length(students) <= 20),
  subjects text check (char_length(subjects) <= 120),
  topic text check (char_length(topic) <= 40),
  message text check (char_length(message) <= 2000),
  status text not null default 'new' check (status in ('new','done')),
  memo text check (char_length(memo) <= 500)
);
alter table site_leads enable row level security;
drop policy if exists "leads insert" on site_leads;
drop policy if exists "leads select" on site_leads;
drop policy if exists "leads update" on site_leads;
drop policy if exists "leads delete" on site_leads;
create policy "leads insert" on site_leads for insert to anon, authenticated with check (status = 'new' and memo is null and (phone is not null or email is not null));
create policy "leads select" on site_leads for select using (is_dev());
create policy "leads update" on site_leads for update using (is_dev());
create policy "leads delete" on site_leads for delete using (is_dev());
grant insert on site_leads to anon, authenticated;
grant usage, select on sequence site_leads_id_seq to anon, authenticated;
