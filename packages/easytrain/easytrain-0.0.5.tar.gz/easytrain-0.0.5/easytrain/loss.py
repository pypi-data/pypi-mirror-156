import numpy as np
from paddle import nn
import paddle
from paddle.nn import functional as F


class FocalLoss(nn.Layer):
    def __init__(self, reduction='mean', weight=None, ignore_index=-1, alpha=None, gamma=2):
        super().__init__()
        if weight is not None:
            if type(weight) is list:
                weight = paddle.to_tensor(weight, dtype='float32')
            alpha = weight
        self.reduction = reduction
        # 不能进行reduction运算，需要精确的获取每一个-log(p),并通过torch.exp(-log(p))求的p
        self.ce_loss_none_alpha = nn.CrossEntropyLoss(reduction="none", soft_label=False, ignore_index=ignore_index,
                                                      axis=-1)
        # 不能进行reduction运算，需要将每一个-log(p)与(1-p)^gamma进行精确的相乘
        self.ce_loss_with_alpha = nn.CrossEntropyLoss(reduction="none", soft_label=False, weight=alpha,
                                                      ignore_index=ignore_index, axis=-1)
        self.gamma = gamma

    # preds:模型的原始输出，没有经过softmax函数处理
    # target:原始标签数据，没有被转换为独热码
    def forward(self, preds, target):
        # 计算每个目录类别的loss，即y_ture*log(y_pred)
        ce_loss = self.ce_loss_none_alpha(preds, target)
        # 难易样本调节,作为梯度调节系数，不需要对 paddle.exp(-ce_loss)=>p进行求导操作
        easy_diff_adjust = paddle.pow((1 - paddle.exp(-ce_loss)), self.gamma).detach()
        # 计算交叉熵与alpha的乘积
        alpha_ce_loss = self.ce_loss_with_alpha(preds, target)
        loss = easy_diff_adjust * alpha_ce_loss
        return self.reduce_loss(loss, self.reduction)

    def reduce_loss(self, loss, reduction='mean'):
        return loss.mean() if reduction == 'mean' else loss.sum() if reduction == 'sum' else loss


if __name__ == "__main__":
    weight_list = [2, 2, 2, 2, 3, 4, 5, 5, 7, 8, 11, 12, 13, 13, 13, 14, 15, 15, 15, 16, 16, 17, 18, 18, 19, 20,
                   21, 21, 22, 26, 27, 30, 32, 35, 36, 40, 45, 48, 56, 90, 90, 100]
    criterion = FocalLoss(weight=weight_list)
    logits = np.random.rand(4, len(weight_list)).astype("float64")
    logits = paddle.to_tensor(logits)
    labels = np.random.randint(0, len(weight_list), size=(4, 1)).astype(np.int64)
    labels = paddle.to_tensor(labels)
    result = criterion(logits, labels)
    print(result)