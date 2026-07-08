import flet as ft
import qrcode
from PIL import Image
from io import BytesIO
import urllib.parse
import base64

current_qr_image = None
uploaded_logo_path = None


async def main(page: ft.Page):
    global current_qr_image, uploaded_logo_path

    # --- Page Setup ---
    page.title = "Ciptacode QR Code Generator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 550
    page.window_height = 850
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.window.icon = "/logo.png"

    # Reset variabel
    current_qr_image = None
    uploaded_logo_path = None

    # --- Header ---
    header = ft.Row(
        controls=[
            ft.Image(src="/logo.png", width=60,
                     height=60, fit=ft.BoxFit.CONTAIN),
            ft.Text("Ciptacode QR Code Generator",
                    size=24, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    description = ft.Column([
        ft.Text(
            "Change any text or URL into a QR Code! Download your QR Code for free!"),
        ft.Text(
            "You can also adjust the color, size and add your own logo to the QR Code"),
        ft.Divider(),
    ])

    # --- Input Fields ---
    url_input = ft.TextField(label="Enter URL or text here", expand=True)

    wifi_ssid = ft.TextField(label="Wi-Fi Name (SSID)", expand=True)
    wifi_enc = ft.Dropdown(
        label="Encryption Type",
        options=[ft.dropdown.Option(
            "WPA/WPA2"), ft.dropdown.Option("WEP"), ft.dropdown.Option("None")],
        value="WPA/WPA2",
        expand=True
    )
    wifi_pass = ft.TextField(
        label="Wi-Fi Password", password=True, can_reveal_password=True, expand=True)

    vcard_first = ft.TextField(label="First Name", expand=True)
    vcard_last = ft.TextField(label="Last Name", expand=True)
    vcard_phone = ft.TextField(label="Phone Number", expand=True)
    vcard_email = ft.TextField(label="Email Address", expand=True)

    wa_phone = ft.TextField(
        label="Enter WhatsApp Number (with country code)", expand=True)
    wa_msg = ft.TextField(label="Enter Message (Optional)",
                          multiline=True, min_lines=2, expand=True)

    # --- STRUKTUR TABS MODERN ---
    content_url = ft.Container(padding=10, content=ft.Column([url_input]))
    content_wifi = ft.Container(padding=10, content=ft.Column(
        [ft.Row([wifi_ssid, wifi_enc]), wifi_pass]))
    content_vcard = ft.Container(padding=10, content=ft.Column(
        [ft.Row([vcard_first, vcard_last]), ft.Row([vcard_phone, vcard_email])]))
    content_wa = ft.Container(
        padding=10, content=ft.Column([wa_phone, wa_msg]))

    tab_contents = [content_url, content_wifi, content_vcard, content_wa]
    tab_content_container = ft.Container(content=tab_contents[0])

    # Tab Content Change Handler
    async def on_tab_change(e):
        tab_content_container.content = tab_contents[int(
            e.control.selected_index)]
        page.update()  # PERBAIKAN: Hapus await

    tabs = ft.Tabs(
        selected_index=0,
        length=4,
        animation_duration=300,
        on_change=on_tab_change,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="URL/Text"),
                        ft.Tab(label="Wi-Fi Access"),
                        ft.Tab(label="vCard"),
                        ft.Tab(label="WhatsApp"),
                    ]
                )
            ]
        )
    )

    # --- Visual Settings ---
    color_fill = ft.TextField(
        label="QR Code Color (Hex)", value="#000000", expand=True)
    color_back = ft.TextField(
        label="Background Color (Hex)", value="#FFFFFF", expand=True)
    box_size_slider = ft.Slider(
        min=1, max=20, divisions=19, value=10, label="Box Size: {value}")
    logo_status = ft.Text("No logo selected", italic=True)

    # --- PERBAIKAN FILE PICKERS (Sistem Asinkronus) ---
    logo_picker = ft.FilePicker()
    save_picker = ft.FilePicker()
    page.services.extend([logo_picker, save_picker])

    async def pick_logo_click(e):
        global uploaded_logo_path
        files = await logo_picker.pick_files(allowed_extensions=["png", "jpg", "jpeg"])

        if files and len(files) > 0:
            uploaded_logo_path = files[0].path
            logo_status.value = f"Selected: {files[0].name}"
        else:
            uploaded_logo_path = None
            logo_status.value = "No logo selected"
        page.update()

    async def save_qr_click(e):
        global current_qr_image
        if current_qr_image:
            save_path = await save_picker.save_file(file_name="ciptacode_qr.png", allowed_extensions=["png"])
            if save_path:
                final_path = save_path if save_path.endswith(
                    ".png") else f"{save_path}.png"
                current_qr_image.save(final_path, format="PNG")

    logo_button = ft.Button(
        "Upload Logo (Optional)",
        icon=ft.Icons.UPLOAD,
        on_click=pick_logo_click
    )

    visual_settings = ft.Column([
        ft.Text("Visual Settings", weight=ft.FontWeight.BOLD, size=18),
        ft.Row([color_fill, color_back]),
        ft.Text("Box Size:"),
        box_size_slider,
        ft.Row([logo_button, logo_status]),
        ft.Divider()
    ])

    # --- Result Container ---
    result_image = ft.Image(src="", width=300, height=300, visible=False)

    download_btn = ft.Button(
        "Download QR Code",
        icon=ft.Icons.DOWNLOAD,
        visible=False,
        on_click=save_qr_click
    )

    # --- Generation Logic ---
    async def generate_qr(e):
        global current_qr_image, uploaded_logo_path
        qr_data = None

        if tabs.selected_index == 0:
            if url_input.value:
                qr_data = url_input.value
        elif tabs.selected_index == 1:
            if wifi_ssid.value:
                enc = "WPA" if wifi_enc.value == "WPA/WPA2" else "WEP" if wifi_enc.value == "WEP" else "nopass"
                qr_data = f"WIFI:T:{enc};S:{wifi_ssid.value};P:{wifi_pass.value};;"
        elif tabs.selected_index == 2:
            if vcard_first.value or vcard_phone.value:
                qr_data = f"BEGIN:VCARD\nVERSION:3.0\nN:{vcard_last.value};{vcard_first.value}\nFN:{vcard_first.value} {vcard_last.value}\nTEL:{vcard_phone.value}\nEMAIL:{vcard_email.value}\nEND:VCARD"
        elif tabs.selected_index == 3:
            if wa_phone.value:
                encoded = urllib.parse.quote(wa_msg.value)
                qr_data = f"https://wa.me{wa_phone.value}?text={encoded}"

        if not qr_data:
            return

        qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=int(
            box_size_slider.value), border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=color_fill.value,
                            back_color=color_back.value).convert("RGBA")

        if uploaded_logo_path is not None:
            logo = Image.open(uploaded_logo_path)
            img_w, img_h = img.size
            logo_max_size = img_w // 4
            logo.thumbnail((logo_max_size, logo_max_size),
                           Image.Resampling.LANCZOS)

            logo_w, logo_h = logo.size
            pos = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)
            img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

        current_qr_image = img

        buf = BytesIO()
        img.save(buf, format="PNG")
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        result_image.src = f"data:image/png;base64,{img_base64}"
        result_image.visible = True
        download_btn.visible = True
        page.update()  # PERBAIKAN: Hapus await

    generate_btn = ft.Button(
        "Generate QR Code",
        icon=ft.Icons.QR_CODE,
        on_click=generate_qr,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE
    )

    # --- Add Everything to Page ---
    page.add(
        header,
        description,
        tabs,
        tab_content_container,
        ft.Divider(),
        visual_settings,
        ft.Row([generate_btn, download_btn],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(content=result_image,
                     alignment=ft.Alignment.CENTER, padding=20)
    )

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
