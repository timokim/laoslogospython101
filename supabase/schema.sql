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
    created_at timestamptz not null default now()
);

create index if not exists idx_questions_quiz on questions(quiz_id);

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
-- Policy suggestion (adjust for your auth needs):
--   allow public read, allow insert for anon (or service role from backend only)
