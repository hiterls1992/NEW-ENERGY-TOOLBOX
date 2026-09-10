# -*- coding: utf-8 -*-
"""将 data/ 下 7 个热轧型钢 CSV 合并生成 data/热轧型钢截面特性-data.js（供工具页 <script> 引入）。"""
import csv
import io
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 文件名 -> 类别名（与工具页显示一致）
FILES = [
    ("GBT706-2016_工字钢.csv",      "工字钢"),
    ("GBT706-2016_槽钢.csv",        "槽钢"),
    ("GBT706-2016_等边角钢.csv",    "等边角钢"),
    ("GBT706-2016_不等边角钢.csv",  "不等边角钢"),
    ("GBT11263-2024_附录A_H型钢.csv", "H型钢"),
    ("GBT11263-2024_附录B_HK型钢.csv", "HK型钢"),
    ("GBT11263-2024_附录C_剖分T型钢.csv", "剖分T型钢"),
]

# 列名标准化：原始表头 -> 展示名（含单位，单位用括号包住便于工具页拆分）
LABEL_MAP = {
    "型号": "型号",
    "h_mm": "高度 h (mm)", "b_mm": "宽度 b (mm)", "B_mm": "长肢宽 B (mm)",
    "d_mm": "腰厚/肢厚 d (mm)", "t_mm": "翼缘厚 t (mm)",
    "r_mm": "圆角半径 r (mm)", "r1_mm": "肢端圆角 r1 (mm)",
    "H": "高度 H (mm)", "B": "宽度 B (mm)", "t1": "腹板厚 t1 (mm)", "t2": "翼缘厚 t2 (mm)",
    "h": "高度 h (mm)",
    "截面面积_cm2": "截面面积 A (cm²)",
    "理论重量_kg/m": "理论重量 (kg/m)",
    "外表面积_m2/m": "外表面积 (m²/m)",
    "Ix_cm4": "惯性矩 Ix (cm⁴)", "Iy_cm4": "惯性矩 Iy (cm⁴)",
    "Ix1_cm4": "惯性矩 Ix1 (cm⁴)", "Iy1_cm4": "惯性矩 Iy1 (cm⁴)",
    "Ix0_cm4": "惯性矩 Ix0 (cm⁴)", "Iy0_cm4": "惯性矩 Iy0 (cm⁴)",
    "Iu_cm4": "惯性矩 Iu (cm⁴)",
    "ix_cm": "回转半径 ix (cm)", "iy_cm": "回转半径 iy (cm)",
    "ix0_cm": "回转半径 ix0 (cm)", "iy0_cm": "回转半径 iy0 (cm)",
    "iu_cm": "回转半径 iu (cm)",
    "Wx_cm3": "截面模量 Wx (cm³)", "Wy_cm3": "截面模量 Wy (cm³)",
    "Wx0_cm3": "截面模量 Wx0 (cm³)", "Wy0_cm3": "截面模量 Wy0 (cm³)",
    "Wu_cm3": "截面模量 Wu (cm³)",
    "Z0_cm": "重心距离 Z0 (cm)",
    "tanA": "tanα",
    "X0_cm": "形心距 X0 (cm)", "Y0_cm": "形心距 Y0 (cm)",
    "重心Cx_cm": "重心距离 Cx (cm)",
    "对应H型钢系列": "对应H型钢系列",
    "基准规格△": "基准规格",
}

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def fmt_token(s):
    """数值保持数字形式（省引号、减小体积），其余以字符串输出；空值输出空字符串。"""
    s = s.strip()
    if s == "":
        return '""'
    if is_number(s):
        return s
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def main():
    out = io.StringIO()
    out.write("""/* ============================================================
 * 热轧型钢截面特性 数据文件
 * 由 data/ 下 7 个 CSV（GBT706-2016 / GBT11263-2024）生成，勿手工修改
 * 结构：var HOT_ROLLED_STEEL = { "<类别>": { labels:[...], rows:[[...]] }, ... }
 * 数值缺失以 "" 表示；labels 中带 (单位) 的列为数值列
 * ============================================================ */
var HOT_ROLLED_STEEL = {
""")

    for fname, cat in FILES:
        path = os.path.join(BASE, fname)
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f))
        header = [h.strip() for h in reader[0]]
        rows = reader[1:]
        labels = [LABEL_MAP.get(h, h) for h in header]
        out.write('  "%s": {\n' % cat)
        out.write("    labels: [%s],\n" % ", ".join('"%s"' % x for x in labels))
        out.write("    rows: [\n")
        for r in rows:
            # 补齐/截断到表头长度，保证每行列数一致
            vals = (r + [""] * len(header))[:len(header)]
            out.write("      [%s],\n" % ", ".join(fmt_token(v) for v in vals))
        out.write("    ]\n  },\n")

    out.write("};\n")
    dst = os.path.join(BASE, "热轧型钢截面特性-data.js")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out.getvalue())

    # 汇总统计
    with open(dst, "r", encoding="utf-8") as f:
        total = f.read().count("\n      [")
    print("OK ->", dst, "| 共", total, "行数据")

if __name__ == "__main__":
    main()
