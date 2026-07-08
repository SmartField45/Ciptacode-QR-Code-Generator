import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO
import urllib.parse

# --- Set Page Config ---
image_name = r"assets/logo.png"
image = Image.open(image_name)

st.set_page_config(page_title="Ciptacode QR Code Generator",
                   page_icon=image, layout="centered")

# --- Showing The Main Logo ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image(image, width=100)
with col_title:
    st.title("Ciptacode QR Code Generator")

st.write("Change any text or URL into a QR Code! Download your QR Code for free!")
st.write("You can also adjust the color, size and add your own logo the QR Code")
st.write("---")

# --- Multifunction Page ---
st.subheader("Choose QR Code Type")
qr_type = st.radio("Options:", ["URL/Text", "Wi-Fi Access", "vCard",
                   "Whatsapp"], horizontal=True, label_visibility="collapsed")

qr_data = None

# --- Input for URL or Text ---
if qr_type == "URL/Text":
    url = st.text_input("Enter URL or text here:")
    if url:
        qr_data = url

# --- Input for Wi-Fi Access ---
elif qr_type == "Wi-Fi Access":
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        ssid = st.text_input("Wi-Fi Name (SSID):")
        encryption = st.selectbox(
            "Encryption Type:", ["WPA/WPA2", "WEP", "None"])
    with col_w2:
        password = st.text_input("Wi-Fi Password:", type="password")

    if ssid:
        encryption_type = "WPA" if encryption == "WPA/WPA2" else "WEP" if encryption == "WEP" else "nopass"
        qr_data = f"WIFI:T:{encryption_type};S:{ssid};P:{password};;"


# --- Input for vCard ---
elif qr_type == "vCard":
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        first_name = st.text_input("First Name:")
        phone = st.text_input("Phone Number:")
    with col_c2:
        last_name = st.text_input("Last Name:")
        email = st.text_input("Email Address:")

    if first_name or phone:
        qr_data = f"""
        BEGIN:VCARD
        VERSION:3.0
        N:{last_name};{first_name}
        FN:{first_name} {last_name}
        TEL:{phone}
        EMAIL:{email}
        END:VCARD
        """

# --- Input for WhatsApp ---
elif qr_type == "Whatsapp":
    phone_wa = st.text_input("Enter WhatsApp Number (with country code):")
    message_wa = st.text_area("Enter Message (Optional):")

    if phone_wa:
        encoded_message = urllib.parse.quote(message_wa)
        qr_data = f"https://wa.me/{phone_wa}?text={encoded_message}"

st.write("---")

# --- Visual Settings ---
st.write("---")
st.subheader("Visual Settings")

col1, col2, col3 = st.columns(3)

with col1:
    fill_color = st.color_picker("QR Code Color", "#000000")
with col2:
    back_color = st.color_picker("Background Color", "#FFFFFF")
with col3:
    box_size = st.slider("Box Size", min_value=1, max_value=20, value=10)

# --- Input for Logo File ---
logo_file = st.file_uploader(
    "Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

st.write("---")

if qr_data:
    # --- Make QR Code ---
    qr = qrcode.QRCode(
        version=5, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=box_size, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    # --- Create Image ---
    img = qr.make_image(fill_color=fill_color,
                        back_color=back_color).convert("RGBA")

    # --- Add Logo ---
    if logo_file is not None:
        logo = image.open(logo_file)

        # --- Resize Logo ---
        img_w, img_h = img.size
        logo_max_size = img_w // 4
        logo.thumbnail((logo_max_size, logo_max_size),
                       Image.Resampling.LANCZOS)

        # --- Calculate Position ---
        logo_w, logo_h = logo.size
        pos = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)

        # --- Paste Logo ---
        img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

    # --- Website Implementation ---
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # --- Show QR Code ---
    st.image(byte_im, caption="Here's your QR Code!", use_column_width=False)

    # --- Download Button ---
    st.download_button(label="Download QR Code", data=byte_im,
                       file_name="qr_code.png", mime="image/png")
