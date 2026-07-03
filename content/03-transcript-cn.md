# 当一百万辆车同时回家

<!--
Chinese edition of the storybook transcript. Parsed by render/build.py --lang cn
into render/storybook-cn.html and output/storybook-cn.pdf.

SYNC RULE: this file is the Chinese counterpart of content/02-transcript.md (the
English source of truth). Any content edit to the English transcript MUST be
mirrored here, and vice versa. This edition is NOT a sentence-by-sentence
translation: it retells the same content in natural, idiomatic Chinese. When
syncing, carry over the meaning and the numbers, then write real Chinese.
Spread numbering, types, and image briefs are shared; images are the same files.

Naming rule: the protagonist is introduced once as 胡平凡 (Pingfan Hu), and is
called 平凡 afterwards. The advisor is introduced once with his full name, John
Paul "JP" Helveston, and is called JP afterwards (that is what most people call
him). All other people keep their English names (Alan, Brian, Eric, Kate,
Matthew, Bogdan). Technical terms are given in Chinese with the
English term (and abbreviation) in parentheses on first use.

Register: same as the English edition. This is a PhD-level storybook for
researchers, professors, and PhD students and graduates. Simplify the content,
never the reader. Natural spoken-written Chinese, no translationese, no European
sentence skeletons. One idea per spread. No em dashes.

Format rules (keep them strict so the parser stays happy):
- Each spread starts with a header line: `## NN | type`  (type = title | standard | backcover)
- Prose paragraphs follow, separated by blank lines. Inline **bold** and *italic* are allowed.
- The illustration brief sits in a fenced block (kept in English, shared with the
  English edition):
      ::: image
      one or more lines describing the picture
      :::
-->

## 01 | title
**当一百万辆车同时回家**

*一个关于智能充电的故事*

胡平凡 (Pingfan Hu) 的博士研究：电动车、电网，和一路做出来的开源工具。

::: image
Cover art. A quiet evening street, warm light, many electric cars turning in toward home. Painterly Ghibli style, inviting.
:::

## 02 | standard
这是胡平凡 (Pingfan Hu)。

读博这几年，平凡一直在研究纯电动汽车 (Battery Electric Vehicle, BEV)。核心问题看起来很简单：这些车会在什么时候充电？充电的时间点，又会给电网带来什么？

为了回答这个问题，平凡做了三项环环相扣的研究：第一项关于人，第二项关于电网和经济账，第三项关于做研究用的工具本身。

写成的博士论文很厚，公式很多，大多数人不会去读。所以他做了这本小书，把同样的研究用大白话再讲一遍。

::: image
Portrait moment of Pingfan at a desk piled with papers and a laptop, looking up with a friendly half-smile. (Pingfan; see characters/cartoon/pingfan-hu.png.)
:::

## 03 | standard
平凡本来没打算读博士。

有一天，John Paul “JP” Helveston 教授主动发来邮件。他刚拿到斯隆基金会 (Alfred P. Sloan Foundation) 的项目，研究电动车的智能充电，觉得平凡的工程和数据科学背景很合适。这事不太常见：一般是学生四处联系导师，很少有导师反过来找学生。

两人第一次见面，原定聊一个小时，结果聊了三个小时，谁都没想到。聊完，一份研究计划的雏形已经出来了：车主愿不愿意把充电交给别人管？他们的参与对电网值多少钱？做这些研究，又需要什么工具？

这三个问题，后来就成了这篇博士论文。

::: image
Pingfan and John talking across a small cafe table covered in notes, both leaning in, deep in conversation. (Pingfan: characters/cartoon/pingfan-hu.png; John: characters/cartoon/john-helveston.png.)
:::

## 04 | standard
问题的关键，在于什么时候充。

电动车能减少交通排放，但好处大不大，要看充电的时机。多数车主傍晚到家就插枪，充电负荷不偏不倚，正好压在**晚高峰**上，那正是家家户户用电最多的时候。要扛住这个叠加的高峰，电网得开动最贵的机组，长远还得扩建平时闲置的容量。

