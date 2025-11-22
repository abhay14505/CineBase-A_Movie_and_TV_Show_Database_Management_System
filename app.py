import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "cinebase")


class CineBaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 CineBase Database GUI")
        self.root.geometry("1100x700")

        self.conn = None
        self.cursor = None
        self.role = StringVar(value="Admin")  # Default role

        self.connect_db()
        self.build_gui()

    # ---------------- Database Connection ----------------
    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )
            self.cursor = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Database Error", f"Could not connect:\n{e}")

    # ---------------- GUI Layout ----------------
    def build_gui(self):
        top_frame = Frame(self.root)
        top_frame.pack(fill=X, pady=5)

        Label(top_frame, text="CineBase Role:", font=("Arial", 11)).pack(side=LEFT, padx=10)
        role_menu = ttk.Combobox(top_frame, textvariable=self.role, values=["Admin", "User"], state="readonly", width=10)
        role_menu.pack(side=LEFT, padx=5)
        role_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_role())

        tab_control = ttk.Notebook(self.root)

        self.table_tab = ttk.Frame(tab_control)
        self.proc_tab = ttk.Frame(tab_control)
        self.query_tab = ttk.Frame(tab_control)
        self.log_tab = ttk.Frame(tab_control)

        tab_control.add(self.table_tab, text="📋 Tables")
        tab_control.add(self.proc_tab, text="⚙️ Procedures / Functions")
        tab_control.add(self.query_tab, text="🔍 Custom Queries")
        tab_control.add(self.log_tab, text="🪵 Trigger Log")
        tab_control.pack(expand=1, fill="both")

        self.build_table_tab()
        self.build_proc_tab()
        self.build_query_tab()
        self.build_log_tab()

    # ---------------- Role Refresh ----------------
    def refresh_role(self):
        role = self.role.get()
        is_admin = (role == "Admin")

        # Enable/disable table operation buttons
        state = NORMAL if is_admin else DISABLED
        for btn in [self.add_btn, self.edit_btn, self.delete_btn]:
            btn.config(state=state)

        # Refresh Procedures tab (rebuild for current role)
        for widget in self.proc_tab.winfo_children():
            widget.destroy()
        self.build_proc_tab()

    # ---------------- Tab 1: Table Browser ----------------
    def build_table_tab(self):
        frame_top = Frame(self.table_tab)
        frame_top.pack(fill=X, pady=10)

        Label(frame_top, text="Select Table:", font=("Arial", 11)).pack(side=LEFT, padx=10)

        self.table_combo = ttk.Combobox(frame_top, state="readonly")
        self.table_combo.pack(side=LEFT, padx=10)
        self.refresh_tables()

        Button(frame_top, text="Load", command=self.load_table_data).pack(side=LEFT, padx=5)
        self.add_btn = Button(frame_top, text="Add Row", command=self.add_row)
        self.add_btn.pack(side=LEFT, padx=5)
        self.edit_btn = Button(frame_top, text="Edit Row", command=self.edit_row)
        self.edit_btn.pack(side=LEFT, padx=5)
        self.delete_btn = Button(frame_top, text="Delete Row", command=self.delete_row)
        self.delete_btn.pack(side=LEFT, padx=5)
        Button(frame_top, text="Refresh Tables", command=self.refresh_tables).pack(side=LEFT, padx=5)

        self.tree = ttk.Treeview(self.table_tab)
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def refresh_tables(self):
        try:
            self.cursor.execute("SHOW TABLES;")
            tables = [t[0] for t in self.cursor.fetchall()]
            self.table_combo["values"] = tables
            if tables:
                self.table_combo.current(0)
        except Error as e:
            messagebox.showerror("Error", f"Error fetching tables: {e}")

    def load_table_data(self):
        table = self.table_combo.get()
        if not table:
            return
        try:
            self.cursor.execute(f"SELECT * FROM {table}")
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = cols
            self.tree["show"] = "headings"

            for col in cols:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)

            for row in rows:
                self.tree.insert("", "end", values=row)
        except Error as e:
            messagebox.showerror("Error", f"Could not load table data: {e}")

    def add_row(self):
        if self.role.get() != "Admin":
            messagebox.showinfo("Access Denied", "Only Admins can add new records.")
            return

        table = self.table_combo.get()
        if not table:
            return
        try:
            self.cursor.execute(f"DESCRIBE {table}")
            cols = [r[0] for r in self.cursor.fetchall()]
            add_win = Toplevel(self.root)
            add_win.title(f"Add Record to {table}")
            entries = {}
            for i, col in enumerate(cols):
                Label(add_win, text=col).grid(row=i, column=0, padx=10, pady=5)
                e = Entry(add_win)
                e.grid(row=i, column=1, padx=10, pady=5)
                entries[col] = e

            def save():
                values = [entries[c].get() or None for c in cols]
                placeholders = ", ".join(["%s"] * len(cols))
                try:
                    self.cursor.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
                    self.conn.commit()
                    messagebox.showinfo("Success", "Record added successfully!")
                    add_win.destroy()
                    self.load_table_data()
                except Error as e:
                    messagebox.showerror("Error", f"Insert failed: {e}")

            Button(add_win, text="Save", command=save).grid(row=len(cols), columnspan=2, pady=10)

        except Error as e:
            messagebox.showerror("Error", f"Could not add record: {e}")

    def edit_row(self):
        if self.role.get() != "Admin":
            messagebox.showinfo("Access Denied", "Only Admins can edit records.")
            return

        table = self.table_combo.get()
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Please select a row to edit.")
            return

        values = self.tree.item(selected, "values")
        self.cursor.execute(f"DESCRIBE {table}")
        cols = [r[0] for r in self.cursor.fetchall()]

        edit_win = Toplevel(self.root)
        edit_win.title(f"Edit Record in {table}")
        entries = {}

        for i, (col, val) in enumerate(zip(cols, values)):
            Label(edit_win, text=col).grid(row=i, column=0, padx=10, pady=5)
            e = Entry(edit_win)
            e.grid(row=i, column=1, padx=10, pady=5)
            e.insert(0, val)
            entries[col] = e

        def update():
            new_values = [entries[c].get() for c in cols]
            set_clause = ", ".join([f"{c}=%s" for c in cols])
            pk = cols[0]
            try:
                self.cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {pk}=%s", new_values + [values[0]])
                self.conn.commit()
                messagebox.showinfo("Success", "Record updated successfully!")
                edit_win.destroy()
                self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Update failed: {e}")

        Button(edit_win, text="Update", command=update).grid(row=len(cols), columnspan=2, pady=10)

    def delete_row(self):
        if self.role.get() != "Admin":
            messagebox.showinfo("Access Denied", "Only Admins can delete records.")
            return

        table = self.table_combo.get()
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Please select a row to delete.")
            return

        values = self.tree.item(selected, "values")
        pk_value = values[0]
        pk_col = self.tree["columns"][0]
        confirm = messagebox.askyesno("Confirm", f"Delete record {pk_value}?")
        if not confirm:
            return
        try:
            self.cursor.execute(f"DELETE FROM {table} WHERE {pk_col}=%s", (pk_value,))
            self.conn.commit()
            messagebox.showinfo("Deleted", "Record deleted successfully.")
            self.load_table_data()
        except Error as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    # ---------------- Tab 2: Procedures / Functions ----------------
    def build_proc_tab(self):
        frame = Frame(self.proc_tab)
        frame.pack(pady=20)

        Label(frame, text="Stored Procedures / Functions", font=("Arial", 13, "bold")).grid(row=0, columnspan=2, pady=10)

        role = self.role.get()

        if role == "Admin":
            Button(frame, text="Add Movie with Genre", command=self.call_add_movie_proc).grid(row=1, column=0, padx=10, pady=5)
        else:
            Label(frame, text="(User mode: movie addition disabled)").grid(row=1, column=0, padx=10, pady=5)

        Button(frame, text="Get Average Rating", command=self.call_avg_rating_proc).grid(row=1, column=1, padx=10, pady=5)
        Button(frame, text="Get User Review Count", command=self.call_user_review_func).grid(row=2, column=0, padx=10, pady=5)
        Button(frame, text="Calculate Age (by UserID)", command=self.call_calc_age_func).grid(row=2, column=1, padx=10, pady=5)

        self.proc_output = Text(self.proc_tab, height=20)
        self.proc_output.pack(fill=BOTH, padx=20, pady=10)

    # -------- Procedures ----------
    def call_add_movie_proc(self):
        win = Toplevel(self.root)
        win.title("Add Movie With Genre")

        fields = ["movieTitle", "releaseDate", "runtime", "languageName", "countryName", "genreName"]
        entries = {}
        for i, f in enumerate(fields):
            Label(win, text=f).grid(row=i, column=0, padx=10, pady=5)
            e = Entry(win)
            e.grid(row=i, column=1, padx=10, pady=5)
            entries[f] = e

        def execute():
            vals = [entries[f].get() for f in fields]
            try:
                self.cursor.callproc("AddMovieWithGenre", vals)
                self.conn.commit()
                messagebox.showinfo("Success", "Movie added successfully via procedure!")
                win.destroy()
                self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Procedure failed: {e}")

        Button(win, text="Run", command=execute).grid(row=len(fields), columnspan=2, pady=10)

    def call_avg_rating_proc(self):
        win = Toplevel(self.root)
        win.title("Get Average Rating")

        Label(win, text="movieID (or leave blank):").grid(row=0, column=0, padx=10, pady=5)
        movie_entry = Entry(win)
        movie_entry.grid(row=0, column=1)

        Label(win, text="showID (or leave blank):").grid(row=1, column=0, padx=10, pady=5)
        show_entry = Entry(win)
        show_entry.grid(row=1, column=1)

        def execute():
            m_id = movie_entry.get() or None
            s_id = show_entry.get() or None
            try:
                self.cursor.callproc("GetAverageRating", [m_id, s_id])
                for result in self.cursor.stored_results():
                    rows = result.fetchall()
                    self.proc_output.insert(END, f"Results:\n{rows}\n\n")
                win.destroy()
            except Error as e:
                messagebox.showerror("Error", f"Procedure failed: {e}")

        Button(win, text="Run", command=execute).grid(row=2, columnspan=2, pady=10)

    # -------- Functions ----------
    def call_user_review_func(self):
        win = Toplevel(self.root)
        win.title("Get User Review Count")

        Label(win, text="Enter UserID:").grid(row=0, column=0, padx=10, pady=5)
        user_entry = Entry(win)
        user_entry.grid(row=0, column=1, padx=10, pady=5)

        def execute():
            try:
                user_id = user_entry.get()
                query = f"SELECT GetUserReviewCount({user_id});"
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                self.proc_output.insert(END, f"User {user_id} has given {result[0]} reviews.\n\n")
                win.destroy()
            except Error as e:
                messagebox.showerror("Error", f"Function call failed: {e}")

        Button(win, text="Run", command=execute).grid(row=1, columnspan=2, pady=10)

    def call_calc_age_func(self):
        win = Toplevel(self.root)
        win.title("Calculate Age (by UserID)")

        Label(win, text="Enter UserID:").grid(row=0, column=0, padx=10, pady=5)
        user_entry = Entry(win)
        user_entry.grid(row=0, column=1, padx=10, pady=5)

        def execute():
            try:
                user_id = user_entry.get()
                if not user_id.isdigit():
                    messagebox.showwarning("Invalid Input", "Please enter a valid numeric UserID.")
                    return

                self.cursor.execute("SELECT DateOfBirth FROM Users WHERE UserID = %s", (user_id,))
                result = self.cursor.fetchone()
                if not result or not result[0]:
                    messagebox.showinfo("No DOB", f"User {user_id} has no DateOfBirth recorded.")
                    return

                dob = result[0]
                self.cursor.execute(f"SELECT CalculateAge('{dob}');")
                age_result = self.cursor.fetchone()
                age = age_result[0] if age_result else "Unknown"

                self.proc_output.insert(END, f"User {user_id} (DOB: {dob}) is {age} years old.\n\n")
                win.destroy()
            except Error as e:
                messagebox.showerror("Error", f"Function call failed: {e}")

        Button(win, text="Run", command=execute).grid(row=1, columnspan=2, pady=10)

    # ---------------- Tab 3: Custom Queries ----------------
    def build_query_tab(self):
        frame = Frame(self.query_tab)
        frame.pack(pady=20, fill=X)

        Label(frame, text="Advanced Database Queries", font=("Arial", 13, "bold")).pack(pady=10)

        btn_frame = Frame(frame)
        btn_frame.pack(pady=10)

        Button(btn_frame, text="🔗 Nested Query: Users with Award-Winning Reviews", 
               command=self.run_nested_query, width=40).pack(pady=5)
        Button(btn_frame, text="🔀 Join Query: Detailed Movie Info with Genres", 
               command=self.run_join_query, width=40).pack(pady=5)
        Button(btn_frame, text="📊 Aggregate Query: Genre Statistics", 
               command=self.run_aggregate_query, width=40).pack(pady=5)

        # Results display
        Label(self.query_tab, text="Query Results:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        
        self.query_tree = ttk.Treeview(self.query_tab)
        self.query_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(self.query_tab, orient="vertical", command=self.query_tree.yview)
        vsb.pack(side=RIGHT, fill=Y)
        self.query_tree.configure(yscrollcommand=vsb.set)

    def run_nested_query(self):
        """Find users who have reviewed award-winning movies (Nested Query)"""
        query = """
        SELECT DISTINCT u.UserID, u.Username, u.Email, u.Country
        FROM Users u
        WHERE u.UserID IN (
            SELECT r.UserID
            FROM Review r
            WHERE r.MovieID IN (
                SELECT aw.MovieID
                FROM Award_Winner aw
                WHERE aw.MovieID IS NOT NULL
            )
        )
        """
        self.execute_and_display_query(query, "Users Who Reviewed Award-Winning Movies")

    def run_join_query(self):
        """Get detailed movie information with genres and ratings (Join Query)"""
        query = """
        SELECT 
            m.MovieID,
            m.Title,
            m.ReleaseDate,
            m.Runtime,
            m.Language,
            m.Country,
            GROUP_CONCAT(DISTINCT g.Name ORDER BY g.Name SEPARATOR ', ') AS Genres,
            ROUND(AVG(r.Rating), 2) AS AvgRating,
            COUNT(DISTINCT r.ReviewID) AS Reviews
        FROM Movie m
        LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
        LEFT JOIN Genre g ON mg.GenreID = g.GenreID
        LEFT JOIN Review r ON m.MovieID = r.MovieID
        GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Runtime, m.Language, m.Country
        ORDER BY AvgRating DESC
        """
        self.execute_and_display_query(query, "Detailed Movie Information")

    def run_aggregate_query(self):
        """Get statistics on content by genre (Aggregate Query)"""
        query = """
        SELECT 
            g.Name AS Genre,
            COUNT(DISTINCT mg.MovieID) AS Movies,
            COUNT(DISTINCT sg.ShowID) AS Shows,
            COUNT(DISTINCT mg.MovieID) + COUNT(DISTINCT sg.ShowID) AS Total,
            ROUND(AVG(r.Rating), 2) AS AvgRating,
            MAX(r.Rating) AS MaxRating,
            MIN(r.Rating) AS MinRating
        FROM Genre g
        LEFT JOIN Movie_Genre mg ON g.GenreID = mg.GenreID
        LEFT JOIN Show_Genre sg ON g.GenreID = sg.GenreID
        LEFT JOIN Review r ON (r.MovieID = mg.MovieID OR r.ShowID = sg.ShowID)
        GROUP BY g.GenreID, g.Name
        ORDER BY Total DESC
        """
        self.execute_and_display_query(query, "Genre Statistics")

    def execute_and_display_query(self, query, title):
        """Helper method to execute a query and display results in the tree"""
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]

            # Clear previous results
            self.query_tree.delete(*self.query_tree.get_children())
            
            # Configure columns
            self.query_tree["columns"] = cols
            self.query_tree["show"] = "headings"

            for col in cols:
                self.query_tree.heading(col, text=col)
                self.query_tree.column(col, width=120, anchor="center")

            # Insert data
            for row in rows:
                self.query_tree.insert("", "end", values=row)

            messagebox.showinfo("Query Executed", f"{title}\n\nReturned {len(rows)} row(s)")
        except Error as e:
            messagebox.showerror("Query Error", f"Failed to execute query:\n{e}")

    # ---------------- Tab 4: Trigger Log ----------------
    def build_log_tab(self):
        Button(self.log_tab, text="Load Review Log", command=self.load_log).pack(pady=10)
        self.log_tree = ttk.Treeview(self.log_tab)
        self.log_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def load_log(self):
        try:
            self.cursor.execute("SELECT * FROM Review_Log ORDER BY ActionTime DESC")
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            self.log_tree.delete(*self.log_tree.get_children())
            self.log_tree["columns"] = cols
            self.log_tree["show"] = "headings"
            for c in cols:
                self.log_tree.heading(c, text=c)
                self.log_tree.column(c, width=130)
            for r in rows:
                self.log_tree.insert("", "end", values=r)
        except Error as e:
            messagebox.showerror("Error", f"Could not load logs: {e}")


if __name__ == "__main__":
    root = Tk()
    app = CineBaseApp(root)
    root.mainloop()
