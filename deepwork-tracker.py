import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from datetime import datetime
import calendar

# ----- COLOR & FONT CONSTANTS -----
BACKGROUND_COLOR = "#f5f5f5"
PRIMARY_COLOR = "#2ecc71"      # Green
SECONDARY_COLOR = "#f1c40f"    # Yellow
TEXT_COLOR = "#333333"
FONT_HEADER = ("Helvetica", 16, "bold")
FONT_SUBHEADER = ("Helvetica", 12, "bold")
FONT_NORMAL = ("Helvetica", 10)
COMPLETED_BG = "#e8f8f5"

# Button styling dict
BUTTON_STYLE = {
    "bg": PRIMARY_COLOR,
    "fg": "white",
    "activebackground": "#27ae60",
    "activeforeground": "white",
    "relief": "flat",
    "padx": 10,
    "pady": 5,
    "font": FONT_NORMAL
}

DATA_FILE = "deepwork_tracker_data.json"

class CustomDialog(tk.Toplevel):
    """Custom dialog for better-looking input dialogs."""
    def __init__(self, parent, title, prompt, field_type="string", default=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.configure(bg=BACKGROUND_COLOR)
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Prompt label
        tk.Label(
            self,
            text=prompt,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=FONT_NORMAL,
            wraplength=380
        ).pack(pady=(20, 10))
        
        # Entry or spinbox based on field type
        if field_type == "integer":
            self.entry = ttk.Spinbox(self, from_=1, to=31, font=FONT_NORMAL, width=30)
            self.entry.set(default if default else 30)
        else:
            self.entry = ttk.Entry(self, font=FONT_NORMAL, width=30)
            self.entry.insert(0, default)
        
        self.entry.pack(pady=10, padx=20)
        
        # Buttons
        btn_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        btn_frame.pack(pady=(10, 20), fill="x")
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            **{**BUTTON_STYLE, "bg": "#e74c3c"}
        )
        cancel_btn.pack(side="left", padx=(20, 10))
        
        ok_btn = tk.Button(btn_frame, text="OK", command=self.ok)
        for key, value in BUTTON_STYLE.items():
            ok_btn[key] = value
        ok_btn.pack(side="right", padx=(10, 20))
        
        # Center the dialog window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.entry.focus_set()
        self.bind("<Return>", lambda event: self.ok())
        self.bind("<Escape>", lambda event: self.cancel())
        
        self.wait_window(self)
    
    def ok(self):
        self.result = self.entry.get()
        self.destroy()
        
    def cancel(self):
        self.result = None
        self.destroy()


class DeepWorkTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Deep-Work-Tracker")
        self.master.geometry("800x600")
        self.master.configure(bg=BACKGROUND_COLOR)
        
        # Load existing data if any
        self.data = self.load_data()
        
        # Create a style for the app
        self.style = ttk.Style()
        self.style.configure("TCheckbutton", background=BACKGROUND_COLOR, font=FONT_NORMAL)
        self.style.configure("TFrame", background=BACKGROUND_COLOR)
        
        # ----- HEADER (only one place for "Deep Work Tracker") -----
        self.header_frame = tk.Frame(self.master, bg=PRIMARY_COLOR, height=60)
        self.header_frame.pack(fill="x")
        
        tk.Label(
            self.header_frame,
            text="You're a champion",
            font=("Helvetica", 18, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(pady=10)
        
        # ----- MAIN CONTENT FRAME -----
        self.content_frame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_main_menu()
        
        # ----- FOOTER -----
        self.footer_frame = tk.Frame(self.master, bg="#ecf0f1", height=30)
        self.footer_frame.pack(fill="x", side="bottom")
        
        current_date = datetime.now().strftime("%B %d, %Y")
        tk.Label(
            self.footer_frame,
            text=f"Today: {current_date}",
            font=("Helvetica", 8),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(pady=5)

    def show_main_menu(self):
        """Show the main menu with options to generate, open, or delete a tracker."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        button_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=60)
        
        generate_btn = tk.Button(
            button_frame,
            text="Generate new Deep Work Tracker",
            command=self.generate_tracker_prompt,
            width=30,
            height=2
        )
        for key, value in BUTTON_STYLE.items():
            generate_btn[key] = value
        generate_btn.pack(pady=10)
        
        if self.data:
            existing_btn = tk.Button(
                button_frame,
                text="Open Existing Tracker",
                command=self.open_existing_tracker,
                width=30,
                height=2
            )
            for key, value in BUTTON_STYLE.items():
                existing_btn[key] = value
            existing_btn["bg"] = SECONDARY_COLOR
            existing_btn["activebackground"] = "#d4ac0d"
            existing_btn.pack(pady=10)
            
            delete_btn = tk.Button(
                button_frame,
                text="Delete Existing Tracker",
                command=self.delete_existing_tracker,
                width=30,
                height=2
            )
            for key, value in BUTTON_STYLE.items():
                delete_btn[key] = value
            delete_btn["bg"] = "#e74c3c"
            delete_btn["activebackground"] = "#c0392b"
            delete_btn.pack(pady=10)
            
            available_months = ", ".join(list(self.data.keys()))
            tk.Label(
                self.content_frame,
                text=f"Available trackers: {available_months}",
                font=FONT_NORMAL,
                bg=BACKGROUND_COLOR,
                fg=TEXT_COLOR
            ).pack(pady=(20, 0))

    def get_custom_string(self, title, prompt, default=""):
        dialog = CustomDialog(self.master, title, prompt, "string", default)
        return dialog.result
        
    def get_custom_integer(self, title, prompt, default=""):
        dialog = CustomDialog(self.master, title, prompt, "integer", default)
        if dialog.result:
            try:
                return int(dialog.result)
            except:
                return None
        return None

    def generate_tracker_prompt(self):
        current_month = datetime.now().strftime("%B")
        month = self.get_custom_string("Month", "What month is this?", current_month)
        if not month:
            return

        if month in self.data:
            overwrite = messagebox.askyesno(
                "Tracker exists!",
                f"A tracker for {month} already exists. Overwrite?"
            )
            if not overwrite:
                return

        current_year = datetime.now().year
        try:
            month_num = datetime.strptime(month, "%B").month
            days_in_month = calendar.monthrange(current_year, month_num)[1]
            default_days = str(days_in_month)
        except:
            default_days = "30"

        days = self.get_custom_integer("Days", f"How many days in {month}?", default_days)
        if not days or days < 1:
            return

        tasks_input = self.get_custom_string(
            "Tasks",
            "Enter tasks to track (comma-separated):\nFor example: Running, Meditation, Reading",
            "Meditation, Reading, Exercise"
        )
        if not tasks_input:
            return
        
        tasks = [t.strip() for t in tasks_input.split(",")]

        self.data[month] = {
            "days": days,
            "tasks": tasks,
            "progress": {}
        }
        self.save_data()
        self.open_tracker(month)

    def open_existing_tracker(self):
        if not self.data:
            messagebox.showinfo("No Trackers", "No existing trackers found. Create a new one first.")
            return

        month_list = list(self.data.keys())
        month_str = ", ".join(month_list)
        
        month = self.get_custom_string("Choose Month", f"Available trackers: {month_str}\n\nEnter the month to open:")
        if not month:
            return
        if month not in self.data:
            messagebox.showerror("Error", f"No tracker found for {month}")
            return
        
        self.open_tracker(month)

    def delete_existing_tracker(self):
        if not self.data:
            messagebox.showinfo("No Trackers", "No existing trackers found. Create a new one first.")
            return
        
        month_list = list(self.data.keys())
        month_str = ", ".join(month_list)
        
        month = self.get_custom_string("Delete Tracker", f"Available trackers: {month_str}\n\nEnter the month to delete:")
        if not month:
            return
        if month not in self.data:
            messagebox.showerror("Error", f"No tracker found for {month}")
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the tracker for '{month}'?")
        if confirm:
            del self.data[month]
            self.save_data()
            messagebox.showinfo("Deleted", f"Tracker for {month} has been deleted.")
            self.show_main_menu()

    def open_tracker(self, month):
        """Show the day/task grid with checkboxes for a specific month, with improved alignment."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.month = month
        self.days = self.data[month]["days"]
        self.tasks = self.data[month]["tasks"]
        self.progress = self.data[month]["progress"]
        
        completed, total = 0, 0
        for day in range(1, self.days + 1):
            day_str = str(day)
            if day_str in self.progress:
                for task in self.tasks:
                    if self.progress[day_str].get(task, False):
                        completed += 1
                    total += 1
        
        if total > 0:
            progress_pct = (completed / total) * 100
            progress_text = f"Progress: {completed}/{total} ({progress_pct:.1f}%)"
        else:
            progress_text = "Progress: 0/0 (0%)"
        
        top_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        top_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            top_frame,
            text=month,
            font=FONT_HEADER,
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            top_frame,
            text=progress_text,
            font=FONT_SUBHEADER,
            bg=BACKGROUND_COLOR,
            fg=SECONDARY_COLOR
        ).pack(side="right")
        
        canvas_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)
        
        # ---- Important: Configure columns for better alignment ----
        # Column 0 = "Day" (narrower); columns 1..N = tasks
        scrollable_frame.grid_columnconfigure(0, weight=0, minsize=50)  # day column
        for i in range(1, len(self.tasks) + 1):
            scrollable_frame.grid_columnconfigure(i, weight=1, uniform="taskcol")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header row
        day_label = tk.Label(
            scrollable_frame,
            text="Day",
            font=FONT_SUBHEADER,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        )
        day_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 10))
        
        for i, task in enumerate(self.tasks):
            task_label = tk.Label(
                scrollable_frame,
                text=task,
                font=FONT_SUBHEADER,
                bg=BACKGROUND_COLOR,
                fg=TEXT_COLOR
            )
            task_label.grid(row=0, column=i+1, sticky="nsew", padx=5, pady=(5, 10))
        
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=len(self.tasks) + 1, sticky="ew", pady=5
        )
        
        # Create rows for each day
        self.check_vars = {}
        for day in range(1, self.days + 1):
            day_str = str(day)
            row_index = day + 1  # offset for header & separator

            # Day label in column 0
            day_label = tk.Label(
                scrollable_frame,
                text=day_str,
                font=FONT_NORMAL,
                bg=BACKGROUND_COLOR,
                fg=TEXT_COLOR
            )
            day_label.grid(row=row_index, column=0, sticky="nsew", padx=5, pady=5)
            
            self.check_vars[day] = {}
            for t_idx, task in enumerate(self.tasks):
                var = tk.BooleanVar()
                if day_str in self.progress and task in self.progress[day_str]:
                    var.set(self.progress[day_str][task])
                else:
                    var.set(False)
                
                cb = ttk.Checkbutton(
                    scrollable_frame,
                    variable=var,
                    command=self.save_current_state,
                    style="TCheckbutton"
                )
                cb.grid(row=row_index, column=t_idx+1, padx=5, pady=5, sticky="nsew")
                self.check_vars[day][task] = var
        
        button_frame = tk.Frame(self.content_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(fill="x", pady=20)
        
        back_btn = tk.Button(button_frame, text="Back to Main Menu", command=self.back_to_main, width=15)
        for key, value in BUTTON_STYLE.items():
            back_btn[key] = value
        back_btn["bg"] = "#7f8c8d"
        back_btn["activebackground"] = "#707b7c"
        back_btn.pack(side="left", padx=5)
        
        check_btn = tk.Button(button_frame, text="Check Progress", command=self.check_month_completion, width=15)
        for key, value in BUTTON_STYLE.items():
            check_btn[key] = value
        check_btn.pack(side="right", padx=5)

    def save_current_state(self):
        for day in range(1, self.days + 1):
            day_str = str(day)
            if day_str not in self.progress:
                self.progress[day_str] = {}
            for task in self.tasks:
                self.progress[day_str][task] = self.check_vars[day][task].get()
        
        self.data[self.month]["progress"] = self.progress
        self.save_data()

    def check_month_completion(self):
        completed = 0
        total = 0
        for day in range(1, self.days + 1):
            day_str = str(day)
            if day_str in self.progress:
                for task in self.tasks:
                    if self.progress[day_str].get(task, False):
                        completed += 1
                    total += 1
        
        if total > 0:
            completion_rate = (completed / total) * 100
            message = f"Your completion rate: {completion_rate:.1f}%\n({completed} out of {total} tasks completed)"
        else:
            message = "No tasks tracked yet."

        congrats_window = tk.Toplevel(self.master)
        congrats_window.title("Congratulations!")
        congrats_window.geometry("400x300")
        congrats_window.configure(bg=BACKGROUND_COLOR)
        
        congrats_window.transient(self.master)
        congrats_window.grab_set()
        
        tk.Label(
            congrats_window,
            text="🎉 Congratulations! 🎉",
            font=("Helvetica", 18, "bold"),
            bg=BACKGROUND_COLOR,
            fg=PRIMARY_COLOR
        ).pack(pady=(30, 10))
        
        tk.Label(
            congrats_window,
            text="Hurrah! You're one step away from becoming\nthe best version of yourself!",
            font=FONT_SUBHEADER,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=10)
        
        stats_frame = tk.Frame(congrats_window, bg=COMPLETED_BG, padx=20, pady=10)
        stats_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(
            stats_frame,
            text=message,
            font=FONT_NORMAL,
            bg=COMPLETED_BG,
            fg=TEXT_COLOR
        ).pack(pady=10)
        
        close_btn = tk.Button(congrats_window, text="Continue My Journey", command=congrats_window.destroy)
        for key, value in BUTTON_STYLE.items():
            close_btn[key] = value
        close_btn.pack(pady=20)
        
        # Center the popup
        congrats_window.update_idletasks()
        width = congrats_window.winfo_width()
        height = congrats_window.winfo_height()
        x = (congrats_window.winfo_screenwidth() // 2) - (width // 2)
        y = (congrats_window.winfo_screenheight() // 2) - (height // 2)
        congrats_window.geometry(f"{width}x{height}+{x}+{y}")

    def back_to_main(self):
        self.show_main_menu()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

def main():
    root = tk.Tk()
    app = DeepWorkTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