**智能充电**是另一条路：把充电挪到深夜。那时用电少，电网有的是余量。

行不行得通，要回答三个问题：车主愿意参加吗，开什么条件？参加了能削掉多少高峰，要花多少钱？还有，要弄清这些，得先有什么样的研究工具？

::: image
A row of suburban houses at 6 PM, many cars plugging into driveway chargers at once, warm-lit windows, utility lines and a street transformer carrying the heavy evening load.
:::

## 05 | standard
论文从第一个问题讲起：人愿不愿意。

智能充电的前提，是车主肯交出一部分控制权。研究一考察了电力公司实际在推的两类项目。一类叫**供电商托管充电** (Supplier-Managed Charging, SMC)：什么时候充，电力公司说了算，但保证到点有电。另一类叫**车网互动** (Vehicle-to-Grid, V2G)：电网缺电时，车还得反过来送电回去，相当于一块会跑的储能电池。

两类项目对车主的要求不一样。SMC 只要你耐心等；V2G 却要动用你的电池，还得搭上电池损耗。可以想见，车主对这两件事的开价不会相同。

::: image
Split scene. Left: a car charging calmly overnight from a home wall charger (Supplier-Managed Charging). Right: the same car connected by a thick cable to a home energy unit, power able to flow back too (Vehicle-to-Grid). Real equipment, no glowing arrows.
:::

## 06 | standard
问什么重要，问谁同样重要。

以往的研究大多去问普通车主，他们中很多人从没给电动车充过电，有些人就算想参加也没条件。研究一换了个思路：找来 **1,356 位真正开电动车的美国车主**，2024 年通过社交媒体定向广告和调查公司招募。

质量靠一道筛选题把关：受访者要在一张覆盖三十年、共 1,748 款车型的列表里选出自己的车，其中纯电车型只有 77 款，占 4.4%。不是真车主，基本蒙不对。

这些人才真正懂充电是怎么回事。其中 682 人还答完了 V2G 部分。

::: image
A friendly crowd of varied real car owners standing proudly beside their EVs in a sunny parking lot. A small Facebook logo and Instagram logo hover in the upper corner of the sky, a nod to how the participants were recruited.
:::

## 07 | standard
“灵活性对你值多少钱？”这种问题没法直接问，谁心里也没有这么个数。

研究一用的是**离散选择实验** (discrete choice experiment)：给受访者看一对对虚拟方案，每个方案由几项具体条件组成，比如一次性奖励给多少、每月给多少钱、每月能手动豁免几次、电量保底是多少。受访者在方案 A、方案 B 和“都不要”之间选一个，SMC 选六轮，V2G 再选六轮。

让人在随机搭配的条件里一次次做选择，**logit 模型**就能算出，每项条件在多大程度上左右着人们的参与意愿。选择，比提问更诚实。

::: image
A survey respondent at a kitchen table looking at a tablet showing two option columns (each with simple attribute rows) and a "not interested" option, hand hovering to choose. A real on-screen choice question.
:::

## 08 | standard
这项工作从头到尾都是合作的产物。

团队来自好几所大学：加州大学戴维斯分校的 Alan Jenn，加州大学尔湾分校的 Brian Tarroja、Kate Forrest 和 Matthew Dean，还有罗切斯特理工学院的 Eric Hittinger，他后来也进了平凡的论文委员会。导师 JP 是项目负责人，始终替团队把着方向。

日常研究由平凡牵头，但这些问题横跨车、电网、调查方法三个领域，谁也不可能样样精通。好在，这个团队加起来可以。

::: image
A warm group scene: Pingfan in the middle with John beside him, and the wider team around a table of charts. (Use portraits: pingfan-hu, john-helveston, alan-jenn, brian-tarroja, eric-hittinger, kate-forrest, matthew-dean.)
:::

## 09 | standard
先看托管充电，结果让人欣慰，也有点出乎意料。

车主没那么在乎钱，更在乎**灵活性**：早上电量有保底，临时有事的晚上能自己说了算。“保底电量”的影响远大于“起充电量”。说白了，大家要的是踏实的续航，过程怎么管，倒不太计较。

