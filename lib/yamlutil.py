import yaml as y

basepath = "./data/"


class yaml:
    def __init__(self, path="./tmp.yaml"):
        self.path = basepath + path

    def load_yaml(self, default: any = dict()) -> any:
        """
        yamlを読み込んでそのままDictとかListにします。
        読み込めなかった場合にはdefaultの値を返します。
        """
        try:
            with open(self.path, 'r', encoding="utf-8_sig") as f:
                data = y.safe_load(f)
                if data != None:
                    return data
                return default
        except FileNotFoundError:
            return default

    def save_yaml(self, data: any):
        """
        yaml形式で保存します。
        """
        with open(self.path, 'w', encoding="utf-8_sig") as f:
            y.dump(data, f, default_flow_style=False, allow_unicode=True)
            return data
