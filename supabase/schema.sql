-- Run this in the Supabase SQL editor when you're ready to connect production.

create extension if not exists "pgcrypto";

create table if not exists quizzes (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    code text not null unique,
    deployed boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists questions (
    id uuid primary key default gen_random_uuid(),
    quiz_id uuid not null references quizzes(id) on delete cascade,
    sort_order int not null default 0,
    question_text text not null,
    options jsonb not null,
    correct_index int not null,
    enabled boolean not null default true,
    created_at timestamptz not null default now()
);

create index if not exists idx_questions_quiz on questions(quiz_id);

-- If you created the questions table before the enabled column existed, run:
alter table questions add column if not exists enabled boolean not null default true;

create table if not exists submissions (
    id uuid primary key default gen_random_uuid(),
    quiz_id uuid not null references quizzes(id) on delete cascade,
    student_name text not null,
    score int not null,
    total int not null,
    submitted_at timestamptz not null default now()
);

create index if not exists idx_submissions_quiz on submissions(quiz_id);

create table if not exists submission_answers (
    id uuid primary key default gen_random_uuid(),
    submission_id uuid not null references submissions(id) on delete cascade,
    question_id uuid not null references questions(id) on delete cascade,
    selected_index int not null,
    is_correct boolean not null
);

create table if not exists students (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    photo_path text not null,
    created_at timestamptz not null default now()
);

-- Storage: create a public bucket named "student-photos" in the Supabase dashboard.
-- Then run the storage policies at the bottom of this file.

-- ---------------------------------------------------------------------------
-- Row level security (required when using the anon key from Streamlit)
-- The instructor PIN lives in the app, not Supabase Auth, so these policies
-- allow the anon role to read/write. Keep your supabase_key in Streamlit
-- secrets only — never expose it in the browser or client-side code.
-- Alternative: use the service_role key in secrets to bypass RLS entirely.
-- ---------------------------------------------------------------------------

alter table quizzes enable row level security;
alter table questions enable row level security;
alter table submissions enable row level security;
alter table submission_answers enable row level security;
alter table students enable row level security;

drop policy if exists "Allow app access" on quizzes;
create policy "Allow app access" on quizzes
    for all to anon, authenticated
    using (true) with check (true);

drop policy if exists "Allow app access" on questions;
create policy "Allow app access" on questions
    for all to anon, authenticated
    using (true) with check (true);

drop policy if exists "Allow app access" on submissions;
create policy "Allow app access" on submissions
    for all to anon, authenticated
    using (true) with check (true);

drop policy if exists "Allow app access" on submission_answers;
create policy "Allow app access" on submission_answers
    for all to anon, authenticated
    using (true) with check (true);

drop policy if exists "Allow app access" on students;
create policy "Allow app access" on students
    for all to anon, authenticated
    using (true) with check (true);

-- Storage bucket + policies (run after tables above)
insert into storage.buckets (id, name, public)
values ('student-photos', 'student-photos', true)
on conflict (id) do update set public = true;

drop policy if exists "Allow public read student photos" on storage.objects;
create policy "Allow public read student photos" on storage.objects
    for select to anon, authenticated
    using (bucket_id = 'student-photos');

drop policy if exists "Allow app upload student photos" on storage.objects;
create policy "Allow app upload student photos" on storage.objects
    for insert to anon, authenticated
    with check (bucket_id = 'student-photos');

drop policy if exists "Allow app update student photos" on storage.objects;
create policy "Allow app update student photos" on storage.objects
    for update to anon, authenticated
    using (bucket_id = 'student-photos')
    with check (bucket_id = 'student-photos');

drop policy if exists "Allow app delete student photos" on storage.objects;
create policy "Allow app delete student photos" on storage.objects
    for delete to anon, authenticated
    using (bucket_id = 'student-photos');
