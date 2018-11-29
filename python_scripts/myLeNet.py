from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from matplotlib.pyplot import imshow
import numpy as np
import os


fontsize = 40

excludedCharacters = [39, 44, 45, 46, 58, 59, 61, 95, 96]


""" TESTING DATASET GENERATION """
""" TESTING DATASET GENERATION """
""" TESTING DATASET GENERATION """
""" TESTING DATASET GENERATION """

fonts_list_test = [
    "verdana.ttf", "verdanai.ttf", "verdanab.ttf", "verdanaz.ttf", \
    "calibri.ttf", "calibrii.ttf", "calibrib.ttf", "calibriz.ttf",
]

dataset_test = []
label_test = []

for myTTF in fonts_list_test:
    for char in range(35, 126+1):
        if char not in excludedCharacters:
            txt = chr(char)

            image = Image.new("L", (50,50), (0)) # (0) denotes background color
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("TTF/"+myTTF, fontsize)

            draw.text((5, 0), txt, (1), font=font) # (1) denotes foreground (font) color

            """ TRIM TO WHITE AREA """
            image = np.array(image)
            mask = image
            image = image[np.ix_(mask.any(1),mask.any(0))]
            image = Image.fromarray(image)

            image = image.resize((28,28), Image.ANTIALIAS)

            # image.show()

            image = np.array(image).astype(np.float32)

            image = np.expand_dims(image, axis=2)

            dataset_test = dataset_test + [image]
            label_test = label_test + [char - 34] # to store values between [1 ... 92]

dataset_test = np.array(dataset_test)
label_test = np.array(label_test).astype(np.uint8)


X_test, y_test             = dataset_test, label_test


assert(len(X_test) == len(y_test))

print()
print("Image Shape: {}".format(X_test[0].shape))
print()

print("Test Set:       {} samples".format(len(X_test)))




# Pad images with 0s

X_test       = np.pad(X_test, ((0,0),(2,2),(2,2),(0,0)), 'constant')
    
print("Updated Image Shape: {}".format(X_test[0].shape))







import random
import numpy as np
import matplotlib.pyplot as plt

index = random.randint(0, len(X_test))
image = X_test[index].squeeze()

plt.figure(figsize=(1,1))
plt.imshow(image, cmap="gray")
print(y_test[index])








import tensorflow as tf

BATCH_SIZE = 64







from tensorflow.contrib.layers import flatten

def LeNet(x):    
    # Arguments used for tf.truncated_normal, randomly defines variables for the weights and biases for each layer
    mu = 0
    sigma = 0.1



    # SOLUTION: Flatten. Input = 32x32x1. Output = 1024.
    fc0   = flatten(x)

    # SOLUTION: Layer 1: Fully Connected. Input = 1024. Output = 900.
    fc1_W = tf.Variable(tf.truncated_normal(shape=(1024, 900), mean = mu, stddev = sigma))
    fc1_b = tf.Variable(tf.zeros(900))
    fc1   = tf.matmul(fc0, fc1_W) + fc1_b
    
    # SOLUTION: Activation.
    fc2    = tf.nn.sigmoid(fc1)



    # SOLUTION: Layer 2: Fully Connected. Input = 900. Output = 300.
    fc2_W  = tf.Variable(tf.truncated_normal(shape=(900, 300), mean = mu, stddev = sigma))
    fc2_b  = tf.Variable(tf.zeros(300))
    fc2    = tf.matmul(fc1, fc2_W) + fc2_b
    
    # SOLUTION: Activation.
    fc2    = tf.nn.sigmoid(fc2)



    # SOLUTION: Layer 3: Fully Connected. Input = 300. Output = 92 (WAS 10).
    fc3_W  = tf.Variable(tf.truncated_normal(shape=(300, 92), mean = mu, stddev = sigma))
    fc3_b  = tf.Variable(tf.zeros(92))
    logits = tf.matmul(fc2, fc3_W) + fc3_b
    
    return logits










x = tf.placeholder(tf.float32, (None, 32, 32, 1))
y = tf.placeholder(tf.int32, (None))
one_hot_y = tf.one_hot(y, 92)











rate = 0.001

logits = LeNet(x)
cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=one_hot_y, logits=logits)
loss_operation = tf.reduce_mean(cross_entropy)
optimizer = tf.train.AdamOptimizer(learning_rate = rate)
training_operation = optimizer.minimize(loss_operation)










correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(one_hot_y, 1))
accuracy_operation = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
saver = tf.train.Saver()

def evaluate(X_data, y_data):
    num_examples = len(X_data)
    total_accuracy = 0
    sess = tf.get_default_session()
    for offset in range(0, num_examples, BATCH_SIZE):
        batch_x, batch_y = X_data[offset:offset+BATCH_SIZE], y_data[offset:offset+BATCH_SIZE]
        accuracy = sess.run(accuracy_operation, feed_dict={x: batch_x, y: batch_y})
        total_accuracy += (accuracy * len(batch_x))
    return total_accuracy / num_examples














with tf.Session() as sess:
    saver.restore(sess, tf.train.latest_checkpoint('./model'))

    test_accuracy = evaluate(X_test, y_test)
    print("Test Accuracy = {:.3f}".format(test_accuracy))