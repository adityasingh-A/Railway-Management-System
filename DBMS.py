import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os

stations = ["station1.db", "station2.db"]

def initialize_databases():
    for db in stations:
        if os.path.exists(db):
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(trains)")
                columns = [col[1] for col in cursor.fetchall()]
                required = ["train_id","name","source","destination","sl_seats","ac3a_seats","ac2a_seats","h1_seats","general_seats"]
                if not all(col in columns for col in required):
                    conn.close()
                    os.remove(db)
                else:
                    conn.close()
            except sqlite3.DatabaseError:
                os.remove(db)

        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS trains(
                        train_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        source TEXT NOT NULL,
                        destination TEXT NOT NULL,
                        sl_seats INTEGER NOT NULL,
                        ac3a_seats INTEGER NOT NULL,
                        ac2a_seats INTEGER NOT NULL,
                        h1_seats INTEGER NOT NULL,
                        general_seats INTEGER NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tickets(
                        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        train_id INTEGER NOT NULL,
                        passenger_name TEXT NOT NULL,
                        seat_class TEXT NOT NULL,
                        seats_booked INTEGER NOT NULL,
                        FOREIGN KEY(train_id) REFERENCES trains(train_id))''')
        conn.commit()
        conn.close()

initialize_databases()

def add_train(name, source, destination, sl, ac3a, ac2a, h1, general):
    if not name or not source or not destination:
        messagebox.showerror("Error", "All fields are required!")
        return
    for db in stations:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO trains(name, source, destination, sl_seats, ac3a_seats, ac2a_seats, h1_seats, general_seats)
                          VALUES(?,?,?,?,?,?,?,?)""", (name, source, destination, sl, ac3a, ac2a, h1, general))
        conn.commit()
        conn.close()

def get_trains():
    all_trains = []
    for db in stations:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trains")
        trains = cursor.fetchall()
        all_trains.extend(trains)
        conn.close()
    seen = set()
    unique_trains = []
    for train in all_trains:
        if train[0] not in seen:
            unique_trains.append(train)
            seen.add(train[0])
    return unique_trains

def book_ticket_multi():
    names_text = passenger_name_var.get().strip()
    if not names_text:
        messagebox.showerror("Error", "Passenger name required!")
        return
    names = [name.strip() for name in names_text.split(",") if name.strip()]
    if not names:
        messagebox.showerror("Error", "Invalid passenger names!")
        return

    train_id = ticket_train_id_var.get()
    seats_per_person = seats_book_var.get()
    if seats_per_person <= 0:
        messagebox.showerror("Error", "Seats to book must be positive!")
        return

    seat_class = seat_class_var.get()
    column_name = seat_class.lower().replace(" ", "") + "_seats"

    for name in names:
        available = False
        for db in stations:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column_name} FROM trains WHERE train_id=?", (train_id,))
            result = cursor.fetchone()
            if result and result[0] >= seats_per_person:
                available = True
                cursor.execute(f"UPDATE trains SET {column_name} = {column_name} - ? WHERE train_id=?", 
                               (seats_per_person, train_id))
                cursor.execute("INSERT INTO tickets(train_id, passenger_name, seat_class, seats_booked) VALUES(?,?,?,?)",
                               (train_id, name, seat_class, seats_per_person))
                conn.commit()
            conn.close()
        if not available:
            messagebox.showerror("Error", f"Not enough seats for {name} in {seat_class} or invalid Train ID!")
            return
    messagebox.showinfo("Success", "Ticket(s) booked successfully!")

def get_tickets():
    tickets_list = []
    for db in stations:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        tickets_list.extend(tickets)
        conn.close()
    seen = set()
    unique_tickets = []
    for ticket in tickets_list:
        if ticket[0] not in seen:
            unique_tickets.append(ticket)
            seen.add(ticket[0])
    return unique_tickets

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"

root = tk.Tk()
root.title("🚆 Railway Management System")
root.geometry("1100x700")
root.configure(bg="#e6f0ff")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 12, "bold"), background="#0078D7", foreground="white", padding=8)
style.map("TButton", background=[("active", "#005A9E")])
style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#0078D7", foreground="white")
style.configure("Treeview", font=("Arial", 10), rowheight=28)

frames = {}

def show_frame(name):
    for frame in frames.values():
        frame.pack_forget()
    frames[name].pack(fill='both', expand=True)

home_frame = tk.Frame(root, bg="#e6f0ff")
frames["home"] = home_frame

tk.Label(home_frame, text="🚄 Railway Management System", font=("Helvetica", 28, "bold"), bg="#e6f0ff", fg="#003366").pack(pady=40)
tk.Label(home_frame, text="Manage trains, book tickets, and view records easily", font=("Arial", 14), bg="#e6f0ff").pack(pady=10)

buttons = [
    ("Add Train", lambda: show_frame("add")),
    ("View Trains", lambda: show_frame("view")),
    ("Book Ticket", lambda: show_frame("book")),
    ("View Tickets", lambda: show_frame("tickets"))
]

for text, cmd in buttons:
    btn = ttk.Button(home_frame, text=text, command=cmd, width=25)
    btn.pack(pady=15)
    btn.bind("<Return>", lambda e, b=btn: b.invoke())

add_frame = tk.Frame(root, bg="#f8fbff")
frames["add"] = add_frame

tk.Label(add_frame, text="➕ Add Train Details", font=("Helvetica", 22, "bold"), bg="#f8fbff", fg="#003366").pack(pady=20)

form = tk.Frame(add_frame, bg="#f8fbff")
form.pack(pady=10)

labels = ["Train Name", "Source", "Destination", "SL Seats", "AC 3A Seats", "AC 2A Seats", "H1 Seats", "General Seats"]
vars_list = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
entries = []

for i, label in enumerate(labels):
    tk.Label(form, text=label + ":", bg="#f8fbff", font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(form, textvariable=vars_list[i], width=30)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entry.bind("<Return>", focus_next_widget)
    entries.append(entry)

def add_train_gui():
    add_train(vars_list[0].get(), vars_list[1].get(), vars_list[2].get(),
              vars_list[3].get(), vars_list[4].get(), vars_list[5].get(),
              vars_list[6].get(), vars_list[7].get())
    messagebox.showinfo("Success", f"Train '{vars_list[0].get()}' added successfully!")

btn_add = ttk.Button(add_frame, text="Add Train", command=add_train_gui)
btn_add.pack(pady=15)
btn_add.bind("<Return>", lambda e: btn_add.invoke())

btn_back1 = ttk.Button(add_frame, text="⬅ Back to Home", command=lambda: show_frame("home"))
btn_back1.pack(pady=10)
btn_back1.bind("<Return>", lambda e: btn_back1.invoke())

view_frame = tk.Frame(root, bg="#f8fbff")
frames["view"] = view_frame

tk.Label(view_frame, text="🚉 All Trains", font=("Helvetica", 22, "bold"), bg="#f8fbff", fg="#003366").pack(pady=20)
tree_trains = ttk.Treeview(view_frame, columns=("ID","Name","Source","Destination","SL","AC3A","AC2A","H1","General"), show='headings')
for col in ("ID","Name","Source","Destination","SL","AC3A","AC2A","H1","General"):
    tree_trains.heading(col, text=col)
tree_trains.pack(fill='both', expand=True, padx=20, pady=10)

def load_trains():
    for row in tree_trains.get_children():
        tree_trains.delete(row)
    trains = get_trains()
    for train in trains:
        tree_trains.insert("", tk.END, values=train)

btn_refresh = ttk.Button(view_frame, text="🔄 Refresh", command=load_trains)
btn_refresh.pack(pady=10)
btn_refresh.bind("<Return>", lambda e: btn_refresh.invoke())

btn_back2 = ttk.Button(view_frame, text="⬅ Back to Home", command=lambda: show_frame("home"))
btn_back2.pack(pady=5)
btn_back2.bind("<Return>", lambda e: btn_back2.invoke())

book_frame = tk.Frame(root, bg="#f8fbff")
frames["book"] = book_frame

tk.Label(book_frame, text="🎫 Book Ticket", font=("Helvetica", 22, "bold"), bg="#f8fbff", fg="#003366").pack(pady=20)

ticket_train_id_var = tk.IntVar()
passenger_name_var = tk.StringVar()
seats_book_var = tk.IntVar()
seat_class_var = tk.StringVar()

form2 = tk.Frame(book_frame, bg="#f8fbff")
form2.pack(pady=10)

entries2 = [
    ("Train ID", ticket_train_id_var),
    ("Passenger Name(s) (comma separated)", passenger_name_var),
    ("Seats to Book", seats_book_var)
]

for i, (label, var) in enumerate(entries2):
    tk.Label(form2, text=label+":", font=("Arial", 12), bg="#f8fbff").grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(form2, textvariable=var, width=30)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entry.bind("<Return>", focus_next_widget)

tk.Label(form2, text="Seat Class:", font=("Arial", 12), bg="#f8fbff").grid(row=3, column=0, padx=10, pady=5, sticky="e")
seat_class_dropdown = ttk.Combobox(form2, textvariable=seat_class_var, values=["SL","AC 3A","AC 2A","H1","General"], width=27)
seat_class_dropdown.grid(row=3, column=1, padx=10, pady=5)
seat_class_dropdown.current(0)
seat_class_dropdown.bind("<Return>", focus_next_widget)

btn_book = ttk.Button(book_frame, text="Book Ticket", command=book_ticket_multi)
btn_book.pack(pady=10)
btn_book.bind("<Return>", lambda e: btn_book.invoke())

btn_back3 = ttk.Button(book_frame, text="⬅ Back to Home", command=lambda: show_frame("home"))
btn_back3.pack(pady=5)
btn_back3.bind("<Return>", lambda e: btn_back3.invoke())

tickets_frame = tk.Frame(root, bg="#f8fbff")
frames["tickets"] = tickets_frame

tk.Label(tickets_frame, text="🎟 View Tickets", font=("Helvetica", 22, "bold"), bg="#f8fbff", fg="#003366").pack(pady=20)
tree_tickets = ttk.Treeview(tickets_frame, columns=("Ticket ID","Train ID","Passenger","Seat Class","Seats Booked"), show='headings')
for col in ("Ticket ID","Train ID","Passenger","Seat Class","Seats Booked"):
    tree_tickets.heading(col, text=col)
tree_tickets.pack(fill='both', expand=True, padx=20, pady=10)

def load_tickets():
    for row in tree_tickets.get_children():
        tree_tickets.delete(row)
    tickets = get_tickets()
    for ticket in tickets:
        tree_tickets.insert("", tk.END, values=ticket)

btn_refresh_t = ttk.Button(tickets_frame, text="🔄 Refresh", command=load_tickets)
btn_refresh_t.pack(pady=10)
btn_refresh_t.bind("<Return>", lambda e: btn_refresh_t.invoke())

btn_back4 = ttk.Button(tickets_frame, text="⬅ Back to Home", command=lambda: show_frame("home"))
btn_back4.pack(pady=5)
btn_back4.bind("<Return>", lambda e: btn_back4.invoke())

show_frame("home")
root.mainloop()
