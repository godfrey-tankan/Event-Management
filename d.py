import cv2
from pyzbar.pyzbar import decode
import time

class BarcodeScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.used_codes = {}

    def scan_barcode(self):
        while True:
            success, frame = self.cap.read()

            for code in decode(frame):
                barcode_data = code.data.decode('utf-8')
                if barcode_data not in self.used_codes:
                    print(f'Participant with barcode {barcode_data} has crossed the checkpoint.')
                    self.used_codes[barcode_data] = time.time()  # Store the current time
                    time.sleep(10)  # Wait for ten seconds before scanning again
                else:
                    print(f'Participant with barcode {barcode_data} has already crossed the checkpoint.')
                    # Calculate duration
                    duration = time.time() - self.used_codes[barcode_data]
                    print(f'Time taken for participant with barcode {barcode_data}: {duration} seconds')
                    del self.used_codes[barcode_data]  # Remove the barcode data from dictionary

            cv2.imshow('Barcode Scanner', frame)
            cv2.waitKey(1)

if __name__ == "__main__":
    scanner = BarcodeScanner()
    scanner.scan_barcode()
