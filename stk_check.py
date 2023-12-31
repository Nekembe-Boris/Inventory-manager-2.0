"""Module tasked with the Verify Qty and Reports section of the ADVANCED TAB"""

from tkinter import Frame, Label, Entry, Button, IntVar, Radiobutton, END
from tkinter import messagebox
import os
import pandas
from functions import clear, list_box, listboxin
from entry import Input
from exit import Exit

BACKGROUND_COLOR = "#DDD0C8"
report_type = ["Entry Records", "Exit Records", "Ledger Records", "Current Stock Level", "Removed From Stock"]
FONT1=("Century Gothic", 12, "bold")
FONT2=("Century Gothic", 10, "bold")
FONT3 = ("Century Gothic", 8, "bold")


class StockLook():
    """
    - Class tasked with allowing the user to  the quantity of an Atricle,
    Delete an Article from Stock.
    - Can also generate ENTRY, EXIT, LEDGER and STOCK LEVEL reports
    """
    def __init__(self, frame:Frame, entry_update:Input, exit_update:Exit):
        self.frame = frame
        self.entry_update = entry_update
        self.exit_update = exit_update

        self.in_label = Label(master=self.frame, text="-------VERIFY QTY-------", font=FONT2, bg=BACKGROUND_COLOR, fg="red")
        self.in_label.place(x=150, y=50)

        self.article_id_label = Label(master=self.frame,text="ARTICLE-ID", font=FONT2, bg=BACKGROUND_COLOR)
        self.article_id_label.place(x=10, y=100)

        self.art_id_entry = Entry(master=self.frame, width=25)
        self.art_id_entry.place(x=10, y=120)

        self.ch_qty_label = Label(master=self.frame,text="Qty", font=FONT2, bg=BACKGROUND_COLOR)
        self.ch_qty_label.place(x=10, y=150)

        self.ch_qty_entry = Entry(master=self.frame, width=25)
        self.ch_qty_entry.place(x=10, y=170)

        self.ch_listbox = list_box(frame=self.frame, x_cor=200, y_cor=100, l_height=20, l_width=40)

        self.select_btn = Button(master=self.frame, text=" Select  ", font=FONT3, command=self.check)
        self.select_btn.place(x=143, y=300)

        self.select_btn = Button(master=self.frame, text=" Refresh", font=FONT3, command=self.refresh)
        self.select_btn.place(x=143, y=340)

        self.select_btn = Button(master=self.frame, text="Remove", font=FONT3, command=self.rem_in_stock)
        self.select_btn.place(x=143, y=380)

        self.report_label = Label(master=self.frame,text="-----REPORTS-----", font=FONT2, bg=BACKGROUND_COLOR, fg="red")
        self.report_label.place(x=150, y=465)

        self.radio_state = IntVar()
        x_cor = 10
        y_cor = 500

        for r_int, report in enumerate(report_type, 1):
            gen_radiobutton = Radiobutton(master=frame, text=report, value=r_int, variable=self.radio_state, font=FONT2, bg=BACKGROUND_COLOR)
            gen_radiobutton.place(x=x_cor, y=y_cor)
            y_cor += 50

        self.gen_excel_btn = Button(master=frame, text="GENERATE EXCEL SHEET",  font=FONT2, bg="#D7E5F0", command=self.generate_excel)
        self.gen_excel_btn.place(x=150, y=750)

        listboxin(self.ch_listbox)


    def refresh(self):
        """Reloads the listbox to get current stock data"""
        clear(self.ch_listbox)

        listboxin((self.ch_listbox))


    def check(self):
        """
        - Loops through the stock data to update the quantity and inserts the ArticleID and quantity of the selected material in their entries so that the current stock quantity can be known
        """
        selected = ""

        clear( self.art_id_entry, self.ch_qty_entry)

        for _ in self.ch_listbox.curselection():
            selected = self.ch_listbox.get(self.ch_listbox.curselection())

        try:
            stock_data = pandas.read_csv("./data/Stock_level.csv")
        except FileNotFoundError:
            print("No data")
        else:
            for (_, row) in stock_data.iterrows():

                if row.Article == selected:

                    self.art_id_entry.insert(END, row.ArticleID)
                    self.ch_qty_entry.insert(END, row.Quantity)


    def generate_excel(self):
        """
        Based on the record type chosen, this function will automatically create an xlsx file and open the file in MICROSOFT EXCEL
        """
        record_type = ["Entries", "Exit", "General_ledger", "Stock_level", "Removed"]

        radio_get = self.radio_state.get() - 1

        if radio_get < 0 :
            messagebox.showinfo(
                title="Error",
                message="No record was selected",
            )
        else:
            try:
                data = pandas.read_csv(f"./data/{record_type[radio_get]}.csv")
            except FileNotFoundError:
                messagebox.showinfo(
                    title="Error",
                    message="Record does not exit"
                )
            else:
                data.to_excel(f"./reports/{record_type[radio_get]}.xlsx", index=False)
                os.system(f'start "excel" "./reports/{record_type[radio_get]}.xlsx"')
            self.radio_state.set(-1)


    def rem_in_stock(self):
        """
        - Removes an Article from Stock and stores it in the Removed csv file.
        - Automatically updates the Article and ArticleID listboxes on the ENTRY and EXIT Tab
        """
        for i in self.ch_listbox.curselection():
            selected = self.ch_listbox.get(i)

        if not selected:
            messagebox.showinfo(
                    title="Error",
                    message="No Article was selected"
                )
        else:
            try:
                data = pandas.read_csv("./data/Stock_level.csv")
            except FileNotFoundError:
                messagebox.showinfo(
                        title="Error",
                        message="No Inventory"
                    )
            else:
                confirm = messagebox.askokcancel(
                        title="CONFIRM",
                        message=f"You are about to remove {selected} from Inventory"
                    )
                if confirm is True:

                    validate = messagebox.askokcancel(
                        title="VALIDATE",
                        message=f"Action can not be reversed.\nProceed in deleting {selected} from Inventory?"
                    )

                    if validate is True:
                        del_data = data[data.Article == selected]
                        rem_data = pandas.DataFrame(del_data)
                        sheet_data = pandas.DataFrame(data)
                        try:
                            pandas.read_csv("./data/Removed.csv")
                        except FileNotFoundError:
                            rem_data.to_csv("./data/Removed.csv", mode='a', index=False)
                        else:
                            rem_data.to_csv("./data/Removed.csv", mode='a', index=False, header=False)

                        for (i, row) in sheet_data.iterrows():

                            if row.Article == selected:
                                sheet_data = data.drop(data.index[i], axis=0)
                                sheet_data.to_csv("./data/Stock_level.csv", index=False)

                        del_index = self.ch_listbox.get(0, END).index(selected)
                        self.ch_listbox.delete(del_index)

                        clear(self.entry_update.article_listbox, self.entry_update.id_listbox, self.exit_update.article_listbox, self.exit_update.id_listbox)

                        listboxin(self.entry_update.article_listbox, self.entry_update.id_listbox)
                        listboxin(self.exit_update.article_listbox, self.exit_update.id_listbox)