只给足灵活性、一分钱不掏，预测参与率就能到 **50%** 以上。再给点钱当然更好，而且按月给最划算：每月两三美元的效果，顶得上一次性给 65 美元，差不多二十比一。

充电可以交出去，但得保证别把人撂在半路。

::: image
A reassured owner asleep while, through the window, the car charges in the driveway with a small steady green charger light. No glowing gauges.
:::

## 10 | standard
车网互动是另一回事。

让电从自家电池往外流，这个请求大得多，车主的开价也直接：V2G 的参与意愿对钱远比 SMC 敏感。按次给钱、给得够多，参与率就一路上扬；每次放电给 20 美元、每月四次，模型预测能有 **82%** 的人参加。

对项目设计，这个启示很清楚：SMC 适合做成简单的包月订阅，给点小钱，把保障做足；V2G 更像按单结算的电网服务市场，按次付费最合适。

为了让结论用得上，团队还上线了一个**参与率模拟器**：一个网页小工具，电力公司和政策制定者随便调参数，马上能看到预测的参与率。

::: image
Night driveway: the car charges from its home charger while the owner stands on the porch, checking a phone app that shows a simple savings bar chart and a dollar amount. No floating coins or energy streams.
:::

## 11 | standard
不过，嘴上说愿意，不等于电网真受益。

研究一搞清了车主参加的条件；研究二接着问两个问题，电力公司干不干，就看这两个答案：第一，托管充电到底能把晚高峰削下去多少？第二，扣掉发给车主的激励，这笔账还划算吗？

经济账是重头。参加的每一户都要给钱，削峰带来的好处，必须对得起这份总开销。

::: image
Pingfan at his desk, chin on hand, studying his laptop and a printout showing two real charts: a flattened peak curve and a steeply rising cost curve, weighing benefit against cost. (Pingfan: characters/cartoon/pingfan-hu.png.)
:::

## 12 | standard
研究二的做法，是用实打实的数据把两头接起来，而不是拍脑袋假设。

研究一的结果先整理成一条**参与率曲线**：月度激励给到多少，就有多大比例的车主参加。再把这条曲线接进一个覆盖全年、每 15 分钟一步的电网仿真：一万辆虚拟汽车按全国家庭出行调查 (NHTS) 的真实出行规律开车、停车、充电，再按人口普查的家庭数，放大成整个地区的车队。

比较选在两个脾气完全不同的电网上：加州的 **CAISO**，光伏多，后半夜低谷又深又稳；纽约的 **NYISO**，曲线平，靠水电，冬天负荷最高。

::: image
A researcher's workspace: a printed US map with sunny California and snowy New York marked, and a laptop showing a concave enrollment-versus-payment curve.
:::

## 13 | standard
加州的电网把道理演得最清楚。

它的日**净负荷** (net load) 曲线，午后被光伏压得一路下沉，太阳一落又猛地窜高。工程师管它叫**鸭子曲线** (duck curve)，看一眼形状就知道为什么。晚高峰过后的低谷又深又稳，正好装得下挪过来的充电。

把充电从傍晚挪进低谷之后，参与率拉满时，CAISO 的晚高峰在普通日子平均削掉 3.7 吉瓦，合 12.1%；赶上最合适的一天，能削 **5.6 吉瓦**。盘子更小、曲线更平的 NYISO，平均削 1.6 吉瓦。

物理上没问题。剩下的是钱的问题。

::: image
Pingfan looking up at a large framed print of a hand-painted daily load curve shaped unmistakably like a duck (low sagging midday belly, steep neck at sunset, tall rounded evening head), with a second soft line flattening the head and filling the belly. A modern city at dusk through the window. (Pingfan: characters/cartoon/pingfan-ref.png.)
:::

## 14 | standard
钱的麻烦，出在一个绕不开的事实上：激励是一口价，每户参与者拿的都一样。

