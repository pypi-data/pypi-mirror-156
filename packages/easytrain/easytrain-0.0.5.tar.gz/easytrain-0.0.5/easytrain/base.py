import numpy as np
import paddle
import paddlenlp
from .data import Dataset
from .callbacks import ClassifierEvalCallback
from .loss import FocalLoss


class Model:
    def __init__(self, network):
        self.network = network
        self.model = paddle.Model(network)
        self.optimizer = None
        self.learning_rate = None
        self.warmup = None
        self.loss = None
        self.weight = None
        self.metrics = None
        self.amp_configs = None
        self.label_names = None
        self.prepared = False

    def prepare(self, optimizer='adamw', learning_rate=5e-5, warmup=None,
                loss="cross_entropy", weight=None, metrics="acc", amp_configs=None):
        """主要用来指定模型的优化器和损失函数

        Args:
            optimizer (str, optional): _description_. Defaults to 'adamw'.
            learning_rate (_type_, optional): _description_. Defaults to 5e-5.
            warmup (_type_, optional): _description_. Defaults to None.
            loss (str, optional): _description_. Defaults to "cross_entropy".
                options: "cross_entropy", "focal_loss"
            weight: list, c dims, c is class num
            metrics (str, optional): _description_. Defaults to "acc".
            amp_configs (_type_, optional): _description_. Defaults to None.
        """
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.warmup = warmup
        self.loss = loss
        self.weight = weight
        self.metrics = metrics
        self.amp_configs = amp_configs
        if type(loss) is str:
            self.loss = self._get_loss()
        if type(metrics) is str or type(metrics) is list:
            self.metrics = self._get_metrics()
        if warmup is not None:
            return
        if type(optimizer) is str:
            self.optimizer = self._get_optimizer()

        self.model.prepare(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics, amp_configs=amp_configs)
        self.prepared = True

    def _get_optimizer(self, num_training_steps=None):
        if self.warmup is not None:
            lr_scheduler = paddlenlp.transformers.LinearDecayWithWarmup(self.learning_rate,
                                                                        num_training_steps,
                                                                        self.warmup)
            optimizer = paddle.optimizer.AdamW(learning_rate=lr_scheduler, parameters=self.model.parameters())
            return optimizer
        if type(self.optimizer) is not str:
            return self.optimizer
        if self.optimizer == 'adamw':
            optimizer = paddle.optimizer.AdamW(learning_rate=self.learning_rate, parameters=self.model.parameters())
        else:
            optimizer = paddle.optimizer.AdamW(learning_rate=self.learning_rate, parameters=self.model.parameters())
        return optimizer

    def _get_loss(self):
        if self.loss == 'cross_entropy':
            loss = paddle.nn.CrossEntropyLoss()
        if self.loss == 'focal_loss':
            loss = FocalLoss(weight=self.weight)
        else:
            loss = paddle.nn.CrossEntropyLoss()
        return loss

    def _get_metrics(self):
        if self.metrics == 'acc':
            metrics = paddle.metric.Accuracy()
        else:
            metrics = None
        return metrics

    def fit(self, X, y=None, eval_X=None, eval_y=None, label_names=None, batch_size=32, epochs=10, eval_freq=1,
            log_freq=10, save_dir=None, save_freq=1, verbose=2, drop_last=False,
            shuffle=True, num_workers=0, callbacks=None):
        """执行训练

        Args:
            X (_type_): _description_
            y (_type_, optional): _description_. Defaults to None.
            eval_X (_type_, optional): _description_. Defaults to None.
            eval_y (_type_, optional): _description_. Defaults to None.
            label_names (_type_, optional): _description_. Defaults to None.
            batch_size (int, optional): _description_. Defaults to 32.
            epochs (int, optional): _description_. Defaults to 10.
            eval_freq (int, optional): _description_. Defaults to 1.
            log_freq (int, optional): _description_. Defaults to 10.
            save_dir (_type_, optional): _description_. Defaults to None.
            save_freq (int, optional): _description_. Defaults to 1.
            verbose (int, optional): _description_. Defaults to 2.
            drop_last (bool, optional): _description_. Defaults to False.
            shuffle (bool, optional): _description_. Defaults to True.
            num_workers (int, optional): _description_. Defaults to 0.
            callbacks (_type_, optional): _description_. Defaults to None.
        """
        if isinstance(X, paddle.io.Dataset) or isinstance(X, paddle.io.DataLoader):
            train_data = X
        else:
            # check
            assert (y is not None)
            if type(X) is tuple:
                for Xi in X:
                    assert len(Xi) == len(y)
            else:
                assert (len(X) == len(y))
            train_data = Dataset(X, y)

        # 如果没有执行prepare,当前只有一种情况，就是warmup需要获取训练总步长
        if not self.prepared:
            num_training_steps = len(train_data) * epochs // batch_size
            optimizer = self._get_optimizer(num_training_steps)
            self.model.prepare(optimizer=optimizer, loss=self.loss, metrics=self.metrics, amp_configs=self.amp_configs)

        eval_data = None
        if eval_X is not None:
            if isinstance(eval_X, paddle.io.Dataset) or isinstance(eval_X, paddle.io.DataLoader):
                eval_data = eval_X
            else:
                assert eval_y is not None
                if type(eval_X) is tuple:
                    for Xi in eval_X:
                        assert len(Xi) == len(eval_y)
                else:
                    assert len(eval_X) == len(eval_y)
                eval_data = Dataset(eval_X, eval_y)

        self.label_names = label_names
        default_callbacks = []
        if self.label_names is not None and eval_data is not None:
            callback = ClassifierEvalCallback(eval_data, label_names=self.label_names, eval_freq=eval_freq, num_workers=num_workers)
            default_callbacks.append(callback)
            eval_freq = 10000
        callback = paddle.callbacks.VisualDL(log_dir='visualdl_log_dir')
        default_callbacks.append(callback)
        callback = paddle.callbacks.LRScheduler(by_step=True, by_epoch=False)
        default_callbacks.append(callback)
        all_callbacks = default_callbacks
        if callbacks is not None:
            all_callbacks.extend(callbacks)

        self.model.fit(train_data, eval_data, batch_size=batch_size, epochs=epochs, eval_freq=eval_freq,
                       log_freq=log_freq, save_dir=save_dir, save_freq=save_freq, verbose=verbose,
                       drop_last=drop_last, shuffle=shuffle, num_workers=num_workers, callbacks=all_callbacks)

    def predict(self, X, batch_size=1, num_workers=0, stack_outputs=True, callbacks=None, verbose=0):
        """执行预测

        Args:
            X (_type_): _description_
            y (_type_, optional): _description_. Defaults to None.
            batch_size (int, optional): _description_. Defaults to 1.
            num_workers (int, optional): _description_. Defaults to 0.
            stack_outputs (bool, optional): _description_. Defaults to True.
            callbacks (_type_, optional): _description_. Defaults to None.
            verbose (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        if isinstance(X, paddle.io.Dataset) or isinstance(X, paddle.io.DataLoader):
            result = self.model.predict(X, batch_size=batch_size, num_workers=num_workers,
                                        stack_outputs=stack_outputs, callbacks=callbacks, verbose=verbose)
            return result[0]

        dataset = Dataset(X)
        result = self.model.predict(dataset, batch_size=batch_size, num_workers=num_workers,
                                    stack_outputs=stack_outputs, callbacks=callbacks, verbose=verbose)
        return result[0]

    def load(self, path, skip_mismatch=False, reset_optimizer=False):
        self.model.load(path, skip_mismatch=skip_mismatch, reset_optimizer=reset_optimizer)


def test():
    X_train = np.random.rand(100, 10).astype('float32')
    y = np.random.randint(0, 10, 100)
    net = paddle.nn.Sequential(
        paddle.nn.Linear(10, 32),
        paddle.nn.ReLU(),
        paddle.nn.Linear(32, 10),
        paddle.nn.Sigmoid())
    model = Model(net)
    model.prepare(label_names=["class_" + str(i) for i in range(10)])
    model.fit(X_train, y, X_train, y)


if __name__ == "__main__":
    test()




