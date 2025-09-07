import streamlit as st
from supabase import create_client
from datetime import date

# -----------------------------
# إعداد الاتصال
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("تطبيق إدارة المحاسبين والفروع")

# -----------------------------
# اختبار عدد الصفوف
# -----------------------------
try:
    res = supabase.table("rota_entries").select("*").execute()
    st.write("عدد الصفوف قبل أي إضافة:", len(res.data))
except Exception as e:
    st.error(f"حدث خطأ أثناء الاتصال بـ Supabase: {e}")

# -----------------------------
# Form لإضافة سجل جديد
# -----------------------------
with st.form("add_entry"):
    d = st.date_input("التاريخ", value=date.today())
    branch_id = st.number_input("Branch ID", min_value=1, step=1)
    accountant_id = st.number_input("Accountant ID", min_value=1, step=1)
    substitute_id = st.number_input("Substitute ID (اختياري)", min_value=0, step=1, value=0)
    notes = st.text_area("ملاحظات (اختياري)")
    submit = st.form_submit_button("حفظ")

    if submit:
        payload = {
            "date": d.isoformat(),
            "branch_id": int(branch_id),
            "accountant_id": int(accountant_id),
            "substitute_id": int(substitute_id) if substitute_id != 0 else None,
            "notes": notes
        }

        try:
            res = supabase.table("rota_entries").insert(payload).execute()
            if not res.data:  # لو مفيش بيانات رجعت، معناها حصل خطأ
                st.error("حدث خطأ أثناء الحفظ. تأكد من جدول RLS ووجود الأعمدة الصحيحة.")
            else:
                st.success("تم الحفظ بنجاح ✅")
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بـ Supabase: {e}")
