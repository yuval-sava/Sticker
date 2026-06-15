import io
import zipfile
import cv2
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="מזהה סטיקרים אוטומטי", layout="centered")

st.title("🤖 מזהה ומקצץ סטיקרים אוטומטי")
st.write(
    "העלה תמונה של דף עם סטיקרים, והמערכת תזהה ותחתוך את כולם אוטומטית!"
)

uploaded_file = st.file_uploader(
    "בחר תמונת סטיקרים:", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # 1. קריאת התמונה והמרתה לפורמט ש-OpenCV מבין
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    st.image(img_rgb, caption="התמונה המקורית", use_container_width=True)

    # 2. עיבוד תמונה לצורך זיהוי (הגדרת סף קריטי)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # שימוש ב-Thresh כדי להפריד את הסטיקרים מהרקע (מתאים לרקע בהיר)
    _, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 3. מציאת קווי מתאר (Contours)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    cropped_stickers = []
    img_with_boxes = img_rgb.copy()

    # לולאה שעוברת על כל קווי המתאר שמצאנו
    for c in contours:
        # סינון רעשים: נתעלם מאזורים קטנים מדי (שאינם סטיקרים באמת)
        if cv2.contourArea(c) > 500:
            x, y, w, h = cv2.boundingRect(c)

            # חיתוך הסטיקר מהתמונה המקורית
            sticker = img_rgb[y : y + h, x : x + w]
            cropped_stickers.append(sticker)

            # ציור מלבן אדום על תמונת המקור לצורך תצוגה
            cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (255, 0, 0), 3)

    st.subheader(f"🎯 זיהוי הושלם! נמצאו {len(cropped_stickers)} סטיקרים")
    st.image(
        img_with_boxes,
        caption="הסטיקרים שזוהו אוטומטית (בריבוע אדום)",
        use_container_width=True,
    )

    if cropped_stickers:
        st.subheader("✂️ הסטיקרים החתוכים:")

        # יצירת קובץ ZIP בזיכרון כדי לאפשר הורדה מרוכזת בטלפון
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, "a", zipfile.ZIP_DEFLATED, False
        ) as zip_file:

            # הצגת כל סטיקר בנפרד והוספתו ל-ZIP
            for idx, sticker in enumerate(cropped_stickers):
                pil_img = Image.fromarray(sticker)

                # מציג את הסטיקר למשתמש
                st.image(
                    pil_img,
                    caption=f"סטיקר מספר {idx+1}",
                    width=150,
                )

                # שמירה ל-ZIP
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format="PNG")
                zip_file.writestr(
                    f"sticker_{idx+1}.png", img_byte_arr.getvalue()
                )

        # כפתור הורדה לקובץ ה-ZIP
        st.download_button(
            label="🎁 הורד את כל הסטיקרים כקובץ ZIP",
            data=zip_buffer.getvalue(),
            file_name="all_stickers.zip",
            mime="application/zip",
        )
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
