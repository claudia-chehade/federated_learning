import os

import flwr as fl
import tensorflow as tf
import argparse
from connection import Connection


# Make TensorFlow log less verbose
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load model and data (MobileNetV2, CIFAR-10)
model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()


# Define Flower client
class CifarClient(fl.client.NumPyClient):
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_parameters(self, config):
        weights = model.get_weights()
        import csv
        weights_filename = 'list_data.csv'
        with open(weights_filename, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(weights)
        import pdb
        pdb.set_trace()
        self.connection.connect(weights_filename)
        return weights

    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=1, batch_size=32)
        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters, config):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": accuracy}


def main():
    parser = argparse.ArgumentParser(description="A script to connect to an SFTP server.")
    parser.add_argument('--sftp-host', required=True, type=str, help="SFTP server hostname or IP address.")
    parser.add_argument('--sftp-port', type=int, default=22, help="SFTP server port (default: 22).")
    parser.add_argument('--sftp-username', type=str, required=True, help="SFTP username.")
    parser.add_argument('--sftp-password', type=str, required=True, help="SFTP password.")
    
    args = parser.parse_args()

    # You can access the arguments like this:
    sftp_host = args.sftp_host
    sftp_port = args.sftp_port
    sftp_username = args.sftp_username
    sftp_password = args.sftp_password

    # Make a connection
    connection = Connection(sftp_host, sftp_port, sftp_username, sftp_password)

    # Start Flower client
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=CifarClient(connection))

    

if __name__ == "__main__":
    main()
