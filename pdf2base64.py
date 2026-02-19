import base64

with open("resume.pdf", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)