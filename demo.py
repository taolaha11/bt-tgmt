from papercheck import display
import cv2
import numpy as np
from Grade import Grading


ANSWER_KEYS = ['A','B','C','D'] * 120
NUM_QUESTIONS = 120

path = "img/1.jpg"

grade = Grading(path, ANSWER_KEYS, num_questions=NUM_QUESTIONS)

student_code = grade.extract_student_code()
test_code = grade.extract_test_code()
score = grade.get_score()
image = grade.get_result_image()

print("Mã thí sinh:", student_code)
print("Mã đề thi:", test_code)
print("Điểm số:", score)
display(image, 0.4, 0)
