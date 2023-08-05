import paddle


class Dataset(paddle.io.Dataset):
    def __init__(self, X, y):
        self.X_data = X
        self.y_data = y

    def __getitem__(self, index):
        if type(self.X_data) is tuple:
            X = (Xi[index] for Xi in self.X_data)
            y = self.y_data[index]
            return X, y
        X = self.X_data[index]
        y = self.y_data[index]
        return X, y

    def __len__(self):
        return len(self.X_data)
