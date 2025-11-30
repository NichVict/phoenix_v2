from core.supabase_client import get_supabase

def listar_clientes():
    sb = get_supabase()
    try:
        res = sb.table("clientes").select("*").execute()
        return res.data or []
    except:
        return []


def buscar_cliente_por_id(cliente_id: int):
    sb = get_supabase()
    res = sb.table("clientes").select("*").eq("id", cliente_id).execute()
    return res.data[0] if res.data else None


def atualizar_cliente(cliente_id: int, dados: dict):
    sb = get_supabase()
    return sb.table("clientes").update(dados).eq("id", cliente_id).execute()


def inserir_cliente(dados: dict):
    sb = get_supabase()
    return sb.table("clientes").insert(dados).execute()
