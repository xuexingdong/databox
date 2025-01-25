# import cv2
# import numpy as np
# from pytesseract import pytesseract
#
#
# class WeiboCheckImgRecognizer:
#
#     @staticmethod
#     def recg(path):
#         img = cv2.imread(path, cv2.COLOR_BGR2RGB)
#         WeiboCheckImgRecognizer.show('img', img)
#
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         _, binary_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#         WeiboCheckImgRecognizer.show('binary_img', binary_img)
#         thinned_img = cv2.ximgproc.thinning(binary_img, cv2.ximgproc.THINNING_ZHANGSUEN)
#
#         noise_lines = WeiboCheckImgRecognizer._find_noise_lines(img)
#         noise_lines_gray = cv2.cvtColor(noise_lines, cv2.COLOR_BGR2GRAY)
#         _, noise_lines_binary_img = cv2.threshold(noise_lines_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#         # 使用均值滤波去除噪点
#         noise_lines_binary_img = cv2.blur(noise_lines_binary_img, (3, 3))
#         WeiboCheckImgRecognizer.show('noise_lines_binary_img', noise_lines_binary_img)
#         noise_lines_thinned_img = cv2.ximgproc.thinning(noise_lines_binary_img, cv2.ximgproc.THINNING_ZHANGSUEN)
#         # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#         # eroded_noise_lines_thinned_img = cv2.morphologyEx(noise_lines_binary_img, cv2.MORPH_OPEN, kernel)
#         # WeiboCheckImgRecognizer.show('eroded_noise_lines_thinned_img', eroded_noise_lines_thinned_img)
#         # cv2.waitKey()
#
#         result = cv2.subtract(thinned_img, noise_lines_thinned_img)
#         WeiboCheckImgRecognizer.show('result', result)
#         cv2.waitKey()
#
#         result = cv2.bitwise_not(result)
#         text = pytesseract.image_to_string(result)
#         print(text)
#
#     @staticmethod
#     def _find_noise_lines(img):
#         specified_colors = [
#             # 蓝色干扰线
#             [254, 101, 101],
#             # 红色干扰线
#             [101, 101, 254]
#         ]
#         mask = np.zeros_like(img, dtype=np.uint8)
#         for specified_color in specified_colors:
#             # 获取图像的高度和宽度
#             height, width, channels = img.shape
#
#             # 定义指定颜色的NumPy数组
#             specified_color_np = np.array(specified_color, dtype=np.uint8)
#
#             # 遍历图像的每个像素点，除去边界
#             for y in range(1, height - 1):
#                 for x in range(1, width - 1):
#                     # 获取当前像素点周围的3x3单元格颜色
#                     neighborhood = img[y - 1:y + 2, x - 1:x + 2, :]
#                     # 计算周围3x3单元格中与指定颜色相同的像素数量
#                     matching_pixels = np.count_nonzero(np.all(neighborhood == specified_color_np, axis=2))
#
#                     # 判断是否超过一半的像素与指定颜色相同
#                     if matching_pixels > 4:  # 5是8个像素的一半加一
#                         # 将当前像素点变为黑
#                         mask[y, x] = [255, 255, 255]
#         return mask
#
#     @staticmethod
#     def split_char(img, binary_img):
#         WeiboCheckImgRecognizer.show(binary_img)
#
#         # 垂直投影分割
#         boundaries = WeiboCheckImgRecognizer.vertical_projection(binary_img)
#         segments = WeiboCheckImgRecognizer.vertical_segmentation(binary_img, boundaries)
#
#         # 显示分割后的图像
#         for i, segment in enumerate(segments):
#             cv2.imshow(f'Segment {i + 1}', segment)
#
#         # 显示原始图像
#         # cv2.imshow('Original Image', img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
#
#     def vertical_projection(image):
#         # 计算图像的垂直投影
#         projection = np.sum(image, axis=0)
#
#         # 找到垂直投影中的峰值，表示字符之间的边界
#         peaks = np.where(projection > 0.5 * np.max(projection))[0]
#
#         # 将峰值点两两配对，表示字符之间的边界
#         boundaries = [(peaks[i], peaks[i + 1]) for i in range(0, len(peaks), 2)]
#
#         return boundaries
#
#     def vertical_segmentation(image, boundaries):
#         # 根据垂直边界分割图像
#         segments = [image[:, start:end] for start, end in boundaries]
#
#         return segments
#
#     @staticmethod
#     def show(winname, mat):
#         cv2.resizeWindow(winname, 600, 400)
#         img_resized = cv2.resize(mat, (600, 400))
#         cv2.imshow(winname, img_resized)