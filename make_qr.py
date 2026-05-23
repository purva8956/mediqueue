import qrcode

# Secret protected registration route
link = " https://botanical-pronounce-pelt.ngrok-free.dev/registration/hospital2026"

# Generate QR
img = qrcode.make(link)

# Save QR image
with open("static/hospital_qr.png", "wb") as f:
	img.save(f)
   
print("✅ Success! QR code generated.")