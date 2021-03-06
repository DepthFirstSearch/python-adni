import csv

from cnn.keras.models.d3H_avg.model import build_model
from cnn.keras.prediction.predict_generator import predict_generator
from cnn.keras.d3.preprocessing.image_processing import inputs
from cnn.keras.d3.preprocessing.predict_generator import target_size, GRID
from cnn.keras.d3.train import _split_scans, classes


batch_size = 64
num_samples = 481 * len(GRID)
path_weights = '/home/mhubrich/checkpoints/adni/d3H_avg_3/weights.193-loss_0.363-acc_0.849.h5'


def predict():
    # Get inputs for labeling
    _, scans_test = _split_scans()
    test_inputs = inputs(scans_test, target_size, batch_size, classes, 'test', seed=None)

    # Set up the model
    model = build_model(num_classes=len(classes), input_shape=(1,)+target_size)
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.load_weights(path_weights)

    # Start labeling
    pred, filenames = predict_generator(model,
                                        test_inputs,
                                        val_samples=num_samples,
                                        max_q_size=256,
                                        nb_preprocessing_threads=2)

    return pred, filenames


def write_submission(predictions, filenames):
    with open('predictions_d3H_avg_3_193-0_36_4.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for i in xrange(0, len(predictions)):
            tmp = [filenames[i]]
            for p in predictions[i]:
                tmp.append(p)
            writer.writerow(tmp)
    print('%d predicitons written.' % (len(predictions)))


if __name__ == "__main__":
    predictions, filenames = predict()
    write_submission(predictions, filenames)

