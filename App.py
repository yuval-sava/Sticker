import io
import streamlit as st
from PIL import Image

st.set_page_config(page_title="חותך הסטיקרים שלי", layout="centered")

st.title("✂️ חותך הסטיקרים לנייד")
st.write("העלה תמונה, הזן אחוזים לחיתוך (או חתוך ריבוע מרכזי), ושמור!")

# 1. העלאת קובץ מהגלריה או המצלמה של הטלפון
uploaded_file = st.file_uploader(
    "בחר תמונת סטיקרים:", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # פתיחת התמונה
    image = Image.open(uploaded_file)
    width, height = image.size

    st.image(image, caption="התמונה המקורית", use_container_width=True)

    st.subheader("הגדרות החיתוך")
    st.write(f"גודל התמונה הנוכחי: {width}x{height} פיקסלים")

    # סליידרים ידידותיים למגע לבחירת אזור החיתוך באחוזים
    col1, col2 = st.columns(2)

    with col1:
        left = st.slider(
            "חיתוך משמאל (ב-%)", 0, 100, 25, help="מאיפה להתחיל לחתוך משמאל"
        )
        right = st.slider(
            "חיתוך מימין (ב-%)", 0, 100, 75, help="איפה לעצור את החיתוך מימין"
        )

    with col2:
        top = st.slider(
            "חיתוך מלמעלה (ב-%)", 0, 100, 25, help="מאיפה להתחיל לחתוך מלמעלה"
        )
        bottom = st.slider(
            "חיתוך מלמטה (ב-%)", 0, 100, 75, help="איפה לעצור את החיתוך מלמטה"
        )

    # וידוא שהערכים הגיוניים (שלא חותכים הפוך)
    if left < right and top < bottom:
        # המרת האחוזים לפיקסלים בפועל
        box = (
            int(width * (left / 100)),
            int(height * (top / 100)),
            int(width * (right / 100)),
            int(height * (bottom / 100)),
        )

        # ביצוע החיתוך
        cropped_image = image.crop(box)

        st.subheader("🎯 הסטיקר שנבחר:")
        st.image(cropped_image, use_container_width=True)

        # הכנת התמונה להורדה לטלפון
        buffer = io.BytesIO()
        cropped_image.save(buffer, format="PNG")
        byte_im = buffer.getvalue()

        # כפתור הורדה ישירות לגלריה/קבצים של הטלפון
        st.download_button(
            label="💾 שמור את הסטיקר לטלפון",
            data=byte_im,
            file_name="my_sticker.png",
            mime="image/png",
        )
    else:
        st.error(
            "טווח החיתוך לא תקין. ודא שערך ימין הגדול משמאל, וערך למטה גדול מלמעלה."
        )
