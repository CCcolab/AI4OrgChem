# P05 Table 5-15七角度连续序列协议 v0.2

## 命题和观测量

P05检验“π–σ轨道相互作用可表现为去稳定化”。唯一端点定义为：

`Delta E_pi_sigma(theta) = E_G(theta) - E_FUD(theta)`。

- 大于`+1.0e-8 Eh`：去稳定化方向；
- 小于`-1.0e-8 Eh`：稳定化方向；
- 其余：容差内不能定号。

## 冻结计算条件

- 同一diphenyl imine固定parent source-proxy；
- 刚性扭转角：0°、5°、10°、17°、25°、35°、45°；
- PySCF RHF/6-31G(d)；
- 同一G/FUD状态构造、source-block metric density和原始RHF能量泛函；
- 逐几何重构LFMO，不更换分子、基组或估计量。

## 预注册验收标准

1. 七点全部通过技术门禁；
2. 0°保持容差内零控制；
3. 六个非零角度端点全部为正；
4. `direct_total + pi_response + sigma_response = E_G-E_FUD`，闭合容差`1.0e-9 Eh`；
5. 17°端点与冻结锚点偏差不超过`1.0e-12 Eh`；
6. LFMO根数和分组维数在七点保持不变。

完整机器协议见[`seven-angle-protocol.yaml`](seven-angle-protocol.yaml)，机器结果见[`seven-angle-result.json`](seven-angle-result.json)。

## 判定边界

Gate通过时，P05记为“**一致，并获同体系多角度支持**”。该判定不把source-defined端点等同标准相互作用能，也不宣称跨分子、跨方法的普遍符号定律。
