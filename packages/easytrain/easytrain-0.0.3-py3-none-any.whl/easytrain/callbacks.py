import paddle
import numpy as np
from sklearn.metrics import classification_report


class ClassifierEvalCallback(paddle.callbacks.Callback):
    def __init__(self, eval_dataset, label_names=None, eval_freq=10):
        self.eval_dataset = eval_dataset
        self.label_names = label_names
        self.eval_freq = eval_freq

    def on_train_batch_end(self, step, logs=None):
        print("here step={}".format(step))
        if (step + 1) % self.eval_freq != 0:
            return
        y_true = []
        for i in range(len(self.eval_dataset)):
            _, y = self.eval_dataset[i]
            y_true.append(y)
        y_true = np.array(y_true)
        y_pred = self.model.predict(self.eval_dataset, stack_outputs=True, verbose=0)[0]
        y_pred = y_pred.argmax(axis=1)
        if self.label_names is not None:
            y_true = [self.label_names[y] for y in y_true]
            y_pred = [self.label_names[y] for y in y_pred]
        result = classification_report(y_true, y_pred)
        print(result)