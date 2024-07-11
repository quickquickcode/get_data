import requests
import json
from tqdm import tqdm
import time

ETHERSCAN_API_KEY = 'IX99PC4XW7U5Y25T1VXM4ZQZBX1WSVWW1W'

def fetch_transactions_by_block(session, block_number, proxies):
    """根据区块号获取所有交易信息"""
    api_url = f'https://api.etherscan.io/api'
    params = {
        'module': 'proxy',
        'action': 'eth_getBlockByNumber',
        'tag': hex(block_number),
        'boolean': 'true',
        'apikey': ETHERSCAN_API_KEY
    }
    response = session.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['result']
    else:
        return None

def save_to_json(data, filename):
    """将数据保存到JSON文件"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def run_for_blocks(start_block, end_block, filename):
    all_transactions = {}

    # 设置你的代理
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    max_retries = 5  # 最大重试次数
    request_interval = 1.0 / 5  # 每秒最多五次请求
    last_request_time = time.time()
    
    with requests.Session() as session:
        
        for block_number in tqdm(range(start_block, end_block + 1), desc=f'Fetching Transactions for blocks {start_block} to {end_block}'):
            retries = 0
            while retries < max_retries:
                current_time = time.time()
                time_since_last_request = current_time - last_request_time
                if time_since_last_request < request_interval:
                    time.sleep((request_interval - time_since_last_request)/2)
                
                transactions = fetch_transactions_by_block(session, block_number, proxies)
                last_request_time = time.time()
                
                if transactions is None:
                    print(f"警告: 没有找到块 {block_number} 的交易，重试第 {retries + 1} 次")
                    retries += 1
                    session.close()  # 关闭当前session
                    session = requests.Session()  # 创建新的session
                    continue
                try:
                    temp = {}
                    temp["baseFeePerGas"] = int(transactions["baseFeePerGas"], 16)
                    max_gas_price = 0
                    for transaction in transactions["transactions"]:
                        gas_price = int(transaction["gasPrice"], 16)
                        if gas_price > max_gas_price:
                            max_gas_price = gas_price
                    temp["maxGasPrice"] = max_gas_price
                    if transactions:
                        all_transactions[block_number] = temp
                    break
                except Exception as e:
                    print(f"警告: 解析块 {block_number} 时出错，重试第 {retries + 1} 次")
                    retries += 1
                    session.close()  # 关闭当前session
                    session = requests.Session()  # 创建新的session
                except KeyError as e:
                    print(f"警告: 解析块 {block_number} 时出错，重试第 {retries + 1} 次")
                    retries += 1
                    session.close()  # 关闭当前session
                    session = requests.Session()  # 创建新的session

    # 保存到JSON文件
    save_to_json(all_transactions, filename)
    print(f'All transactions between blocks {start_block} and {end_block} have been saved to {filename}.')


def divide_interval(start, end, parts):
    """将区块范围等分为指定的份数"""
    delta = (end - start) // parts
    return [(start + i * delta, start + (i + 1) * delta - 1) for i in range(parts)]

if __name__ == '__main__':
    original_intervals = [
        #(19388222, 19390607),
        #(19390607, 19397698),
        #(19392970, 19397698)
        (19900000, 19910000),
        (19910000, 19920000),
        (19920000, 19930000),
        (19930000, 19940000),
        (19940000, 19950000),
        (19950000, 19960000), 
        (19960000, 19970000),
        (19970000, 19980000),
        (19980000, 19990000),
        (19990000, 20000000),
        
        #(19397698, 19404850),
        #(19404850, 19412014),
        #(19412014, 19419157),
        #(19419157, 19426310),
        #(19426310, 19433404),
    ]
    
    # # 现在我们将每个区间等分为三份
    # divided_intervals = []
    # for start, end in original_intervals:
    #     divided_intervals.extend(divide_interval(start, end, 3))
    
    # for i, (start_block, end_block) in enumerate(divided_intervals):
    #     filename = f'./transactions_{start_block}_to_{end_block}.json'
    #     run_for_blocks(start_block, end_block, filename)

    for i, (start_block, end_block) in enumerate(original_intervals):
        filename = f'./transactions_{start_block}_to_{end_block}.json'
        run_for_blocks(start_block, end_block, filename)
    