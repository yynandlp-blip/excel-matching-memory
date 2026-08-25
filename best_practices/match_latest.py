import pandas as pd
import re
import json
import unicodedata
import html
import sys

def clean_name(s):
    if pd.isna(s):
        return ''
    s = str(s).strip()
    s = html.unescape(s)
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'\d+$', '', s).strip()
    return s

def clean_unit(s):
    if pd.isna(s):
        return ''
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKC', s)
    return s

def clean_qty(v):
    if pd.isna(v):
        return ''
    try:
        f = float(v)
        if f == int(f):
            return str(int(f))
        return str(f)
    except:
        return str(v).strip()

def find_col(columns, patterns):
    for pat in patterns:
        for col in columns:
            if pat in str(col):
                return col
    return None

def match(tender_path, supply_path):
    t = pd.read_excel(tender_path)
    s = pd.read_excel(supply_path)

    tender_id_col = find_col(t.columns, ['业务主键ID', '主键', '招标序号']) or t.columns[0]
    tender_name_col = find_col(t.columns, ['销售货品名', '货品名', '物料名称', '品名', '名称'])
    tender_unit_col = find_col(t.columns, ['单位'])
    tender_qty_col = find_col(t.columns, ['数量', '采购数量', '需求数量'])

    supply_id_col = find_col(s.columns, ['业务主键ID', '主键']) or s.columns[0]
    supply_name_col = find_col(s.columns, ['供货货品名', '销售货品名', '货品名', '物料名称', '品名', '名称'])
    supply_unit_col = find_col(s.columns, ['单位'])
    supply_qty_col = find_col(s.columns, ['数量', '供货数量', '库存数量'])
    supply_price_col = find_col(s.columns, ['实际供货单价', '供货单价', '单价', '报价'])

    supply_map = {}
    for _, row in s.iterrows():
        key = (clean_name(row[supply_name_col]), clean_unit(row[supply_unit_col]), clean_qty(row[supply_qty_col]))
        if key not in supply_map:
            supply_map[key] = row

    matched_list = []
    for _, row in t.iterrows():
        key = (clean_name(row[tender_name_col]), clean_unit(row[tender_unit_col]), clean_qty(row[tender_qty_col]))
        if key in supply_map:
            sp = supply_map[key]
            price = round(float(sp[supply_price_col]), 2)
            qty = float(row[tender_qty_col])
            amt = round(price * qty, 2)
            matched_list.append({
                'id': int(row[tender_id_col]),
                'goods_name': html.unescape(str(sp[supply_name_col])),
                'price': f"{price:.2f}",
                'amt': f"{amt:.2f}"
            })

    return len(t), matched_list

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('{"error":"缺少参数"}')
        sys.exit(1)
    total, data = match(sys.argv[1], sys.argv[2])
    parts = []
    for item in data:
        parts.append(
            '{"id":' + str(item['id']) +
            ',"goods_name":' + json.dumps(item['goods_name'], ensure_ascii=False) +
            ',"price":' + item['price'] +
            ',"amt":' + item['amt'] + '}'
        )
    out = '{"total":' + str(total) + ',"matched":' + str(len(data)) + ',"data":[' + ','.join(parts) + ']}'
    print(out)
