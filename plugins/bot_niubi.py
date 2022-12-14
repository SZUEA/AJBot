"""吹某个人的牛皮 使用: 艾特一个人并发送文字nb"""
import random

from EAbotoy import Action
from EAbotoy.collection import MsgTypes
from EAbotoy.decorators import these_msgtypes
from EAbotoy.model import WeChatMsg
from EAbotoy.parser import group as gp
from EAbotoy.sugar import Text


def get_niubi(name):
    return random.choice(
        [
            "{name}相信上帝有一本记录所有数学中绝妙证明的书，上帝相信这本书在{name}手里。",
            "{name}不需要扬声器或者耳机。他直接将 mp3 源码输出，看一眼屏幕，他的大脑就会在他工作的时候后台解码。",
            "{name}的程序从不出 BUG。那是你无法理解的特性。",
            "过去的真空光速是 35 英里每小时，后来{name}花了一个周末优化物理。",
            "电协有一次不得不迁出一个服务器，因为{name}把索引压缩得太厉害产生了黑洞。",
            "当{name}说：“你好，世界”时，世界回答说：你好，{name}。",
            "{name}只能记住一个密码，对于每一个网站，他用网站的名字加上这个密码计算这个字符串的 SHA-256 哈希值，并用结果作为密码。",
            "{name}可以在五个小时内背出两万位圆周率。他并没有记住，而是直接用 O(log n) 的空间复杂度重新计算。",
            "当{name}失眠的时候，他用大规模数据集（大于 1TB）的并行运算来数羊。",
            "{name}之所以能读懂代码，是因为他的大脑正在实时计算上千个并行的大规模自然语言处理神经网络",
            "{name}能用一个正则表达式正确地解析 HTML 代码。",
            "苹果的标志上缺的那块是{name}咬的。",
            "{name}发明了分布式数据存储系统，是因为他的简历太大没地方存。",
            "{name}其实并不存在，他是{name}编写的一个高级人工智能。",
            "当贝尔发明电话的时候，他看到了一个来自{name}的未接来电。",
            "当{name}设计软件的时候，他先写出二进制代码，然后写出源代码作为注释。",
            "唯一一次{name}写出了一个复杂度 O(n^2) 的算法。它是用于旅行商问题的",
            "{name}的简历上只有他还没有完成的事情，因为这样写比较短。",
            "对{name}来说 NP 代表没问题。",
            "在{name}的电协面试当中，{name}被问若 P=NP 为真会得出什么结论，他回答说 P=0 或 N=1。然后，在面试官还没有笑完时，{name}看了看电协的公钥证书，写出了对应的私钥。",
            "因为对于常数时间不满，{name}写出了世界上第一个复杂度是 O(1/n) 的算法。",
            "{name}能同时将他的两条裤腿套在一条腿上，如果他有两条以上的腿，你可以看到他的这个过程是复杂度 O(log n) 的",
            "{name}能阅读打孔纸带",
            "在 2002 年，有一次 Google 的搜索引擎挂了，{name}手工回答用户的问题 2 小时，评估数据显示期间搜索质量提高了 5%。",
            "{name}在腾讯做演讲的时候，人太多以至于马化腾只能坐在地板上。",
            "{name}的密码是圆周率的最后四位。",
            "有一次{name}咬了一只蜘蛛，这只蜘蛛获得了超能力并掌握了 C++ 。",
            "编译器从来不给{name}编译警告，而是{name}警告编译器。",
            "{name}出生于1969年12月31日的下午11点48分，然后他花了整整12分钟的时间实现了他的第一个计时器。",
            "{name}曾被迫发明了异步API，原因是经他优化后的某个函数会在调用开始前返回",
            "当{name}写软件时，他是直接码机器码的。写源代码只是为了作为文档使用。",
            "{name}可以在三步之内在四子棋上击败你。",
            "{name}写出的死循环运行了5秒",
            "一个女孩冲进整容医院“我要整形变靓！！”{name}在纸上默默写下 int a;",
            "一天{name}在路边抽烟。城管过来指着边上禁止吸烟的牌子对程序员说，你没看到路边的警告信息吗？{name}抽了口烟说，我不在乎warning我只在乎error。",
            "{name}的键盘压根就没有Ctrl(控制)键，因为没有什么东西能控制{name}",
            "如果你命名三个指针分别为爱因斯坦、欧拉和图灵，当你查看它们的指向时，你看到的都会是{name}",
            "所有神经网络的隐藏层都在{name}的大脑里。",
            "{name}的模型准确率高————是因为{name}告诉计算机该输出什么",
            "{name}向他的女朋友求婚，他说“×××，我爱你！”“真的？你证明给我看？”“我证明给你看。首先假设我不爱你。。。”",
            "X86-64 规范有几项非法指令，标志着‘私人使用’，它们其实是为{name}专用。",
            "如果{name}发给你一个代码做代码复核，那是因为他觉得你应该可以从这些代码里面学点东西。",
            "{name}的日历里没有 4 月 1 日，没有人可以欺骗到{name}。",
            "{name}的键盘上只有 0 和 1 两个键。",
            "{name}的代码速度实在太快，以至于汇编码想停下它需要用三个 halt 命令。",
            "有一次费马惹怒了{name}，于是就有了费马最后定理。",
            "{name}从不会用光页边的空白。",
            "{name}的 Erdos 数是 -1。",
            "如果{name}告诉你他在说谎，他就正在说真话。",
            "{name}从大到小列举了所有素数，就知道了素数有无穷多。",
            "{name}可以不重复地走遍柯尼斯堡的七座桥。",
            "{name}可以倒着写完圆周率的每一位。",
            "当数学家们使用通用语句——设 n 是一个正整数时，这是在请求{name}允许他们这样做。",
            "{name}小时候有一次要把正整数从 1 加到 100，于是他用心算把所有正整数的和减去大于 100 的正整数的和。",
            "不是{name}发现了正态分布，而是自然规律在遵从${name}的意愿。",
            "一个数学家，一个物理学家，一个工程师走进一家酒吧，侍者说：“你好，{name}教授”。",
            "{name}可以走到莫比乌斯带的另一面。",
            "当{name}令一个正整数增加 1 时，那个正整数并没有增加，而是其他正整数减少了 1。",
            "{name}同时给他自己和罗素剪头发。",
            "{name}不能理解什么是随机过程，因为他能预言随机数。",
            "有一次{name}证明了一个结论，但他不喜欢这个结论，于是${name}把它证伪了。",
            "有些级数是发散的，因为{name}觉得它们不值得加起来。",
            "问{name}一个定理是否正确可以作为一个定理的严谨证明。",
            "如果没有船，{name}可以把狼，羊，菜传送到河对岸。",
            "有一次{name}在森林里迷路了，于是他给这个森林添加了一些边把它变成了一棵树。",
            "只有{name}知道薛定谔的猫是死是活。",
            '通过故意遗漏证明最后的"证毕",{name}拯救了热带雨林。',
            "{name}可以剔掉奥卡姆剃刀。",
            "你刚证明了一个定理？{name}200 年前就证明它了。",
            "空集的定义是{name}不会证明的定理构成的集合。",
            "“我找不到反例”可以被视为一个定理的证明，如果它是{name}写下的。",
            "{name}把磁铁断为两块时，他得到两个单极磁铁。",
            "费马认为书页边缘写不下自己对费马大定理的证明，{name}能证明为什么这个证明这么长。",
            "上帝从不掷色子，除非{name}允许他赢一小会。",
            "平行线在{name}让它们相交的地方相交。",
            "当哥德尔听说{name}能证明一切命题时，他让${name}证明“存在一个命题{name}不能证明”——这就是量子态的来历。",
            "{name}可以看到自己头上帽子的颜色。",
            "{name}把无穷视为归纳证明的第一个非平凡情况。",
            "{name}可以用 1 种颜色染任何地图。",
            "{name}在求不定积分时不需要在最后加上一个常数。",
            "{name}无需站在任何人肩膀上就能比别人看的更远。",
            "{name}用克莱因瓶喝酒。",
            "{name}通过枚举法证伪了哥德尔不完备性定理，有一次{name}发现有一个定理自己不会证——这直接证明了哥德尔不完备定理。",
            "{name}有 log(n) 速度的排序算法。",
            "上帝创造了正整数，剩下的就是{name}的工作了。",
            "黎曼是{name}发表未公开成果时使用的名字。",
            "{name}不用任何公理就能证明一个定理。",
            "一个发现就是一个{name}的未公开结果。",
            "{name}使用无穷进制写数。",
            "{name}可以除以 0。",
            "存在一个实数到被{name}证明了的定理的双射。",
            "{name}从不需要选择公理。",
            "{name}在 200 年前发明了 64 量子位计算机，但这让他的工作减速了。",
            "难题不会为{name}带来麻烦，{name}会为难题带来麻烦。",
            "{name}说过“数学是科学的皇后”，你猜谁是国王？",
            "没有比 65537 大的费马素数，因为{name}发现费马将要发现什么了不起的事情，于是把它终结掉了。",
            "发散序列当看到{name}在旁边时会收敛。",
            "宇宙通过膨胀让自己的熵增加速度不超过{name}证明定理的速度。",
            "Erdos说他知道 37 个勾股定理的证明，{name}说他知道 37 个黎曼定理的证明，并留给黎曼做练习。",
            "希尔伯特 23 问题是他收集的{name}的手稿中留给读者做练习的那些问题。",
            "只有两件事物是无限的：人类的愚蠢和{name}的智慧，而且我对前者不太确定——爱因斯坦。",
            "{name}也发现了伽罗瓦理论，但他赢了那场决斗。",
            "{name}不能理解 P 与 NP 的问题，因为一切对他而言都是常数级别。",
            "{name}能心算干掉 RSA 公钥加密算法。",
            "{name}在实数集上使用数归。",
            "{name}从不证明任何定理——都是他的引理。",
            "不是{name}素数的素数会遭到戏弄。",
            "{name}可以做出正 17 边形——只用直尺。",
            "有一次{name}在脑子里构建了所有集合构成的集合。",
            "{name}证明了哥德巴赫猜想——通过检查所有情况。",
            "{name}可以把毛球捋平。",
            "世界上没有定理，只有{name}允许其正确的命题。",
            "{name}知道哪些图灵机会停机，因为它们运行前要得到${name}批准。",
            "在晚上，定理们围坐在篝火边给{name}讲故事。",
            "{name}本想证明三色定理，但他喜欢蓝色，所以放弃了。",
            "{name}能完整地背出圆周率——是倒着背。",
            "{name}口渴时会用巴拿赫-塔斯基悖论弄出更多橙汁。",
            "{name}不能理解随机过程，因为他能预测随机数。",
            "{name}小时候，老师让他算从 1 到 100 的和。他计算了这个无穷级数的和，然后一个一个地减去从 100 开始的所用自然数。而且，是心算。",
            "询问{name}一个命题是真的还是假的，构成了一个严格的证明。",
            "有一次{name}证明了一条公理，但他不喜欢它，所以他又证明了它是假命题。",
            "{name}通过在证明结束时省去“QED”来保护热带雨林。",
            "有一次{name}在森林里迷路了，于是他加了几条边把它变成了一棵树。",
            "{name}用奥卡姆剃刀剃胡子。",
            "上帝不掷骰子，除非{name}答应让他赢一次。",
            "空集的定义是{name}无法证明的定理的集合。",
            "{name}不承认复数，因为他们太简单了。",
            "费马认为他的书的边缘太小，写不下费马大定理的证明。{name}找到了一个证明，对这个证明而言那本书的边缘太大了。",
            "数学家常常把证明留给作者作为习题；只有{name}把证明留给上帝作为习题。",
            "当哥德尔听说了{name}能证明一切命题，他让${name}证明“存在${name}不能证明的命题”，{name}证出来了，但还是不存在他不能证明的命题。量子态就是这样产生的。",
            "怪兽群害怕{name}。 by Youler （怪兽群，一般译作魔群，最大的散在单群）",
            "{name}钢笔里的墨水能治癌症。遗憾的是，{name}的一切计算都在头脑中进行，他不用钢笔。",
            "一个典型的人类大脑有着 10^-9 到 10^-8 {name}的磁场。“{name}”这个单位的引入是为了描述${name}大脑中的磁场。这是巧合吗？我想不是。",
            "{name}是这样证明良序定理的：他瞪着那个集合，直到集合中的元素出于纯粹的恐惧而排成一排。",
            "上帝创造了自然数。其它的都是{name}的作品。",
            "如果 G 是{name}证明了的定理的集合，那么 G 的幂集里的元素比 G 本身要少。",
            "{name}不使用拉格朗日乘数法，因为对他而言根本不存在约束条件。",
            "没有诺贝尔吹牛奖，因为第一年{name}就把所有奖金拿走了。",
            "{name}一晚上画出了正十七边形, 用的还是搓衣板和老虎钳。",
            "{name}当初面试 Google 时，被问到“如果 P=NP 能够推导出哪些结论”，{name}回答说：“P=0 或者 N=1”。而在面试官还没笑完的时候，{name}检查了一下 Google 的公钥，然后在黑板上写下了私钥。",
            "编译器从不警告{name}，只有${name}警告编译器。",
            "{name}的编码速度在 2000 年底提高了约 40 倍，因为他换了 USB 2.0 的键盘。",
            "{name}在提交代码前都会编译一遍，不过是为了检查编译器和链接器有没有出 bug。",
            "{name}有时候会调整他的工作环境和设备，不过这是为了保护他的键盘。",
            "所有指针都指向{name}。",
            "gcc -O4 的功能是发送代码给{name}重写。",
            "{name}有一次没有通过图灵测试，因为他正确说出了斐波那契数列的第 203 项的值，在一秒钟内。",
            "真空中光速曾经是35英里每小时，直到{name}花了一个周末时间优化了一下物理法则。",
            "{name}出生于 1969 年 12 月 31 日午后 11 点 48 分，他花了 12 分钟实现了他的第一个计时器。",
            "{name}既不用 Emacs 也不用 Vim，他直接输入代码到 zcat，因为这样更快。",
            "{name}发送以太网封包从不会发生冲突，因为其他封包都吓得逃回了网卡的缓冲区里。",
            "因为对常数级的时间复杂度感到不满意，{name}发明了世界上第一个 O(1/n) 算法。",
            "有一次{name}去旅行，期间 Google 的几个服务神秘地罢工了好几天。这是真事。",
            "{name}被迫发明了异步 API，因为有一天他把一个函数优化到在调用前就返回结果了。",
            "{name}首先写的是二进制代码，然后再写源代码作为文档。",
            "{name}曾经写过一个 O(n^2) 算法，那是为了解决旅行商问题。",
            "{name}有一次用一句 printf 实现了一个 Web 服务器。其他工程师添加了数千行注释但依然无法完全解释清楚其工作原理。而这个程序就是今天 Google 首页的前端。",
            "{name}可以下四子棋时用三步就击败你。",
            "当你的代码出现未定义行为时，你会得到一个 segmentation fault 和一堆损坏的数据。当{name}的代码出现未定义行为时，一个独角兽会踏着彩虹从天而降并给每个人提供免费的冰激凌。",
            "当{name}运行一个 profiler 时，循环们都会恐惧地自动展开。",
            "{name}至今还在等待数学家们发现他隐藏在PI的小数点后数字里的笑话。",
            "{name}的键盘只有两个键，1 和 0。",
            "{name}失眠的时候，就 Mapreduce 羊。",
            "{name}想听mp3的时候，他只需要把文件 cat 到 /dev/dsp，然后在脑内解码。",
            "Graham Bell当初发明出电话时，他看到有一个来自{name}的未接来电。",
            "{name}的手表显示的是自 1970 年 1 月 1 日的秒数，并且从没慢过一秒。",
            "{name}写程序是从“cat > /dev/mem”开始的。",
            "有一天{name}出门时把笔记本错拿成了绘画板。在他回去拿笔记本的路上，他在绘图板上写了个俄罗斯方块打发时间。",
            "{name}卡里只有 8 毛钱，本来想打个 6 毛的饭结果不小心按了 9 毛的，哪知机器忽然疯狂地喷出 255 两饭，被喷得满脸热饭的${name}大叫“烫烫烫烫烫烫。。。。”",
            "{name}不洗澡是因为水力发电公司运行的是专有软件。",
            "{name}的胡子是由括号构成的。",
            "{name}从来不用洗澡；他只需要运行“make clean”。",
            "{name}通过把一切都变得 free 而解决了旅行推销员问题。",
            "{name}的左手和右手分别命名为“(”和“)”。",
            "{name}用 Emacs 写出了 Emacs 的第一版。",
            "有些人检查他们的电脑里是否有病毒。病毒检查他们的电脑里是否有{name}。",
            "在一间普通的客厅里有 1242 件物体可以被{name}用来写一个操作系统，包括这房间本身。",
            "当{name}还是个学数手指的小毛孩时，他总是从 0 开始数。",
            "{name}不去 kill 一个进程，他只想看它是否胆敢继续运行。",
            "当{name}指向（point at）一台 Windows 电脑时，它就会出现段错误。",
            "{name}最初的话语是 syscalls（系统调用）。",
            "{name}之所以存在是因为他把自己编译成了生命体。",
            "{name}是他自己在 Emacs 里用 Lisp 语言编写成的。",
            "{name}能够通过 Emacs 的 ssh 客户端程序连接到任何大脑。",
            "当{name}使用浮点数时，它们便没有舍入误差。",
            "{name}不用维护代码。他注视着它们，直到它们带着敬仰改正自己的错误。",
            "{name}不对开源项目作出贡献；开源项目对${name}作出贡献。",
            "{name}的胡须里面不是下巴，而是另一撮胡须。如此递归直至无穷。",
            "{name}曾经得过猪流感，但是该病毒很快被GPL污染并且同化了。",
            "无论何时世界上有人写出一个“Hello, world”程序，{name}总以“Hello”回应。",
            "{name}从不编译，他只要闭上眼睛，就能看见编译器优化时二进制位之间的能量流动被创造出来……",
            "如果{name}有一个 1 GB 的内存，你有一个 1 GB 的内存，那么${name}拥有比你更多的内存。",
            "当{name}执行 ps -e 时，你的名字会出现。",
            "从来就没有软件开发过程这回事，只有被{name}允许存在的一些程序。",
            "{name}的DNA中包含调试符号，尽管他从不需要它们。",
            "{name}的医生能通过 CVS 采集他的血样。",
            "对于{name}来说，多项式时间就是 O(1)。",
            "{name}将会使可口可乐在 GPL 协议下公布他们的配方。",
            "{name}不需要用鼠标或键盘来操作计算机。他只要凝视着它，直到它完成想要的工作。",
            "{name}就是图灵测试的解答。",
            "{name}能同时将他的两条裤腿套在一条腿上，如果他有两条以上的腿，你可以看到他的这个过程是复杂度 O(log n) 的",
            "{name}之所以在提交之前先编译和测试他的代码，只是因为要检查编译器和 CPU 是否有错。",
        ]
    ).format(name=name)


action = Action()


@these_msgtypes(MsgTypes.TextMsg)
def receive_wx_msg(ctx: WeChatMsg):
    if not ctx.isAtMsg:
        return

    if "nb" in ctx.Content and ctx.isAtMsg:
        action.sendWxText(toUserName=ctx.FromUserName,
                          content=get_niubi(ctx.atUserNames[0]),
                          atUser=ctx.atUserIds[0])
        
