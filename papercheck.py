import cv2
import numpy as np

RATIO_COORDINATES = {
    "test_code":[0.876, 0.94, 0.0975, 0.298],
    "student_code":[0.727, 0.845,0.0975, 0.298],
    "sheet_ans":[0.055, 0.927, 0.326, 0.9455]
}
MINMAX_AREA = {
    "test_code":[50000,70000],
    "student_code":[100000, 120000],
    "sheet_ans":[500000,600000]
}

width,height = 1830,2560

def display(img, ratio = 0.4, time_sec = 5):
    img = cv2.resize(img, (0, 0), fx=ratio, fy=ratio)
    cv2.imshow("show",img)
    cv2.waitKey(int(time_sec * 1000))
    cv2.destroyAllWindows()

def extract_part_area(image, name):
    mi,mx = MINMAX_AREA[name]
    countours = get_contours(image, minArea=mi, maxArea=mx)
    results = []
    for in4 in countours:
        x, y, w, h = cv2.boundingRect(in4[4])
        cropped_img = image[y:y+h, x:x+w]
        results.append([[x,y,w,h],cropped_img])
    # Xêp theo x tăng dần
    results.sort(key=lambda x: x[0][0])
    return results

def get_contours(img,cThread=[100,100],minArea=1000, maxArea=int(1e7), filter=4):
    # Xử lý ảnh
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur,cThread[0],cThread[1])
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(imgCanny, kernel, iterations = 3)
    erode = cv2.erode(imgDilation, kernel, iterations = 2)
    _, thresh = cv2.threshold(erode, 127, 255, 0)
    # Tìm các contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    final_countours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea and area < maxArea:
            # print(area)
            peri = cv2.arcLength(contour,True)
            approx = cv2.approxPolyDP(contour,0.02*peri,True)
            bbox = cv2.boundingRect(approx)
            if filter > 0:
                if len(approx) == filter:
                    final_countours.append([len(approx),area,approx,bbox,contour])
            else:
                final_countours.append([len(approx),area,approx,bbox,contour])
    final_countours = sorted(final_countours, key = lambda x:x[1], reverse=True)
    return final_countours

# Hàm hỗ trợ tìm bài kiểm tra
def wrap_image(img, points, widthImg, heightImg, pad = 0):
    points= get_4_contour(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2) 
    wrap = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    wrap = wrap[pad:wrap.shape[0]-pad,pad:wrap.shape[1]-pad]
    return wrap

def get_4_contour(points):
    center = np.mean(points, axis=0).astype(int)

    points_above_center = np.array([point.squeeze() for point in points if point.squeeze()[1] < center[0][1]])
    points_below_center = np.array([point.squeeze() for point in points if point.squeeze()[1] >= center[0][1]])

    top_left = points_above_center[np.argmin(points_above_center[:, 0])]
    top_right = points_above_center[np.argmax(points_above_center[:, 0])]
    botton_left = points_below_center[np.argmin(points_below_center[:, 0])]
    botton_right = points_below_center[np.argmax(points_below_center[:, 0])]
    return np.array([[top_left], [top_right], [botton_left],[botton_right]])