import keras
import numpy as np

from keras import backend as K

import matplotlib.pyplot as plt



model = keras.models.load_model('neurovision-2d327377b559adb7fc04e0c3ee5c950c')
model_input_layer = model.layers[0].input
model_output_layer = model.layers[-1].output


print(model.summary())
print("Input layer : ", model_input_layer)
print("Output layer:", model_output_layer)

# Our cost function is the mean squared error between the output and 1, our desired output.
cost_fn = keras.losses.mean_squared_error(model_output_layer, 1)

# Gradient
gradient_fn = K.gradients(cost_fn, model_input_layer)[0] 

# Function that returns the cost and gradient, when given an input
calc_cost_and_gradients = K.function([model_input_layer], [cost_fn, gradient_fn])


target_cost = 0.1
learning_rate = 20 

# Generate a random image of 218x68 pixels. 
hacked_image=np.random.rand(1,68,218)

count=0
while True:
    cost, gradients = calc_cost_and_gradients([hacked_image])

    if cost < target_cost:
        break

    # Update the image
    hacked_image -= gradients * learning_rate
    
    count+=1
    if count%1000 == 0:
        print("Iteration %d. Cost: %f" % (count,cost))
        

plt.imshow(hacked_image[0])
plt.show()


