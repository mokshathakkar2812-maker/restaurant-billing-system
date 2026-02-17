import csv,os

import pywhatkit
import pywhatkit as kit
from datetime import datetime

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtWidgets import QMainWindow
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from shreeji_food_menu_ui import Ui_MainWindow

import sys,glob,time,pyautogui,webbrowser
#from PyQt5.QtWidgets import QMessageBox, QInputDialog


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.s1 = Ui_MainWindow()
        self.s1.setupUi(self)
        self.category = ['--Select--','--Fast Food--','Pizza','Burger','Drinks']
        #category1 = ['abc','def']
        self.orders = []
        self.total_amount = 0
        self.csv_file = "transaction1.csv"
        self.last_pdf_path = ""

        #generated a menu
        self.menu = {
            "Pizza": {
                "Margherita-Small": {"price": 150, "img": "images/margherita.jpg"},
                "Margherita-Medium": {"price": 210, "img": "images/margherita.jpg"},
                "Margherita-Large": {"price": 300, "img": "images/margherita.jpg"},
                "Farmhouse-Small": {"price": 200, "img": "images/farmhouse1.jpg"},
                "Farmhouse-Medium": {"price": 250, "img": "images/farmhouse1.jpg"},
                "Farmhouse-Large": {"price": 310, "img": "images/farmhouse1.jpg"},
                "Paneer Tikka-Small": {"price": 220, "img": "images/paneer.jpg"},
                "Paneer Tikka-Medium": {"price": 280, "img": "images/paneer.jpg"},
                "Paneer Tikka-Large": {"price": 320, "img": "images/paneer.jpg"}



            },
            "Burger": {
                "Veggie Burger-Small": {"price": 80, "img": "images/veggie.jpg"},
                "Veggie Burger-large": {"price": 80, "img": "images/veggie.jpg"},
                "Cheese Burger-Small": {"price": 100, "img": "images/cheese_burger.jpg"},
                "Cheese Burger-Large": {"price": 100, "img": "images/cheese_burger.jpg"},
                "Aloo Tikki Burger-Small": {"price": 90, "img": "images/aloo.jpg"},
                "Aloo Tikki Burger-Large": {"price": 90, "img": "images/aloo.jpg"}

            },
            "Drinks": {
                "Coke": {"price": 40, "img": "images/coke.jpg"},
                "Pepsi": {"price": 40, "img": "images/pepsi.jpg"},
                "Cold Coffee": {"price": 70, "img": "images/coffee.jpg"},
                "Lemonade": {"price": 60, "img": "images/lemonade.jpeg"}
            }
        }


        self.s1.cbox_cat.addItems(self.category)
        self.s1.btn_exit.clicked.connect(self.exit_app)
        self.s1.cbox_cat.currentIndexChanged.connect(self.set_items)
        self.s1.lst_item.currentItemChanged.connect(self.show_image)
        self.s1.btn_order.clicked.connect(self.add_order)
        self.s1.btn_checkout.clicked.connect(self.checkout)
        self.s1.btn_cancel_last.clicked.connect(self.cancel_last_item)
        self.s1.btn_cancel_ent.clicked.connect(self.cancel_all_orders)
        self.s1.btn_next.clicked.connect(self.next_order)
        self.s1.btn_gen_pdf.clicked.connect(self.generate_pdf)
        self.s1.btn_summary.clicked.connect(self.daily_summary)
        self.s1.btn_monthly_summary.clicked.connect(self.monthly_summary)
        self.s1.btn_weekly_summary.clicked.connect(self.weekly_summary)
        self.s1.btn_share.clicked.connect(self.send_whatsapp_bill)
        self.s1.btn_share_wp.clicked.connect(self.send_whatsapp_pdf1)



    def exit_app(self):
        sys.exit()

    def set_items(self):
        category = self.s1.cbox_cat.currentText()#currentText() = it returns the present text from combo box to the variable
        self.s1.lst_item.clear()
        if category in self.menu:
            for item, details in self.menu[category].items():
                display_text = f"{item} - ₹{details['price']}"
                self.s1.lst_item.addItem(display_text)
                self.s1.sbox_quantity.setValue(1)

    def show_image(self):
        category = self.s1.cbox_cat.currentText()
        item = self.s1.lst_item.currentItem()
        if category in self.menu and item:
            item_name = item.text().split(" - ")[0]  # get clean name
            img_path = self.menu[category][item_name]["img"]
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path).scaled(200, 150)
                self.s1.lbl_image.setPixmap(pixmap)
            else:
                self.s1.lbl_image.setText("Image not found")



    def add_order(self):
        category = self.s1.cbox_cat.currentText()
        item = self.s1.lst_item.currentItem()
        print(item,category)

        if not item:
            QMessageBox.warning(self, "Warning", "Please select an item!")
            return

        # Extract actual item name
        item_name = item.text().split(" - ")[0]
        base_price = self.menu[category][item_name]["price"]
        print(item_name,base_price)

        # Size adjustment
        # if self.small_radio.isChecked():
        #     price = base_price * 0.8
        #     size_note = "Small"
        # elif self.large_radio.isChecked():
        #     price = base_price * 1.3
        #     size_note = "Large"
        # else:
        #     price = base_price
        #     size_note = "Medium"

        # Extras
        # extras = []
        # if self.cheese_check.isChecked():
        #     extras.append("Cheese")
        #     price += 20
        # if self.sauce_check.isChecked():
        #     extras.append("Sauce")
        #     price += 10
        # if self.fries_check.isChecked():
        #     extras.append("Fries")
        #    price += 50

        qty = self.s1.sbox_quantity.value()
        total = base_price * qty
        print(qty,total)

        order_line = (
            f"{qty} x {item_name} (₹{base_price} each) "
            f"= ₹{total:.2f}"
        )
        self.orders.append(order_line)
        self.total_amount += total

        self.s1.te_bill.append(order_line)

        # Save record to CSV
        self.csv_file = "transaction1.csv"
        now = datetime.now()
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)#writer is an object of csv file
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), item_name, qty, total])

    def checkout(self):
        response = QMessageBox.question(self,"Checkout","Confirm your order?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            if not self.orders:
                QMessageBox.warning(self, "Empty", "No items in order!")
            else:
                self.s1.te_bill.append("\n------------------")
                self.s1.te_bill.append(f"Total Bill: ₹{self.total_amount:.2f}")
                self.s1.te_bill.append("------------------")
                #self.s1.te_bill.clear()



    def cancel_last_item(self):
        """Removes the last added item from the order."""
        if not self.orders:
            QMessageBox.warning(self, "Empty", "No items to cancel!")
            return

        last_item = self.orders.pop()  # remove from list
        # extract total from last line (₹xxx.xx at the end)
        try:
            last_price = float(last_item.split("₹")[-1])
            #last_price = float(last_item.split("-")[-1])
            self.total_amount -= last_price
        except:
            pass

        # Refresh bill text
        self.s1.te_bill.clear()
        for order in self.orders:
            self.s1.te_bill.append(order)
        self.s1.te_bill.append(f"\nCurrent Total: ₹{self.total_amount:.2f}")
        QMessageBox.information(self, "Cancelled", "Last item removed successfully!")

    def cancel_all_orders(self):
        """Clears the entire current order."""
        if not self.orders:
            QMessageBox.warning(self, "Empty", "No items to cancel!")
            return

        confirm = QMessageBox.question(
            self, "Confirm Cancel",
            "Are you sure you want to cancel the entire order?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.orders.clear()
            self.total_amount = 0
            self.s1.te_bill.clear()
            self.s1.sbox_quantity.setValue(1)
            self.s1.lst_item.clear()
            self.s1.cbox_cat.setCurrentText(self.category[0])
            self.s1.lbl_image.setText("  ")
            QMessageBox.information(self, "Cancelled", "All items removed successfully!")


    def next_order(self):
        """Clears the entire current order."""
        self.orders.clear()
        self.total_amount = 0
        self.s1.te_bill.clear()
        self.s1.sbox_quantity.setValue(1)
        self.s1.lst_item.clear()
        self.s1.cbox_cat.setCurrentText(self.category[0])
        self.s1.lbl_image.setText("  ")
        QMessageBox.information(self, "next order", "Moving to the next order!")

    def generate_pdf(self):
        """Generate a professional PDF bill"""
        if not self.orders:
            QMessageBox.warning(self, "Empty", "No items in order!")
            return

        current_date_time = datetime.now()
        fname = 'Bill_'+current_date_time.strftime("%Y_%m_%d_%H_%M_%S")+'.pdf'
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF Bill", fname, "PDF Files (*.pdf)")
        filepath = f"./bills/{filename}"
        if filename:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Header
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width/2, height-50, "🍴 Mini Restaurant Bill 🍴")

            c.setFont("Helvetica", 12)
            c.drawString(50, height-100, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Order details
            y = height - 150
            c.setFont("Helvetica", 12)
            for order in self.orders:
                c.drawString(50, y, order)
                y -= 20
                if y < 100:  # new page if too long
                    c.showPage()
                    y = height - 50

            # Total
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y-20, f"Total: ₹{self.total_amount:.2f}")

            c.save()
            self.last_pdf_path = filepath
            print(self.last_pdf_path)
            QMessageBox.information(self, "Saved", f"PDF Bill saved as {filename}")

            # Reset order for new customer
            self.orders.clear()
            self.total_amount = 0
            self.s1.te_bill.clear()

    def daily_summary(self):
        """Show total transactions and sales for today"""
        today = str(datetime.now().date())
        count = 0
        total_sales = 0
        print(today)
        print(self.csv_file)
        with open(self.csv_file, "r") as f:
            reader = csv.DictReader(f)
            #print(reader)
            for row in reader:
                print(row["Date"])
                if row["Date"] == today:
                    count += 1
                    total_sales += float(row["Price"])


        QMessageBox.information(
            self, "Daily Summary",
            f"Date: {today}\nTransactions: {count}\nTotal Sales: ₹{total_sales:.2f}"
        )

    def monthly_summary(self):
        """Show total transactions and sales for a selected month."""
        from PyQt5.QtWidgets import QInputDialog

        month, ok = QInputDialog.getText(
            self, "Monthly Summary",
            "Enter month (in YYYY-MM format):"
        )

        if not ok or not month.strip():
            return

        count = 0
        total_sales = 0.0

        try:
            with open(self.csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Date"].startswith(month.strip()):
                        count += 1
                        total_sales += float(row["Price"])

            if count == 0:
                QMessageBox.information(
                    self, "Monthly Summary",
                    f"No transactions found for {month}."
                )
            else:
                QMessageBox.information(
                    self, "Monthly Summary",
                    f"Month: {month}\nTransactions: {count}\nTotal Sales: ₹{total_sales:.2f}"
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read records: {e}")

    def weekly_summary(self):
        """Show total transactions and sales between two dates."""
        from PyQt5.QtWidgets import QInputDialog
        from datetime import datetime

        start_date_str, ok1 = QInputDialog.getText(
            self, "Weekly Summary", "Enter start date (YYYY-MM-DD):"
        )
        if not ok1 or not start_date_str.strip():
            return

        end_date_str, ok2 = QInputDialog.getText(
            self, "Weekly Summary", "Enter end date (YYYY-MM-DD):"
        )
        if not ok2 or not end_date_str.strip():
            return

        try:
            start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()

            count = 0
            total_sales = 0.0

            with open(self.csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                    if start_date <= row_date <= end_date:
                        count += 1
                        total_sales += float(row["Price"])

            if count == 0:
                QMessageBox.information(
                    self, "Weekly Summary",
                    f"No transactions found between {start_date} and {end_date}."
                )
            else:
                QMessageBox.information(
                    self, "Weekly Summary",
                    f"Week Summary:\nFrom: {start_date}\nTo: {end_date}\n"
                    f"Transactions: {count}\nTotal Sales: ₹{total_sales:.2f}"
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid input or file error:\n{e}")

    import pywhatkit
    from PyQt5.QtWidgets import QMessageBox, QInputDialog

    def send_whatsapp_bill(self):
        # Get bill text from your bill text area
        bill_text = self.s1.te_bill.toPlainText().strip()
        print(bill_text)

        if not bill_text:
            QMessageBox.warning(self, "No Bill", "Please generate the bill first before sending.")
            return

        # Ask for phone number
        phone_no, ok = QInputDialog.getText(self, "Send Bill",
                                            "Enter WhatsApp number with country code (+91XXXXXXXXXX):")

        if ok and phone_no:
            try:
                # Send instantly (no time scheduling)
                pywhatkit.sendwhatmsg_instantly(phone_no,bill_text,15,True,3)

                QMessageBox.information(self, "Sent", f"Bill has been sent to {phone_no} successfully on WhatsApp.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message.\nError: {e}")
        else:
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")

    def send_whatsapp_pdf(self):

        # Ask for phone number
        phone_no, ok = QInputDialog.getText(
            self, "Send Bill PDF", "Enter WhatsApp number with country code (+91XXXXXXXXXX):"
        )
        print(phone_no)
        if not ok or not phone_no:
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return

        # Folder where all PDF bills are saved
        pdf_folder = "./advanced_learning"  # <-- change this to your folder path
        print(pdf_folder)
        pdf_path = os.path.abspath(self.last_pdf_path)

        # Find the latest PDF file
        list_of_pdfs = glob.glob(os.path.join(pdf_folder, "*.pdf"))
        print(list_of_pdfs)
        if not list_of_pdfs:
            QMessageBox.warning(self, "No PDF Found", "No bill PDF found in the folder.")
            return

        latest_pdf = max(list_of_pdfs, key=os.path.getmtime)
        print(latest_pdf)
        pdf_path = os.path.abspath(latest_pdf)
        print(pdf_path)

        try:
            # Open WhatsApp Web chat for the entered number
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_no}")
            QMessageBox.information(self, "WhatsApp", "Opening WhatsApp Web... Please wait 15 seconds.")
            time.sleep(15)

            # Attach and send the latest bill PDF
            pyautogui.hotkey('ctrl', 'shift', 'a')  # Opens file picker (works in newer WhatsApp Web)
            time.sleep(2)
            pyautogui.write(pdf_path)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            pyautogui.press('enter')

            QMessageBox.information(self, "Success", f"Latest Bill PDF sent to {phone_no} successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send PDF.\nError: {e}")

    def send_whatsapp_pdf1(self):
        print(self.last_pdf_path)
        # Check if PDF was generated
        # if not hasattr(self, 'last_pdf_path') or not os.path.exists(self.last_pdf_path):
        #     QMessageBox.warning(self, "No PDF", "Please generate the bill first before sending.")
        #     return

        phone_no, ok = QInputDialog.getText(
            self, "Send Bill PDF", "Enter WhatsApp number with country code (+91XXXXXXXXXX):"
        )

        if not ok or not phone_no:
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return

        pdf_path = os.path.abspath(self.last_pdf_path)
        print(pdf_path)

        try:
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_no}")
            QMessageBox.information(self, "WhatsApp", "Opening WhatsApp Web... Please wait 15 seconds.")
            time.sleep(15)

            pyautogui.hotkey('ctrl', 'shift', 'a')
            time.sleep(2)
            pyautogui.write(pdf_path)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            pyautogui.press('enter')

            QMessageBox.information(self, "Success", f"Bill PDF sent to {phone_no} successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send PDF.\nError: {e}")


def main():

    app = QApplication(sys.argv)
    style1 = open('QSS/coffee.qss','r')
    app.setStyleSheet(style1.read())
    window = Main()
    window.show()
    #sys.exit(app.exec_())
    app.exec_()


main()