import cv2
import numpy as np

# Load the image
image_path = 'omr_sheet_1.png'  # Replace with your image path
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Threshold the image to binary (black and white)
_, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

# Find contours of the filled circles
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Function to determine the degree of fill for a circle
def get_fill_percentage(contour):
    area = cv2.contourArea(contour)
    radius = cv2.minEnclosingCircle(contour)[1]
    circle_area = np.pi * (radius ** 2)
    fill_percentage = (area / circle_area) * 100
    return fill_percentage

# Sort contours based on their positions on the grid
def sort_contours(contours):
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    # Sort by y (row), then by x (column) within each row
    contours_sorted = sorted(zip(contours, bounding_boxes), key=lambda b: (b[1][1], b[1][0]))
    return [c[0] for c in contours_sorted]

# Sort contours by their position on the image
sorted_contours = sort_contours(contours)

# Recalculate fill percentages after sorting
sorted_fill_percentages = [get_fill_percentage(contour) for contour in sorted_contours]

# Select the top 16 fill percentages now that they are sorted by position
top_16_fill_percentages = sorted_fill_percentages[:16]

# Reshape into a 4x4 grid
sorted_fill_percentages_grid = np.reshape(top_16_fill_percentages, (4, 4))
print(sorted_fill_percentages_grid)

# Correct answers provided by the user
correct_answers = ['D', 'A', 'D', 'C']

# Mapping indices to answers
index_to_answer = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}

# Calculate the score
score = 0

for i in range(4):  # For each question
    filled_answers = np.where(sorted_fill_percentages_grid[i] > 75)[0]  # Get indices of definite answers
    # if len(filled_answers) == 1:  # Only consider if there's exactly one definite answer
    selected_answer = index_to_answer[filled_answers[0]]
    print(selected_answer)
    print(correct_answers[i])
    if selected_answer == correct_answers[i]:
        print(selected_answer)
        print(correct_answers[i])
        score += 1

print("Score:", score)

# Optional: Draw the detected contours on the original image for visualization

# Convert the original grayscale image to BGR for color drawing
image_with_contours = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# Draw all detected contours
cv2.drawContours(image_with_contours, sorted_contours, -1, (0, 255, 0), 2)

# Save the image with contours drawn for inspection
contours_image_path = 'contours_detected.png'
cv2.imwrite(contours_image_path, image_with_contours)

print(f"Contours image saved at {contours_image_path}")