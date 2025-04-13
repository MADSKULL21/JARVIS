import tensorflow as tf
import numpy as np

# Load TFLite model
model_path = "model.tflite"
interpreter = tf.lite.Interpreter(model_path=model_path)

# Get model input details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Check if the model has a dynamic input shape
input_shape = input_details[0]['shape']  # Get original input shape
print(f"Original Input Shape: {input_shape}")

# If model has a dynamic shape (-1), resize it to a fixed size
if -1 in input_shape:
    fixed_shape = (1, 224, 224, 3)  # Modify this based on your model’s expected input
    print(f"Resizing model input to fixed shape: {fixed_shape}")

    interpreter.resize_tensor_input(input_details[0]['index'], fixed_shape)
    interpreter.allocate_tensors()  # Reallocate after resizing

# Prepare dummy input with the correct shape
input_data = np.random.rand(*fixed_shape).astype(np.float32)

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()

# Get output
output_data = interpreter.get_tensor(output_details[0]['index'])
print(f"Model Output: {output_data}")