参与率曲线是弯的：分文不给，也有大约 **30%** 的车主愿意参加；每月 20 美元，能拉到 **60%** 左右；可要让人人都参加，得每月掏 **85 美元**，而且每户都得给。想拉来下一位，就得给所有人一起涨价。于是总成本越滚越快，新增的削峰效果却越来越小。

经济学管这叫**边际收益递减**。在这类项目里，递减得格外狠。

::: image
A modern room where a steeply rising cost curve is drawn on a whiteboard, low and flat on the left then climbing sharply on the right; a researcher gestures at the steep part. No floating coins.
:::

## 15 | standard
所以，务实的答案是适可而止。

参与率落在 **30% 到 50%** 之间时，花小头的钱，就能拿到大头的削峰效果。再往上，每多削一吉瓦都贵得离谱。

更要命的是，过了某个坎，拉人越多反而越糟：太多充电挤进同一个深夜时段，低谷里反倒隆起一座新的高峰。在 CAISO，大约 **15%** 的日子会出现这种情况。山没被削平，只是搬了个家。

参与率适度、有的放矢，才是性价比最高的运行点。人越多越好，恰恰是误区。

::: image
The overnight valley with too many cars crowding in, forming a new small peak at midnight; a wry mood.
:::

## 16 | standard
这笔账，还得看地方、看季节。

CAISO 的成本效益一年四季都稳，因为光伏让晚高峰和深夜低谷之间始终隔着足够大的落差。NYISO 一到冬天就吃力：取暖用电把后半夜撑得满满当当，项目赖以运转的低谷被压窄了。

教训很直接：智能充电不是一件到哪儿都能用的标准品，而是一张要按当地净负荷的形状来调的时刻表。

::: image
Two nighttime scenes side by side. California: a wide-open valley with room for cars. New York winter: a valley already crowded by glowing heated homes.
:::

## 17 | standard
研究三的起因，是研究一里攒下的一肚子火。

要对 1,356 人做一场严谨的实验，先得有趁手的问卷软件。可市面上的选项个个差点意思：商业平台功能全，但又贵又封闭；免费工具上手快，但处处受限。更根本的是，几乎没有平台像对待代码和论文那样对待问卷：可以管版本、可以分享、可以审查、几年后还能一字不差地复现。

对讲究可复现的研究来说，这不是不方便，而是方法论上的一个窟窿。团队决定自己动手补上。

::: image
Pingfan frowning at his laptop, whose screen shows a clunky survey website blocked by a paywall (a subscription panel and a locked-feature padlock icon in the real UI). No floating padlock or lightbulb. (Pingfan: characters/cartoon/pingfan-hu.png.)
:::

## 18 | standard
成果叫 **surveydown**，一个用 R 写的开源问卷平台。

用它做问卷，不用再在网页上点来点去，直接用纯文本写：markdown 加 R 代码，surveydown 负责把它变成能直接上线的网页问卷。背后是三件成熟的开源工具：**Quarto** 管文档，**Shiny** 管交互，**PostgreSQL** 管数据。

实验室里工程管理与系统工程系的本科生 Bogdan Bunea 搭起了安全存储答卷的数据库层。整个平台免费开源，以 MIT 许可证发布在 CRAN 上。

::: image
A simple text file on one side turning into a clean, live web survey on the other; Pingfan and Bogdan beside it. (Pingfan: characters/cartoon/pingfan-hu.png; Bogdan: characters/cartoon/bogdan-bunea.png.)
:::

## 19 | standard
用纯文本写问卷，听着不起眼，平台的三大长处全靠它。

一是**可复现** (reproducibility)：问卷就是几个文本文件，可以进版本库、可以共享、可以审查，几年后照样一字不差地跑起来。在专有平台上点出来的问卷，做不到。

二是**可编程**：问卷运行时跑的是真代码，想按条件显示、想跳题、想随机化、想做完全自定义的实验设计，都行。研究一的选择实验就是这么做出来的。

三是**数据在自己手里**：问卷程序、部署环境、答卷数据库三者分离，数据完全归研究者自己，不用向平台租回自己的数据。

