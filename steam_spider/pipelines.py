import json
from itemadapter import ItemAdapter


class SteamSpiderPipeline:
    def open_spider(self, spider):
        self.file = open('games.json', 'w')
        self.game_info = {}

    def close_spider(self, spider):
        self.file.write('{\n')
        for num1, key in enumerate(self.game_info.keys()):
            self.file.write('\t' + json.dumps(key) + ':\n')
            self.file.write('\t\t[\n')
            for num2, val in enumerate(self.game_info[key]):
                if num2 < len(self.game_info[key]) - 1:
                    self.file.write('\t\t\t' + json.dumps(val) + ',\n')
                else:
                    self.file.write('\t\t\t' + json.dumps(val) + '\n')
            if num1 < len(self.game_info.keys()) - 1:
                self.file.write('\t],\n')
            else:
                self.file.write('\t]\n')
        self.file.write('}\n')
        self.file.close()

    def process_item(self, item, spider):
        if item.get_request() not in self.game_info:
            self.game_info[item.get_request()] = [ItemAdapter(item).asdict()]
        else:
            self.game_info[item.get_request()].append(ItemAdapter(item).asdict())
        return item
