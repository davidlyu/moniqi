class Tools:
    @staticmethod
    def lookup(table, x):
        """
        查表函数，table是二维列表，
        在第一列查找x，返回第二列对应的值，
        如果没有精确的值，则返回相邻两个值得插值。
        :param table: 二维表，第一列降序排列
        :param x: 要查询的值
        :return: 在第二列中与第一列中x对应的值。
        """
        if x > table[0][0]:
            return None
        elif x < table[-1][0]:
            return table[-1][1]
        else:
            i = 0
            while table[i][0] > x:
                i += 1

            if table[i][0] == x:
                return table[i][1]
            else:
                return (table[i][1] - table[i - 1][1]) / (table[i][0] - table[i - 1][0]) * \
                       (x - table[i - 1][0]) + table[i - 1][1]
