from src.utils.utils import probabilities_to_binary


def predict(classifier, predict_data, prediction_optimal_threshold=0.5):
    """ Function for predictions. Returns both classes and probabilites and get take customer threshold for binary

    Args:
        classifier (sklearn object) trained classifier to use for prediction
        predict_data (numpay array or pandas dataframe) preprocessed data readed to be fed to classifier
        prediction_optimal_threshold (float) 0-1 value for converting continuous probability to binary classes

    Returns:
        predicted_probabilities (list) list of predicted probabilities for the corresponding data
        predicted_probabilities (list) list of converted predicted probabilities into classes

    """
    predicted_probabilities = classifier.predict_proba(predict_data)[:, 1]
    predicted_classes = probabilities_to_binary(predicted_probabilities, prediction_optimal_threshold)

    return predicted_probabilities, predicted_classes