from cnn.keras.models.partitions4.model import build_model
from cnn.keras.prediction.predict_generator import predict_generator
from cnn.keras.partitions.preprocessing.image_processing import inputs
from cnn.keras.utils.write_prediction import write_prediction
from utils.split_scans import read_imageID
from utils.config import config


classes = ['Normal', 'AD']
target_size = (29, 29, 29)
batch_size = 16
load_all_scans = False
path_weights = '/home/mhubrich/weights.795-loss_0.362-acc_0.849.h5'
output_name = 'part4_1_795-5_5.csv'

interval_x = range(7, 86+2 - target_size[0], 5)
interval_y = range(3, 92+2 - target_size[1], 5)
interval_z1 = [15, 17, 19, 21, 23]
interval_z2 = [43, 45, 47, 49, 51]
grid1 = [(x, y, z) for x in interval_x for y in interval_y for z in interval_z1]
grid2 = [(x, y, z) for x in interval_x for y in interval_y for z in interval_z2]
grid = [grid1, grid2]


def predict():
    # Get inputs for labeling
    scans_test = read_imageID(config['ADNI'], '/home/mhubrich/mogon_val')
    test_inputs = inputs(scans_test, target_size, grid, batch_size, load_all_scans, classes, 'predict')

    # Set up the model
    model = build_model(num_classes=len(classes), input_shape=(1,)+target_size)
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.load_weights(path_weights)

    # Start labeling
    pred, filenames = predict_generator(model,
                                        test_inputs,
                                        val_samples=test_inputs.nb_sample,
                                        max_q_size=64,
                                        nb_preprocessing_threads=2)

    return pred, filenames


if __name__ == "__main__":
    predictions, filenames = predict()
    write_prediction(output_name, predictions, filenames)
