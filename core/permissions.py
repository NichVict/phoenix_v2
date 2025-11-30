from core.supabase_client import get_supabase

def get_user_permissions(email: str):
    supabase = get_supabase()
    res = supabase.table("clientes").select("*").eq("email", email).execute()

    if not res.data:
        return []

    return res.data[0].get("carteiras", [])
