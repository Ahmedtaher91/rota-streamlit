# app.py
import streamlit as st
from supabase import create_client, Client

st.title("اختبار الاتصال بـ Supabase")

# قراءة المفاتيح من Secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

st.write("SUPABASE_URL:", SUPABASE_URL)
st.write("SUPABASE_KEY:", SUPABASE_KEY)

# إنشاء العميل
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# تجربة جلب جدول بسيط
try:
    res = supabase.table("rota_entries").select("*").execute()
    st.write("عدد الصفوف في rota_entries:", len(res.data))
except Exception as e:
    st.error(f"حدث خطأ أثناء الاتصال بـ Supabase: {e}")

