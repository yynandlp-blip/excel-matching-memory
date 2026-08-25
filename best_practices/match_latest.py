import pandas as pd
import re
import json
import unicodedata
import sys

def clean_name(s):
    if pd.isna(s):
        return ''
    s = str(s).strip()
    # 全角转半角
    s = unicodedata.normalize('NFKC', s)
    # 去除末尾数字（如 "pH传感器4" → "pH传感器"）
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

def find_col(columns, patterns, first_match=True):
    """按优先级在列名中查找匹配列"""
    for pat in patterns:
        for col in columns:
            if pat in str(col):
                return col
    return None

def match(tender_path, supply_path):
    t = pd.read_excel(tender_path)
    s = pd.read_excel(supply_path)

    # 列名识别
    tender_id_col = find_col(t.columns, ['业务主键ID', '主键', '招标序号']) or t.columns[0]
    tender_name_col = find_col(t.columns, ['销售货品名', '货品名', '物料名称', '品名', '名称'])
    tender_unit_col = find_col(t.columns, ['单位'])
    tender_qty_col = find_col(t.columns, ['数量', '采购数量', '需求数量'])

    supply_id_col = find_col(s.columns, ['业务主键ID', '主键']) or s.columns[0]
    supply_name_col = find_col(s.columns, ['供货货品名', '销售货品名', '货品名', '物料名称', '品名', '名称'])
    supply_unit_col = find_col(s.columns, ['单位'])
    supply_qty_col = find_col(s.columns, ['数量', '供货数量', '库存数量'])
    supply_price_col = find_col(s.columns, ['实际供货单价', '供货单价', '单价', '报价'])

    # 构建供货侧索引：三键 -> 第一条记录
    supply_map = {}
    for _, row in s.iterrows():
        key = (clean_name(row[supply_name_col]), clean_unit(row[supply_unit_col]), clean_qty(row[supply_qty_col]))
        if key not in supply_map:
            supply_map[key] = row

    # 匹配
    matched_list = []
    for _, row in t.iterrows():
        key = (clean_name(row[tender_name_col]), clean_unit(row[tender_unit_col]), clean_qty(row[tender_qty_col]))
        if key in supply_map:
            sp = supply_map[key]
            price = float(sp[supply_price_col])
            qty = float(row[tender_qty_col])
            amt = round(price * qty, 2)
            matched_list.append({
                'id': int(row[tender_id_col]),
                'goods_name': str(sp[supply_name_col]),
                'price': price,
                'amt': amt
            })

    result = {
        'total': len(t),
        'matched': len(matched_list),
        'data': matched_list
    }
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': '缺少参数: tender_path supply_path'}, ensure_ascii=False))
        sys.exit(1)
    res = match(sys.argv[1], sys.argv[2])
    print(json.dumps(res, ensure_ascii=False, separators=(',', ':')))
