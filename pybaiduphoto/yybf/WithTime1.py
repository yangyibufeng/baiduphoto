from datetime import datetime, date
import json
import os
import time
class WithTime1:

    def _parse_date_input(self,date_input):
        """解析日期输入为 date 对象

        Args:
            date_input: 支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串格式1: "2026:01:01" (只有日期)
                - 字符串格式2: "2026:01:01 20:33:12" (完整时间)
                - 字符串格式3: "2026-01-01" (ISO格式)

        Returns:
            date 对象
        """
        if isinstance(date_input, date) and not isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, str):
            # 尝试不同的格式
            for fmt in ["%Y:%m:%d %H:%M:%S", "%Y:%m:%d", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(date_input, fmt)
                    return dt.date()
                except ValueError:
                    continue
            raise ValueError(f"无法解析日期字符串: {date_input}")
        else:
            raise TypeError(f"不支持的日期类型: {type(date_input)}")


    def _get_item_date(self,item):
        """获取 item 的日期(只到天,不含时分秒)

        Args:
            item: OnlineItem 对象

        Returns:
            date 对象,如果没有 date_time 则返回 None
        """
        extra_info = item.info.get("extra_info", {})
        date_time_str = extra_info.get("date_time", None)
        if date_time_str:
            try:
                dt = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
                return dt.date()  # 只返回日期部分
            except ValueError:
                return None
        return None


    def _binary_search_first_before_date(self,items, end_date):
        """二分查找第一个早于 end_date 的 item 的索引(按日期粒度)

        Args:
            items: item 列表(时间倒序,即最新的在前面)
            end_date: date 对象,结束日期

        Returns:
            第一个早于 end_date 的 item 的索引,如果没有找到则返回 -1
        """
        left, right = 0, len(items) - 1
        result = -1

        while left <= right:
            mid = (left + right) // 2
            mid_date = self._get_item_date(items[mid])

            if mid_date is None:
                # 如果当前 item 没有日期信息,跳过
                left = mid + 1
                continue

            if mid_date < end_date:
                # 当前 item 的日期早于 end_date,记录位置并继续向左查找
                result = mid
                right = mid - 1
            else:
                # 当前 item 的日期晚于或等于 end_date,向右查找
                left = mid + 1

        return result


    def get_photo_with_end_date_and_count_items(self,SinglePageFunc, end_date, count):
        """根据结束日期和数量获取指定数量的 items (按日期粒度,不考虑具体时间)
            结束日期向前数count个

        Args:
            SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
            end_date: 结束日期,支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
            count: int,需要获取的 item 数量

        Returns:
            list,包含指定数量的 items (所有 item 的日期都早于 end_date)
        """
        # ----------------------------------------------------------------
        # def SinglePageFunc(cursor=None) -> dict:
        #     return { 'items':[] , "has_more":True/False, "cursor"  }
        # ----------------------------------------------------------------
        # 解析结束日期
        end_date = self._parse_date_input(end_date)

        cursor = None
        r = []

        while True:
            # 获取一页数据
            page = SinglePageFunc(cursor=cursor)
            items = page["items"]

            if not items:
                # 没有更多数据了
                break

            # 检查最后一个 item 的日期
            last_item_date = self._get_item_date(items[-1])

            if last_item_date is None or last_item_date >= end_date:
                # 最后一个 item 的日期仍然晚于或等于 end_date
                # 继续请求下一页
                if page["has_more"]:
                    cursor = page["cursor"]
                else:
                    # 没有更多数据了
                    break
            else:
                # 最后一个 item 的日期早于 end_date
                # 使用二分查找找到第一个早于 end_date 的 item
                first_index = self._binary_search_first_before_date(items, end_date)

                if first_index != -1:
                    # 找到了第一个日期早于 end_date 的 item
                    # 将从该位置开始的所有 items 加入结果
                    r.extend(items[first_index:])

                    # 检查是否已经收集到足够的数量
                    if len(r) >= count:
                        return r[:count]

                    # 如果还需要更多,继续请求
                    if page["has_more"]:
                        cursor = page["cursor"]
                    else:
                        break
                else:
                    # 没有找到早于 end_date 的 item,继续下一页
                    if page["has_more"]:
                        cursor = page["cursor"]
                    else:
                        break

        # 返回收集到的所有 items(可能少于 count)
        return r[:count] if len(r) >= count else r


    def _binary_search_date_range_boundary(self,items, start_date, end_date):
        """在items中找到日期区间的边界索引

        Args:
            items: item 列表(时间倒序,即最新的在前面)
            start_date: date 对象,开始日期(包含)
            end_date: date 对象,结束日期(不包含)

        Returns:
            tuple (start_index, end_index):
                - start_index: 第一个日期 >= start_date 的item索引,-1表示未找到
                - end_index: 第一个日期 < end_date 的item索引,-1表示未找到
        """
        # 找到第一个日期早于 end_date 的位置(即 < end_date)
        end_index = self._binary_search_first_before_date(items, end_date)

        # 找到第一个日期早于 start_date 的位置
        # items在这个位置之前(不包含)的都是 >= start_date 的
        left, right = 0, len(items) - 1
        first_before_start = -1

        while left <= right:
            mid = (left + right) // 2
            mid_date = self._get_item_date(items[mid])

            if mid_date is None:
                left = mid + 1
                continue

            if mid_date < start_date:
                # 找到第一个 < start_date 的位置
                first_before_start = mid
                right = mid - 1
            else:
                # mid_date >= start_date
                left = mid + 1

        # start_index 应该是从第一个item到 first_before_start 之前
        # 如果 first_before_start == -1,说明所有item的日期都 >= start_date
        # 如果 first_before_start == 0,说明第一个item就 < start_date,没有符合条件的

        if first_before_start == 0:
            # 第一个item就已经 < start_date,没有符合条件的items
            return -1, -1

        # 确定区间
        # [0, first_before_start) 是 >= start_date 的区间
        # [0, end_index] 是 < end_date 的区间
        # 交集就是 [0, min(first_before_start, end_index+1))

        if end_index == -1:
            # 没有 < end_date 的items,所有items都 >= end_date
            return -1, -1

        if first_before_start == -1:
            # 所有items都 >= start_date
            # 那么区间就是 [0, end_index]
            return 0, end_index
        else:
            # 区间是 [0, min(first_before_start-1, end_index)]
            if first_before_start - 1 < 0:
                return -1, -1
            return 0, min(first_before_start - 1, end_index)


    def get_photo_with_date_range_1items(self,SinglePageFunc, start_date, end_date):
        """获取指定日期区间内的所有 items (按日期粒度)
        原始代码逻辑

        Args:
            SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
            start_date: 开始日期(包含),支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
            end_date: 结束日期(不包含),格式同 start_date

        Returns:
            list,包含日期在 [start_date, end_date) 区间内的所有 items
        """
        # ----------------------------------------------------------------
        # def SinglePageFunc(cursor=None) -> dict:
        #     return { 'items':[] , "has_more":True/False, "cursor"  }


        #  逻辑：
        #  每个items都有对应的first（数组中的最后一个，日期最小），last（数组中的第一个，日期最大）
        #  因此有五种情况
        # 1. 当前区间全部不在范围内：即 first > end_date 或者last < start_data 当前区间全部不添加
        # 2. 当前区间后半部分在范围内：即 first >= end_date && first <= start_data, last < end_date 取[first, end_date)
        # 3. 当前区间前半部分在范围内：即 first < start_date, last >= start_date && last <= end_date 取[start_date, last]
        # 4. 当前区间全部在范围内：即 first < start_date && last > end_date 取[first,last]
        # ----------------------------------------------------------------
        # 解析日期
        start_date = self._parse_date_input(start_date)
        end_date = self._parse_date_input(end_date)

        if start_date >= end_date:
            raise ValueError(f"start_date ({start_date}) 必须小于 end_date ({end_date})")

        cursor = None
        r = []
        found_start_boundary = False
        page_number = 0  #log 用于标识页码
        debug_dir = "debug_json_logs"  #log 调试日志目录
        os.makedirs(debug_dir, exist_ok=True)  #log 创建目录

        while True:
            # 获取一页数据
            page = SinglePageFunc(cursor=cursor)
            items = page["items"]
            page_number += 1  #log

            if not items:
                # 没有更多数据了
                break

            item_end_data = self._get_item_date(items[0])  #log
            item_begin_data = self._get_item_date(items[-1])  #log
            print(f"\n========== 第 {page_number} 页 ==========")  #log
            print(f"页面 items 总数: {len(items)}")  #log
            print(f"item_begin_data = {item_begin_data}")  #log
            print(f"item_end_data = {item_end_data}")  #log
            print(f"目标区间: [{start_date}, {end_date})")  #log

            # 检查第一个 item 的日期(因为是倒序,第一个是最新的)
            first_item_date = self._get_item_date(items[0])

            if first_item_date is not None and first_item_date < start_date:
                # 第一个item的日期都小于开始日期,说明已经超出范围,停止
                break

            # 检查最后一个 item 的日期
            last_item_date = self._get_item_date(items[-1])

            # 判断当前页与区间的关系
            if last_item_date is not None and last_item_date >= end_date:
                # 整页都在 end_date 之后(或等于),继续请求下一页
                if page["has_more"]:
                    print(f"⏱ 等待 500 毫秒后请求下一页...")  #log
                    time.sleep(0.5)  #log
                    cursor = page["cursor"]
                else:
                    break
                continue

            # 到这里,说明当前页包含了部分或全部区间内的数据
            # 需要精确找到区间边界

            # 找到第一个 < end_date 的位置
            end_boundary = self._binary_search_first_before_date(items, end_date)

            if end_boundary == -1:
                # 当前页没有 < end_date 的items,继续下一页
                if page["has_more"]:
                    print(f"⏱ 等待 500 毫秒后请求下一页...")  #log
                    time.sleep(0.5)  #log
                    cursor = page["cursor"]
                else:
                    break
                continue

            # 找到第一个 < start_date 的位置
            start_boundary = self._binary_search_first_before_date(items, start_date)

            # 确定要收集的区间（数据是倒序的！）
            # start_boundary 是第一个 < start_date 的位置
            # [0, start_boundary) 是 >= start_date 的区间
            # end_boundary 是第一个 < end_date 的位置
            # [end_boundary, len) 是 < end_date 的区间
            # 
            # 能执行到这里，说明 end_boundary != -1，即当前页有 < end_date 的数据
            # 我们要收集的是：>= start_date 且 < end_date 的items

            if start_boundary == -1:
                # 所有items都 >= start_date
                # 由于能执行到这里，end_boundary != -1，说明有 < end_date 的数据
                # 所以整页都在 [start_date, end_date) 区间内
                collected_items = items[0:len(items)]
                r.extend(collected_items)
                found_start_boundary = False  # 还没找到start边界，继续下一页
                
                # 打印加入的个数  #log
                print(f"✓ 本次加入 {len(collected_items)} 个 items (区间: [0:{len(items)}]) - 整页都在区间内")  #log
                print(f"  当前 r 总数: {len(r)}")  #log
                
                # 保存完整的 page JSON  #log
                # json_filename = os.path.join(debug_dir, f"page_{page_number}_partial_match.json")  #log
                # with open(json_filename, 'w', encoding='utf-8') as f:  #log
                #     json.dump(page, f, ensure_ascii=False, indent=2, default=str)  #log
                # print(f"  已保存 JSON 到: {json_filename}")  #log
                
            elif start_boundary == 0:
                # 第一个item就 < start_date,没有符合条件的
                print(f"✗ 第一个 item 就 < start_date, 停止搜索")  #log
                break
            else:
                # 部分items在区间内
                # 需要同时考虑start和end边界
                # [0, start_boundary) 是 >= start_date 的items
                # 但还需要进一步检查这些items是否 < end_date
                collected_items = []
                for i in range(0, start_boundary):
                    item_date = self._get_item_date(items[i])
                    if item_date is not None and item_date < end_date:
                        collected_items.append(items[i])
                    else:
                        # 如果项目日期 >= end_date，则跳过
                        continue
                
                if collected_items:
                    r.extend(collected_items)
                    found_start_boundary = True
                    
                    # 打印加入的个数  #log
                    print(f"✓ 本次加入 {len(collected_items)} 个 items (区间边界处理)")  #log
                    print(f"  start_boundary={start_boundary}, end_boundary={end_boundary}")  #log
                    print(f"  当前 r 总数: {len(r)}")  #log
                
                # 已经找到了 start_date 的边界,不需要继续
                print(f"✓ 已找到 start_date 边界，搜索完成")  #log
                break

            # 检查是否已经完整覆盖了区间
            if last_item_date is not None and last_item_date < start_date:
                # 已经超出 start_date,停止
                break

            # 继续下一页
            if page["has_more"]:
                print(f"⏱ 等待 500 毫秒后请求下一页...")  #log
                time.sleep(0.5)  #log
                cursor = page["cursor"]
            else:
                break

        return r

    def get_photo_with_date_range_items(self, SinglePageFunc, start_date, end_date):
        """获取指定日期区间内的所有 items (按日期粒度)

        Args:
            SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
            start_date: 开始日期(包含),支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
            end_date: 结束日期(不包含),格式同 start_date

        Returns:
            list,包含日期在 [start_date, end_date) 区间内的所有 items
        """
        # ----------------------------------------------------------------
        # def SinglePageFunc(cursor=None) -> dict:
        #     return { 'items':[] , "has_more":True/False, "cursor"  }

        #  逻辑：
        #  每个items都有对应的first（数组中的最后一个，日期最小），last（数组中的第一个，日期最大）
        #  因此有五种情况
        # 1. 当前区间全部不在范围内：即 first > end_date 或者last < start_data 当前区间全部不添加
        # 2. 当前区间后半部分在范围内：即 first >= end_date && first <= start_data, last < end_date 取[first, end_date)
        # 3. 当前区间前半部分在范围内：即 first < start_date, last >= start_date && last <= end_date 取[start_date, last]
        # 4. 当前区间全部在范围内：即 first < start_date && last > end_date 取[first,last]
        # ----------------------------------------------------------------
        # 解析日期
        start_date = self._parse_date_input(start_date)
        end_date = self._parse_date_input(end_date)

        if start_date >= end_date:
            raise ValueError(f"start_date ({start_date}) 必须小于 end_date ({end_date})")

        cursor = None
        r = []
        page_number = 0  # log 用于标识页码
        debug_dir = "debug_json_logs"  # log 调试日志目录
        os.makedirs(debug_dir, exist_ok=True)  # log 创建目录

        while True:
            # 获取一页数据
            page = SinglePageFunc(cursor=cursor)
            items = page["items"]
            page_number += 1  # log

            if not items:
                # 没有更多数据了
                break

            item_end_data = self._get_item_date(items[0])  # log
            item_begin_data = self._get_item_date(items[-1])  # log
            print(f"\n========== 第 {page_number} 页 ==========")  # log
            print(f"页面 items 总数: {len(items)}")  # log
            print(f"item_begin_data = {item_begin_data}")  # log
            print(f"item_end_data = {item_end_data}")  # log
            print(f"目标区间: [{start_date}, {end_date})")  # log

            # 获取当前页的第一个和最后一个item的日期
            first_item_date = self._get_item_date(items[0])  # 最大日期（最新的）
            last_item_date = self._get_item_date(items[-1])  # 最小日期（最旧的）

            # 根据指定逻辑判断五种情况
            # 1. 当前区间全部不在范围内：即 last_item_date > end_date 或者 first_item_date < start_date
            if (last_item_date is not None and last_item_date >= end_date) or \
                    (first_item_date is not None and first_item_date < start_date):
                print("✗ 当前区间全部不在范围内")  # log
                # 继续下一页
                if page["has_more"]:
                    print(f"⏱ 等待 500 毫秒后请求下一页...")  # log
                    time.sleep(0.5)  # log
                    cursor = page["cursor"]
                else:
                    break
                continue

            # 2. 当前区间后半部分在范围内：即 last_item_date >= start_date && first_item_date >= start_date && last_item_date < end_date
            # 修正：当前区间后半部分在范围内，last_item_date < end_date && first_item_date >= start_date
            if (last_item_date is not None and last_item_date < end_date) and \
                    (first_item_date is not None and first_item_date >= start_date):
                print("✓ 当前区间后半部分在范围内")  # log
                # 找到第一个 < end_date 的位置
                end_boundary = self._binary_search_first_before_date(items, end_date)
                if end_boundary != -1:
                    # 取从 end_boundary 到末尾的items（即 [end_boundary, len(items))）
                    collected_items = items[end_boundary:]
                    r.extend(collected_items)
                    print(f"✓ 本次加入 {len(collected_items)} 个 items (区间: [{end_boundary}:{len(items)}])")  # log
                    print(f"  当前 r 总数: {len(r)}")  # log
                # 继续下一页
                if page["has_more"]:
                    print(f"⏱ 等待 500 毫秒后请求下一页...")  # log
                    time.sleep(0.5)  # log
                    cursor = page["cursor"]
                else:
                    break
                continue

            # 3. 当前区间前半部分在范围内：即 last_item_date < start_date && first_item_date <= end_date
            if (last_item_date is not None and last_item_date < start_date) and \
                    (first_item_date is not None and first_item_date < end_date):
                print("✓ 当前区间前半部分在范围内")  # log
                # 找到第一个 < start_date 的位置
                start_boundary = self._binary_search_first_before_date(items, start_date)
                if start_boundary != -1:
                    # 取从开始到 start_boundary 的items（即 [0, start_boundary)）
                    collected_items = items[0:start_boundary]
                    r.extend(collected_items)
                    print(f"✓ 本次加入 {len(collected_items)} 个 items (区间: [0:{start_boundary}])")  # log
                    print(f"  当前 r 总数: {len(r)}")  # log
                # 已经处理完需要的数据，可以停止
                break

            # 4. 当前区间全部在范围内：即 last_item_date >= start_date && first_item_date < end_date
            if (last_item_date is not None and last_item_date >= start_date) and \
                    (first_item_date is not None and first_item_date < end_date):
                print("✓ 当前区间全部在范围内")  # log
                # 整个页面的items都在范围内
                collected_items = items[:]
                r.extend(collected_items)
                print(f"✓ 本次加入 {len(collected_items)} 个 items (整页)")  # log
                print(f"  当前 r 总数: {len(r)}")  # log
                # 继续下一页
                if page["has_more"]:
                    print(f"⏱ 等待 500 毫秒后请求下一页...")  # log
                    time.sleep(0.5)  # log
                    cursor = page["cursor"]
                else:
                    break
                continue

            # 如果以上情况都不符合，继续下一页
            if page["has_more"]:
                print(f"⏱ 等待 500 毫秒后请求下一页...")  # log
                time.sleep(0.5)  # log
                cursor = page["cursor"]
            else:
                break

        return r


    def get_photo_with_end_date_and_count(self,SinglePageFunc, end_date, count):
        """根据结束日期和数量获取指定数量的 items,返回标准数据格式

        这是 get_photo_with_end_date_and_count_items 的封装版本,
        返回与 api.get_self_1page 相同的数据结构

        Args:
            SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
            end_date: 结束日期,支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
            count: int,需要获取的 item 数量

        Returns:
            dict: {'items': [...], 'has_more': False, 'cursor': None}
                - items: 包含指定数量的 items (所有 item 的日期都早于 end_date)
                - has_more: 总是 False (因为已经获取了所有需要的数据)
                - cursor: 总是 None
        """
        items = self.get_photo_with_end_date_and_count_items(SinglePageFunc, end_date, count)
        return {
            'items': items,
            'has_more': False,
            'cursor': None
        }


    def get_photo_with_date_range(self,SinglePageFunc, start_date, end_date):
        """获取指定日期区间内的所有 items,返回标准数据格式

        这是 get_photo_with_date_range_items 的封装版本,
        返回与 api.get_self_1page 相同的数据结构

        Args:
            SinglePageFunc: 单页获取函数,接受 cursor 参数,返回 {'items':[], 'has_more':True/False, 'cursor'}
            start_date: 开始日期(包含),支持多种格式:
                - date 对象
                - datetime 对象(会提取日期部分)
                - 字符串: "2026:01:01" 或 "2026:01:01 20:33:12" 或 "2026-01-01"
            end_date: 结束日期(不包含),格式同 start_date

        Returns:
            dict: {'items': [...], 'has_more': False, 'cursor': None}
                - items: 包含日期在 [start_date, end_date) 区间内的所有 items
                - has_more: 总是 False (因为已经获取了所有需要的数据)
                - cursor: 总是 None
        """
        items = self.get_photo_with_date_range_items(SinglePageFunc, start_date, end_date)
        result = {
            'items': items,
            'has_more': False,
            'cursor': None
        }
        
        # 生成当前时间戳和文件名
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        start_str = self._parse_date_input(start_date).strftime("%Y-%m-%d")
        end_str = self._parse_date_input(end_date).strftime("%Y-%m-%d")
        count = len(items)
        filename = f"{current_time}_{start_str}_{end_str}_{count}.json"
        
        # 保存结果到JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"已将结果保存到文件: {filename}")
        
        return result
