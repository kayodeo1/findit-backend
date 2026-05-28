from django.conf import settings
from supabase import Client, create_client


def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_admin_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


supabase_anon: Client = get_supabase_client()
supabase_admin: Client = get_supabase_admin_client()
