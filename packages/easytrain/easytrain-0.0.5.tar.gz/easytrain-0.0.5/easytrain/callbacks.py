import paddle
from paddle.utils import try_import
import numbers
from paddle.distributed import ParallelEnv
import numpy as np
from sklearn.metrics import classification_report


class ClassifierEvalCallback(paddle.callbacks.Callback):
    def __init__(self, eval_dataset, label_names=None, eval_freq=10, num_workers=0):
        self.eval_dataset = eval_dataset
        self.label_names = label_names
        self.eval_freq = eval_freq
        self.num_workers = num_workers

    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1) % self.eval_freq != 0:
            return
        print("start to get report ...")
        if isinstance(self.eval_dataset, paddle.io.DataLoader):
            y_true = []
            for i, batch_data in enumerate(self.eval_dataset):
                _, _, y = batch_data
                y = y.numpy().reshape(-1)
                y_true.append(y)
            y_true = np.concatenate(y_true)
        else:
            y_true = []
            for i in range(len(self.eval_dataset)):
                _, y = self.eval_dataset[i]
                y_true.append(y)
            y_true = np.array(y_true)
        y_pred = self.model.predict(self.eval_dataset, stack_outputs=True, verbose=0,
                                    num_workers=self.num_workers)[0]
        y_pred = y_pred.argmax(axis=1)
        if self.label_names is not None:
            y_true = [self.label_names[y] for y in y_true]
            y_pred = [self.label_names[y] for y in y_pred]
        result = classification_report(y_true, y_pred, digits=4)
        print("--------------------------- classification report -----------------------------\n")
        print(result)

 
class VisualDL(paddle.callbacks.Callback):
    """
    VisualDL callback function.
    Args:
        log_dir (str): The directory to save visualdl log file.
    Examples:
        .. code-block:: python
            import paddle
            import paddle.vision.transforms as T
            from paddle.static import InputSpec
            inputs = [InputSpec([-1, 1, 28, 28], 'float32', 'image')]
            labels = [InputSpec([None, 1], 'int64', 'label')]
            transform = T.Compose([
                T.Transpose(),
                T.Normalize([127.5], [127.5])
            ])
            train_dataset = paddle.vision.datasets.MNIST(mode='train', transform=transform)
            eval_dataset = paddle.vision.datasets.MNIST(mode='test', transform=transform)
            net = paddle.vision.models.LeNet()
            model = paddle.Model(net, inputs, labels)
            optim = paddle.optimizer.Adam(0.001, parameters=net.parameters())
            model.prepare(optimizer=optim,
                        loss=paddle.nn.CrossEntropyLoss(),
                        metrics=paddle.metric.Accuracy())
            
            ## uncomment following lines to fit model with visualdl callback function
            # callback = paddle.callbacks.VisualDL(log_dir='visualdl_log_dir')
            # model.fit(train_dataset, eval_dataset, batch_size=64, callbacks=callback)
    """

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.epochs = None
        self.steps = None
        self.epoch = 0

    def _is_write(self):
        return ParallelEnv().local_rank == 0

    def on_train_begin(self, logs=None):
        self.epochs = self.params['epochs']
        assert self.epochs
        self.train_metrics = self.params['metrics']
        assert self.train_metrics
        self._is_fit = True
        self.train_step = 0

    def on_epoch_begin(self, epoch=None, logs=None):
        self.steps = self.params['steps']
        self.epoch = epoch

    def _updates(self, logs, mode):
        if not self._is_write():
            return
        if not hasattr(self, 'writer'):
            visualdl = try_import('visualdl')
            self.writer = visualdl.LogWriter(self.log_dir)

        metrics = getattr(self, '%s_metrics' % (mode))
        current_step = getattr(self, '%s_step' % (mode))

        if mode == 'train':
            total_step = current_step
        else:
            total_step = self.epoch

        for k in metrics:
            if k in logs:
                temp_tag = mode + '/' + k

                if isinstance(logs[k], (list, tuple)):
                    temp_value = logs[k][0]
                elif isinstance(logs[k], numbers.Number):
                    temp_value = logs[k]
                else:
                    continue

                self.writer.add_scalar(
                    tag=temp_tag, step=total_step, value=temp_value)

    def on_train_batch_end(self, step, logs=None):
        logs = logs or {}
        self.train_step += 1

        if self._is_write():
            self._updates(logs, 'train')

    def on_eval_begin(self, logs=None):
        self.eval_steps = logs.get('steps', None)
        self.eval_metrics = logs.get('metrics', [])
        self.eval_step = 0
        self.evaled_samples = 0

    def on_train_end(self, logs=None):
        if hasattr(self, 'writer'):
            self.writer.close()
            delattr(self, 'writer')

    def on_eval_end(self, logs=None):
        if self._is_write():
            self._updates(logs, 'eval')

            if (not hasattr(self, '_is_fit')) and hasattr(self, 'writer'):
                self.writer.close()
                delattr(self, 'writer')