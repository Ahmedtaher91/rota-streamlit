import streamlit as st
from supabase import create_client
from datetime import date

# -----------------------------
# إعداد الاتصال بـ Supabase
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("تطبيق إدارة المحاسبين والفروع")

# -----------------------------
# اختبار عدد الصفوف في rota_entries
# -----------------------------
try:
    res = supabase.table("rota_entries").select("*").execute()
    st.write("عدد الصفوف قبل أي إضافة:", len(res.data))
except Exception as e:
    st.error(f"حدث خطأ أثناء الاتصال بـ Supabase: {e}")

# -----------------------------
# جلب بيانات الفروع والمحصلين
# -----------------------------
branches_res = supabase.table("branches").select("*").execute()
branches = branches_res.data or []

users_res = supabase.table("users").select("*").execute()
users = users_res.data or []

branch_options = {b['name']: b['id'] for b in branches} if branches else {}
accountant_options = {u['name']: u['id'] for u in users} if users else {}

# -----------------------------
# Form لإضافة سجل جديد
# -----------------------------
with st.form("add_entry"):
    d = st.date_input("التاريخ", value=date.today())

    # لو القوائم فارغة، نعرض تحذير لكن الفورم يبقى موجود
    if not branch_options or not accountant_options:
        st.warning("البيانات غير موجودة في الفروع أو المحصلين. تحقق من RLS أو أضف بيانات.")
        submit = st.form_submit_button("حفظ")
    else:
        branch_name = st.selectbox("اختر الفرع", list(branch_options.keys()))
        accountant_name = st.selectbox("اختر المحاسب", list(accountant_options.keys()))

        branch_id = branch_options[branch_name]
        accountant_id = accountant_options[accountant_name]

        substitute_id = st.number_input("Substitute ID (اختياري)", min_value=0, step=1, value=0)
        notes = st.text_area("ملاحظات (اختياري)")

        submit = st.form_submit_button("حفظ")

        if submit:
            payload = {
                "date": d.isoformat(),
                "branch_id": branch_id,
                "accountant_id": accountant_id,
                "substitute_id": int(substitute_id) if substitute_id != 0 else None,
                "notes": notes
            }
            try:
                res = supabase.table("rota_entries").insert(payload).execute()
                if not res.data:
                    st.error("حدث خطأ أثناء الحفظ. تأكد من جدول RLS ووجود الأعمدة الصحيحة.")
                else:
                    st.success("تم الحفظ بنجاح ✅")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Supabase: {e}")
