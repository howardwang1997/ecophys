create table if not exists public.data_assets (
    id uuid primary key default gen_random_uuid(),
    local_path text not null,
    r2_bucket text not null,
    r2_key text not null,
    size_bytes bigint not null,
    sha256 text not null,
    source text not null,
    dataset text not null,
    symbol text,
    market text,
    interval text,
    year int,
    month int,
    content_type text,
    uploaded_at timestamptz,
    upload_status text not null default 'pending',
    error_message text,
    metadata jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (r2_bucket, r2_key)
);

create index if not exists idx_data_assets_dataset on public.data_assets (dataset);
create index if not exists idx_data_assets_source on public.data_assets (source);
create index if not exists idx_data_assets_r2_key on public.data_assets (r2_key);

create or replace function public.set_data_assets_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_data_assets_updated_at on public.data_assets;
create trigger trg_data_assets_updated_at
before update on public.data_assets
for each row execute function public.set_data_assets_updated_at();