::: image
Over-the-shoulder view of a laptop: the screen shows a version-control history with neat branching lines, a preview of the rendered survey, and a small database-cylinder icon for safely stored data. A real desk with a plant and a mug.
:::

## 20 | standard
surveydown 后来长到了实验室外面。

它在 CRAN 上被下载了数千次，用户早就不限于交通领域：公共卫生、经济学、教育学、公共政策，都有人在用。社区贡献者不断添砖加瓦，包括六种语言的翻译；配套的图形界面工具 **sdstudio** 也在开发中，目标是不牺牲可复现性，还能让不写代码的人用起来。

一个为了应急做出来的小工具，成了大家共用的研究基础设施。

::: image
A world map on a screen with small clusters of real researchers in a lab, an office, and a classroom, all using the same survey tool on laptops; marker dots across many countries suggest a worldwide, multi-language community.
:::

## 21 | standard
把三项研究摆在一起看，其实是一个完整的论证。

研究一从 1,356 位车主那里，量出了大家愿意参加托管充电的条件；研究二把这些条件带进电网仿真，得出一条很实际的准则：参与率要适度，方案要按当地电网来调，好处多、花钱少的区间就在那里；研究三把做这些测量要用的工具造了出来，开源留给了所有人。

消费者行为、电网经济、研究工具：每一项研究回答的，恰好是前一项留下的问题。

::: image
Three framed prints side by side on a study wall, joined by a single shelf: a crowd (people), a grid load curve (system), a survey tool on a laptop (method). No glowing panels or golden thread.
:::

## 22 | standard
论文也把自己还说不准的地方，写得明明白白。

问卷里的表态往往比现实慷慨：已经落地的试点项目，参与率只有 **4% 到 10%**，离模型算出的最优区间还很远，用真实项目的数据来校准，是最清楚的下一步。仿真只覆盖了有车库的独栋住宅，公寓、办公楼和公共充电还没碰。V2G 也还欠一笔 SMC 已经算过的经济账。至于 sdstudio，得再打磨一阵，surveydown 才能真正服务不写代码的研究者。

这里的每一条，都够再做一个课题。研究就是这样接力下去的。

::: image
A calm, hopeful near-future town in the evening, electric cars charging at staggered times along ordinary streets, the grid steady and bright; the work continuing.
:::

## 23 | standard
博士学位给人本事，平凡带走的是一整套：选择建模、电网仿真、R 语言数据科学，还有做研究软件的手艺。

但更大的收获是一种心态，四年里从 JP 身上学来的：对自己的工作负责到底；难题面前不轻易松手；看每个项目，都把它放回更大的系统里，看清它从哪儿来、到哪儿去。

这一切不是一个人做成的。委员会和合作者磨利了每一项研究；Helveston 实验室让这几年过得充实又开心；斯隆基金会资助了研究，还为意外长出来的软件成果喝彩；父母、朋友，尤其是妻子，一路把他撑到了今天。

谢谢你们，每一位。

::: image
A warm ensemble scene suggesting mentors, family, and lab mates gathered around the work; Pingfan among them. (Pingfan: characters/cartoon/pingfan-hu.png; John: characters/cartoon/john-helveston.png.)
:::

## 24 | backcover
一百万辆车同时回家的故事，讲到这里。四年的研究，回答的其实就是一件事：它们该在什么时候充电。

论文全文题为：

*Sustainable Transportation, Sustainable Research: Consumer Adoption and Grid Peak-Shaving of Battery Electric Vehicle Smart Charging, Inspiring the surveydown Open-Source Survey Platform*

方法、模型和结果都在里面，欢迎你翻开读读。

*胡平凡 (Pingfan Hu)，博士*

*乔治·华盛顿大学，2026*

::: image
The dissertation re-imagined as one cohesive hand-painted top-down desk scene: the thick bound volume tilted about 30 degrees clockwise with the simplified English title page (title, By Pingfan Hu, PhD degree line, The George Washington University, 2026, and a small Tesla-like EV at a charger), a fountain pen and a cup of coffee beside it. Final art produced via Gemini image-to-image repaint; shared with the English edition.
:::
