# WP2 / Gate V2-2 跨程序复算报告

- Gate：`NOT_PASSED`
- 科学状态：`INDETERMINATE_PSI4_BACKEND_CONTRACT_AND_ORCA_UNAVAILABLE`
- PySCF/Psi4 功能能量烟测：`PASS`
- Psi4 无DF后端合同：`FAIL`
- ORCA：`not available`；未使用替代程序冒充 ORCA
- 烟测/锚点最大绝对能量差：`1.80854755172e-07 Eh`（门限 `5e-6 Eh`）
- 最大梯度 RMS 差：`nan Eh/bohr`（门限 `5e-5 Eh/bohr`）

## 判定

苯功能能量烟测在数值容差内，但Psi4 1.11在请求DIRECT DFT时实际进入MemDFJK/@DF-RKS；精确PK路径对最大NBA锚点又超出本轮合理资源规模。因此八个核心锚点在第一个结果产生前按失败纪律停止。加之本机没有经许可的ORCA二进制，Gate V2-2保持NOT_PASSED。该结果不修改V0.1十四项结论，也不把普通态复算冒充LFMO/DSI/FUD自定义态复现。

机器记录：`data/science_v0.2/raw/wp2/wp2_open_program_anchors.json`（SHA-256 `1fa0c478a5acd312a06d63af2eeae7f0c95694107eae0eeb40ecfa3275e10c10`）。
