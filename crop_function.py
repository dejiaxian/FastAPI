from ultralytics import YOLO
import cv2
import os
from fastapi import HTTPException

def process_image(image_path: str, model_path: str, custom_save_path: str = "predictions"):
    # Load the trained model
    model = YOLO(model_path)

    # Ensure the save directory exists
    os.makedirs(custom_save_path, exist_ok=True)

    # Perform prediction on CPU
    results = model.predict(source=image_path, save=False, device="cpu", conf=0.5)

    # Load the original image
    original_image = cv2.imread(image_path)

    # Check if any boxes are detected
    if len(results[0].boxes.xyxy) == 0:
        raise HTTPException(status_code=400, detail="No objects detected!")
    else:
        print(f"Detected {len(results[0].boxes.xyxy)} objects.")

        cropped_resized_paths = []
        coordinates = []

        # Process each bounding box
        for i, box in enumerate(results[0].boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)  # Convert to integers for coordinates
            cropped_image = original_image[y1:y2, x1:x2]  # Crop the image to the bounding box

            # Resize the cropped image to the size of a ikad_temp card (adjust the target size as needed)
            target_size = (856, 539)  # Example size in pixels (width, height)
            resized_image = cv2.resize(cropped_image, target_size)

            # Save the cropped and resized image
            cropped_resized_path = os.path.join(custom_save_path, f"cropped_resized_{i}.jpg")
            cv2.imwrite(cropped_resized_path, resized_image)
            cropped_resized_paths.append(cropped_resized_path)
            coordinates.append((x1, y1, x2, y2))
            print(f"Cropped and resized image saved at: {cropped_resized_path}")

        # Annotate and save the original image with bounding boxes (optional)
        class_names = ['ikad_temp']  
        for i, box in enumerate(results[0].boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)  # Convert to integers for coordinates
            confidence = results[0].boxes.conf[i].item()  # Get confidence score
            class_id = int(results[0].boxes.cls[i].item())  # Get class ID
            class_name = class_names[class_id]  # Map the class ID to a class name

            # Draw bounding box and label
            color = (0, 255, 0)  # Green color for the bounding box
            thickness = 2  # Thickness of the bounding box
            label = f"{class_name} ({confidence*100:.2f}%)"

            # Draw the rectangle (bounding box)
            cv2.rectangle(original_image, (x1, y1), (x2, y2), color, thickness)

            # Add the label text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            label_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
            label_x = x1
            label_y = y1 - 10
            cv2.rectangle(original_image, (label_x, label_y - label_size[1]), (label_x + label_size[0], label_y), color, -1)
            cv2.putText(original_image, label, (label_x, label_y), font, font_scale, (255, 255, 255), font_thickness)

        # Save the annotated image
        annotated_image_path = os.path.join(custom_save_path, "annotated_image.jpg")
        cv2.imwrite(annotated_image_path, original_image)
        print(f"Annotated image saved at: {annotated_image_path}")

        return {
            "cropped_resized_paths": cropped_resized_paths,
            "annotated_image_path": annotated_image_path,
            "coordinates": coordinates
        }
