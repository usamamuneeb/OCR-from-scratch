from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import numpy as np
import os
import random

import tensorflow as tf
from tensorflow.contrib.layers import flatten


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 




excludedCharacters = [39, 44, 45, 46, 58, 59, 61, 95, 96]

sentences = np.load(os.path.join('python_scripts', 'postSplit.npy'))




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

logits = LeNet(x)

saver = tf.train.Saver()

print("START_LENET")

with tf.Session() as sess:
    saver.restore(sess, tf.train.latest_checkpoint(os.path.join('.','python_scripts','model')))
    sess = tf.get_default_session()

    for (idx, sentence) in enumerate(sentences):
        print("ITEM_"+str(idx))

        if (len(sentence) > 0):
            spaces = []

            for idx in range(0, len(sentence)):
                if ( type(sentence[idx]) == type('*') ):
                    spaces.append(idx)
                    sentence[idx] = np.zeros((28,28))

            sentence = np.array(sentence)
            sentence = np.expand_dims(sentence, axis=3)
            sentence = np.pad(sentence, ((0,0),(2,2),(2,2),(0,0)), 'constant')

            # print(sentence.shape)

            outputs = sess.run(tf.argmax(logits, 1)+34, feed_dict={x: sentence})
            outputs = [chr(ascii_code) for ascii_code in outputs]

            for idx in range(0, len(spaces)):
                outputs[spaces[idx]] = ' '

            outputs = ''.join(outputs)

            print(outputs)
        else:
            print(" ")


        # break

print("END_LENET")