import paddle


class MultiClassPrecision(paddle.metric.Metric):
    def __init__(self, name="multi-class precision", *args, **kwargs):
        super(MultiClassPrecision, self).__init__(*args, **kwargs)
        self.name = name
        pred_cnt = dict()
        label_cnt = dict()

    def name(self):
        return self.name

    def update(self, preds, labels):
        pass

    def reset(self):
        pass


    def accumulate(self):
        return 1.0, 0.0

