Extraction of tuple (facet, comment) from user generated comments on Taobao.

本项目主要针对淘宝评论进行开放域信息抽取。

首先根据词性序列模式抽取出<名词、动词>对，之后采用矩阵分解或双聚类方法抽取出评论中产品的主要维度以及相关描述。

为了对产品特征和用户需求进行区分，同时加入了时态的判断，即判断用户体验是发生在使用产品之前（用户需求）或之后（产品特征）。
