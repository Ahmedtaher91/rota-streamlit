# app.py
import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date

st.set_page_config(page_title="نظام توزيع المحاسبين", layout="wide")

# --- قراءة مفاتيح Supabase من Streamlit secrets ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("أضِف SUPABASE_URL و SUPABASE_KEY في Streamlit Secrets ثم أعد النشر.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- مساعدة لجلب جدول كامل ---
def fetch_table(name):
    res = supabase.table(name).select("*").execute()
    if getattr(res, "error", None):
        st.error(f"خطأ عند جلب جدول {name}: {res.error}")
        return []
    return res.data or []

# --- جلب بيانات الفروع والمستخدمين والسجلات ---
branches = fetch_table("branches")
users = fetch_table("users")
entries_res = supabase.table("rota_entries").select("*").order("date", {"ascending": True}).execute()
entries = entries_res.data if getattr(entries_res, "data", None) is not None else []

# تحويل لأسماء للعرض
branches_by_id = {b.get("id"): b.get("name") for b in branches}
users_by_id = {u.get("id"): u.get("name", u.get("email", "")) for u in users}

rows = []
for e in entries:
    rows.append({
        "id": e.get("id"),
        "date": e.get("date"),
        "branch": branches_by_id.get(e.get("branch_id"), e.get("branch_id")),
        "accountant": users_by_id.get(e.get("accountant_id"), e.get("accountant_id")),
        "substitute": users_by_id.get(e.get("substitute_id"), ""),
        "notes": e.get("notes","")
    })

df = pd.DataFrame(rows)

# --- الواجهة ---
st.title("📊 نظام توزيع المحاسبين — Streamlit")
st.markdown("تقدر تضيف محاسب لفرع في تاريخ، وتشوف القائمة الحالية من Supabase.")

col1, col2 = st.columns([1,2])

with col1:
    st.subheader("أضف/سجل مهمة جديدة")
    with st.form("add_entry"):
        d = st.date_input("التاريخ", value=date.today())
        if branches:
            branch = st.selectbox("الفرع", options=branches, format_func=lambda b: b.get("name"))
            branch_id = branch.get("id")
        else:
            branch_id = st.text_input("فرع ID (أدخل ID أو اسم)")
        if users:
            acct = st.selectbox("المحاسب", options=users, format_func=lambda u: u.get("name"))
            accountant_id = acct.get("id")
            sub_options = [None] + users
            substitute = st.selectbox("بديل (اختياري)", options=sub_options, format_func=lambda u: "" if u is None else u.get("name"))
            substitute_id = None if substitute is None else substitute.get("id")
        else:
            accountant_id = st.text_input("محاسب ID")
            substitute_id = st.text_input("بديل ID (اختياري)")
        notes = st.text_area("ملاحظات (اختياري)")
        submit = st.form_submit_button("حفظ")
        if submit:
            payload = {
                "date": d.isoformat(),
                "branch_id": branch_id,
                "accountant_id": accountant_id,
                "substitute_id": substitute_id or None,
                "notes": notes
            }
            res = supabase.table("rota_entries").insert(payload).execute()
            if getattr(res, "error", None):
                st.error(f"خطأ أثناء الحفظ: {res.error}")
            else:
                st.success("✅ تم الحفظ")
                st.experimental_rerun()

with col2:
    st.subheader("عرض السجلات (من Supabase)")
    st.write("يمكنك تصفية أو تصدير النتائج من هنا.")
    st.dataframe(df)

    st.markdown("**ملاحظة:** لو الفروع أو المحاسبين غير موجودين، أضفهم أولًا في Supabase Table Editor (صفحة المشروع).")

# --- زر تصدير CSV سريع ---
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("تحميل CSV", data=csv, file_name="rota_export.csv", mime="text/csv")
