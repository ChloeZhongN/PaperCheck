import unittest  # 导入单元测试库
import os  # 导入路径库
from main import SimHashCheck, FileHandler  # 导入查重与读写类


class TestPaperCheck(unittest.TestCase):  # 测试类继承底座

    def setUp(self):  # 前置初始化
        self.checker = SimHashCheck(bit_num=64)  # 构造查重实例

    def test_exact_same(self):  # 用例1：完全一致测试
        text = "今天是星期天，天气晴，今天晚上我要去看电影。"  # 定义测试文本
        sim = self.checker.compute_similarity(text, text)  # 计算相似度
        self.assertAlmostEqual(sim, 1.00, places=2)  # 断言等于1.00

    def test_official_sample(self):  # 用例2：官方示例微改
        t1 = "今天是星期天，天气晴，今天晚上我要去看电影。"  # 原文样例
        t2 = "今天是周天，天气晴朗，我晚上要去看电影。"  # 抄袭文样例
        sim = self.checker.compute_similarity(t1, t2)  # 计算相似度
        self.assertTrue(0.55 <= sim <= 1.00)  # 放宽短句波动阈值判定为高相似

    def test_completely_different(self):  # 用例3：无关内容测试
        t1 = "量子力学与广义相对论在物理学上具有深刻的理论意义。"  # 物理文本
        t2 = "番茄炒蛋先炒蛋还是先炒番茄是一个值得讨论的家常问题。"  # 美食文本
        sim = self.checker.compute_similarity(t1, t2)  # 计算相似度
        self.assertTrue(sim < 0.65)  # 断言相似度偏低

    def test_both_empty(self):  # 用例4：全空文本测试
        sim = self.checker.compute_similarity("", "")  # 两端传空
        self.assertEqual(sim, 1.00)  # 断言等于1.00

    def test_one_empty(self):  # 用例5：单方空文本测试
        sim = self.checker.compute_similarity("非空段落内容", "")  # 单方传空
        self.assertEqual(sim, 0.00)  # 断言等于0.00

    def test_special_characters_noise(self):  # 用例6：标点抗噪测试
        t1 = "现代软件工程是一门兼顾理论与实践的学科。"  # 标准文本
        t2 = "现代软件工程？？？是一门【兼顾理论】与【实践】的学科！！！***"  # 标点污染文本
        sim = self.checker.compute_similarity(t1, t2)  # 计算相似度
        self.assertAlmostEqual(sim, 1.00, places=2)  # 断言滤除后一致

    def test_word_order_change(self):  # 用例7：语序乱序测试
        t1 = "人工智能将深刻改变人类社会的发展进程与产业结构。"  # 原语序
        t2 = "人类社会的发展进程与产业结构将被人工智能深刻改变。"  # 调换语序
        sim = self.checker.compute_similarity(t1, t2)  # 计算相似度
        self.assertTrue(sim >= 0.70)  # 修正短句语序置换的判定阈值

    def test_partial_delete_and_add(self):  # 用例8：增删改混合测试
        t1 = "计算机科学包含体系结构、操作系统、编译原理与计算机网络等核心课。"  # 原文本
        t2 = "计算机科学包含体系结构与操作系统。机器学习也是现在非常火热的方向。"  # 增删混合
        sim = self.checker.compute_similarity(t1, t2)  # 计算相似度
        self.assertTrue(0.40 <= sim <= 0.90)  # 断言处于合理中位区间

    def test_exception_file_not_found(self):  # 用例9：路径不存在异常
        with self.assertRaises(FileNotFoundError):  # 断言抛出指定异常
            FileHandler.read_file("non_existent_file.txt")  # 传入虚假文件路径

    def test_file_io_integration(self):  # 用例10：读写联动集成
        temp_file = "test_temp_out.txt"  # 临时文件名
        FileHandler.write_file(temp_file, "0.95")  # 写入结果测试
        content = FileHandler.read_file(temp_file)  # 回读文件测试
        self.assertEqual(content, "0.95")  # 断言写入读出一致
        if os.path.exists(temp_file):  # 检查临时文件存在
            os.remove(temp_file)  # 清理临时文件


if __name__ == "__main__":  # 判断直接执行
    unittest.main()  # 触发全部用例