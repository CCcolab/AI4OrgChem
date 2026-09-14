# P14公开输入几何说明

[English](README.md)

两个XYZ文件是P14冻结固定几何端点所用的公开source-proxy几何。它们根据原著发表的五参数结构描述重构，**不是**原著未公开的笛卡尔坐标。

- `source_proxy_G.xyz`：普通G描述符几何；
- `source_proxy_PLG.xyz`：PLG描述符几何；
- 两者的C–H键长均固定为`1.080 Å`，因为原著表格未给出该坐标；
- 原子顺序为C1–C12，随后为H1–H6，与仓库内经检查的处理后JSON记录一致。

包括全精度坐标在内的权威机器记录是[`p14_C12H6_source_level_fixed_geometry_v0.1.json`](../processed/p14_C12H6_source_level_fixed_geometry_v0.1.json)。
