import sys  # 系统参数模块
import os  # 文件路径模块
import re  # 正则表达式模块
import hashlib  # MD5哈希模块
import jieba  # 中文分词模块


class FileHandler:  # 文件处理类

    @staticmethod  # 静态方法装饰器
    def read_file(file_path: str) -> str:  # 读文件函数
        if not os.path.exists(file_path):  # 检查路径是否存在
            raise FileNotFoundError(f"文件不存在: {file_path}")  # 不存在则抛异常
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:  # utf-8只读打开
            return f.read()  # 读取全文并返回

    @staticmethod  # 静态方法装饰器
    def write_file(file_path: str, content: str) -> None:  # 写文件函数
        dir_path = os.path.dirname(file_path)  # 提取上级目录
        if dir_path and not os.path.exists(dir_path):  # 若目录不存在
            os.makedirs(dir_path, exist_ok=True)  # 递归创建目录
        with open(file_path, "w", encoding="utf-8") as f:  # 覆盖写入打开
            f.write(content)  # 写入文本内容


class SimHashCheck:  # 查重计算类

    def __init__(self, bit_num: int = 64):  # 构造初始化
        self.bit_num = bit_num  # 设指纹为64位

    def filter_text(self, text: str) -> str:  # 文本过滤函数
        pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9]")  # 仅保留汉字英数正则
        return pattern.sub("", text)  # 清除标点与空白字符

    def get_token_hash(self, token: str) -> int:  # 单词哈希函数
        md5_hex = hashlib.md5(token.encode("utf-8")).hexdigest()[:16]  # 计算MD5取前16位
        return int(md5_hex, 16)  # 转换为64位整数

    def calculate_simhash(self, text: str) -> int:  # 计算SimHash指纹
        clean_text = self.filter_text(text)  # 正则清洗标点
        if not clean_text:  # 判空处理
            return 0  # 空文本直接返0

        tokens = jieba.lcut(clean_text)  # 结巴切分词语
        if not tokens:  # 切词为空判定
            return 0  # 返回特征值0

        v = [0] * self.bit_num  # 建立64维零向量

        freq_dict = {}  # 词频统计字典
        for token in tokens:  # 遍历全部词语
            freq_dict[token] = freq_dict.get(token, 0) + 1  # 词频累加计数

        for token, weight in freq_dict.items():  # 遍历加权计算
            token_hash = self.get_token_hash(token)  # 获取词哈希值
            for i in range(self.bit_num):  # 遍历64个二进制位
                if token_hash & (1 << i):  # 判断第i位是否为1
                    v[i] += weight  # 为1加权重
                else:  # 判断第i位为0
                    v[i] -= weight  # 为0减权重

        fingerprint = 0  # 初始化最终指纹
        for i in range(self.bit_num):  # 遍历向量降维
            if v[i] > 0:  # 权重和大于0
                fingerprint |= (1 << i)  # 当前位置1

        return fingerprint  # 返回64位特征指纹

    def get_hamming_distance(self, hash1: int, hash2: int) -> int:  # 算海明距离
        diff = hash1 ^ hash2  # 异或获取差异位
        distance = 0  # 初始化距离计数器
        while diff:  # 统计1的个数
            diff &= (diff - 1)  # 抹去最低位1
            distance += 1  # 累加差异数量
        return distance  # 返回相异位数

    def compute_similarity(self, text1: str, text2: str) -> float:  # 相似度接口
        clean_text1 = self.filter_text(text1)  # 清洗文本1
        clean_text2 = self.filter_text(text2)  # 清洗文本2

        if not clean_text1 and not clean_text2:  # 双方皆空
            return 1.00  # 视作完全一致
        if not clean_text1 or not clean_text2:  # 单方为空
            return 0.00  # 视作完全无关
        if clean_text1 == clean_text2:  # 文本字面完全相同
            return 1.00  # 判定相似度100%

        hash1 = self.calculate_simhash(text1)  # 文本1指纹
        hash2 = self.calculate_simhash(text2)  # 文本2指纹

        distance = self.get_hamming_distance(hash1, hash2)  # 求海明距离
        similarity = 1.0 - (distance / self.bit_num)  # 映射为相似比率
        return max(0.00, min(1.00, similarity))  # 规整到0与1范围


def main():  # 主程序入口
    if len(sys.argv) != 4:  # 校验入参个数
        print("Usage: python main.py <orig> <copy> <ans>")  # 输出用法提示
        sys.exit(1)  # 退出进程

    orig_path = sys.argv[1]  # 获取原文路径
    plagiarized_path = sys.argv[2]  # 获取抄袭版路径
    ans_path = sys.argv[3]  # 获取输出路径

    try:  # 异常保护块
        orig_text = FileHandler.read_file(orig_path)  # 读取原文
        plagiarized_text = FileHandler.read_file(plagiarized_path)  # 读取抄袭文

        checker = SimHashCheck(bit_num=64)  # 实例化查重器
        similarity = checker.compute_similarity(orig_text, plagiarized_text)  # 计算相似度

        result_str = f"{similarity:.2f}"  # 保留两位小数
        FileHandler.write_file(ans_path, result_str)  # 写入目标文件
        print(f"查重结果: {result_str}")  # 控制台打印

    except Exception as err:  # 捕获运行时错误
        print(f"运行失败: {err}")  # 打印错误提示
        sys.exit(1)  # 异常安全退出


if __name__ == "__main__":  # 判断主模块运行
    main()  # 执行主函数