import tkinter as tk
from tkinter import ttk
import cv2
from pyzbar import pyzbar
from PIL import Image, ImageTk
import time

class BarcodeScannerApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Barcode & QR Code Scanner")

        # Define products database (for barcode items)
        self.products = {
            "1234567890128": {"name": "Milk", "price": 30.00},
            "9782123456803": {"name": "Bread", "price": 35.00},
            "8901491503051": {"name": "Orange Lays", "price": 10.00},
            "89007655": {"name": "DoubleMint", "price": 20.00},
            "7622202398735": {"name": "Dairy Milk Chocolate", "price": 55.00}
        }

        # Dictionary to track scanned items (barcodes)
        self.bill_items = {}

        # Discount related variables
        self.discount_applied = False
        self.discount_percent = 0  # e.g., 5 for 5% discount

        # Cooldown mechanism variables for barcode scanning
        self.last_scanned_barcode = None
        self.last_scanned_time = 0
        self.cooldown_duration = 2  # seconds

        # Setup GUI components
        self.setup_gui()

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open video stream.")
            self.window.destroy()
            return

        # Start the video update loop
        self.update_frame()

    def setup_gui(self):
        # Main container frames
        left_frame = tk.Frame(self.window, width=400, height=480)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(self.window, width=600, height=480)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Video display label
        self.video_label = tk.Label(left_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Bill display treeview
        columns = ("Product", "Qty", "Price", "Total")
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 16), rowheight=25)
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15, style="Treeview")
        self.tree.heading("Product", text="Product Name", anchor=tk.W)
        self.tree.heading("Qty", text="Qty", anchor=tk.CENTER)
        self.tree.heading("Price", text="Price (₹)", anchor=tk.E)
        self.tree.heading("Total", text="Total (₹)", anchor=tk.E)
        self.tree.column("Product", width=250, stretch=tk.YES)
        self.tree.column("Qty", width=80, anchor=tk.CENTER)
        self.tree.column("Price", width=100, anchor=tk.E)
        self.tree.column("Total", width=100, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Button frame for additional controls
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=5)

        # Remove Selected Item Button
        remove_btn = tk.Button(button_frame, text="Remove Selected Item", font=('Arial', 14),
                               command=self.remove_selected_item)
        remove_btn.pack(side=tk.LEFT, padx=5)

        # Create Remove Discount Button (do not pack it here; it will be packed dynamically)
        self.remove_discount_btn = tk.Button(button_frame, text="Remove Discount", font=('Arial', 14),
                                             command=self.remove_discount)

        # Total price label
        self.total_label = tk.Label(right_frame, text="Total Bill Amount: ₹0.00", 
                                    font=('Arial', 18, 'bold'), fg='blue')
        self.total_label.pack(pady=10, anchor=tk.E)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Resize and convert frame
            frame = cv2.resize(frame, (400, 300))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Decode codes (barcodes and QR codes)
            codes = pyzbar.decode(gray)
            for code in codes:
                code_data = code.data.decode("utf-8")
                code_type = code.type  # e.g., "QRCODE" or other barcode types
                (x, y, w, h) = code.rect

                if code_type.upper() == "QRCODE":
                    # Draw bounding box for QR code in blue
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    text = f"{code_data} (QR)"
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 0, 0), 2)
                    self.process_qr_code(code_data)
                else:
                    # Draw bounding box for barcodes in green
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = f"{code_data} ({code_type})"
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)
                    self.add_to_bill_with_cooldown(code_data)

            # Display frame in Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.window.after(10, self.update_frame)

    def add_to_bill_with_cooldown(self, barcode):
        current_time = time.time()
        if (barcode != self.last_scanned_barcode or 
            (current_time - self.last_scanned_time) >= self.cooldown_duration):
            self.add_to_bill(barcode)
            self.last_scanned_barcode = barcode
            self.last_scanned_time = current_time

    def add_to_bill(self, barcode):
        if barcode in self.products:
            product = self.products[barcode]
            if barcode in self.bill_items:
                self.bill_items[barcode]["quantity"] += 1
            else:
                self.bill_items[barcode] = {
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": 1
                }
            self.update_bill_display()

    def update_bill_display(self):
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0.0
        # Insert product rows
        for key, item in self.bill_items.items():
            item_total = item["price"] * item["quantity"]
            total += item_total
            self.tree.insert("", "end", iid=key, values=(
                item["name"],
                item["quantity"],
                f"{item['price']:.2f}",
                f"{item_total:.2f}"
            ))
        
        # If discount is applied, add a discount row and show the Remove Discount button
        if self.discount_applied and self.discount_percent > 0:
            discount_amount = total * (self.discount_percent / 100)
            self.tree.insert("", "end", iid="discount", values=(
                "Discount Applied", "", "", f"-{discount_amount:.2f}"
            ))
            total_after_discount = total - discount_amount
            self.total_label.config(text=f"Total Bill Amount: ₹{total_after_discount:.2f} ({self.discount_percent}% discount applied)")
            # Show the Remove Discount button if not already visible
            if not self.remove_discount_btn.winfo_ismapped():
                self.remove_discount_btn.pack(side=tk.LEFT, padx=5)
        else:
            self.total_label.config(text=f"Total Bill Amount: ₹{total:.2f}")
            # Hide the Remove Discount button if discount is not applied
            self.remove_discount_btn.pack_forget()

    def process_qr_code(self, qr_data):
        # Only apply discount if no discount has been applied yet
        if not self.discount_applied:
            try:
                discount = int(qr_data)
                if 0 < discount <= 100:
                    self.discount_percent = discount
                    self.discount_applied = True
                    print(f"Applying {discount}% discount.")
                    self.update_bill_display()
                else:
                    print("Invalid discount value scanned:", qr_data)
            except ValueError:
                print("QR code does not contain a valid discount percentage:", qr_data)

    def remove_selected_item(self):
        selected = self.tree.selection()
        if selected:
            for item_id in selected:
                if item_id == "discount":
                    print("Please use the 'Remove Discount' button to remove the discount.")
                else:
                    if item_id in self.bill_items:
                        del self.bill_items[item_id]
            self.update_bill_display()

    def remove_discount(self):
        if self.discount_applied:
            self.discount_applied = False
            self.discount_percent = 0
            print("Discount removed.")
            self.update_bill_display()

    def on_closing(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = BarcodeScannerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
