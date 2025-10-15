import streamlit as st
from docx import Document
import re

st.set_page_config(page_title="Post Test ISO 9001 & 22000", layout="wide")

# --- CSS untuk efek highlight jawaban terpilih ---
st.markdown("""
<style>
.question-box {
    background-color: #f9f9f9;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
}
.option {
    padding: 10px;
    border-radius: 8px;
    margin: 4px 0;
    cursor: pointer;
    border: 1px solid #e0e0e0;
    transition: all 0.2s ease-in-out;
}
.option:hover {
    background-color: #f1f1f1;
}
.option-selected {
    background-color: #d1ffd6 !important; /* hijau muda */
    border-color: #2ecc71 !important;
    font-weight: bold;
}
.submit-btn {
    background-color: #2ecc71;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧩 Post Test ISO 9001:2015 & ISO 22000:2018")
st.write(
    "Jawablah semua pertanyaan. Tombol **Lihat Hasil** akan muncul otomatis setelah semua soal dijawab."
)

# --- Fungsi: Baca dan parsing soal dari DOCX ---
def load_questions(doc_path):
    doc = Document(doc_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    pattern = r"(\d+\..*?)(?=(?:\n\d+\.|\Z))"
    raw_questions = re.findall(pattern, text, flags=re.S)

    questions = []
    for q in raw_questions:
        lines = [line.strip() for line in q.split("\n") if line.strip()]
        question_text = re.sub(r"^\d+\.\s*", "", lines[0])
        options = [l for l in lines if re.match(r"^[A-D]\.", l)]
        correct_match = re.search(r"✅\s*Jawaban[: ]*([A-D])", q)
        correct = correct_match.group(1) if correct_match else None
        if options and correct:
            questions.append({
                "question": question_text,
                "options": options,
                "answer": correct
            })
    return questions


# --- Load file soal ---
questions = load_questions("Soal Kompetensi.docx")
if not questions:
    st.error("❌ Tidak ditemukan soal. Pastikan file 'Soal Kompetensi.docx' tersedia.")
    st.stop()

# --- Inisialisasi jawaban user ---
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# --- Tampilkan soal ---
st.write(f"📄 Total Soal: **{len(questions)}**")
st.markdown("---")

for i, q in enumerate(questions):
    st.markdown(f"### {i+1}. {q['question']}")
    st.markdown('<div class="question-box">', unsafe_allow_html=True)

    # Loop opsi jawaban
    for opt in q["options"]:
        opt_letter = opt[0]  # ambil huruf (A/B/C/D)
        selected = st.session_state.user_answers.get(i) == opt_letter
        opt_class = "option option-selected" if selected else "option"

        # Tombol per opsi
        if st.button(opt, key=f"btn_{i}_{opt_letter}"):
            st.session_state.user_answers[i] = opt_letter
            st.rerun()  # refresh agar highlight langsung muncul

        # Warna highlight via CSS
        st.markdown(f'<div class="{opt_class}">{opt}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

st.markdown("---")

# --- Logika: tombol hasil hanya muncul jika semua soal sudah dijawab ---
answered = len(st.session_state.user_answers)
total = len(questions)

if answered < total:
    st.info(f"📝 Anda telah menjawab {answered} dari {total} soal. Lengkapi semua jawaban untuk melihat hasil.")
else:
    if st.button("🎯 Lihat Hasil", key="submit", use_container_width=True):
        correct = 0
        wrong = []
        for i, q in enumerate(questions):
            user_ans = st.session_state.user_answers.get(i)
            if user_ans == q["answer"]:
                correct += 1
            else:
                wrong.append({
                    "no": i+1,
                    "question": q["question"],
                    "your": user_ans,
                    "correct": q["answer"]
                })

        score = round((correct / total) * 100, 2)
        st.success(f"✅ Skor Anda: **{score}%** ({correct} benar dari {total} soal)")
        st.markdown("---")

        if wrong:
            st.error("❌ Soal yang Anda jawab salah:")
            for w in wrong:
                st.markdown(
                    f"**{w['no']}. {w['question']}**  \n"
                    f"Jawaban Anda: `{w['your']}`  \n"
                    f"Jawaban Benar: ✅ `{w['correct']}`"
                )
        else:
            st.balloons()
            st.success("🎉 Semua jawaban Anda benar! Hebat sekali!")

st.markdown("---")
st.caption("Dibuat oleh ChatGPT – Post Test Generator ISO 9001 & 22000 (Streamlit)")
