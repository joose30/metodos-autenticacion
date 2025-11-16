import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
from ports.qr_service_port import QRServicePort

class QRGeneratorAdapter(QRServicePort):
    def generate_qr_image(self, uri: str) -> bytes:
        buffer = BytesIO()
        img = qrcode.make(uri, image_factory=PilImage)
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()