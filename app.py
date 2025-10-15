import streamlit as st
from docx import Document
import re

st.set_page_config(page_title="Post Test ISO 9001 & 22000", layout="wide")

st.title("🧩 Post Test ISO 9001:2015 & ISO 22000:2018")
st.write("Jawablah semua pertanyaan berikut, lalu klik **Lihat Hasil** di bagian bawah untuk melihat skor dan pembahasan.")

# Fungsi membaca soal dari file .docx
def load_questions(doc_path):
    doc = Document(doc_path)
    text = "\n".join([p.text for p in doc.paragraphs])

    # Pola untuk memisahkan soal berdasarkan nomor (1., 2., dst)
    pattern = r"(\d+\..*?)(?=(?:\n\d+\.|\Z))"
    questions_raw = re.findall(pattern, text, flags=re.S)

    questions = []
    for q in questions_raw:
        lines = [line.strip() for line in q.split("\n") if line.strip()]
        question_line = lines[0]
        question_text = re.sub(r"^\d+\.\s*", "", question_line)

        # Cari opsi
        options = [l for l in lines if re.match(r"^[A-D]\.", l)]
        # Cari jawaban benar
        answer_match = re.search(r"✅ Jawaban[: ]*([A-D])", q)
        correct = answer_match.group(1) if answer_match else None

        if options and correct:
            questions.append({
                "question": question_text,
                "options": options,
                "answer": correct
            })
    return questions


# Load soal dari file
questions = load_questions("Soal Kompetensi.docx")

# Session state untuk jawaban user
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "show_result" not in st.session_state:
    st.session_state.show_result = False

st.write(f"Total Soal: **{len(questions)}**")

# Tampilkan soal satu per satu
if not st.session_state.show_result:
    for idx, q in enumerate(questions):
        st.markdown(f"### {idx + 1}. {q['question']}")
        user_choice = st.radio(
            "Pilih jawaban:",
            q["options"],
            key=f"q_{idx}"
        )
        st.session_state.user_answers[idx] = user_choice[0]  # Ambil huruf A/B/C/D

    st.markdown("---")

    # Tombol untuk lihat hasil
    if st.button("🎯 Lihat Hasil"):
        st.session_state.show_result = True
        st.experimental_rerun()

else:
    # Menampilkan hasil
    correct_count = 0
    wrong_details = []

    for idx, q in enumerate(questions):
        user_answer = st.session_state.user_answers.get(idx)
        if user_answer == q["answer"]:
            correct_count += 1
        else:
            wrong_details.append({
                "no": idx + 1,
                "question": q["question"],
                "your": user_answer,
                "correct": q["answer"]
            })

    total = len(questions)
    score = round((correct_count / total) * 100, 2)

    st.success(f"✅ Skor Anda: **{score}%** ({correct_count} benar dari {total} soal)")
    st.markdown("---")

    if wrong_details:
        st.error("❌ Berikut soal yang Anda jawab salah:")
        for w in wrong_details:
            st.markdown(
                f"**{w['no']}. {w['question']}**  \n"
                f"Jawaban Anda: `{w['your']}`  \n"
                f"Jawaban Benar: ✅ `{w['correct']}`"
            )
    else:
        st.balloons()
        st.success("🎉 Semua jawaban Anda benar! Luar biasa!")

    st.markdown("---")

    # 🔁 Tombol Reset Test
    if st.button("🔁 Reset Test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

st.markdown("---")
st.caption("Dibuat oleh ChatGPT - Streamlit Post Test Generator untuk ISO 9001 & ISO 22000")
