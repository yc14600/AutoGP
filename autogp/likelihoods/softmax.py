import numpy as np
import tensorflow as tf

from autogp import util
import likelihood


class Softmax(likelihood.Likelihood):
    def __init__(self, num_samples=2000):
        self.num_samples = num_samples

    def log_cond_prob(self, outputs, latent):
        return tf.reduce_sum(outputs * latent, 2) - util.logsumexp(latent, 2)

    def get_params(self):
        return []

    def predict(self, latent_means, latent_vars):
        # Generate samples to estimate the expected value and variance of outputs.
        num_points = tf.shape(latent_means)[0]
        output_dims = tf.shape(latent_means)[1]
        latent = (latent_means + tf.sqrt(latent_vars) *
                  tf.random_normal([self.num_samples, num_points, output_dims]))
        # Compute the softmax of all generated latent values in a stable fashion.
        softmax = tf.exp(latent - tf.expand_dims(util.logsumexp(latent, 2), 2))

        # Estimate the expected value of the softmax and the variance through sampling.
        pred_means = tf.reduce_mean(softmax, 0)
        pred_vars = tf.reduce_sum((softmax - pred_means) ** 2, 0) / (self.num_samples - 1.0)

        return pred_means, pred_vars

