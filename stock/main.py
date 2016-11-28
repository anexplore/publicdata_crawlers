#coding=utf-8
import sys
import time
import stock.sina_stock_api as sina_stock_api
import stock.utils as utils    

def get_all_stock(save_path):
    """获得所有A股股票
    Args:
        save_path: 保存路径
    """
    save_file = open(save_path, 'w')
    try:
        index = 0
        while True:
            total_count, count, items = sina_stock_api.astock_list(index, 40)
            if count == 0:
                break
            for symbol, code, name in items:
                line = '%s\t%s\t%s\n' % (symbol, code, name)
                print line
                save_file.write(line.encode('utf-8'))
            index += 1
    finally:
        if save_file:
            save_file.close()

#sh600059 sh600059
def show_stock_realtime_hq(stock_list_string):
    """动态更新股票的最新行情
    Args:
        stock_list_string: 股票列表: sz002385,sz002170
    """
    if not stock_list_string:
        return
    while True:
        hq_list =  sina_stock_api.stocks_hq(stock_list_string)
        hq_string_list = []
        for hq in hq_list:
            hq_string_list.append('%s\t%s\t%f' % (hq[0], hq[3],100 * (float(hq[3]) - float(hq[2])) / float(hq[2])))

        sys.stdout.write('\r' + '\t'.join(hq_string_list))
        sys.stdout.flush()
        time.sleep(1)

if __name__ == '__main__':
    #get_all_stock('all_stock')
    show_stock_realtime_hq('sz002385,sz002170')
