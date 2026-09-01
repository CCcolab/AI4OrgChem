# WP4 / Gate V2-4P 轮烯成对先导报告

- Gate：`NOT_PASSED`
- 科学状态：`INDETERMINATE_INPUT_DEFINITION_INCOMPLETE`
- 科学计算：未启动，避免以猜测结构改变 ISE-II 估计量
- P12-A：V0.1 冻结结论不变
- P12-A / P12-B：`INCOMPARABLE`

## 原因

协议已冻结 `8/10、16/18、32/34`、B3LYP/6-31G(d)、ZPVE、双构象来源和停止标准，但本地尚无六组 A/B/C/D 的精确结构身份与笛卡尔坐标。2025 年 ISE-II 来源还复用了更早文献中的 B/D 能量和 ZPVE。此时直接生成结构会改变主估计量，因此本次 V0.2 将缺口作为可审计结果发布，而不制造数值。

来源核对：[Van Nyvel, Alonso and Solà, Chemical Science 2025, DOI 10.1039/D4SC08225G](https://doi.org/10.1039/D4SC08225G) 及其补充信息。

## 后续解锁条件

取得并许可归档 A/B/C/D 的来源结构、版本化坐标及反–顺校正定义后，重新密封 WP4 输入包，再执行构象搜索、无虚频确认和 0 K ASE。
