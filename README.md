# Barcode Scanner & Bill Maker App

A simple and efficient desktop application built with **Python** and **Tkinter**, designed for small stores to quickly generate bills by scanning item barcodes. The app supports **QR code-based discount vouchers** and calculates totals in real-time.

## Features

- 🔍 Scan barcodes of registered items
- 🧾 Automatically adds items to the bill as they are scanned
- 💸 Real-time total calculation
- 🎟️ Apply discount vouchers by scanning QR codes (5% and 10%)
- Simple and clean UI using Tkinter

## Technologies Used

- **Python 3**
- **Tkinter** for GUI
- **pyzbar / Pillow** for barcode and QR code scanning

## How It Works

1. Register items with their barcodes and prices (can be hardcoded or loaded from a file/database).
2. Start the app and begin scanning.
3. Each time a barcode is scanned, the corresponding item is added to the current bill.
4. Scan a QR code voucher to apply a discount:
   - 5% off voucher
   - 10% off voucher
5. Total is updated in real-time and displayed at the bottom.
