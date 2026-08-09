create extension if not exists pgcrypto;

create table if not exists public.ai_usage_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  action text not null default 'analyze-meal'
);

create index if not exists ai_usage_logs_user_action_created_at_idx
on public.ai_usage_logs (user_id, action, created_at desc);

alter table public.ai_usage_logs enable row level security;

drop policy if exists "ai usage logs owner read" on public.ai_usage_logs;
drop policy if exists "ai usage logs owner insert" on public.ai_usage_logs;
drop policy if exists "ai usage logs owner update" on public.ai_usage_logs;
drop policy if exists "ai usage logs owner delete" on public.ai_usage_logs;
