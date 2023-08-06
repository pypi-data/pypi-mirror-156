import paddle
import paddlenlp
import numpy as np


class Dataset(paddle.io.Dataset):
    def __init__(self, X, y=None):
        self.X_data = X
        self.y_data = y

    def __getitem__(self, index):
        if type(self.X_data) is tuple:
            X = (Xi[index] for Xi in self.X_data)
            if self.y_data is None:
                return X
            y = self.y_data[index]
            return X, y
        X = self.X_data[index]
        if self.y_data is None:
            return X
        y = self.y_data[index]
        return X, y

    def __len__(self):
        if type(self.X_data) is tuple:
            return len(self.X_data[0])
        return len(self.X_data)

 
class TextDataset(paddle.io.Dataset):
    def __init__(self, X, y, tokenizer, max_seq_len=None):
        super(TextDataset, self).__init__()
        self.X_data = X
        self.y_data = y
        self.tokenizer = tokenizer
        if max_seq_len is not None:
            self.max_seq_len = max_seq_len
        elif type(self.X_data) is tuple:
            self.max_seq_len = 512
        else:
            self.max_seq_len = 128
        
    def __getitem__(self, index):
        if type(self.X_data) is tuple:
            sent_a = self.X_data[0][index]
            sent_b = self.X_data[1][index]
            ret = self.tokenizer(text=sent_a, text_pair=sent_b, max_seq_len=self.max_seq_len)
            input_ids = ret['input_ids']
            token_type_ids = ret['token_type_ids']
            input_ids = np.array(input_ids)
            token_type_ids = np.array(token_type_ids)
            if self.y_data is None:
                return input_ids, token_type_ids
            y = self.y_data[index]
            return input_ids, token_type_ids, y
        else:
            X = self.X_data[index]
            ret = self.tokenizer(X, )
            input_ids = ret['input_ids']
            input_ids = np.array(input_ids)
            if self.y_data is None:
                return input_ids
            y = self.y_data[index]
            return input_ids, y

    def __len__(self):
        if isinstance(self.X_data, tuple):
            return len(self.X_data[0])
        else:
            return len(self.X_data)


def tst_TextDataset():
    a = (['你好', '你好吗', '我很好'], ['你的', '我的', '他的'])
    a_x = ['你好', '你好吗', '我很好']
    a_y = [1, 0, 1]
   
    text_dataset = TextDataset(a_x, a_y, tokenizer='ernie-tiny')
    print(len(text_dataset))
    print(text_dataset[0])
    

class OutModel(paddle.nn.Layer):
    def __init__(self, model):
        super(OutModel, self).__init__()
        self.model = model
    
    def forward(self, x, xx=None):
        if xx is not None:
            return self.model(x, xx)
        else:
            return self.model(x)

class OutModel2(paddle.nn.Layer):
    def __init__(self, model):
        super(OutModel2, self).__init__()
        self.model = model
    
    def forward(self, x):
        return self.model(x)


def tst_model():
    model = paddlenlp.transformers.AutoModelForSequenceClassification.from_pretrained("ernie-tiny", num_classes=2)
    model = OutModel2(model)
    model = paddle.Model(model)
    model.prepare(paddle.optimizer.AdamW(learning_rate=0.01, parameters=model.parameters()), 
                    loss=paddle.nn.CrossEntropyLoss())
    a = (['你好', '你好吗', '我很好'], ['你的', '我的', '他的'])
    a_x = ['你好', '你好吗', '我很好']
    a_y = [1, 0, 1]
   
    text_dataset = TextDataset(a_x, a_y, tokenizer='ernie-tiny')
    model.fit(text_dataset)
    # x, y = text_dataset[0]
    # x0 = x[0].reshape(1, -1)
    # x1 = x[1].reshape(1, -1)
    # print(x0.shape, x1.shape)
    # ret = model((paddle.to_tensor(x0), paddle.to_tensor(x1)))
    # print(ret)

if __name__ == "__main__":
    # tst_TextDataset()
    tst_model()
    

