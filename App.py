import io
import streamlit as st
from PIL import Image
# יבוא של רכיב החיתוך הנייד
from streamlit_image_cropper import st_cropper

st.set_page_config(
    page_title="חיתוך סטיקר עם מסגרת דינמית", layout="centered"
)

st.title("✂️ חיתוך סטיקר מותאם אישית")
st.write(
    "העלה תמונה, והשתמש באצבע כדי להזיז, להגדיל או להקטין את מסגרת החיתוך סביב הסטיקר הנבחר!"
)

# העלאת תמונה מהטלפון
uploaded_file = st.file_uploader(
    "בחר תמונת סטיקרים:", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # פתיחת התמונה בעזרת Pillow
    img = Image.open(uploaded_file)

    st.subheader("🔍 כוונן את המסגרת סביב הסטיקר:")
    st.info("ניתן לגרור את הפינות של הריבוע כדי להקטין/להגדיל את אזור החיתוך.")

    # הצגת רכיב החיתוך הדינמי שמגיב למגע ואצבע
    # הרכיב מחזיר אוטומטית את התמונה החתוכה בכל שינוי של המסגרת
    cropped_img = st_cropper(
        img,
        realtime_update=True,
        box_color="#FF0000",
        aspect_ratio=None,  # מאפשר מסגרת חופשית (לא רק ריבוע מושלם)
    )

    # הצגת התוצאה הסופית
    st.subheader("🎯 הסטיקר שנבחר:")
    st.image(cropped_img, use_container_width=True)

    # הכנת הקובץ להורדה ישירות לגלריה של הטלפון
    buffer = io.BytesIO()
    cropped_img.save(buffer, format="PNG")
    byte_im = buffer.getvalue()

    st.download_button(
        label="💾 שמור את הסטיקר לטלפון",
        data=byte_im,
        file_name="my_sticker.png",
        mime="image/png",
    )
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
