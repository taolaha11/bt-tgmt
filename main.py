import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import csv
import numpy as np
from papercheck import display
from Grade import Grading


NUM_QUESTIONS = 120
ANSWER_KEYS = ['A'] * NUM_QUESTIONS  # Mặc định toàn bộ đáp án là A

def save_score(student_code, test_code, score):
    file_path = "grades.csv"
    header = ["Student Code", "Test Code", "Score"]
    updated_rows = []

    try:
        # Đọc toàn bộ dữ liệu hiện tại nếu có
        try:
            with open(file_path, "r", newline="") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                if rows and rows[0] == header:
                    rows = rows[1:]  # Bỏ dòng tiêu đề
                # Giữ lại các dòng không trùng mã thí sinh
                updated_rows = [row for row in rows if row[0] != student_code]
        except FileNotFoundError:
            pass  # Nếu file chưa tồn tại thì không sao

        # Thêm dòng mới vào danh sách đã lọc
        updated_rows.append([student_code, test_code, score])

        # Ghi lại toàn bộ file
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(updated_rows)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu điểm: {e}")

class GradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Chấm Điểm")
        
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.upload_button = tk.Button(self.left_frame, text="Chọn Ảnh", command=self.upload_image)
        self.upload_button.pack(pady=5)

        self.load_answer_button = tk.Button(self.left_frame, text="Tải Đáp Án", command=self.load_answer_key)
        self.load_answer_button.pack(pady=5)

        self.manual_entry = tk.Entry(self.left_frame, width=50)
        self.manual_entry.pack(pady=5)
        self.manual_entry.insert(0, ",".join(ANSWER_KEYS))

        self.save_answer_button = tk.Button(self.left_frame, text="Lưu Đáp Án", command=self.save_manual_answer)
        self.save_answer_button.pack(pady=5)

        self.grade_button = tk.Button(self.left_frame, text="Chấm Điểm", command=self.grade_image, state=tk.DISABLED)
        self.grade_button.pack(pady=10)

        self.info_label = tk.Label(self.left_frame, text="Mã thí sinh: \nMã đề thi: \nĐiểm số:", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.image_label = tk.Label(self.right_frame)
        self.image_label.pack()

        self.filepath = None

    def upload_image(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.filepath:
            img = Image.open(self.filepath)
            img = img.resize((550, 740))
            img = ImageTk.PhotoImage(img)

            self.image_label.config(image=img)
            self.image_label.image = img
            self.grade_button.config(state=tk.NORMAL)

    def load_answer_key(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    answers = {int(row[0])-1: row[1] for row in reader}
                    for i in range(NUM_QUESTIONS):
                        ANSWER_KEYS[i] = answers.get(i, 'A')
                self.manual_entry.delete(0, tk.END)
                self.manual_entry.insert(0, ",".join(ANSWER_KEYS))
                messagebox.showinfo("Thành công", "Tải đáp án từ CSV thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi đọc CSV: {e}")

    def save_manual_answer(self):
        global ANSWER_KEYS
        user_input = self.manual_entry.get().split(',')
        if len(user_input) == NUM_QUESTIONS and all(x in ['A', 'B', 'C', 'D'] for x in user_input):
            ANSWER_KEYS = user_input
            messagebox.showinfo("Thành công", "Đáp án đã được cập nhật!")
        else:
            messagebox.showerror("Lỗi", "Định dạng đáp án không hợp lệ. Hãy nhập đúng 120 đáp án A,B,C,D.")

    def grade_image(self):
        if self.filepath:
            grade = Grading(self.filepath, ANSWER_KEYS, num_questions=NUM_QUESTIONS)
            student_code = grade.extract_student_code()
            test_code = grade.extract_test_code()
            score = grade.get_score()
            result_image = grade.get_result_image()

            self.info_label.config(text=f"Mã thí sinh: {student_code}\nMã đề thi: {test_code}\nĐiểm số: {score}")

            # Lưu điểm vào CSV
            save_score(student_code, test_code, score)

            img = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
            img = img.resize((550, 740))
            img = ImageTk.PhotoImage(img)

            self.image_label.config(image=img)
            self.image_label.image = img
        else:
            messagebox.showerror("Lỗi", "Không có ảnh nào được chọn.")

root = tk.Tk()
app = GradingApp(root)
root.mainloop()


